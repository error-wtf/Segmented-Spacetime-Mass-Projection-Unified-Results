#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ All-in-One Terminal Runner v3 (module-native)
- Uses z_gravitational / z_special_rel / z_combined / z_seg_pred exported by the module.
- Portable, deterministic, no fitting.
- Robust casting for masses (M_solar) and radii (r_emit_m).
"""
import sys, os, json, time, hashlib, math, textwrap
from pathlib import Path
from statistics import median
from math import isfinite as _isfinite
import numpy as np
import argparse
import numpy as np
import matplotlib.pyplot as plt

def fmt_sig(x, sig=3):
    try:
        x = float(x)
    except:
        return "n/a"
    if not np.isfinite(x):
        return "n/a"
    ax = abs(x)
    if (ax != 0 and (ax >= 1e6 or ax < 1e-3)):
        return f"{x:.{sig}e}"
    else:
        # significant-figure-ish formatting
        s = f"{x:.{sig}g}"
        # ensure decimal point for small values (pretty)
        if "e" not in s and "." not in s:
            s = s + ".0"
        return s

def maybe_save_raws(raws, outdir, enable=False):
    if not enable: return None
    import csv
    outdir.mkdir(parents=True, exist_ok=True)
    raw_path = outdir / "raws_full.csv"
    keys = ["case","M_solar","abs_seg","abs_grsr","abs_gr","abs_sr"]
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in raws:
            w.writerow({k: r.get(k, "") for k in keys})
    return raw_path

def maybe_plots(raws, outdir, enable=False):
    if not enable: return []
    outdir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    df = pd.DataFrame(raws)
    figs = []

    # Histogram for each model
    for key, label in [("abs_seg","SEG"), ("abs_grsr","GR×SR"), ("abs_gr","GR"), ("abs_sr","SR")]:
        if key in df and df[key].notna().any():
            plt.figure(figsize=(7,5))
            df[key].dropna().astype(float).plot(kind="hist", bins=30)
            plt.xlabel("|Δz|")
            plt.ylabel("Count")
            plt.title(f"Histogram of |Δz| — {label}")
            p = outdir / f"hist_abs_{label.replace('×','x')}.png"
            plt.tight_layout(); plt.savefig(p, dpi=300); plt.close()
            figs.append(p)

    # ECDF SEG vs GR×SR
    if {"abs_seg","abs_grsr"}.issubset(df.columns):
        s = df["abs_seg"].dropna().astype(float).sort_values()
        g = df["abs_grsr"].dropna().astype(float).sort_values()
        if len(s)>0 and len(g)>0:
            ys = (np.arange(1, len(s)+1))/len(s)
            yg = (np.arange(1, len(g)+1))/len(g)
            plt.figure(figsize=(7,5))
            plt.plot(s.values, ys, label="SEG")
            plt.plot(g.values, yg, label="GR×SR")
            plt.xlabel("|Δz|"); plt.ylabel("ECDF"); plt.title("ECDF — SEG vs GR×SR")
            plt.legend()
            p = outdir / "ecdf_abs_SEG_vs_GRSR.png"
            plt.tight_layout(); plt.savefig(p, dpi=300); plt.close()
            figs.append(p)

    # Boxplot SEG vs GR×SR
    if {"abs_seg","abs_grsr"}.issubset(df.columns):
        s = df["abs_seg"].dropna().astype(float).values
        g = df["abs_grsr"].dropna().astype(float).values
        if len(s)>0 and len(g)>0:
            plt.figure(figsize=(7,5))
            plt.boxplot([s, g], labels=["SEG","GR×SR"])
            plt.ylabel("|Δz|"); plt.title("SEG vs GR×SR — |Δz|")
            p = outdir / "box_abs_SEG_vs_GRSR.png"
            plt.tight_layout(); plt.savefig(p, dpi=300); plt.close()
            figs.append(p)
    return figs


BANNER = "="*88
SUB = "-"*88

# Physical constants
M_sun = 1.98847e30

def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def wrap(msg, width=88):
    return "\n".join(textwrap.fill(str(msg), width=width).splitlines())

def pretty_block(title, body_lines):
    print(BANNER); print(f" {title}"); print(BANNER)
    for ln in body_lines: print(wrap(ln)); print()

def find_file(names, bases):
    for base in bases:
        for nm in names:
            p = (base / nm).resolve()
            if p.exists(): return p
    return None

def ffloat(x):
    try: return float(x)
    except Exception: return float("nan")

def finite(x):
    try: return _isfinite(float(x))
    except Exception: return False

def mass_from_row(row):
    for key in ("M_solar","M","mass_solar","Mcentral","M☉","M_sun"):
        if key in row and finite(row[key]): return ffloat(row[key])
    return float("nan")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--save-raws', action='store_true', help='save residuals CSV to full_pipeline/reports')
    parser.add_argument('--plots', action='store_true', help='save plots to full_pipeline/figures')
    args, _ = parser.parse_known_args()

    cwd = Path.cwd(); sdir = Path(__file__).resolve().parent
    csv_path = find_file(["real_data_full.csv"], [cwd, sdir])
    mod_path = find_file(["segspace_all_in_one_extended.py"], [cwd, sdir])
    if not csv_path or not mod_path:
        print(BANNER); print(" FATAL: Could not locate required files."); print(BANNER)
        print(" Looked for 'real_data_full.csv' and 'segspace_all_in_one_extended.py'")
        print(f" CWD : {cwd}"); print(f" DIR : {sdir}"); sys.exit(2)

    prov = {
        "csv": {"path": str(csv_path), "sha256": sha256(csv_path),
                "mtime_iso": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(csv_path.stat().st_mtime))},
        "module": {"path": str(mod_path), "sha256": sha256(mod_path),
                   "mtime_iso": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(mod_path.stat().st_mtime))},
        "script": {"path": str(Path(__file__).resolve())}
    }

    pretty_block("SEGMENTED SPACETIME — AUTO RUN (NO ARGS)",
        ["Deterministic SSZ evaluation with φ/2 coupling and fixed Δ(M).",
         "Direct calculations only — no fitting. Verbose comparison against GR, SR, GR×SR."])
    pretty_block("INPUTS & PROVENANCE (REPRODUCIBILITY)",
        [f"CSV file     : {prov['csv']['path']}",
         f"CSV sha256   : {prov['csv']['sha256']}",
         f"CSV mtime    : {prov['csv']['mtime_iso']}",
         f"Module file  : {prov['module']['path']}",
         f"Module sha256: {prov['module']['sha256']}",
         f"Module mtime : {prov['module']['mtime_iso']}",
         f"Runner script: {prov['script']['path']}"])

    import runpy
    ns = runpy.run_path(str(mod_path))
    load_csv = ns["load_csv"]
    evaluate_redshift = ns["evaluate_redshift"]
    z_gravitational = ns["z_gravitational"]
    z_special_rel = ns["z_special_rel"]
    z_combined = ns["z_combined"]
    z_seg_pred = ns["z_seg_pred"]
    A = float(ns["A"]); B = float(ns["B"]); ALPHA = float(ns["ALPHA"])

    pretty_block("PHYSICAL CONSTANTS & MODEL CHOICES",
        [f"Δ(M) parameters (fixed): A={A}, B={B}, ALPHA={ALPHA} (slow; dimensionless after norm).",
         "PPN outer series A(U)=1−2U+2U²+O(U³) ⇒ β_PPN=γ_PPN=1 (unchanged)."])

    print(f"[ECHO] Loading CSV: {csv_path}")
    rows = load_csv(csv_path)
    print(f"[ECHO] [OK] loaded rows: {len(rows)}")
    pretty_block("DATASET SUMMARY",
        [f"Rows loaded              : {len(rows)}",
         "Hybrid use of z (observed) else z_geom_hint. Deterministic predictions; no fit."])

    # Headline medians/sign-test from module
    res = evaluate_redshift(rows=rows, prefer_z=True, mode="hybrid",
                            dmA=A, dmB=B, dmAlpha=ALPHA, lo=None, hi=None,
                            drop_na=False, paired_stats=True, n_boot=0, bins=8,
                            do_plots=False, out_fig_dir=None, filter_complete_gr=True)
    med = res.get("med", {}); paired = res.get("paired", {})

    # Build raw residuals and masses using module-native functions
    raws = []
    for r in rows:
        z_obs = r.get("z")
        z_geom = r.get("z_geom_hint")
        z_use = ffloat(z_obs) if finite(z_obs) else (ffloat(z_geom) if finite(z_geom) else None)
        Msun = mass_from_row(r); Mkg = Msun * M_sun if finite(Msun) else float("nan")
        rem = ffloat(r.get("r_emit_m"))
        v_los = ffloat(r.get("v_los_mps")) if "v_los_mps" in r else 0.0
        v_tot = ffloat(r.get("v_tot_mps")) if "v_tot_mps" in r else float("nan")
        if not (finite(Mkg) and finite(rem) and rem > 0 and z_use is not None):
            continue
        zgr = z_gravitational(Mkg, rem)
        zsr = z_special_rel(v_tot, v_los)
        zgrsr = z_combined(zgr, zsr)
        lM = math.log10(Mkg) if finite(Mkg) and Mkg > 0 else math.log10(M_sun)
        zseg = z_seg_pred("hybrid", ffloat(z_geom), zgr, zsr, zgrsr, A, B, ALPHA, lM, None, None)
        def adiff(zm):
            try: return abs(float(z_use) - float(zm))
            except Exception: return float("nan")
        raws.append({"case": r.get("case"), "M_solar": Msun,
                     "abs_seg": adiff(zseg), "abs_grsr": adiff(zgrsr),
                     "abs_gr": adiff(zgr), "abs_sr": adiff(zsr)})

    
    # Mass-binned (robust: equal-count index bins, no duplicate edges)
    valid = [row for row in raws if finite(row["M_solar"])]
    valid.sort(key=lambda r: r["M_solar"])
    bins = []
    if len(valid) >= 8:
        parts = np.array_split(np.arange(len(valid)), 8)
        for i, idxs in enumerate(parts):
            if len(idxs) == 0:
                bins.append({"bin": i, "lo": float("nan"), "hi": float("nan"),
                             "count": 0, "med_seg": float("nan"), "med_grsr": float("nan")})
                continue
            sel = [valid[j] for j in idxs]
            lo = sel[0]["M_solar"]; hi = sel[-1]["M_solar"]
            def med_key(k):
                vals = [r[k] for r in sel if finite(r[k])]
                return float(median(vals)) if vals else float("nan")
            bins.append({"bin": i, "lo": float(lo), "hi": float(hi),
                         "count": len(sel), "med_seg": med_key("abs_seg"),
                         "med_grsr": med_key("abs_grsr")})
    else:
        def med_key_all(k):
            vals = [r[k] for r in valid if finite(r[k])]
            return float(median(vals)) if vals else float("nan")
        bins = [{"bin": 0, "lo": float("nan"), "hi": float("nan"),
                 "count": len(valid), "med_seg": med_key_all("abs_seg"),
                 "med_grsr": med_key_all("abs_grsr")}]

    # Print headline
    print(BANNER); print(" ACCURACY — MEDIAN ABSOLUTE REDSHIFT ERROR |Δz| (LOWER IS BETTER)"); print(BANNER)
    for mdl_key, mdl_name in [("seg","SSZ (φ/2 + ΔM)"), ("grsr","GR×SR"), ("gr","GR"), ("sr","SR")]:
        val = med.get(mdl_key, None)
        if val is not None: print(f"{mdl_name:<22}: {val:.6g}")
    print()

    if paired:
        print(SUB); print(" PAIRED SIGN-TEST — SSZ vs GR×SR (per-row absolute errors)"); print(SUB)
        for k in ["N_pairs","N_Seg_better","share_Seg_better","binom_two_sided_p"]:
            v = paired.get(k, None)
            if isinstance(v, float): print(f"{k:<22}: {v:.6g}")
            else: print(f"{k:<22}: {v}")
        print()

    print(SUB); print(" MASS-BINNED MEDIANS (SEG vs GR×SR) — with counts"); print(SUB)
    print(f"{'bin':>3} | {'lo→hi (M☉)':<24} | {'count':>5} | {'med_seg':>12} | {'med_grsr':>12}")
    print("-"*70)
    for b in bins:
        def fnum(x):
            try: return f"{float(x):.3g}"
            except Exception: return "n/a"
        rng = f"[{fmt_sig(b['lo'])}…{fmt_sig(b['hi'])}]"
        print(f"{b['bin']:>3} | {rng:<24} | {b['count']:>5} | {b['med_seg']:>12.6g} | {b['med_grsr']:>12.6g}")
    print()

    
    # Optional artifacts
    repdir = Path("full_pipeline/reports"); figdir = Path("full_pipeline/figures")
    raw_csv = maybe_save_raws(raws, repdir, enable=args.save_raws)
    figs = maybe_plots(raws, figdir, enable=args.plots)

    # Save summary
    outdir = Path("full_pipeline/reports"); outdir.mkdir(parents=True, exist_ok=True)
    summary = {"med": med, "paired": paired, "bins": bins, "raws": raws, "provenance": prov}
    out_json = outdir / "summary_full_terminal_v3.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(BANNER); print(" RUN COMPLETE"); print(BANNER)
    print(f"Summary JSON             : {out_json.resolve()}")
    print("Deterministic; no fitting. For figures, post-process this JSON.")
    if raw_csv:
        print(f"Raw residuals CSV        : {raw_csv.resolve()}")
    if figs:
        print("Figures:")
        for p in figs:
            print(" -", p.resolve())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(BANNER); print(" FATAL: An unexpected error occurred."); print(BANNER)
        traceback.print_exc(); sys.exit(1)
