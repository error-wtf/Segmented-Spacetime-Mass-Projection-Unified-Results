#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Segment-Redshift Add-on
Nur Ergänzung – KEINE Änderungen an bestehender Pipeline.
Schreibt ausschließlich nach reports/ (und reports/figures bei --seg-plot).
"""

import argparse, math, json, csv, sys, os
from pathlib import Path

# UTF-8 Setup für Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, Exception):
        pass

def _band_from_freq(nu_hz: float) -> str:
    if nu_hz < 3e6:   return "VLF/MF"
    if nu_hz < 3e8:   return "Radio"
    if nu_hz < 3e11:  return "Microwave"
    if nu_hz < 4e14:  return "IR"
    if nu_hz < 7.5e14:return "Optical"
    if nu_hz < 3e16:  return "UV"
    if nu_hz < 3e19:  return "X-ray"
    return "Gamma"

def chi_from_phi(phi: float) -> float:
    return math.exp(-float(phi))

def phi_from_N(r_grid, N_grid):
    import numpy as np
    r = np.asarray(r_grid, float)
    N = np.asarray(N_grid, float)
    ln_r = np.log(np.clip(r, 1e-30, None))
    return float(np.trapz(N, ln_r))

def phi_from_rho_pr(r_grid, rho, pr):
    import numpy as np
    alpha = 1.0  # ggf. später kalibrieren
    r = np.asarray(r_grid, float)
    ln_r = np.log(np.clip(r, 1e-30, None))
    integrand = alpha * (np.abs(np.asarray(rho, float)) + np.abs(np.asarray(pr, float)))
    return float(np.trapz(integrand, ln_r))

def phi_from_gtt(gtt_em, gtt_out=-1.0):
    return 0.5 * math.log(float(gtt_out) / float(gtt_em))

def predict_nu_infinity(nu_em, phi):
    return float(nu_em) * math.exp(-float(phi))

def _load_first_existing(paths):
    for p in paths:
        pp = Path(p)
        if pp.exists():
            return pp
    return None

def _read_any_table(pp):
    """
    Liest CSV oder JSON und gibt dict(key->list) zurück.
    """
    import pandas as pd
    if str(pp).lower().endswith(".json"):
        data = json.loads(pp.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {k: (v if isinstance(v, list) else v) for k, v in data.items()}
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Liste von Records
            import pandas as pd
            df = pd.DataFrame(data)
            return {k: df[k].tolist() for k in df.columns}
        return {"_raw": data}
    df = pd.read_csv(pp)
    return {k: df[k].tolist() for k in df.columns}

def _pick(d, candidates, default=None):
    for k in candidates:
        if k in d:
            return d[k]
    return default

def _slice_between_radii(r, cols, r_em, r_out):
    import numpy as np
    r = np.asarray(r, float)
    mask = (r >= min(r_em, r_out)) & (r <= max(r_em, r_out))
    out = [r[mask]]
    for c in cols:
        out.append(np.asarray(c, float)[mask])
    return out

def main():
    ap = argparse.ArgumentParser(description="SSZ Segment-Redshift Add-on (non-intrusive)")
    ap.add_argument("--segment-redshift", action="store_true", help="Aktiviere Berechnung")
    ap.add_argument("--nu-em", type=float, default=1.0e18, help="Emissionsfrequenz in Hz (Default: 1e18)")
    ap.add_argument("--r-em", type=float, default=2.0, help="Emissionsradius in r_s (Default: 2.0)")
    ap.add_argument("--r-out", type=float, default=50.0, help="äußerer Referenzradius in r_s (Default: 50)")
    ap.add_argument("--proxy", choices=["N","rho-pr","gtt"], default="N", help="Proxy für Phi")
    ap.add_argument("--seg-plot", action="store_true", help="Plot schreiben (reports/figures)")
    # optionale Pfade, ohne Pflicht
    ap.add_argument("--src-N", nargs="*", default=[
        "reports/ring_chain.csv","agent_out/reports/ring_chain.csv",
        "reports/ring_chain.json","agent_out/reports/ring_chain.json"
    ])
    ap.add_argument("--src-rhopr", nargs="*", default=[
        "reports/energy_conditions.csv","agent_out/reports/energy_conditions.csv",
        "reports/stress_energy.csv","agent_out/reports/stress_energy.csv"
    ])
    ap.add_argument("--src-gtt", nargs="*", default=[
        "reports/metric_profile.csv","agent_out/reports/metric_profile.csv",
        "reports/metric_profile.json","agent_out/reports/metric_profile.json"
    ])
    args = ap.parse_args()

    # Nichts tun, wenn Flag nicht gesetzt (explizit non-invasive)
    if not args.segment_redshift:
        print("[SSZ][addon] segment-redshift disabled (use --segment-redshift).")
        return

    Path("reports").mkdir(parents=True, exist_ok=True)
    out_csv = Path("reports/segment_redshift.csv")
    out_md  = Path("reports/segment_redshift.md")
    out_plot= Path("reports/figures/fig_shared_segment_redshift_profile.png")

    # Quelle wählen
    src = None
    if args.proxy == "N":
        src = _load_first_existing(args.src_N)
    elif args.proxy == "rho-pr":
        src = _load_first_existing(args.src_rhopr)
    else:
        src = _load_first_existing(args.src_gtt)

    if not src:
        out_md.write_text(
            f"# Segment Redshift\nQuelle für proxy={args.proxy} nicht gefunden.\n",
            encoding="utf-8"
        )
        print("[SSZ][addon] Quelle fehlt → reports/segment_redshift.md")
        return

    data = _read_any_table(src)

    # Spalten finden
    r = _pick(data, ["r_over_rs","r/rs","radius_rs","r_rs","r"])
    if r is None:
        out_md.write_text(
            f"# Segment Redshift\nFehlende Radius-Spalte in {src.name}.\n"
            f"Erwartet: r_over_rs | r/rs | radius_rs | r_rs | r\n",
            encoding="utf-8"
        )
        print("[SSZ][addon] Radius fehlt → report.")
        return

    # Phi bestimmen
    phi = None
    if args.proxy == "N":
        N = _pick(data, ["N","N_seg","segment_density","segN"])
        if N is None:
            out_md.write_text("# Segment Redshift\nFehlende N-Spalte (proxy=N).\n", encoding="utf-8")
            print("[SSZ][addon] N fehlt → report.")
            return
        r_s, N_s = _slice_between_radii(r, [N], args.r_em, args.r_out)
        phi = phi_from_N(r_s, N_s)

    elif args.proxy == "rho-pr":
        rho = _pick(data, ["rho_kg_m3","rho","rho_si"])
        pr  = _pick(data, ["pr_pa","p_r","p_r_pa","pr"])
        if rho is None or pr is None:
            out_md.write_text("# Segment Redshift\nFehlende rho/pr-Spalte (proxy=rho-pr).\n", encoding="utf-8")
            print("[SSZ][addon] rho/pr fehlt → report.")
            return
        r_s, rho_s, pr_s = _slice_between_radii(r, [rho, pr], args.r_em, args.r_out)
        phi = phi_from_rho_pr(r_s, rho_s, pr_s)

    else:  # gtt
        gtt = _pick(data, ["g_tt","gtt","gtt_neg"])
        if gtt is None:
            out_md.write_text("# Segment Redshift\nFehlende g_tt-Spalte (proxy=gtt).\n", encoding="utf-8")
            print("[SSZ][addon] g_tt fehlt → report.")
            return
        import numpy as np
        r_arr = np.asarray(r, float)
        gtt_arr = np.asarray(gtt, float)
        i_em  = int(np.argmin(np.abs(r_arr - args.r_em)))
        i_out = int(np.argmin(np.abs(r_arr - args.r_out)))
        phi = phi_from_gtt(gtt_arr[i_em], gtt_arr[i_out])

    # Ergebnisse
    chi = chi_from_phi(phi)
    nu_inf = predict_nu_infinity(args.nu_em, phi)
    band = _band_from_freq(nu_inf)

    # CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["r_em(rs)","r_out(rs)","proxy","Phi_seg","chi_em","nu_em_Hz","nu_inf_Hz","band","source"])
        w.writerow([args.r_em, args.r_out, args.proxy, f"{phi:.6f}", f"{chi:.6e}",
                    f"{args.nu_em:.6e}", f"{nu_inf:.6e}", band, src.as_posix()])

    # Markdown
    out_md.write_text(
        "# Segment Redshift (Add-on)\n"
        f"- Source: `{src.as_posix()}` (proxy={args.proxy})\n"
        f"- Integration: r_em={args.r_em:g} r_s → r_out={args.r_out:g} r_s\n"
        f"- Φ_seg = **{phi:.6f}** → χ_em = e^-Φ = **{chi:.3e}**\n"
        f"- ν_em = **{args.nu_em:.3e} Hz** → ν_∞ = **{nu_inf:.3e} Hz**  (**{band}**)\n",
        encoding="utf-8"
    )

    # Optionaler Plot
    if args.seg_plot:
        import matplotlib.pyplot as plt
        out_plot.parent.mkdir(parents=True, exist_ok=True)
        fig = plt.figure(figsize=(6.2, 3.4))
        ax1 = fig.add_subplot(111)
        ax1.axhline(phi, linestyle="--")
        ax1.set_ylabel("Φ_seg (r_em→r_out)")
        ax1.set_xlabel("integration path")
        ax1.set_title("Segment Redshift Summary")
        ax2 = ax1.twinx()
        ax2.scatter([0],[nu_inf])
        ax2.set_yscale("log")
        ax2.set_ylabel("ν∞ [Hz] (log)")
        fig.tight_layout()
        fig.savefig(out_plot, dpi=600, bbox_inches="tight")
        plt.close(fig)

    print("[SSZ][addon] segment-redshift: OK → reports/segment_redshift.csv | .md")
    if args.seg_plot:
        print("[SSZ][addon] plot →", out_plot.as_posix())

if __name__ == "__main__":
    main()
