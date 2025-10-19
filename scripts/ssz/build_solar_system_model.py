from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml


@dataclass
class SolarConfig:
    run_id: str
    cosmology_field: Path
    output_json: Path
    viz_html: Path
    params: Dict[str, object]
    experiments_root: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construct local solar system SSZ model")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cosmology-root", default=Path("models/cosmology"), type=Path)
    parser.add_argument("--solar-root", default=Path("models/solar_system"), type=Path)
    parser.add_argument("--params", default=Path("configs/ssz_params.yaml"), type=Path)
    parser.add_argument("--experiments-root", default=Path("experiments"), type=Path)
    return parser.parse_args()


def load_params(path: Path) -> Dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_config(args: argparse.Namespace) -> SolarConfig:
    cosmology_field = args.cosmology_root / args.run_id / "ssz_field.parquet"
    if not cosmology_field.exists():
        raise FileNotFoundError(f"Cosmology field missing: {cosmology_field}")
    params = load_params(args.params)
    solar_root = args.solar_root / args.run_id
    solar_root.mkdir(parents=True, exist_ok=True)
    experiments_root = args.experiments_root / args.run_id / "viz"
    experiments_root.mkdir(parents=True, exist_ok=True)
    return SolarConfig(
        run_id=args.run_id,
        cosmology_field=cosmology_field,
        output_json=solar_root / "solar_ssz.json",
        viz_html=experiments_root / "solar_ssz.html",
        params=params,
        experiments_root=experiments_root,
    )


def load_cosmology_field(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def select_local_volume(df: pd.DataFrame, params: Dict[str, object]) -> pd.DataFrame:
    max_distance_pc = params.get("local_volume_selection", {}).get("max_distance_pc", 200.0)
    distance_pc = df["distance_pc"].fillna(np.inf)
    mask = distance_pc <= max_distance_pc
    return df[mask].copy()


def discretize_segments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["solar_ring"] = np.floor(np.sqrt(df["x_kpc"] ** 2 + df["y_kpc"] ** 2) * 1000).astype(int)
    df["solar_segment"] = df["segment_id"] % 16
    return df


def generate_manifest(df: pd.DataFrame, cfg: SolarConfig) -> Dict[str, object]:
    return {
        "run_id": cfg.run_id,
        "points": len(df),
        "segment_range": [int(df["solar_segment"].min()), int(df["solar_segment"].max())] if not df.empty else [0, 0],
    }


def write_json(df: pd.DataFrame, cfg: SolarConfig) -> None:
    payload = {
        "metadata": {
            "run_id": cfg.run_id,
            "count": int(len(df)),
        },
        "segments": df.to_dict(orient="records"),
    }
    cfg.output_json.write_text(json.dumps(payload, indent=2))


def write_placeholder_viz(cfg: SolarConfig) -> None:
    html = [
        "<html><head><title>Solar SSZ Visualization</title></head>",
        "<body>",
        "<h1>Solar SSZ Visualization Placeholder</h1>",
        "<p>Populate with Plotly exports from scripts/viz/plot_solar_ssz.py.</p>",
        "</body></html>",
    ]
    cfg.viz_html.write_text("\n".join(html), encoding="utf-8")


def main() -> None:
    args = parse_args()
    cfg = build_config(args)
    df = load_cosmology_field(cfg.cosmology_field)
    df = select_local_volume(df, cfg.params)
    df = discretize_segments(df)
    manifest = generate_manifest(df, cfg)
    write_json(df, cfg)
    write_placeholder_viz(cfg)
    (cfg.cosmology_field.parent / "solar_manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
