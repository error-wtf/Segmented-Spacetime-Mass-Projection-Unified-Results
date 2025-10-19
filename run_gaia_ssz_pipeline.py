from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scripts.preprocess.io_utils import ensure_both_formats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="End-to-end runner for SSZ cosmology pipeline")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--adql", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--cones-config", type=Path, default=None)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--models-root", type=Path, default=Path("models"))
    parser.add_argument("--experiments-root", type=Path, default=Path("experiments"))
    parser.add_argument("--cfg-ssz", type=Path, default=Path("configs/ssz_params.yaml"))
    parser.add_argument("--cfg-frame", type=Path, default=Path("configs/cosmology_frame.yaml"))
    parser.add_argument("--format", choices=["parquet", "csv", "fits"], default="parquet")
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--skip-cones", action="store_true")
    parser.add_argument("--prefer-parquet", default="true", help="true/false preference for Parquet primary outputs")
    parser.add_argument("--gaia-base", type=Path, help="Dataset base path (without extension) for GAIA raw data")
    parser.add_argument("--sdss-base", type=Path, help="Dataset base path (without extension) for SDSS raw data")
    return parser.parse_args()


def sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs(run_id: str, data_root: Path, experiments_root: Path, models_root: Path | None = None) -> Dict[str, Path]:
    models_root = Path("models") if models_root is None else Path(models_root)
    raw_dir = data_root / "raw" / "gaia" / run_id
    interim_dir = data_root / "interim" / "gaia" / run_id
    cache_dir = data_root / "cache" / "astro"
    logs_dir = data_root / "logs"
    model_cosmo_dir = models_root / "cosmology" / run_id
    model_solar_dir = models_root / "solar_system" / run_id
    viz_dir = experiments_root / run_id / "viz"
    qa_dir = experiments_root / run_id / "qa"
    backup_dir = Path("backups") / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{run_id}"

    for directory in [raw_dir, interim_dir, cache_dir, logs_dir, model_cosmo_dir, model_solar_dir, viz_dir, qa_dir, backup_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    (backup_dir / "metadata.json").write_text(
        json.dumps({"run_id": run_id, "created": datetime.utcnow().isoformat()}, indent=2),
        encoding="utf-8",
    )

    return {
        "raw": raw_dir,
        "interim": interim_dir,
        "cache": cache_dir,
        "logs": logs_dir,
        "cosmo": model_cosmo_dir,
        "solar": model_solar_dir,
        "viz": viz_dir,
        "qa": qa_dir,
        "backup": backup_dir,
        "models_root": models_root,
    }


def run_step(command: List[str], description: str) -> None:
    print(f"[SSZ PIPELINE] {description}: {' '.join(command)}")
    result = subprocess.run(command, check=True)
    if result.returncode != 0:
        raise RuntimeError(f"Step failed: {description}")


def gather_files(paths: List[Optional[Path]]) -> List[Dict[str, str]]:
    files = []
    for path in paths:
        if path is None:
            continue
        if path.exists():
            files.append({"path": str(path), "sha256": sha256(path)})
    return files


def run_ssz_cosmo(
    run_id: str,
    frame_config: str | Path,
    ssz_params: str | Path,
    *,
    data_root: str | Path = Path("data"),
    models_root: str | Path = Path("models"),
    experiments_root: str | Path = Path("experiments"),
    gaia_base: str | Path | None = None,
    sdss_base: str | Path | None = None,
    prefer_parquet: bool = True,
) -> Dict[str, Path]:
    """Programmatic entry point used by CI/autorun to build SSZ artifacts."""

    frame_config = Path(frame_config)
    ssz_params = Path(ssz_params)
    data_root = Path(data_root)
    experiments_root = Path(experiments_root)
    models_root = Path(models_root)

    locations = ensure_dirs(run_id, data_root, experiments_root, models_root)

    gaia_base_path = Path(gaia_base) if gaia_base else data_root / "raw" / "gaia" / run_id / "gaia_dr3_core"
    sdss_base_path = Path(sdss_base) if sdss_base else data_root / "raw" / "sdss" / run_id / "sdss_catalog"

    ensure_both_formats(gaia_base_path, prefer_parquet=prefer_parquet)
    ensure_both_formats(sdss_base_path, prefer_parquet=prefer_parquet)

    run_step(
        [
            sys.executable,
            "scripts/preprocess/gaia_clean_map.py",
            "--run-id",
            run_id,
            "--raw-root",
            str(data_root / "raw" / "gaia"),
            "--interim-root",
            str(data_root / "interim" / "gaia"),
            "--qa-root",
            str(experiments_root),
            "--sources-config",
            str(Path("sources.json")),
        ],
        "Clean GAIA catalog",
    )

    run_step(
        [
            sys.executable,
            "scripts/preprocess/gaia_frame_transform.py",
            "--run-id",
            run_id,
            "--interim-root",
            str(data_root / "interim" / "gaia"),
            "--frame-config",
            str(frame_config),
        ],
        "Frame transform",
    )

    run_step(
        [
            sys.executable,
            "scripts/ssz/build_ssz_model.py",
            "--run-id",
            run_id,
            "--interim-root",
            str(data_root / "interim" / "gaia"),
            "--model-root",
            str(models_root / "cosmology"),
            "--params",
            str(ssz_params),
            "--experiments-root",
            str(experiments_root),
        ],
        "Build SSZ cosmology field",
    )

    run_step(
        [
            sys.executable,
            "scripts/ssz/build_solar_system_model.py",
            "--run-id",
            run_id,
            "--cosmology-root",
            str(models_root / "cosmology"),
            "--solar-root",
            str(models_root / "solar_system"),
            "--params",
            str(ssz_params),
            "--experiments-root",
            str(experiments_root),
        ],
        "Build solar SSZ model",
    )

    run_step(
        [
            sys.executable,
            "scripts/viz/plot_ssz_maps.py",
            "--run-id",
            run_id,
            "--model-root",
            str(models_root / "cosmology"),
            "--experiments-root",
            str(experiments_root),
        ],
        "Cosmology visualization",
    )

    run_step(
        [
            sys.executable,
            "scripts/viz/plot_solar_ssz.py",
            "--run-id",
            run_id,
            "--solar-root",
            str(models_root / "solar_system"),
            "--experiments-root",
            str(experiments_root),
        ],
        "Solar visualization",
    )

    return {
        "ssz_field": locations["cosmo"] / "ssz_field.parquet",
        "ssz_meta": locations["cosmo"] / "ssz_meta.json",
        "gamma_viz": locations["viz"] / "gamma_seg_xy.png",
        "z_hist_viz": locations["viz"] / "z_seg_hist.png",
    }


def main() -> None:
    args = parse_args()
    start = datetime.utcnow()

    prefer_parquet = str(args.prefer_parquet).strip().lower() in {"1", "true", "t", "yes", "y"}

    locations = ensure_dirs(args.run_id, args.data_root, args.experiments_root, args.models_root)

    raw_dir = locations["raw"]
    interim_dir = locations["interim"]
    viz_dir = locations["viz"]

    if args.adql is None and not args.gaia_base:
        raise ValueError("Either --adql must be provided for fetching or --gaia-base must point to existing data.")

    if not args.skip_fetch and args.adql:
        gaia_out_path = raw_dir / "gaia_dr3_core.parquet"
        cmd = [
            sys.executable,
            "scripts/gaia/fetch_gaia_adql.py",
            "--adql",
            str(args.adql),
            "--out",
            str(gaia_out_path),
            "--cache",
            str(locations["cache"]),
            "--run-id",
            args.run_id,
            "--format",
            args.format,
            "--log-dir",
            str(locations["logs"]),
        ]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        run_step(cmd, "Fetch GAIA ADQL")

    if args.cones_config and not args.skip_cones:
        cmd = [
            sys.executable,
            "scripts/gaia/fetch_gaia_conesearch.py",
            "--config",
            str(args.cones_config),
            "--out",
            str(raw_dir),
            "--cache",
            str(locations["cache"]),
            "--run-id",
            args.run_id,
            "--format",
            args.format,
            "--log-dir",
            str(locations["logs"]),
        ]
        run_step(cmd, "Cone search")

    # Ensure mixed-format readiness for GAIA and SDSS raw inputs
    gaia_base = Path(args.gaia_base) if args.gaia_base else (locations["raw"] / "gaia_dr3_core")
    sdss_base = Path(args.sdss_base) if args.sdss_base else (args.data_root / "raw" / "sdss" / args.run_id / "sdss_catalog")

    gaia_paths = ensure_both_formats(gaia_base, prefer_parquet=prefer_parquet)
    sdss_paths = ensure_both_formats(sdss_base, prefer_parquet=prefer_parquet)
    print(f"[GAIA] primary dataset: {gaia_paths['primary']} (csv={gaia_paths['csv'] is not None}, parquet={gaia_paths['parquet'] is not None})")
    print(f"[SDSS] primary dataset: {sdss_paths['primary']} (csv={sdss_paths['csv'] is not None}, parquet={sdss_paths['parquet'] is not None})")

    run_step(
        [
            sys.executable,
            "scripts/preprocess/gaia_clean_map.py",
            "--run-id",
            args.run_id,
            "--raw-root",
            str(args.data_root / "raw" / "gaia"),
            "--interim-root",
            str(args.data_root / "interim" / "gaia"),
            "--qa-root",
            str(args.experiments_root),
            "--sources-config",
            str(Path("sources.json")),
        ],
        "Clean GAIA catalog",
    )

    run_step(
        [
            sys.executable,
            "scripts/preprocess/gaia_frame_transform.py",
            "--run-id",
            args.run_id,
            "--interim-root",
            str(args.data_root / "interim" / "gaia"),
            "--frame-config",
            str(args.cfg_frame),
        ],
        "Frame transform",
    )

    run_step(
        [
            sys.executable,
            "scripts/ssz/build_ssz_model.py",
            "--run-id",
            args.run_id,
            "--interim-root",
            str(args.data_root / "interim" / "gaia"),
            "--model-root",
            str(args.models_root / "cosmology"),
            "--params",
            str(args.cfg_ssz),
            "--experiments-root",
            str(args.experiments_root),
        ],
        "Build SSZ cosmology field",
    )

    run_step(
        [
            sys.executable,
            "scripts/ssz/build_solar_system_model.py",
            "--run-id",
            args.run_id,
            "--cosmology-root",
            str(args.models_root / "cosmology"),
            "--solar-root",
            str(args.models_root / "solar_system"),
            "--params",
            str(args.cfg_ssz),
            "--experiments-root",
            str(args.experiments_root),
        ],
        "Build solar SSZ model",
    )

    run_step(
        [
            sys.executable,
            "scripts/viz/plot_ssz_maps.py",
            "--run-id",
            args.run_id,
            "--model-root",
            str(args.models_root / "cosmology"),
            "--experiments-root",
            str(args.experiments_root),
        ],
        "Cosmology visualization",
    )

    run_step(
        [
            sys.executable,
            "scripts/viz/plot_solar_ssz.py",
            "--run-id",
            args.run_id,
            "--solar-root",
            str(args.models_root / "solar_system"),
            "--experiments-root",
            str(args.experiments_root),
        ],
        "Solar visualization",
    )

    outputs = [
        interim_dir / "gaia_clean.parquet",
        interim_dir / "gaia_phase_space.parquet",
        locations["cosmo"] / "ssz_field.parquet",
        locations["cosmo"] / "ssz_meta.json",
        locations["solar"] / "solar_ssz.json",
        viz_dir / "ssz_density_scatter.html",
    ]

    manifest_path = args.experiments_root / args.run_id / "MANIFEST.json"
    pip_freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True)

    manifest = {
        "run_id": args.run_id,
        "timestamp": {
            "started": start.isoformat(),
            "finished": datetime.utcnow().isoformat(),
        },
        "inputs": gather_files([args.adql, args.cfg_ssz, args.cfg_frame] + ([args.cones_config] if args.cones_config else [])),
        "outputs": gather_files(outputs),
        "environment": {
            "python": sys.version,
            "pip_freeze": pip_freeze.stdout.splitlines(),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    time.sleep(1.0)
    print(f"[SSZ PIPELINE] Completed run. Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
