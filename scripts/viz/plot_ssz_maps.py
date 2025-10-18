from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt


@dataclass
class VizConfig:
    run_id: str
    cosmology_field: Path
    viz_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SSZ cosmology visualization assets")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-root", default=Path("models/cosmology"), type=Path)
    parser.add_argument("--experiments-root", default=Path("experiments"), type=Path)
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> VizConfig:
    cosmology_field = args.model_root / args.run_id / "ssz_field.parquet"
    if not cosmology_field.exists():
        raise FileNotFoundError(f"Missing cosmology field: {cosmology_field}")
    viz_dir = args.experiments_root / args.run_id / "viz"
    viz_dir.mkdir(parents=True, exist_ok=True)
    return VizConfig(args.run_id, cosmology_field, viz_dir)


def load_field(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def plot_density(df: pd.DataFrame, cfg: VizConfig) -> Path:
    fig = px.scatter_3d(
        df.sample(min(10000, len(df))),
        x="x_kpc",
        y="y_kpc",
        z="z_kpc",
        color="ssz_density",
        size_max=4,
        opacity=0.6,
        title=f"SSZ Density Field ({cfg.run_id})",
        color_continuous_scale="Viridis",
    )
    out_path = cfg.viz_dir / "ssz_density_scatter.html"
    fig.write_html(out_path)
    return out_path


def _ensure_galactic(df: pd.DataFrame) -> pd.DataFrame:
    if {"l_deg", "b_deg"}.issubset(df.columns):
        return df
    if not {"ra", "dec"}.issubset(df.columns):
        return df
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        coord = SkyCoord(
            ra=pd.to_numeric(df["ra"], errors="coerce").to_numpy(float) * u.deg,
            dec=pd.to_numeric(df["dec"], errors="coerce").to_numpy(float) * u.deg,
            frame="icrs",
        )
        gal = coord.galactic
        df = df.copy()
        df["l_deg"] = gal.l.deg
        df["b_deg"] = gal.b.deg
    except Exception:
        # Astropy not available or conversion failed; leave as-is.
        pass
    return df


def _write_placeholder(path: Path, message: str, debug_df: pd.DataFrame | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    html_path = path.with_suffix(".html")
    html_path.write_text(
        f"<html><body><p>{message}</p><img src='{path.name}' alt='{message}'/></body></html>",
        encoding="utf-8",
    )
    if debug_df is not None and debug_df.size:
        debug_df.to_csv(path.with_suffix(".debug.csv"), index=False)


def plot_mollweide(df: pd.DataFrame, cfg: VizConfig) -> Path:
    df = _ensure_galactic(df)
    viz_dir = cfg.viz_dir
    png_path = viz_dir / "ssz_density_mollweide.png"

    if not {"l_deg", "b_deg"}.issubset(df.columns):
        _write_placeholder(png_path, "No galactic coordinates available")
        return png_path

    l = pd.to_numeric(df["l_deg"], errors="coerce").to_numpy()
    b = pd.to_numeric(df["b_deg"], errors="coerce").to_numpy()
    weights = pd.to_numeric(df.get("ssz_density", pd.Series(np.ones(len(df)))), errors="coerce").to_numpy()

    mask = np.isfinite(l) & np.isfinite(b) & np.isfinite(weights)
    l, b, weights = l[mask], b[mask], weights[mask]

    if l.size == 0:
        _write_placeholder(png_path, "No finite galactic data", df)
        return png_path

    l_wrapped = ((l + 180.0) % 360.0) - 180.0
    n_l, n_b = 180, 90
    heatmap, l_edges, b_edges = np.histogram2d(
        l_wrapped,
        b,
        bins=(n_l, n_b),
        range=[(-180.0, 180.0), (-90.0, 90.0)],
        weights=weights,
        density=False,
    )
    heatmap = heatmap.T

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection="mollweide")
    L, B = np.meshgrid(np.deg2rad(l_edges), np.deg2rad(b_edges))
    im = ax.pcolormesh(L, B, heatmap, shading="auto", cmap="viridis")
    ax.grid(True, color="lightgray", linestyle="--", linewidth=0.5)
    ax.set_title(f"SSZ Sky Map ({cfg.run_id})")
    cb = fig.colorbar(im, ax=ax, pad=0.08)
    cb.set_label("Counts")
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    html_path = png_path.with_suffix(".html")
    html_path.write_text(
        f"<html><body><img src='{png_path.name}' alt='SSZ mollweide map'/></body></html>",
        encoding="utf-8",
    )
    return html_path


def main() -> None:
    args = parse_args()
    cfg = build_config(args)
    df = load_field(cfg.cosmology_field)
    plot_density(df, cfg)
    try:
        plot_mollweide(df, cfg)
    except KeyError:
        pass


if __name__ == "__main__":
    main()
