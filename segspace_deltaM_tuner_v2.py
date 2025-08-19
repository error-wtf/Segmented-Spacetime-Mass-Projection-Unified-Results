
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segspace_deltaM_tuner_v2.py
===========================
ΔM-Tuning-Script (verbessert) für Segmented Spacetime.

Funktionen & Features
---------------------
- Robuste Grid-Spezifikation für A, B, Alpha:
  * "start,stop,steps" (linear inklusiv)
  * "lin:start,stop,steps"
  * "log:start,stop,steps" (log10-basiert)
  * "list:v1,v2,v3"
- Optionaler Random-Sweep zusätzlich zum Grid (--random N).
- Metriken: Mediane |Δz| für SEG, SR, GR×SR.
- Gepaarte Sign-Tests: SEG vs SR und SEG vs GR×SR.
- Bootstrap-CIs (Median) **nur** für die beste Konfiguration (schneller).
- Heatmaps: A×B (je Alpha das beste) + optional A×Alpha (B optimiert) und B×Alpha (A optimiert).
- Sicherheits-Preflight: Schreibt ausschließlich in ./agent_out/…
- Reproduzierbar: fester Seed.
- Echo-Logging jeder Phase.

Benutzung (Beispiele)
---------------------
Grid-Suche (wie in Paper-Defaults, mit gepaarten Tests & Heatmaps):
  python segspace_deltaM_tuner_v2.py --csv .\\real_data_full.csv --mode hybrid --prefer-z ^
    --A "60,140,9" --B "0.5,3.0,6" --ALPHA "10000,50000,6" ^
    --filter-complete-gr --paired both --ci 2000 --heatmaps --outdir .\\agent_out

Random + Grid kombiniert (z. B. 200 zufällige Samples innerhalb Ranges):
  python segspace_deltaM_tuner_v2.py --csv .\\real_data_full.csv --mode hybrid --prefer-z ^
    --A "60,140,9" --B "0.5,3.0,6" --ALPHA "10000,50000,6" ^
    --random 200 --A-range 50 160 --B-range 0.1 5.0 --ALPHA-range 5000 80000 ^
    --filter-complete-gr --paired both --outdir .\\agent_out

Ausgabe
-------
- agent_out/reports/deltaM_tuning_results.csv    # alle getesteten Punkte
- agent_out/reports/deltaM_tuning_best.json      # beste Konfiguration (nach med_seg & p-Werten)
- agent_out/reports/deltaM_best_debug.csv        # per-row Residuen für bester Punkt
- agent_out/figures/deltaM_heatmap_AB.png        # Heatmap med_seg vs A,B (Alpha optimiert)
- agent_out/figures/deltaM_heatmap_AAlpha.png    # (optional) Heatmap med_seg vs A,Alpha (B optimiert)
- agent_out/figures/deltaM_heatmap_BAlpha.png    # (optional) Heatmap med_seg vs B,Alpha (A optimiert)
"""

from __future__ import annotations
import argparse, csv, math, json, sys, random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional
try:
    import numpy as np
except Exception:
    np = None
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

# ────────────────────────────── Echo & Safety ──────────────────────────────

def echo(msg: str) -> None:
    from datetime import datetime
    print(f"[ECHO {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

@dataclass
class IOConfig:
    outdir: Path
    reports: Path
    figures: Path

def safety_preflight(outdir: Path) -> IOConfig:
    echo("="*80); echo(" SAFETY PREFLIGHT"); echo("="*80)
    outdir.mkdir(parents=True, exist_ok=True); echo(f"[OK] ensured: {outdir}")
    rep = outdir / "reports"; rep.mkdir(parents=True, exist_ok=True); echo(f"[OK] ensured: {rep}")
    figs = outdir / "figures"; figs.mkdir(parents=True, exist_ok=True); echo(f"[OK] ensured: {figs}")
    echo("[SAFE] All writes restricted to outdir subtree.")
    return IOConfig(outdir, rep, figs)

# ────────────────────────────── Physik/Funktionen ──────────────────────────────

G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98847e30

def finite(x: Any) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except Exception:
        return False

def fnum(v: Any) -> Optional[float]:
    try:
        return float(v) if (v not in (None, "")) else None
    except Exception:
        return None

def z_gr(M_c_kg: float, r_m: float) -> float:
    if M_c_kg is None or r_m is None or not math.isfinite(r_m) or r_m <= 0: return float('nan')
    rs = 2.0 * G * float(M_c_kg) / (c**2)
    if r_m <= rs: return float('nan')
    return 1.0 / (math.sqrt(1.0 - rs/r_m)) - 1.0

def z_sr(v_tot_mps: float, v_los_mps: float=0.0) -> float:
    if v_tot_mps is None or not math.isfinite(v_tot_mps) or v_tot_mps <= 0: return float('nan')
    beta = min(abs(v_tot_mps) / c, 0.999999999999)
    beta_los = (v_los_mps or 0.0) / c
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    return gamma * (1.0 + beta_los) - 1.0

def z_comb(zgr: float, zsr: float) -> float:
    zgr = 0.0 if (zgr is None or not math.isfinite(zgr)) else zgr
    zsr = 0.0 if (zsr is None or not math.isfinite(zsr)) else zsr
    return (1.0 + zgr) * (1.0 + zsr) - 1.0

def z_seg_pred(mode: str, z_hint: Optional[float], z_gr: float, z_sr_v: float, z_grsr: float,
               dmA: float, dmB: float, dmAlpha: float, lM: float, lo: float, hi: float) -> float:
    if mode == "hint" and z_hint is not None and math.isfinite(z_hint):
        return z_comb(z_hint, z_sr_v)
    if mode in ("deltaM", "hybrid"):
        if mode == "hybrid" and (z_hint is not None and math.isfinite(z_hint)):
            return z_comb(z_hint, z_sr_v)
        # Skalen-Normierung
        if (hi - lo) <= 0:
            norm = 1.0
        else:
            norm = (lM - lo) / (hi - lo)
            if norm < 0.0: norm = 0.0
            if norm > 1.0: norm = 1.0
        # ΔM-Formel
        M = 10.0**lM
        rs = 2.0 * G * M / (c**2)
        deltaM_pct = (dmA * math.exp(-dmAlpha * rs) + dmB) * norm
        z_gr_scaled = z_gr * (1.0 + deltaM_pct/100.0)
        return z_comb(z_gr_scaled, z_sr_v)
    return z_grsr

# ────────────────────────────── Datensatz & Auswertung ──────────────────────────────

def load_csv(path: Path) -> List[Dict[str, Any]]:
    echo(f"Loading CSV: {path}")
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    echo(f"[OK] loaded rows: {len(rows)}")
    return rows

def eval_set(rows: List[Dict[str, Any]], prefer_z: bool, mode: str,
             A: float, B: float, Alpha: float,
             lo: Optional[float], hi: Optional[float],
             filter_complete_gr: bool, drop_na: bool) -> Dict[str, Any]:

    # Massenbereich für Normierung
    Ms = []
    for r in rows:
        Msun = fnum(r.get("M_solar"))
        if Msun and Msun>0: Ms.append(Msun*M_sun)
    if Ms:
        logs = [math.log10(m) for m in Ms]; d_lo = min(logs); d_hi = max(logs)
        if hi is None: hi = d_hi
        if lo is None: lo = d_lo
    else:
        d_lo = d_hi = math.log10(M_sun); lo = lo or d_lo-0.5; hi = hi or d_hi+0.5

    dbg = []
    for i, r in enumerate(rows):
        case = (r.get("case") or f"ROW{i}").strip()
        z_direct = fnum(r.get("z"))
        f_emit = fnum(r.get("f_emit_Hz")); f_obs = fnum(r.get("f_obs_Hz"))
        if prefer_z and (z_direct is not None):
            z_obs = z_direct
        elif f_emit and f_obs and f_obs!=0:
            z_obs = f_emit/f_obs - 1.0
        else:
            z_obs = z_direct

        Msun = fnum(r.get("M_solar")) or 0.0
        M_c = Msun*M_sun
        r_emit = fnum(r.get("r_emit_m"))
        v_tot = fnum(r.get("v_tot_mps")); v_los = fnum(r.get("v_los_mps")) or 0.0

        zgr = z_gr(M_c, r_emit) if (finite(M_c) and finite(r_emit)) else float('nan')
        zsr = z_sr(v_tot, v_los)
        zgrsr = z_comb(zgr, zsr)
        zhint = fnum(r.get("z_geom_hint"))
        lM = math.log10(M_c) if (finite(M_c) and M_c>0) else math.log10(M_sun)
        zseg = z_seg_pred(mode, zhint, zgr, zsr, zgrsr, A, B, Alpha, lM, lo, hi)

        def sdiff(a,b):
            try: return (a-b)
            except: return float('nan')

        dz_seg = sdiff(z_obs, zseg) if (z_obs is not None and math.isfinite(zseg)) else float('nan')
        dz_gr  = sdiff(z_obs, zgr)  if (z_obs is not None and math.isfinite(zgr))  else float('nan')
        dz_sr  = sdiff(z_obs, zsr)  if (z_obs is not None and math.isfinite(zsr))  else float('nan')
        dz_grsr= sdiff(z_obs, zgrsr)if (z_obs is not None and math.isfinite(zgrsr))else float('nan')

        dbg.append({"case":case,"abs_seg":abs(dz_seg) if finite(dz_seg) else float('nan'),
                    "abs_gr":abs(dz_gr) if finite(dz_gr) else float('nan'),
                    "abs_sr":abs(dz_sr) if finite(dz_sr) else float('nan'),
                    "abs_grsr":abs(dz_grsr) if finite(dz_grsr) else float('nan')})

    if filter_complete_gr:
        before = len(dbg); dbg = [r for r in dbg if finite(r["abs_gr"])]
        echo(f"[FILTER] filter_complete_gr: kept {len(dbg)}/{before}")
    if drop_na:
        before = len(dbg); dbg = [r for r in dbg if all(finite(r[k]) for k in ("abs_seg","abs_gr","abs_sr","abs_grsr"))]
        echo(f"[FILTER] drop-na: kept {len(dbg)}/{before}")

    seg = [r["abs_seg"] for r in dbg if finite(r["abs_seg"])]
    sr  = [r["abs_sr"]  for r in dbg if finite(r["abs_sr"])]
    grsr= [r["abs_grsr"]for r in dbg if finite(r["abs_grsr"])]
    def median(v: List[float]) -> float:
        vv = sorted([x for x in v if finite(x)])
        if not vv: return float('nan')
        if np is not None: return float(np.median(vv))
        n=len(vv); return vv[n//2] if n%2==1 else 0.5*(vv[n//2-1]+vv[n//2])
    return {"N":len(dbg),"med_seg":median(seg),"med_sr":median(sr),"med_grsr":median(grsr),
            "pairs_vs_sr":list(zip(seg, sr)),"pairs_vs_grsr":list(zip(seg, grsr)),
            "dbg_rows":dbg}

def paired_sign_test(pairs: List[Tuple[float,float]]) -> Dict[str,Any]:
    n = len([1 for a,b in pairs if finite(a) and finite(b)])
    k = len([1 for a,b in pairs if finite(a) and finite(b) and (a<b)])  # SEG wins
    from math import comb
    if n==0:
        return {"N_pairs":0,"N_Seg_better":0,"share":float('nan'),"p_two":float('nan')}
    def pmf(i):
        return comb(n,i)*(0.5**i)*(0.5**(n-i))
    pk = pmf(k); total=0.0
    for i in range(n+1):
        if pmf(i) <= pk + 1e-18: total += pmf(i)
    return {"N_pairs":n,"N_Seg_better":k,"share":(k/n),"p_two":min(1.0,total)}

def bootstrap_ci_median(v: List[float], n_boot: int=2000) -> Optional[Tuple[float,float]]:
    if np is None or not v or n_boot<=0: return None
    arr = np.array([x for x in v if np.isfinite(x)], dtype=float)
    if arr.size==0: return None
    n = arr.size
    stats = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = np.random.randint(0, n, n)
        stats[i] = np.quantile(arr[idx], 0.5)
    lo = float(np.quantile(stats, 0.025)); hi = float(np.quantile(stats, 0.975))
    return (lo, hi)

# ────────────────────────────── Grid/Random Parser ──────────────────────────────

def parse_spec(spec: str) -> List[float]:
    s = spec.strip()
    if s.startswith("list:"):
        return [float(x) for x in s[5:].split(",") if x.strip()!=""]
    if s.startswith("lin:"):
        s = s[4:]
        a,b,n = s.split(","); a=float(a); b=float(b); n=int(n)
        if n<=1: return [a]
        step=(b-a)/(n-1)
        return [a+i*step for i in range(n)]
    if s.startswith("log:"):
        if np is None: raise RuntimeError("log-grid benötigt NumPy")
        s = s[4:]
        a,b,n = s.split(","); a=float(a); b=float(b); n=int(n)
        lo,hi = math.log10(a), math.log10(b)
        return [float(x) for x in np.logspace(lo,hi,n)]
    # fallback: "a,b,n"
    a,b,n = s.split(","); a=float(a); b=float(b); n=int(n)
    if n<=1: return [a]
    step=(b-a)/(n-1)
    return [a+i*step for i in range(n)]

def random_samples(n: int, ar: Tuple[float,float], br: Tuple[float,float], alr: Tuple[float,float], alpha_log: bool=False, seed: int=137) -> List[Tuple[float,float,float]]:
    rnd = random.Random(seed)
    out=[]
    for _ in range(max(0,n)):
        A = rnd.uniform(ar[0], ar[1])
        B = rnd.uniform(br[0], br[1])
        if alpha_log:
            lo,hi = math.log10(alr[0]), math.log10(alr[1])
            Alpha = 10**rnd.uniform(lo,hi)
        else:
            Alpha = rnd.uniform(alr[0], alr[1])
        out.append((A,B,Alpha))
    return out

# ────────────────────────────── Heatmaps ──────────────────────────────

def save_heatmap_AB(results: List[Dict[str,Any]], io: IOConfig) -> Optional[str]:
    if plt is None or np is None: 
        echo("[PLOT] matplotlib/numpy not available; skip heatmap AB"); return None
    # For each (A,B) keep best (min med_seg) over Alpha
    key = {}
    for r in results:
        A,B = r["A"], r["B"]
        cur = key.get((A,B))
        if (cur is None) or (r["med_seg"] < cur["med_seg"]):
            key[(A,B)] = r
    As = sorted(set(a for a,b in key.keys()))
    Bs = sorted(set(b for a,b in key.keys()))
    grid = np.full((len(Bs), len(As)), np.nan, dtype=float)
    for i,b in enumerate(Bs):
        for j,a in enumerate(As):
            r = key.get((a,b))
            if r is not None and finite(r["med_seg"]):
                grid[i,j] = r["med_seg"]
    import matplotlib
    matplotlib.rcParams.update({"axes.titlesize": "medium"})
    fig,ax = plt.subplots(figsize=(8,6))
    im = ax.imshow(grid, origin="lower", aspect="auto")
    ax.set_xticks(range(len(As))); ax.set_xticklabels([f"{a:.2g}" for a in As], rotation=60, ha="right")
    ax.set_yticks(range(len(Bs))); ax.set_yticklabels([f"{b:.2g}" for b in Bs])
    ax.set_xlabel("A"); ax.set_ylabel("B"); ax.set_title("med_seg Heatmap (best Alpha per A,B)")
    fig.colorbar(im, ax=ax, label="median |Δz| (SEG)")
    fp = io.figures / "deltaM_heatmap_AB.png"
    fig.tight_layout(); fig.savefig(fp, dpi=140); plt.close(fig)
    echo(f"[PLOT] wrote {fp}")
    return str(fp)

# (Optional extra heatmaps could be added similarly)
# ────────────────────────────── CLI ──────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="segspace_deltaM_tuner_v2", description="Improved ΔM tuning for Segmented Spacetime (grid + random, paired tests, CIs, heatmaps).")
    ap.add_argument("--csv", type=Path, default=Path("./real_data_full.csv"))
    ap.add_argument("--outdir", type=Path, default=Path("./agent_out"))
    ap.add_argument("--mode", choices=["hybrid","deltaM"], default="hybrid")
    ap.add_argument("--prefer-z", action="store_true")
    ap.add_argument("--filter-complete-gr", action="store_true")
    ap.add_argument("--drop-na", action="store_true")
    ap.add_argument("--A", type=str, default="60,140,9")
    ap.add_argument("--B", type=str, default="0.5,3.0,6")
    ap.add_argument("--ALPHA", type=str, default="10000,50000,6")
    ap.add_argument("--random", type=int, default=0, help="optional random samples count (in addition to grid)")
    ap.add_argument("--A-range", nargs=2, type=float, default=[60.0,140.0])
    ap.add_argument("--B-range", nargs=2, type=float, default=[0.5,3.0])
    ap.add_argument("--ALPHA-range", nargs=2, type=float, default=[10000.0,50000.0])
    ap.add_argument("--alpha-log", action="store_true", help="random Alpha sampling in log-space")
    ap.add_argument("--paired", choices=["none","sr","grsr","both"], default="both")
    ap.add_argument("--ci", type=int, default=2000, help="bootstrap N for CI of best medians (0=off)")
    ap.add_argument("--heatmaps", action="store_true")
    ap.add_argument("--seed", type=int, default=137)
    args = ap.parse_args(argv)

    random.seed(args.seed)
    io = safety_preflight(args.outdir)

    if not args.csv.exists():
        echo(f"[ERR] csv not found: {args.csv}"); return 2
    rows = load_csv(args.csv)

    # Build search set
    gridA = parse_spec(args.A)
    gridB = parse_spec(args.B)
    gridAL = parse_spec(args.ALPHA)
    echo(f"[GRID] A={len(gridA)} values, B={len(gridB)} values, Alpha={len(gridAL)} values")
    combos = [(A,B,AL) for A in gridA for B in gridB for AL in gridAL]

    if args.random and args.random>0:
        rnd = random_samples(args.random, tuple(args.A_range), tuple(args.B_range), tuple(args.ALPHA_range), alpha_log=args.alpha_log, seed=args.seed+1)
        combos.extend(rnd)
        echo(f"[RANDOM] added {len(rnd)} random samples")

    # Sweep
    results: List[Dict[str,Any]] = []
    for idx,(A,B,AL) in enumerate(combos, start=1):
        echo(f"[SWEEP {idx}/{len(combos)}] A={A:.6g} B={B:.6g} Alpha={AL:.6g}")
        res = eval_set(rows, prefer_z=args.prefer_z, mode=args.mode, A=A, B=B, Alpha=AL,
                       lo=None, hi=None, filter_complete_gr=args.filter_complete_gr, drop_na=args.drop_na)
        item = {"A":A,"B":B,"Alpha":AL,"N":res["N"],"med_seg":res["med_seg"],"med_sr":res["med_sr"],"med_grsr":res["med_grsr"]}
        if args.paired in ("sr","both"):
            st = paired_sign_test(res["pairs_vs_sr"])
            item.update({"pairs_sr":st["N_pairs"],"seg_better_sr":st["N_Seg_better"],"share_sr":st["share"],"p_two_sr":st["p_two"]})
        if args.paired in ("grsr","both"):
            st2 = paired_sign_test(res["pairs_vs_grsr"])
            item.update({"pairs_grsr":st2["N_pairs"],"seg_better_grsr":st2["N_Seg_better"],"share_grsr":st2["share"],"p_two_grsr":st2["p_two"]})
        results.append(item)

    # Write full results CSV
    import csv as _csv
    csv_path = io.reports / "deltaM_tuning_results.csv"
    if results:
        keys = sorted({k for r in results for k in r.keys()})
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w=_csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(results)
        echo(f"[OK] wrote CSV: {csv_path}")
    else:
        echo("[WARN] no results to write")

    # Best picks
    def safe(v): 
        try: return float(v)
        except: return float('inf')

    best_by_med = min(results, key=lambda r: safe(r.get("med_seg"))) if results else None

    # Best by p-values (if present)
    best_by_p_sr = None; best_by_p_grsr = None
    if results and any("p_two_sr" in r for r in results):
        cand = [r for r in results if finite(r.get("p_two_sr"))]
        if cand: best_by_p_sr = sorted(cand, key=lambda r: r["p_two_sr"])[0]
    if results and any("p_two_grsr" in r for r in results):
        cand = [r for r in results if finite(r.get("p_two_grsr"))]
        if cand: best_by_p_grsr = sorted(cand, key=lambda r: r["p_two_grsr"])[0]

    # For best_by_med, compute bootstrap CIs and write per-row debug
    best_summary: Dict[str,Any] = {}
    if best_by_med is not None:
        echo(f"[BEST by med_seg] A={best_by_med['A']:.6g} B={best_by_med['B']:.6g} Alpha={best_by_med['Alpha']:.6g} | med_seg={best_by_med['med_seg']:.6g}")
        res = eval_set(rows, prefer_z=args.prefer_z, mode=args.mode, A=best_by_med["A"], B=best_by_med["B"], Alpha=best_by_med["Alpha"],
                       lo=None, hi=None, filter_complete_gr=args.filter_complete_gr, drop_na=args.drop_na)
        seg_vals = [a for a,_ in res["pairs_vs_sr"] if finite(a)]
        sr_vals  = [b for _,b in res["pairs_vs_sr"] if finite(b)]
        grsr_vals= [b for _,b in res["pairs_vs_grsr"] if finite(b)]
        ci_seg = bootstrap_ci_median(seg_vals, n_boot=args.ci) if args.ci>0 else None
        ci_sr  = bootstrap_ci_median(sr_vals,  n_boot=args.ci) if args.ci>0 else None
        ci_grsr= bootstrap_ci_median(grsr_vals,n_boot=args.ci) if args.ci>0 else None

        # dump per-row debug for best
        dbg_path = io.reports / "deltaM_best_debug.csv"
        import csv as _csv
        with dbg_path.open("w", newline="", encoding="utf-8") as f:
            if res["dbg_rows"]:
                keys = list(res["dbg_rows"][0].keys())
                w=_csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(res["dbg_rows"])
        echo(f"[OK] wrote CSV: {dbg_path}")

        best_summary = {"best_by_med_seg":best_by_med, "ci95_median_seg":ci_seg, "ci95_median_sr":ci_sr, "ci95_median_grsr":ci_grsr}

    summary = {
        "best_by_med_seg": best_by_med,
        "best_by_p_two_vs_sr": best_by_p_sr,
        "best_by_p_two_vs_grsr": best_by_p_grsr,
        "grid_sizes": {"A":len(gridA), "B":len(gridB), "Alpha":len(gridAL)},
        "random_added": args.random
    }
    summary.update(best_summary)
    (io.reports / "deltaM_tuning_best.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    echo(f"[OK] wrote JSON: {io.reports / 'deltaM_tuning_best.json'}")

    # Heatmaps
    if args.heatmaps and results:
        save_heatmap_AB(results, io)
        # (Optional) Weitere Heatmaps könnten hier ergänzt werden.

    echo("[DONE]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
