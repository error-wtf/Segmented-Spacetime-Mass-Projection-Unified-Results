
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segspacetime_quick_tests.py — Kurztests mit realen Daten (S2) für das Segmentierungsmodell
=========================================================================================
Ziel:
- Einfache, reproduzierbare Checks der herleitenden Beziehungen aus dem Paper
- Benötigt: f_emit (Quelle), f_obs (Erde), N0, N' (ggf. aus Literatur)
- Verifiziert: m_bound, alpha_local und Rückrechnung f_emit
- Vergleicht: N_seg ~ z_gr

Standard: nutzt einen realen S2/Sgr A* Datensatz (f_emit/f_obs aus eurer Arbeit). Weitere
Fälle können per CSV nachgeladen werden.

CSV-Schema (Header):
case,f_emit_Hz,f_obs_Hz,N0,Nprime,alpha_fs

Beispielzeile (S2):
S2_SgrA*,138394255537000,134920458147000,1.0000000028,1.102988010497717,0.0072973525692838015

Ausgabe:
- Console-Report pro Fall (PASS/FAIL je Check)
- CSV: out/quick_tests_results.csv

© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

import sys, math, argparse, csv
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

# --- Konstanten ---
try:
    from scipy.constants import h, c
except Exception:
    h = 6.62607015e-34
    c = 299_792_458.0

ALPHA_FS_DEFAULT = 1.0 / 137.035999084

@dataclass
class Inputs:
    case: str
    f_emit: float
    f_obs: float
    N0: float = 1.0000000028
    Nprime: float = 1.102988010497717
    alpha_fs: float = ALPHA_FS_DEFAULT

@dataclass
class Results:
    case: str
    E_emit_J: float
    alpha_mbound_kg: float
    m_bound_kg: float
    alpha_local: float
    f_emit_check_Hz: float
    rel_error_f_emit: float
    z_gr: float
    N_seg: float
    delta_Nseg_zgr: float
    pass_recon: bool
    pass_zmatch: bool

def compute_E_emit(f_emit: float) -> float:
    return h * f_emit

def compute_alpha_mbound(f_obs: float, Nprime: float, N0: float) -> float:
    return (h * f_obs * Nprime) / (N0 * c**2)

def compute_m_bound(alpha_mbound: float, alpha_fs: float) -> float:
    return alpha_mbound / alpha_fs

def compute_alpha_local(E_emit: float, m_bound: float) -> float:
    return E_emit / (m_bound * c**2)

def reconstruct_f_emit(alpha_local: float, m_bound: float) -> float:
    return (alpha_local * m_bound * c**2) / h

def compute_z_gr(f_emit: float, f_obs: float) -> float:
    return (f_emit - f_obs) / f_obs

def compute_N_seg(f_emit: float, f_obs: float, N0: float) -> float:
    return f_emit / f_obs - N0

def eval_case(inp: Inputs, tol_recon=1e-12, tol_z=5e-8) -> Results:
    E_emit = compute_E_emit(inp.f_emit)
    alpha_mbound = compute_alpha_mbound(inp.f_obs, inp.Nprime, inp.N0)
    m_bound = compute_m_bound(alpha_mbound, inp.alpha_fs)
    alpha_local = compute_alpha_local(E_emit, m_bound)
    f_emit_check = reconstruct_f_emit(alpha_local, m_bound)
    rel_err = abs(f_emit_check - inp.f_emit) / inp.f_emit if inp.f_emit else float('nan')
    zgr = compute_z_gr(inp.f_emit, inp.f_obs)
    Nseg = compute_N_seg(inp.f_emit, inp.f_obs, inp.N0)
    pass_recon = (rel_err <= tol_recon)
    pass_zmatch = (abs(Nseg - zgr) <= tol_z)
    return Results(
        case=inp.case,
        E_emit_J=E_emit,
        alpha_mbound_kg=alpha_mbound,
        m_bound_kg=m_bound,
        alpha_local=alpha_local,
        f_emit_check_Hz=f_emit_check,
        rel_error_f_emit=rel_err,
        z_gr=zgr,
        N_seg=Nseg,
        delta_Nseg_zgr=(Nseg - zgr),
        pass_recon=pass_recon,
        pass_zmatch=pass_zmatch,
    )

def default_dataset():
    return [
        Inputs(
            case="S2_SgrA*",
            f_emit=138_394_255_537_000.0,
            f_obs=134_920_458_147_000.0,
            N0=1.0000000028,
            Nprime=1.102988010497717,
            alpha_fs=ALPHA_FS_DEFAULT,
        )
    ]

def load_csv(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                Inputs(
                    case=r.get("case","case"),
                    f_emit=float(r["f_emit_Hz"]),
                    f_obs=float(r["f_obs_Hz"]),
                    N0=float(r.get("N0", "1.0000000028")),
                    Nprime=float(r.get("Nprime", "1.102988010497717")),
                    alpha_fs=float(r.get("alpha_fs", str(ALPHA_FS_DEFAULT))),
                )
            )
    return rows

def main():
    ap = argparse.ArgumentParser(description="Kurztests für segmentierte Raumzeit mit realen Daten (S2 etc.).")
    ap.add_argument("--csv", type=str, help="Pfad zu real_data.csv (case,f_emit_Hz,f_obs_Hz,N0,Nprime,alpha_fs)")
    ap.add_argument("--out", type=str, default="out/quick_tests_results.csv", help="CSV-Ausgabe")
    ap.add_argument("--tol-recon", type=float, default=1e-12, help="Toleranz für f_emit-Rekonstruktion (relativ)")
    ap.add_argument("--tol-z", type=float, default=5e-8, help="Toleranz für |N_seg - z_gr|")
    args = ap.parse_args()

    cases = load_csv(Path(args.csv)) if args.csv else default_dataset()
    results = []
    print("="*72)
    print(" SEGMENTED SPACETIME — QUICK TESTS (real data where available) ")
    print("="*72)
    print("© 2025 Carmen Wrede & Lino Casu – All rights reserved.\n")

    for inp in cases:
        res = eval_case(inp, tol_recon=args.tol_recon, tol_z=args.tol_z)
        results.append(res)
        print(f"[{res.case}]")
        print(f"  E_emit = {res.E_emit_J:.6e} J")
        print(f"  α·m_bound = {res.alpha_mbound_kg:.6e} kg")
        print(f"  m_bound = {res.m_bound_kg:.6e} kg")
        print(f"  alpha_local = {res.alpha_local:.6e}")
        print(f"  f_emit_check = {res.f_emit_check_Hz:.6f} Hz   (rel_err={res.rel_error_f_emit:.3e})  PASS={res.pass_recon}")
        print(f"  z_gr = {res.z_gr:.9f},  N_seg = {res.N_seg:.9f},  Δ = {res.delta_Nseg_zgr:.3e}   PASS={res.pass_zmatch}")
        print()

    # CSV export
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if pd is None:
        # write trivial csv
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow([*Results.__annotations__.keys()])
            for r in results:
                w.writerow([getattr(r, k) for k in Results.__annotations__.keys()])
    else:
        df = pd.DataFrame([asdict(r) for r in results])
        df.to_csv(out, index=False)
    print(f"[INFO] Ergebnisse gespeichert: {out.resolve()}")

if __name__ == "__main__":
    main()
