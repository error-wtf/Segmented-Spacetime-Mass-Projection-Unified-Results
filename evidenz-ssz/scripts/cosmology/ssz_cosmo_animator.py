#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Readable animation of SSZ cosmology fit diagnostics."""
from __future__ import annotations

import argparse
import io
import json
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from PIL import Image

try:
    import imageio.v2 as imageio  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    imageio = None

from ssz_cosmo_core import BackgroundParams, CosmoEngine
from ssz_cosmo_models import build_context
from ssz_cosmo_data import DataRepository

C_LIGHT_KM_S = 299792.458


# ---------------------------------------------------------------------------
# Logging / IO helpers
# ---------------------------------------------------------------------------


def setup_stdout_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            try:
                sys.stdout = io.TextIOWrapper(  # type: ignore[assignment]
                    sys.stdout.buffer,
                    encoding="utf-8",
                    errors="replace",
                    line_buffering=True,
                )
            except Exception:
                pass


def log(level: str, message: str) -> None:
    print(f"{level}: {message}")


# ---------------------------------------------------------------------------
# Data and summary loading
# ---------------------------------------------------------------------------


def load_summary(path: Optional[Path]) -> Dict:
    if path is None:
        return {}
    if not path.exists():
        log("WARN", f"Summary file {path} not found – using defaults")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # pragma: no cover
        log("WARN", f"Failed to read summary {path}: {exc}")
        return {}


def build_engine(model_key: str, summary: Dict) -> Tuple[CosmoEngine, BackgroundParams, Dict[str, float]]:
    best = summary.get("best_fit", {})
    background = BackgroundParams(
        H0=float(best.get("H0", 70.0)),
        Omega_m=float(best.get("Omega_m", 0.3)),
        Omega_b=float(best.get("Omega_b", 0.05)),
        Omega_lambda=float(best.get("Omega_lambda", 0.7)),
        Omega_k=float(best.get("Omega_k", 0.0)),
        sigma8=float(best.get("sigma8", 0.8)),
    )
    extra = {
        "alpha_ssz": float(best.get("alpha_ssz", 0.0)),
        "beta": float(best.get("beta", 0.0)),
        "gamma": float(best.get("gamma", 0.0)),
        "eta_ssz": float(best.get("eta_ssz", 0.0)),
        "beta_g": float(best.get("beta_g", 0.0)),
    }
    context = build_context(model_key, background, extra)
    engine = CosmoEngine(context)
    return engine, background, extra


# ---------------------------------------------------------------------------
# Theory curves
# ---------------------------------------------------------------------------


def distance_modulus(engine: CosmoEngine, z: np.ndarray) -> np.ndarray:
    dl = np.array([engine.luminosity_distance(float(zi)) for zi in z])
    dl = np.clip(dl, 1e-6, None)
    return 5 * np.log10(dl) + 25


def bao_dv_by_rd(engine: CosmoEngine, z: np.ndarray) -> np.ndarray:
    rd = engine.sound_horizon()
    rd = max(rd, 1e-6)
    dv = np.array([engine.volume_distance(float(zi)) for zi in z])
    return dv / rd


def theory_fs8(engine: CosmoEngine, z: np.ndarray) -> np.ndarray:
    return engine.f_sigma8(z)


# ---------------------------------------------------------------------------
# Storyboard
# ---------------------------------------------------------------------------


@dataclass
class FrameState:
    index: int
    total: int
    frac: float
    sn_points: int
    bao_points: int
    fs8_points: int


def generate_storyboard(total_frames: int, sn_n: int, bao_n: int, fs8_n: int) -> List[FrameState]:
    frames: List[FrameState] = []
    fractions = np.linspace(0.05, 1.0, total_frames)
    for idx, frac in enumerate(fractions):
        frames.append(
            FrameState(
                index=idx,
                total=total_frames,
                frac=float(frac),
                sn_points=max(1, int(np.ceil(frac * sn_n))) if sn_n > 0 else 0,
                bao_points=max(1, int(np.ceil(frac * bao_n))) if bao_n > 0 else 0,
                fs8_points=max(1, int(np.ceil(frac * fs8_n))) if fs8_n > 0 else 0,
            )
        )
    return frames


# ---------------------------------------------------------------------------
# Figure rendering
# ---------------------------------------------------------------------------


def _wrap_legend(legend: Optional[matplotlib.legend.Legend], width: int = 28) -> None:
    if legend is None:
        return
    for text in legend.get_texts():
        content = text.get_text()
        if not content:
            continue
        text.set_text(textwrap.fill(content, width=width))


def init_figure(dpi: int = 160) -> Tuple[plt.Figure, Dict[str, plt.Axes]]:
    fig = plt.figure(figsize=(14.0, 7.8), dpi=dpi)
    fig_w, fig_h = fig.get_size_inches()
    scale = (fig_w * fig_h) / 22.0
    base = max(8.0, min(16.0, 1.5 * scale))
    plt.rcParams.update(
        {
            "font.size": base,
            "axes.titlesize": base + 1,
            "axes.labelsize": base,
            "xtick.labelsize": max(base - 2, 6),
            "ytick.labelsize": max(base - 2, 6),
            "legend.fontsize": max(base - 2, 6),
            "figure.titlesize": base + 3,
        }
    )
    gs = GridSpec(
        2,
        2,
        figure=fig,
        width_ratios=[1.0, 1.05],
        height_ratios=[1.05, 1.0],
        wspace=0.28,
        hspace=0.32,
    )
    ax_sn = fig.add_subplot(gs[0, 0])
    ax_bao = fig.add_subplot(gs[0, 1])
    ax_fs8 = fig.add_subplot(gs[1, 0])
    ax_info = fig.add_subplot(gs[1, 1])
    ax_info.axis("off")
    return fig, {"sn": ax_sn, "bao": ax_bao, "fs8": ax_fs8, "info": ax_info, "base_font": base}


def update_frame(
    fig: plt.Figure,
    axes: Dict[str, plt.Axes],
    state: FrameState,
    sn_df: np.ndarray,
    bao_df: np.ndarray,
    fs8_df: np.ndarray,
    theory: Dict[str, np.ndarray],
    summary: Dict,
    meta: Dict[str, Dict],
) -> None:
    ax_sn = axes["sn"]
    ax_sn.clear()
    if sn_df.size:
        ax_sn.errorbar(
            sn_df[: state.sn_points, 0],
            sn_df[: state.sn_points, 1],
            yerr=sn_df[: state.sn_points, 2],
            fmt="o",
            color="#1f77b4",
            ecolor="#1f77b4",
            markersize=6,
            alpha=0.9,
            label="SN Ia",
        )
    ax_sn.plot(theory["sn_z"], theory["sn_mu"], color="#d62728", linewidth=3, label="Modell")
    base = axes.get("base_font", 12.0)
    ax_sn.set_xlabel("Rotverschiebung z")
    ax_sn.set_ylabel("Distanzmodul μ")
    ax_sn.set_title("Hubble-Diagramm", pad=8)
    ax_sn.grid(True, alpha=0.25)
    leg_sn = ax_sn.legend(loc="upper left", frameon=True, framealpha=0.85)
    _wrap_legend(leg_sn)

    ax_bao = axes["bao"]
    ax_bao.clear()
    if bao_df.size:
        ax_bao.errorbar(
            bao_df[: state.bao_points, 0],
            bao_df[: state.bao_points, 1],
            yerr=bao_df[: state.bao_points, 2] if bao_df.shape[1] > 2 else None,
            fmt="s",
            color="#2ca02c",
            ecolor="#2ca02c",
            markersize=7,
            alpha=0.9,
            label="BAO",
        )
    ax_bao.plot(theory["bao_z"], theory["bao_dv"], color="#9467bd", linewidth=3, label="Modell")
    ax_bao.set_xlabel("Rotverschiebung z")
    ax_bao.set_ylabel(r"$D_V / r_d$")
    ax_bao.set_title("BAO Distanzmaß", pad=8)
    ax_bao.grid(True, alpha=0.25)
    leg_bao = ax_bao.legend(loc="upper left", frameon=True, framealpha=0.85)
    _wrap_legend(leg_bao)

    ax_fs8 = axes["fs8"]
    ax_fs8.clear()
    if fs8_df.size:
        ax_fs8.errorbar(
            fs8_df[: state.fs8_points, 0],
            fs8_df[: state.fs8_points, 1],
            yerr=fs8_df[: state.fs8_points, 2],
            fmt="^",
            color="#ff7f0e",
            ecolor="#ff7f0e",
            markersize=7,
            alpha=0.9,
            label=r"Daten $f\sigma_8$",
        )
    ax_fs8.plot(theory["fs8_z"], theory["fs8_curve"], color="#17becf", linewidth=3, label=r"Modell $f\sigma_8$")
    ax_fs8.set_xlabel("Rotverschiebung z")
    ax_fs8.set_ylabel(r"$f\sigma_8$")
    ax_fs8.set_title("Wachstum der Strukturen", pad=8)
    ax_fs8.grid(True, alpha=0.25)
    leg_fs = ax_fs8.legend(loc="upper right", frameon=True, framealpha=0.85)
    _wrap_legend(leg_fs)

    ax_info = axes["info"]
    ax_info.clear()
    ax_info.axis("off")
    best = summary.get("best_fit", {})
    chi2 = summary.get("chi2", {})
    meta_lines = [
        f"Frame {state.index + 1}/{state.total} ({state.frac * 100:5.1f}%)",
        "",
        "Parameter:",
    ]
    param_block = [
        f"H₀ = {best.get('H0', 70.0):.2f}",
        f"Ωₘ = {best.get('Omega_m', 0.3):.3f}",
        f"Ω_b = {best.get('Omega_b', 0.05):.3f}",
        f"σ₈ = {best.get('sigma8', 0.8):.3f}",
        f"α_ssz = {best.get('alpha_ssz', 0.0):.3f}",
        f"β = {best.get('beta', 0.0):.3f}",
        f"γ = {best.get('gamma', 0.0):.3f}",
        f"η_ssz = {best.get('eta_ssz', 0.0):.3f}",
        f"β_g = {best.get('beta_g', 0.0):.3f}",
    ]
    half = (len(param_block) + 1) // 2
    left_params = "\n".join(param_block[:half])
    right_params = "\n".join(param_block[half:])
    chi_lines = [
        "",
        "χ² Beiträge:",
        f"gesamt = {chi2.get('total', np.nan):.2f}",
        f"SN = {chi2.get('sn', np.nan):.2f}",
        f"BAO = {chi2.get('bao', np.nan):.2f}",
        f"CMB = {chi2.get('cmb', np.nan):.2f}",
        f"fσ₈ = {chi2.get('fs8', np.nan):.2f}",
    ]
    sources = [
        "",
        "Datenquellen:",
        f"SN: {meta['sn'].get('source', 'synthetisch')}",
        f"BAO: {meta['bao'].get('source', 'synthetisch')}",
        f"fσ₈: {meta['fs8'].get('source', 'synthetisch')}",
    ]
    ax_info.text(0.0, 1.0, "\n".join(meta_lines), ha="left", va="top", fontsize=max(base - 1, 7))
    ax_info.text(0.0, 0.78, left_params, ha="left", va="top", fontsize=max(base - 1, 7), linespacing=1.25)
    ax_info.text(0.52, 0.78, right_params, ha="left", va="top", fontsize=max(base - 1, 7), linespacing=1.25)
    ax_info.text(0.0, 0.35, "\n".join(chi_lines), ha="left", va="top", fontsize=max(base - 1, 7), linespacing=1.2)
    ax_info.text(0.0, 0.05, "\n".join(sources), ha="left", va="top", fontsize=max(base - 2, 6), linespacing=1.2)

    fig.suptitle("ΛCDM vs. SSZ — Vergleich mit observablen Daten", y=0.98, fontweight="bold")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_frames(
    fig: plt.Figure,
    axes: Dict[str, plt.Axes],
    storyboard: Sequence[FrameState],
    sn_df: np.ndarray,
    bao_df: np.ndarray,
    fs8_df: np.ndarray,
    theory: Dict[str, np.ndarray],
    summary: Dict,
    meta: Dict[str, Dict],
) -> List[Image.Image]:
    frames: List[Image.Image] = []
    for state in storyboard:
        update_frame(fig, axes, state, sn_df, bao_df, fs8_df, theory, summary, meta)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        buffer = np.asarray(renderer.buffer_rgba())
        frame = Image.fromarray(buffer[..., :3].copy())
        frames.append(frame)
    return frames


def save_gif(outfile: Path, frames: Sequence[Image.Image], fps: int) -> None:
    duration_ms = int(1000 / fps)
    if imageio is not None:
        imageio.mimsave(outfile, frames, duration=duration_ms / 1000.0)
    else:
        first, *rest = frames
        first.save(outfile, save_all=True, append_images=rest, duration=duration_ms, loop=0)
    log("INFO", f"Saved GIF: {outfile}")


def save_mp4(outfile: Path, frames: Sequence[Image.Image], fps: int) -> None:
    if imageio is None:
        log("WARN", "imageio not available – MP4 skipped")
        return
    frames_np = [np.array(frame) for frame in frames]
    try:
        with imageio.get_writer(
            outfile,
            fps=fps,
            codec="libx264",
            format="FFMPEG",
            macro_block_size=None,
        ) as writer:
            for arr in frames_np:
                writer.append_data(arr)
    except Exception as exc:  # pragma: no cover
        log("WARN", f"FFMPEG writer failed ({exc}); attempting fallback")
        imageio.mimsave(outfile, frames_np, fps=fps, codec="libx264", format="FFMPEG")
    log("INFO", f"Saved MP4: {outfile}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SSZ cosmology animator")
    parser.add_argument("--data-dir", type=Path, default=Path("/mnt/data"))
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--model", type=str, choices=["A", "B"], default=None)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--outfile", type=Path, default=None)
    parser.add_argument("--mp4-outfile", type=Path, default=None)
    parser.add_argument("--dpi", type=int, default=160)
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    setup_stdout_utf8()
    args = parse_args()

    summary_path = args.summary or (args.data_dir / "summary.json")
    summary = load_summary(summary_path)
    model_key = args.model or summary.get("model", "A")

    engine, background, extra = build_engine(model_key, summary)

    repo = DataRepository(args.data_dir)
    sn_df, sn_meta = repo.load_sn()
    bao_df, bao_meta = repo.load_bao()
    fs8_df, fs8_meta = repo.load_fs8()

    sn_arr = sn_df[["z", "mu", "mu_err"]].to_numpy(dtype=float) if not sn_df.empty else np.empty((0, 3))
    bao_cols = [col for col in ["z", "DV_by_rd", "err"] if col in bao_df.columns]
    bao_arr = bao_df[bao_cols].to_numpy(dtype=float) if bao_cols else np.empty((0, 3))
    fs8_arr = fs8_df[["z", "fs8", "err"]].to_numpy(dtype=float) if not fs8_df.empty else np.empty((0, 3))

    z_sn = np.linspace(0.01, max(1.8, sn_arr[:, 0].max() + 0.2 if sn_arr.size else 1.8), 280)
    z_bao = np.linspace(0.05, max(2.0, bao_arr[:, 0].max() + 0.2 if bao_arr.size else 2.0), 220)
    z_fs8 = np.linspace(0.0, max(1.2, fs8_arr[:, 0].max() + 0.1 if fs8_arr.size else 1.2), 200)

    theory = {
        "sn_z": z_sn,
        "sn_mu": distance_modulus(engine, z_sn),
        "bao_z": z_bao,
        "bao_dv": bao_dv_by_rd(engine, z_bao),
        "fs8_z": z_fs8,
        "fs8_curve": theory_fs8(engine, z_fs8),
    }

    total_frames = max(int(args.fps * args.seconds), 24)
    storyboard = generate_storyboard(total_frames, sn_arr.shape[0], bao_arr.shape[0], fs8_arr.shape[0])

    fig, axes = init_figure(dpi=args.dpi)
    frames = render_frames(
        fig,
        axes,
        storyboard,
        sn_arr,
        bao_arr,
        fs8_arr,
        theory,
        summary,
        {"sn": sn_meta, "bao": bao_meta, "fs8": fs8_meta},
    )

    outfile = args.outfile or (args.data_dir / "ssz_cosmo_anim.gif")
    mp4_out = args.mp4_outfile or outfile.with_suffix(".mp4")
    save_gif(outfile, frames, args.fps)
    save_mp4(mp4_out, frames, args.fps)


if __name__ == "__main__":
    main()
