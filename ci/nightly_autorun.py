from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "ci" / "suite_config.yaml"
AUTORUN = ROOT / "ci" / "autorun_suite.py"


def _load_config(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _write_temp_config(cfg: Dict) -> Path:
    tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix="_suite.yaml", delete=False)
    with tmp:
        yaml.safe_dump(cfg, tmp)
    return Path(tmp.name)


def _derive_run_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{stamp}_{prefix}"


def _run_suite(config_path: Path, mode: str) -> None:
    cmd = [
        sys.executable,
        str(AUTORUN),
        "--config",
        str(config_path),
    ]
    print(f"[NIGHTLY] Running suite: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Autorun failed with exit code {result.returncode}")


def _collect_artifact_paths(run_id: str) -> List[Path]:
    items = [
        ROOT / "ci" / "suite_manifest.json",
        ROOT / "experiments" / run_id / "autofetch_manifest.json",
        ROOT / "reports" / run_id / "suite_report.html",
        ROOT / "reports" / run_id / "pytest_results.xml",
        ROOT / "reports" / run_id / "pytest_summary.json",
    ]
    viz_dir = ROOT / "experiments" / run_id / "viz"
    plots_dir = ROOT / "reports" / run_id / "suite_plots"
    if viz_dir.exists():
        items.extend(sorted(viz_dir.rglob("*")))
    if plots_dir.exists():
        items.extend(sorted(plots_dir.rglob("*")))
    return [path for path in items if path.exists()]


def _bundle(run_id: str, out_path: Path) -> Dict[str, str]:
    files = _collect_artifact_paths(run_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = file_path.relative_to(ROOT)
            zf.write(file_path, arcname)
    return {"zip": str(out_path.relative_to(ROOT)), "files": [str(p.relative_to(ROOT)) for p in files]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nightly runner for SSZ suite")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--mode", choices=["fast", "full"], default="full")
    parser.add_argument("--run-id", help="Override generated run id")
    parser.add_argument("--prefix", default="gaia_ssz_nightly", help="Run id suffix prefix")
    parser.add_argument("--bundle-path", type=Path, help="Optional explicit bundle path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = _load_config(args.config)

    run_id = args.run_id or _derive_run_id(args.prefix)
    cfg["run_id"] = run_id
    cfg["mode"] = args.mode
    cfg["outputs_root"] = f"experiments/{run_id}/suite"

    tmp_cfg = _write_temp_config(cfg)
    try:
        _run_suite(tmp_cfg, args.mode)
    finally:
        tmp_cfg.unlink(missing_ok=True)

    bundle_path = args.bundle_path or (ROOT / "reports" / run_id / f"{run_id}_bundle.zip")
    bundle_info = _bundle(run_id, bundle_path)

    metadata = {
        "run_id": run_id,
        "mode": args.mode,
        "bundle": bundle_info,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = bundle_path.with_suffix(".json")
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"[NIGHTLY] Bundle written to {bundle_path}")
    print(f"[NIGHTLY] Metadata written to {meta_path}")


if __name__ == "__main__":
    main()
