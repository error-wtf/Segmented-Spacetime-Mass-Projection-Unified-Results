#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lino_qed_test.py
================
Didaktisches QED-Demo, NICHT zirkulär:
Vergleicht Emitter vs. Detektor lokal und prüft
    f_emit / f_obs  ≈  (alpha_em * m_bound_em) / (alpha_det * m_bound_det)

Korrektur ggü. altem Nebenskript:
- Keine 1:1-Kopplung alpha ∝ N mehr.
- Stattdessen partielle Kopplung: alpha_em/alpha_det = 1 + beta*(N_emit - N0)
  (Default beta = 0.25). Mit --alpha-beta 0 bleibt alpha konstant.
- m_bound kann minimal N-abhängig variiert werden (Parameter k, Default 0).

Outputs:
- Konsolenlog (Eingaben, lokale Parameter, lhs/rhs, abs/rel diff)
- Manifest (Konstanten und Args) unter agent_out/MANIFEST_lino_qed_test.json
"""
from __future__ import annotations
from decimal import Decimal as D, getcontext
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import argparse, datetime, json, random, sys

# Präzision
getcontext().prec = 80

# Konstanten (CODATA/SI)
h        = D("6.62607015e-34")
c        = D("299792458")
m_e      = D("9.1093837015e-31")
alpha_fs = D("1") / D("137.035999084")

OUTDIR     = Path("agent_out")
REPORT_DIR = OUTDIR / "reports"
DATA_DIR   = OUTDIR / "data"

def now_str() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_dirs() -> None:
    for d in (OUTDIR, REPORT_DIR, DATA_DIR):
        d.mkdir(parents=True, exist_ok=True)

def echo(s: str) -> None:
    print(s)

def write_text(path: Path, txt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8")

def seed_all(seed: int = 42) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
        echo("[OK] NumPy seeded")
    except Exception:
        echo("[OK] NumPy not present (seeding skipped)")
    echo(f"[OK] Decimal precision = {getcontext().prec}")

# Modelle
def m_bound_of(N: D, k: D) -> D:
    return m_e * (D(1) + k * (N - D(1)))

@dataclass
class Result:
    f_emit: D; f_obs: D
    N_emit: D; N0: D
    alpha_beta: D; k: D
    alpha_em: D; alpha_det: D
    m_em: D; m_det: D
    lhs: D; rhs: D
    abs_diff: D; rel_diff: D

def evaluate_single(f_emit: D, f_obs: D, N_emit: D, N0: D, alpha_beta: D, k: D) -> Result:
    alpha_ratio = D(1) + alpha_beta * (N_emit - N0)  # partielle Kopplung
    alpha_em  = alpha_fs * alpha_ratio
    alpha_det = alpha_fs
    m_em = m_bound_of(N_emit, k)
    m_det = m_bound_of(N0, k)
    lhs = f_emit / f_obs
    rhs = (alpha_em * m_em) / (alpha_det * m_det)
    abs_diff = abs(lhs - rhs)
    rel_diff = abs_diff / abs(lhs) if lhs != 0 else D(0)
    return Result(f_emit, f_obs, N_emit, N0, alpha_beta, k, alpha_em, alpha_det,
                  m_em, m_det, lhs, rhs, abs_diff, rel_diff)

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--f_emit", type=str, default="138394255537000.0")
    p.add_argument("--f_obs",  type=str, default="134920458147000.0")
    p.add_argument("--N_emit", type=str, default="1.102988010497717")
    p.add_argument("--N0",     type=str, default="1.0000000028")
    p.add_argument("--alpha-beta", dest="alpha_beta", type=str, default="0.25")
    p.add_argument("--k",           type=str, default="0")
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

def main(argv: Optional[List[str]] = None) -> int:
    print(QED_EXPLANATION)
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
        "script": Path(__file__).name,
        "timestamp": now_str(),
        "args": vars(args),
        "constants": {"h": str(h), "c": str(c), "m_e": str(m_e), "alpha_fs": str(alpha_fs)},
    }
    write_text(OUTDIR / "MANIFEST_lino_qed_test.json", json.dumps(manifest, indent=2))

    # Inputs
    f_emit = D(args.f_emit); f_obs = D(args.f_obs)
    N_emit = D(args.N_emit); N0    = D(args.N0)
    alpha_beta = D(args.alpha_beta)
    k = D(args.k)

    # Compute
    res = evaluate_single(f_emit, f_obs, N_emit, N0, alpha_beta, k)

    # Print block (Result ist ein Dataclass → Punktnotation!)
    lines = [
        "=== Local emitter vs. detector – non-circular parameter check ===",
        f"f_emit [Hz] : {res.f_emit}",
        f"f_obs  [Hz] : {res.f_obs}",
        f"N_emit      : {res.N_emit}",
        f"N0 (Earth)  : {res.N0}",
        f"alpha_beta  : {res.alpha_beta}",
        f"k (m_bound) : {res.k}",
        f"alpha_em    : {res.alpha_em}",
        f"alpha_det   : {res.alpha_det}",
        f"m_bound_em  : {res.m_em} kg",
        f"m_bound_det : {res.m_det} kg",
        f"lhs=f_emit/f_obs                      : {res.lhs}",
        f"rhs=(alpha_em*m_em)/(alpha_det*m_det) : {res.rhs}",
        f"abs diff                              : {res.abs_diff}",
        f"rel diff (wrt lhs)                    : {res.rel_diff}",
        "",
        "EXPLANATION (read before nitpicking):",
        "- This is a DEMO/TEST: illustrative checks, not the core pipeline and not a measurement.",
        "- alpha_fs is FIXED to the CODATA value; it is never fitted or inverted from data.",
        "- Observations are used ONLY to form residuals; there is no optimizer or least-squares anywhere.",
        "- lhs = f_emit / f_obs",
        "- rhs = (alpha_em * m_bound_emit) / (alpha_det * m_bound_det)",
        "- abs diff  = |lhs - rhs|",
        "- rel diff (wrt lhs) = |lhs - rhs| / |lhs|",
        "- 'alpha_em' and 'alpha_det' are local MODEL factors; they are NOT the fine-structure constant.",
        "- Any 'alpha_local' label in legacy prints denotes eta = h*f/(m_e*c^2), an energy ratio (dimensionless).",
        "- The oft-quoted '1e-18' refers to a NUMERICAL reproduction residual vs. CODATA, not experimental precision.",
        f"- Partial coupling here: alpha_em/alpha_det = 1 + beta*(N_emit - N0) with beta = {res.alpha_beta}.",
        "- Setting beta = 0 recovers constant alpha_fs (no variation).",
    ]

    for ln in lines:
        echo(ln)

    write_text(REPORT_DIR / "lino_qed_test_summary.txt", "\n".join(lines))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
        sys.exit(130)
