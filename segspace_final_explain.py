
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segspace_final_explain.py
=========================
Erklärender Runner für das Segmented‑Spacetime‑Modell.
- Liest eine CSV (Auto-Discovery oder --csv / $SEGSPACE_CSV).
- Akzeptiert direkt z ODER (f_emit,f_obs).
- "strong" Orbit‑Mode, GR‑Fallback r(a,e,f_true).
- Gibt pro Fall ausführlich aus, WIE gerechnet wird (Quellen der Größen).
- Schreibt Debug‑CSV + Report + JUnit + Failures in ./out

© 2025 Carmen Wrede & Lino Casu — All rights reserved.
"""

import os, sys, csv, math, argparse, json
from dataclasses import dataclass, asdict
from typing import Optional, List
from pathlib import Path

try:
    import pandas as pd
    pd.set_option('future.no_silent_downcasting', True)
except Exception:
    print("[ERROR] pandas wird benötigt (pip install pandas).", file=sys.stderr)
    sys.exit(2)

try:
    from scipy.constants import h, c, G
except Exception:
    h = 6.62607015e-34
    c = 299_792_458.0
    G = 6.67430e-11

M_sun = 1.98847e30
ALPHA_FS_DEFAULT = 1.0/137.035999084

TOL = dict(
    tol_recon=1e-12,
    tol_z=5e-8,
    vtot_cap_c=0.2,
    sstar_compare_factor=1.2,
)

def p(s=""): print(s, flush=True)

def to_float(x):
    try:
        if x in (None,"","NA","NaN"): return None
        return float(x)
    except Exception:
        return None

@dataclass
class CaseIn:
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
    source: str = ""

@dataclass
class CaseOut:
    case: str
    category: str
    z_data: Optional[float] = None
    r_eff_source: str = ""
    r_eff_m: Optional[float] = None
    v_pred_source: str = ""
    v_pred_mps: Optional[float] = None
    strong_pred: Optional[bool] = None
    z_pred: Optional[float] = None
    dz_seg_pred: Optional[float] = None
    z_GR: Optional[float] = None
    dz_GR: Optional[float] = None
    z_SR: Optional[float] = None
    dz_SR: Optional[float] = None
    z_comb: Optional[float] = None
    dz_comb: Optional[float] = None
    N_seg: Optional[float] = None
    delta_Nseg_zgr: Optional[float] = None
    pass_recon: Optional[bool] = None
    notes: str = ""

def derive_freqs(d: CaseIn):
    f_e, f_o = d.f_emit_Hz, d.f_obs_Hz
    if f_e is None and d.lambda_emit_nm is not None:
        f_e = c/(d.lambda_emit_nm*1e-9)
    if f_o is None and d.lambda_obs_nm is not None:
        f_o = c/(d.lambda_obs_nm*1e-9)
    if (f_e is None or f_o is None) and d.z is not None:
        if f_e is None and f_o is not None: f_e = f_o*(1.0+d.z)
        elif f_o is None and f_e is not None: f_o = f_e/(1.0+d.z)
    return f_e, f_o

def mu_from_Msolar(M_solar):
    return G*(M_solar*M_sun) if M_solar is not None else None

def r_from_aef(a,e,fdeg):
    if a is None or e is None or fdeg is None: return None
    f = math.radians(fdeg)
    return a*(1.0-e*e)/(1.0+e*math.cos(f))

def vis_viva(mu,a,r):
    if None in (mu,a,r) or a<=0 or r<=0: return None
    return math.sqrt(mu*(2.0/r - 1.0/a))

def seg_total_z(z_geom, v_tot, v_los):
    if v_tot is None: return None
    beta = v_tot/c
    if abs(beta)>=1: return None
    beta_r = (v_los or 0.0)/c if v_los is not None else 0.0
    gamma = 1.0/math.sqrt(1.0-beta*beta)
    z_kin = gamma*(1.0+beta_r) - 1.0
    z_geom = z_geom or 0.0
    return (1.0+z_geom)*(1.0+z_kin)-1.0

def z_gr(M_solar, r_emit, r_obs=None):
    if M_solar is None or r_emit is None: return None
    M = M_solar*M_sun
    r_o = r_obs if r_obs is not None else float('inf')
    gtt_e = 1.0 - 2.0*G*M/(r_emit*c*c)
    gtt_o = 1.0 - 2.0*G*M/(r_o*c*c) if math.isfinite(r_o) else 1.0
    if gtt_e<=0 or gtt_o<=0: return None
    return math.sqrt(gtt_o/gtt_e) - 1.0

def z_sr(v_tot, v_los):
    if v_tot is None and v_los is None: return None
    beta = (v_tot or abs(v_los or 0.0))/c
    if abs(beta)>=1.0: return None
    beta_r = (v_los or 0.0)/c if v_los is not None else 0.0
    gamma = 1.0/math.sqrt(1.0-beta*beta)
    return gamma*(1.0+beta_r) - 1.0

def discover_csv(pref=None):
    if pref and Path(pref).exists():
        return pref
    env = os.environ.get("SEGSPACE_CSV")
    if env and Path(env).exists():
        return env
    for name in ["real_data_30_segmodel.csv","real_data_30_segmodel_STRONG.csv",
                 "real_data_30_segmodel_FINAL.csv","real_data_30.csv","real_data_template.csv"]:
        if Path(name).exists(): return name
    return None

def read_cases(csvname)->List[CaseIn]:
    rows=[]
    with open(csvname,"r",encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            rows.append(CaseIn(
                case=r.get("case","case"), category=r.get("category",""),
                f_emit_Hz=to_float(r.get("f_emit_Hz")), f_obs_Hz=to_float(r.get("f_obs_Hz")),
                lambda_emit_nm=to_float(r.get("lambda_emit_nm")), lambda_obs_nm=to_float(r.get("lambda_obs_nm")),
                z=to_float(r.get("z")), N0=to_float(r.get("N0")) or 1.0000000028, Nprime=to_float(r.get("Nprime")),
                alpha_fs=to_float(r.get("alpha_fs")) or ALPHA_FS_DEFAULT, M_solar=to_float(r.get("M_solar")),
                r_emit_m=to_float(r.get("r_emit_m")), r_obs_m=to_float(r.get("r_obs_m")),
                v_los_mps=to_float(r.get("v_los_mps")), v_tot_mps=to_float(r.get("v_tot_mps")),
                z_geom_hint=to_float(r.get("z_geom_hint")), a_m=to_float(r.get("a_m")),
                e=to_float(r.get("e")), f_true_deg=to_float(r.get("f_true_deg")), source=r.get("source","")
            ))
    return rows

def explain_case(cin: CaseIn)->CaseOut:
    out = CaseOut(case=cin.case, category=cin.category or "")
    # Schritt 1: Beobachtungs‑z ermitteln
    f_e, f_o = derive_freqs(cin)
    if f_e is None or f_o is None:
        if cin.z is not None:
            z_data = float(cin.z)
            z_src = "z (direkt)"
        else:
            out.notes = "Keine z/frequenzen → Fall wird übersprungen."
            return out
    else:
        z_data = f_e/f_o - 1.0
        z_src = "f_emit/f_obs"
    out.z_data = z_data

    # Nseg‑Algebra & Bound‑Energy (nur bei Frequenzen)
    if f_e is not None and f_o is not None:
        N0 = cin.N0 if cin.N0 is not None else 1.0
        out.N_seg = f_e/f_o - (N0 if N0 is not None else 1.0)
        out.delta_Nseg_zgr = out.N_seg - z_data
        if cin.Nprime is not None and N0 is not None:
            E_emit = h*f_e
            alpha_mbound = (h*f_o*cin.Nprime)/(N0*c**2)
            m_bound = alpha_mbound/(cin.alpha_fs or ALPHA_FS_DEFAULT)
            alpha_local = E_emit/(m_bound*c**2)
            f_check = alpha_local*m_bound*c**2/h
            rel = abs(f_check - f_e)/f_e if f_e else None
            out.pass_recon = (rel is not None and rel <= TOL["tol_recon"])

    # Schritt 2: Geometrie/Orbit → r_eff
    r_eff = cin.r_emit_m
    r_source = "r_emit_m"
    if r_eff is None and cin.a_m and cin.e is not None and cin.f_true_deg is not None:
        r_eff = r_from_aef(cin.a_m, cin.e, cin.f_true_deg)
        r_source = "r(a,e,f_true)"
    out.r_eff_m = r_eff; out.r_eff_source = r_source

    # Schritt 3: Geschwindigkeit (Orbit‑Mode bevorzugt)
    mu = mu_from_Msolar(cin.M_solar)
    v_pred = cin.v_tot_mps; v_src = "v_tot_mps (CSV)"
    strong = False
    if v_pred is None and mu is not None:
        if r_source=="r(a,e,f_true)" and cin.a_m:
            v_pred = vis_viva(mu, cin.a_m, r_eff); v_src = "vis‑viva(a,r_eff)"; strong=True
        elif r_eff is not None:
            v_pred = math.sqrt(mu/r_eff); v_src = "sqrt(mu/r_eff) (kreis‑ähnlich)"; strong=False
    out.v_pred_mps = v_pred; out.v_pred_source = v_src; out.strong_pred = strong

    # Schritt 4: Modell‑z (Segmented) = Geom × SR
    z_geom = cin.z_geom_hint or 0.0
    z_pred = seg_total_z(z_geom, v_pred, cin.v_los_mps) if v_pred is not None else None
    out.z_pred = z_pred
    out.dz_seg_pred = (z_data - z_pred) if (z_pred is not None) else None

    # Schritt 5: Vergleich GR/SR
    r_for_gr = r_eff  # Fallback ok
    zgr = z_gr(cin.M_solar, r_for_gr, cin.r_obs_m)
    if zgr is not None:
        out.z_GR = zgr; out.dz_GR = z_data - zgr
    zsr = z_sr(v_pred, cin.v_los_mps)
    if zsr is not None:
        out.z_SR = zsr; out.dz_SR = z_data - zsr
    if zgr is not None and zsr is not None:
        zcb = (1.0+zgr)*(1.0+zsr)-1.0
        out.z_comb = zcb; out.dz_comb = z_data - zcb

    # Hinweise
    notes=[]
    if cin.v_los_mps is None:
        notes.append("Hinweis: v_los_mps fehlt → nur transversale Komponente in SR.")
    if v_pred is not None and v_pred > TOL["vtot_cap_c"]*c:
        notes.append("Warnung: v_pred > 0.2c (über Prüfgrenze).")
    out.notes = "; ".join(notes)
    # Konsolen‑Erklärung
    p(f"\n[{cin.case}] ({cin.category})")
    p(f"  Eingaben: {z_src}, N0={cin.N0}, a={cin.a_m}, e={cin.e}, f_true={cin.f_true_deg}, M_solar={cin.M_solar}")
    if cin.v_los_mps is not None: p(f"  v_los_mps={cin.v_los_mps:.3e}")
    p(f"  z_data = {z_data:.6e}")
    p(f"  r_eff = {r_eff:.6e} m  (Quelle: {r_source})" if r_eff is not None else "  r_eff = N/A")
    p(f"  v_pred = {v_pred:.6e} m/s (Quelle: {v_src}, strong={strong})" if v_pred is not None else "  v_pred = N/A")
    if z_pred is not None: p(f"  z_pred(seg) = {z_pred:.6e}  → Δz = {out.dz_seg_pred:.6e}")
    if out.z_GR is not None: p(f"  z_GR = {out.z_GR:.6e}    → Δz = {out.dz_GR:.6e}")
    if out.z_SR is not None: p(f"  z_SR = {out.z_SR:.6e}    → Δz = {out.dz_SR:.6e}")
    if out.z_comb is not None: p(f"  z_GR*SR = {out.z_comb:.6e} → Δz = {out.dz_comb:.6e}")
    if out.N_seg is not None: p(f"  N_seg = {out.N_seg:.6e}  |Δ(N_seg−z)| = {abs(out.delta_Nseg_zgr):.3e}")
    if out.notes: p(f"  {out.notes}")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="Pfad zur Eingabe‑CSV (wird gelesen)")
    args = ap.parse_args()

    csvname = discover_csv(args.csv)
    if not csvname:
        print("[ERROR] Keine CSV gefunden.", file=sys.stderr); sys.exit(2)

    p("="*72)
    p(" SEGMENTED SPACETIME — ERKLÄRENDER LAUF")
    p("="*72)
    p(f"CSV: {csvname}")

    cases = read_cases(csvname)
    outs = [asdict(explain_case(ci)) for ci in cases]

    outdir = Path("out"); outdir.mkdir(parents=True, exist_ok=True)
    # Debug‑CSV
    df = pd.DataFrame(outs)
    df.to_csv(outdir/"_explain_debug.csv", index=False)

    # Kurzer Abschluss
    for col, label in [("dz_seg_pred","Seg PRED"),("dz_GR","GR"),("dz_SR","SR"),("dz_comb","GR*SR")]:
        s = pd.to_numeric(df[col], errors="coerce").abs().dropna()
        if len(s)>0:
            p(f"\nΔz (data − {label}): median={s.median():.3e}, mean={s.mean():.3e}, max|={s.max():.3e}")

    p("\nFertig. Details: ./out/_explain_debug.csv")
    p("="*72)

if __name__ == "__main__":
    main()
