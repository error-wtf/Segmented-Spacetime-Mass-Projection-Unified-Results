
#!/usr/bin/env python3
"""
bound_energy.py — Herleitende (Paper-konsistente) Version
Reproduziert die S2/Sgr A*–Zahlen aus dem Paper via:
    E_emit = h * f_emit
    α·m_bound = (h * f_obs * N') / (N0 * c^2)
    m_bound = (α·m_bound) / α_fs
    α_local = E_emit / (m_bound * c^2)
    f_emit_check = α_local * m_bound * c^2 / h  ≈ f_emit

Standard = "locked" (reproduzierbare Paperzahlen). Exploration nur mit --unlock.

Copyright © 2025 Carmen Wrede & Lino Casu
All rights reserved.
"""

__authors__ = ["Carmen Wrede", "Lino Casu"]
__copyright__ = "© 2025 Carmen Wrede & Lino Casu"
__license__ = "All rights reserved"

import sys
import math
import argparse
from dataclasses import dataclass, asdict
from pathlib import Path

# --- Konstanten (mit SciPy-Fallback) ---
try:
    from scipy.constants import h, c
except Exception:
    h = 6.62607015e-34         # Planck [J*s] (exact)
    c = 299_792_458.0          # speed of light [m/s] (exact)

# CODATA 2018/2019 value (paper used 1/137.035999084)
ALPHA_FS_DEFAULT = 1.0 / 137.035999084

@dataclass
class Inputs:
    f_emit: float   # Emissionsfrequenz [Hz]
    f_obs: float    # Beobachtete Frequenz auf der Erde [Hz]
    N0: float       # Basis-Segmentdichte
    Nprime: float   # Segment-Faktor entlang der Sichtlinie
    alpha_fs: float # Feinstrukturkonstante

@dataclass
class Results:
    E_emit_J: float
    alpha_mbound_kg: float
    m_bound_kg: float
    alpha_local: float
    f_emit_check_Hz: float
    rel_error_f_emit: float
    z_gr: float
    N_seg: float
    delta_Nseg_zgr: float

def compute_E_emit(f_emit: float) -> float:
    return h * f_emit

def compute_alpha_mbound(f_obs: float, Nprime: float, N0: float) -> float:
    # α·m_bound = h * f_obs * N' / (N0 * c^2)
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

def run_calc(inp: Inputs) -> Results:
    E_emit = compute_E_emit(inp.f_emit)
    alpha_mbound = compute_alpha_mbound(inp.f_obs, inp.Nprime, inp.N0)
    m_bound = compute_m_bound(alpha_mbound, inp.alpha_fs)
    alpha_local = compute_alpha_local(E_emit, m_bound)
    f_emit_check = reconstruct_f_emit(alpha_local, m_bound)
    rel_err = abs(f_emit_check - inp.f_emit) / inp.f_emit if inp.f_emit else float("nan")
    zgr = compute_z_gr(inp.f_emit, inp.f_obs)
    Nseg = compute_N_seg(inp.f_emit, inp.f_obs, inp.N0)
    return Results(
        E_emit_J=E_emit,
        alpha_mbound_kg=alpha_mbound,
        m_bound_kg=m_bound,
        alpha_local=alpha_local,
        f_emit_check_Hz=f_emit_check,
        rel_error_f_emit=rel_err,
        z_gr=zgr,
        N_seg=Nseg,
        delta_Nseg_zgr=(Nseg - zgr),
    )

def print_summary(inp: Inputs, res: Results):
    print("="*65)
    print(" SEGMENTED SPACETIME — BOUND ENERGY (Derivation = Paper) ")
    print("="*65)
    print("© 2025 Carmen Wrede & Lino Casu – All rights reserved.")
    print("\nEingaben (locked):")
    print(f"  f_emit (Quelle) [Hz] : {inp.f_emit:.0f}")
    print(f"  f_obs  (Erde)  [Hz] : {inp.f_obs:.0f}")
    print(f"  N0                 : {inp.N0:.10f}")
    print(f"  N'                 : {inp.Nprime:.15f}")
    print(f"  alpha_fs           : {inp.alpha_fs:.12f}  (~1/137.035999084)")

    print("\nErgebnisse:")
    print(f"  E_emit = h·f_emit [J]        : {res.E_emit_J:.6e}")
    print(f"  α·m_bound [kg]               : {res.alpha_mbound_kg:.6e}")
    print(f"  m_bound [kg]                 : {res.m_bound_kg:.6e}")
    print(f"  alpha_local                  : {res.alpha_local:.6e}")
    print(f"  f_emit (rekonstruiert) [Hz]  : {res.f_emit_check_Hz:.6f}")
    print(f"  rel. Fehler f_emit           : {res.rel_error_f_emit:.3e}")
    print(f"  z_gr (klassisch)             : {res.z_gr:.9f}")
    print(f"  N_seg                        : {res.N_seg:.9f}")
    print(f"  N_seg - z_gr                 : {res.delta_Nseg_zgr:.9e}")

def main():
    parser = argparse.ArgumentParser(description="Bound energy — Paper-konsistente Herleitung (locked by default).")
    parser.add_argument("--unlock", action="store_true", help="Erlaubt das Überschreiben der Eingaben (Exploration).")
    parser.add_argument("--f-emit", type=float, default=138_394_255_537_000.0, help="Emissionsfrequenz [Hz]")
    parser.add_argument("--f-obs", type=float, default=134_920_458_147_000.0, help="Beobachtete Frequenz [Hz]")
    parser.add_argument("--N0", type=float, default=1.0000000028, help="Basis-Segmentdichte")
    parser.add_argument("--Nprime", type=float, default=1.102988010497717, help="Segment-Faktor N'")
    parser.add_argument("--alpha-fs", type=float, default=ALPHA_FS_DEFAULT, help="Feinstrukturkonstante")
    parser.add_argument("--out", type=str, default="bound_energy_results.csv", help="CSV-Datei für Ergebnisse")
    parser.add_argument("--no-csv", action="store_true", help="Kein CSV schreiben")
    parser.add_argument("--selftest", action="store_true", help="Prüft, ob f_emit rekonstruiert wird (Paper-Werte).")
    args = parser.parse_args()

    # LOCKED-Modus: Werte dürfen nur im --unlock-Modus überschrieben werden
    if not args.unlock:
        # ignore any user-provided overrides (keep defaults)
        f_emit = 138_394_255_537_000.0
        f_obs = 134_920_458_147_000.0
        N0 = 1.0000000028
        Nprime = 1.102988010497717
        alpha_fs = ALPHA_FS_DEFAULT
    else:
        f_emit = args.f_emit
        f_obs = args.f_obs
        N0 = args.N0
        Nprime = args.Nprime
        alpha_fs = args.alpha_fs

    inp = Inputs(f_emit=f_emit, f_obs=f_obs, N0=N0, Nprime=Nprime, alpha_fs=alpha_fs)
    res = run_calc(inp)
    print_summary(inp, res)

    # Selftest (nur sinnvoll im locked Modus)
    if args.selftest and not args.unlock:
        # numerisch harte Prüfung: f_emit Rekonstruktion
        if not math.isclose(res.f_emit_check_Hz, inp.f_emit, rel_tol=1e-12):
            print("[SELFTEST] FAIL: f_emit nicht korrekt rekonstruiert.")
            sys.exit(1)
        # zusätzliche Erwartungswerte (Papierzahlen, Toleranz)
        if not (abs(res.m_bound_kg - 1.503481e-34) / 1.503481e-34 < 5e-6):
            print("[SELFTEST] FAIL: m_bound weicht von Paperwert ab.")
            sys.exit(1)
        if not (abs(res.alpha_local - 6.786327e-3) / 6.786327e-3 < 5e-6):
            print("[SELFTEST] FAIL: alpha_local weicht von Paperwert ab.")
            sys.exit(1)
        print("[SELFTEST] PASS")

    # CSV
    if not args.no_csv:
        try:
            import pandas as pd
            df = pd.DataFrame([{
                "f_emit_Hz": inp.f_emit,
                "f_obs_Hz": inp.f_obs,
                "N0": inp.N0,
                "Nprime": inp.Nprime,
                "alpha_fs": inp.alpha_fs,
                "E_emit_J": res.E_emit_J,
                "alpha_mbound_kg": res.alpha_mbound_kg,
                "m_bound_kg": res.m_bound_kg,
                "alpha_local": res.alpha_local,
                "f_emit_check_Hz": res.f_emit_check_Hz,
                "rel_error_f_emit": res.rel_error_f_emit,
                "z_gr": res.z_gr,
                "N_seg": res.N_seg,
                "delta_Nseg_zgr": res.delta_Nseg_zgr,
            }])
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out, index=False)
            print(f"\n[INFO] CSV exportiert: {out.resolve()}")
        except Exception as e:
            print(f"[WARN] Konnte CSV nicht schreiben: {e}")

if __name__ == "__main__":
    main()
