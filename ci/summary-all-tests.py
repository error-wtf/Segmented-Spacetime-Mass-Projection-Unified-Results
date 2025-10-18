#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# summary-all-tests.py
# Aggregiert Testergebnisse & Reports (ohne Plots) in output-summary.md.
# © 2025 — MIT License

from __future__ import annotations
import sys, io, os, json, csv, math
from pathlib import Path
from datetime import datetime
import argparse
import xml.etree.ElementTree as ET

# --- RING TEMP -> VELOCITY (Section 4.6) ------------------------------------
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# --- UTF-8 erzwingen (Windows-safe) ---
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def human_int(n: int | float | None) -> str:
    if n is None:
        return "–"
    return f"{int(n):,}".replace(",", "_")


def read_text(p: Path, max_chars=8000) -> str | None:
    if not p or not p.exists():
        return None
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
        if len(txt) > max_chars:
            return txt[:max_chars] + "\n[… gekürzt …]\n"
        return txt
    except Exception as e:
        return f"[Fehler beim Lesen: {e}]"

def try_json(p: Path):
    if not p or not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None

def try_csv_head_counts(p: Path, max_rows=10):
    """
    CSV vorsichtig lesen: nur Header + bis zu max_rows Zeilen mitzählen,
    zusätzlich Gesamtzeilenzahl effizient (streamend) ermitteln.
    """
    if not p or not p.exists():
        return None
    total = 0
    head_rows = []
    header = None
    try:
        with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    header = row
                else:
                    if len(head_rows) < max_rows:
                        head_rows.append(row)
                total += 1
        # total enthält inkl. Header
        data_rows = max(0, total - 1)
        return {"header": header, "rows_preview": head_rows, "rows_total": data_rows}
    except Exception as e:
        return {"error": str(e)}

def parse_junit_xml(p: Path):
    """
    Grobe PyTest/JUnit-Stats: tests, failures, errors, skipped, time
    """
    if not p or not p.exists():
        return None
    try:
        tree = ET.parse(p)
        root = tree.getroot()
        # PyTest schreibt oft <testsuite> als root oder <testsuites><testsuite>…
        suites = []
        if root.tag == "testsuite":
            suites = [root]
        elif root.tag == "testsuites":
            suites = list(root)
        total = {"tests":0,"failures":0,"errors":0,"skipped":0,"time":0.0}
        for s in suites:
            total["tests"] += int(s.attrib.get("tests", 0))
            total["failures"] += int(s.attrib.get("failures", 0))
            total["errors"] += int(s.attrib.get("errors", 0))
            total["skipped"] += int(s.attrib.get("skipped", 0))
            try:
                total["time"] += float(s.attrib.get("time", 0.0))
            except Exception:
                pass
        return total
    except Exception as e:
        return {"error": str(e)}

def find_latest_run_id(reports_dir: Path) -> str | None:
    """
    Nimmt den 'jüngsten' Unterordner in reports/* als Run-ID.
    """
    if not reports_dir.exists():
        return None
    cand = sorted([p for p in reports_dir.iterdir() if p.is_dir()],
                  key=lambda p: p.stat().st_mtime,
                  reverse=True)
    if cand:
        return cand[0].name
    return None

def load_suite_manifest(root: Path):
    mf = root / "ci" / "suite_manifest.json"
    return try_json(mf)

def summarize_suite(manifest: dict | None) -> str:
    if not manifest:
        return "_Keine suite_manifest.json gefunden._\n"
    lines = []
    rid = manifest.get("run_id") or "?"
    started = manifest.get("started_at") or "?"
    finished = manifest.get("finished_at") or "?"
    overall = manifest.get("overall_status") or "?"
    lines.append(f"- **run_id**: `{rid}`")
    lines.append(f"- **Start** : `{started}`")
    lines.append(f"- **Ende**  : `{finished}`")
    lines.append(f"- **Status**: **{overall}**")
    rep = manifest.get("report_path")
    if rep:
        lines.append(f"- **Report**: `{rep}`")
    # Steps
    steps = manifest.get("steps") or []
    if steps:
        lines.append("\n**Schritte:**")
        for s in steps:
            name = s.get("name","?")
            status = s.get("status","?")
            dur = s.get("duration_sec")
            lines.append(f"  - `{name}` → **{status}**" + (f" ({dur:.2f}s)" if isinstance(dur,(int,float)) else ""))
    return "\n".join(lines) + "\n"

def md_table(headers, rows):
    head = "| " + " | ".join(headers) + " |\n"
    sep  = "| " + " | ".join(["---"]*len(headers)) + " |\n"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return head + sep + (body + "\n" if body else "")

def summarize_mass_validation_csv(p: Path) -> str:
    info = try_csv_head_counts(p, max_rows=8)
    if not info:
        return "_mass_validation.csv nicht gefunden._\n"
    if "error" in info:
        return f"_Fehler beim Lesen von mass_validation.csv: {info['error']}_\n"
    header = info["header"] or []
    rows = info["rows_preview"] or []
    lines = [f"- Datei: `{p}`",
             f"- Zeilen gesamt (ohne Header): **{human_int(info['rows_total'])}**",
             "",
             "_Vorschau (erste Zeilen):_",
             md_table(header, rows)]
    return "\n".join(lines)

def summarize_redshift_json(medians_path: Path, paired_path: Path) -> str:
    med = try_json(medians_path)
    pair = try_json(paired_path)
    lines = []
    if med:
        # Beispiel-Schlüssel: {'seg_median_abs_residual': ..., 'gr_median_abs_residual': ..., ...}
        seg = med.get("seg_median_abs_residual")
        gr  = med.get("gr_median_abs_residual")
        sr  = med.get("sr_median_abs_residual")
        grsr= med.get("grsr_median_abs_residual")
        lines.append(f"- **Medians |Δz|**: Seg={seg}, GR={gr}, SR={sr}, GR×SR={grsr}")
    if pair:
        better = pair.get("seg_better_count")
        total  = pair.get("total_pairs")
        pval   = pair.get("sign_test_p_two_sided") or pair.get("p_two_sided")
        lines.append(f"- **Paired**: Seg besser in **{better}/{total}** Paaren (p≈{pval})")
    if not lines:
        return "_redshift_* JSONs nicht gefunden._\n"
    return "\n".join(lines) + "\n"

def summarize_enhanced_debug(p: Path) -> str:
    info = try_csv_head_counts(p, max_rows=5)
    if not info:
        return "_out/_enhanced_debug.csv nicht gefunden._\n"
    if "error" in info:
        return f"_Fehler beim Lesen von _enhanced_debug.csv: {info['error']}_\n"
    return "\n".join([
        f"- Datei: `{p}`",
        f"- Zeilen (ohne Header): **{human_int(info['rows_total'])}**",
        "_Vorschau:_",
        md_table(info["header"], info["rows_preview"])
    ])

def summarize_explain_debug(p: Path) -> str:
    info = try_csv_head_counts(p, max_rows=10)
    if not info:
        return "_out/_explain_debug.csv nicht gefunden._\n"
    if "error" in info:
        return f"_Fehler beim Lesen von _explain_debug.csv: {info['error']}_\n"
    return "\n".join([
        f"- Datei: `{p}`",
        f"- Zeilen (ohne Header): **{human_int(info['rows_total'])}**",
        "_Vorschau:_",
        md_table(info["header"], info["rows_preview"])
    ])

# --- RING TEMP -> VELOCITY FUNCTIONS -----------------------------------------

def compute_ring_velocity_from_temperature(csv_path: str, v0_kms: float = 10.0):
    """
    Implementiert die Logik aus ring_temperature_to_velocity.py direkt hier,
    damit wir keinen Subprozess parsen müssen. Erwartet Spalten:
    ring, T_proxy_K[, v_obs_kms]
    """
    if not HAS_PANDAS:
        raise ImportError("pandas required for ring temperature analysis")
    
    df = pd.read_csv(csv_path).sort_values("ring").reset_index(drop=True)
    if "ring" not in df.columns or "T_proxy_K" not in df.columns:
        raise ValueError(f"{csv_path} fehlt 'ring' oder 'T_proxy_K'")

    # q_k = T_k / T_{k-1}
    q = [np.nan]
    for i in range(1, len(df)):
        q.append(df.loc[i, "T_proxy_K"] / df.loc[i-1, "T_proxy_K"])
    df["q_k"] = q

    # v_k = v_{k-1} * q_k^{-1/2}
    v_pred = [float(v0_kms)]
    for i in range(1, len(df)):
        v_pred.append(v_pred[-1] * (df.loc[i, "q_k"]) ** (-0.5))
    df["v_pred_kms"] = v_pred

    # Residuen (falls Observed vorhanden)
    mae = None
    if "v_obs_kms" in df.columns:
        df["residual_kms"] = df["v_obs_kms"] - df["v_pred_kms"]
        if df["v_obs_kms"].notna().any():
            mae = df["residual_kms"].abs().mean()

    delta_v = df["v_pred_kms"].iloc[-1] - df["v_pred_kms"].iloc[0]
    ratio = df["v_pred_kms"].iloc[-1] / df["v_pred_kms"].iloc[0]

    return df, float(delta_v), float(ratio), (None if mae is None else float(mae))


def render_ring_section_markdown(df, delta_v: float, ratio: float, mae: float | None):
    # Kompakte Markdown-Tabelle (nur Kernspalten)
    cols = ["ring", "T_proxy_K", "q_k", "v_pred_kms"]
    if "v_obs_kms" in df.columns:
        cols += ["v_obs_kms", "residual_kms"]
    df_show = df[cols].copy()

    # Schönere Formatierung
    def fmt(x):
        if isinstance(x, (int, np.integer)) if HAS_PANDAS else isinstance(x, int):
            return str(x)
        try:
            return f"{float(x):,.6g}".replace(",", " ")
        except Exception:
            return str(x)

    md_table_str = "| " + " | ".join(cols) + " |\n"
    md_table_str += "| " + " | ".join("---" for _ in cols) + " |\n"
    for _, row in df_show.iterrows():
        md_table_str += "| " + " | ".join(fmt(row[c]) for c in cols) + " |\n"

    lines = []
    lines.append("## Ring-Temperatur → Geschwindigkeitsprofil (Section 4.6)")
    lines.append("")
    lines.append("_Eingang_: pro Ring Temperatur-Proxy `T_proxy_K`, Vorwärtsmodell `v_k = v_{k-1} · q_k^{-1/2}` mit `q_k = T_k/T_{k-1}`.")
    lines.append("")
    lines.append(md_table_str)
    lines.append("")
    lines.append(f"**Δv_gesamt** = {delta_v:.3f} km/s &nbsp;&nbsp;•&nbsp;&nbsp; **Faktor** = {ratio:.3f}×")
    if mae is not None:
        lines.append(f"**MAE** (wo beobachtet) = {mae:.3f} km/s")
    lines.append("")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description="Erzeuge Markdown-Zusammenfassung aller Tests/Reports (ohne Plots).")
    ap.add_argument("--root", type=str, default=".", help="Repo-Root (Standard: aktuelles Verzeichnis)")
    ap.add_argument("--run-id", type=str, default=None, help="Run-ID (z.B. 2025-10-17_gaia_ssz_real). Wenn leer, wird die jüngste in reports/ genommen.")
    ap.add_argument("--out", type=str, default="output-summary.md", help="Ausgabe-Markdown")
    ap.add_argument("--rings-csv", default=None, help="CSV für Ring-Temperatur-zu-v (Spalten: ring,T_proxy_K[,v_obs_kms])")
    ap.add_argument("--rings-v0", type=float, default=10.0, help="Baseline v0 am Ring 0 [km/s] (Default: 10.0)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    reports_dir = root / "reports"
    testergebnisse_dir = root / "testergebnisse"

    run_id = args.run_id or find_latest_run_id(reports_dir) or "unknown_run"
    out_md = Path(args.out).resolve()

    # Artefakt-Pfade
    suite_manifest = load_suite_manifest(root)

    junit_repo = (testergebnisse_dir / run_id / "repo_pytest_full.xml")
    junit_scripts = (reports_dir / run_id / "pytest_results.xml")

    agent_reports = root / "agent_out" / "reports"
    mass_csv = agent_reports / "mass_validation.csv"
    redshift_medians = agent_reports / "redshift_medians.json"
    redshift_paired = agent_reports / "redshift_paired_stats.json"
    bound_energy = agent_reports / "bound_energy.txt"

    out_dir = root / "out"
    enhanced_debug = out_dir / "_enhanced_debug.csv"
    explain_debug  = out_dir / "_explain_debug.csv"

    # === (0) RING: Temperatur -> Geschwindigkeit (vor den Summary-Schritten) ===
    ring_section = None
    if args.rings_csv:
        try:
            ring_csv_path = Path(args.rings_csv)
            if not ring_csv_path.is_absolute():
                ring_csv_path = root / ring_csv_path
            
            if ring_csv_path.exists():
                ring_df, ring_delta_v, ring_ratio, ring_mae = compute_ring_velocity_from_temperature(
                    str(ring_csv_path), args.rings_v0
                )
                ring_section = render_ring_section_markdown(ring_df, ring_delta_v, ring_ratio, ring_mae)

                # Optional artifacts: CSV & JSON für Visualisierung/Weiterverarbeitung
                artifacts_dir = out_md.parent / "ring_temp2v"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                ring_df.to_csv(artifacts_dir / "ring_results.csv", index=False)
                
                # JSON summary
                ring_summary = {
                    "delta_v_kms": ring_delta_v,
                    "velocity_ratio": ring_ratio,
                    "mae_kms": ring_mae,
                    "v0_kms": args.rings_v0,
                    "num_rings": len(ring_df)
                }
                with open(artifacts_dir / "ring_summary.json", "w", encoding="utf-8") as f:
                    json.dump(ring_summary, f, indent=2)
                
                print(f"[OK] Ring temperature analysis complete: Δv={ring_delta_v:.3f} km/s, ratio={ring_ratio:.3f}×")
            else:
                ring_section = f"## Ring-Temperatur → Geschwindigkeit\n\n_CSV nicht gefunden_: `{ring_csv_path}`\n"
                print(f"[WARN] Ring CSV not found: {ring_csv_path}", file=sys.stderr)
        except ImportError as e:
            ring_section = f"## Ring-Temperatur → Geschwindigkeit\n\n_Fehlgeschlagen_: pandas/numpy required\n"
            print(f"[WARN] Ring analysis skipped: {e}", file=sys.stderr)
        except Exception as e:
            ring_section = f"## Ring-Temperatur → Geschwindigkeit\n\n_Fehlgeschlagen_: `{e}`\n"
            print(f"[ERROR] Ring analysis failed: {e}", file=sys.stderr)

    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Header
    lines.append(f"# Test- & Pipeline-Zusammenfassung")
    lines.append("")
    lines.append(f"- Generiert: `{now}`")
    lines.append(f"- Repo: `{root}`")
    lines.append(f"- Run-ID: `{run_id}`")
    lines.append("")

    # Suite Manifest
    lines.append("## Suite / Schritte")
    lines.append(summarize_suite(suite_manifest))
    lines.append("")

    # PyTest: repo_full
    lines.append("## PyTest – Repository gesamt")
    repo_stats = parse_junit_xml(junit_repo)
    if repo_stats and "error" not in repo_stats:
        lines.append(md_table(
            ["tests","failures","errors","skipped","time[s]"],
            [[repo_stats.get("tests",0), repo_stats.get("failures",0), repo_stats.get("errors",0),
              repo_stats.get("skipped",0), f"{repo_stats.get('time',0.0):.2f}"]]
        ))
        lines.append(f"_Quelle_: `{junit_repo}`\n")
    else:
        lines.append("_JUnit-Ergebnis (repo) nicht gefunden._\n")

    # PyTest: scripts/tests
    lines.append("## PyTest – scripts/tests")
    scr_stats = parse_junit_xml(junit_scripts)
    if scr_stats and "error" not in scr_stats:
        lines.append(md_table(
            ["tests","failures","errors","skipped","time[s]"],
            [[scr_stats.get("tests",0), scr_stats.get("failures",0), scr_stats.get("errors",0),
              scr_stats.get("skipped",0), f"{scr_stats.get('time',0.0):.2f}"]]
        ))
        lines.append(f"_Quelle_: `{junit_scripts}`\n")
    else:
        lines.append("_JUnit-Ergebnis (scripts) nicht gefunden._\n")

    # GAIA/SSZ Reports
    lines.append("## SSZ / GAIA Reports")
    if bound_energy.exists():
        be_txt = read_text(bound_energy, max_chars=2000) or ""
        # erste Zeile extrahieren
        first_line = be_txt.splitlines()[0] if be_txt else ""
        lines.append(f"- **Bound Energy**: `{first_line}`  \n_Quelle_: `{bound_energy}`\n")
    else:
        lines.append("- Bound Energy: _nicht gefunden_\n")

    # redshift JSONs
    lines.append("### Redshift-Auswertung")
    lines.append(summarize_redshift_json(redshift_medians, redshift_paired))

    # mass_validation CSV
    lines.append("### Mass Validation")
    lines.append(summarize_mass_validation_csv(mass_csv))
    lines.append("")

    # Enhanced Debug
    lines.append("## Enhanced Debug (Kennzahlen)")
    lines.append(summarize_enhanced_debug(enhanced_debug))
    lines.append("")

    # Explain Debug
    lines.append("## Explain Debug (Vorschau)")
    lines.append(summarize_explain_debug(explain_debug))
    lines.append("")

    # Encoding-/Terminal-Warnung (Dokumentation)
    lines.append("> Hinweis: Falls frühere Läufe an Windows-Encoding scheiterten (`'charmap' codec`),")
    lines.append("> wurden in den Tools UTF-8-Settings berücksichtigt. Für manuelle Runs:")
    lines.append("> `python -X utf8 ci/autorun_suite.py`.\n")

    # Build final markdown: prepend ring section if available
    summary_md = "\n".join(lines)
    if ring_section:
        summary_md = ring_section + "\n\n" + summary_md

    out_md.write_text(summary_md, encoding="utf-8", errors="replace")
    print(f"[OK] Markdown geschrieben: {out_md}")

if __name__ == "__main__":
    main()
