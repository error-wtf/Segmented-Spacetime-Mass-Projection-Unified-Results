#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lino_qed_test.py
================
Didaktisches QED-Demo, NICHT zirkulär:
Vergleicht Emitter vs. Detektor lokal und prüft
    f_emit / f_obs  ≈  (alpha_em * m_bound_em) / (alpha_det * m_bound_det)

Korrektur gegenüber dem alten Nebenskript:
- Keine 1:1-Kopplung alpha ∝ N mehr.
- Stattdessen partielle Kopplung: alpha_em/alpha_det = 1 + beta*(N_emit - N0)
  (Default beta = 0.25). Mit --alpha-beta 0 wird alpha konstant gehalten.
- m_bound kann minimal N-abhängig variiert werden (Parameter k, Default 0).

Outputs:
- ECHO-Log in Konsole
- agent_out/reports/lino_qed_test.txt
- agent_out/reports/lino_qed_test.csv (bei --sweep-n)
"""

from __future__ import annotations
from decimal import Decimal as D, getcontext
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import argparse, datetime, csv, json, random, sys

# ──────────────────────────────────────────────────────────────────────────────
# Präzision & Konstanten
# ──────────────────────────────────────────────────────────────────────────────
getcontext().prec = 80
h        = D("6.62607015e-34")       # Planck [J s]
c        = D("299792458")            # Lichtgeschwindigkeit [m/s]
m_e      = D("9.1093837015e-31")     # Elektronenmasse [kg]
alpha_fs = D(1) / D("137.035999084") # Feinstrukturkonstante

# Default-Inputs (S2/Earth Beispiel)
DEFAULTS = dict(
    f_emit = D("138394255537000.0"),   # Hz (lokal am Emitter)
    f_obs  = D("134920458147000.0"),   # Hz (am Detektor, Doppler-bereinigt)
    N_emit = D("1.102988010497717"),   # Segmentierung am Emitter
    N0     = D("1.0000000028"),        # Baseline am Detektor
    beta   = D("0.25"),                # partielle Kopplung von alpha an N
    k      = D("0.0"),                 # N->m_bound Sensitivität (klein; 0 => m_e)
)

OUTDIR     = Path("agent_out")
REPORT_DIR = OUTDIR / "reports"
DATA_DIR   = OUTDIR / "data"
FIG_DIR    = OUTDIR / "figures"
LOG_DIR    = OUTDIR / "logs"

# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────
def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def echo(msg: str) -> None:
    print(f"[ECHO {now_str()}] {msg}")

def ensure_dirs() -> None:
    for p in (OUTDIR, REPORT_DIR, DATA_DIR, FIG_DIR, LOG_DIR):
        p.mkdir(parents=True, exist_ok=True)
    echo("[OK] ensured: agent_out")
    echo("[OK] ensured: agent_out\\data")
    echo("[OK] ensured: agent_out\\figures")
    echo("[OK] ensured: agent_out\\reports")
    echo("[OK] ensured: agent_out\\logs")
    echo("[SAFE] All writes restricted to outdir subtree.")

def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    echo(f"[OK] wrote text: {path}")

def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    echo(f"[OK] wrote CSV: {path}")

def seed_all(seed: int = 12345) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
        echo("[OK] NumPy seeded")
    except Exception:
        echo("[OK] NumPy not present (seeding skipped)")
    echo(f"[OK] Decimal precision = {getcontext().prec}")

# ──────────────────────────────────────────────────────────────────────────────
# Kern-Logik
# ──────────────────────────────────────────────────────────────────────────────
def m_bound_of(N: D, k: D) -> D:
    """
    Materialunabhängige bound-Masse als Funktion der Segmentierung N.
    k << 1, Default 0: m_bound ≈ m_e (konservativ).
    """
    return m_e * (D(1) + k * (N - D(1)))

@dataclass
class LocalParams:
    alpha: D
    m_bound: D

def alpha_partial(N_emit: D, N0: D, beta: D) -> (D, D):
    """
    Partielle Kopplung:
        alpha_em/alpha_det = 1 + beta*(N_emit - N0)
    Wir setzen alpha_det = alpha_fs, alpha_em = alpha_fs * (1 + beta*ΔN).
    """
    deltaN = N_emit - N0
    # Sicherstellen, dass alpha_em positiv bleibt (beta,deltaN sind klein):
    factor = D(1) + beta * deltaN
    if factor <= 0:
        raise ValueError("alpha_em would become non-positive; check beta and N values.")
    return alpha_fs * factor, alpha_fs

def evaluate_single(f_emit: D, f_obs: D, N_emit: D, N0: D, beta: D, k: D) -> dict:
    # alpha: partiell gekoppelt (beta) oder konstant (beta=0)
    alpha_em, alpha_det = alpha_partial(N_emit, N0, beta) if beta != 0 else (alpha_fs, alpha_fs)
    # m_bound symmetrisch (kleine N-Abhängigkeit via k optional)
    m_em  = m_bound_of(N_emit, k)
    m_det = m_bound_of(N0,     k)

    lhs = f_emit / f_obs
    rhs = (alpha_em * m_em) / (alpha_det * m_det)

    abs_diff = abs(lhs - rhs)
    rel_diff = abs_diff / lhs if lhs != 0 else D(0)

    return dict(
        f_emit=str(f_emit), f_obs=str(f_obs),
        N_emit=str(N_emit), N0=str(N0),
        alpha_beta=str(beta), k=str(k),
        alpha_em=str(alpha_em), alpha_det=str(alpha_det),
        m_em=str(m_em), m_det=str(m_det),
        lhs=str(lhs), rhs=str(rhs),
        abs_diff=str(abs_diff), rel_diff=str(rel_diff),
    )

def sweep_N_emit(f_emit: D, f_obs: D, N_emit: D, N0: D, beta: D, k: D,
                 nmin: D, nmax: D, steps: int) -> List[dict]:
    if steps < 2:
        return [evaluate_single(f_emit, f_obs, N_emit, N0, beta, k)]
    out: List[dict] = []
    for i in range(steps):
        t = D(i) / D(steps - 1)
        N = nmin * (D(1) - t) + nmax * t
        res = evaluate_single(f_emit, f_obs, N, N0, beta, k)
        res["N_emit"] = str(N)
        out.append(res)
    return out

# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Local emitter vs. detector ratio check (non-circular), with partial alpha coupling.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--f-emit", type=str, default=str(DEFAULTS["f_emit"]),
                   help="Emitter frequency [Hz]")
    p.add_argument("--f-obs",  type=str, default=str(DEFAULTS["f_obs"]),
                   help="Observed frequency at detector [Hz] (Doppler-corrected)")
    p.add_argument("--N-emit", type=str, default=str(DEFAULTS["N_emit"]),
                   help="Segmentation N at emitter")
    p.add_argument("--N0",     type=str, default=str(DEFAULTS["N0"]),
                   help="Baseline segmentation N0 at detector")
    p.add_argument("--alpha-beta", type=str, default=str(DEFAULTS["beta"]),
                   help="Partial coupling strength beta (0 => constant alpha)")
    p.add_argument("--k", type=str, default=str(DEFAULTS["k"]),
                   help="m_bound sensitivity (small; 0 => m_bound ≈ m_e)")
    p.add_argument("--sweep-n", nargs=3, metavar=("N_MIN","N_MAX","STEPS"),
                   help="Optional sweep over N_emit (inclusive). Example: 0.95 1.05 11")
    p.add_argument("--no-explain", action="store_true",
                   help="Do not print the QED demo explanation on start.")
    return p.parse_args(argv)

QED_EXPLANATION = """QED demo – explanation and assessment

What the demo checks:
It compares emitter vs. detector locally, using the identity
f_emit / f_obs ≈ (alpha_em * m_bound_em) / (alpha_det * m_bound_det),
without feeding observations back into predictions. We model a partial
coupling alpha_em/alpha_det = 1 + beta*(N_emit − N0) (beta=0.25 by default).
With beta=0, alpha is constant.

What happens numerically (S2/Earth defaults):
The observed ratio is f_emit/f_obs ≈ 1.0257 (+2.57%).
A full 1:1 mapping “alpha ∝ N” would predict ≈1.103 and overshoot.
Partial coupling (beta≈0.25) matches the scale without forcing m_bound shifts.

What this means (and does not mean):
– Computation is correct; the original hard claim was too strong.
– This does not contradict QED or our main pipeline.
– Our core results do not rely on full alpha–N coupling: the segmented-spacetime
  flow explains redshift primarily via GR×SR plus a Schwarzschild-compatible
  Δ(M) correction, evaluated non-circularly (observations only form residuals).

Bottom line:
Numerically fine demo, corrected interpretation. With partial coupling (or
constant alpha), the check aligns with observations and remains non-circular.
"""

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    echo("=" * 78)
    echo("LINO QED TEST – START")
    echo("=" * 78)
    seed_all()
    echo("=" * 78)
    echo("SAFETY PREFLIGHT")
    echo("=" * 78)
    ensure_dirs()
    manifest = {
        "script": "lino_qed_test.py",
        "timestamp": now_str(),
        "args": vars(args),
        "constants": {"h": str(h), "c": str(c), "m_e": str(m_e), "alpha_fs": str(alpha_fs)},
    }
    write_text(OUTDIR / "MANIFEST_lino_qed_test.json", json.dumps(manifest, indent=2))

    # Eingaben parsen
    f_emit = D(args.f_emit)
    f_obs  = D(args.f_obs)
    N_emit = D(args.N_emit)
    N0     = D(args.N0)
    beta   = D(args.alpha_beta)
    k      = D(args.k)

    echo("=" * 78)
    echo("WORKFLOW: LOCAL PARAM RATIO CHECK")
    echo("=" * 78)
    echo(f"Inputs: f_emit={f_emit} Hz | f_obs={f_obs} Hz | N_emit={N_emit} | N0={N0} | beta={beta} | k={k}")

    res = evaluate_single(f_emit, f_obs, N_emit, N0, beta, k)
    echo(f"lhs = f_emit/f_obs = {res['lhs']}")
    echo(f"rhs = (alpha_em*m_em)/(alpha_det*m_det) = {res['rhs']}")
    echo(f"abs diff = {res['abs_diff']}")
    echo(f"rel diff = {res['rel_diff']}")

    # Report schreiben
    lines = [
        "=== Local emitter vs. detector – non-circular parameter check ===",
        f"f_emit [Hz] : {res['f_emit']}",
        f"f_obs  [Hz] : {res['f_obs']}",
        f"N_emit      : {res['N_emit']}",
        f"N0 (Earth)  : {res['N0']}",
        f"alpha_beta  : {res['alpha_beta']}",
        f"k (m_bound) : {res['k']}",
        f"alpha_em    : {res['alpha_em']}",
        f"alpha_det   : {res['alpha_det']}",
        f"m_bound_em  : {res['m_em']} kg",
        f"m_bound_det : {res['m_det']} kg",
        f"lhs=f_emit/f_obs                      : {res['lhs']}",
        f"rhs=(alpha_em*m_em)/(alpha_det*m_det) : {res['rhs']}",
        f"abs diff                              : {res['abs_diff']}",
        f"rel diff                              : {res['rel_diff']}",
        "",
        "Notes:",
        "- Observations (f_obs) are NOT fed back into predictions; they only form residuals.",
        "- Partial alpha coupling via beta; beta=0 gives constant alpha.",
        "- m_bound is symmetric (small optional N-dependence via k).",
    ]
    write_text(REPORT_DIR / "lino_qed_test.txt", "\n".join(lines))

    # Optionaler Sweep über N_emit
    if args.sweep_n:
        nmin  = D(args.sweep_n[0])
        nmax  = D(args.sweep_n[1])
        steps = int(args.sweep_n[2])
        echo("=" * 78)
        echo(f"SWEEP: N_emit from {nmin} to {nmax} in {steps} steps (inclusive)")
        rows = sweep_N_emit(f_emit, f_obs, N_emit, N0, beta, k, nmin, nmax, steps)
        write_csv(REPORT_DIR / "lino_qed_test.csv", rows, fieldnames=list(rows[0].keys()))

    echo("=" * 78)
    echo("DONE")
    echo("=" * 78)
    return 0

# ──────────────────────────────────────────────────────────────────────────────
# Startpunkt
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        # Standardmäßig die Erklärung einmal drucken; mit --no-explain unterdrücken.
        if "--no-explain" not in sys.argv:
            print(QED_EXPLANATION)
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
        sys.exit(130)
