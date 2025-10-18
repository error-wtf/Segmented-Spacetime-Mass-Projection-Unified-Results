from __future__ import annotations

import argparse
import glob
import io
import json
import logging
import os
from logging.handlers import RotatingFileHandler
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

try:
    from scripts.utils.summarize_results import write_and_print_summary
except Exception:  # pragma: no cover - optional dependency safeguard
    write_and_print_summary = None

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("LANG", "C.UTF-8")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED_ROOT_SUFFIX = "_bak_2025-10-17_17-03-00"


def ensure_correct_repo_root():
    """Exit immediately if running from the wrong repository directory."""
    repo = ROOT
    if not repo.name.endswith(EXPECTED_ROOT_SUFFIX):
        msg = (
            f"\n{'='*70}\n"
            f"FEHLER: Falsches Arbeitsverzeichnis!\n"
            f"{'='*70}\n"
            f"  Gefunden     : {repo}\n"
            f"  Erwartet endet mit: {EXPECTED_ROOT_SUFFIX}\n\n"
            f"Bitte wechseln Sie in den korrekten Backup-Ordner:\n"
            f"  cd ${REPO_ROOT}{EXPECTED_ROOT_SUFFIX}\n"
            f"{'='*70}\n"
        )
        print(msg, file=sys.stderr, flush=True)
        sys.exit(2)


def _utf8_env(parent: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return environment dict with UTF-8 forced for child processes."""
    env = dict(parent or os.environ)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    env.setdefault("LANG", "C.UTF-8")
    return env
DEFAULT_CONFIG = ROOT / "ci" / "suite_config.yaml"
CHANGED_FILES_PATH = ROOT / "ci" / "changed_files.json"
AUTOFETCH_MANIFEST = "autofetch_manifest.json"
SUITE_MANIFEST_PATH = ROOT / "ci" / "suite_manifest.json"
SWEEP_CONFIG_FULL = ROOT / "configs" / "param_sweep.yaml"
SWEEP_CONFIG_FAST = ROOT / "configs" / "param_sweep_fast.yaml"


def _find_latest_nightly_zip() -> Path | None:
    candidates: List[tuple[float, Path]] = []
    reports_root = ROOT / "reports"
    if not reports_root.exists():
        return None
    for path in reports_root.glob("*_nightly/*.zip"):
        try:
            candidates.append((path.stat().st_mtime, path))
        except OSError:
            continue
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]


@dataclass
class StepResult:
    name: str
    t_start: datetime
    t_end: datetime
    ok: bool
    error: Optional[str]
    artifacts: Dict[str, Any]

    @property
    def duration(self) -> float:
        return (self.t_end - self.t_start).total_seconds()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "t_start": self.t_start.isoformat(),
            "t_end": self.t_end.isoformat(),
            "dt_s": round(self.duration, 3),
            "ok": self.ok,
            "error": self.error,
            "artifacts": self.artifacts,
        }


class StepExecutionError(Exception):
    def __init__(self, message: str, artifacts: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.artifacts = artifacts or {}


def setup_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("SUITE")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def load_yaml_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def compute_changed_files(days: int, logger: logging.Logger) -> Dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    iso_since = since.isoformat()

    git_files: Dict[str, bool] = {}
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            git_files[line.replace("/", "\\")] = True
    except Exception:
        git_files = {}

    changed: Dict[str, Dict[str, Any]] = {}
    skip_dirs = {".git", "__pycache__", "data", "experiments", "reports", "agent_out", "out", "vfall_out", "models"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        if mtime < since:
            continue
        rel = path.relative_to(ROOT)
        key = str(rel).replace("\\", "/")
        changed[key] = {
            "path": key,
            "size": path.stat().st_size,
            "mtime": mtime.isoformat(),
            "in_git": key in git_files,
        }

    files = sorted(changed.values(), key=lambda item: item["path"])
    payload = {
        "since": iso_since,
        "time_window_days": days,
        "count": len(files),
        "files": files,
    }
    CHANGED_FILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHANGED_FILES_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    logger.info(
        "Tracked %s changed files since %s (window=%s days)",
        payload["count"],
        payload["since"],
        days,
    )
    return payload


def _relative(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _normalize_path(value: Optional[str | Path]) -> Optional[str]:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return _relative(path)


def step_autofetch(run_id: str, prefer_parquet: bool, logger: logging.Logger) -> Dict[str, Any]:
    from scripts.autofetch import AutoFetchConfig, autofetch

    gaia_base = Path(f"data/raw/gaia/{run_id}/gaia_dr3_core")
    sdss_base = Path(f"data/raw/sdss/{run_id}/sdss_catalog")
    planck_fits = Path(f"data/raw/planck/{run_id}/planck_map.fits")

    cfg = AutoFetchConfig(
        run_id=run_id,
        gaia_base=gaia_base,
        sdss_base=sdss_base,
        planck_fits=planck_fits,
        prefer_parquet=prefer_parquet,
        run_pipeline=False,
        run_pytest=False,
    )
    logger.info("Autofetch starting for run_id=%s", run_id)
    manifest = autofetch(cfg)
    auto_manifest_path = ROOT / "experiments" / run_id / AUTOFETCH_MANIFEST
    artifacts_data = manifest.get("artifacts", {})
    return {
        "autofetch_manifest": _relative(auto_manifest_path),
        "gaia_primary": _normalize_path(artifacts_data.get("gaia_primary")),
        "gaia_parquet": _normalize_path(artifacts_data.get("gaia_parquet")),
        "gaia_csv": _normalize_path(artifacts_data.get("gaia_csv")),
        "sdss_primary": _normalize_path(artifacts_data.get("sdss_primary")),
        "sdss_parquet": _normalize_path(artifacts_data.get("sdss_parquet")),
        "sdss_csv": _normalize_path(artifacts_data.get("sdss_csv")),
        "planck_fits": _normalize_path(artifacts_data.get("planck_fits")),
        "errors": manifest.get("errors", []),
    }


def step_ssz_pipeline(run_id: str, logger: logging.Logger) -> Dict[str, Any]:
    try:
        import run_gaia_ssz_pipeline as pipeline
    except ModuleNotFoundError as exc:  # pragma: no cover - optional pipeline
        raise StepExecutionError(f"run_gaia_ssz_pipeline not available: {exc}")

    logger.info("Running SSZ pipeline for %s", run_id)
    items = pipeline.run_ssz_cosmo(
        run_id,
        frame_config=ROOT / "configs" / "cosmology_frame.yaml",
        ssz_params=ROOT / "configs" / "ssz_params.yaml",
        data_root=ROOT / "data",
        models_root=ROOT / "models",
        experiments_root=ROOT / "experiments",
    )
    artifacts = {
        name: _relative(path) for name, path in items.items()
    }
    return artifacts


def step_ssz_terminal(run_id: str, logger: logging.Logger) -> Dict[str, Any]:
    logger.info("Running legacy terminal SSZ suite")
    cmd = [
        sys.executable,
        "run_all_ssz_terminal.py",
        "all",
        "--run-id",
        run_id,
    ]
    logger.info("Executing: %s", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_utf8_env(os.environ),
    )
    if proc.stdout:
        logger.info(proc.stdout.strip())
    if proc.stderr:
        logger.warning(proc.stderr.strip())
    if proc.returncode != 0:
        raise StepExecutionError(
            f"run_all_ssz_terminal.py exit code {proc.returncode}",
            {"return_code": proc.returncode},
        )
    return {
        "return_code": proc.returncode,
    }


def step_ssz_terminal_all(run_id: str, cfg: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    import time

    logger.info("Running full SSZ terminal suite (all)")
    reports_dir = ROOT / "reports" / run_id
    reports_dir.mkdir(parents=True, exist_ok=True)
    collect_dir = ROOT / "testergebnisse" / run_id
    collect_dir.mkdir(parents=True, exist_ok=True)

    log_txt = reports_dir / "ssz_terminal_all.txt"
    log_master = collect_dir / "ALL_TESTS_PRINT.txt"

    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")

    cmd = [sys.executable, "run_all_ssz_terminal.py", "all"]

    # Write to log_txt only during execution, then append to master log
    with log_txt.open("w", encoding="utf-8", newline="") as fh_txt:
        header = (
            f"\n===== RUN_ALL_SSZ_TERMINAL (BEGIN) {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n"
            f"CMD: {' '.join(cmd)}\n\n"
        )
        sys.stdout.write(header)
        sys.stdout.flush()
        fh_txt.write(header)

        proc = subprocess.Popen(
            cmd,
            env=_utf8_env(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            fh_txt.write(line)

        rc = proc.wait()

        footer = f"\n===== RUN_ALL_SSZ_TERMINAL (END) rc={rc} =====\n"
        sys.stdout.write(footer)
        sys.stdout.flush()
        fh_txt.write(footer)

    # Append to master log in a single operation
    with log_master.open("a", encoding="utf-8", newline="") as fh_master:
        with log_txt.open("r", encoding="utf-8") as fh_source:
            fh_master.write(fh_source.read())

    artifacts = {
        "ssz_terminal_all_log": _relative(log_txt),
        "all_tests_master": _relative(log_master),
        "return_code": rc,
    }
    if rc != 0:
        log_msg = f"run_all_ssz_terminal.py exited with code {rc}"
        logger.warning(log_msg)
        return artifacts
    return artifacts


def step_nightly_bundle_replay(run_id: str, cfg: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    testergebnisse_root = ROOT / "testergebnisse" / run_id
    testergebnisse_root.mkdir(parents=True, exist_ok=True)

    bundle_cfg = cfg.get("nightly_bundle_path")
    bundle = Path(bundle_cfg) if bundle_cfg else _find_latest_nightly_zip()
    if not bundle or not bundle.exists():
        msg = f"No nightly bundle found (checked: {bundle_cfg or 'auto'})"
        print(f"\n[BundleReplay] {msg}\n")
        return {
            "bundle_found": False,
            "message": msg,
        }

    replay_dir = ROOT / "reports" / run_id / "bundle_replay"
    idx = 1
    out_dir = replay_dir / f"extract_{idx}"
    while out_dir.exists():
        idx += 1
        out_dir = replay_dir / f"extract_{idx}"
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(bundle, "r") as zf:
        zf.extractall(out_dir)

    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")

    executed = False
    run_cmds: List[List[str]] = []

    for candidate in ["autorun_suite.py", "ci/autorun_suite.py"]:
        matches = list(out_dir.rglob(candidate))
        if matches:
            cmd = [sys.executable, str(matches[0])]
            run_cmds.append(cmd)
            executed = True
            break

    if not executed:
        tests_dir = (out_dir / "scripts" / "tests").exists() or (out_dir / "tests").exists()
        if tests_dir:
            cmd = [sys.executable, "-m", "pytest", "-s", "-q"]
            run_cmds.append(cmd)
            executed = True

    if not executed:
        run_all = list(out_dir.rglob("run_all_ssz_terminal.py"))
        if run_all:
            cmd = [sys.executable, str(run_all[0]), "all"]
            run_cmds.append(cmd)
            executed = True

    collected: List[Dict[str, Any]] = []
    for idx_cmd, cmd in enumerate(run_cmds or [], start=1):
        print("\n================ NIGHTLY BUNDLE EXEC (BEGIN) ================\n")
        print("CWD:", out_dir)
        print("CMD:", " ".join(cmd), "\n")

        proc = subprocess.run(
            cmd,
            cwd=out_dir,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if proc.stdout:
            sys.stdout.write(proc.stdout)
            if not proc.stdout.endswith("\n"):
                sys.stdout.write("\n")
        if proc.stderr:
            print("\n--- STDERR ---\n")
            sys.stdout.write(proc.stderr)
            if not proc.stderr.endswith("\n"):
                sys.stdout.write("\n")

        print("\n================ NIGHTLY BUNDLE EXEC (END) ==================\n")
        sys.stdout.flush()

        raw_log = testergebnisse_root / f"bundle_exec_{idx_cmd:02d}.txt"
        with raw_log.open("w", encoding="utf-8", newline="") as fh:
            fh.write("### CWD ###\n" + str(out_dir) + "\n\n")
            fh.write("### CMD ###\n" + " ".join(cmd) + "\n\n")
            fh.write("### STDOUT ###\n" + (proc.stdout or "") + "\n\n")
            fh.write("### STDERR ###\n" + (proc.stderr or "") + "\n\n")
            fh.write("### RETURN CODE ###\n" + str(proc.returncode) + "\n")

        collected.append(
            {
                "cmd": cmd,
                "return_code": proc.returncode,
                "log": _relative(raw_log),
            }
        )

    patterns = [
        "**/pytest_results.xml",
        "**/junit*.xml",
        "**/suite_report.html",
        "**/ssz_terminal_all.txt",
        "**/ssz_terminal_all_summary.txt",
        "**/suite_manifest.json",
        "**/suite_*.log",
    ]
    copied: List[str] = []
    for pattern in patterns:
        for src in out_dir.glob(pattern):
            dst = testergebnisse_root / f"bundle_{src.name}"
            try:
                shutil.copy2(src, dst)
                copied.append(_relative(dst))
            except OSError:
                continue

    repo_junit = testergebnisse_root / "repo_pytest_full.xml"
    repo_log = testergebnisse_root / "repo_pytest_full.txt"
    cmd_repo = [
        sys.executable,
        "-m",
        "pytest",
        "-s",
        "-q",
        "--maxfail=999",
        f"--junitxml={repo_junit}",
    ]
    proc_repo = subprocess.run(
        cmd_repo,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    with repo_log.open("w", encoding="utf-8", newline="") as fh:
        fh.write("### CMD ###\n" + " ".join(cmd_repo) + "\n\n")
        fh.write("### STDOUT ###\n" + (proc_repo.stdout or "") + "\n\n")
        fh.write("### STDERR ###\n" + (proc_repo.stderr or "") + "\n\n")
        fh.write("### RETURN CODE ###\n" + str(proc_repo.returncode) + "\n")

    print("\n================ REPO PYTEST FULL (BEGIN) ================\n")
    sys.stdout.write(proc_repo.stdout or "")
    if proc_repo.stderr:
        if proc_repo.stdout and not proc_repo.stdout.endswith("\n"):
            sys.stdout.write("\n")
        print("\n--- STDERR ---\n")
        sys.stdout.write(proc_repo.stderr)
        if not proc_repo.stderr.endswith("\n"):
            sys.stdout.write("\n")
    print("\n================ REPO PYTEST FULL (END) ==================\n")
    sys.stdout.flush()

    artifacts = {
        "bundle_found": True,
        "bundle_path": _relative(bundle),
        "extract_dir": _relative(out_dir),
        "executed_cmds": [
            {
                "cmd": " ".join(entry["cmd"]),
                "return_code": entry["return_code"],
                "log": entry["log"],
            }
            for entry in collected
        ],
        "copied_from_bundle": copied,
        "repo_pytest_full": {
            "return_code": proc_repo.returncode,
            "stdout_path": _relative(repo_log),
            "junitxml": _relative(repo_junit),
        },
        "testergebnisse_dir": _relative(testergebnisse_root),
    }

    if any(entry["return_code"] != 0 for entry in collected) or proc_repo.returncode != 0:
        raise StepExecutionError(
            "Nightly bundle replay detected failures",
            artifacts,
        )

    return artifacts


def step_param_sweep(run_id: str, mode: str, logger: logging.Logger) -> Dict[str, Any]:
    cfg_path = SWEEP_CONFIG_FAST if mode == "fast" and SWEEP_CONFIG_FAST.exists() else SWEEP_CONFIG_FULL
    if not cfg_path.exists():
        raise StepExecutionError(f"Sweep config missing: {cfg_path}")

    cmd = [
        sys.executable,
        "scripts/ssz/sweep.py",
        run_id,
        "--config",
        str(cfg_path),
    ]
    logger.info("Running parameter sweep: %s", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_utf8_env(os.environ),
    )
    if proc.stdout:
        logger.info(proc.stdout.strip())
    if proc.stderr:
        logger.warning(proc.stderr.strip())
    if proc.returncode != 0:
        raise StepExecutionError(
            f"Parameter sweep failed with exit code {proc.returncode}",
            {"return_code": proc.returncode},
        )

    summary_path = ROOT / "reports" / run_id / "param_sweep_summary.json"
    artifacts = {
        "summary": _relative(summary_path),
        "config": _relative(cfg_path),
    }
    results_csv = ROOT / "reports" / run_id / "param_sweep_results.csv"
    if results_csv.exists():
        artifacts["results_csv"] = _relative(results_csv)
    return artifacts


def parse_junit_summary(junit_path: Path) -> Dict[str, Any]:
    import xml.etree.ElementTree as ET

    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "duration": 0.0,
        "cases": [],
    }
    if not junit_path.exists():
        return summary

    tree = ET.parse(junit_path)
    root = tree.getroot()
    for suite in root.findall("testsuite"):
        summary["total"] += int(suite.get("tests", 0))
        summary["failed"] += int(suite.get("failures", 0)) + int(suite.get("errors", 0))
        summary["skipped"] += int(suite.get("skipped", 0))
        summary["duration"] += float(suite.get("time", 0.0) or 0.0)
        for case in suite.findall("testcase"):
            case_name = case.get("classname", "") + "." + case.get("name", "")
            duration = float(case.get("time", 0.0) or 0.0)
            status = "passed"
            if case.find("failure") is not None or case.find("error") is not None:
                status = "failed"
            elif case.find("skipped") is not None:
                status = "skipped"
            summary["cases"].append({"name": case_name, "duration": duration, "status": status})
    summary["passed"] = summary["total"] - summary["failed"] - summary["skipped"]
    return summary


def step_tests(run_id: str, mode: str, logger: logging.Logger) -> Dict[str, Any]:
    import importlib.util

    reports_dir = ROOT / "reports" / run_id
    reports_dir.mkdir(parents=True, exist_ok=True)
    junit_path = reports_dir / "pytest_results.xml"
    summary_path = reports_dir / "pytest_summary.json"

    if importlib.util.find_spec("pytest") is None:
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0,
            "cases": [],
            "error": "pytest not installed",
        }
        with summary_path.open("w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        raise StepExecutionError("pytest not installed", {
            "summary_json": _relative(summary_path),
        })

    pytest_args = ["-s", "-q"]
    if mode.lower() == "fast":
        fast_filter = os.environ.get("SSZ_PYTEST_FAST_FILTER", "smoke or ssz_kernel")
        pytest_args += ["-k", fast_filter]
    # Use absolute path to tests directory to avoid path issues
    tests_dir = str(ROOT / "scripts" / "tests")
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        tests_dir,
        *pytest_args,
        f"--junitxml={junit_path}",
    ]
    logger.info("Running tests: %s", " ".join(cmd))
    env = _utf8_env(os.environ)
    env.setdefault("MPLBACKEND", "Agg")
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if proc.stdout:
        logger.info(proc.stdout.strip())
    if proc.stderr:
        logger.info(proc.stderr.strip())

    summary = parse_junit_summary(junit_path)
    with summary_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    artifacts = {
        "junit_xml": _relative(junit_path),
        "summary_json": _relative(summary_path),
        "return_code": proc.returncode,
    }
    if proc.returncode != 0:
        raise StepExecutionError(
            f"pytest exited with code {proc.returncode}",
            {
                "junit_xml": artifacts["junit_xml"],
                "summary_json": artifacts["summary_json"],
                "return_code": proc.returncode,
            },
        )
    return artifacts


def step_visualize(run_id: str, previous_results: List[StepResult], logger: logging.Logger) -> Dict[str, Any]:
    from scripts.viz import suite_dashboard

    logger.info("Building visualization dashboard")
    result = suite_dashboard.build_report(run_id, [res.as_dict() for res in previous_results])
    return {
        "report": result.get("report_html"),
        "plots": result.get("plots", []),
        "warnings": result.get("warnings", []),
    }


def step_summary(run_id: str, cfg: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    """Generate markdown and HTML summary reports."""
    reports_dir = ROOT / "reports" / run_id
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    md_out = reports_dir / "output-summary.md"
    html_out = reports_dir / "output-summary.html"
    assets_dir = reports_dir / "_summary_assets"
    
    artifacts = {}
    
    # --- Step 1: Generate Markdown Summary ---
    logger.info("Generating markdown summary...")
    try:
        summary_script = ROOT / "ci" / "summary-all-tests.py"
        if not summary_script.exists():
            raise StepExecutionError(f"summary-all-tests.py not found at {summary_script}")
        
        # Build command with optional ring analysis
        cmd = [
            sys.executable, "-X", "utf8", str(summary_script),
            "--root", str(ROOT),
            "--run-id", run_id,
            "--out", str(md_out)
        ]
        
        # Add ring temperature analysis if configured
        rings_csv = cfg.get("rings_csv")
        if rings_csv:
            cmd.extend(["--rings-csv", str(rings_csv)])
            rings_v0 = cfg.get("rings_v0", 10.0)
            cmd.extend(["--rings-v0", str(rings_v0)])
            logger.info("Ring temperature analysis enabled: %s (v0=%.1f)", rings_csv, rings_v0)
        
        logger.info("Executing: %s", " ".join(cmd))
        summary_proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_utf8_env(os.environ),
        )
        
        if summary_proc.returncode != 0:
            raise StepExecutionError(
                f"summary-all-tests.py failed (rc={summary_proc.returncode}): {summary_proc.stderr}",
                {"return_code": summary_proc.returncode}
            )
        
        if summary_proc.stdout:
            logger.info(summary_proc.stdout.strip())
        
        artifacts["markdown"] = _relative(md_out)
        logger.info("Markdown summary generated: %s", md_out)
        
    except StepExecutionError:
        raise
    except Exception as exc:
        raise StepExecutionError(f"Failed to generate markdown summary: {exc}")
    
    # --- Step 2: Generate HTML + Plots ---
    logger.info("Generating HTML report with plots...")
    try:
        viz_script = ROOT / "ci" / "summary_visualize.py"
        if not viz_script.exists():
            logger.warning("summary_visualize.py not found, skipping HTML generation")
            return artifacts
        
        if not md_out.exists():
            logger.warning("Markdown not generated, skipping HTML generation")
            return artifacts
        
        # Check for matplotlib
        try:
            import matplotlib  # noqa: F401
            plots_flag = ["--plots"]
            logger.info("Matplotlib available - plots will be generated")
        except ImportError:
            plots_flag = []
            logger.info("Matplotlib not available - skipping plots")
        
        cmd = [
            sys.executable, "-X", "utf8", str(viz_script),
            "--run-dir", str(ROOT),
            "--md", str(md_out),
            "--html", str(html_out),
            *plots_flag
        ]
        
        logger.info("Executing: %s", " ".join(cmd))
        viz_proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_utf8_env(os.environ),
        )
        
        if viz_proc.returncode == 0:
            artifacts["html"] = _relative(html_out)
            logger.info("HTML report generated: %s", html_out)
            if assets_dir.exists():
                artifacts["assets"] = _relative(assets_dir)
                logger.info("Plot assets saved to: %s", assets_dir)
            if viz_proc.stdout:
                logger.info(viz_proc.stdout.strip())
        else:
            logger.warning("summary_visualize.py failed (rc=%d): %s",
                         viz_proc.returncode, viz_proc.stderr)
            
    except Exception as exc:
        logger.warning("Failed to generate HTML report: %s", exc)
    
    return artifacts


def run_step(name: str, func: Callable[[], Dict[str, Any]], logger: logging.Logger) -> StepResult:
    t_start = datetime.now(timezone.utc)
    error = None
    artifacts: Dict[str, Any] = {}
    ok = True
    try:
        artifacts = func() or {}
    except StepExecutionError as exc:
        ok = False
        error = str(exc)
        artifacts = exc.artifacts
        logger.error("Step '%s' failed: %s", name, exc)
        logger.debug("\n%s", traceback.format_exc())
    except Exception as exc:  # pragma: no cover - defensive
        ok = False
        error = str(exc)
        logger.error("Step '%s' failed: %s", name, exc)
        logger.debug("\n%s", traceback.format_exc())
    t_end = datetime.now(timezone.utc)
    return StepResult(name=name, t_start=t_start, t_end=t_end, ok=ok, error=error, artifacts=artifacts)


def step_ring_temperature_analysis(run_id: str, cfg: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    """
    Run ring temperature → velocity prediction analysis (Section 4.6).
    """
    rings_csv = cfg.get("rings_csv")
    rings_v0 = float(cfg.get("rings_v0", 10.0))
    
    if not rings_csv or str(rings_csv).lower() == "null":
        logger.info("Ring temperature analysis disabled (rings_csv not set)")
        return {"status": "skipped", "reason": "rings_csv not configured"}
    
    rings_csv_path = ROOT / rings_csv
    if not rings_csv_path.exists():
        raise StepExecutionError(
            f"Ring temperature CSV not found: {rings_csv_path}",
            {"rings_csv": str(rings_csv_path)}
        )
    
    reports_dir = ROOT / "reports" / run_id
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    output_txt = reports_dir / "ring_temperature_analysis.txt"
    output_csv = reports_dir / "ring_temperature_predictions.csv"
    
    script_path = ROOT / "scripts" / "ring_temperature_to_velocity.py"
    
    # CSV is positional argument, not --csv
    cmd = [
        sys.executable,
        str(script_path),
        str(rings_csv_path),  # Positional argument (not --csv)
        "--v0", str(rings_v0),
        "--output", str(output_txt),
        "--csv-output", str(output_csv),
    ]
    
    logger.info("Running ring temperature analysis: %s", " ".join(cmd))
    
    env = _utf8_env(os.environ)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    
    if proc.stdout:
        logger.info(proc.stdout.strip())
    if proc.stderr:
        logger.warning(proc.stderr.strip())
    
    if proc.returncode != 0:
        raise StepExecutionError(
            f"Ring temperature analysis failed with code {proc.returncode}",
            {
                "return_code": proc.returncode,
                "rings_csv": _relative(rings_csv_path),
                "output_txt": _relative(output_txt) if output_txt.exists() else None,
            }
        )
    
    artifacts = {
        "rings_csv": _relative(rings_csv_path),
        "output_txt": _relative(output_txt),
        "output_csv": _relative(output_csv),
        "v0_kms": rings_v0,
        "return_code": proc.returncode,
    }
    
    return artifacts


def step_final_reports(run_id: str, cfg: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    """
    Consolidate all reports, outputs, and analyses into final_reports directory.
    """
    final_reports_dir_name = cfg.get("final_reports_dir", "final_reports")
    final_reports_dir = ROOT / final_reports_dir_name
    final_reports_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Consolidating all outputs to %s", final_reports_dir)
    
    # Directories to copy
    copy_map = {
        "reports": ROOT / "reports" / run_id,
        "testergebnisse": ROOT / "testergebnisse" / run_id,
        "agent_out": ROOT / "agent_out" / "reports",
        "experiments": ROOT / "experiments" / run_id,
        "logs": ROOT / "data" / "logs",
    }
    
    copied_items = {}
    
    for dest_name, source_path in copy_map.items():
        if not source_path.exists():
            logger.warning("Source path does not exist, skipping: %s", source_path)
            continue
        
        dest_path = final_reports_dir / dest_name
        
        try:
            if source_path.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
                logger.info("Copied directory: %s → %s", source_path, dest_path)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                logger.info("Copied file: %s → %s", source_path, dest_path)
            
            copied_items[dest_name] = _relative(dest_path)
        except Exception as exc:
            logger.warning("Failed to copy %s: %s", source_path, exc)
    
    # Copy analysis files
    analysis_files = [
        "RESULTS_ANALYSIS.md",
        "SEGSPACE_CONSOLIDATED_FINDINGS.md",
        "FINAL_ANALYSIS.md",
        "EHT_COMPARISON_MATRIX.md",
        "QA_CHECKLIST.md",
    ]
    
    for filename in analysis_files:
        source = ROOT / filename
        if source.exists():
            dest = final_reports_dir / filename
            shutil.copy2(source, dest)
            logger.info("Copied analysis: %s", filename)
            copied_items[filename] = _relative(dest)
    
    # Copy suite manifest
    if SUITE_MANIFEST_PATH.exists():
        dest = final_reports_dir / "suite_manifest.json"
        shutil.copy2(SUITE_MANIFEST_PATH, dest)
        copied_items["suite_manifest"] = _relative(dest)
    
    # Create index file
    index_path = final_reports_dir / "INDEX.md"
    index_lines = [
        f"# Final Reports — {run_id}",
        "",
        f"**Generated**: {datetime.now().isoformat()}",
        "",
        "## Directory Structure",
        "",
    ]
    
    for name, path in sorted(copied_items.items()):
        index_lines.append(f"- **{name}**: `{path}`")
    
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    logger.info("Created index: %s", index_path)
    
    artifacts = {
        "final_reports_dir": _relative(final_reports_dir),
        "index": _relative(index_path),
        "copied_items": copied_items,
        "count": len(copied_items),
    }
    
    return artifacts


def main(argv: Optional[List[str]] = None) -> int:
    ensure_correct_repo_root()  # Exit if running from wrong directory
    parser = argparse.ArgumentParser(description="Run the segmented spacetime suite")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to the suite_config.yaml")
    args = parser.parse_args(argv)

    if not args.config.exists():
        raise SystemExit(f"Suite configuration not found: {args.config}")

    cfg = load_yaml_config(args.config)
    run_id = cfg.get("run_id")
    if not run_id:
        raise SystemExit("suite_config.yaml missing run_id")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_root = Path(cfg.get("logs_root", "data/logs"))
    log_path = logs_root / f"suite_{run_id}_{timestamp}.log"
    logger = setup_logger(log_path)
    logger.info("Suite starting for run_id=%s", run_id)

    time_window_days = int(cfg.get("time_window_days", 7))
    changed_files = compute_changed_files(time_window_days, logger)
    prefer_parquet = bool(cfg.get("prefer_parquet", True))
    steps_cfg = cfg.get("steps", [])
    reports_dir = ROOT / "reports" / run_id
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "suite_plots").mkdir(parents=True, exist_ok=True)

    step_results: List[StepResult] = []

    mode = str(cfg.get("mode", "full")).lower()
    if mode == "fast":
        os.environ.setdefault("SSZ_SDSS_LIMIT", "5000")
        os.environ.setdefault("SSZ_GAIA_LIMIT", "20000")
        os.environ.setdefault("SSZ_ENABLE_SOLAR_VIZ", "0")

    step_funcs = {
        "autofetch": lambda: step_autofetch(run_id, prefer_parquet, logger),
        "ssz_pipeline": lambda: step_ssz_pipeline(run_id, logger),
        "ssz_terminal": lambda: step_ssz_terminal(run_id, logger),
        "ssz_terminal_all": lambda: step_ssz_terminal_all(run_id, cfg, logger),
        "nightly_bundle_replay": lambda: step_nightly_bundle_replay(run_id, cfg, logger),
        "param_sweep": lambda: step_param_sweep(run_id, mode, logger),
        "tests": lambda: step_tests(run_id, mode, logger),
        "ring_temperature_analysis": lambda: step_ring_temperature_analysis(run_id, cfg, logger),
        "summary": lambda: step_summary(run_id, cfg, logger),
        "final_reports": lambda: step_final_reports(run_id, cfg, logger),
    }

    for entry in steps_cfg:
        name = entry.get("name")
        enabled = entry.get("enabled", True)
        if not name:
            continue
        if not enabled:
            logger.info("Skipping disabled step '%s'", name)
            continue
        if name == "visualize":
            func = lambda sr=list(step_results): step_visualize(run_id, sr, logger)
        else:
            func = step_funcs.get(name)
        if func is None:
            logger.warning("Unknown step '%s' in configuration", name)
            continue
        logger.info("--- Step: %s ---", name)
        result = run_step(name, func, logger)
        step_results.append(result)

    suite_start = step_results[0].t_start if step_results else datetime.now(timezone.utc)
    suite_end = step_results[-1].t_end if step_results else suite_start

    manifest = {
        "run_id": run_id,
        "started": suite_start.isoformat(),
        "finished": suite_end.isoformat(),
        "duration_s": round((suite_end - suite_start).total_seconds(), 3),
        "log": _relative(log_path),
        "steps": [res.as_dict() for res in step_results],
        "changed_files": {
            "path": _relative(CHANGED_FILES_PATH) if CHANGED_FILES_PATH.exists() else None,
            "count": changed_files.get("count"),
            "time_window_days": time_window_days,
            "files": changed_files.get("files", []),
        },
    }
    SUITE_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Suite manifest written to %s", SUITE_MANIFEST_PATH)
    
    # Check for summary artifacts (from summary step if it ran)
    md_out = reports_dir / "output-summary.md"
    html_out = reports_dir / "output-summary.html"
    assets_dir = reports_dir / "_summary_assets"

    if write_and_print_summary is not None:
        try:
            testergebnisse_dir = ROOT / "testergebnisse" / run_id
            experiments_dir = ROOT / "experiments" / run_id
            agent_out_dir = ROOT / "agent_out"
            extra_roots = [
                ROOT / "out",
                ROOT / "vfall_out",
                ROOT / "models",
                ROOT / "models" / "cosmology",
                ROOT / "models" / "solar_system",
            ]
            write_and_print_summary(
                run_id=run_id,
                repo_root=ROOT,
                reports_dir=reports_dir,
                testergebnisse_dir=testergebnisse_dir,
                experiments_dir=experiments_dir,
                agent_out_dir=agent_out_dir,
                suite_manifest_path=SUITE_MANIFEST_PATH,
                pytest_xml_path=reports_dir / "pytest_results.xml",
                repo_pytest_xml_path=testergebnisse_dir / "repo_pytest_full.xml",
                extra_artifact_roots=[path for path in extra_roots if path.exists()],
            )
        except Exception as exc:  # pragma: no cover - diagnostic only
            print(f"[SUMMARY] Skipped (error while generating summary): {exc}", file=sys.stderr)

    ok_count = sum(1 for res in step_results if res.ok)
    fail_count = sum(1 for res in step_results if not res.ok)
    
    # Build comprehensive summary
    summary_lines = [
        f"Suite complete in {manifest['duration_s']}s -> OK: {ok_count}, Fail: {fail_count}",
        f"Markdown Report: {md_out}" if md_out.exists() else "Markdown Report: not generated",
    ]
    if html_out.exists():
        summary_lines.append(f"HTML Report    : {html_out}")
        if assets_dir.exists():
            summary_lines.append(f"Plot Assets    : {assets_dir}")
    
    summary = "\n".join(summary_lines)
    print(summary)
    logger.info(summary)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
