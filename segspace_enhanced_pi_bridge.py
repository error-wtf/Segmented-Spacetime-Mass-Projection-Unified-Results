#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEGSPACE — ENHANCED TEST + π‑BRIDGE (Chudnovsky / Builtin / ϕ)
=================================================================
Vergleicht GR, SR, GR*SR und den Segmented‑Spacetime‑Weg auf einem
Dataset (CSV), mit frei wählbarer π‑Quelle:

  --pi-source {chud,builtin,phi}
    chud    → Chudnovsky‑Serie (Decimal; --prec, --chud-terms)
    builtin → math.pi (double)
    phi     → π ≈ 5·arccos(ϕ/2) (Demo, double)

Zusätzlich:
- Bericht mit Median(|Δz|) je Modell und Seg/GR‑Performance
- Punktweise Faktoren: Seg/GR und Seg/(GR*SR) (Quartile & Trefferquoten)
- Debug‑CSV mit allen Zwischenwerten
- Optionaler Balken‑Plot der Mediane

Beispiel:
  python segspace_enhanced_pi_bridge.py --csv real_data_full.csv \
    --prefer-z --seg-mode hybrid --pi-source chud --prec 200 --chud-terms 16
"""

from __future__ import annotations
import argparse, csv, math, time, sys
from pathlib import Path
from decimal import Decimal as D, getcontext

try:
    import pandas as pd
except Exception:
    pd = None

# ─────────────────────────────────────────────────────────────────────────────
# π-Quellen
# ─────────────────────────────────────────────────────────────────────────────

def chudnovsky_pi(prec: int = 120, terms: int = 12) -> D:
    """
    π via Chudnovsky (Decimal). ~14 Dezimalstellen pro Term.
    """
    if prec < 50:
        prec = 50
    if terms < 1:
        terms = 1
    getcontext().prec = prec + 10  # guard digits

    C = 640320
    C3 = C**3

    # simple factorial (ok für kleine 'terms')
    def fact(n: int) -> int:
        f = 1
        for i in range(2, n+1):
            f *= i
        return f

    S = D(0)
    for k in range(terms):
        sign = -1 if (k & 1) else 1
        sixk   = fact(6*k)
        threek = fact(3*k)
        kfact  = fact(k)
        num = D(sign) * D(sixk) * D(13591409 + 545140134*k)
        den = D(threek) * (D(kfact)**3) * (D(C3)**k)
        S += num / den

    pi = (D(426880) * D(10005).sqrt()) / S
    getcontext().prec = prec
    return +pi

def builtin_pi() -> D:
    return D(str(math.pi))

def phi_pi_demo() -> D:
    """
    π aus ϕ‑Identität (Demo‑Genauigkeit):
        π ≈ 5·arccos(ϕ/2),  ϕ = (1+√5)/2
    Achtung: nutzt double für acos → nicht für Hochpräzision.
    """
    phi = (1.0 + 5.0**0.5) / 2.0
    x = max(-1.0, min(1.0, phi/2.0))
    return D(str(5.0 * math.acos(x)))

# ─────────────────────────────────────────────────────────────────────────────
# Konstanten & Helfer
# ─────────────────────────────────────────────────────────────────────────────

G     = 6.67430e-11
c     = 299_792_458.0
M_sun = 1.98847e30

def deg2rad_with_pi(deg: float, pi_float: float) -> float:
    return deg * (pi_float / 180.0)

def robust_median(vals):
    try:
        import statistics as stats
        return stats.median(vals) if vals else float('nan')
    except Exception:
        if not vals: return float('nan')
        v = sorted(vals); n = len(v)
        return v[n//2] if (n % 2) else 0.5*(v[n//2 - 1] + v[n//2])

def qtiles(vec):
    if not vec:
        return (float('nan'), float('nan'), float('nan'))
    v = sorted(vec)
    n = len(v)
    def q(p):
        k = p*(n-1)
        lo, hi = int(math.floor(k)), int(math.ceil(k))
        if lo == hi: return v[lo]
        t = k - lo
        return v[lo]*(1-t) + v[hi]*t
    return (q(0.25), q(0.5), q(0.75))  # Q1, Median, Q3

def f2(x, default=None):
    try:
        if x is None: return default
        xs = str(x).strip()
        if xs == "": return default
        return float(xs)
    except Exception:
        return default

# ─────────────────────────────────────────────────────────────────────────────
# Geometrie/Physik
# ─────────────────────────────────────────────────────────────────────────────

def r_from_orbit(a_m, e, f_true_rad):
    denom = (1.0 + e*math.cos(f_true_rad))
    if denom == 0:
        return float('nan')
    return a_m * (1.0 - e*e) / denom

def vis_viva(mu, a_m, r_m):
    term = mu * (2.0/max(r_m, 1e-99) - 1.0/max(a_m, 1e-99))
    return math.sqrt(term) if term >= 0.0 else float('nan')

def z_gravitational(M_central_kg, r_m):
    if M_central_kg is None or r_m is None: return float('nan')
    if not (math.isfinite(M_central_kg) and math.isfinite(r_m)): return float('nan')
    if M_central_kg <= 0 or r_m <= 0: return float('nan')
    rs = 2.0 * G * M_central_kg / (c**2)
    if r_m <= rs: return float('nan')
    return 1.0 / math.sqrt(1.0 - rs/r_m) - 1.0

def z_special_rel(v_tot_mps, v_los_mps=0.0):
    if v_tot_mps is None or not math.isfinite(v_tot_mps):
        return float('nan')
    v_tot_abs = abs(v_tot_mps)
    if v_tot_abs <= 0:
        return float('nan')
    beta = min(v_tot_abs / c, 0.999999999999)
    beta_los = 0.0 if v_los_mps is None or (not math.isfinite(v_los_mps)) else (v_los_mps / c)
    gamma = 1.0 / math.sqrt(1.0 - beta*beta)
    return gamma * (1.0 + beta_los) - 1.0

def z_combined(z_gr, z_sr):
    zgr = 0.0 if (z_gr is None or not math.isfinite(z_gr)) else z_gr
    zsr = 0.0 if (z_sr is None or not math.isfinite(z_sr)) else z_sr
    return (1.0 + zgr) * (1.0 + zsr) - 1.0

# ─────────────────────────────────────────────────────────────────────────────
# Δ(M) – log‑normiertes Korrekturmodell
# ─────────────────────────────────────────────────────────────────────────────

def build_delta_percent(dataset_masses_kg, A=98.01, alpha=2.7177e4, B=1.96):
    logs = [math.log10(m) for m in dataset_masses_kg if (m is not None and m > 0)]
    if not logs:
        Lmin=Lmax=0.0
    else:
        Lmin, Lmax = min(logs), max(logs)
        if abs(Lmax - Lmin) < 1e-12:
            m = Lmin; Lmin, Lmax = m - 0.5, m + 0.5
    ΔL = (Lmax - Lmin) if (Lmax > Lmin) else 1.0

    def delta_percent(M_kg: float) -> float:
        if M_kg is None or not math.isfinite(M_kg) or M_kg <= 0:
            return 0.0
        rs = 2.0 * G * M_kg / (c**2)
        raw = A * math.exp(-alpha * rs) + B
        norm = (math.log10(M_kg) - Lmin) / ΔL
        norm = min(1.0, max(0.0, norm))
        return raw * norm
    return delta_percent

# ─────────────────────────────────────────────────────────────────────────────
# Seg‑Vorhersage
# ─────────────────────────────────────────────────────────────────────────────

def z_seg_pred_hint(row, z_sr: float, z_grsr: float) -> float:
    z_hint = f2(row.get("z_geom_hint"))
    if z_hint is not None and math.isfinite(z_hint):
        return z_combined(z_hint, z_sr)
    return z_grsr

def z_seg_pred_deltam(row, z_gr: float, z_sr: float,
                      A_pct: float, B_pct: float, alpha: float,
                      delta_percent_fn) -> float:
    M_solar = f2(row.get("M_solar"))
    if M_solar is None or not math.isfinite(M_solar) or M_solar <= 0:
        return z_combined(z_gr, z_sr)
    M = M_solar * M_sun
    delta_pct = delta_percent_fn(M)
    z_gr_scaled = z_gr * (1.0 + delta_pct/100.0)
    return z_combined(z_gr_scaled, z_sr)

def z_seg_pred(mode: str, row, z_gr: float, z_sr: float, z_grsr: float,
               dmA: float, dmB: float, dmAlpha: float,
               delta_percent_fn) -> float:
    m = (mode or "hybrid").lower().strip()
    if m == "hint":
        return z_seg_pred_hint(row, z_sr, z_grsr)
    elif m == "deltam":
        return z_seg_pred_deltam(row, z_gr, z_sr, dmA, dmB, dmAlpha, delta_percent_fn)
    else:  # hybrid: HINT falls vorhanden, sonst ΔM
        z_hint = f2(row.get("z_geom_hint"))
        if z_hint is not None and math.isfinite(z_hint):
            return z_seg_pred_hint(row, z_sr, z_grsr)
        return z_seg_pred_deltam(row, z_gr, z_sr, dmA, dmB, dmAlpha, delta_percent_fn)

# ─────────────────────────────────────────────────────────────────────────────
# CSV‑I/O
# ─────────────────────────────────────────────────────────────────────────────

def load_rows(csv_path: Path) -> list[dict]:
    if pd is not None:
        try:
            df = pd.read_csv(csv_path)
            return df.to_dict(orient="records")
        except Exception:
            pass
    rows = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            rows.append(row)
    return rows

def observed_z_from_row(row: dict, prefer_z: bool):
    z_direct = f2(row.get("z"))
    f_emit   = f2(row.get("f_emit_Hz"))
    f_obs    = f2(row.get("f_obs_Hz"))
    if prefer_z and z_direct is not None:
        return z_direct, "z"
    if (f_emit is not None) and (f_obs is not None) and (f_obs != 0.0):
        return (f_emit/f_obs - 1.0), "freq"
    return (z_direct, ("z" if z_direct is not None else "missing"))

# ─────────────────────────────────────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate(csv_path: Path, prefer_z: bool, seg_mode: str,
             dmA: float, dmB: float, dmAlpha: float,
             pi_float_for_deg: float,
             make_plots: bool, outdir: Path):
    rows = load_rows(csv_path)
    if not rows:
        print(f"[ERROR] CSV leer oder unlesbar: {csv_path}")
        sys.exit(2)

    # Massenbereich für ΔM‑Normierung
    Ms = []
    for r in rows:
        Msun = f2(r.get("M_solar"))
        if Msun is not None and math.isfinite(Msun) and Msun > 0:
            Ms.append(Msun * M_sun)
    delta_percent_fn = build_delta_percent(Ms, A=dmA, alpha=dmAlpha, B=dmB)

    abs_res = {"seg": [], "gr": [], "sr": [], "grsr": []}
    pairs_gr, pairs_grsr = [], []  # für punktweise Verhältnisse
    used = 0
    dbg = []

    for i, r in enumerate(rows):
        case = str(r.get("case", "") or f"ROW{i}")
        z_obs, z_src = observed_z_from_row(r, prefer_z=prefer_z)
        if z_obs is None or not math.isfinite(z_obs):
            continue

        # Radien/Geschwindigkeiten
        M_solar = f2(r.get("M_solar"))
        M_c = (M_solar or 0.0) * M_sun

        a_m  = f2(r.get("a_m"))
        e    = f2(r.get("e"))
        fdeg = f2(r.get("f_true_deg"))
        r_emit_m = f2(r.get("r_emit_m"))

        if r_emit_m is not None and math.isfinite(r_emit_m) and r_emit_m > 0:
            r_eff = r_emit_m
        elif all(v is not None for v in (a_m, e, fdeg)):
            r_eff = r_from_orbit(a_m, e, deg2rad_with_pi(fdeg, pi_float_for_deg))
        else:
            r_eff = None

        v_los = f2(r.get("v_los_mps")) or 0.0
        v_tot = f2(r.get("v_tot_mps"))
        if (v_tot is None or not math.isfinite(v_tot)) and (M_c > 0.0) and (a_m not in (None,0.0)) and (r_eff not in (None,0.0)):
            mu = G * M_c
            v_tot = vis_viva(mu, a_m, r_eff)

        z_gr   = z_gravitational(M_c, r_eff)
        z_sr   = z_special_rel(v_tot, v_los)
        z_grsr = z_combined(z_gr, z_sr)
        z_seg  = z_seg_pred(seg_mode, r, z_gr, z_sr, z_grsr, dmA, dmB, dmAlpha, delta_percent_fn)

        # Residuen erfassen
        if z_seg  is not None and math.isfinite(z_seg):  abs_res["seg"].append(abs(z_obs - z_seg))
        if z_gr   is not None and math.isfinite(z_gr):   abs_res["gr"].append(abs(z_obs - z_gr))
        if z_sr   is not None and math.isfinite(z_sr):   abs_res["sr"].append(abs(z_obs - z_sr))
        if z_grsr is not None and math.isfinite(z_grsr): abs_res["grsr"].append(abs(z_obs - z_grsr))

        # Punktweise Verhältnisse (nur wenn Nenner > 0)
        if (z_gr  is not None and math.isfinite(z_gr)) and abs(z_obs - z_gr)  > 0:
            pairs_gr.append(  (abs(z_obs - z_seg),  abs(z_obs - z_gr)) )
        if (z_grsr is not None and math.isfinite(z_grsr)) and abs(z_obs - z_grsr)> 0:
            pairs_grsr.append((abs(z_obs - z_seg),  abs(z_obs - z_grsr)) )

        used += 1

        dbg.append({
            **r,
            "case": case,
            "z_obs": z_obs, "z_source": z_src,
            "r_eff_m": r_eff if (r_eff is not None and math.isfinite(r_eff)) else "",
            "v_tot_mps_eff": v_tot if (v_tot is not None and math.isfinite(v_tot)) else "",
            "z_gr": z_gr if (z_gr is not None and math.isfinite(z_gr)) else "",
            "z_sr": z_sr if (z_sr is not None and math.isfinite(z_sr)) else "",
            "z_grsr": z_grsr if (z_grsr is not None and math.isfinite(z_grsr)) else "",
            "z_seg": z_seg if (z_seg is not None and math.isfinite(z_seg)) else "",
        })

    med = {k: robust_median(v) for k, v in abs_res.items()}

    # Verhältnisse Seg/GR, Seg/(GR*SR)
    ratios_seg_gr   = [s/g   for (s,g)   in pairs_gr   if g>0]
    ratios_seg_grsr = [s/gsr for (s,gsr) in pairs_grsr if gsr>0]
    q1_gr, med_gr_ratio, q3_gr   = qtiles(ratios_seg_gr)
    q1_gs, med_gs_ratio, q3_gs   = qtiles(ratios_seg_grsr)

    better_gr   = sum(1 for (s,g)   in pairs_gr   if s < g)
    better_gsr  = sum(1 for (s,gsr) in pairs_grsr if s < gsr)
    frac_better_gr  = better_gr  / len(pairs_gr)   if pairs_gr   else float('nan')
    frac_better_gsr = better_gsr / len(pairs_grsr) if pairs_grsr else float('nan')

    # Debug‑CSV
    outdir.mkdir(parents=True, exist_ok=True)
    dbg_csv = outdir / "segspace_pi_bridge_debug.csv"
    try:
        if pd is not None:
            pd.DataFrame(dbg).to_csv(dbg_csv, index=False)
        else:
            # Fallback
            if dbg:
                with dbg_csv.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(dbg[0].keys()))
                    writer.writeheader()
                    for row in dbg:
                        writer.writerow(row)
        wrote = True
    except Exception as ex:
        wrote = False
        print(f"[WARN] Debug‑CSV konnte nicht geschrieben werden: {ex}")

    # Bericht
    print("="*61)
    print(" SEGMENTED SPACETIME – Δ(M) + π‑Bridge (Chud/Builtin/ϕ)")
    print("="*61)
    print(f"CSV               : {csv_path.name}")
    print(f"Zeilen (verwendet): {used}")
    print(f"π‑Quelle          : {PI_SOURCE_LABEL}")
    if PI_SOURCE_LABEL.startswith("chud"):
        print(f"                    (Chud: terms={CHUD_TERMS}, prec={PRECISION})")
    print(f"Seg‑Mode          : {seg_mode}")
    print(f"ΔM‑Params         : A={dmA:.2f}%, α={dmAlpha:.0f} [1/m], B={dmB:.2f}%")
    print("-"*61)
    print(f"Median |Δz|  GR   : {med['gr']:.9e}")
    print(f"Median |Δz|  SR   : {med['sr']:.9e}")
    print(f"Median |Δz|  GR*SR: {med['grsr']:.9e}")
    print(f"Median |Δz|  Seg  : {med['seg']:.9e}")
    perf = med['seg'] / med['gr'] if (med['gr'] and med['gr']>0) else float('nan')
    print(f"Performance (Seg/GR): {perf:.6f} ×")
    print("-"*61)
    print("Punktweise Faktoren (Seg / Baseline):")
    print(f"  vs GR   → Q1={q1_gr:.3e}, Q2={med_gr_ratio:.3e}, Q3={q3_gr:.3e} | better={better_gr}/{len(pairs_gr)} ({frac_better_gr:.1%})")
    print(f"  vs GR*SR→ Q1={q1_gs:.3e}, Q2={med_gs_ratio:.3e}, Q3={q3_gs:.3e} | better={better_gsr}/{len(pairs_grsr)} ({frac_better_gsr:.1%})")
    if wrote:
        print(f"Debug‑CSV          : {dbg_csv.resolve()}")

    # Optional: Plot
    if make_plots:
        try:
            import matplotlib.pyplot as plt
            models = ["GR","SR","GR*SR","Seg"]
            Y = [med['gr'], med['sr'], med['grsr'], med['seg']]
            plt.figure(figsize=(7,4))
            plt.bar(models, Y)
            plt.yscale('log')
            plt.ylabel('Median |Δz| (log)')
            plt.title('Medianfehler pro Modell')
            plt.grid(True, axis='y', which='both', ls='--', alpha=0.4)
            out_png = outdir / "segspace_median_plot.png"
            plt.tight_layout(); plt.savefig(out_png, dpi=180)
            print(f"Plot gespeichert   : {out_png.resolve()}")
            # plt.show()  # optional
        except Exception as ex:
            print(f"[WARN] Plot fehlgeschlagen: {ex}")

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global PI_SOURCE_LABEL, CHUD_TERMS, PRECISION

    ap = argparse.ArgumentParser(description="Segmented Spacetime vs GR/SR mit π‑Bridge")
    ap.add_argument("--csv", required=True, help="Pfad zur CSV (z.B. real_data_full.csv)")
    ap.add_argument("--prefer-z", action="store_true", help="z-Spalte bevorzugen (statt Frequenzpaaren)")
    ap.add_argument("--seg-mode", default="hybrid", choices=["hint","deltam","hybrid"], help="Segmented-Variante")
    ap.add_argument("--deltam-A", type=float, default=98.01, help="ΔM Parameter A (%%)")
    ap.add_argument("--deltam-B", type=float, default=1.96, help="ΔM Parameter B (%%)")
    ap.add_argument("--deltam-alpha", type=float, default=27177.0, help="ΔM alpha [1/m]")
    ap.add_argument("--pi-source", default="chud", choices=["chud","builtin","phi"], help="π‑Quelle für Grad→Bogenmaß")
    ap.add_argument("--prec", type=int, default=120, help="Decimal‑Präzision für Chudnovsky")
    ap.add_argument("--chud-terms", type=int, default=12, help="Serienterme für Chudnovsky")
    ap.add_argument("--plots", action="store_true", help="Balkenplot der Mediane speichern")
    ap.add_argument("--outdir", default="segspace_pi_bridge_out", help="Ausgabe‑Ordner")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] CSV nicht gefunden: {csv_path}")
        sys.exit(2)

    # π beschaffen
    t0 = time.time()
    if args.pi_source == "chud":
        piD = chudnovsky_pi(args.prec, args.chud_terms)
        PI_SOURCE_LABEL = f"chud"
    elif args.pi_source == "builtin":
        piD = builtin_pi()
        PI_SOURCE_LABEL = "builtin"
    else:
        piD = phi_pi_demo()
        PI_SOURCE_LABEL = "phi_demo"
    t1 = time.time()

    # Hinweis: π wird hier nur für Grad→Bogenmaß (f_true_deg → rad) als float gebraucht
    pi_float_for_deg = float(piD)
    CHUD_TERMS = args.chud_terms
    PRECISION  = args.prec

    # Kopf ausgeben
    print("\n=============================================================")
    print(" SEGMENTED SPACETIME – Δ(M) + CHUDNOVSKY‑π BRIDGE (Runner)")
    print("=============================================================")
    if args.pi_source == "chud":
        print(f"π (Chudnovsky)     : {str(piD)[:100]}...")
        print(f"π compute time     : {1e3*(t1-t0):.3f} ms")
    else:
        print(f"π (source={args.pi_source}) : {piD}")

    # Eval
    outdir = Path(args.outdir)
    evaluate(csv_path=csv_path,
             prefer_z=args.prefer_z,
             seg_mode=args.seg_mode,
             dmA=args.deltam_A, dmB=args.deltam_B, dmAlpha=args.deltam_alpha,
             pi_float_for_deg=pi_float_for_deg,
             make_plots=args.plots,
             outdir=outdir)

if __name__ == "__main__":
    main()
