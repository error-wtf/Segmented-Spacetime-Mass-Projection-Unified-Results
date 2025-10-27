#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ssz_animator.py
===================

Animated proof visualization for Segmented Space-Time (SSZ) stability sweeps.
Builds a 1280×720 GIF combining heatmap, boundary curves, disagreement map,
and amplitude evolution derived from existing CSV/JSON artefacts.

Usage
-----
python ssz_animator.py --data-dir /mnt/data --prefix v6

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations



import argparse
import io
import json
import math
import sys
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize

try:  # optional import
    import imageio.v2 as imageio  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    imageio = None

from PIL import Image

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_DATA_DIR = Path("/mnt/data")
DEFAULT_PREFIX = "v6"
DEFAULT_FPS = 15
DEFAULT_SECONDS = 12.0
DEFAULT_DPI = 140
DEFAULT_ROUNDTRIPS = 50
DEFAULT_SEED = 42
FIG_SIZE = (12.8, 7.2)

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

def setup_stdout_utf8() -> None:
    """Ensure stdout can emit UTF-8 characters on Windows consoles."""

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
# Data discovery and loading
# ---------------------------------------------------------------------------

def discover_files(data_dir: Path, prefix: str, fallback_order: Sequence[str]) -> Dict[str, Optional[Path]]:
    """Locate artefact files, applying fallback prefixes if necessary."""

    candidates = [prefix, *[p for p in fallback_order if p != prefix]]
    artefacts = {"results": None, "boundaries": None, "summary": None, "heatmap_png": None,
                 "disagreement_png": None, "boundary_png": None}

    for key, stem, ext in [
        ("results", "proof_sweep_results", ".csv"),
        ("boundaries", "stability_boundaries", ".csv"),
        ("summary", "proof_sweep_summary", ".json"),
    ]:
        for pref in candidates:
            path = data_dir / f"{stem}_{pref}{ext}"
            if path.exists():
                artefacts[key] = path
                artefacts.setdefault("resolved_prefix", pref)
                break

    resolved = artefacts.get("resolved_prefix", prefix)
    for name, stem in [("heatmap_png", "heatmap_stability_uniform"),
                       ("disagreement_png", "disagreement_map_uniform"),
                       ("boundary_png", "boundary_lambdaA_vs_Omega0")]:
        png_path = data_dir / f"{stem}_{resolved}.png"
        if png_path.exists():
            artefacts[name] = png_path

    artefacts.setdefault("resolved_prefix", resolved)
    return artefacts


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        lower = col.lower()
        if lower in {"k", "segments"}:
            rename_map[col] = "K"
        elif "lambda" in lower:
            rename_map[col] = "lambda_A"
        elif lower in {"omega0", "omega_0", "Ω0".lower()}:
            rename_map[col] = "Omega0"
    if "K" not in rename_map and "K" in df.columns:
        rename_map["K"] = "K"
    df = df.rename(columns=rename_map)
    return df


def load_grid(path: Optional[Path]) -> Optional[pd.DataFrame]:
    if path is None:
        return None
    try:
        df = pd.read_csv(path)
        df = _normalise_columns(df)
        if "K" not in df.columns or "lambda_A" not in df.columns:
            log("WARN", f"Grid CSV {path} lacks K/lambda_A columns")
            return None
        if "stable_direct" not in df.columns:
            if "logG" in df.columns:
                df["stable_direct"] = df["logG"].astype(float) <= 0.0
            else:
                log("WARN", f"Grid CSV {path} missing stable_direct and logG")
                df["stable_direct"] = False
        else:
            df["stable_direct"] = df["stable_direct"].astype(bool)
        if "stable_criterion" in df.columns:
            df["stable_criterion"] = df["stable_criterion"].astype(bool)
        return df
    except Exception as exc:  # pragma: no cover - defensive
        log("WARN", f"Failed to load grid CSV {path}: {exc}")
        return None


def load_boundaries(path: Optional[Path]) -> Optional[pd.DataFrame]:
    if path is None:
        return None
    try:
        df = pd.read_csv(path)
        df = _normalise_columns(df)
        expected = ["Omega0", "lambdaA_crit_direct", "lambdaA_crit_criterion"]
        missing = [col for col in expected if col not in df.columns]
        if missing:
            log("WARN", f"Boundary CSV {path} missing columns {missing}")
        return df
    except Exception as exc:  # pragma: no cover
        log("WARN", f"Failed to load boundaries CSV {path}: {exc}")
        return None


def load_summary(path: Optional[Path]) -> Optional[Dict]:
    if path is None:
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # pragma: no cover
        log("WARN", f"Failed to load summary JSON {path}: {exc}")
        return None

# ---------------------------------------------------------------------------
# Computations
# ---------------------------------------------------------------------------

def _resample_grid(df: pd.DataFrame, max_size: int = 128) -> pd.DataFrame:
    unique_k = np.unique(df["K"])
    unique_lambda = np.unique(df["lambda_A"])
    if len(unique_k) <= max_size and len(unique_lambda) <= max_size:
        return df
    sampled_k = np.linspace(unique_k.min(), unique_k.max(), min(len(unique_k), max_size))
    sampled_lambda = np.linspace(unique_lambda.min(), unique_lambda.max(), min(len(unique_lambda), max_size))
    df_resampled = []
    for k in sampled_k:
        closest_k = unique_k[np.abs(unique_k - k).argmin()]
        slice_k = df[df["K"] == closest_k]
        if slice_k.empty:
            continue
        for lam in sampled_lambda:
            closest_l = unique_lambda[np.abs(unique_lambda - lam).argmin()]
            cell = slice_k[slice_k["lambda_A"] == closest_l]
            if cell.empty:
                continue
            df_resampled.append(cell.iloc[0])
    if not df_resampled:
        return df
    return pd.DataFrame(df_resampled)


def compute_maps(df: pd.DataFrame) -> Dict:
    df = _resample_grid(df)
    df = df.copy()
    if "segment_mode" in df.columns:
        df["segment_mode"] = df["segment_mode"].astype(str).str.lower()
    grid = df.groupby(["K", "lambda_A"], as_index=False).agg(
        frac_stable=("stable_direct", "mean"),
        count=("stable_direct", "size"),
    )
    frac_pivot = grid.pivot(index="K", columns="lambda_A", values="frac_stable").sort_index()
    disagree_pivot = None
    agreement_ratio = None
    if "stable_criterion" in df.columns:
        df["disagree"] = (df["stable_direct"] != df["stable_criterion"]).astype(float)
        disagree_grid = df.groupby(["K", "lambda_A"], as_index=False).agg(
            disagree=("disagree", "mean"),
        )
        disagree_pivot = disagree_grid.pivot(index="K", columns="lambda_A", values="disagree").sort_index()
        agreement_ratio = float((df["stable_direct"] == df["stable_criterion"]).mean())
    log_stats = None
    if "logG" in df.columns:
        log_stats = {
            "min": float(df["logG"].min()),
            "median": float(df["logG"].median()),
            "max": float(df["logG"].max()),
        }
    modes_present = sorted(df["segment_mode"].unique()) if "segment_mode" in df.columns else ["both"]
    return {
        "frac": frac_pivot,
        "disagree": disagree_pivot,
        "agreement_ratio": agreement_ratio,
        "log_stats": log_stats,
        "modes": modes_present,
        "df": df,
    }


def amp_trace_from_logG(logg: float, n_roundtrips: int = DEFAULT_ROUNDTRIPS, A0: float = 1.0) -> np.ndarray:
    logg = float(logg)
    trace = np.empty(n_roundtrips + 1)
    trace[0] = A0
    factor = math.exp(logg)
    for i in range(1, n_roundtrips + 1):
        trace[i] = trace[i - 1] * factor
        trace[i] = min(max(trace[i], 1e-12), 1e12)
    return trace

# ---------------------------------------------------------------------------
# Storyboard generation
# ---------------------------------------------------------------------------

@dataclass
class FrameState:
    index: int
    total: int
    mode: str
    lambda_value: float
    k_value: float
    frac_slice: np.ndarray
    disagree_slice: Optional[np.ndarray]
    boundary_progress: float
    boundary_direct: Optional[Tuple[np.ndarray, np.ndarray]]
    boundary_criterion: Optional[Tuple[np.ndarray, np.ndarray]]
    logg_value: float
    agreement_ratio: Optional[float]
    log_stats: Optional[Dict[str, float]]


def make_storyboard(stats: Dict, boundaries: Optional[pd.DataFrame], rng: np.random.Generator,
                    frames: int, modes: Sequence[str], mode_filter: str) -> List[FrameState]:
    frac = stats["frac"].copy()
    disagree = stats["disagree"]
    lambda_vals = frac.columns.values.astype(float)
    k_vals = frac.index.values.astype(float)
    frac_array = frac.values
    disagree_array = disagree.values if disagree is not None else None

    indices = list(range(frames))
    rng.shuffle(indices)

    boundary_direct = None
    boundary_criterion = None
    if boundaries is not None and not boundaries.empty:
        bd = boundaries
        if "segment_mode" in bd.columns:
            bd["segment_mode"] = bd["segment_mode"].astype(str).str.lower()
            if mode_filter in {"uniform", "weighted"}:
                bd = bd[bd["segment_mode"] == mode_filter]
        if "lambdaA_crit_direct" in bd.columns:
            boundary_direct = (bd["Omega0"].values, bd["lambdaA_crit_direct"].values)
        if "lambdaA_crit_criterion" in bd.columns:
            boundary_criterion = (bd["Omega0"].values, bd["lambdaA_crit_criterion"].values)

    storyboard: List[FrameState] = []
    total = len(indices)
    for frame_idx, idx in enumerate(indices):
        frac_row = frac_array[idx % frac_array.shape[0]]
        lam_idx = idx % len(lambda_vals)
        lam_val = float(lambda_vals[lam_idx])
        k_val = float(k_vals[idx % len(k_vals)])
        logg_value = 0.0
        if "logG" in stats["df"].columns:
            subset = stats["df"][(stats["df"]["lambda_A"] == lam_val) & (stats["df"]["K"] == k_val)]
            if not subset.empty:
                logg_value = float(subset["logG"].median())
        mode_choice = mode_filter
        if mode_filter == "both" and "segment_mode" in stats["df"].columns:
            subset_modes = stats["df"][stats["df"]["lambda_A"] == lam_val]
            if not subset_modes.empty:
                mode_choice = str(subset_modes.iloc[0].get("segment_mode", "both"))
        state = FrameState(
            index=frame_idx,
            total=total,
            mode=mode_choice,
            lambda_value=lam_val,
            k_value=k_val,
            frac_slice=frac_row,
            disagree_slice=disagree_array[idx % disagree_array.shape[0]] if disagree_array is not None else None,
            boundary_progress=(frame_idx + 1) / total,
            boundary_direct=boundary_direct,
            boundary_criterion=boundary_criterion,
            logg_value=logg_value,
            agreement_ratio=stats.get("agreement_ratio"),
            log_stats=stats.get("log_stats"),
        )
        storyboard.append(state)
    return storyboard

# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def init_figure(boundaries: bool = True, dpi: int = DEFAULT_DPI) -> Tuple[plt.Figure, Dict[str, matplotlib.axes.Axes]]:
    fig = plt.figure(figsize=FIG_SIZE, dpi=dpi)
    fig_w, fig_h = fig.get_size_inches()
    scale = (fig_w * fig_h) / 20.0
    base = max(8.0, min(16.0, 1.4 * scale))
    plt.rcParams.update({
        "font.size": base,
        "axes.titlesize": base + 1,
        "axes.labelsize": base,
        "xtick.labelsize": max(base - 2, 6),
        "ytick.labelsize": max(base - 2, 6),
        "legend.fontsize": max(base - 2, 6),
        "figure.titlesize": base + 2,
    })
    gs = GridSpec(
        2,
        2,
        figure=fig,
        width_ratios=[2.2, 1.0],
        height_ratios=[1.4, 1.0],
        wspace=0.28,
        hspace=0.35,
    )
    heat_ax = fig.add_subplot(gs[0, 0])
    amp_ax = fig.add_subplot(gs[1, 0])
    boundary_ax = fig.add_subplot(gs[0, 1]) if boundaries else None
    disagree_ax = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_axes([0.72, 0.08, 0.25, 0.3])
    ax_info.axis("off")
    return fig, {
        "heat": heat_ax,
        "boundary": boundary_ax,
        "disagree": disagree_ax,
        "amp": amp_ax,
        "info": ax_info,
        "base_font": base,
    }


def update_frame(fig: plt.Figure, axes: Dict[str, matplotlib.axes.Axes], state: FrameState,
                 frac_pivot: pd.DataFrame, disagree_pivot: Optional[pd.DataFrame],
                 amp_roundtrips: int) -> None:
    heat_ax = axes["heat"]
    heat_ax.clear()
    frac_data = frac_pivot.values
    extent = [frac_pivot.columns.min(), frac_pivot.columns.max(), frac_pivot.index.min(), frac_pivot.index.max()]
    im = heat_ax.imshow(frac_data, origin="lower", aspect="auto", cmap="viridis", vmin=0.0, vmax=1.0,
                        extent=extent)
    heat_ax.set_xlabel("λ_A")
    heat_ax.set_ylabel("K")
    heat_ax.set_title("Fraction stable (direct)")
    cbar = fig.colorbar(im, ax=heat_ax, pad=0.02, shrink=0.92)
    base = axes.get("base_font", 12.0)
    cbar.ax.tick_params(labelsize=max(base - 2, 6))
    heat_ax.axvline(state.lambda_value, color="white", linestyle="--", linewidth=1.0)
    heat_ax.axhline(state.k_value, color="white", linestyle="--", linewidth=1.0)

    disagree_ax = axes["disagree"]
    disagree_ax.clear()
    if disagree_pivot is not None:
        dis_data = disagree_pivot.values
        extent_dis = [disagree_pivot.columns.min(), disagree_pivot.columns.max(),
                      disagree_pivot.index.min(), disagree_pivot.index.max()]
        im2 = disagree_ax.imshow(dis_data, origin="lower", aspect="auto", cmap="magma",
                                 vmin=0.0, vmax=1.0, extent=extent_dis)
        disagree_ax.set_title("Disagreement ratio")
        disagree_ax.set_xlabel("λ_A")
        disagree_ax.set_ylabel("K")
        cbar2 = fig.colorbar(im2, ax=disagree_ax, pad=0.02, shrink=0.9)
        cbar2.ax.tick_params(labelsize=max(base - 2, 6))
    else:
        disagree_ax.set_title("Disagreement ratio (n/a)")
        disagree_ax.text(0.5, 0.5, "no criterion data", ha="center", va="center", transform=disagree_ax.transAxes)
        disagree_ax.set_xticks([])
        disagree_ax.set_yticks([])

    amp_ax = axes["amp"]
    amp_ax.clear()
    trace = amp_trace_from_logG(state.logg_value, n_roundtrips=amp_roundtrips)
    amp_ax.plot(trace, color="tab:blue")
    amp_ax.axhline(1.0, color="tab:gray", linestyle=":")
    amp_ax.set_yscale("log")
    amp_ax.set_ylim(1e-6, 1e12)
    amp_ax.set_xlabel("Roundtrip n")
    amp_ax.set_ylabel("Amplitude A_n")
    title = "Amplitude evolution"
    if state.logg_value > 0:
        title += " — WARN: logG > 0"
    amp_ax.set_title(title, color="tab:red" if state.logg_value > 0 else "black")

    boundary_ax = axes.get("boundary")
    if boundary_ax is not None:
        boundary_ax.clear()
        boundary_ax.set_title("λ_A,crit vs Ω0")
        boundary_ax.set_xlabel("Ω0")
        boundary_ax.set_ylabel("λ_A,crit")
        progress = state.boundary_progress
        if state.boundary_direct is not None:
            x, y = state.boundary_direct
            max_idx = max(1, int(len(x) * progress))
            boundary_ax.plot(x[:max_idx], y[:max_idx], "o-", label="direct")
        if state.boundary_criterion is not None:
            x, y = state.boundary_criterion
            max_idx = max(1, int(len(x) * progress))
            boundary_ax.plot(x[:max_idx], y[:max_idx], "s--", label="criterion")
        if state.boundary_direct is None and state.boundary_criterion is None:
            boundary_ax.text(0.5, 0.5, "no boundary data", ha="center", va="center",
                             transform=boundary_ax.transAxes)
        handles, labels = boundary_ax.get_legend_handles_labels()
        if handles:
            boundary_ax.legend(handles, labels, loc="lower right")

    header_text = f"SSZ Animator — λ_A={state.lambda_value:.3f}, K={state.k_value:.1f}"
    fig.suptitle(header_text, y=0.97, fontweight="bold")

    stats_lines = [
        f"Frame {state.index + 1}/{state.total} ({(state.index + 1)/state.total*100:5.1f}%)",
    ]
    if state.agreement_ratio is not None:
        stats_lines.append(f"Übereinstimmung: {state.agreement_ratio:.3f}")
    if state.log_stats:
        stats_lines.extend(
            [
                f"logG min {state.log_stats['min']:.2f}",
                f"logG median {state.log_stats['median']:.2f}",
                f"logG max {state.log_stats['max']:.2f}",
            ]
        )
    params_left = [
        f"λ_A = {state.lambda_value:.4f}",
        f"K = {state.k_value:.3f}",
        f"logG = {state.logg_value:.3f}",
    ]
    params_right = [
        f"Mode = {state.mode}",
        f"Runden = {amp_roundtrips}",
        f"Total Frames = {state.total}",
    ]
    info_ax = axes.get("info")
    if info_ax is not None:
        info_ax.clear()
        info_ax.axis("off")
        info_ax.text(
            0.0,
            1.0,
            "\n".join(stats_lines),
            ha="left",
            va="top",
            fontsize=max(base - 1, 7),
            linespacing=1.25,
        )
        info_ax.text(
            0.0,
            0.55,
            "\n".join(params_left),
            ha="left",
            va="top",
            fontsize=max(base - 1, 7),
            linespacing=1.2,
        )
        info_ax.text(
            0.55,
            0.55,
            "\n".join(params_right),
            ha="left",
            va="top",
            fontsize=max(base - 1, 7),
            linespacing=1.2,
        )

# ---------------------------------------------------------------------------
# GIF rendering
# ---------------------------------------------------------------------------

def render_frames(fig: plt.Figure, axes: Dict[str, matplotlib.axes.Axes], storyboard: Sequence[FrameState],
                  frac_pivot: pd.DataFrame, disagree_pivot: Optional[pd.DataFrame],
                  amp_roundtrips: int, fps: int) -> Tuple[List[Image.Image], List[float]]:
    frames: List[Image.Image] = []
    for state in storyboard:
        update_frame(fig, axes, state, frac_pivot, disagree_pivot, amp_roundtrips)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        buffer = np.asarray(renderer.buffer_rgba())
        image = buffer[..., :3].copy()
        frames.append(Image.fromarray(image))

    tick_times = [index / float(fps) for index in range(len(frames))]
    return frames, tick_times


def _write_gif(outfile: Path, frames: Sequence[Image.Image], fps: int, tick_metadata: Sequence[float]) -> None:
    duration_ms = int(1000 / fps)

    if imageio is not None:
        meta = {"duration": duration_ms / 1000.0, "tick_times": list(tick_metadata)}
        imageio.mimsave(outfile, frames, duration=duration_ms / 1000.0, metadata=meta)
    else:
        first, *rest = frames
        info = first.info.copy()
        info["duration"] = duration_ms
        info["loop"] = 0
        info["comment"] = str(tick_metadata).encode("utf-8")
        first.save(outfile, save_all=True, append_images=rest, **info)
    log("INFO", f"Saved GIF: {outfile}")


def _generate_metronome_wav(path: Path, fps: int, frame_count: int, sample_rate: int = 44100,
                            tick_freq: float = 880.0, tick_duration: float = 0.05) -> List[float]:
    beat_times: List[float] = []
    total_samples = int(frame_count * sample_rate / fps)
    data = np.zeros(total_samples, dtype=np.float32)

    tick_samples = int(sample_rate * tick_duration)
    t = np.linspace(0, tick_duration, tick_samples, endpoint=False)
    envelope = np.linspace(1.0, 0.0, tick_samples)
    tick_wave = 0.2 * np.sin(2 * np.pi * tick_freq * t) * envelope

    for frame_idx in range(frame_count):
        start_sample = int(frame_idx * sample_rate / fps)
        end_sample = min(start_sample + tick_samples, total_samples)
        data[start_sample:end_sample] += tick_wave[: end_sample - start_sample]
        beat_times.append(frame_idx / float(fps))

    max_val = np.max(np.abs(data))
    if max_val > 0:
        data /= max_val

    pcm = (data * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wav_writer:
        wav_writer.setnchannels(1)
        wav_writer.setsampwidth(2)
        wav_writer.setframerate(sample_rate)
        wav_writer.writeframes(pcm.tobytes())

    log("INFO", f"Saved metronome WAV: {path}")
    return beat_times


def _write_mp4(outfile: Path, frames: Sequence[Image.Image], audio_wav: Path, fps: int) -> None:
    if imageio is None:
        log("WARN", "imageio not available; MP4 export skipped")
        return

    frames_np = [np.array(frame) for frame in frames]
    try:
        with imageio.get_writer(
            outfile,
            fps=fps,
            codec="libx264",
            format="FFMPEG",
            macro_block_size=None,
            audio_path=str(audio_wav),
        ) as writer:
            for frame_arr in frames_np:
                writer.append_data(frame_arr)
    except TypeError:
        imageio.mimsave(
            outfile,
            frames_np,
            fps=fps,
            codec="libx264",
            format="FFMPEG",
        )
    log("INFO", f"Saved MP4: {outfile}")

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SSZ proof animation generator")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--prefix", type=str, default=DEFAULT_PREFIX)
    parser.add_argument("--mode", type=str, choices=["both", "uniform", "weighted"], default="both")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--seconds", type=float, default=DEFAULT_SECONDS)
    parser.add_argument("--outfile", type=str, default=None)
    parser.add_argument("--mp4-outfile", type=str, default=None)
    parser.add_argument("--audio-outfile", type=str, default=None)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    parser.add_argument("--no-boundary", action="store_true")
    parser.add_argument("--roundtrips", type=int, default=DEFAULT_ROUNDTRIPS)
    return parser.parse_args()


def main() -> None:
    setup_stdout_utf8()
    args = parse_args()
    outfile = Path(args.outfile) if args.outfile else args.data_dir / f"ssz_proof_anim_{args.prefix}.gif"
    mp4_out = Path(args.mp4_outfile) if args.mp4_outfile else outfile.with_suffix(".mp4")
    audio_out = Path(args.audio_outfile) if args.audio_outfile else outfile.with_suffix(".wav")
    artefacts = discover_files(args.data_dir, args.prefix, ("v6", "v5", "v4"))
    resolved_prefix = artefacts.get("resolved_prefix", args.prefix)

    df_grid = load_grid(artefacts.get("results"))
    if df_grid is None:
        log("ERROR", "No grid data available; cannot render animation")
        return

    if args.mode in {"uniform", "weighted"} and "segment_mode" in df_grid.columns:
        df_grid = df_grid[df_grid["segment_mode"].astype(str).str.lower() == args.mode]
        if df_grid.empty:
            log("WARN", f"No rows for mode {args.mode}, falling back to both")
            df_grid = load_grid(artefacts.get("results"))

    boundaries = None if args.no_boundary else load_boundaries(artefacts.get("boundaries"))
    summary = load_summary(artefacts.get("summary"))
    stats = compute_maps(df_grid)

    rng = np.random.default_rng(args.seed)
    total_frames = int(max(1, args.fps * args.seconds))
    storyboard = make_storyboard(stats, boundaries, rng, total_frames, stats["modes"], args.mode)

    fig, axes = init_figure(boundaries=boundaries is not None and not args.no_boundary, dpi=args.dpi)
    frames, tick_times = render_frames(fig, axes, storyboard, stats["frac"], stats["disagree"], args.roundtrips, args.fps)

    beats = _generate_metronome_wav(audio_out, args.fps, len(frames))
    _write_gif(outfile, frames, args.fps, beats)
    _write_mp4(mp4_out, frames, audio_out, args.fps)


if __name__ == "__main__":
    main()
