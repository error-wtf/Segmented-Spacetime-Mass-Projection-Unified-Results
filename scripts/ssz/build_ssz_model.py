from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import yaml


@dataclass
class SSZConfig:
    run_id: str
    phase_space_path: Path
    model_root: Path
    params: Dict[str, object]
    output_field: Path
    output_meta: Path
    viz_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construct segmented spacetime cosmology fields")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--phase-space", default=None)
    parser.add_argument("--interim-root", default=Path("data/interim/gaia"), type=Path)
    parser.add_argument("--model-root", default=Path("models/cosmology"), type=Path)
    parser.add_argument("--params", default=Path("configs/ssz_params.yaml"), type=Path)
    parser.add_argument("--experiments-root", default=Path("experiments"), type=Path)
    return parser.parse_args()


def load_params(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing SSZ params: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_config(args: argparse.Namespace) -> SSZConfig:
    interim = args.phase_space or (args.interim_root / args.run_id / "gaia_phase_space.parquet")
    phase_space_path = Path(interim)
    if not phase_space_path.exists():
        raise FileNotFoundError(f"Phase-space catalog missing: {phase_space_path}")
    params = load_params(args.params)
    model_dir = args.model_root / args.run_id
    model_dir.mkdir(parents=True, exist_ok=True)
    output_field = model_dir / "ssz_field.parquet"
    output_meta = model_dir / "ssz_meta.json"
    viz_dir = args.experiments_root / args.run_id / "viz"
    viz_dir.mkdir(parents=True, exist_ok=True)
    return SSZConfig(args.run_id, phase_space_path, model_dir, params, output_field, output_meta, viz_dir)


def load_phase_space(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def compute_segment_density(df: pd.DataFrame, params: Dict[str, object]) -> pd.DataFrame:
    df = df.copy()
    phi = params.get("phi", 1.61803398875)
    base_segments = params.get("base_segments_at_r1", 6)
    sigma = params.get("velocity_weight", 0.2)

    radius = np.sqrt(df["x_kpc"] ** 2 + df["y_kpc"] ** 2 + df["z_kpc"] ** 2)
    radius = np.nan_to_num(radius, nan=0.0, posinf=0.0, neginf=0.0)
    segment_count = base_segments * (phi ** np.log1p(radius))
    df["segment_density"] = segment_count
    df["segment_velocity_weight"] = sigma * np.sqrt(df["v_x_kms"] ** 2 + df["v_y_kms"] ** 2 + df["v_z_kms"] ** 2)
    df["segment_velocity_weight"] = np.nan_to_num(df["segment_velocity_weight"], nan=0.0, posinf=0.0, neginf=0.0)
    df["ssz_density"] = df["segment_density"] * (1.0 + df["segment_velocity_weight"])
    return df


def assign_segments(df: pd.DataFrame, params: Dict[str, object]) -> pd.DataFrame:
    df = df.copy()
    phi = params.get("phi", 1.61803398875)
    growth_rate = params.get("segment_scale_law", "logarithmic")
    if growth_rate == "logarithmic":
        ring_index = np.floor(np.log1p(np.hypot(df["x_kpc"], df["y_kpc"])) * phi)
    else:
        ring_index = np.floor(np.hypot(df["x_kpc"], df["y_kpc"]) * phi)
    ring_index = np.nan_to_num(ring_index, nan=0.0, posinf=0.0, neginf=0.0)
    ring_idx_int = ring_index.astype(int)
    segment_id = (ring_idx_int % 360).astype(int)
    df["ring_id"] = ring_idx_int
    df["segment_id"] = segment_id
    return df


def natural_boundary(df: pd.DataFrame, params: Dict[str, object]) -> pd.DataFrame:
    beta = params.get("natural_boundary_beta", 0.05)
    delta_m_ref = params.get("delta_m_reference", 0.0)
    radius = np.sqrt(df["x_kpc"] ** 2 + df["y_kpc"] ** 2 + df["z_kpc"] ** 2)
    df["natural_boundary"] = (params.get("phi", 1.61803398875) / 2.0) * (1.0 + beta * (df.get("mass_proxy", delta_m_ref))) * radius
    return df


def spiral_parameters(df: pd.DataFrame, params: Dict[str, object]) -> pd.DataFrame:
    df = df.copy()
    spiral_turns = params.get("spiral_turns", 3)
    growth = params.get("segment_scale_law", "logarithmic")
    df["spiral_turn_index"] = (df["segment_id"] % max(spiral_turns, 1)).astype(int)
    df["spiral_growth_rule"] = growth
    return df


def write_outputs(df: pd.DataFrame, cfg: SSZConfig) -> None:
    df.to_parquet(cfg.output_field, index=False)
    meta = {
        "run_id": cfg.run_id,
        "rows": len(df),
        "params_path": str(cfg.params),
        "features": ["segment_density", "segment_id", "natural_boundary", "spiral_turn_index"],
    }
    cfg.output_meta.write_text(json.dumps(meta, indent=2))


def main() -> None:
    args = parse_args()
    cfg = build_config(args)
    df = load_phase_space(cfg.phase_space_path)
    df = compute_segment_density(df, cfg.params)
    df = assign_segments(df, cfg.params)
    df = natural_boundary(df, cfg.params)
    df = spiral_parameters(df, cfg.params)
    write_outputs(df, cfg)


if __name__ == "__main__":
    main()
