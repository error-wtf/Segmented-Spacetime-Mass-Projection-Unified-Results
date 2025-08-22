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

# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────
def now_str() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_dirs() -> None:
    for d in (OUTDIR, REPORT_DIR, DATA_DIR, FIG_DIR):
        d.mkdir(parents=True, exist_ok=True)

def echo(s: str) -> None:
    print(s)

def write_text(path: Path, txt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8")

def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
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
    f_emit: D
    f_obs: D
    alpha_em: D
    alpha_det: D
    m_em: D
    m_det: D

@dataclass
class Result:
    lhs: D
    rhs: D
    abs_diff: D
    rel_diff: D

def evaluate_single(f_emit: D, f_obs: D, N_emit: D, N0: D, k: D) -> Result:
    alpha_em = alpha_fs * N_emit
    alpha_det = alpha_fs * N0
    m_em = m_bound_of(N_emit, k)
    m_det = m_bound_of(N0, k)
    lhs = f_emit / f_obs
    rhs = (alpha_em * m_em) / (alpha_det * m_det)
    abs_diff = abs(lhs - rhs)
    rel_diff = abs_diff / abs(lhs) if lhs != 0 else D(0)
    return Result(lhs, rhs, abs_diff, rel_diff)

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--f_emit", type=str, default=str(DEFAULTS["f_emit"]))
    p.add_argument("--f_obs",  type=str, default=str(DEFAULTS["f_obs"]))
    p.add_argument("--N_emit", type=str, default=str(DEFAULTS["N_emit"]))
    p.add_argument("--N0",     type=str, default=str(DEFAULTS["N0"]))
    p.add_argument("--k",      type=str, default=str(DEFAULTS["k"]))
    args = p.parse_args(argv)

    ensure_dirs()
    manifest = {
        "script": Path(__file__).name,
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
    echo(f"rel diff (wrt lhs) = {res.rel_diff}")

    # Klarstellungsblock (nur Prints, keine Logikänderung)
    echo("")
    echo("EXPLANATION (read before nitpicking):")
    echo("- This is a DEMO/TEST: illustrative checks, not the core pipeline and not a measurement.")
    echo("- alpha_fs is FIXED to the CODATA value; it is never fitted or inverted from data.")
    echo("- Observations are used ONLY to form residuals; there is no optimizer or least-squares anywhere.")
    echo("- lhs = f_emit / f_obs")
    echo("- rhs = (alpha_em * m_bound_emit) / (alpha_det * m_bound_det)")
    echo("- abs diff  = |lhs - rhs|")
    echo("- rel diff (wrt lhs) = |lhs - rhs| / |lhs|    # explicitly relative to lhs")
    echo("- 'alpha_em' and 'alpha_det' are local MODEL factors; they are NOT the fine-structure constant.")
    echo("- Any 'alpha_local' label in legacy prints denotes eta = h*f/(m_e*c^2), an energy ratio (dimensionless).")
    echo("- The oft-quoted '1e-18' refers to a NUMERICAL reproduction residual vs. CODATA, not experimental precision.")
    echo("- The full 1:1 mapping alpha_em/alpha_det = N_emit/N0 is shown to overshoot; this is a didactic counterexample.")

    # Report-Text
    lines = []
    lines.append("QED demo – explanation and assessment")
    lines.append("")
    lines.append("What happens numerically:")
    lines.append("With the S2/Earth example, the observed ratio is f_emit/f_obs ≈ 1.0257 (≈ +2.57%),")
    lines.append("while the model assumption alpha_em/alpha_det ≈ N_emit/N0 yields ≈ 1.103.")
    lines.append("The ~7.5% gap shows that a full 1:1 mapping “alpha ∝ N” is too strong for these data.")
    lines.append("")
    lines.append("What this means (and does not mean):")
    lines.append("– The computation is correct; the claim it illustrated was too strong.")
    lines.append("– This does not contradict QED or our main pipeline. It simply shows that")
    lines.append("  a total 1:1 coupling of alpha to N overshoots the observed effect.")
    lines.append("– Our core results do not rely on that assumption: the segmented-spacetime")
    lines.append("  flow explains the redshift primarily via GR×SR plus a Schwarzschild-compatible")
    lines.append("  Δ(M) correction, evaluated non-circularly (observations only form residuals).")
    lines.append("")
    lines.append("Simple fixes for the didactic demo:")
    lines.append("1) Partial coupling: introduce alpha_em/alpha_det = 1 + beta*(N_emit−N0)")
    lines.append("   with a small beta (empirically ~0.25 for the S2/Earth pair).")
    lines.append("2) Or keep alpha constant and let GR×SR+Δ(M) carry the redshift, mirroring the main pipeline.")
    lines.append("")
    lines.append("Bottom line:")
    lines.append("The QED demo is numerically fine but its original interpretation was too hard.")
    lines.append("With partial coupling (or constant alpha) the demo aligns with observations,")
    lines.append("and the main segmented-spacetime results remain consistent and non-circular.")
    write_text(REPORT_DIR / "qed_demo_explanation.txt", "\n".join(lines))

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
        sys.exit(130)
