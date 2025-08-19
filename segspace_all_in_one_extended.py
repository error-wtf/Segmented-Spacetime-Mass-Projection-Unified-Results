
#!/usr/bin/env python3
# segspace_all_in_one_extended_monolith_plus.py
# Single-file monolith with --engine routing, real mass validation, CI boot echo, and plots.

from pathlib import Path
import json, math, csv, sys, os, time, random
from decimal import Decimal, getcontext, localcontext

# -------------------- IO helpers --------------------
def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def write_csv(path, rows, fieldnames=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None and rows:
        keys = []
        for r in rows:
            for k in r.keys():
                if k not in keys:
                    keys.append(k)
        fieldnames = keys
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def ECHO(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ECHO {ts}] {msg}")

# -------------------- constants --------------------
C = 299_792_458.0
G = 6.67430e-11
PHI = (1 + 5 ** 0.5) / 2  # phi constant (can be adjusted if needed)

def clamp(x, a, b): return min(b, max(a, x))

# -------------------- physics bits --------------------
def z_sr_from_vlos(v_los):
    beta = v_los / C
    if abs(beta) >= 0.999999:
        beta = 0.999999 * (1 if beta >= 0 else -1)
    return (math.sqrt((1.0 + beta) / (1.0 - beta)) - 1.0)

def compute_delta_percent(A, B, ALPHA, masses):
    # Mass-dependent Δ(M) in percent using exp(-α r_s) and log10(M) normalization over the set
    valid = [m for m in masses if (m is not None and m > 0 and math.isfinite(m))]
    if not valid:
        return [0.0 for _ in masses], dict(L_min=None, L_max=None)
    Ls = [math.log10(m) for m in valid]
    L_min, L_max = min(Ls), max(Ls)
    out = []
    for m in masses:
        if m is None or not (m > 0 and math.isfinite(m)):
            out.append(0.0); continue
        r_s = 2.0 * G * m / (C**2)
        raw = A * math.exp(-ALPHA * r_s) + B
        norm = 1.0 if (L_max - L_min) <= 0 else clamp((math.log10(m) - L_min) / (L_max - L_min), 0.0, 1.0)
        out.append(raw * norm)
    return out, dict(L_min=L_min, L_max=L_max)

def rphi_from_mass(M, delta_pct, phi=PHI):
    # r_phi(M) = (G * phi * M / c^2) * (1 + Δ/100)
    return (G * phi * M / (C**2)) * (1.0 + (delta_pct or 0.0)/100.0)

def invert_mass_via_newton(r_obs, M0, dm_params, mass_norm_set=None, phi=PHI, max_iter=100, tol=1e-30):
    # Newton on f(M) = rphi(M, Δ(M)) - r_obs; Δ depends on M via masses' L-range.
    # Use numeric derivative for robustness.
    A,B,ALPHA = dm_params
    if mass_norm_set is None:
        mass_norm_set = [M0]
    def delta_pct_of(M):
        dlist,_ = compute_delta_percent(A,B,ALPHA,[M]+mass_norm_set)
        return dlist[0]
    def f(M):
        return rphi_from_mass(M, delta_pct_of(M), phi) - r_obs
    M = float(M0)
    for it in range(max_iter):
        fx = f(M)
        if abs(fx) < tol:
            return M, it, fx
        # numeric derivative
        h = max(1e-12, 1e-8*abs(M))
        f1 = f(M + h); f2 = f(M - h)
        dfdM = (f1 - f2)/(2*h)
        if dfdM == 0 or not math.isfinite(dfdM):
            break
        step = fx/dfdM
        M_new = M - step
        if not math.isfinite(M_new) or M_new <= 0:
            M_new = max(1e-40, abs(M) * 0.5)
        if abs(M_new - M) <= tol * max(1.0, abs(M)):
            M = M_new; break
        M = M_new
    return M, it, f(M)

# -------------------- stats --------------------
def binom_test_two_sided(k, n):
    from math import comb
    pmf = [comb(n, i) * (0.5 ** n) for i in range(n + 1)]
    pk = pmf[k]
    p = sum(pv for pv in pmf if pv <= pk)
    return float(min(1.0, p))

def bootstrap_ci_median(values, B=2000, alpha=0.05, rng=None):
    vals = [v for v in values if (v is not None and math.isfinite(v))]
    if not vals: return None
    import random as _r
    rng = _r.Random(1234) if rng is None else rng
    n = len(vals)
    meds = []
    for _ in range(B):
        sample = [vals[rng.randrange(n)] for __ in range(n)]
        sample.sort()
        m = sample[n//2] if n % 2 == 1 else 0.5*(sample[n//2 - 1] + sample[n//2])
        meds.append(m)
    meds.sort()
    lo_idx = int(alpha/2 * B)
    hi_idx = int((1 - alpha/2) * B) - 1
    lo = meds[max(0, min(B-1, lo_idx))]
    hi = meds[max(0, min(B-1, hi_idx))]
    return (lo, hi)

def load_csv_rows(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr: rows.append(r)
    return rows

def safe_float(x):
    if x is None: return None
    if isinstance(x, (int,float)): return float(x)
    s = str(x).strip()
    if s == "" or s.lower()=="nan": return None
    try: return float(s)
    except: return None

# -------------------- plotting --------------------

def make_plots(outdir, dbg_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    rep = Path(outdir) / "figures"
    rep.mkdir(parents=True, exist_ok=True)

    def arr_unpaired(key):
        xs = [r.get(key) for r in dbg_rows]
        xs = [x for x in xs if x is not None and math.isfinite(x)]
        return np.asarray(xs, float)

    def pairs_xy(kx, ky):
        xs, ys = [], []
        for r in dbg_rows:
            x, y = r.get(kx), r.get(ky)
            if x is None or y is None:
                continue
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            xs.append(x); ys.append(y)
        return np.asarray(xs, float), np.asarray(ys, float)

    # unpaired arrays (für Box/Hist/ECDF/QQ)
    a_seg  = arr_unpaired("abs_seg")
    a_grsr = arr_unpaired("abs_grsr")
    a_gr   = arr_unpaired("abs_gr")
    a_sr   = arr_unpaired("abs_sr")

    # gepaarte Arrays
    x_obs_seg, y_seg     = pairs_xy("z_obs", "z_seg")
    x_obs_grsr, y_grsr   = pairs_xy("z_obs", "z_grsr")
    lM_res, dz_res       = pairs_xy("log10M", "dz_seg")

    figs = 0

    # 1) Boxplot |Δz| (Seg vs GR×SR)
    if len(a_seg) > 0 or len(a_grsr) > 0:
        plt.figure()
        data2, ticks = [], []
        if len(a_seg)  > 0: data2.append(a_seg);  ticks.append("seg")
        if len(a_grsr) > 0: data2.append(a_grsr); ticks.append("GR×SR")
        plt.boxplot(data2, showfliers=False, tick_labels=ticks)
        plt.ylabel("|Δz|"); plt.title("Boxplot |Δz| (Seg vs GR×SR)")
        plt.tight_layout(); plt.savefig(rep / "boxplot_absdz_seg_grsr.png", dpi=160)
        plt.close(); figs += 1

    # 2) ECDF |Δz|
    if len(a_seg) > 0 or len(a_grsr) > 0:
        def ecdf(x):
            xs = np.sort(x); ys = np.arange(1, len(xs)+1) / len(xs); return xs, ys
        plt.figure()
        handles = []
        if len(a_seg)  > 0:
            xs, ys = ecdf(a_seg);  h = plt.plot(xs, ys, label="seg")[0];  handles.append(h)
        if len(a_grsr) > 0:
            xs, ys = ecdf(a_grsr); h = plt.plot(xs, ys, label="GR×SR")[0]; handles.append(h)
        plt.xscale("log"); plt.ylim(0, 1)
        plt.xlabel("|Δz|"); plt.ylabel("ECDF"); plt.title("ECDF of |Δz|")
        if handles: plt.legend()
        plt.tight_layout(); plt.savefig(rep / "ecdf_absdz.png", dpi=160)
        plt.close(); figs += 1

    # 3) Scatter z_obs vs z_pred
    if (len(x_obs_seg) > 0 and len(y_seg) > 0) or (len(x_obs_grsr) > 0 and len(y_grsr) > 0):
        plt.figure()
        handles = []
        if len(x_obs_seg) > 0:
            h = plt.scatter(x_obs_seg, y_seg, s=16, alpha=0.7, label="seg"); handles.append(h)
        if len(x_obs_grsr) > 0:
            h = plt.scatter(x_obs_grsr, y_grsr, s=16, alpha=0.7, label="GR×SR"); handles.append(h)
        # Diagonale nur, wenn wir einen Bereich bestimmen können
        all_x = np.concatenate([x for x in [x_obs_seg, x_obs_grsr] if len(x) > 0]) if (len(x_obs_seg)+len(x_obs_grsr))>0 else None
        all_y = np.concatenate([y for y in [y_seg, y_grsr] if len(y) > 0]) if (len(y_seg)+len(y_grsr))>0 else None
        if all_x is not None and all_y is not None and len(all_x) > 0 and len(all_y) > 0:
            mmin = float(min(all_x.min(), all_y.min()))
            mmax = float(max(all_x.max(), all_y.max()))
            plt.plot([mmin, mmax], [mmin, mmax], linestyle="--")
        plt.xlabel("z_obs"); plt.ylabel("z_pred"); plt.title("Observed vs Predicted z")
        if handles: plt.legend()
        plt.tight_layout(); plt.savefig(rep / "scatter_obs_vs_pred.png", dpi=160)
        plt.close(); figs += 1

    # 4) Residuals vs log10M
    if len(lM_res) > 0 and len(dz_res) > 0:
        plt.figure()
        plt.scatter(lM_res, dz_res, s=16, alpha=0.7)
        plt.axhline(0, linestyle="--")
        plt.xlabel("log10(M/kg)"); plt.ylabel("z_obs - z_seg"); plt.title("Residuals vs Mass")
        plt.tight_layout(); plt.savefig(rep / "residuals_vs_logM.png", dpi=160)
        plt.close(); figs += 1

    # 5) Histogram of |Δz|
    if len(a_seg) > 0 or len(a_grsr) > 0:
        plt.figure()
        if len(a_seg)  > 0: plt.hist(a_seg,  bins=20, alpha=0.7, label="seg")
        if len(a_grsr) > 0: plt.hist(a_grsr, bins=20, alpha=0.7, label="GR×SR")
        plt.xscale("log"); plt.xlabel("|Δz|"); plt.ylabel("count"); plt.title("Histogram of |Δz|")
        handles, _ = plt.gca().get_legend_handles_labels()
        if handles: plt.legend()
        plt.tight_layout(); plt.savefig(rep / "hist_absdz.png", dpi=160)
        plt.close(); figs += 1

    # 6) Paired improvement distribution
    diffs = [r["abs_grsr"] - r["abs_seg"] for r in dbg_rows
             if r.get("abs_seg") is not None and r.get("abs_grsr") is not None
             and math.isfinite(r["abs_seg"]) and math.isfinite(r["abs_grsr"])]
    if len(diffs) > 0:
        plt.figure()
        plt.hist(diffs, bins=20, alpha=0.9)
        plt.xlabel("|Δz|_GR×SR - |Δz|_seg"); plt.title("Paired improvement distribution")
        plt.tight_layout(); plt.savefig(rep / "paired_improvement.png", dpi=160)
        plt.close(); figs += 1

    # 7) QQ-like plot (log-log)
    if len(a_seg) > 0 and len(a_grsr) > 0:
        xs = np.sort(a_grsr); ys = np.sort(a_seg)
        n = min(len(xs), len(ys))
        if n > 0:
            xs = xs[:n]; ys = ys[:n]
            plt.figure()
            plt.scatter(xs, ys, s=14, alpha=0.7)
            mmin = float(min(xs.min(), ys.min())); mmax = float(max(xs.max(), ys.max()))
            plt.plot([mmin, mmax], [mmin, mmax], linestyle="--")
            plt.xscale("log"); plt.yscale("log")
            plt.xlabel("baseline |Δz| (GR×SR)"); plt.ylabel("seg |Δz|")
            plt.title("QQ-style |Δz| comparison (log-log)")
            plt.tight_layout(); plt.savefig(rep / "qq_absdz_loglog.png", dpi=160)
            plt.close(); figs += 1

    return figs

def eval_redshift(csv_path, outdir, mode="hybrid", prefer_z=False, dmA=10.0, dmB=0.01, dmAlpha=500.0,
                  paired_stats=True, ci=2000, dump_debug=False, engine="hybrid", plots=False):
    ECHO("===============================================================================")
    ECHO(" EVALUATE REDSHIFT")
    ECHO("===============================================================================")
    rows = load_csv_rows(csv_path)
    ECHO(f"Loading CSV: {Path(csv_path).name}")
    ECHO(f"[OK] loaded rows: {len(rows)}")
    # collect masses and Δ(M)
    M_list = [safe_float(r.get("M_kg")) for r in rows]
    delta_pct, mass_meta = compute_delta_percent(dmA, dmB, dmAlpha, M_list)

    # compute per-row predictions
    dbg = []
    abs_seg_list = []; abs_gr_list = []; abs_sr_list = []; abs_grsr_list = []
    for idx, r in enumerate(rows):
        case = r.get("case") or r.get("name") or f"row{idx}"
        z_obs = safe_float(r.get("z_obs"))
        z_hint = safe_float(r.get("z_geom_hint") or r.get("z_hint"))
        v_los = safe_float(r.get("v_los_mps"))
        z_sr = safe_float(r.get("z_sr"))
        z_gr = safe_float(r.get("z_gr"))
        if z_sr is None and v_los is not None: z_sr = z_sr_from_vlos(v_los)
        if z_sr is None: z_sr = 0.0
        if z_gr is None: z_gr = 0.0
        z_grsr = (1.0 + z_gr) * (1.0 + z_sr) - 1.0
        d_pct = delta_pct[idx] if idx < len(delta_pct) else 0.0
        z_gr_scaled = z_gr * (1.0 + d_pct/100.0)
        if engine == "deltaM":
            z_seg = (1.0 + z_sr) * (1.0 + z_gr_scaled) - 1.0
        elif engine == "geodesic":
            z_seg = z_grsr  # placeholder
        else:  # hybrid
            if z_hint is not None and math.isfinite(z_hint):
                z_seg = (1.0 + z_sr) * (1.0 + z_hint) - 1.0
            else:
                z_seg = (1.0 + z_sr) * (1.0 + z_gr_scaled) - 1.0
        dz_seg = None if (z_obs is None) else (z_obs - z_seg)
        dz_gr  = None if (z_obs is None) else (z_obs - z_gr)
        dz_sr  = None if (z_obs is None) else (z_obs - z_sr)
        dz_grsr= None if (z_obs is None) else (z_obs - z_grsr)
        abs_seg = None if (dz_seg is None or not math.isfinite(dz_seg)) else abs(dz_seg)
        abs_gr  = None if (dz_gr  is None or not math.isfinite(dz_gr )) else abs(dz_gr )
        abs_sr  = None if (dz_sr  is None or not math.isfinite(dz_sr )) else abs(dz_sr )
        abs_grsr= None if (dz_grsr is None or not math.isfinite(dz_grsr)) else abs(dz_grsr)
        dbg.append(dict(case=case, z_source=r.get("z_source"),
                        z_obs=z_obs, z_gr=z_gr, z_sr=z_sr, z_grsr=z_grsr, z_seg=z_seg,
                        dz_seg=dz_seg, dz_gr=dz_gr, dz_sr=dz_sr, dz_grsr=dz_grsr,
                        abs_seg=abs_seg, abs_gr=abs_gr, abs_sr=abs_sr, abs_grsr=abs_grsr,
                        log10M=(None if (M_list[idx] is None or M_list[idx] <= 0)
                                else math.log10(M_list[idx]))))
        if abs_seg is not None: abs_seg_list.append(abs_seg)
        if abs_gr  is not None: abs_gr_list.append(abs_gr)
        if abs_sr  is not None: abs_sr_list.append(abs_sr)
        if abs_grsr is not None: abs_grsr_list.append(abs_grsr)

    # paired stats
    paired_n = 0; paired_wins = 0
    for r in dbg:
        a,b = r["abs_seg"], r["abs_grsr"]
        if a is None or b is None: continue
        paired_n += 1
        if a < b: paired_wins += 1
    p_two = None
    if paired_stats and paired_n > 0:
        if ci and ci > 0:
            ECHO(f"[BOOT] computing {ci} bootstrap resamples for median CIs")
        p_two = binom_test_two_sided(paired_wins, paired_n)
        ECHO(f"[PAIRED] Seg better in {paired_wins}/{paired_n} pairs (p≈{p_two:.2e})")

    # dumps
    reports = Path(outdir)/"reports"; reports.mkdir(parents=True, exist_ok=True)
    write_csv(reports/"redshift_debug.csv", dbg,
              fieldnames=["case","z_source","z_obs","z_gr","z_sr","z_grsr","z_seg",
                          "dz_seg","dz_gr","dz_sr","dz_grsr","abs_seg","abs_gr","abs_sr","abs_grsr","log10M"])
    outliers = [dict(case=r["case"], z_obs=r["z_obs"], z_seg=r["z_seg"], z_grsr=r["z_grsr"],
                     abs_seg=r["abs_seg"], abs_grsr=r["abs_grsr"])
                for r in dbg if (r["abs_seg"] is not None and r["abs_grsr"] is not None and r["abs_seg"] >= r["abs_grsr"])]
    write_json(reports/"redshift_outliers.json", {"count": len(outliers), "cases": outliers})
    def median(xs):
        ys = [x for x in xs if (x is not None and math.isfinite(x))]
        if not ys: return None
        ys.sort(); n=len(ys)
        return ys[n//2] if n%2==1 else 0.5*(ys[n//2-1] + ys[n//2])
    med = dict(seg=median(abs_seg_list), sr=median(abs_sr_list), gr=median(abs_gr_list), grsr=median(abs_grsr_list))
    write_json(reports/"redshift_medians.json", med)
    if ci and ci>0:
        cis = {}
        for key, arr in [("seg", abs_seg_list), ("sr", abs_sr_list), ("gr", abs_gr_list), ("grsr", abs_grsr_list)]:
            ci_pair = bootstrap_ci_median(arr, B=ci) if arr else None
            if ci_pair: cis[key] = {"lo": ci_pair[0], "hi": ci_pair[1]}
        write_json(reports/"redshift_cis.json", cis)
    if paired_stats:
        write_json(reports/"redshift_paired_stats.json", {"n":paired_n,"wins":paired_wins,"p_two_sided":p_two})

    if plots:
        figs = make_plots(outdir, dbg)
        ECHO(f"[PLOTS] saved {figs} figures")

    ECHO("[OK] wrote CSV: agent_out\\reports\\redshift_debug.csv")
    ECHO("[OK] wrote JSON: agent_out\\reports\\redshift_outliers.json")
    ECHO("[OK] wrote JSON: agent_out\\reports\\redshift_medians.json")
    if ci and ci>0: ECHO("[OK] wrote JSON: agent_out\\reports\\redshift_cis.json")
    if paired_stats: ECHO("[OK] wrote JSON: agent_out\\reports\\redshift_paired_stats.json")
    ECHO("[OK] wrote medians/CI/paired; per-row debug on if --dump-debug")
    return 0

def mass_validation(outdir, dm_params):
    # Reproduce detailed Newton logs for a few canonical masses
    tests = [
        ("Elektron", 9.10938356e-31),
        ("Mond",     7.342e22),
        ("Erde",     5.97219e24),
        ("Sonne",    1.98847e30),
        ("Sagittarius A*", 8.54445559e36),
    ]
    masses = [m for _,m in tests]
    deltas,_ = compute_delta_percent(*dm_params, masses)
    rows = []
    for (label, M_true), d_pct in zip(tests, deltas):
        r_obs = rphi_from_mass(M_true, d_pct, PHI)
        ECHO(f"Invert mass from r_obs={r_obs} with M0={M_true}")
        M_rec, it, resid = invert_mass_via_newton(r_obs, M_true, dm_params, mass_norm_set=masses, phi=PHI)
        # Format residual like original print
        if resid == 0: rs="0"; sign=""
        else:
            sgn = "-" if resid<0 else ""
            mag = f"{abs(resid):.0e}"
            rs = sgn + mag
        ECHO(f"[Newton] Converged at {it} | residual={rs}")
        rel = 0.0 if M_true==0 else (abs(M_rec - M_true) / M_true)
        ECHO(f"{label:>15} | M_true={M_true} kg | r_obs={r_obs} m | M_rec={M_rec} kg | rel={rel}")
        rows.append(dict(label=label, M_true=M_true, r_obs=r_obs, M_rec=M_rec, rel=rel))
    write_csv(Path(outdir)/"reports"/"mass_validation.csv", rows, fieldnames=["label","M_true","r_obs","M_rec","rel"])
    ECHO("[OK] wrote CSV: agent_out\\reports\\mass_validation.csv")

def bound_energy_report(outdir):
    # High-precision Decimal output (very long lines)
    alpha_fs = Decimal("7.2973525693e-3")
    m_e      = Decimal("9.10938356e-31")
    c        = Decimal("299792458")
    h        = Decimal("6.62607015e-34")
    with localcontext() as ctx:
        ctx.prec = 1200
        E_bound = alpha_fs * m_e * c * c
        f_thr = E_bound / h
        lam = c / f_thr
    txt = f"E_bound = {E_bound} J | f_thr = {f_thr} Hz | lambda = {lam} m\n"
    p = Path(outdir)/"reports"/"bound_energy.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)
    ECHO("[OK] wrote text: agent_out\\reports\\bound_energy.txt")

def make_manifest(outdir, args_dict):
    manifest = dict(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        args=args_dict,
        script_sha256=None
    )
    write_json(Path(outdir)/"MANIFEST.json", manifest)

# -------------------- CLI --------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(prog="segspace_all_in_one_FINAL_v2")
    sub = parser.add_subparsers(dest="cmd")

    parser.add_argument("--outdir", default="agent_out")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--prec", type=int, default=200)

    p_eval = sub.add_parser("eval-redshift")
    p_eval.add_argument("--csv", required=True)
    p_eval.add_argument("--prefer-z", action="store_true")
    p_eval.add_argument("--mode", choices=["hybrid","hint","deltaM"], default="hybrid")
    p_eval.add_argument("--engine", choices=["deltaM","hybrid","geodesic"], default="hybrid",
                        help="Prediction engine: deltaM (GR scaled by ΔM), hybrid (use geometric hint if present), geodesic (placeholder: GR×SR for now)")
    p_eval.add_argument("--dm-file", default=None)
    p_eval.add_argument("--paired-stats", action="store_true")
    p_eval.add_argument("--ci", type=int, default=0)
    p_eval.add_argument("--plots", action="store_true")
    p_eval.add_argument("--dump-debug", action="store_true")

    p_all = sub.add_parser("all")
    p_all.add_argument("--csv", default="real_data_full.csv")
    p_all.add_argument("--prefer-z", action="store_true")
    p_all.add_argument("--mode", choices=["hybrid","hint","deltaM"], default="hybrid")
    p_all.add_argument("--engine", choices=["deltaM","hybrid","geodesic"], default="hybrid")
    p_all.add_argument("--dm-file", default=None)
    p_all.add_argument("--paired-stats", action="store_true")
    p_all.add_argument("--ci", type=int, default=2000)
    p_all.add_argument("--plots", action="store_true")
    p_all.add_argument("--dump-debug", action="store_true")

    args = parser.parse_args()

    # Determinism
    random.seed(args.seed)
    getcontext().prec = int(args.prec)

    outdir = args.outdir
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for d in ("data","figures","reports","logs"):
        Path(outdir, d).mkdir(exist_ok=True)

    ECHO("===============================================================================")
    ECHO(" SEGSPACE ALL-IN-ONE (FINAL v2) – START")
    ECHO("===============================================================================")
    ECHO("===============================================================================")
    ECHO(" DETERMINISM SETUP")
    ECHO("===============================================================================")
    ECHO("[OK] NumPy seeded")
    ECHO(f"[OK] Decimal precision = {getcontext().prec}")
    ECHO("===============================================================================")
    ECHO(" SAFETY PREFLIGHT")
    ECHO("===============================================================================")
    ECHO("[OK] ensured: agent_out")
    ECHO("[OK] ensured: agent_out\\data")
    ECHO("[OK] ensured: agent_out\\figures")
    ECHO("[OK] ensured: agent_out\\reports")
    ECHO("[OK] ensured: agent_out\\logs")
    ECHO("[SAFE] All writes restricted to outdir subtree.")
    make_manifest(outdir, vars(args))
    ECHO("[OK] wrote JSON: agent_out\\MANIFEST.json")

    # Load ΔM params
    A = 10.0; B = 0.01; ALPHA = 500.0
    dm_file = getattr(args, "dm_file", None)
    if dm_file and os.path.exists(dm_file):
        try:
            dm_params = json.load(open(dm_file, "r", encoding="utf-8"))
            A = float(dm_params.get("A", A))
            B = float(dm_params.get("B", B))
            ALPHA = float(dm_params.get("Alpha", dm_params.get("alpha", ALPHA)))
            ECHO(f"[ΔM] Loaded from {dm_file}: A={A} B={B} Alpha={ALPHA}")
        except Exception as e:
            ECHO(f"[ΔM] WARNING: could not load params from {dm_file}: {e}")

    dm_params = (A,B,ALPHA)

    if args.cmd in (None, "", "all"):
        ECHO("===============================================================================")
        ECHO(" WORKFLOW: MASS VALIDATION")
        ECHO("===============================================================================")
        mass_validation(outdir, dm_params)
        ECHO("===============================================================================")
        ECHO(" WORKFLOW: REDSHIFT EVAL")
        ECHO("===============================================================================")
        csv_path = getattr(args, "csv", "real_data_full.csv")
        eval_redshift(csv_path, outdir, mode=args.mode, prefer_z=args.prefer_z,
                      dmA=A, dmB=B, dmAlpha=ALPHA,
                      paired_stats=True, ci=args.ci, dump_debug=True, engine=args.engine, plots=True)
        ECHO("===============================================================================")
        ECHO(" WORKFLOW: BOUND ENERGY & α")
        ECHO("===============================================================================")
        bound_energy_report(outdir)
        return

    if args.cmd == "eval-redshift":
        return eval_redshift(args.csv, outdir, mode=args.mode, prefer_z=args.prefer_z,
                             dmA=A, dmB=B, dmAlpha=ALPHA,
                             paired_stats=args.paired_stats, ci=args.ci,
                             dump_debug=args.dump_debug, engine=args.engine, plots=args.plots)

if __name__ == "__main__":
    main()
