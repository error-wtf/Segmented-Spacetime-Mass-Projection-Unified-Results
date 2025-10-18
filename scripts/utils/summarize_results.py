from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _files_table(root: Path, max_rows: int = 200) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rows.append(
                {
                    "path": str(path.relative_to(root)),
                    "size": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
        except Exception:
            continue
        if len(rows) >= max_rows:
            break
    return rows


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

+
+def _read_junit(path: Path) -> dict[str, Any] | None:
+    try:
+        tree = ET.parse(path)
+        root = tree.getroot()
+        if root.tag == "testsuite":
+            suites = [root]
+        else:
+            suites = root.findall("testsuite")
+        total = sum(int(s.attrib.get("tests", 0)) for s in suites)
+        errors = sum(int(s.attrib.get("errors", 0)) for s in suites)
+        failures = sum(int(s.attrib.get("failures", 0)) for s in suites)
+        skipped = sum(int(s.attrib.get("skipped", 0)) for s in suites)
+        duration = sum(float(s.attrib.get("time", 0.0) or 0.0) for s in suites)
+        return {
+            "tests": total,
+            "errors": errors,
+            "failures": failures,
+            "skipped": skipped,
+            "time": duration,
+        }
+    except Exception:
+        return None
+
+
+def generate_summary_md(
+    *,
+    run_id: str,
+    repo_root: Path,
+    reports_dir: Path,
+    testergebnisse_dir: Path,
+    experiments_dir: Path,
+    agent_out_dir: Path,
+    suite_manifest_path: Path | None = None,
+    pytest_xml_path: Path | None = None,
+    repo_pytest_xml_path: Path | None = None,
+    extra_artifact_roots: list[Path] | None = None,
+) -> str:
+    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
+    lines: list[str] = []
+    lines.append(f"# SSZ Suite Summary — {run_id}")
+    lines.append("")
+    lines.append(f"_Generated: {timestamp}_")
+    lines.append("")
+
+    if suite_manifest_path and suite_manifest_path.exists():
+        manifest = _read_json(suite_manifest_path) or {}
+        steps = manifest.get("steps", [])
+        ok = sum(1 for step in steps if step.get("ok"))
+        fail = sum(1 for step in steps if not step.get("ok"))
+        total_runtime = manifest.get("duration_s")
+        lines.extend(
+            [
+                "## Suite Status",
+                f"- OK: **{ok}**",
+                f"- Fail: **{fail}**",
+                (
+                    f"- Total runtime: **{total_runtime:.2f}s**"
+                    if isinstance(total_runtime, (int, float))
+                    else "- Total runtime: _n/a_"
+                ),
+                "",
+            ]
+        )
+
+    if pytest_xml_path and pytest_xml_path.exists():
+        junit = _read_junit(pytest_xml_path) or {}
+        lines.extend(
+            [
+                "## scripts/tests (pytest)",
+                (
+                    "- Tests: **{tests}** | Failures: **{failures}** | Errors: **{errors}** | "
+                    "Skipped: **{skipped}** | Time: **{time}s**"
+                ).format(**{k: junit.get(k, "?") for k in ["tests", "failures", "errors", "skipped", "time"]}),
+                "",
+            ]
+        )
+
+    if repo_pytest_xml_path and repo_pytest_xml_path.exists():
+        junit = _read_junit(repo_pytest_xml_path) or {}
+        lines.extend(
+            [
+                "## Repo-wide pytest",
+                (
+                    "- Tests: **{tests}** | Failures: **{failures}** | Errors: **{errors}** | "
+                    "Skipped: **{skipped}** | Time: **{time}s**"
+                ).format(**{k: junit.get(k, "?") for k in ["tests", "failures", "errors", "skipped", "time"]}),
+                "",
+            ]
+        )
+
+    known_jsons = [
+        agent_out_dir / "reports" / "redshift_medians.json",
+        agent_out_dir / "reports" / "redshift_paired_stats.json",
+        repo_root / "full_pipeline" / "reports" / "summary_full_terminal_v4.json",
+    ]
+    lines.append("## Key JSON summaries")
+    found_json = False
+    for path in known_jsons:
+        if not path.exists():
+            continue
+        found_json = True
+        doc = _read_json(path) or {}
+        subset = {key: doc[key] for key in list(doc.keys())[:10]}
+        lines.append(f"- **{path.relative_to(repo_root)}**:")
+        lines.append("  ```json")
+        lines.append("  " + json.dumps(subset, indent=2)[:2000].replace("\n", "\n  "))
+        lines.append("  ```")
+    if not found_json:
+        lines.append("- _No known JSON summaries found._")
+    lines.append("")
+
+    artifact_roots = [reports_dir, experiments_dir, agent_out_dir]
+    if extra_artifact_roots:
+        artifact_roots.extend(extra_artifact_roots)
+    lines.append("## Artifacts & Files (first 200 per root)")
+    for root in artifact_roots:
+        if not root.exists():
+            continue
+        files = _files_table(root)
+        lines.append(f"### {root.relative_to(repo_root)}")
+        if not files:
+            lines.append("_No files_")
+            lines.append("")
+            continue
+        lines.append("| file | size (bytes) | sha256 |")
+        lines.append("|---|---:|---|")
+        for entry in files:
+            lines.append(
+                f"| `{entry['path']}` | {entry['size']} | `{entry['sha256']}` |"
+            )
+        lines.append("")
+
+    markdown = "\n".join(lines)
+    testergebnisse_dir.mkdir(parents=True, exist_ok=True)
+    (testergebnisse_dir / "SUMMARY.md").write_text(markdown, encoding="utf-8")
+    return markdown
+
+
+def write_and_print_summary(**kwargs: Any) -> None:
+    markdown = generate_summary_md(**kwargs)
+    print("\n================ SUMMARY (BEGIN) ================\n")
+    print(markdown)
+    print("\n================ SUMMARY (END) ==================\n")
