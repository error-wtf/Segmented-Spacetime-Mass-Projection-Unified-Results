from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import json
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go


@dataclass
class SolarVizConfig:
    run_id: str
    solar_model: Path
    viz_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize solar system SSZ segments")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--solar-root", default=Path("models/solar_system"), type=Path)
    parser.add_argument("--experiments-root", default=Path("experiments"), type=Path)
    parser.add_argument("--ephemerides", default=None, type=Path, help="Optional ephemerides JSON for orbital overlays")
    parser.add_argument("--phi-turns", type=int, default=3, help="Number of φ-spiral turns to overlay around origin")
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> SolarVizConfig:
    solar_model = args.solar_root / args.run_id / "solar_ssz.json"
    if not solar_model.exists():
        raise FileNotFoundError(f"Solar SSZ model missing: {solar_model}")
    viz_dir = args.experiments_root / args.run_id / "viz"
    viz_dir.mkdir(parents=True, exist_ok=True)
    return SolarVizConfig(args.run_id, solar_model, viz_dir)


def load_ephemerides(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        # accept {"bodies": [...]} or plain list
        records = payload.get("bodies") or payload.get("ephemerides") or payload.get("data") or []
    else:
        records = payload
    return pd.DataFrame(records)


def orbit_trace(df: pd.DataFrame) -> list[go.Scatter3d]:
    if df.empty:
        return []
    traces: list[go.Scatter3d] = []
    au_to_kpc = 4.84813681109536e-9
    for _, row in df.iterrows():
        radius_au = row.get("semi_major_axis_au") or row.get("radius_au")
        if not radius_au:
            continue
        samples = 240
        theta = np.linspace(0, 2 * math.pi, samples)
        r_kpc = float(radius_au) * au_to_kpc
        x = r_kpc * np.cos(theta)
        y = r_kpc * np.sin(theta)
        z = np.zeros_like(theta)
        traces.append(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line=dict(color="#FFB347", width=2),
                name=f"Orbit: {row.get('name', 'body')}"
            )
        )
    return traces


def phi_spiral_trace(turns: int, max_radius_kpc: float) -> go.Scatter3d:
    if max_radius_kpc <= 0 or turns <= 0:
        return None
    phi = (1 + 5 ** 0.5) / 2
    samples = 400
    theta = np.linspace(0, turns * 2 * math.pi, samples)
    # logarithmic spiral r = a * phi^(theta / (2π))
    a = max_radius_kpc / (phi ** turns)
    r = a * (phi ** (theta / (2 * math.pi)))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.zeros_like(theta)
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        line=dict(color="#6A5ACD", width=2, dash="dash"),
        name=f"φ-spiral ({turns} turns)"
    )


def load_segments(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    segments = payload.get("segments", [])
    if not segments:
        return pd.DataFrame()
    return pd.DataFrame(segments)


def plot_segments(df: pd.DataFrame, cfg: SolarVizConfig, ephemerides: pd.DataFrame, phi_turns: int) -> Path:
    fig = go.Figure()

    if df.empty:
        fig.add_annotation(text="No solar SSZ segments available", showarrow=False, font=dict(size=18))
    else:
        x = df["x_kpc"].to_numpy() if "x_kpc" in df else np.zeros(len(df))
        y = df["y_kpc"].to_numpy() if "y_kpc" in df else np.zeros(len(df))
        z = df["z_kpc"].to_numpy() if "z_kpc" in df else np.zeros(len(df))
        segments = df["solar_segment"].to_numpy() if "solar_segment" in df else np.zeros(len(df))
        hover = df["segment_id"].astype(str).to_list() if "segment_id" in df else ["segment"] * len(df)

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="markers",
                marker=dict(
                    size=4,
                    color=segments,
                    colorscale="Viridis",
                    opacity=0.7,
                ),
                text=hover,
                name="Segments",
            )
        )

        max_radius = float(np.sqrt((x ** 2 + y ** 2).max())) if len(x) else 0.0
        spiral = phi_spiral_trace(phi_turns, max_radius if max_radius > 0 else 0.02)
        if spiral:
            fig.add_trace(spiral)

    for trace in orbit_trace(ephemerides):
        fig.add_trace(trace)

    fig.update_layout(
        title=f"Solar SSZ Segments ({cfg.run_id})",
        scene=dict(xaxis_title="x (kpc)", yaxis_title="y (kpc)", zaxis_title="z (kpc)"),
    )
    out_path = cfg.viz_dir / "solar_ssz.html"
    fig.write_html(out_path)
    return out_path


def main() -> None:
    args = parse_args()
    cfg = build_config(args)
    df = load_segments(cfg.solar_model)
    ephemerides = load_ephemerides(args.ephemerides)
    plot_segments(df, cfg, ephemerides, args.phi_turns)


if __name__ == "__main__":
    main()
