#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summary_visualize.py
Erzeugt aus output-summary.md einen HTML-Report und zieht Kennzahlen/Plots aus CSV/JSON/XML.
Kompatibel mit Windows (UTF-8), ohne externe Logins/APIs.

Beispiel:
  python summary_visualize.py --run-dir . --md output-summary.md --html output-summary.html --plots
"""

from __future__ import annotations
import argparse, sys, os, io, json, csv, base64, textwrap, hashlib
import math
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# ---- Utils ------------------------------------------------------------------

def read_text(fp: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return fp.read_text(encoding=enc, errors="replace")
        except Exception:
            continue
    # letzte Chance
    with open(fp, "rb") as f:
        return f.read().decode("utf-8", errors="replace")

def write_text(fp: Path, text: str) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(text, encoding="utf-8", errors="replace")

def find_one(globs: List[str], base: Path) -> Optional[Path]:
    for g in globs:
        for p in base.glob(g):
            if p.is_file():
                return p
    return None

def find_all(globs: List[str], base: Path) -> List[Path]:
    out = []
    for g in globs:
        out.extend([p for p in base.glob(g) if p.is_file()])
    return out

def parse_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None

def sha256_file(fp: Path) -> str:
    h=hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# ---- Markdown → HTML (mit Fallback) -----------------------------------------

def md_to_html(md: str) -> str:
    try:
        import markdown  # type: ignore
        return markdown.markdown(md, extensions=["tables", "fenced_code", "toc"])
    except Exception:
        # Minimal-Fallback
        safe = (
            md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        # Überschriften simpel umsetzen
        lines = []
        for line in safe.splitlines():
            if line.startswith("#"):
                n = len(line) - len(line.lstrip("#"))
                content = line.lstrip("#").strip()
                lines.append(f"<h{n}>{content}</h{n}>")
            elif line.startswith("|") and line.rstrip().endswith("|"):
                # sehr simpler Tabellen-Fallback
                row = [c.strip() for c in line.strip("|").split("|")]
                if not lines or not lines[-1].startswith("<table"):
                    lines.append("<table><tr>" + "".join(f"<th>{c}</th>" for c in row) + "</tr>")
                else:
                    lines.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
            else:
                if lines and lines[-1].startswith("<table"):
                    lines.append("</table>")
                if line.strip():
                    lines.append(f"<p>{line}</p>")
                else:
                    lines.append("<br/>")
        if lines and lines[-1].startswith("<table"):
            lines.append("</table>")
        return "\n".join(lines)

# ---- Daten-Lader ------------------------------------------------------------

def load_csv_preview(fp: Path, limit=5) -> Tuple[List[str], List[List[str]], int]:
    rows = []
    total = 0
    header = []
    with open(fp, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                total += 1
                if len(rows) < limit:
                    rows.append(row)
    return header, rows, total

def load_json(fp: Path) -> Any:
    try:
        return json.loads(read_text(fp))
    except Exception:
        return None

def load_pytest_xml_counts(fp: Path) -> Optional[Dict[str, Any]]:
    # sehr schlanke Parser-Variante (kein xml-Modul nötig für simple counts)
    text = read_text(fp)
    # Suche Attribute tests, failures, errors, skipped, time
    import re
    m = re.search(r'tests="(\d+)"[^>]*failures="(\d+)"[^>]*errors="(\d+)"[^>]*skipped="(\d+)"[^>]*time="([\d\.]+)"', text)
    if not m:
        # JUnit-Varianten
        m = re.search(r'failures="(\d+)"[^>]*errors="(\d+)"[^>]*tests="(\d+)"[^>]*time="([\d\.]+)"', text)
        if m:
            tests = int(m.group(3)); failures=int(m.group(1)); errors=int(m.group(2)); time=float(m.group(4)); skipped=0
            return dict(tests=tests, failures=failures, errors=errors, skipped=skipped, time=time)
        return None
    tests = int(m.group(1)); failures=int(m.group(2)); errors=int(m.group(3)); skipped=int(m.group(4)); time=float(m.group(5))
    return dict(tests=tests, failures=failures, errors=errors, skipped=skipped, time=time)

# ---- Plots ------------------------------------------------------------------

def ensure_assets_dir(base: Path) -> Path:
    d = base / "_summary_assets"
    d.mkdir(parents=True, exist_ok=True)
    return d

def plot_hist(values: List[float], title: str, outpath: Path) -> Optional[Path]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.hist([v for v in values if v is not None and not math.isnan(v)], bins=30)
        plt.title(title)
        plt.xlabel("Wert")
        plt.ylabel("Häufigkeit")
        fig.savefig(outpath, bbox_inches="tight", dpi=150)
        plt.close(fig)
        return outpath
    except Exception as e:
        print(f"[WARN] plot_hist failed: {e}", file=sys.stderr)
        return None

def plot_scatter(x: List[float], y: List[float], title: str, outpath: Path, xlabel="x", ylabel="y") -> Optional[Path]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.scatter(x, y, s=12)
        plt.title(title)
        plt.xlabel(xlabel); plt.ylabel(ylabel)
        fig.savefig(outpath, bbox_inches="tight", dpi=150)
        plt.close(fig)
        return outpath
    except Exception as e:
        print(f"[WARN] plot_scatter failed: {e}", file=sys.stderr)
        return None

def img_tag(fp: Path) -> str:
    try:
        data = fp.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        mime = "image/png"
        return f'<img alt="{fp.name}" src="data:{mime};base64,{b64}" style="max-width:100%;height:auto;border:1px solid #ddd;border-radius:8px;padding:4px;margin:6px 0;" />'
    except Exception:
        return ""

# ---- Kennzahlen aus Dateien -------------------------------------------------

def summarize_mass_validation(fp: Path) -> Dict[str, Any]:
    header, rows, total = load_csv_preview(fp, limit=9999)
    rel_err_idx = None
    obj_idx = None
    if header:
        if "rel_err" in header:
            rel_err_idx = header.index("rel_err")
        if "object" in header:
            obj_idx = header.index("object")
    rels = []
    for r in rows:
        if rel_err_idx is not None and rel_err_idx < len(r):
            v = parse_float(r[rel_err_idx])
            if v is not None:
                rels.append(v)
    return dict(
        total=total,
        rel_err_min=min(rels) if rels else None,
        rel_err_max=max(rels) if rels else None,
        rel_err_mean=(sum(rels)/len(rels) if rels else None),
        preview_rows=rows[:5],
        header=header,
    )

def summarize_enhanced_debug(fp: Path) -> Dict[str, Any]:
    # Wir wollen |dz_seg|, |dz_gr|, |dz_sr|, |dz_grsr|
    header, rows, total = load_csv_preview(fp, limit=2000)
    idx = {name:i for i,name in enumerate(header)}
    def col_abs(name):
        i = idx.get(name)
        vals = []
        if i is None: return vals
        for r in rows:
            if i < len(r):
                v = parse_float(r[i])
                if v is not None:
                    vals.append(abs(v))
        return vals
    dz_seg = col_abs("dz_seg")
    dz_gr  = col_abs("dz_gr")
    dz_sr  = col_abs("dz_sr")
    dz_grsr = col_abs("dz_grsr")
    strong_col = idx.get("strong")
    strong_count = 0
    if strong_col is not None:
        for r in rows:
            if strong_col < len(r) and r[strong_col].strip().lower() == "true":
                strong_count += 1
    return dict(
        total=total,
        dz_seg=dz_seg, dz_gr=dz_gr, dz_sr=dz_sr, dz_grsr=dz_grsr,
        strong_count=strong_count,
        header=header
    )

def summarize_pytest(run_dir: Path) -> Dict[str, Any]:
    result = {}
    repo_xml = find_one([
        "testergebnisse/*/repo_pytest_full.xml",
        "testergebnisse/**/repo_pytest_full.xml"
    ], run_dir)
    scripts_xml = find_one([
        "reports/*/pytest_results.xml",
        "reports/**/pytest_results.xml"
    ], run_dir)
    if repo_xml:
        result["repo_pytest_full"] = load_pytest_xml_counts(repo_xml)
        result["repo_pytest_full_path"] = str(repo_xml)
    if scripts_xml:
        result["scripts_tests"] = load_pytest_xml_counts(scripts_xml)
        result["scripts_tests_path"] = str(scripts_xml)
    return result

# ---- Renderer ---------------------------------------------------------------

CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;line-height:1.45;padding:24px;color:#1b1f23;}
h1,h2,h3{line-height:1.2}
code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,Monaco,monospace}
.table{border-collapse:collapse;width:100%;margin:6px 0 16px 0}
.table th,.table td{border:1px solid #e1e4e8;padding:6px 8px;text-align:left}
.badge{display:inline-block;border-radius:8px;padding:2px 8px;border:1px solid #e1e4e8;background:#f6f8fa;margin-left:8px}
.kpi{display:inline-block;margin:2px 10px 2px 0;padding:4px 8px;border-radius:6px;background:#f6f8fa;border:1px solid #e1e4e8}
hr{border:none;border-top:1px solid #e1e4e8;margin:16px 0}
blockquote{border-left:4px solid #e1e4e8;padding:6px 12px;color:#444;background:#fbfbfb}
"""

def render_html(md_html: str, extra_sections: List[str]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [
        "<!doctype html><meta charset='utf-8'>",
        f"<title>Output Summary – {now}</title>",
        f"<style>{CSS}</style>",
        f"<div style='display:flex;justify-content:space-between;align-items:center'><h1>Output Summary</h1><span class='badge'>{now}</span></div>",
        md_html,
        *extra_sections
    ]
    return "\n".join(parts)

def fmt_kpi(label: str, value: Any, suffix: str = "") -> str:
    if value is None: val="—"
    elif isinstance(value, float): 
        val = f"{value:.6g}"
    else:
        val = str(value)
    return f"<span class='kpi'><strong>{label}:</strong> {val}{suffix}</span>"

# ---- Main -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Render output-summary and visualize metrics.")
    ap.add_argument("--run-dir", type=str, default=".", help="Repo-Root/Run-Root")
    ap.add_argument("--md", type=str, default="output-summary.md", help="Pfad zur Markdown-Datei")
    ap.add_argument("--html", type=str, default=None, help="Optionaler HTML-Output (z.B. output-summary.html)")
    ap.add_argument("--plots", action="store_true", help="Plots erzeugen und einbetten")
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    md_path = (run_dir / args.md).resolve() if not Path(args.md).is_absolute() else Path(args.md)
    if not md_path.exists():
        print(f"[ERROR] Markdown nicht gefunden: {md_path}", file=sys.stderr)
        sys.exit(2)

    md_text = read_text(md_path)
    md_html = md_to_html(md_text)

    # Datenquellen lokalisieren
    mass_csv = find_one([
        "agent_out/reports/mass_validation.csv",
        "experiments/*/mass_validation.csv",
        "out/segmented_spacetime_mass_validation.csv",
    ], run_dir)

    enh_csv = find_one([
        "out/_enhanced_debug.csv",
    ], run_dir)

    explain_csv = find_one([
        "out/_explain_debug.csv",
    ], run_dir)

    redshift_jsons = {
        "medians": find_one(["agent_out/reports/redshift_medians.json","experiments/*/redshift_medians.json"], run_dir),
        "paired":  find_one(["agent_out/reports/redshift_paired_stats.json","experiments/*/redshift_paired_stats.json"], run_dir),
    }

    bound_txt = find_one([
        "agent_out/reports/bound_energy.txt",
    ], run_dir)

    pytest_info = summarize_pytest(run_dir)

    extra_sections = []

    # PyTest-Box
    if pytest_info:
        box = ["<h2>PyTest-Überblick</h2>"]
        for k in ("repo_pytest_full","scripts_tests"):
            stats = pytest_info.get(k)
            path = pytest_info.get(k + "_path")
            if stats:
                box.append(
                    "<div>" +
                    fmt_kpi("tests", stats.get("tests")) +
                    fmt_kpi("failures", stats.get("failures")) +
                    fmt_kpi("errors", stats.get("errors")) +
                    fmt_kpi("skipped", stats.get("skipped")) +
                    fmt_kpi("time[s]", stats.get("time")) +
                    (f"<span class='badge'>Quelle: {path}</span>" if path else "") +
                    "</div>"
                )
        extra_sections.append("\n".join(box) + "<hr/>")

    # Bound energy
    if bound_txt and bound_txt.exists():
        val_line = read_text(bound_txt).strip().splitlines()[0] if bound_txt else ""
        extra_sections.append(f"<h2>Bound Energy</h2><blockquote>{val_line}</blockquote>"
                              f"<div class='badge'>Quelle: {bound_txt}</div><hr/>")

    # Mass validation
    if mass_csv and mass_csv.exists():
        msum = summarize_mass_validation(mass_csv)
        tab = ["<h2>Mass Validation</h2>",
               "<div>",
               fmt_kpi("Zeilen", msum["total"]),
               fmt_kpi("rel_err(min)", msum["rel_err_min"]),
               fmt_kpi("rel_err(mean)", msum["rel_err_mean"]),
               fmt_kpi("rel_err(max)", msum["rel_err_max"]),
               f"<span class='badge'>Quelle: {mass_csv}</span>",
               "</div>"]
        # Vorschau
        hdr = msum["header"]
        rows = msum["preview_rows"]
        if hdr and rows:
            tab.append("<table class='table'><thead><tr>" + "".join(f"<th>{h}</th>" for h in hdr) + "</tr></thead><tbody>")
            for r in rows[:8]:
                tab.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
            tab.append("</tbody></table>")
        extra_sections.append("\n".join(tab) + "<hr/>")

    # Enhanced debug & plots
    assets_dir = ensure_assets_dir(md_path.parent)
    if enh_csv and enh_csv.exists():
        esum = summarize_enhanced_debug(enh_csv)
        sec = ["<h2>Enhanced Debug (Kennzahlen)</h2>",
               "<div>",
               fmt_kpi("Zeilen", esum["total"]),
               fmt_kpi("Strong rows", esum["strong_count"]),
               f"<span class='badge'>Quelle: {enh_csv}</span>",
               "</div>"]

        if args.plots:
            # Histogramme für |Δz|
            def safe(vals): return [v for v in vals if v is not None and not math.isnan(v)]
            for name, arr in (("dz_seg", esum["dz_seg"]),
                              ("dz_gr", esum["dz_gr"]),
                              ("dz_sr", esum["dz_sr"]),
                              ("dz_grsr", esum["dz_grsr"])):
                if arr:
                    img = assets_dir / f"{name}_hist.png"
                    p = plot_hist(safe(arr), f"|Δz| – {name}", img)
                    if p: sec.append(img_tag(p))

            # Scatter Seg vs GR (falls beide vorhanden)
            if esum["dz_seg"] and esum["dz_gr"]:
                n = min(len(esum["dz_seg"]), len(esum["dz_gr"]))
                img = assets_dir / "dz_seg_vs_gr.png"
                p = plot_scatter(esum["dz_gr"][:n], esum["dz_seg"][:n],
                                 "|Δz|: Seg vs GR", img, xlabel="|Δz| GR", ylabel="|Δz| Seg")
                if p: sec.append(img_tag(p))

        extra_sections.append("\n".join(sec) + "<hr/>")

    # Explain debug (kleine Vorschau)
    if explain_csv and explain_csv.exists():
        hdr, rows, total = load_csv_preview(explain_csv, limit=10)
        sec = ["<h2>Explain Debug (Vorschau)</h2>",
               "<div>",
               fmt_kpi("Zeilen", total),
               f"<span class='badge'>Quelle: {explain_csv}</span>",
               "</div>"]
        if hdr and rows:
            sec.append("<table class='table'><thead><tr>" + "".join(f"<th>{h}</th>" for h in hdr) + "</tr></thead><tbody>")
            for r in rows[:10]:
                sec.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
            sec.append("</tbody></table>")
        extra_sections.append("\n".join(sec) + "<hr/>")

    # Redshift-JSONs
    if redshift_jsons["medians"] or redshift_jsons["paired"]:
        sec = ["<h2>Redshift Auswertung</h2>"]
        med = load_json(redshift_jsons["medians"]) if redshift_jsons["medians"] else None
        pai = load_json(redshift_jsons["paired"]) if redshift_jsons["paired"] else None
        if med:
            # Erwartete Struktur: keys wie "median_abs_dz_seg", etc.
            sec.append("<div>")
            for k, label in [
                ("median_abs_dz_seg", "Median |Δz| Seg"),
                ("median_abs_dz_gr", "Median |Δz| GR"),
                ("median_abs_dz_sr", "Median |Δz| SR"),
                ("median_abs_dz_grsr", "Median |Δz| GR×SR"),
            ]:
                v = med.get(k)
                sec.append(fmt_kpi(label, v))
            sec.append(f"<span class='badge'>Quelle: {redshift_jsons['medians']}</span></div>")
        if pai:
            # z.B. {"seg_better": 82, "total_pairs": 127, "pvalue": 0.00131}
            seg_better = pai.get("seg_better")
            total_pairs = pai.get("total_pairs")
            pvalue = pai.get("pvalue")
            sec.append("<div>")
            sec.append(fmt_kpi("Seg besser", seg_better))
            sec.append(fmt_kpi("Paare", total_pairs))
            sec.append(fmt_kpi("p-Wert", pvalue))
            sec.append(f"<span class='badge'>Quelle: {redshift_jsons['paired']}</span></div>")
        extra_sections.append("\n".join(sec) + "<hr/>")

    # Finale HTML
    html = render_html(md_html, extra_sections)

    if args.html:
        html_path = (run_dir / args.html) if not Path(args.html).is_absolute() else Path(args.html)
        write_text(html_path, html)
        print(f"[OK] HTML geschrieben: {html_path}")
        print(f"[OK] Assets (falls erzeugt): {assets_dir}")
    else:
        # stdout
        sys.stdout.write(html)

if __name__ == "__main__":
    main()
