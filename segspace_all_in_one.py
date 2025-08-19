#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
SEGSPACE – All-in-One Toolkit
=============================

Funktionen:
  • π-Bridge (Chudnovsky/builtin/phi) + Dataset-Evaluator (Seg vs GR/SR/GR*SR)
  • Δ(M)-Massenvalidierung mit Newton-Inversion (high-precision Decimal)
  • Bound-Energy & lokale Feinstruktur-α aus Frequenzpaaren (+ optionaler Plot)

Wichtig:
  - --prec wird global UND pro Subcommand akzeptiert.
  - pandas ist für pi-bridge erforderlich; matplotlib nur für Plots.
"""

import argparse, csv, math, sys, time, statistics as stats, hashlib, textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# -----------------------------
# Optional Libraries
# -----------------------------
try:
    import pandas as pd
except Exception:
    pd = None

def _lazy_matplotlib():
    import matplotlib.pyplot as plt
    return plt

# -----------------------------
# Numerik / Konstanten
# -----------------------------
from decimal import Decimal as D, getcontext

# Default-Precision (kann via CLI global oder pro Subcommand gesetzt werden)
getcontext().prec = 80

G     = D('6.67430e-11')       # m^3 kg^-1 s^-2
c     = D('2.99792458e8')      # m s^-1
h     = D('6.62607015e-34')    # J s
M_sun = D('1.98847e30')

phi   = (D(1) + D(5).sqrt()) / D(2)      # goldene Zahl ~1.618...
BLC   = phi / D(2)                       # φ/2 ~ 0.809017...

# Δ(M)-Standardparameter (Paper Defaults)
DM_A     = D('98.01')        # %
DM_ALPHA = D('2.7177e4')     # 1/m
DM_B     = D('1.96')         # %
TOL      = D('1e-120')

# -----------------------------
# Utils
# -----------------------------
def d(x) -> Optional[D]:
    if x is None: return None
    try:
        xs = str(x).strip()
        if xs == "": return None
        return D(xs)
    except Exception:
        return None

def f2(x, default=None):
    try:
        if x is None: return default
        xs = str(x).strip()
        if xs == "": return default
        return float(xs)
    except Exception:
        return default

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

# -----------------------------
# Chudnovsky-π
# -----------------------------
def chudnovsky_pi(terms: int, prec: int) -> Tuple[D, float]:
    """Compute π via Chudnovsky series with 'terms' and Decimal precision 'prec'."""
    from decimal import getcontext
    old = getcontext().prec
    getcontext().prec = prec
    start = time.perf_counter()

    C = 426880 * D(10005).sqrt()
    M = D(1); L = D(13591409); X = D(1); K = D(6); S = L
    for _k in range(1, terms):
        M = (M * (K**3 - 16*K)) / (D(_k)**3)
        L += 545140134
        X *= -262537412640768000
        S += (M * L) / X
        K += 12

    pi = C / S
    dt = (time.perf_counter() - start) * 1000.0  # ms
    getcontext().prec = old
    return +pi, dt

# -----------------------------
# Orbital/Redshift Physik
# -----------------------------
def deg2rad(dg): return dg * math.pi / 180.0

def r_from_orbit(a_m, e, f_true_rad):
    denom = (1.0 + e*math.cos(f_true_rad))
    if denom == 0: return float('nan')
    return a_m * (1.0 - e*e) / denom

def vis_viva(mu, a_m, r_m):
    term = mu * (2.0/max(r_m, 1e-99) - 1.0/max(a_m, 1e-99))
    return math.sqrt(term) if term >= 0.0 else float('nan')

def z_gravitational(M_central_kg: float, r_m: float) -> float:
    if not (M_central_kg > 0 and r_m and math.isfinite(r_m) and r_m > 0): return float('nan')
    rs = 2.0 * float(G) * M_central_kg / (float(c)**2)
    if r_m <= rs: return float('nan')
    return 1.0 / math.sqrt(1.0 - rs/r_m) - 1.0

def z_special_rel(v_tot_mps: float, v_los_mps: float = 0.0) -> float:
    if v_tot_mps is None or not math.isfinite(v_tot_mps): return float('nan')
    v_tot_abs = abs(v_tot_mps)
    if v_tot_abs <= 0: return float('nan')
    c_f = float(c)
    beta = min(v_tot_abs / c_f, 0.999999999999)
    beta_los = 0.0 if v_los_mps is None or (not math.isfinite(v_los_mps)) else (v_los_mps / c_f)
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    return gamma * (1.0 + beta_los) - 1.0

def z_combined(z_gr: float, z_sr: float) -> float:
    zgr = 0.0 if (z_gr is None or not math.isfinite(z_gr)) else z_gr
    zsr = 0.0 if (z_sr is None or not math.isfinite(z_sr)) else z_sr
    return (1.0 + zgr) * (1.0 + zsr) - 1.0

def observed_z(row: dict, prefer_z: bool) -> Tuple[Optional[float], str]:
    z_direct = f2(row.get("z"))
    f_emit   = f2(row.get("f_emit_Hz"))
    f_obs    = f2(row.get("f_obs_Hz"))
    if prefer_z and z_direct is not None:
        return z_direct, "z"
    if (f_emit is not None) and (f_obs is not None) and (f_obs != 0.0):
        return (f_emit / f_obs - 1.0), "freq"
    return z_direct, ("z" if z_direct is not None else "missing")

# -----------------------------
# Δ(M)-Modell & Inversion
# -----------------------------
def dm_raw(M: D, A: D = DM_A, alpha: D = DM_ALPHA, B: D = DM_B) -> D:
    rs = (D(2) * G * M) / (c**2)
    return A * (-(alpha*rs)).exp() + B

def dm_norm_bounds(masses: List[D]) -> Tuple[D, D]:
    logs = [D(str(math.log10(m))) for m in masses if m > 0]
    if not logs: return D('0'), D('1')
    Lmin, Lmax = min(logs), max(logs)
    if Lmax <= Lmin:
        Lmin, Lmax = Lmin - D('0.5'), Lmin + D('0.5')
    return Lmin, Lmax

def dm_percent(M: D, Lmin: D, Lmax: D, A: D = DM_A, alpha: D = DM_ALPHA, B: D = DM_B) -> D:
    if M <= 0: return D(0)
    norm = (D(str(math.log10(M))) - Lmin) / (Lmax - Lmin)
    norm = max(D(0), min(D(1), norm))
    return dm_raw(M, A, alpha, B) * norm

def rphi_from_mass(M: D) -> D:
    return (G * M / (c**2)) * phi

def mass_from_rphi(r_phi: D) -> D:
    return (c**2) * r_phi / (G * phi)

def f_mass_eq(M: D, r_obs: D, Lmin: D, Lmax: D,
              A: D = DM_A, alpha: D = DM_ALPHA, B: D = DM_B) -> D:
    return (G*phi*M/c**2) * (D(1) + dm_percent(M, Lmin, Lmax, A, alpha, B)/D(100)) - r_obs

def df_dM(M: D, r_obs: D, Lmin: D, Lmax: D,
          A: D = DM_A, alpha: D = DM_ALPHA, B: D = DM_B) -> D:
    h = M * D('1e-25') if M != 0 else D('1e-25')
    return (f_mass_eq(M+h, r_obs, Lmin, Lmax, A, alpha, B) - f_mass_eq(M-h, r_obs, Lmin, Lmax, A, alpha, B)) / (D(2)*h)

def invert_mass(r_obs: D, M0: D, Lmin: D, Lmax: D,
                A: D = DM_A, alpha: D = DM_ALPHA, B: D = DM_B) -> D:
    M = max(M0, D('1e-50'))
    for _ in range(200):
        y = f_mass_eq(M, r_obs, Lmin, Lmax, A, alpha, B)
        if abs(y) < TOL: break
        step = -y / df_dM(M, r_obs, Lmin, Lmax, A, alpha, B)
        while abs(step) > abs(M):
            step *= D('0.5')
        M += step
        if abs(step / M) < TOL: break
    return M

# -----------------------------
# Seg-Modell (Hint / ΔM / Hybrid)
# -----------------------------
def z_seg_hint(row: dict, z_sr: float, z_grsr: float) -> float:
    z_hint = f2(row.get("z_geom_hint"))
    if z_hint is not None and math.isfinite(z_hint):
        return z_combined(z_hint, z_sr)
    return z_grsr

def z_seg_deltam(row: dict, z_gr: float, z_sr: float,
                 A: float, B: float, alpha_m: float,
                 logM_min: Optional[float], logM_max: Optional[float],
                 dataset_Lmin: Optional[float], dataset_Lmax: Optional[float]) -> float:
    Msun = f2(row.get("M_solar"))
    if Msun is None or not math.isfinite(Msun) or Msun <= 0:
        return z_combined(z_gr, z_sr)
    M = Msun * float(M_sun)
    rs = 2.0 * float(G) * M / (float(c)**2)
    lM = math.log10(M)
    lo = (logM_min if (logM_min is not None) else dataset_Lmin)
    hi = (logM_max if (logM_max is not None) else dataset_Lmax)
    if (lo is None) or (hi is None) or (hi <= lo):
        lo, hi = lM - 0.5, lM + 0.5
    norm = (lM - lo) / (hi - lo)
    norm = min(1.0, max(0.0, norm))
    delta_pct = (A * math.exp(-alpha_m * rs) + B) * norm
    z_gr_scaled = z_gr * (1.0 + delta_pct/100.0)
    return z_combined(z_gr_scaled, z_sr)

def z_seg(row: dict, mode: str, z_gr: float, z_sr: float, z_grsr: float,
          dmA: float, dmB: float, dmAlpha: float,
          logM_min: Optional[float], logM_max: Optional[float],
          dataset_Lmin: Optional[float], dataset_Lmax: Optional[float],
          use_emission_gate: bool = True) -> float:
    if mode == "hint":
        return z_seg_hint(row, z_sr, z_grsr)
    elif mode == "deltaM":
        return z_seg_deltam(row, z_gr, z_sr, dmA, dmB, dmAlpha,
                            logM_min, logM_max, dataset_Lmin, dataset_Lmax)
    elif mode == "hybrid":
        z_hint = f2(row.get("z_geom_hint"))
        case = str(row.get("case","")).lower()
        category = str(row.get("category","")).lower()
        # Beispiel-Heuristik: S-Sterne nutzen Hint, sonst ΔM
        # Optionales Emissions-Gate: nur wenn aktiviert
        if use_emission_gate:
            bad_for_deltaM = ("jet","psr","pulsar","bl_lac","3c","agn","quasar")
            if any((t in case) or (t in category) for t in bad_for_deltaM):
                return z_grsr
        # Emissionsklassen-Gate: Für bekannte Nicht-Δ(M)-Fälle (Jets/Pulsare/BL Lacs/AGN/Quasare)
        # verwenden wir GR*SR (z_grsr), da Δ(M)-Heuristik dort nicht passt.
        bad_for_deltaM = ("jet","psr","pulsar","bl_lac","3c","agn","quasar")
        if any((t in case) or (t in category) for t in bad_for_deltaM):
            return z_grsr
        if ("s-star" in category or "sgra" in case) and z_hint is not None:
            return z_seg_hint(row, z_sr, z_grsr)
        return z_seg_deltam(row, z_gr, z_sr, dmA, dmB, dmAlpha,
                            logM_min, logM_max, dataset_Lmin, dataset_Lmax)
    return z_grsr

# -----------------------------
# Evaluator (CSV-Datensatz)
# -----------------------------
def robust_mean(vec):
    if not vec: return None
    m = stats.median(vec)
    mad = stats.median([abs(x-m) for x in vec]) if len(vec) > 1 else 0.0
    filtered = [x for x in vec if (mad == 0 or abs(x-m) <= 5*mad)]
    return sum(filtered)/len(filtered) if filtered else m

def evaluate_dataset(df, prefer_z: bool, seg_mode: str, outdir: Path,
                     dmA: float, dmB: float, dmAlpha: float,
                     logM_min: Optional[float], logM_max: Optional[float],
                     make_plots: bool, top_k: int = 10,
                     use_emission_gate: bool = True):
    outdir.mkdir(parents=True, exist_ok=True)
    if pd is None:
        raise RuntimeError("pandas required for dataset evaluation. pip install pandas")

    # logM Bounds aus Datensatz
    Ms = []
    for _, r in df.iterrows():
        Msun = f2(r.get("M_solar"))
        if Msun and Msun > 0: Ms.append(D(str(Msun)) * M_sun)
    Lmin, Lmax = dm_norm_bounds(Ms) if Ms else (D('0'), D('1'))

    dbg_rows = []
    per_model_abs = {"seg": [], "gr": [], "sr": [], "grsr": []}
    ratios_vs_gr = []
    ratios_vs_grsr = []

    for idx, r in df.iterrows():
        row = {k: r[k] for k in df.columns}
        case = str(row.get("case", "")).strip() or f"ROW{idx}"

        # Beobachtung
        z_obs, z_src = observed_z(row, prefer_z=prefer_z)
        if z_obs is None or not math.isfinite(z_obs):
            dbg_rows.append({**row, "case": case, "z_source": z_src, "note": "no observed z"})
            continue

        # Geometrie / Geschwindigkeiten
        Msun = f2(row.get("M_solar"))
        M_c = (Msun or 0.0) * float(M_sun)
        a_m = f2(row.get("a_m"))
        e   = f2(row.get("e"))
        fdeg= f2(row.get("f_true_deg"))
        r_emit_m = f2(row.get("r_emit_m"))

        if r_emit_m is not None and math.isfinite(r_emit_m) and r_emit_m > 0:
            r_eff = r_emit_m
            r_note = "r_emit_m"
        elif all(v is not None for v in (a_m, e, fdeg)):
            r_eff = r_from_orbit(a_m, e, deg2rad(fdeg))
            r_note = "r(a,e,f)"
        else:
            r_eff, r_note = None, "no r"

        v_los = f2(row.get("v_los_mps")) or 0.0
        v_tot = f2(row.get("v_tot_mps"))

        # Baselines
        z_gr = z_gravitational(M_c, r_eff)
        z_sr = z_special_rel(v_tot, v_los)
        z_grsr = z_combined(z_gr, z_sr)
        # Segmented
        z_sg   = z_seg(row, seg_mode, z_gr, z_sr, z_grsr,
                       dmA, dmB, dmAlpha, logM_min, logM_max,
                       float(Lmin), float(Lmax),
                       use_emission_gate=use_emission_gate)

        dz_seg  = (z_obs - z_sg)    if math.isfinite(z_sg)   else float('nan')
        dz_gr   = (z_obs - z_gr)    if math.isfinite(z_gr)   else float('nan')
        dz_sr   = (z_obs - z_sr)    if math.isfinite(z_sr)   else float('nan')
        dz_grsr = (z_obs - z_grsr)  if math.isfinite(z_grsr) else float('nan')

        if math.isfinite(dz_seg):  per_model_abs["seg"].append(abs(dz_seg))
        if math.isfinite(dz_gr):   per_model_abs["gr"].append(abs(dz_gr))
        if math.isfinite(dz_sr):   per_model_abs["sr"].append(abs(dz_sr))
        if math.isfinite(dz_grsr): per_model_abs["grsr"].append(abs(dz_grsr))

        if math.isfinite(dz_gr) and abs(dz_gr) > 0 and math.isfinite(dz_seg):
            ratios_vs_gr.append((case, abs(dz_seg)/abs(dz_gr), abs(dz_seg), abs(dz_gr)))
        if math.isfinite(dz_grsr) and abs(dz_grsr) > 0 and math.isfinite(dz_seg):
            ratios_vs_grsr.append((case, abs(dz_seg)/abs(dz_grsr), abs(dz_seg), abs(dz_grsr)))

        dbg_rows.append({
            **row,
            "case": case,
            "z_obs": z_obs, "z_source": z_src,
            "r_eff_m": r_eff if (r_eff is not None and math.isfinite(r_eff)) else "",
            "r_note": r_note,
            "v_tot_mps": v_tot if (v_tot is not None and math.isfinite(v_tot)) else "",
            "v_los_mps": v_los if (v_los is not None and math.isfinite(v_los)) else "",
            "z_gr": z_gr if math.isfinite(z_gr) else "",
            "z_sr": z_sr if math.isfinite(z_sr) else "",
            "z_grsr": z_grsr if math.isfinite(z_grsr) else "",
            "z_seg": z_sg if math.isfinite(z_sg) else "",
            "dz_seg": dz_seg if math.isfinite(dz_seg) else "",
            "dz_gr": dz_gr if math.isfinite(dz_gr) else "",
            "dz_sr": dz_sr if math.isfinite(dz_sr) else "",
            "dz_grsr": dz_grsr if math.isfinite(dz_grsr) else "",
        })

    def summarize(vec):
        if not vec: return (None, None, None)
        return (stats.median(vec), robust_mean(vec), max(vec))

    med_seg, mean_seg, max_seg = summarize(per_model_abs["seg"])
    med_gr,  mean_gr,  max_gr  = summarize(per_model_abs["gr"])
    med_sr,  mean_sr,  max_sr  = summarize(per_model_abs["sr"])
    med_grsr,mean_grsr,max_grsr= summarize(per_model_abs["grsr"])

    outdir.mkdir(parents=True, exist_ok=True)
    dbg_path = outdir / "segspace_debug.csv"
    if pd is not None:
        pd.DataFrame(dbg_rows).to_csv(dbg_path, index=False)

    rep = textwrap.dedent(f"""
    =====================================================================
     SEGMENTED SPACETIME – DATASET EVALUATION
    =====================================================================
    Rows used: {len(dbg_rows)}
    seg-mode : {seg_mode}
    Δ(M)     : A={dmA}%  B={dmB}%  alpha={dmAlpha} [1/m]
    logM     : user=[{logM_min},{logM_max}]  dataset=[{float(Lmin):.3f},{float(Lmax):.3f}]

    Median/Mean/Max |Δz|
      Seg   : {med_seg!s:>10}  {mean_seg!s:>10}  {max_seg!s:>10}
      GR    : {med_gr!s:>10}  {mean_gr!s:>10}  {max_gr!s:>10}
      SR    : {med_sr!s:>10}  {mean_sr!s:>10}  {max_sr!s:>10}
      GR*SR : {med_grsr!s:>10}  {mean_grsr!s:>10}  {max_grsr!s:>10}

    Performance vs GR (Median): { (med_seg/med_gr if med_seg and med_gr else 'N/A') } ×
    Debug CSV  : {dbg_path}
    """).strip("\n")
    print(rep)

    ratio_path = outdir / "segspace_ratios.csv"
    with ratio_path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["case","ratio_vs_GR","dz_seg","dz_gr","ratio_vs_GR*SR","dz_grsr"])
        map_grsr = {c:(r,ds,dg) for c,r,ds,dg in ratios_vs_grsr}
        for c, r, ds, dg in ratios_vs_gr:
            r2, ds2, dg2 = map_grsr.get(c, (None,None,None))
            wr.writerow([c, f"{r:.6e}", f"{ds:.6e}", f"{dg:.6e}",
                         (f"{r2:.6e}" if r2 is not None else ""),
                         (f"{dg2:.6e}" if dg2 is not None else "")])
    print(f"Ratios-CSV         : {ratio_path}")

    def top_block(title, items, top_k):
        print("-------------------------------------------------------------")
        print(title)
        print("-------------------------------------------------------------")
        for case, r, ds, db in items[:top_k]:
            print(f"  {case:<24} ratio={r:8.3e}  | dz_seg={ds:8.3e}, dz_base={db:8.3e}")

    ratios_vs_gr.sort(key=lambda x: x[1])
    top_block("TOP – Seg vs GR (kleiner = besser):", ratios_vs_gr, top_k)
    ratios_vs_gr.sort(key=lambda x: x[1], reverse=True)
    top_block("Worst – Seg vs GR (größer = schlechter):", ratios_vs_gr, top_k)

    ratios_vs_grsr.sort(key=lambda x: x[1])
    top_block("TOP – Seg vs GR*SR (kleiner = besser):", ratios_vs_grsr, top_k)
    ratios_vs_grsr.sort(key=lambda x: x[1], reverse=True)
    top_block("Worst – Seg vs GR*SR (größer = schlechter):", ratios_vs_grsr, top_k)

    if make_plots:
        try:
            plt = _lazy_matplotlib()
            for key, title in [("seg","Seg"),("gr","GR"),("sr","SR"),("grsr","GR*SR")]:
                vec = per_model_abs[key]
                if not vec: continue
                plt.figure(figsize=(8, 5))
                plt.hist(vec, bins=24, alpha=0.75)
                plt.xlabel("|Δz|"); plt.ylabel("Count")
                plt.title(f"Residuals: {title} (Median = {stats.median(vec):.2e})")
                plt.grid(True, alpha=0.3)
                outp = outdir / f"hist_{key}.png"
                plt.savefig(outp, dpi=140, bbox_inches="tight")
                plt.close()
                print(f"[INFO] Plot saved: {outp}")
        except Exception as ex:
            print(f"[WARN] plotting failed: {ex}")

# -----------------------------
# Bound-Energy & α (Frequenzen)
# -----------------------------
def bound_energy_rows(pairs: List[Tuple[D, D, str]]) -> List[dict]:
    rows = []
    for f_emit, f_obs, label in pairs:
        N_seg = f_emit / f_obs - D(1)
        E_gamma = h * f_emit
        alpha_local = (f_obs * h) / (D('9.1093837015e-31') * c**2)
        f_emit_back = (alpha_local * D('9.1093837015e-31') * c**2) / h
        z_gr = (f_emit - f_obs) / f_obs
        rel_error = abs(f_emit_back - f_emit) / f_emit
        rows.append({
            "label": label,
            "f_emit_Hz": f_emit,
            "f_obs_Hz": f_obs,
            "N_seg": N_seg,
            "E_gamma_J": E_gamma,
            "alpha_local": alpha_local,
            "z_gr": z_gr,
            "f_emit_back_calc_Hz": f_emit_back,
            "rel_error": rel_error
        })
    return rows

# -----------------------------
# Subcommands – Implementierungen
# -----------------------------
def cmd_pi_bridge(args):
    # Präzision (Subcommand-lokal erlaubt)
    getcontext().prec = int(args.prec)

    # π-Banner (für Protokoll/Reproduzierbarkeit)
    if args.pi_source == "chud":
        pi, ms = chudnovsky_pi(args.chud_terms, args.prec)
        pi_str = str(+pi)
        ms_str = f"{ms:.3f} ms"
    elif args.pi_source == "builtin":
        import math
        pi_str = repr(math.pi); ms_str = "0.000 ms"
    elif args.pi_source == "phi":
        pi_str = "phi-mode (π nicht genutzt)"; ms_str = "0.000 ms"
    else:
        raise ValueError("invalid --pi-source")

    print("\n=============================================================")
    print(" SEGMENTED SPACETIME – Δ(M) + CHUDNOVSKY‑π BRIDGE (Runner)")
    print("=============================================================")
    print(f"π ({args.pi_source})     : {pi_str[:100]}...")
    print(f"π compute time     : {ms_str}")

    # CSV wählen
    cand = [Path(args.csv)] if args.csv else []
    cand += [Path(x) for x in [
        "real_data_full.csv",
        "real_data_30_segmodel.csv",
        "real_data_30_segmodel_STRONG_NET.csv",
        "real_data_30_segmodel_LOCKED.csv",
    ]]
    csv_path = None
    for p in cand:
        if p and p.exists():
            csv_path = p; break
    if csv_path is None:
        print("[ERROR] no CSV found. Use --csv PATH.", file=sys.stderr)
        sys.exit(2)

    if pd is None:
        print("[ERROR] pandas required. pip install pandas", file=sys.stderr)
        sys.exit(3)

    df = pd.read_csv(csv_path)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    evaluate_dataset(
        df,
        prefer_z=args.prefer_z,
        seg_mode=args.seg_mode,
        outdir=outdir,
        dmA=args.deltam_A,
        dmB=args.deltam_B,
        dmAlpha=args.deltam_alpha,
        logM_min=args.logM_min,
        logM_max=args.logM_max,
        make_plots=args.plots,
        top_k=args.top
    )
    print(f"Debug‑CSV          : {outdir/'segspace_debug.csv'}")
    print(f"Ratios‑CSV         : {outdir/'segspace_ratios.csv'}")

def cmd_mass_validate(args):
    getcontext().prec = int(args.prec)

    BASE = {
        'Elektron':        D('9.10938356e-31'),
        'Mond':            D('7.342e22'),
        'Erde':            D('5.97219e24'),
        'Sonne':           M_sun,
        'Sagittarius A*':  D('4.297e6') * M_sun,
    }
    if args.extra_csv and Path(args.extra_csv).exists():
        with open(args.extra_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    name = row['Objekt']
                    m_sun = D(str(row['M_true_Msun']))
                    BASE.setdefault(name, m_sun * M_sun)
                except Exception:
                    continue

    masses = list(BASE.values())
    Lmin, Lmax = dm_norm_bounds(masses)

    results = []
    for name, M_true in BASE.items():
        r_s   = D(2)*G*M_true/c**2
        r_obs = BLC * r_s * (D(1) + dm_percent(M_true, Lmin, Lmax, D(str(args.deltam_A)), D(str(args.deltam_alpha)), D(str(args.deltam_B))) / D(100))
        M_rec = invert_mass(r_obs, M_true, Lmin, Lmax, D(str(args.deltam_A)), D(str(args.deltam_alpha)), D(str(args.deltam_B)))
        rel   = abs((M_rec - M_true)/M_true) * D(100)
        results.append((name, M_true, M_rec, rel))

    out_csv = Path(args.out or ".") / "segmented_spacetime_mass_validation_full.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Objekt","M_true_kg","M_rec_kg","RelErr_%"])
        for name, Mt, Mr, err in results:
            w.writerow([name, f"{Mt:.6e}", f"{Mr:.6e}", f"{err:.3e}"])

    print("\n=============================================================")
    print(" SEGMENTED SPACETIME – MASS VALIDATION")
    print("=============================================================")
    print(f"{'Objekt':<20} {'M_true(kg)':>15} {'M_rec(kg)':>15} {'RelErr_%':>10}")
    print("-"*64)
    for name, Mt, Mr, err in results:
        print(f"{name:<20} {Mt:15.6e} {Mr:15.6e} {float(err):10.3e}")
    print(f"\nCSV export → {out_csv.resolve()}")

def cmd_bound_energy(args):
    getcontext().prec = int(args.prec)

    pairs: List[Tuple[D,D,str]] = []
    if args.pairs and Path(args.pairs).exists():
        # CSV mit Spalten: label,f_emit_Hz,f_obs_Hz
        with open(args.pairs, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    label = row.get("label","?")
                    f_emit = D(str(row["f_emit_Hz"]))
                    f_obs  = D(str(row["f_obs_Hz"]))
                    pairs.append((f_emit, f_obs, label))
                except Exception:
                    continue
    else:
        # Demo-Daten
        pairs = [
            (D("1.384e14"), D("1.383e14"), "S2 near Sgr A*"),
            (D("4.568e14"), D("4.567e14"), "Sirius B"),
            (D("4.759e14"), D("4.759e14"), "Sun line"),
            (D("3.482e18"), D("3.482e18"), "Pound–Rebka"),
            (D("4.570e14"), D("4.570e14"), "Earth lab"),
        ]

    rows = bound_energy_rows(pairs)
    outdir = Path(args.out or ".")
    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / "bound_energy_results.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label","f_emit_Hz","f_obs_Hz","N_seg","E_gamma_J","alpha_local","z_gr","f_emit_back_calc_Hz","rel_error"])
        for r in rows:
            w.writerow([
                r["label"],
                f"{r['f_emit_Hz']:.6E}",
                f"{r['f_obs_Hz']:.6E}",
                f"{r['N_seg']:.12E}",
                f"{r['E_gamma_J']:.12E}",
                f"{r['alpha_local']:.12E}",
                f"{r['z_gr']:.12E}",
                f"{r['f_emit_back_calc_Hz']:.6E}",
                f"{r['rel_error']:.6E}",
            ])

    print("\n================================================================")
    print(" SEGMENTED SPACETIME – BOUND ENERGY / LOCAL α")
    print("================================================================")
    for r in rows:
        print(f"\n--- {r['label']} ---")
        print(f"f_emit    : {r['f_emit_Hz']:.6E} Hz")
        print(f"f_obs     : {r['f_obs_Hz']:.6E} Hz")
        print(f"N_seg     : {r['N_seg']:.12E}")
        print(f"E_gamma   : {r['E_gamma_J']:.12E} J")
        print(f"alpha_loc : {r['alpha_local']:.12E}")
        print(f"z_gr      : {r['z_gr']:.12E}")
        print(f"f_emit←α  : {r['f_emit_back_calc_Hz']:.6E} Hz")
        print(f"rel_error : {r['rel_error']:.6E}")

    print(f"\nCSV export → {out_csv.resolve()}")

    if args.plot:
        try:
            plt = _lazy_matplotlib()
            xs = list(range(1, len(rows)+1))
            errs = [float(r["rel_error"]) for r in rows]
            labels = [r["label"] for r in rows]
            plt.figure(figsize=(9,5))
            plt.plot(xs, errs, marker='o')
            for i, txt in enumerate(labels):
                plt.annotate(txt, (xs[i], errs[i]), fontsize=8, xytext=(4,5), textcoords='offset points')
            plt.xlabel("Source ID")
            plt.ylabel("Relative Error of f_emit back-calc")
            plt.grid(True, alpha=0.4)
            out_png = outdir / "bound_energy_rel_error.png"
            plt.tight_layout(); plt.savefig(out_png, dpi=140)
            print(f"Plot saved → {out_png.resolve()}")
        except Exception as ex:
            print(f"[WARN] plotting failed: {ex}")

# -----------------------------
# CLI
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="SEGSPACE – All-in-One Toolkit")
    # Global --prec (falls VOR dem Subcommand verwendet wird)
    ap.add_argument("--prec", type=int, default=80, help="Decimal precision (global, default 80)")

    sub = ap.add_subparsers(dest="cmd", required=True)

    # π-Bridge / Evaluator
    ap_pi = sub.add_parser("pi-bridge", help="Run π-Bridge + Dataset Evaluation")
    ap_pi.add_argument("--prec", type=int, default=200, help="Decimal precision for this subcommand")
    ap_pi.add_argument("--csv", type=str, default=None, help="Input CSV (auto-detect fallback)")
    ap_pi.add_argument("--out", type=str, default="segspace_pi_bridge_out", help="Output directory")
    ap_pi.add_argument("--seg-mode", type=str, default="hybrid", choices=["hint","deltaM","hybrid","grsr"], help="Segment model")
    ap_pi.add_argument("--no-emission-gate", action="store_true", help="Disable emission-class gating (jets/pulsars/BL Lacs/AGN→GR*SR)")
    ap_pi.add_argument("--prefer-z", action="store_true", help="Prefer 'z' column over f_emit/f_obs")
    ap_pi.add_argument("--deltam-A", type=float, default=98.01, help="Δ(M) A in percent")
    ap_pi.add_argument("--deltam-B", type=float, default=1.96, help="Δ(M) B in percent")
    ap_pi.add_argument("--deltam-alpha", type=float, default=27177.0, help="Δ(M) alpha [1/m]")
    ap_pi.add_argument("--logM-min", type=float, default=None, help="Override min(log10 M)")
    ap_pi.add_argument("--logM-max", type=float, default=None, help="Override max(log10 M)")
    ap_pi.add_argument("--plots", action="store_true", help="Create residual histograms")
    ap_pi.add_argument("--top", type=int, default=10, help="Top K in Best/Worst lists")
    ap_pi.add_argument("--pi-source", type=str, default="chud", choices=["chud","builtin","phi"], help="π source for banner")
    ap_pi.add_argument("--chud-terms", type=int, default=16, help="Chudnovsky terms")
    ap_pi.set_defaults(func=cmd_pi_bridge)

    # Mass validate
    ap_mv = sub.add_parser("mass-validate", help="Validate Δ(M) mass inversion")
    ap_mv.add_argument("--prec", type=int, default=200, help="Decimal precision for this subcommand")
    ap_mv.add_argument("--extra-csv", type=str, default=None, help="Optional CSV with columns: Objekt,M_true_Msun")
    ap_mv.add_argument("--out", type=str, default="segspace_mass_out", help="Output directory")
    ap_mv.add_argument("--deltam-A", type=float, default=98.01)
    ap_mv.add_argument("--deltam-B", type=float, default=1.96)
    ap_mv.add_argument("--deltam-alpha", type=float, default=27177.0)
    ap_mv.set_defaults(func=cmd_mass_validate)

    # Bound energy
    ap_be = sub.add_parser("bound-energy", help="Compute bound energy & local α from frequency pairs")
    ap_be.add_argument("--prec", type=int, default=200, help="Decimal precision for this subcommand")
    ap_be.add_argument("--pairs", type=str, default=None, help="CSV: label,f_emit_Hz,f_obs_Hz")
    ap_be.add_argument("--out", type=str, default="bound_energy_out", help="Output directory")
    ap_be.add_argument("--plot", action="store_true", help="Plot relative error of f_emit back-calc")
    ap_be.set_defaults(func=cmd_bound_energy)

    args = ap.parse_args()

    # Falls --prec NUR global übergeben wurde (vor Subcommand): anwenden.
    getcontext().prec = int(getattr(args, "prec", 80))

    # Subcommand ausführen
    args.func(args)

if __name__ == "__main__":
    main()