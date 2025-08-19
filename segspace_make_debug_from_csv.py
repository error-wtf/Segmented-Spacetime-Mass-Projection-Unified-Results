
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segspace_make_debug_from_csv.py
--------------------------------
Recompute per-row predictions (z_gr, z_sr, z_grsr, z_seg) and residuals, and write
agent_out/reports/redshift_debug.csv, so that pair-tests can run even without v1 'all'.

Usage example:
  python segspace_make_debug_from_csv.py --csv .\real_data_full_with_r.csv --mode hybrid --prefer-z --filter-complete-gr

Options mirror the v2 evaluator:
  --csv PATH
  --mode {hybrid,deltaM,hint}
  --prefer-z
  --dmA, --dmB, --dmAlpha
  --drop-na
  --filter-complete-gr
  --outdir PATH (default ./agent_out)
"""
import argparse, csv, math, json
from pathlib import Path

G=6.67430e-11
c=2.99792458e8
M_sun=1.98847e30

def echo(msg):
    from datetime import datetime
    print(f"[ECHO {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def finite(x):
    try:
        return x is not None and math.isfinite(float(x))
    except Exception:
        return False

def fnum(x):
    try: 
        return float(x) if (x not in (None,"")) else None
    except: 
        return None

def load_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

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

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path("./real_data_full.csv"))
    ap.add_argument("--mode", choices=["hybrid","deltaM","hint"], default="hybrid")
    ap.add_argument("--prefer-z", action="store_true")
    ap.add_argument("--dmA", type=float, default=98.01)
    ap.add_argument("--dmB", type=float, default=1.96)
    ap.add_argument("--dmAlpha", type=float, default=2.7177e4)
    ap.add_argument("--drop-na", action="store_true")
    ap.add_argument("--filter-complete-gr", action="store_true")
    ap.add_argument("--outdir", type=Path, default=Path("./agent_out"))
    args=ap.parse_args()

    echo("MAKE DEBUG FROM CSV – START")
    if not args.csv.exists():
        echo(f"[ERR] CSV not found: {args.csv}"); return 2
    rows = load_csv(args.csv)

    # mass range for normalization
    Ms=[]
    for r in rows:
        Msun = fnum(r.get("M_solar"))
        if Msun and Msun>0: Ms.append(Msun*M_sun)
    if Ms:
        logs=[math.log10(m) for m in Ms]
        lo = min(logs); hi = max(logs)
    else:
        lo=hi=math.log10(M_sun)

    dbg=[]
    for i,r in enumerate(rows):
        case=(r.get("case") or f"ROW{i}").strip()
        z_direct=fnum(r.get("z")); f_emit=fnum(r.get("f_emit_Hz")); f_obs=fnum(r.get("f_obs_Hz"))
        if args.prefer_z and (z_direct is not None):
            z_obs=z_direct; z_src="z"
        elif f_emit and f_obs and f_obs!=0:
            z_obs=f_emit/f_obs-1.0; z_src="freq"
        else:
            z_obs=z_direct; z_src="z?"
        Msun=fnum(r.get("M_solar")) or 0.0; M_c=Msun*M_sun
        r_emit=fnum(r.get("r_emit_m"))
        v_tot=fnum(r.get("v_tot_mps")); v_los=fnum(r.get("v_los_mps")) or 0.0
        zgr=z_gr(M_c, r_emit) if (M_c and r_emit) else float('nan')
        zsr=z_sr(v_tot, v_los)
        zgrsr=z_comb(zgr, zsr)
        zhint=fnum(r.get("z_geom_hint"))
        lM=math.log10(M_c) if (M_c and M_c>0) else math.log10(M_sun)
        zseg=z_seg_pred(args.mode, zhint, zgr, zsr, zgrsr, args.dmA, args.dmB, args.dmAlpha, lM, lo, hi)

        def diff(a,b):
            try: return (a-b)
            except: return float('nan')

        dz_seg  = diff(z_obs, zseg) if (z_obs is not None and math.isfinite(zseg)) else float('nan')
        dz_gr   = diff(z_obs, zgr)  if (z_obs is not None and math.isfinite(zgr))  else float('nan')
        dz_sr_v = diff(z_obs, zsr)  if (z_obs is not None and math.isfinite(zsr))  else float('nan')
        dz_grsr = diff(z_obs, zgrsr)if (z_obs is not None and math.isfinite(zgrsr))else float('nan')

        row={**r, "case":case, "z_source":z_src,"z_obs":z_obs,
             "z_gr":zgr,"z_sr":zsr,"z_grsr":zgrsr,"z_seg":zseg,
             "dz_seg":dz_seg,"dz_gr":dz_gr,"dz_sr":dz_sr_v,"dz_grsr":dz_grsr,
             "abs_seg":abs(dz_seg) if finite(dz_seg) else float('nan'),
             "abs_gr": abs(dz_gr)  if finite(dz_gr)  else float('nan'),
             "abs_sr": abs(dz_sr_v)if finite(dz_sr_v)else float('nan'),
             "abs_grsr":abs(dz_grsr)if finite(dz_grsr)else float('nan')}
        dbg.append(row)

    if args.filter_complete_gr:
        before=len(dbg); dbg=[r for r in dbg if finite(r["abs_gr"])]
        echo(f"[FILTER] filter_complete_gr: kept {len(dbg)}/{before}")
    if args.drop_na:
        before=len(dbg); dbg=[r for r in dbg if all(finite(r[k]) for k in ("abs_seg","abs_gr","abs_sr","abs_grsr"))]
        echo(f"[FILTER] drop-na: kept {len(dbg)}/{before}")

    outdir=args.outdir/ "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    path=outdir/"redshift_debug.csv"
    cols=list(dbg[0].keys()) if dbg else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=cols); 
        if cols: 
            w.writeheader(); w.writerows(dbg)
    echo(f"[OK] wrote CSV: {path}")
    return 0

if __name__=="__main__":
    sys.exit(main())
