# phi_bic_test.py
# Usage-Beispiele:
#   python phi_bic_test.py --in real_data_full.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz --tol 1e-3
#   python phi_bic_test.py --in data.csv --outdir out --z-col z
#   python phi_bic_test.py --in data.csv --outdir out --lambda-obs lambda_obs --lambda-rest lambda_rest

import argparse, json, math, os, sys
from math import log, sqrt
import pandas as pd
import numpy as np

PHI = (1+5**0.5)/2

def autodetect(df, arg_ratio, arg_z, arg_fe, arg_fo, arg_lo, arg_lr):
    cols = {c.lower(): c for c in df.columns}
    used = {}

    def pick(cand):
        for k in cand:
            if k.lower() in cols: return cols[k.lower()]
        return None

    ratio = arg_ratio or pick(["ratio","f_emit/f_obs","freq_ratio","r"])
    zcol  = arg_z     or pick(["z","redshift"])
    f_e   = arg_fe    or pick(["f_emit","f_emit_hz","nu_emit","nu_emit_hz"])
    f_o   = arg_fo    or pick(["f_obs","f_obs_hz","nu_obs","nu_obs_hz"])
    l_o   = arg_lo    or pick(["lambda_obs","lam_obs","w_obs","lambda_observed"])
    l_r   = arg_lr    or pick(["lambda_rest","lam_rest","w_rest","lambda_0","lambda0"])

    used["has_ratio"]= ratio is not None
    used["has_z"]=     zcol is not None
    used["has_f_emit"]=f_e  is not None
    used["has_f_obs"]= f_o  is not None
    used["has_lambda_obs"]= l_o is not None
    used["has_lambda_rest"]=l_r is not None

    return ratio, zcol, f_e, f_o, l_o, l_r, used

def build_ratio(df, ratio, zcol, f_e, f_o, l_o, l_r):
    if ratio and ratio in df: 
        x = pd.to_numeric(df[ratio], errors="coerce")
        return x
    if zcol and zcol in df:
        z = pd.to_numeric(df[zcol], errors="coerce")
        return 1.0 + z
    if f_e in df and f_o in df:
        fe = pd.to_numeric(df[f_e], errors="coerce")
        fo = pd.to_numeric(df[f_o], errors="coerce")
        return fe/fo
    if l_o in df and l_r in df:
        lo = pd.to_numeric(df[l_o], errors="coerce")
        lr = pd.to_numeric(df[l_r], errors="coerce")
        # 1+z = lambda_obs / lambda_rest
        return lo/lr
    raise ValueError("Keine passenden Spalten gefunden. Gib sie per --lambda-obs/--lambda-rest oder "
                     "--f-emit/--f-obs oder --ratio-col oder --z-col an.")

def safe_binom_two_sided(k, n):
    # Normalapprox. mit Kontinuitätskorrektur (robust und overflow-sicher)
    if n == 0: return float('nan')
    p = 0.5
    mean = n*p
    var = n*p*(1-p)
    z = (abs(k-mean)-0.5)/sqrt(var) if var>0 else 0.0
    # Phi(-|z|) * 2
    # numerische Approximation der Normal-CDF:
    t = 1.0/ (1.0 + 0.2316419*abs(z))
    d = 0.39894228*math.exp(-z*z/2.0)
    prob = d*t*(0.31938153 + t*(-0.356563782 + t*(1.781477937 + t*(-1.821255978 + t*1.330274429))))
    # für z>=0 ist Phi(z)=1 - prob; hier wollen 2*(1-Phi(|z|))
    p_two = 2.0*prob
    return min(1.0, max(0.0, p_two))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tol", type=float, default=1e-3)
    ap.add_argument("--phi", type=float, default=PHI)

    ap.add_argument("--ratio-col", default=None)
    ap.add_argument("--z-col", default=None)
    ap.add_argument("--f-emit", default=None)
    ap.add_argument("--f-obs", default=None)
    ap.add_argument("--lambda-obs", default=None)
    ap.add_argument("--lambda-rest", default=None)

    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)

    df = pd.read_csv(a.inp)
    ratio, zc, fe, fo, lo, lr, avail = autodetect(df, a.ratio_col, a.z_col, a.f_emit, a.f_obs, a.lambda_obs, a.lambda_rest)
    r = build_ratio(df, ratio, zc, fe, fo, lo, lr)

    r = pd.to_numeric(r, errors="coerce")
    r = r[np.isfinite(r)]
    r = r[r>0]

    if len(r)==0:
        print("[FATAL] Keine gültigen Ratio-Werte nach Säuberung.", file=sys.stderr)
        print("[HINT]", avail, file=sys.stderr)
        sys.exit(1)

    logphi = log(a.phi)

    nstar = np.log(r)/logphi
    resid = nstar - np.rint(nstar)          # in 'Schritten'
    abs_resid = np.abs(resid)

    # Metriken
    N = int(resid.size)
    med_abs = float(np.median(abs_resid))
    mad = float(np.median(np.abs(abs_resid - med_abs))*1.4826)
    ties = int(np.sum(abs_resid<=a.tol))
    used = int(np.sum(abs_resid>a.tol))

    # BIC: φ-Gitter (wrapped Normal ~ Normal bei kleinen Residuen) vs. Uniform(-0.5,0.5)
    # MLE für σ^2 = mean(resid^2)
    sigma2 = float(np.mean(resid**2))
    sigma = max(1e-12, math.sqrt(sigma2))
    # logLik Normal(0,σ): sum log pdf
    loglik_lattice = np.sum(-0.5*np.log(2*np.pi*sigma*sigma) - (resid*resid)/(2*sigma*sigma))
    bic_lattice = (1)*np.log(N) - 2.0*loglik_lattice   # k=1 (σ)
    # Uniform(-0.5,0.5): pdf=1 → logLik=0 → BIC=0 (k=0)
    bic_uniform = 0.0
    delta_bic = bic_uniform - bic_lattice  # >0 ⇒ φ-Gitter besser

    # Sign-Test (Vorzeichen der Residuen, Ties ausgeschlossen)
    mask = abs_resid>a.tol
    k_pos = int(np.sum(resid[mask]>0))
    n_eff = int(np.sum(mask))
    p_two = safe_binom_two_sided(k_pos, n_eff)

    # Outputs
    out_csv = os.path.join(a.outdir, "phi_bic_perrow.csv")
    pd.DataFrame({
        "ratio": r.values,
        "n_star": nstar.values,
        "residual": resid.values,
        "abs_residual": abs_resid.values,
        "nearest_n": np.rint(nstar).astype(int)
    }).to_csv(out_csv, index=False)

    summary = {
        "N_total": N,
        "tol": a.tol,
        "ties_<=tol": ties,
        "used_for_sign_test": n_eff,
        "abs_residual_median": med_abs,
        "abs_residual_MAD": mad,
        "sigma_hat_steps": sigma,
        "BIC_lattice": bic_lattice,
        "BIC_uniform": bic_uniform,
        "DeltaBIC_uniform_minus_lattice": delta_bic,
        "sign_test_k_pos": k_pos,
        "sign_test_p_two_sided": p_two,
        "phi": a.phi,
        "column_info": {
            "ratio_col": ratio, "z_col": zc, "f_emit": fe, "f_obs": fo,
            "lambda_obs": lo, "lambda_rest": lr
        },
        "files": {"perrow_csv": out_csv}
    }
    out_json = os.path.join(a.outdir, "phi_bic_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[OK] rows used: {N}")
    print(f"[OK] abs_residual_median: {med_abs}")
    print(f"[OK] ΔBIC (uniform - lattice): {delta_bic}  -> {'φ-Gitter besser' if delta_bic>0 else 'Uniform besser/gleich'}")
    print(f"[OK] sign-test p(two-sided): {p_two}")
    print(f"[OK] outdir: {a.outdir}")

if __name__=="__main__":
    main()
