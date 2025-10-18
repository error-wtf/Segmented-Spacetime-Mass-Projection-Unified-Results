from __future__ import annotations

import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np

from . import _theme

ROOT = Path(__file__).resolve().parents[1]
RUN_REPORT_DIR = ROOT / "reports"
PLOTS_SUBDIR = "suite_plots"
LOGGER = logging.getLogger("suite.viz")
AUTOFETCH_MANIFEST = "autofetch_manifest.json"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _encode_image(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _render_plot(fig, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="png", bbox_inches="tight")
    plt.close(fig)
    return _encode_image(path) or ""


def _plot_step_durations(step_results: List[Dict[str, Any]], path: Path) -> Tuple[Optional[str], Optional[str]]:
    if not step_results:
        return None, None
    labels = [step["name"] for step in step_results]
    durations = [step.get("dt_s", 0.0) for step in step_results]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.barh(labels, durations, color="#38bdf8")
    ax.set_xlabel("Duration [s]")
    ax.set_ylabel("Suite Step")
    ax.set_title("Step Durations")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    encoded = _render_plot(fig, path)
    return encoded, _relative_path(path)


def parse_pytest_xml(path: Path) -> Dict[str, Any]:
    stats = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0, "time_s": 0.0}
    if not path.exists():
        return stats
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return stats
    root = tree.getroot()
    for suite in root.findall(".//testsuite"):
        stats["total"] += int(suite.get("tests", 0))
        stats["failed"] += int(suite.get("failures", 0))
        stats["errors"] += int(suite.get("errors", 0))
        stats["skipped"] += int(suite.get("skipped", 0))
        stats["time_s"] += float(suite.get("time", 0.0))
    stats["passed"] = max(0, stats["total"] - stats["failed"] - stats["errors"] - stats["skipped"])
    return stats


def plot_tests_pie(stats: Dict[str, Any], path: Path) -> Tuple[Optional[str], Optional[str]]:
    labels = ["passed", "failed", "errors", "skipped"]
    values = [stats.get(label, 0) for label in labels]
    if sum(values) == 0:
        labels, values = ["no tests"], [1]
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(values, labels=labels, autopct="%1.0f%%")
    ax.set_title(
        f"Tests (total={stats.get('total', 0)}, time={stats.get('time_s', 0.0):.1f}s)"
    )
    encoded = _render_plot(fig, path)
    return encoded, _relative_path(path)


def _plot_test_status(summary: Dict[str, Any], path: Path) -> Tuple[Optional[str], Optional[str]]:
    if summary.get("error"):
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            summary["error"],
            ha="center",
            va="center",
            fontsize=12,
            wrap=True,
        )
        ax.set_title("Tests Skipped")
        encoded = _render_plot(fig, path)
        return encoded, _relative_path(path)

    total = summary.get("total", 0)
    if total == 0:
        labels = ["Skipped"]
        sizes = [1]
        colors = ["#fbbf24"]
    else:
        labels = ["Passed", "Failed", "Skipped"]
        sizes = [summary.get("passed", 0), summary.get("failed", 0), summary.get("skipped", 0)]
        colors = ["#22c55e", "#ef4444", "#fbbf24"]
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%")
    ax.set_title("Test Status")
    encoded = _render_plot(fig, path)
    return encoded, _relative_path(path)


def _plot_test_durations(summary: Dict[str, Any], path: Path) -> Tuple[Optional[str], Optional[str]]:
    cases = summary.get("cases", [])
    if not cases:
        return None, None
    durations = [case.get("duration", 0.0) for case in cases]
    if not any(durations):
        return None, None
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.hist(durations, bins=min(len(durations), 12), color="#38bdf8", alpha=0.7)
    ax.set_xlabel("Test Duration [s]")
    ax.set_ylabel("Count")
    ax.set_title("Per-test Durations")
    encoded = _render_plot(fig, path)
    return encoded, _relative_path(path)


def _artifact_link(path: Optional[str]) -> str:
    if not path:
        return "<span class='badge warn'>missing</span>"
    return f"<a href='../{path}'>{path}</a>"


def _relative_path(path: Path) -> Optional[str]:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _step_map(steps: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {step.get("name"): step for step in steps}


def build_report(run_id: str, step_history: Optional[Iterable[Dict[str, Any]]] = None) -> Dict[str, Any]:
    run_reports_dir = RUN_REPORT_DIR / run_id
    plots_dir = run_reports_dir / PLOTS_SUBDIR
    _ensure_dir(plots_dir)

    manifest_path = ROOT / "ci" / "suite_manifest.json"
    autofetch_manifest_path = ROOT / "experiments" / run_id / "autofetch_manifest.json"
    changed_files_path = ROOT / "ci" / "changed_files.json"
    summary_json_path = run_reports_dir / "pytest_summary.json"

    suite_manifest = _load_json(manifest_path)
    autofetch_manifest = _load_json(autofetch_manifest_path)
    changed_files = _load_json(changed_files_path)
    pytest_summary = _load_json(summary_json_path)

    provided_steps = list(step_history or [])
    steps = suite_manifest.get("steps", provided_steps) or provided_steps
    step_lookup = _step_map(steps)

    durations_plot, durations_path = _plot_step_durations(
        steps, plots_dir / "step_durations.png"
    )
    tests_plot, tests_plot_path = _plot_test_status(
        pytest_summary, plots_dir / "tests_status.png"
    )
    tests_hist, tests_hist_path = _plot_test_durations(
        pytest_summary, plots_dir / "tests_duration.png"
    )
    junit_xml = run_reports_dir / "pytest_results.xml"
    junit_stats = parse_pytest_xml(junit_xml)
    pie_plot, pie_plot_path = plot_tests_pie(junit_stats, plots_dir / "tests_pie.png")

    viz_dir = ROOT / "experiments" / run_id / "viz"
    gamma_img = _encode_image(viz_dir / "gamma_seg_xy.png")
    z_hist_img = _encode_image(viz_dir / "z_seg_hist.png")

    autofetch_artifacts = step_lookup.get("autofetch", {}).get("artifacts", {})
    if not autofetch_artifacts:
        autofetch_artifacts = autofetch_manifest.get("artifacts", {})

    template = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<title>Segmented Spacetime Suite — {run_id}</title>
<style>
{_theme.BASE_CSS}
</style>
</head>
<body>
<header>
  <h1>Segmented Spacetime Suite — {run_id}</h1>
  <p><span class='badge'>Started: {suite_manifest.get('started', 'n/a')}</span>
     <span class='badge'>Duration: {suite_manifest.get('duration_s', 'n/a')} s</span>
     <span class='badge'>Changed files: {changed_files.get('count', '0')}</span>
  </p>
</header>

<section class='grid'>
  <article class='card'>
    <h2>Changed Files</h2>
    <details>
      <summary>{changed_files.get('count', 0)} files in last 7 days</summary>
      <ul class='steplist'>
        {''.join(f"<li><code>{item['path']}</code></li>" for item in changed_files.get('files', [])[:200]) or '<li>None</li>'}
      </ul>
    </details>
  </article>

  <article class='card'>
    <h2>Data Availability</h2>
    <ul class='steplist'>
      <li>GAIA: {_artifact_link(autofetch_artifacts.get('gaia_parquet'))}</li>
      <li>SDSS: {_artifact_link(autofetch_artifacts.get('sdss_csv'))}</li>
      <li>Planck: {_artifact_link(autofetch_artifacts.get('planck_fits'))}</li>
    </ul>
  </article>

  <article class='card'>
    <h2>Suite Steps</h2>
    <ul class='steplist'>
      {''.join(_step_entry(step) for step in steps) or '<li>No steps recorded.</li>'}
    </ul>
    {f"<div class='img-wrap'><img src='{durations_plot}' alt='Step durations'></div>" if durations_plot else ''}
  </article>

  <article class='card'>
    <h2>Testübersicht</h2>
    {f"<div class='img-wrap'><img src='{pie_plot}' alt='Tests pie'></div>" if pie_plot else '<p class="badge warn">No test data</p>'}
    <div class='kv'>
      <div>passed:</div><div>{junit_stats['passed']}</div>
      <div>failed:</div><div>{junit_stats['failed']}</div>
      <div>errors:</div><div>{junit_stats['errors']}</div>
      <div>skipped:</div><div>{junit_stats['skipped']}</div>
      <div>total:</div><div>{junit_stats['total']}</div>
      <div>time:</div><div>{junit_stats['time_s']:.1f} s</div>
    </div>
  </article>

  <article class='card'>
    <h2>Tests</h2>
    <p>Total: {pytest_summary.get('total',0)} | Passed: {pytest_summary.get('passed',0)} | Failed: {pytest_summary.get('failed',0)} | Skipped: {pytest_summary.get('skipped',0)}</p>
    {f"<div class='img-wrap'><img src='{tests_plot}' alt='Test status'></div>" if tests_plot else ''}
    {f"<div class='img-wrap'><img src='{tests_hist}' alt='Test durations'></div>" if tests_hist else ''}
  </article>

  <article class='card'>
    <h2>SSZ Visualizations</h2>
    {"<p class='badge warn'>gamma_seg_xy.png missing</p>" if not gamma_img else f"<div class='img-wrap'><img src='{gamma_img}' alt='Gamma seg'></div>"}
    {"<p class='badge warn'>z_seg_hist.png missing</p>" if not z_hist_img else f"<div class='img-wrap'><img src='{z_hist_img}' alt='Z histogram'></div>"}
  </article>

  <article class='card'>
    <h2>Artifacts</h2>
    <ul class='steplist'>
      <li>Manifest: {_artifact_link('ci/suite_manifest.json')}</li>
      <li>Autofetch: {_artifact_link(f'experiments/{run_id}/{AUTOFETCH_MANIFEST}')}</li>
      <li>Test summary: {_artifact_link(f'reports/{run_id}/pytest_summary.json')}</li>
      <li>Suite plots: {_artifact_link(f'reports/{run_id}/{PLOTS_SUBDIR}')}</li>
    </ul>
  </article>
</section>

</body>
</html>
"""

    report_path = run_reports_dir / "suite_report.html"
    report_path.write_text(template, encoding="utf-8")

    return {
        "report_html": f"reports/{run_id}/suite_report.html",
        "plots": [
            p
            for p in [durations_path, tests_plot_path, tests_hist_path]
            if p is not None
        ],
        "warnings": [] if gamma_img and z_hist_img else [
            msg for msg, cond in (
                ("Missing gamma_seg_xy.png", not gamma_img),
                ("Missing z_seg_hist.png", not z_hist_img),
            ) if cond
        ],
    }


def _step_entry(step: Dict[str, Any]) -> str:
    ok = step.get("ok", False)
    badge = "ok" if ok else "fail"
    err = step.get("error")
    err_html = f"<br><code>{err}</code>" if err else ""
    artifacts = step.get("artifacts", {})
    artifact_list = "".join(
        f"<li><code>{key}</code>: {_artifact_link(val) if isinstance(val, str) else json.dumps(val)}</li>"
        for key, val in artifacts.items() if val
    )
    if artifact_list:
        artifact_html = f"<details><summary>Artifacts</summary><ul>{artifact_list}</ul></details>"
    else:
        artifact_html = ""
    return (
        f"<li><span class='badge {badge}'>{step.get('name')}</span> "
        f"{step.get('dt_s','0')} s{err_html}{artifact_html}</li>"
    )
