#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paired test: SEG vs SR on |Δz|
- Reads agent_out/reports/redshift_debug.csv (or --debug-csv)
- Computes: N pairs (finite for both), N where SEG < SR, share, exact two-sided binomial p
- Also reports medians and optional bootstrap CIs for SEG and SR on the paired subset
"""
import argparse, csv, math, json, sys, os, random
from pathlib import Path

try:
    import numpy as np
except Exception:
    np = None

def echo(msg):
    from datetime import datetime
    print(f"[ECHO {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def finite(x):
    try:
        return x is not None and math.isfinite(float(x))
    except Exception:
        return False

def bootstrap_ci(data, n_boot=2000, q=0.5):
    if np is None or not data or n_boot <= 0:
        return None
    arr = np.array([d for d in data if np.isfinite(d)], dtype=float)
    if arr.size == 0:
        return None
    n = arr.size
    stats = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = np.random.randint(0, n, n)
        stats[i] = np.quantile(arr[idx], q)
    lo = float(np.quantile(stats, 0.025))
    hi = float(np.quantile(stats, 0.975))
    return [lo, hi]

def median(v):
    vv = sorted([x for x in v if finite(x)])
    if not vv: return float('nan')
    if np is not None: 
        return float(np.median(vv))
    n=len(vv)
    return vv[n//2] if n%2==1 else 0.5*(vv[n//2-1]+vv[n//2])

def binom_test_two_sided(k, n, p=0.5):
    from math import comb
    if n == 0:
        return float('nan')
    def pmf(i):
        return comb(n, i) * (p**i) * ((1-p)**(n-i))
    pk = pmf(k)
    total = 0.0
    for i in range(0, n+1):
        if pmf(i) <= pk + 1e-18:
            total += pmf(i)
    return min(1.0, total)

def read_debug_csv(path: Path):
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

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--debug-csv", type=Path, default=Path("./agent_out/reports/redshift_debug.csv"))
    ap.add_argument("--nboot", type=int, default=2000)
    args=ap.parse_args()

    echo("PAIRED TEST SEG vs SR – START")
    if not args.debug_csv.exists():
        echo(f"[ERR] not found: {args.debug_csv}")
        return 2
    rows=read_debug_csv(args.debug_csv)

    pairs=[]
    for r in rows:
        a = fnum(r.get("abs_seg"))
        b = fnum(r.get("abs_sr"))
        if finite(a) and finite(b):
            pairs.append((a,b,r.get("case","")))

    n=len(pairs)
    k=sum(1 for a,b,_ in pairs if a<b)  # SEG wins
    share = (k/n) if n>0 else float('nan')
    p_two = binom_test_two_sided(k, n, p=0.5) if n>0 else float('nan')

    seg_vals=[a for a,b,_ in pairs]
    sr_vals=[b for a,b,_ in pairs]

    out = {
        "N_pairs": n,
        "N_Seg_better": k,
        "share_Seg_better": share,
        "p_two_sided": p_two,
        "median_abs_seg": median(seg_vals),
        "median_abs_sr": median(sr_vals),
    }

    if args.nboot and args.nboot>0:
        out["ci95_median_abs_seg"] = bootstrap_ci(seg_vals, n_boot=args.nboot, q=0.5)
        out["ci95_median_abs_sr"]  = bootstrap_ci(sr_vals, n_boot=args.nboot, q=0.5)

    outdir = Path("./agent_out/reports")
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir/"paired_seg_vs_sr.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    echo(f"[OK] wrote JSON: {path}")
    echo(f"[RESULT] SEG better in {k}/{n} pairs (p≈{p_two:.3g}); medians: seg={out['median_abs_seg']}, sr={out['median_abs_sr']}")
    return 0

if __name__=="__main__":
    sys.exit(main())
