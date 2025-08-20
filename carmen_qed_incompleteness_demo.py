#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carmen_qed_incompleteness_demo_v2.py
====================================

Ziel
----
Nicht-zirkulärer, ortsaufgelöster Vergleich Emitter vs. Detektor:
Wir zeigen, dass das beobachtete Frequenzverhältnis f_emit/f_obs
als Verhältnis lokaler Parameter (alpha, m_bound) verstanden werden kann,
ohne Beobachtungen in die Modellvorhersage zurückzuspeisen.

Kernidentität (rein lokal, ohne Rückkopplung):
    f_emit / f_obs = (alpha_em * m_bound_em) / (alpha_det * m_bound_det)

Mapping im Sinne des Repos:
    alpha_em  = alpha_fs * N_emit
    alpha_det = alpha_fs * N0
Standardmäßig setzen wir m_bound ≈ m_e (konservativ). Optional kann eine
sehr kleine N-abhängige Variation gewählt werden:
    m_bound(N) = m_e * (1 + k * (N - 1)),  mit k << 1 (Default: k=0)

CLI-Beispiele
-------------
# Standard (S2/Earth), konservativ (m_bound ≈ m_e):
python carmen_qed_incompleteness_demo_v2.py

# Mit leichter N-abhängiger m_bound-Variation (k = 1e-8):
python carmen_qed_incompleteness_demo_v2.py --k 1e-8

# Sweep über N_emit (±5% um Default, 11 Punkte):
python carmen_qed_incompleteness_demo_v2.py --sweep-n 0.95 1.05 11

Ausgaben
--------
- Klarer ECHO-Log in die Konsole
- agent_out/reports/qed_incompleteness_v2.txt
- agent_out/reports/qed_incompleteness_v2.csv   (bei --sweep-n)

© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from __future__ import annotations
from decimal import Decimal as D, getcontext
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import argparse, datetime, csv, math, sys, json, random, os

# ──────────────────────────────────────────────────────────────────────────────
# Präzision & Konstanten (CODATA-kompatibel)
# ──────────────────────────────────────────────────────────────────────────────
getcontext().prec = 80

h        = D("6.62607015e-34")       # Planck [J·s]
c        = D("299792458")            # Lichtgeschwindigkeit [m/s]
m_e      = D("9.1093837015e-31")     # Elektronenmasse [kg]
alpha_fs = D("1") / D("137.035999084")

# Standard-Beispiel: S2 (Emitter) vs. Erde (Detektor)
DEFAULTS = dict(
    f_emit=D("138394255537000.0"),   # Hz  (S2, lokal)
    f_obs =D("134920458147000.0"),   # Hz  (Erde, Doppler-korrigiert)
    N_emit=D("1.102988010497717"),   # aus euren Papern
    N0    =D("1.0000000028"),        # Earth baseline
    k     =D("0.0"),                 # m_bound-Sensitivität (0 => m_bound ≈ m_e)
)

OUTDIR = Path("agent_out")
REPORT_DIR = OUTDIR / "reports"
DATA_DIR = OUTDIR / "data"
FIG_DIR = OUTDIR / "figures"
LOG_DIR = OUTDIR / "logs"


# ──────────────────────────────────────────────────────────────────────────────
# Utils
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

def seed_all(seed: int = 42) -> None:
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
    Default k=0 ⇒ m_bound ≈ m_e (konservativ).
    Für kleine k (z. B. 1e-8) entsteht eine minimale Variation.
    """
    return m_e * (D(1) + k * (N - D(1)))

@dataclass
class LocalParams:
    N: D
    alpha: D
    m_bound: D

def local_params(N: D, k: D) -> LocalParams:
    return LocalParams(
        N=N,
        alpha=alpha_fs * N,
        m_bound=m_bound_of(N, k),
    )

@dataclass
class Result:
    f_emit: D
    f_obs: D
    lhs: D
    rhs: D
    abs_diff: D
    rel_diff: D
    alpha_em: D
    alpha_det: D
    m_em: D
    m_det: D

def evaluate_single(f_emit: D, f_obs: D, N_emit: D, N0: D, k: D) -> Result:
    em  = local_params(N_emit, k)
    det = local_params(N0,     k)

    lhs = f_emit / f_obs
    rhs = (em.alpha * em.m_bound) / (det.alpha * det.m_bound)

    abs_diff = abs(lhs - rhs)
    rel_diff = abs_diff / lhs if lhs != 0 else D(0)

    return Result(
        f_emit=f_emit, f_obs=f_obs,
        lhs=lhs, rhs=rhs,
        abs_diff=abs_diff, rel_diff=rel_diff,
        alpha_em=em.alpha, alpha_det=det.alpha,
        m_em=em.m_bound, m_det=det.m_bound
    )

def sweep_N_emit(f_emit: D, f_obs: D, N_emit: D, N0: D, k: D,
                 nmin: D, nmax: D, steps: int) -> List[Result]:
    if steps < 2:
        return [evaluate_single(f_emit, f_obs, N_emit, N0, k)]
    results: List[Result] = []
    for i in range(steps):
        t = D(i) / D(steps - 1)
        N = nmin * (D(1) - t) + nmax * t
        results.append(evaluate_single(f_emit, f_obs, N, N0, k))
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Emitter-vs-Detektor (alpha, m_bound) – nicht-zirkulärer Demo-Check",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--f-emit", type=str, default=str(DEFAULTS["f_emit"]),
                   help="Lokale Emissionsfrequenz am Emitter [Hz]")
    p.add_argument("--f-obs",  type=str, default=str(DEFAULTS["f_obs"]),
                   help="Beobachtete Frequenz am Detektor [Hz] (Doppler-korrigiert)")
    p.add_argument("--N-emit", type=str, default=str(DEFAULTS["N_emit"]),
                   help="Segmentierung am Emitter")
    p.add_argument("--N0",     type=str, default=str(DEFAULTS["N0"]),
                   help="Baseline-Segmentierung am Detektor")
    p.add_argument("--k",      type=str, default=str(DEFAULTS["k"]),
                   help="m_bound-Sensitivitätsfaktor (klein; 0 => m_bound ≈ m_e)")
    p.add_argument("--sweep-n", nargs=3, metavar=("N_MIN","N_MAX","STEPS"),
                   help="Optional: Sweep über N_emit (inklusive; steps≥2). Beispiele: 0.95 1.05 11")
    return p.parse_args(argv)

def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    # Determinismus & sichere Ausgabepfade
    echo("=" * 79)
    echo("SEGSPACE – QED Incompleteness Demo (v2) – START")
    echo("=" * 79)
    seed_all(12345)
    echo("=" * 79)
    echo("SAFETY PREFLIGHT")
    echo("=" * 79)
    ensure_dirs()
    manifest = {
        "script": "carmen_qed_incompleteness_demo_v2.py",
        "timestamp": now_str(),
        "args": vars(args),
        "constants": {
            "h": str(h), "c": str(c), "m_e": str(m_e), "alpha_fs": str(alpha_fs)
        }
    }
    write_text(OUTDIR / "MANIFEST_qed_incompl_v2.json", json.dumps(manifest, indent=2))

    # Eingaben parsen
    f_emit = D(args.f_emit)
    f_obs  = D(args.f_obs)
    N_emit = D(args.N_emit)
    N0     = D(args.N0)
    k      = D(args.k)

    echo("=" * 79)
    echo("WORKFLOW: LOCAL PARAM RATIO CHECK")
    echo("=" * 79)
    echo(f"Inputs: f_emit={f_emit} Hz | f_obs={f_obs} Hz | N_emit={N_emit} | N0={N0} | k={k}")

    # Einzelrechnung
    res = evaluate_single(f_emit, f_obs, N_emit, N0, k)
    echo(f"lhs = f_emit/f_obs = {res.lhs}")
    echo(f"rhs = (alpha_em*m_em)/(alpha_det*m_det) = {res.rhs}")
    echo(f"abs diff = {res.abs_diff}")
    echo(f"rel diff = {res.rel_diff}")

    # Report-Text
    lines = []
    lines.append("=== Emitter vs. Detektor – nicht-zirkulärer Parameter-Check ===")
    lines.append(f"f_emit [Hz] : {res.f_emit}")
    lines.append(f"f_obs  [Hz] : {res.f_obs}")
    lines.append(f"N_emit      : {N_emit}")
    lines.append(f"N0 (Earth)  : {N0}")
    lines.append(f"alpha_em    : {res.alpha_em}")
    lines.append(f"alpha_det   : {res.alpha_det}")
    lines.append(f"m_bound_em  : {res.m_em} kg")
    lines.append(f"m_bound_det : {res.m_det} kg")
    lines.append(f"lhs=f_emit/f_obs                  : {res.lhs}")
    lines.append(f"rhs=(alpha_em*m_em)/(alpha_det*m_det) : {res.rhs}")
    lines.append(f"abs diff                         : {res.abs_diff}")
    lines.append(f"rel diff                         : {res.rel_diff}")
    lines.append("")
    lines.append("Hinweis:")
    lines.append("- Beobachtungen (f_obs) werden NICHT in Vorhersagen zurückgespeist;")
    lines.append("  sie dienen ausschließlich der Residuenbildung / dem Verhältnis-Check.")
    lines.append("- alpha_em=N_emit*alpha_fs, alpha_det=N0*alpha_fs (modellinterne, lokale Größen).")
    lines.append("- m_bound≈m_e (konservativ) oder minimale N-Abhängigkeit via k; global und symmetrisch.")
    write_text(REPORT_DIR / "qed_incompleteness_v2.txt", "\n".join(lines))

    # Optionaler Sweep über N_emit
    if args.sweep_n:
        nmin = D(args.sweep_n[0])
        nmax = D(args.sweep_n[1])
        steps = int(args.sweep_n[2])
        echo("=" * 79)
        echo(f"SWEEP: N_emit from {nmin} to {nmax} in {steps} steps (inclusive)")
        sweep = sweep_N_emit(f_emit, f_obs, N_emit, N0, k, nmin, nmax, steps)
        rows = []
        for i, r in enumerate(sweep):
            rows.append({
                "idx": i,
                "N_emit": str(nmin + (nmax - nmin) * D(i) / D(max(steps - 1, 1))),
                "f_emit_Hz": str(r.f_emit),
                "f_obs_Hz": str(r.f_obs),
                "lhs_femit_fobs": str(r.lhs),
                "rhs_alpha_m_ratio": str(r.rhs),
                "abs_diff": str(r.abs_diff),
                "rel_diff": str(r.rel_diff),
            })
        write_csv(REPORT_DIR / "qed_incompleteness_v2.csv", rows,
                  fieldnames=list(rows[0].keys()))

    echo("=" * 79)
    echo("DONE")
    echo("=" * 79)
    return 0

if __name__ == "__main__":
    try:
        print("""QED demo – explanation and assessment

What the demo checks:
It compares emitter vs. detector locally, using the identity
f_emit / f_obs ≈ (alpha_em * m_bound_em) / (alpha_det * m_bound_det),
without feeding observations back into predictions. In the demo we set
alpha_em = alpha_fs * N_emit, alpha_det = alpha_fs * N0, and (by default) m_bound_em ≈ m_bound_det ≈ m_e.

What happens numerically:
With the S2/Earth example, the observed ratio is f_emit/f_obs ≈ 1.0257 (≈ +2.57%),
while the model assumption alpha_em/alpha_det ≈ N_emit/N0 yields ≈ 1.103.
The ~7.5% gap shows that a full 1:1 mapping “alpha ∝ N” is too strong for these data.

What this means (and does not mean):
– The computation is correct; the claim it illustrated was too strong.
– This does not contradict QED or our main pipeline. It simply shows that
  a total 1:1 coupling of alpha to N overshoots the observed effect.
– Our core results do not rely on that assumption: the segmented-spacetime
  flow explains the redshift primarily via GR×SR plus a Schwarzschild-compatible
  Δ(M) correction, evaluated non-circularly (observations only form residuals).

Simple fixes for the didactic demo:
1) Partial coupling: introduce alpha_em/alpha_det = 1 + beta*(N_emit−N0)
   with a small beta (empirically ~0.25 for the S2/Earth pair).
2) Or keep alpha constant and let GR×SR+Δ(M) carry the redshift, mirroring the main pipeline.

Bottom line:
The QED demo is numerically fine but its original interpretation was too hard.
With partial coupling (or constant alpha) the demo aligns with observations,
and the main segmented-spacetime results remain consistent and non-circular.
""")
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
        sys.exit(130)
        

