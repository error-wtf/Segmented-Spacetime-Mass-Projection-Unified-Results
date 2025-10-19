#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ΔM Tuner for Segmented Spacetime (standalone, no import of v2 script)
- Reads a dataset (default: real_data_full.csv)
- Evaluates medians |Δz| for SEG (hybrid), SR, GR×SR
- Grid-search over (A, B, Alpha) with user ranges
- Outputs CSV with scores and a JSON best summary
- Optional: paired sign-test SEG vs SR per grid point
"""
import argparse, csv, math, json, sys, itertools, random
from pathlib import Path

try:
    import numpy as np
except Exception:
    np = None

def echo(msg):
    from datetime import datetime
    print(f"[ECHO {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

# constants
G=6.67430e-11
c=2.99792458e8
M_sun=1.98847e30

def finite(x):
    try:
        return x is not None and math.isfinite(float(x))
    except Exception:
        return False

def read_csv(path: Path):
    rows=[]
    with path.open("r", encoding="utf-8", newline="") as f:
        rdr=csv.DictReader(f)
        for r in rdr: rows.append(r)
    return rows

def fnum(v):
    try:
        return float(v)
    except Exception:
        return float('nan')

def z_gr(M_c_kg, r_m):
    if M_c_kg is None or r_m is None or not math.isfinite(r_m) or r_m<=0: return float('nan')
    rs = 2.0 * G * float(M_c_kg) / (c**2)
    if r_m <= rs: return float('nan')
    return 1.0 / (math.sqrt(1.0 - rs/r_m)) - 1.0

def z_sr(v_tot_mps, v_los_mps=0.0):
    if v_tot_mps is None or not math.isfinite(v_tot_mps) or v_tot_mps <= 0: return float('nan')
    beta = min(abs(v_tot_mps)/c, 0.999999999999)
    beta_los = (v_los_mps or 0.0)/c
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    return gamma * (1.0 + beta_los) - 1.0

def z_comb(zgr, zsr):
    zgr = 0.0 if (zgr is None or not math.isfinite(zgr)) else zgr
    zsr = 0.0 if (zsr is None or not math.isfinite(zsr)) else zsr
    return (1.0 + zgr) * (1.0 + zsr) - 1.0

def median(v):
    vv = sorted([x for x in v if finite(x)])
    if not vv: return float('nan')
    if np is not None: return float(np.median(vv))
    n=len(vv); return vv[n//2] if n%2==1 else 0.5*(vv[n//2-1]+vv[n//2])

def eval_set(rows, prefer_z=True, mode="hybrid", A=98.01, B=1.96, Alpha=2.7177e4,
             lo=None, hi=None, filter_complete_gr=False, drop_na=False):
    Ms=[]
    for r in rows:
        Msun=fnum(r.get("M_solar"))
        if finite(Msun) and Msun>0: Ms.append(Msun*M_sun)
    if Ms:
        logs=[math.log10(m) for m in Ms]
        d_lo=min(logs); d_hi=max(logs)
        if hi is None: hi=d_hi
        if lo is None: lo=d_lo
    else:
        d_lo=d_hi=math.log10(M_sun); lo=lo or d_lo-0.5; hi=hi or d_hi+0.5

    dbg=[]
    for i,r in enumerate(rows):
        def g(k): 
            z = r.get(k)
            try: return float(z) if z not in (None,"") else None
            except: return None
        z_direct=g("z"); f_emit=g("f_emit_Hz"); f_obs=g("f_obs_Hz")
        if prefer_z and (z_direct is not None): z_obs=z_direct
        elif f_emit and f_obs and f_obs!=0: z_obs=f_emit/f_obs-1.0
        else: z_obs=z_direct

        Msun = g("M_solar") or 0.0; M_c = Msun*M_sun
        r_emit = g("r_emit_m")
        zgr = z_gr(M_c, r_emit) if (finite(M_c) and finite(r_emit)) else float('nan')
        zsr = z_sr(g("v_tot_mps"), g("v_los_mps") or 0.0)
        zgrsr = z_comb(zgr, zsr)
        zhint = g("z_geom_hint")
        lM = math.log10(M_c) if finite(M_c) and M_c>0 else math.log10(M_sun)

        def z_seg_pred(mode, z_hint, z_gr, z_sr, z_grsr, A,B,Alpha,lM,lo,hi):
            if mode=="hint" and z_hint is not None and math.isfinite(z_hint):
                return z_comb(z_hint, z_sr)
            if mode in ("deltaM","hybrid"):
                if mode=="hybrid" and (z_hint is not None and math.isfinite(z_hint)):
                    return z_comb(z_hint, z_sr)
                norm = 1.0 if (hi - lo) <= 0 else min(1.0, max(0.0, (lM - lo) / (hi - lo)))
                M = 10.0**lM
                rs = 2.0 * G * M / (c**2)
                deltaM_pct = (A * math.exp(-Alpha * rs) + B) * norm
                z_gr_scaled = z_gr * (1.0 + deltaM_pct/100.0)
                return z_comb(z_gr_scaled, z_sr)
            return z_grsr

        zseg = z_seg_pred(mode, zhint, zgr, zsr, zgrsr, A,B,Alpha,lM,lo,hi)

        def sd(a,b):
            try: return (a-b)
            except: return float('nan')

        dz_seg = sd(z_obs, zseg) if (z_obs is not None and math.isfinite(zseg)) else float('nan')
        dz_gr  = sd(z_obs, zgr)  if (z_obs is not None and math.isfinite(zgr))  else float('nan')
        dz_sr  = sd(z_obs, zsr)  if (z_obs is not None and math.isfinite(zsr))  else float('nan')
        dz_grsr= sd(z_obs, zgrsr)if (z_obs is not None and math.isfinite(zgrsr))else float('nan')

        row={"abs_seg":abs(dz_seg) if finite(dz_seg) else float('nan'),
             "abs_gr":abs(dz_gr) if finite(dz_gr) else float('nan'),
             "abs_sr":abs(dz_sr) if finite(dz_sr) else float('nan'),
             "abs_grsr":abs(dz_grsr) if finite(dz_grsr) else float('nan')}
        dbg.append(row)

    if filter_complete_gr:
        dbg=[r for r in dbg if finite(r["abs_gr"])]
    if drop_na:
        dbg=[r for r in dbg if all(finite(r[k]) for k in ("abs_seg","abs_gr","abs_sr","abs_grsr"))]

    seg=[r["abs_seg"] for r in dbg if finite(r["abs_seg"])]
    sr =[r["abs_sr"]  for r in dbg if finite(r["abs_sr"])]
    grsr=[r["abs_grsr"] for r in dbg if finite(r["abs_grsr"])]
    return {
        "N": len(dbg),
        "med_seg": median(seg),
        "med_sr": median(sr),
        "med_grsr": median(grsr),
        "pairs_vs_sr": list(zip(seg, sr)),
    }

def sign_test_pairs(pairs):
    # pairs: list of (seg, sr)
    n=len(pairs)
    k=sum(1 for a,b in pairs if finite(a) and finite(b) and (a<b))
    from math import comb
    if n==0: 
        return {"N_pairs":0,"N_Seg_better":0,"share":float('nan'),"p_two":float('nan')}
    def pmf(i):
        return comb(n,i)*(0.5**i)*(0.5**(n-i))
    pk=pmf(k)
    total=0.0
    for i in range(n+1):
        if pmf(i)<=pk+1e-18: total+=pmf(i)
    return {"N_pairs":n,"N_Seg_better":k,"share":k/n,"p_two":min(1.0,total)}

def parse_range(spec: str):
    # "start,stop,steps" inclusive grid
    a,b,s = spec.split(",")
    a=float(a); b=float(b); s=int(s)
    if s<=1: return [a]
    step=(b-a)/(s-1)
    return [a+i*step for i in range(s)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path("./real_data_full.csv"))
    ap.add_argument("--mode", choices=["hybrid","deltaM"], default="hybrid")
    ap.add_argument("--prefer-z", action="store_true")
    ap.add_argument("--A", type=str, default="60,140,9", help="grid: start,stop,steps (default 60..140 step ~10)")
    ap.add_argument("--B", type=str, default="0.5,3.0,6", help="grid: start,stop,steps")
    ap.add_argument("--ALPHA", type=str, default="10000,50000,6", help="grid: start,stop,steps")
    ap.add_argument("--drop-na", action="store_true")
    ap.add_argument("--filter-complete-gr", action="store_true")
    ap.add_argument("--paired-stats", action="store_true")
    ap.add_argument("--outdir", type=Path, default=Path("./agent_out"))
    args=ap.parse_args()

    echo("ΔM TUNER – START")
    if not args.csv.exists():
        echo(f"[ERR] csv not found: {args.csv}"); return 2
    rows = read_csv(args.csv)

    gridA = parse_range(args.A)
    gridB = parse_range(args.B)
    gridAL = parse_range(args.ALPHA)

    results=[]
    for A in gridA:
        for B in gridB:
            for AL in gridAL:
                res = eval_set(rows, prefer_z=args.prefer_z, mode=args.mode, A=A, B=B, Alpha=AL,
                               lo=None, hi=None, filter_complete_gr=args.filter_complete_gr, drop_na=args.drop_na)
                item={"A":A,"B":B,"Alpha":AL,
                      "N":res["N"],"med_seg":res["med_seg"],"med_sr":res["med_sr"],"med_grsr":res["med_grsr"]}
                if args.paired_stats:
                    st = sign_test_pairs(res["pairs_vs_sr"])
                    item.update({"pairs":st["N_pairs"],"seg_better":st["N_Seg_better"],
                                 "share_seg_better":st["share"],"p_two":st["p_two"]})
                results.append(item)
                echo(f"A={A:.4g} B={B:.4g} Alpha={AL:.4g} | N={item['N']} med_seg={item['med_seg']:.6g} med_sr={item['med_sr']:.6g} med_grsr={item['med_grsr']:.6g}" + (f" | p_two={item.get('p_two'):.3g}" if args.paired_stats else ""))

    # sort by med_seg ascending
    results_sorted = sorted(results, key=lambda r: (float('inf') if not finite(r["med_seg"]) else r["med_seg"]))

    args.outdir.mkdir(parents=True, exist_ok=True)
    rep_dir = args.outdir / "reports"
    rep_dir.mkdir(parents=True, exist_ok=True)

    # write CSV
    import csv as _csv
    csv_path = rep_dir / "deltaM_tuning_results.csv"
    if results_sorted:
        keys = list(results_sorted[0].keys())
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w=_csv.DictWriter(f, fieldnames=keys)
            w.writeheader(); w.writerows(results_sorted)
    # best summaries
    best_by_med = results_sorted[0] if results_sorted else {}
    best_by_p = None
    if args.paired_stats:
        r_valid = [r for r in results if "p_two" in r and finite(r["p_two"])]
        if r_valid:
            best_by_p = sorted(r_valid, key=lambda x: x["p_two"])[0]

    summary={"best_by_med_seg":best_by_med,"best_by_p_two":best_by_p,"grid_sizes":{"A":len(gridA),"B":len(gridB),"Alpha":len(gridAL)}}
    (rep_dir/"deltaM_tuning_best.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    echo(f"[OK] wrote CSV: {csv_path}")
    echo(f"[OK] wrote JSON: {rep_dir/'deltaM_tuning_best.json'}")
    echo("[DONE]")
    return 0

if __name__=="__main__":
    sys.exit(main())
