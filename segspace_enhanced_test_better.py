#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segspace_enhanced_test_better.py (Improved version with velocity fixes)
Enhanced test runner for Segmented Spacetime vs GR/SR baselines with data cleaning.

New Features
------------
- Automatic velocity correction for nearby stars with negative v_tot
- Improved SR computation for non-orbital objects
- Enhanced debugging output with correction tracking
- Better handling of radial vs total velocities
- Hybrid model support (hint + deltaM combination)

Usage
-----
  python segspace_enhanced_test_better.py --csv real_data_full.csv --prefer-z --seg-mode hint --plots --junit
  python segspace_enhanced_test_better.py --csv real_data_full.csv --seg-mode deltaM --deltam-A 3.5 --deltam-B 0.2 --plots
  python segspace_enhanced_test_better.py --csv real_data_full.csv --seg-mode hybrid --plots --junit

© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

from __future__ import annotations
import argparse, csv, hashlib, math, sys, textwrap, statistics as stats
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

# Physical constants
G = 6.67430e-11
c = 299_792_458.0
M_sun = 1.98847e30

# -----------------------------
# Utils
# -----------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def f2(x, default=None):
    try:
        if x is None: return default
        xs = str(x).strip()
        if xs == "": return default
        return float(xs)
    except Exception:
        return default

def deg2rad(d): return d * math.pi / 180.0

# -----------------------------
# Velocity correction utilities
# -----------------------------

def fix_stellar_velocities(row: dict, category: str) -> tuple[float, str]:
    """
    Korrigiert negative Geschwindigkeiten für normale Sterne.
    
    Args:
        row: CSV row dictionary
        category: Object category string
        
    Returns:
        (v_total_corrected, correction_note)
    """
    v_tot = f2(row.get("v_tot_mps"))
    v_los = f2(row.get("v_los_mps")) or 0.0
    
    # Spezialbehandlung für normale Sterne (nicht-relativistische Objekte)
    if category in ["nearby-stars", "wolf-rayet", "luminous-blue"]:
        if v_tot is not None and v_tot < 0:
            # Negative v_tot sind wahrscheinlich Radialgeschwindigkeiten
            v_radial = abs(v_tot)
            
            # Schätze typische Tangentialgeschwindigkeit für Sterntyp
            source_str = str(row.get("source", "")).lower()
            if "giant" in source_str or "supergiant" in source_str:
                v_tangential = 30000  # 30 km/s für Riesen
            elif "dwarf" in source_str or "main" in source_str:
                v_tangential = 15000  # 15 km/s für Zwerge
            else:
                v_tangential = 20000  # 20 km/s für Hauptreihensterne
                
            # Pythagoras: v_total = sqrt(v_radial² + v_tangential²)
            v_tot_corrected = math.sqrt(v_radial**2 + v_tangential**2)
            return v_tot_corrected, f"fixed_negative(v_rad={v_radial:.0f},v_tan={v_tangential:.0f})"
            
        elif v_tot is None and abs(v_los) > 1000:
            # Wenn nur v_los vorhanden, schätze v_total
            v_radial = abs(v_los)
            v_tangential = 25000  # Typisch für Feldsterne
            v_tot_corrected = math.sqrt(v_radial**2 + v_tangential**2)
            return v_tot_corrected, f"estimated_from_v_los(v_rad={v_radial:.0f},v_tan={v_tangential:.0f})"
    
    return v_tot, "original"

# -----------------------------
# Orbital / redshift physics
# -----------------------------

def r_from_orbit(a_m, e, f_true_rad):
    """Kepler ellipse radius at true anomaly f: r = a(1-e^2) / (1 + e cos f)"""
    denom = (1.0 + e*math.cos(f_true_rad))
    if denom == 0:
        return float('nan')
    return a_m * (1.0 - e*e) / denom

def vis_viva(mu, a_m, r_m):
    """Orbital speed from vis-viva: v = sqrt(mu*(2/r - 1/a))"""
    term = mu * (2.0/max(r_m, 1e-99) - 1.0/max(a_m, 1e-99))
    return math.sqrt(term) if term >= 0.0 else float('nan')

def z_gravitational(M_central_kg, r_m):
    """Gravitational redshift at radius r relative to infinity: 1/sqrt(1 - rs/r) - 1."""
    if M_central_kg <= 0 or r_m is None or not math.isfinite(r_m) or r_m <= 0:
        return float('nan')
    rs = 2.0 * G * M_central_kg / (c**2)
    if r_m <= rs:
        return float('nan')
    return 1.0 / math.sqrt(1.0 - rs/r_m) - 1.0

def z_special_rel(v_tot_mps, v_los_mps=0.0):
    """SR redshift: gamma*(1 + beta_los) - 1; beta=v/c; beta_los=v_los/c."""
    if v_tot_mps is None or not math.isfinite(v_tot_mps):
        return float('nan')
    
    # Handle negative velocities by taking absolute value
    v_tot_abs = abs(v_tot_mps)
    if v_tot_abs <= 0:
        return float('nan')
        
    beta = min(v_tot_abs / c, 0.999999999999)
    beta_los = 0.0 if v_los_mps is None or (not math.isfinite(v_los_mps)) else (v_los_mps / c)
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    return gamma * (1.0 + beta_los) - 1.0

def z_combined(z_gr, z_sr):
    zgr = 0.0 if (z_gr is None or not math.isfinite(z_gr)) else z_gr
    zsr = 0.0 if (z_sr is None or not math.isfinite(z_sr)) else z_sr
    return (1.0 + zgr) * (1.0 + zsr) - 1.0

# -----------------------------
# CSV ingest & provenance
# -----------------------------

def observed_z_from_row(row: dict, prefer_z: bool):
    z_direct = f2(row.get("z"))
    f_emit   = f2(row.get("f_emit_Hz"))
    f_obs    = f2(row.get("f_obs_Hz"))
    if prefer_z and z_direct is not None:
        return z_direct, "z"
    if (f_emit is not None) and (f_obs is not None) and (f_obs != 0.0):
        return (f_emit / f_obs - 1.0), "freq"
    return z_direct, ("z" if z_direct is not None else "missing")

def is_strong_row(row: dict) -> bool:
    return all([
        f2(row.get("a_m")) is not None,
        f2(row.get("e")) is not None,
        f2(row.get("f_true_deg")) is not None,
        f2(row.get("M_solar")) is not None,
    ])

# -----------------------------
# Built-in Seg model
# -----------------------------

def z_seg_pred_hint(row: dict, z_sr: float, z_grsr: float) -> float:
    z_hint = f2(row.get("z_geom_hint"))
    if z_hint is not None and math.isfinite(z_hint):
        return z_combined(z_hint, z_sr)
    return z_grsr

def z_seg_pred_deltam(row: dict, z_gr: float, z_sr: float,
                      A_pct: float, B_pct: float, alpha: float,
                      logM_min: float|None, logM_max: float|None,
                      dataset_logM_min: float|None, dataset_logM_max: float|None) -> float:
    """
    Δ(M) = (A·e^(−α·r_s) + B) · norm(log10 M)
    A,B in PERCENT (e.g., 4.0 = 4%)
    r_s from central mass M (kg); norm(log10 M) in [0,1] from dataset or overrides.

    FIXED: Apply ΔM as a RELATIVE scaling to z_GR ONLY:
       z_GR_scaled = z_GR * (1 + ΔM_frac)
       z_seg = (1 + z_GR_scaled)*(1 + z_SR) - 1
    """
    M_solar = f2(row.get("M_solar"))
    if M_solar is None or not math.isfinite(M_solar) or M_solar <= 0:
        return z_combined(z_gr, z_sr)  # fallback

    M = M_solar * M_sun
    rs = 2.0 * G * M / (c**2)

    # norm(log10 M) bounds
    lM = math.log10(M)
    lo = (logM_min if (logM_min is not None) else dataset_logM_min)
    hi = (logM_max if (logM_max is not None) else dataset_logM_max)
    if (lo is None) or (hi is None) or (hi <= lo):
        lo, hi = lM - 0.5, lM + 0.5
    norm = (lM - lo) / (hi - lo)
    norm = min(1.0, max(0.0, norm))

    deltaM_pct  = (A_pct * math.exp(-alpha * rs) + B_pct) * norm
    deltaM_frac = deltaM_pct / 100.0

    # *** FIX: scale only z_GR, not (1+z_GR) ***
    z_gr_scaled = z_gr * (1.0 + deltaM_frac)
    return z_combined(z_gr_scaled, z_sr)

def z_seg_pred_hybrid(row: dict, z_gr: float, z_sr: float, z_grsr: float,
                      dmA: float, dmB: float, dmAlpha: float,
                      logM_min: float|None, logM_max: float|None,
                      dataset_logM_min: float|None, dataset_logM_max: float|None) -> float:
    """Hybrid approach: use hint for S-stars, deltaM for others"""
    z_hint = f2(row.get("z_geom_hint"))
    category = str(row.get("category", "")).lower()
    
    # Use hint mode for S-stars with available z_geom_hint
    if ("s-star" in category or "sgra" in str(row.get("case", "")).lower()) and z_hint is not None:
        return z_seg_pred_hint(row, z_sr, z_grsr)
    else:
        # Use deltaM for other objects
        return z_seg_pred_deltam(row, z_gr, z_sr, dmA, dmB, dmAlpha,
                                logM_min, logM_max, dataset_logM_min, dataset_logM_max)

def z_seg_pred(row: dict, mode: str, z_gr: float, z_sr: float, z_grsr: float,
               dmA: float, dmB: float, dmAlpha: float,
               logM_min: float|None, logM_max: float|None,
               dataset_logM_min: float|None, dataset_logM_max: float|None) -> float:
    if mode == "hint":
        return z_seg_pred_hint(row, z_sr, z_grsr)
    elif mode == "deltaM":
        return z_seg_pred_deltam(row, z_gr, z_sr, dmA, dmB, dmAlpha,
                                 logM_min, logM_max, dataset_logM_min, dataset_logM_max)
    elif mode == "hybrid":
        return z_seg_pred_hybrid(row, z_gr, z_sr, z_grsr, dmA, dmB, dmAlpha,
                                logM_min, logM_max, dataset_logM_min, dataset_logM_max)
    # default/fallback
    return z_grsr

# -----------------------------
# Core evaluation
# -----------------------------

def evaluate(df, prefer_z: bool, seg_mode: str, outdir: Path, make_plots: bool, write_junit: bool,
             dmA: float, dmB: float, dmAlpha: float, logM_min: float|None, logM_max: float|None):
    outdir.mkdir(parents=True, exist_ok=True)

    # Dataset logM min/max (for deltaM normalization)
    Ms = []
    for _, r in df.iterrows():
        Msun = f2(r.get("M_solar"))
        if Msun is not None and math.isfinite(Msun) and Msun > 0:
            Ms.append(Msun * M_sun)
    if Ms:
        logs = [math.log10(m) for m in Ms]
        dataset_logM_min = min(logs)
        dataset_logM_max = max(logs)
        if abs(dataset_logM_max - dataset_logM_min) < 1e-12:
            m = dataset_logM_min
            dataset_logM_min, dataset_logM_max = m - 0.5, m + 0.5
    else:
        dataset_logM_min = dataset_logM_max = None

    dbg_rows = []
    per_model_abs = {"seg": [], "gr": [], "sr": [], "grsr": []}
    strong_count = 0
    velocity_corrections = 0

    for idx, r in df.iterrows():
        row = {k: r[k] for k in df.columns}

        case = str(row.get("case", "")).strip() or f"ROW{idx}"
        category = str(row.get("category", "")).strip()

        # observed z
        z_obs, z_src = observed_z_from_row(row, prefer_z=prefer_z)
        if z_obs is None:
            dbg_rows.append({**row, "case": case, "z_source": z_src, "note": "no observed z"})
            print(f"[WARN] {case}: no observed z (source={z_src}) – skipping residuals")
            continue

        # strong?
        strong = is_strong_row(row)
        if strong:
            strong_count += 1

        # central mass (kg)
        M_solar = f2(row.get("M_solar"))
        M_c = (M_solar or 0.0) * M_sun

        # r_eff
        a_m = f2(row.get("a_m"))
        e   = f2(row.get("e"))
        fdeg= f2(row.get("f_true_deg"))
        r_emit_m = f2(row.get("r_emit_m"))
        if r_emit_m is not None and math.isfinite(r_emit_m) and r_emit_m > 0:
            r_eff = r_emit_m
            r_note = "r_emit_m"
        elif strong and all(v is not None for v in (a_m, e, fdeg)):
            r_eff = r_from_orbit(a_m, e, deg2rad(fdeg))
            r_note = "r(a,e,f)"
        else:
            r_eff = None
            r_note = "no r"

        # velocities with improved handling
        v_los = f2(row.get("v_los_mps"))
        if (v_los is None) or (not math.isfinite(v_los)):
            v_los = 0.0

        # Apply velocity corrections for problematic objects
        v_tot_raw = f2(row.get("v_tot_mps"))
        v_tot, v_correction = fix_stellar_velocities(row, category)
        if v_correction != "original":
            velocity_corrections += 1
            
        # Orbital velocity calculation (if needed)
        if (v_tot is None or not math.isfinite(v_tot)) and (M_c > 0.0) and (r_eff not in (None, 0.0)) and (a_m not in (None, 0.0)):
            mu = G * M_c
            v_tot = vis_viva(mu, a_m, r_eff)
            v_correction = "vis_viva_orbital"

        # model reds
        z_gr = z_gravitational(M_c, r_eff)
        z_sr = z_special_rel(v_tot, v_los)
        if not math.isfinite(z_sr):
            print(f"[WARN] {case}: SR not computed (v_tot={v_tot}, v_los={v_los}, r_note={r_note}, a={a_m}, e={e}, fdeg={fdeg}, M_solar={M_solar})")

        z_grsr = z_combined(z_gr, z_sr)
        z_seg  = z_seg_pred(row, seg_mode, z_gr, z_sr, z_grsr,
                            dmA, dmB, dmAlpha, logM_min, logM_max,
                            dataset_logM_min, dataset_logM_max)

        # residuals
        dz_seg  = (z_obs - z_seg)   if math.isfinite(z_seg)  else float('nan')
        dz_gr   = (z_obs - z_gr)    if math.isfinite(z_gr)   else float('nan')
        dz_sr   = (z_obs - z_sr)    if math.isfinite(z_sr)   else float('nan')
        dz_grsr = (z_obs - z_grsr)  if math.isfinite(z_grsr) else float('nan')

        if math.isfinite(dz_seg):  per_model_abs["seg"].append(abs(dz_seg))
        if math.isfinite(dz_gr):   per_model_abs["gr"].append(abs(dz_gr))
        if math.isfinite(dz_sr):   per_model_abs["sr"].append(abs(dz_sr))
        if math.isfinite(dz_grsr): per_model_abs["grsr"].append(abs(dz_grsr))

        # debug row with enhanced information
        rs_dbg = (2.0 * G * M_c / (c**2)) if (M_c > 0) else ""
        dm_pct, dm_norm = "", ""
        if seg_mode in ["deltaM", "hybrid"] and (M_c > 0):
            lM = math.log10(M_c)
            lo = (logM_min if (logM_min is not None) else dataset_logM_min)
            hi = (logM_max if (logM_max is not None) else dataset_logM_max)
            if (lo is None) or (hi is None) or (hi <= lo):
                lo, hi = lM - 0.5, lM + 0.5
            dm_norm = min(1.0, max(0.0, (lM - lo)/(hi - lo)))
            dm_pct = (dmA * math.exp(-dmAlpha * (rs_dbg if rs_dbg != "" else 0.0)) + dmB) * dm_norm

        dbg_rows.append({
            **row,
            "case": case, "category": category,
            "z_obs": z_obs, "z_source": z_src,
            "r_eff_m": r_eff if (r_eff is not None and math.isfinite(r_eff)) else "",
            "r_note": r_note,
            "v_tot_original": v_tot_raw if (v_tot_raw is not None and math.isfinite(v_tot_raw)) else "",
            "v_tot_corrected": v_tot if (v_tot is not None and math.isfinite(v_tot)) else "",
            "v_correction_method": v_correction,
            "v_los_mps_eff": v_los if (v_los is not None and math.isfinite(v_los)) else "",
            "z_gr": z_gr if math.isfinite(z_gr) else "",
            "z_sr": z_sr if math.isfinite(z_sr) else "",
            "z_grsr": z_grsr if math.isfinite(z_grsr) else "",
            "z_seg": z_seg if math.isfinite(z_seg) else "",
            "dz_seg": dz_seg if math.isfinite(dz_seg) else "",
            "dz_gr": dz_gr if math.isfinite(dz_gr) else "",
            "dz_sr": dz_sr if math.isfinite(dz_sr) else "",
            "dz_grsr": dz_grsr if math.isfinite(dz_grsr) else "",
            "strong": strong,
            "rs_m": rs_dbg,
            "deltaM_percent": dm_pct,
            "log10M_norm": dm_norm,
        })

    # Summaries
    def summarize(vec):
        if not vec: return (None, None, None)
        return (stats.median(vec), sum(vec)/len(vec), max(vec))

    med_seg, mean_seg, max_seg = summarize(per_model_abs["seg"])
    med_gr,  mean_gr,  max_gr  = summarize(per_model_abs["gr"])
    med_sr,  mean_sr,  max_sr  = summarize(per_model_abs["sr"])
    med_grsr,mean_grsr,max_grsr= summarize(per_model_abs["grsr"])

    # Write debug CSV
    dbg_path = outdir / "_enhanced_debug.csv"
    if pd is not None:
        pd.DataFrame(dbg_rows).to_csv(dbg_path, index=False)
    else:
        keys = list(dbg_rows[0].keys()) if dbg_rows else ["note"]
        with dbg_path.open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=keys); wr.writeheader()
            for r in dbg_rows: wr.writerow({k: r.get(k, "") for k in keys})

    # Enhanced Report
    rep = textwrap.dedent(f"""
    ========================================================================
     SEGSPACE — ENHANCED TEST REPORT (IMPROVED)
    ========================================================================
    Rows used: {len(dbg_rows)}   |   Strong rows: {sum(1 for r in dbg_rows if r.get('strong'))}
    Velocity corrections applied: {velocity_corrections}
    seg-mode : {seg_mode}
    deltaM   : A={dmA}%  B={dmB}%  alpha={dmAlpha}  logM_min={logM_min}  logM_max={logM_max}
               dataset_logM_min={dataset_logM_min}  dataset_logM_max={dataset_logM_max}

    Median/Mean/Max |Δz|
      Seg   : {med_seg!s:>10}  {mean_seg!s:>10}  {max_seg!s:>10}
      GR    : {med_gr!s:>10}  {mean_gr!s:>10}  {max_gr!s:>10}
      SR    : {med_sr!s:>10}  {mean_sr!s:>10}  {max_sr!s:>10}
      GR*SR : {med_grsr!s:>10}  {mean_grsr!s:>10}  {max_grsr!s:>10}

    Performance vs GR:
      Seg   : {(med_seg/med_gr if med_seg and med_gr else 'N/A')!s:>10}x  {"✓ BETTER" if med_seg and med_gr and med_seg < med_gr else "✗ worse"}
      SR    : {(med_sr/med_gr if med_sr and med_gr else 'N/A')!s:>10}x
      GR*SR : {(med_grsr/med_gr if med_grsr and med_gr else 'N/A')!s:>10}x

    Debug CSV : {dbg_path}
    """).strip("\n")

    (outdir / "enhanced_report.txt").write_text(rep, encoding="utf-8")
    print(rep)

    # Optional plots
    if make_plots:
        try:
            import matplotlib.pyplot as plt
            for key, title in [("seg","Seg"),("gr","GR"),("sr","SR"),("grsr","GR*SR")]:
                vec = per_model_abs[key]
                if not vec: continue
                plt.figure(figsize=(8, 6))
                plt.hist(vec, bins=20, alpha=0.7)
                plt.xlabel("|Δz|")
                plt.ylabel("Count")
                plt.title(f"Residuals: {title} (Median = {stats.median(vec):.2e})")
                plt.grid(True, alpha=0.3)
                outp = outdir / f"hist_{key}.png"
                plt.savefig(outp, dpi=120, bbox_inches="tight")
                plt.close()
                print(f"[INFO] Plot saved: {outp}")
        except Exception as ex:
            print(f"[WARN] plotting failed: {ex}")

    # Optional JUnit
    if write_junit:
        junit_path = outdir / "enhanced_junit.xml"
        ok = True
        if (med_seg is not None) and (med_gr is not None):
            ok = (med_seg <= 1.2 * med_gr)
        junit = f'''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="segspace_enhanced" tests="1" failures="{0 if ok else 1}">
  <testcase classname="segspace" name="median_comparison">
    {"" if ok else f"<failure message='Seg median {med_seg} > 1.2 * GR median {med_gr}'/>"}
  </testcase>
</testsuite>
'''
        junit_path.write_text(junit, encoding="utf-8")
        print(f"[INFO] JUnit: {junit_path}")

# -----------------------------
# Main
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Enhanced tests for segmented spacetime vs GR/SR baselines (improved version)")
    ap.add_argument("--csv", type=str, default=None, help="Input CSV (default: auto-detect common names)")
    ap.add_argument("--out", type=str, default="out", help="Output directory")
    ap.add_argument("--prefer-z", action="store_true", help="Prefer z column over f_emit/f_obs if both present")
    ap.add_argument("--seg-mode", type=str, default="hint", choices=["hint","grsr","deltaM","hybrid"],
                    help="Built-in Seg model: 'hint' uses z_geom_hint; 'grsr' equals GR*SR; 'deltaM' applies Δ(M) scaling; 'hybrid' combines hint+deltaM")
    # deltaM params
    ap.add_argument("--deltam-A", type=float, default=4.0, help="A in percent (default 4.0)")
    ap.add_argument("--deltam-B", type=float, default=0.0, help="B in percent (default 0.0)")
    ap.add_argument("--deltam-alpha", type=float, default=1e-11, help="alpha [1/m] (default 1e-11)")
    ap.add_argument("--logM-min", type=float, default=None, help="override min(log10 M) for Δ(M) norm")
    ap.add_argument("--logM-max", type=float, default=None, help="override max(log10 M) for Δ(M) norm")
    ap.add_argument("--plots", action="store_true", help="Generate residual histograms")
    ap.add_argument("--junit", action="store_true", help="Write a simple JUnit summary")
    args = ap.parse_args()

    outdir = Path(args.out)

    # Pick CSV
    cand = []
    if args.csv:
        cand.append(Path(args.csv))
    cand += [Path(x) for x in [
        "real_data_full.csv",
        "real_data_30_segmodel.csv",
        "real_data_30_segmodel_STRONG_NET.csv",
        "real_data_30_segmodel_LOCKED.csv",
    ]]
    csv_path = None
    for p in cand:
        if p.exists():
            csv_path = p
            break
    if csv_path is None:
        print("[ERROR] no CSV found. Use --csv PATH.", file=sys.stderr)
        sys.exit(2)

    # Hash
    try:
        h = sha256_file(csv_path)
        print(f"[INFO] CSV: {csv_path} | SHA256={h}")
    except Exception:
        print(f"[INFO] CSV: {csv_path}")

    # Load
    if pd is None:
        print("[ERROR] pandas required. pip install pandas", file=sys.stderr)
        sys.exit(3)
    df = pd.read_csv(csv_path)

    evaluate(
        df, prefer_z=args.prefer_z, seg_mode=args.seg_mode, outdir=outdir,
        make_plots=args.plots, write_junit=args.junit,
        dmA=args.deltam_A, dmB=args.deltam_B, dmAlpha=args.deltam_alpha,
        logM_min=args.logM_min, logM_max=args.logM_max
    )

if __name__ == "__main__":
    main()
