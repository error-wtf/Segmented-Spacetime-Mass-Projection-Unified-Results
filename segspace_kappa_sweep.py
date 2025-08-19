#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create CSV variants with r_emit_m = kappa * r_s (Schwarzschild radius).
- Input: real_data_full.csv
- Output: real_data_full_kappa_<K>.csv for each K
"""
import argparse, csv, math, sys
from pathlib import Path

G=6.67430e-11; c=299792458.0; M_sun=1.98847e30

def fnum(v):
    try:
        return float(v)
    except Exception:
        return float('nan')

def make_variant(src: Path, dst: Path, K: float):
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    cols = rows[0].keys()
    out=[]
    for r in rows:
        Msun = fnum(r.get("M_solar"))
        M = Msun*M_sun if math.isfinite(Msun) else float('nan')
        rs = 2*G*M/(c**2) if math.isfinite(M) and M>0 else float('nan')
        if math.isfinite(rs):
            r["r_emit_m"] = f"{K*rs}"
        else:
            r["r_emit_m"] = ""
        out.append(r)
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path("./real_data_full.csv"))
    ap.add_argument("--kappas", type=str, default="2.5,3,4,6")
    ap.add_argument("--outdir", type=Path, default=Path("."))
    args=ap.parse_args()

    ks=[float(x.strip()) for x in args.kappas.split(",")]
    for K in ks:
        dst = args.outdir / f"real_data_full_kappa_{str(K).replace('.','_')}.csv"
        make_variant(args.csv, dst, K)
        print(f"[OK] wrote {dst}")

if __name__=="__main__":
    main()
