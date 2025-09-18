# phi_bic_test.py
# Beispiele:
#   python phi_bic_test.py --in real_data_full.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz --tol 1e-3
#   python phi_bic_test.py --in data.csv --outdir out --z-col z
#   python phi_bic_test.py --in data.csv --outdir out --lambda-obs lambda_obs --lambda-rest lambda_rest
#   python phi_bic_test.py --in real_data_full_filled.csv --outdir out --f-emit f_emit_Hz --f-obs f_obs_Hz --tol 0 --jitter 1e-12 --n-rand 20000

import argparse, json, math, os, sys, random
from math import log, sqrt
import numpy as np
import pandas as pd

PHI = (1 + 5**0.5) / 2

# ---------- Utils ----------

def to_py(x):
    """JSON-safe Konvertierung für numpy/pandas-Objekte."""
    if isinstance(x, (np.generic,)):
        return x.item()
    if isinstance(x, (np.ndarray,)):
        return x.tolist()
    return x

def jdump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=to_py)

def autodetect(df, arg_ratio, arg_z, arg_fe, arg_fo, arg_lo, arg_lr):
    cols = {c.lower(): c for c in df.columns}

    def pick(cand):
        for k in cand:
            if k.lower() in cols:
                return cols[k.lower()]
        return None

    used = {}
    ratio = arg_ratio or pick(["ratio","f_emit/f_obs","freq_ratio","r"])
    zcol  = arg_z     or pick(["z","redshift"])
    f_e   = arg_fe    or pick(["f_emit","f_emit_hz","nu_emit","nu_emit_hz"])
    f_o   = arg_fo    or pick(["f_obs","f_obs_hz","nu_obs","nu_obs_hz"])
    l_o   = arg_lo    or pick(["lambda_obs","lam_obs","w_obs","lambda_observed"])
    l_r   = arg_lr    or pick(["lambda_rest","lam_rest","w_rest","lambda_0","lambda0"])

    used.update({
        "has_ratio": ratio is not None,
        "has_z": zcol is not None,
        "has_f_emit": f_e is not None,
        "has_f_obs": f_o is not None,
        "has_lambda_obs": l_o is not None,
        "has_lambda_rest": l_r is not None,
    })
    return ratio, zcol, f_e, f_o, l_o, l_r, used

def build_ratio(df, ratio, zcol, f_e, f_o, l_o, l_r):
    if ratio and ratio in df:
        return pd.to_numeric(df[ratio], errors="coerce")
    if zcol and zcol in df:
        z = pd.to_numeric(df[zcol], errors="coerce")
        return 1.0 + z
    if f_e in df and f_o in df:
        fe = pd.to_numeric(df[f_e], errors="coerce")
        fo = pd.to_numeric(df[f_o], errors="coerce")
        return fe / fo
    if l_o in df and l_r in df:
        lo = pd.to_numeric(df[l_o], errors="coerce")
        lr = pd.to_numeric(df[l_r], errors="coerce")
        return lo / lr
    raise ValueError("Keine passenden Spalten gefunden. Gib sie per --lambda-obs/--lambda-rest "
                     "oder --f-emit/--f-obs oder --ratio-col oder --z-col an.")

def safe_binom_two_sided(k, n):
    """Overflow-freier z-Approx p-Wert (zweiseitig) für Sign-Test (p=0.5)."""
    if n <= 0:
        return float('nan')
    p = 0.5
    mean = n * p
    var = n * p * (1 - p)
    if var <= 0:
        return float('nan')
    z = (abs(k - mean) - 0.5) / sqrt(var)
    # rational approx für Phi(|z|)-Tail (Moro/West) – wie zuvor
    t = 1.0 / (1.0 + 0.2316419 * abs(z))
    d = 0.39894228 * math.exp(-z*z/2.0)
    tail = d * t * (0.31938153 + t*(-0.356563782 + t*(1.781477937 + t*(-1.821255978 + t*1.330274429))))
    p_two = 2.0 * tail
    return min(1.0, max(0.0, p_two))

# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tol", type=float, default=1e-3, help="Toleranz für Ties (0 <= tol < 0.5)")
    ap.add_argument("--phi", type=float, default=PHI)

    ap.add_argument("--ratio-col", default=None)
    ap.add_argument("--z-col", default=None)
    ap.add_argument("--f-emit", default=None)
    ap.add_argument("--f-obs", default=None)
    ap.add_argument("--lambda-obs", default=None)
    ap.add_argument("--lambda-rest", default=None)

    # Neu: Randomized Sign-Test
    ap.add_argument("--jitter", type=float, default=0.0, help="Uniformes Jitter |ε|<=jitter auf Residuen (Schritte).")
    ap.add_argument("--n-rand", type=int, default=0, help="Anzahl Monte-Carlo-Samples für randomisierten Sign-Test.")

    a = ap.parse_args()

    if not (0 <= a.tol < 0.5):
        print("[FATAL] tol muss in [0, 0.5) liegen.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(a.outdir, exist_ok=True)

    df = pd.read_csv(a.inp)
    ratio, zc, fe, fo, lo, lr, avail = autodetect(df, a.ratio_col, a.z_col, a.f_emit, a.f_obs, a.lambda_obs, a.lambda_rest)
    r = build_ratio(df, ratio, zc, fe, fo, lo, lr)

    # Säuberung
    r = pd.to_numeric(r, errors="coerce")
    r = r[np.isfinite(r)]
    r = r[r > 0]

    if len(r) == 0:
        print("[FATAL] Keine gültigen Ratio-Werte nach Säuberung.", file=sys.stderr)
        print("[HINT]", avail, file=sys.stderr)
        sys.exit(1)

    # Residuen in φ-Schritten
    logphi = float(np.log(a.phi))
    if not np.isfinite(logphi) or logphi == 0.0:
        print("[FATAL] Ungültiges φ.", file=sys.stderr); sys.exit(1)

    nstar = np.log(r) / logphi
    nearest = np.rint(nstar)
    resid = nstar - nearest
    abs_resid = np.abs(resid)

    # Kerndaten
    N = int(len(resid))
    med_abs = float(np.median(abs_resid))
    mad = float(np.median(np.abs(abs_resid - med_abs)) * 1.4826)
    ties = int(np.sum(abs_resid <= a.tol))
    mask = abs_resid > a.tol
    n_eff = int(np.sum(mask))
    k_pos = int(np.sum(resid[mask] > 0))

    # BIC: φ-Gitter (Normal um 0) vs. Uniform(-0.5,0.5)
    sigma2 = float(np.mean((resid if N>0 else np.array([0.0]))**2))
    sigma = max(1e-18, math.sqrt(sigma2))
    # logLik Normal
    loglik_lattice = float(np.sum(-0.5*np.log(2*np.pi*sigma*sigma) - (resid*resid)/(2*sigma*sigma))) if N>0 else 0.0
    bic_lattice = 1*np.log(max(1, N)) - 2.0*loglik_lattice  # k=1 (σ)
    bic_uniform = 0.0                                        # logLik=0, k=0
    delta_bic = bic_uniform - bic_lattice

    # Sign-Test (klassisch)
    p_two = safe_binom_two_sided(k_pos, n_eff)

    # Randomized Sign-Test (optional)
    jitter = float(a.jitter)
    n_rand = int(a.n_rand)
    p_two_rand_med = float('nan')
    p_two_rand_lo = float('nan')
    p_two_rand_hi = float('nan')
    rand_used = 0

    if n_rand > 0 and jitter > 0 and N > 0:
        rng = random.Random(12345)
        pvals = []
        base = resid.copy()
        for _ in range(n_rand):
            # Uniformes Jitter in Schritten: U(-jitter, +jitter)
            jit = np.array([rng.uniform(-jitter, jitter) for _ in range(N)], dtype=float)
            rj = base + jit
            mask_j = np.abs(rj) > a.tol
            n_eff_j = int(np.sum(mask_j))
            if n_eff_j == 0:
                continue
            k_pos_j = int(np.sum(rj[mask_j] > 0))
            pvals.append(safe_binom_two_sided(k_pos_j, n_eff_j))
        if len(pvals) > 0:
            rand_used = len(pvals)
            p_two_rand_med = float(np.median(pvals))
            q = np.quantile(pvals, [0.025, 0.975])
            p_two_rand_lo, p_two_rand_hi = float(q[0]), float(q[1])

    # Output per-row
    perrow = pd.DataFrame({
        "ratio": r.values,
        "n_star": nstar.values,
        "residual": resid.values,
        "abs_residual": abs_resid.values,
        "nearest_n": nearest.astype(int)
    })
    perrow_csv = os.path.join(a.outdir, "phi_bic_perrow.csv")
    perrow.to_csv(perrow_csv, index=False)
    # Alias wie von dir erwartet:
    alias_csv = os.path.join(a.outdir, "phi_bic_residuals.csv")
    perrow.to_csv(alias_csv, index=False)

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
        "randomized_sign_test": {
            "enabled": (n_rand > 0 and jitter > 0),
            "jitter": jitter,
            "n_rand": n_rand,
            "samples_used": rand_used,
            "p_two_median": p_two_rand_med,
            "p_two_95ci": [p_two_rand_lo, p_two_rand_hi]
        },
        "files": {
            "perrow_csv": perrow_csv,
            "residuals_csv_alias": alias_csv
        }
    }
    jdump(summary, os.path.join(a.outdir, "phi_bic_summary.json"))

    print(f"[OK] rows used: {N}")
    print(f"[OK] abs_residual_median: {med_abs}")
    print(f"[OK] ΔBIC (uniform - lattice): {delta_bic}  -> {'φ-Gitter besser' if delta_bic>0 else 'Uniform besser/gleich'}")
    print(f"[OK] sign-test p(two-sided): {p_two}")
    if n_rand > 0 and jitter > 0:
        print(f"[OK] randomized sign-test: median p={p_two_rand_med} 95%CI=({p_two_rand_lo}, {p_two_rand_hi}) "
              f"[samples_used={rand_used}/{n_rand}]")
    print(f"[OK] outdir: {a.outdir}")

if __name__ == "__main__":
    main()
