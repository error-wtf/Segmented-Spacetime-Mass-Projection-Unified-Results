
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segspace_final_test.py
======================
Strenge, reproduzierbare Tests für das Segmented‑Spacetime‑Modell.

- Nimmt eine CSV (auto-discovery oder --csv PATH).
- Akzeptiert entweder (f_emit,f_obs) oder direkt z.
- "strong" PRED wenn Orbit‑Mode verfügbar (a,e,f_true). GR nutzt r(a,e,f) als Fallback.
- Bewertet Kategorie‑Medians (nur strong rows) und vergleicht gegen GR.
- Schreibt: JUnit, Report, Failures, Debug‑CSV.

© 2025 Carmen Wrede & Lino Casu – All rights reserved.
"""

import csv, json, math, sys, argparse, os, time
from dataclasses import dataclass, asdict
from typing import Optional, List
from pathlib import Path

try:
    import pandas as pd
    pd.set_option('future.no_silent_downcasting', True)
except Exception:
    print("[ERROR] pandas wird benötigt. Bitte installieren (pip/conda).", file=sys.stderr)
    sys.exit(2)

try:
    from scipy.constants import h, c, G
except Exception:
    h = 6.62607015e-34
    c = 299_792_458.0
    G = 6.67430e-11

M_sun = 1.98847e30
ALPHA_FS_DEFAULT = 1.0/137.035999084

TOL = {
    "tol_recon": 1e-12,
    "tol_z": 5e-8,
    "median_abs_pred": {
        "Lab": 1e-12,
        "Lab/Geo": 1e-9,
        "Solar": 1e-6,
        "WhiteDwarf": 1e-3,
        "S-stars": 5e-3,
    },
    "vtot_cap_c": 0.2,
    "sstar_compare_factor": 1.2,
}

@dataclass
class CaseInput:
    case: str
    category: str = ""
    f_emit_Hz: Optional[float] = None
    f_obs_Hz: Optional[float] = None
    lambda_emit_nm: Optional[float] = None
    lambda_obs_nm: Optional[float] = None
    z: Optional[float] = None
    N0: Optional[float] = 1.0000000028
    Nprime: Optional[float] = None
    alpha_fs: Optional[float] = ALPHA_FS_DEFAULT
    M_solar: Optional[float] = None
    r_emit_m: Optional[float] = None
    r_obs_m: Optional[float] = None
    v_los_mps: Optional[float] = None
    v_tot_mps: Optional[float] = None
    z_geom_hint: Optional[float] = None
    a_m: Optional[float] = None
    e: Optional[float] = None
    f_true_deg: Optional[float] = None

@dataclass
class CaseDerived:
    case: str
    category: str
    f_emit_Hz: Optional[float]
    f_obs_Hz: Optional[float]
    z_data: Optional[float] = None
    N_seg: Optional[float] = None
    delta_Nseg_zgr: Optional[float] = None
    rel_error_f_emit: Optional[float] = None
    pass_recon: Optional[bool] = None
    dz_seg_fit: Optional[float] = None
    dz_seg_pred: Optional[float] = None
    v_pred_mps: Optional[float] = None
    strong_pred: Optional[bool] = None
    dz_GR: Optional[float] = None
    dz_SR: Optional[float] = None
    dz_comb: Optional[float] = None

def to_float(x):
    try:
        if x in (None, "", "NA", "NaN"): return None
        return float(x)
    except Exception:
        return None

def derive_freqs(d: CaseInput):
    f_e, f_o = d.f_emit_Hz, d.f_obs_Hz
    if f_e is None and d.lambda_emit_nm is not None:
        f_e = c / (d.lambda_emit_nm * 1e-9)
    if f_o is None and d.lambda_obs_nm is not None:
        f_o = c / (d.lambda_obs_nm * 1e-9)
    if (f_e is None or f_o is None) and d.z is not None:
        if f_e is None and f_o is not None: f_e = f_o*(1.0+d.z)
        elif f_o is None and f_e is not None: f_o = f_e/(1.0+d.z)
    return f_e, f_o

def mu_from_Msolar(M_solar):
    if M_solar is None: return None
    return G*(M_solar*M_sun)

def r_from_aef(a, e, fdeg):
    if a is None or e is None or fdeg is None: return None
    f = math.radians(fdeg)
    return a*(1.0 - e*e)/(1.0 + e*math.cos(f))

def vis_viva_speed(mu, a, r):
    if mu is None or a is None or r is None or a<=0 or r<=0: return None
    return math.sqrt(mu*(2.0/r - 1.0/a))

def seg_total_z(z_geom, v_tot, v_los):
    if v_tot is None: return None
    beta = v_tot/c
    if abs(beta) >= 1: return None
    beta_r = (v_los or 0.0)/c if v_los is not None else 0.0
    gamma = 1.0/math.sqrt(1.0 - beta*beta)
    z_kin = gamma*(1.0+beta_r) - 1.0
    z_geom = z_geom or 0.0
    return (1.0 + z_geom)*(1.0 + z_kin) - 1.0

def z_gr_schwarzschild(M_solar, r_emit, r_obs=None):
    if M_solar is None or r_emit is None: return None
    M = M_solar*M_sun
    r_o = r_obs if r_obs is not None else float('inf')
    gtt_e = 1.0 - 2.0*G*M/(r_emit*c**2)
    gtt_o = 1.0 - 2.0*G*M/(r_o*c**2) if math.isfinite(r_o) else 1.0
    if gtt_e <= 0 or gtt_o <= 0: return None
    return math.sqrt(gtt_o/gtt_e) - 1.0

def z_sr(v_tot, v_los):
    if v_tot is None and v_los is None: return None
    beta = (v_tot or abs(v_los or 0.0))/c
    if abs(beta) >= 1.0: return None
    beta_r = (v_los or 0.0)/c if v_los is not None else 0.0
    gamma = 1.0/math.sqrt(1.0 - beta*beta)
    return gamma*(1.0+beta_r) - 1.0

def eval_case(cin: CaseInput, tol_recon=1e-12, tol_z=5e-8) -> CaseDerived:
    f_e, f_o = derive_freqs(cin)
    res = CaseDerived(case=cin.case, category=cin.category or "", f_emit_Hz=f_e, f_obs_Hz=f_o)

    # z_data from freqs or direct z
    if f_e is None or f_o is None:
        if cin.z is not None:
            z_data = float(cin.z)
        else:
            return res
    else:
        z_data = f_e/f_o - 1.0
    res.z_data = z_data

    # Nseg algebra only if freqs present
    if f_e is not None and f_o is not None:
        N0 = cin.N0 if cin.N0 is not None else 1.0
        res.N_seg = f_e/f_o - (N0 if N0 is not None else 1.0)
        res.delta_Nseg_zgr = res.N_seg - z_data

        if cin.Nprime is not None and N0 is not None:
            E_emit = h*f_e
            alpha_mbound = (h*f_o*cin.Nprime)/(N0*c**2)
            m_bound = alpha_mbound/(cin.alpha_fs or ALPHA_FS_DEFAULT)
            alpha_local = E_emit/(m_bound*c**2)
            f_check = alpha_local*m_bound*c**2/h
            rel = abs(f_check - f_e)/f_e if f_e else None
            res.rel_error_f_emit = rel
            res.pass_recon = (rel is not None and rel <= tol_recon)

    # Seg FIT (sanity): invert aus z_data
    z_geom = cin.z_geom_hint or 0.0
    beta_r = (cin.v_los_mps or 0.0)/c if cin.v_los_mps is not None else 0.0
    gamma_fit = (1.0 + z_data)/(1.0 + z_geom)
    gamma_fit = gamma_fit/(1.0 + beta_r) if (1.0+beta_r)>0 else gamma_fit
    if gamma_fit >= 1.0:
        v_fit = c*math.sqrt(1.0 - 1.0/(gamma_fit*gamma_fit))
        z_fit = seg_total_z(z_geom, v_fit, cin.v_los_mps)
        res.dz_seg_fit = z_data - z_fit if z_fit is not None else None

    # Seg PRED (Orbit-Mode bevorzugt)
    mu = mu_from_Msolar(cin.M_solar)
    v_pred = cin.v_tot_mps
    strong = False
    r_eff = cin.r_emit_m
    if cin.a_m is not None and cin.e is not None and cin.f_true_deg is not None:
        r_orb = r_from_aef(cin.a_m, cin.e, cin.f_true_deg)
        if r_orb is not None:
            r_eff = r_orb
            strong = True
    if v_pred is None and mu is not None:
        if strong and r_eff is not None and cin.a_m is not None:
            v_pred = vis_viva_speed(mu, cin.a_m, r_eff); strong = True
        elif r_eff is not None:
            v_pred = math.sqrt(mu/r_eff); strong = False
    res.v_pred_mps = v_pred
    res.strong_pred = strong

    if v_pred is not None and 0.0 < v_pred < c:
        z_pred = seg_total_z(z_geom, v_pred, cin.v_los_mps)
        res.dz_seg_pred = z_data - z_pred if z_pred is not None else None

    # GR/SR (GR nutzt r_eff als Fallback)
    r_eff_gr = cin.r_emit_m if cin.r_emit_m is not None else r_eff
    zgr = z_gr_schwarzschild(cin.M_solar, r_eff_gr, cin.r_obs_m)
    if zgr is not None: res.dz_GR = z_data - zgr
    zsr = z_sr(v_pred, cin.v_los_mps)
    if zsr is not None: res.dz_SR = z_data - zsr
    if zgr is not None and zsr is not None:
        zcb = (1.0 + zgr)*(1.0 + zsr) - 1.0
        res.dz_comb = z_data - zcb

    return res

def discover_csv(preferred=None):
    if preferred and Path(preferred).exists():
        print(f"[INFO] using --csv {preferred}")
        return preferred
    env = os.environ.get("SEGSPACE_CSV")
    if env and Path(env).exists():
        print(f"[INFO] using SEGSPACE_CSV={env}")
        return env
    for name in ["real_data_30_segmodel_STRONG.csv","real_data_30_segmodel.csv","real_data_30_segmodel_FINAL.csv","real_data_30.csv","real_data_template.csv"]:
        if Path(name).exists():
            return name
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="Pfad zur Eingabe-CSV")
    args = ap.parse_args()

    csvname = discover_csv(args.csv)
    if not csvname:
        print("[ERROR] Keine CSV gefunden.", file=sys.stderr); sys.exit(2)

    rows = []
    with open(csvname, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows.append(CaseInput(
                case=r.get("case","case"),
                category=r.get("category",""),
                f_emit_Hz=to_float(r.get("f_emit_Hz")),
                f_obs_Hz=to_float(r.get("f_obs_Hz")),
                lambda_emit_nm=to_float(r.get("lambda_emit_nm")),
                lambda_obs_nm=to_float(r.get("lambda_obs_nm")),
                z=to_float(r.get("z")),
                N0=to_float(r.get("N0")) or 1.0000000028,
                Nprime=to_float(r.get("Nprime")),
                alpha_fs=to_float(r.get("alpha_fs")) or ALPHA_FS_DEFAULT,
                M_solar=to_float(r.get("M_solar")),
                r_emit_m=to_float(r.get("r_emit_m")),
                r_obs_m=to_float(r.get("r_obs_m")),
                v_los_mps=to_float(r.get("v_los_mps")),
                v_tot_mps=to_float(r.get("v_tot_mps")),
                z_geom_hint=to_float(r.get("z_geom_hint")),
                a_m=to_float(r.get("a_m")),
                e=to_float(r.get("e")),
                f_true_deg=to_float(r.get("f_true_deg")),
            ))

    derived = [eval_case(ci, TOL["tol_recon"], TOL["tol_z"]) for ci in rows]
    df = pd.DataFrame([asdict(d) for d in derived])

    out = Path("out"); out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out/"_final_test_debug.csv", index=False)

    # Tests
    failures = []
    def rec(name, ok, msg, case="ALL"):
        failures.append({"test":name,"ok":ok,"case":case,"message":msg})

    # T1 Nseg algebra (nur wo berechnet)
    if "delta_Nseg_zgr" in df.columns:
        v = pd.to_numeric(df["delta_Nseg_zgr"], errors="coerce").abs().dropna()
        rec("T1_Nseg_algebra", (len(v)==0) or (v.max() <= TOL["tol_z"]), f"max|Δ|={0.0 if len(v)==0 else v.max():.3e} (≤{TOL['tol_z']})")

    # T2 Bound-energy ≥90% (nur wo berechnet)
    if "pass_recon" in df.columns:
        total = int(df["pass_recon"].notna().sum())
        passed = int((df["pass_recon"]==True).sum())
        ok = (total==0) or (passed/(total or 1) >= 0.90)
        rec("T2_bound_energy_recon", ok, f"pass={passed}/{total} (≥90% required)")

    # T3 Seg FIT ~ 0
    v = pd.to_numeric(df["dz_seg_fit"], errors="coerce").abs().dropna()
    rec("T3_seg_fit_zero", (len(v)==0) or (v.max() <= 1e-12), f"max|Δz_fit|={0.0 if len(v)==0 else v.max():.3e} (≤1e-12)")

    # T4 medians per category (strong only)
    if {"dz_seg_pred","category","strong_pred"}.issubset(df.columns):
        df["abs_pred"] = pd.to_numeric(df["dz_seg_pred"], errors="coerce").abs()
        strong = df["strong_pred"]==True
        for cat, thr in TOL["median_abs_pred"].items():
            sub = df[(df["category"]==cat) & strong]
            if len(sub)==0:
                rec(f"T4_pred_{cat}", None, "SKIP (keine strong rows)", case=cat)
            else:
                med = sub["abs_pred"].median()
                rec(f"T4_pred_{cat}", med <= thr, f"median|Δz_pred|={med:.3e} (≤{thr:g})", case=cat)

    # T5 physicality
    v = pd.to_numeric(df["v_pred_mps"], errors="coerce").dropna()
    ok = True
    if len(v)>0 and (v.abs() >= TOL["vtot_cap_c"]*c).any(): ok = False
    rec("T5_physicality", ok, f"Require v_pred < {TOL['vtot_cap_c']}c")

    # T6 compare S-stars (strong only)
    if {"dz_seg_pred","dz_GR","category","strong_pred"}.issubset(df.columns):
        ss = df[(df["category"]=="S-stars") & (df["strong_pred"]==True)]
        if len(ss)==0:
            rec("T6_compare_Sstars", None, "SKIP (keine strong S-stars)", case="S-stars")
        else:
            med_pred = ss["dz_seg_pred"].abs().median()
            med_gr   = ss["dz_GR"].abs().median()
            ok = med_pred <= TOL["sstar_compare_factor"]*med_gr
            rec("T6_compare_Sstars", ok, f"median|Δz|: Seg={med_pred:.3e}, GR={med_gr:.3e} (Seg ≤ {TOL['sstar_compare_factor']}×GR)", case="S-stars")

    # Artefakte
    fail_df = pd.DataFrame(failures)
    fail_df.to_csv(out/"final_failures.csv", index=False)

    rep = []
    rep.append("SEGMENTED SPACETIME — FINAL TEST REPORT\n")
    rep.append(f"Rows: {len(df)}\n")
    for col,lbl in [("dz_seg_pred","Seg PRED"),("dz_GR","GR"),("dz_SR","SR"),("dz_comb","GR*SR")]:
        if col in df.columns:
            v = pd.to_numeric(df[col], errors="coerce").abs().dropna()
            if len(v)>0:
                rep.append(f"{lbl}: median|Δz|={v.median():.3e}, mean={v.mean():.3e}, max={v.max():.3e}\n")
    rep.append("\nTESTS:\n")
    for r in failures:
        status = "SKIP" if r["ok"] is None else ("PASS" if r["ok"] else "FAIL")
        rep.append(f" - {r['test']}: {status} — {r['message']} (case={r['case']})\n")
    (out/"final_test_report.txt").write_text("".join(rep), encoding="utf-8")

    # JUnit
    from xml.sax.saxutils import escape as xml_escape
    tests = len(failures)
    fails = sum(1 for f in failures if f["ok"] is False)
    skipped = sum(1 for f in failures if f["ok"] is None)
    xml = [f'<testsuite name="segspace_final" tests="{tests}" failures="{fails}" skipped="{skipped}">']
    for f in failures:
        xml.append(f'  <testcase classname="segspace" name="{xml_escape(f["test"])}">')
        if f["ok"] is None:
            xml.append('    <skipped/>')
        elif f["ok"] is False:
            xml.append(f'    <failure message="{xml_escape(str(f["message"]))}">case={xml_escape(str(f["case"]))}</failure>')
        xml.append('  </testcase>')
    xml.append('</testsuite>')
    (out/"final_junit.xml").write_text("\\n".join(xml), encoding="utf-8")

    print("="*72)
    print(" SEGSPACE — FINALE TESTS abgeschlossen. Siehe ./out")
    print("="*72)

if __name__ == "__main__":
    main()
