#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python renderer for Big Bang vs. SSZ comparison animation.

Generates both GIF and MP4 (with audio) outputs using matplotlib + imageio.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import math
import shutil
import subprocess
import sys
import tempfile
import textwrap
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


from PIL import Image

try:
    import imageio.v2 as imageio  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    imageio = None


# ---------------------------------------------------------------------------
# Utilities
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


def smoothstep(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def smootherstep(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


# ---------------------------------------------------------------------------
# Frame state and animation helpers
# ---------------------------------------------------------------------------


def _make_grid(resolution: int = 720, span: Tuple[float, float] = (-1.8, 1.8)) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lin = np.linspace(span[0], span[1], resolution)
    xx, yy = np.meshgrid(lin, lin)
    rr = np.sqrt(xx ** 2 + yy ** 2)
    return xx, yy, rr


GRID_LEFT = _make_grid(640, (-1.6, 1.6))
GRID_RIGHT = _make_grid(640, (-2.2, 2.2))


FIG_PIXEL_WIDTH = 1920
FIG_PIXEL_HEIGHT = 1080

PANEL_LEFT = dict(x=0.0, y=54 / FIG_PIXEL_HEIGHT, width=900 / FIG_PIXEL_WIDTH, height=972 / FIG_PIXEL_HEIGHT)
PANEL_RIGHT = dict(x=1020 / FIG_PIXEL_WIDTH, y=54 / FIG_PIXEL_HEIGHT, width=900 / FIG_PIXEL_WIDTH, height=972 / FIG_PIXEL_HEIGHT)
DIVIDER = dict(x=900 / FIG_PIXEL_WIDTH, y=54 / FIG_PIXEL_HEIGHT, width=20 / FIG_PIXEL_WIDTH, height=972 / FIG_PIXEL_HEIGHT)
FOOTER = dict(x=0.0, y=0.0, width=1.0, height=54 / FIG_PIXEL_HEIGHT)

SAFE_INSET_X_FRAC = 40.0 / 900.0
SAFE_INSET_Y_FRAC = 40.0 / 936.0

TITLE_FONT_RANGE = (46, 56)
H2_FONT_RANGE = (30, 36)
BODY_FONT_RANGE = (22, 26)
CAPTION_FONT_RANGE = (18, 20)

TEXT_MAX_WIDTH_FRAC = 0.68
TEXT_MARGIN_PX = 24.0
TEXT_PAD_PX = 16.0
TEXT_MAX_LINES = 12
TEXT_MAX_CHARS = 420
TEXT_DEFAULT_LINE_HEIGHT = 1.18
TEXT_MIN_LINE_HEIGHT = 1.08

LANGUAGE_PROFILES: Dict[str, Dict[str, object]] = {
    "de": {
        "left_phase_a": (
            "Klassisches ΛCDM-Modell\n"
            "• Ursprung als Singularität (∞-Dichte)\n"
            "• ‘Explosion’ erzeugt Raum, Zeit, Materie\n"
            "• Temperatur fällt mit Expansion"
        ),
        "left_phase_b": (
            "Klassisches ΛCDM-Modell\n"
            "• Unendliche Dichte → mathematische Singularität\n"
            "• Energie breitet sich radial aus\n"
            "• Galaxien entstehen in expandierendem Raum"
        ),
        "right_phase_a": (
            "Segmentierte Raumzeit (SSZ)\n"
            "• Geordnete Ursprungsschicht, keine Singularität\n"
            "• Raum entsteht durch Segmentierung\n"
            "• Expansion = Entfaltung, Resonanz-getrieben"
        ),
        "right_phase_b": (
            "Segmentierte Raumzeit (SSZ)\n"
            "• Segmentierter Ursprung → endliche Dichten\n"
            "• Pulsierende Resonanz erzeugt Raum & Zeit\n"
            "• Geometrische Ordnung bewahrt Stabilität"
        ),
        "left_foot": "Unendliche Dichte – Anfangspunkt des klassischen Big Bang",
        "right_foot": "Segmentierter Ursprung – Expansion aus geordneter Struktur",
        "footer_title": "Von der Singularität zur Segmentierung",
        "footer_subtitle": "Zwei Anfänge des Universums – ΛCDM vs. SSZ",
        "voice_schedule": [
            (0.8, "Links sehen wir das klassische Modell – ein Universum aus einer unendlichen Singularität geboren."),
            (6.5, "Doch die Mathematik der segmentierten Raumzeit zeigt: Unendliche Dichte kann es nicht geben."),
            (12.5, "Stattdessen entsteht Raum durch Segmentierung – nicht durch Explosion, sondern durch Entfaltung."),
            (18.0, "Jeder Abschnitt wächst aus Ordnung heraus – stabil, endlich und voller Potenzial für Leben."),
        ],
    },
    "en": {
        "left_phase_a": (
            "Classical ΛCDM Model\n"
            "• Origin as singularity (infinite density)\n"
            "• “Explosion” births space, time, matter\n"
            "• Temperature falls as the universe expands"
        ),
        "left_phase_b": (
            "Classical ΛCDM Model\n"
            "• Infinite density → mathematical singularity\n"
            "• Energy radiates outward\n"
            "• Galaxies emerge within expanding space"
        ),
        "right_phase_a": (
            "Segmented Spacetime (SSZ)\n"
            "• Ordered origin layer, no singularity\n"
            "• Space emerges through segmentation\n"
            "• Expansion = resonance-driven unfolding"
        ),
        "right_phase_b": (
            "Segmented Spacetime (SSZ)\n"
            "• Segmented origin → finite densities\n"
            "• Pulsing resonance generates space & time\n"
            "• Geometric order preserves stability"
        ),
        "left_foot": "Infinite density – starting point of the classical Big Bang",
        "right_foot": "Segmented origin – expansion from structured order",
        "footer_title": "From Singularity to Segmentation",
        "footer_subtitle": "Two beginnings of the universe – ΛCDM vs. SSZ",
        "voice_schedule": [
            (0.8, "On the left we see the classical model – a universe born from an infinite singularity."),
            (6.5, "Yet segmented spacetime mathematics shows that infinite density cannot exist."),
            (12.5, "Instead, space unfolds through segmentation – not an explosion, but an emergence."),
            (18.0, "Each region grows from ordered structure – stable, finite, full of potential for life."),
        ],
    },
    "it": {
        "left_phase_a": (
            "Modello ΛCDM classico\n"
            "• Origine come singolarità (densità infinita)\n"
            "• La “esplosione” genera spazio, tempo e materia\n"
            "• La temperatura cala con l’espansione"
        ),
        "left_phase_b": (
            "Modello ΛCDM classico\n"
            "• Densità infinita → singolarità matematica\n"
            "• L’energia si propaga radialmente\n"
            "• Le galassie nascono nello spazio in espansione"
        ),
        "right_phase_a": (
            "Spazio-tempo segmentato (SSZ)\n"
            "• Strato d’origine ordinato, nessuna singolarità\n"
            "• Lo spazio emerge per segmentazione\n"
            "• Espansione = dispiegarsi guidato da risonanza"
        ),
        "right_phase_b": (
            "Spazio-tempo segmentato (SSZ)\n"
            "• Origine segmentata → densità finite\n"
            "• La risonanza pulsante genera spazio e tempo\n"
            "• L’ordine geometrico preserva la stabilità"
        ),
        "left_foot": "Densità infinita – punto di partenza del Big Bang classico",
        "right_foot": "Origine segmentata – espansione da una struttura ordinata",
        "footer_title": "Dalla Singolarità alla Segmentazione",
        "footer_subtitle": "Due origini dell’universo – ΛCDM vs. SSZ",
        "voice_schedule": [
            (0.8, "A sinistra vediamo il modello classico: un universo nato da una singolarità infinita."),
            (6.5, "Ma la matematica dello spazio-tempo segmentato mostra che una densità infinita non può esistere."),
            (12.5, "Lo spazio nasce dalla segmentazione: non un’esplosione, ma un dispiegarsi ordinato."),
            (18.0, "Ogni regione cresce dall’ordine – stabile, finita e ricca di potenziale per la vita."),
        ],
    },
}

VOICE_SAMPLE_RATE = 44100

np.random.seed(42)
GALAXY_POS = np.random.normal(scale=0.55, size=(1600, 2))
GALAXY_POS /= np.maximum(1.0, np.linalg.norm(GALAXY_POS, axis=1, keepdims=True))
GALAXY_POS *= np.random.uniform(0.05, 1.4, size=(1600, 1))

np.random.seed(24)
PARTICLE_COUNT = 900
PARTICLE_RADIAL = np.linspace(0.35, 3.2, PARTICLE_COUNT)
PARTICLE_PHASE = np.random.uniform(0.0, 2.0 * np.pi, PARTICLE_COUNT)


@dataclass
class AnimationConfig:
    duration: float = 25.0
    fps: int = 30
    dpi: int = 160
    figsize: Tuple[float, float] = (12.0, 6.75)  # 1920x1080 at 160 dpi
    outdir: Path = Path("/mnt/data")
    basename: str = "ssz_vs_bigbang"
    language: str = "de"

    @property
    def total_frames(self) -> int:
        return int(self.duration * self.fps)

    @property
    def profile(self) -> Dict[str, object]:
        return LANGUAGE_PROFILES.get(self.language, LANGUAGE_PROFILES["de"])


def _bigbang_field(t_norm: float) -> np.ndarray:
    x, y, r = GRID_LEFT
    collapse = smoothstep(1.0 - min(t_norm / 0.12, 1.0))
    expansion = smootherstep(max(t_norm - 0.08, 0.0) / 0.92)
    radius = 0.1 + 1.6 * expansion
    envelope = np.exp(-((r / radius) ** 2))
    ripple = 0.35 * np.sin((r * (6.0 + 6.0 * expansion) - t_norm * 12.0) * np.pi) * np.exp(-r * 1.4)
    waves = np.maximum(0.0, envelope + ripple)
    heat = np.clip(waves ** 0.8 + collapse * 0.12, 0.0, 1.0)
    return heat


def _ssz_field(t_norm: float) -> np.ndarray:
    x, y, r = GRID_RIGHT
    angle = np.arctan2(y, x)
    unfold = smootherstep(max(t_norm - 0.05, 0.0) / 0.95)
    spiral = np.cos(6.0 * angle + 8.0 * unfold * r)
    radial = np.sin(4.0 * r - unfold * 9.0)
    pattern = 0.55 * (spiral * 0.5 + 0.5) + 0.45 * (radial * 0.5 + 0.5)
    glow = np.clip(pattern ** 1.1 + 0.25 * np.exp(-r * 0.7), 0.0, 1.0)
    gradient = np.clip(0.3 + unfold * (np.sin(angle * 3.0 + unfold * 4.0) * 0.25 + 0.5), 0.0, 1.0)
    return np.clip(glow * gradient, 0.0, 1.0)


def _scale_font_range(range_tuple: Tuple[int, int], scale: float) -> Tuple[int, int]:
    low = max(12, int(round(range_tuple[0] * scale)))
    high = max(low, int(round(range_tuple[1] * scale)))
    return (low, high)


def _wrap_lines(text: str, width: int = 34) -> List[str]:
    lines: List[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            lines.append("")
            continue
        bullet = ""
        payload = stripped
        if stripped[0] in {"•", "-", "–"}:
            parts = stripped.split(maxsplit=1)
            bullet = parts[0]
            payload = parts[1] if len(parts) > 1 else ""
        indent = "  " if bullet else ""
        wrap_width = max(10, width - (2 if bullet else 0))
        wrapped = textwrap.wrap(payload, width=wrap_width, break_long_words=False, break_on_hyphens=True) or [payload]
        for idx, segment in enumerate(wrapped):
            prefix = f"{bullet} " if bullet and idx == 0 else indent
            lines.append(f"{prefix}{segment}" if prefix else segment)
    return lines


def _truncate_lines(lines: List[str], max_lines: int, max_chars: int) -> List[str]:
    trimmed: List[str] = []
    total_chars = 0
    for line in lines:
        if len(trimmed) >= max_lines:
            break
        remaining = max_chars - total_chars
        if remaining <= 0:
            break
        if len(line) <= remaining:
            trimmed.append(line)
            total_chars += len(line)
        else:
            trimmed.append(textwrap.shorten(line, width=max(4, remaining), placeholder="…"))
            total_chars = max_chars
            break
    if not trimmed and lines:
        trimmed.append(textwrap.shorten(lines[0], width=max_chars, placeholder="…"))
    return trimmed


def _fit_text_height(
    lines: List[str],
    font_range: Tuple[int, int],
    panel_pixel_height: float,
    max_height_frac: float = 0.38,
) -> Tuple[int, float, float, List[str]]:
    lines = _truncate_lines(lines, TEXT_MAX_LINES, TEXT_MAX_CHARS)
    if not lines:
        return font_range[0], 0.0, TEXT_DEFAULT_LINE_HEIGHT, []
    height_limit_px = panel_pixel_height * max_height_frac
    line_height = TEXT_DEFAULT_LINE_HEIGHT
    font_size = font_range[1]

    while True:
        size_found = False
        for size in range(font_range[1], font_range[0] - 1, -1):
            line_height = TEXT_DEFAULT_LINE_HEIGHT
            while line_height >= TEXT_MIN_LINE_HEIGHT:
                line_height_px = size * line_height
                total_px = line_height_px * len(lines)
                if total_px <= height_limit_px:
                    return size, total_px, line_height, lines
                line_height -= 0.02
        # reduce text content if still overflowing
        if len(lines) <= 1:
            shortened = textwrap.shorten(lines[0], width=max(8, len(lines[0]) - 4), placeholder="…")
            if shortened == lines[0] or len(shortened) <= 3:
                return font_range[0], height_limit_px, TEXT_MIN_LINE_HEIGHT, [shortened]
            lines = [shortened]
        else:
            lines = lines[:-1]
            lines[-1] = textwrap.shorten(lines[-1], width=max(8, len(lines[-1]) - 4), placeholder="…")
        if not lines:
            return font_range[0], 0.0, TEXT_DEFAULT_LINE_HEIGHT, []
        lines = _truncate_lines(lines, TEXT_MAX_LINES, TEXT_MAX_CHARS)


def _render_text_box(
    ax: plt.Axes,
    text: str,
    anchor: Tuple[float, float],
    width_frac: float,
    pad_x_frac: float,
    pad_y_frac: float,
    font_range: Tuple[int, int],
    panel_pixel_width: float,
    panel_pixel_height: float,
    align: str = "left",
    max_height_frac: float = 0.38,
) -> None:
    lines = _wrap_lines(text)
    font_size, content_height_px, line_height, lines = _fit_text_height(lines, font_range, panel_pixel_height, max_height_frac)
    if not lines:
        return
    content_height_frac = content_height_px / panel_pixel_height
    box_height = content_height_frac + 2 * pad_y_frac
    bbox = FancyBboxPatch(
        (anchor[0], anchor[1] - box_height),
        width_frac,
        box_height,
        transform=ax.transAxes,
        boxstyle="round,pad=0.0",
        linewidth=0.0,
        facecolor=(0.02, 0.02, 0.02, 0.58),
        zorder=5,
    )
    ax.add_patch(bbox)
    content = "\n".join(lines)
    if align == "left":
        text_x = anchor[0] + pad_x_frac
        ha = "left"
    else:
        text_x = anchor[0] + width_frac - pad_x_frac
        ha = "right"
    ax.text(
        text_x,
        anchor[1] - pad_y_frac,
        content,
        transform=ax.transAxes,
        ha=ha,
        va="top",
        fontsize=font_size,
        color="#f4f6ff",
        linespacing=line_height,
        zorder=6,
    )


def _render_footer(
    ax: plt.Axes,
    fig_scale: float,
    panel_pixel_height: float,
    title_text: str,
    subtitle_text: str,
) -> None:
    ax.clear()
    ax.set_axis_off()
    ax.set_facecolor((0.02, 0.03, 0.05, 0.0))
    title_range = _scale_font_range(TITLE_FONT_RANGE, fig_scale)
    caption_range = _scale_font_range(CAPTION_FONT_RANGE, fig_scale)
    title_lines = _wrap_lines(title_text, width=34)
    title_size, _, title_line_height, title_lines = _fit_text_height(title_lines, title_range, panel_pixel_height, max_height_frac=0.9)
    subtitle_lines = _wrap_lines(subtitle_text, width=40)
    subtitle_size, _, subtitle_line_height, subtitle_lines = _fit_text_height(subtitle_lines, caption_range, panel_pixel_height, max_height_frac=0.9)
    subtitle = "\n".join(subtitle_lines)
    ax.text(
        0.5,
        0.74,
        "\n".join(title_lines),
        ha="center",
        va="center",
        fontsize=title_size,
        color="#f4f6ff",
        fontweight="bold",
        linespacing=title_line_height,
    )
    ax.text(
        0.5,
        0.28,
        subtitle,
        ha="center",
        va="center",
        fontsize=subtitle_size,
        color="#cfd6f6",
        linespacing=subtitle_line_height,
    )


def _draw_divider(ax: plt.Axes) -> None:
    ax.clear()
    ax.set_axis_off()
    gradient = np.linspace(0.0, 1.0, 256)
    gradient = np.vstack([gradient, gradient])
    ax.imshow(
        gradient.T,
        cmap=matplotlib.colors.LinearSegmentedColormap.from_list("divider", ["#050505", "#222831"]),
        origin="lower",
        aspect="auto",
        extent=(0, 1, 0, 1),
    )


def _draw_hex_layers(ax: plt.Axes, extent: float, t_norm: float) -> None:
    depth = 12
    base_radius = 0.28 + 0.08 * smootherstep(max(t_norm - 0.05, 0.0) / 0.95)
    for idx in range(depth):
        radius = base_radius + idx * 0.18 + 0.25 * smootherstep(t_norm)
        hex_patch = matplotlib.patches.RegularPolygon(
            (0.0, 0.0),
            numVertices=6,
            radius=radius,
            orientation=np.pi / 6.0,
            edgecolor=(0.94, 0.79, 0.35, 0.22 + 0.03 * idx),
            facecolor=(0, 0, 0, 0),
            linewidth=0.7,
            zorder=4,
        )
        ax.add_patch(hex_patch)



def update_frame(fig: plt.Figure, axes: Dict[str, plt.Axes], frame_idx: int, cfg: AnimationConfig) -> Image.Image:
    progress = frame_idx / max(cfg.total_frames - 1, 1)
    fig.patch.set_facecolor("#050505")

    left_ax = axes["left"]
    right_ax = axes["right"]
    divider_ax = axes["divider"]
    footer_ax = axes["footer"]

    left_ax.cla()
    right_ax.cla()

    # Panel background setup
    for ax in (left_ax, right_ax):
        ax.set_facecolor("#050505")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)

    # Left panel – Big Bang depiction
    collapse = smoothstep(1.0 - min(progress / 0.12, 1.0))
    expansion = smootherstep(max(progress - 0.08, 0.0) / 0.92)
    left_field = _bigbang_field(progress)
    left_ax.imshow(
        left_field,
        cmap="inferno",
        origin="lower",
        extent=(-1.0, 1.0, -1.0, 1.0),
        vmin=0.0,
        vmax=1.0,
        alpha=0.9,
    )
    ripple_alpha = smootherstep(max(progress - 0.08, 0.0) / 0.25)
    contours = left_ax.contour(
        GRID_LEFT[0],
        GRID_LEFT[1],
        left_field,
        levels=[0.25, 0.45, 0.65, 0.85],
        colors=[(1.0, 1.0, 1.0, 0.1 + 0.32 * ripple_alpha)] * 4,
        linewidths=0.6,
    )
    if hasattr(contours, "collections"):
        for line in contours.collections:
            line.set_linestyle("solid")

    # Galaxy particle layer
    particle_activation = smootherstep(max(progress - 0.26, 0.0) / 0.6)
    activations = particle_activation * np.clip((np.linalg.norm(GALAXY_POS, axis=1) - 0.3) / 1.2, 0.0, 1.0)
    size = 5 + 18 * activations
    color = np.column_stack([
        0.95 * (1 - activations) + 0.2 * activations,
        0.85 * (1 - activations) + 0.2 * activations,
        0.55 * (1 - activations) + 0.9 * activations,
        0.35 + 0.4 * activations,
    ])
    left_ax.scatter(
        GALAXY_POS[:, 0],
        GALAXY_POS[:, 1],
        s=size,
        c=color,
        marker="o",
        linewidths=0.0,
        zorder=3,
    )

    # Copy of field for overlay highlight
    burst_radius = 0.06 + expansion * 0.7
    theta = np.linspace(0.0, 2.0 * np.pi, 720)
    left_ax.plot(
        burst_radius * np.cos(theta),
        burst_radius * np.sin(theta),
        color=(1.0, 0.9, 0.6, 0.55 * collapse),
        linewidth=2.2,
        zorder=4,
    )

    profile = cfg.profile
    left_phase_a = profile["left_phase_a"]  # type: ignore[index]
    left_phase_b = profile["left_phase_b"]  # type: ignore[index]
    right_phase_a = profile["right_phase_a"]  # type: ignore[index]
    right_phase_b = profile["right_phase_b"]  # type: ignore[index]
    left_text = left_phase_a if progress < 0.65 else left_phase_b

    # SSZ panel – field + spiral + particles
    unfold = smootherstep(max(progress - 0.05, 0.0) / 0.95)
    right_field = _ssz_field(progress)
    right_ax.imshow(
        right_field,
        cmap="viridis",
        origin="lower",
        extent=(-1.0, 1.0, -1.0, 1.0),
        vmin=0.0,
        vmax=1.0,
        alpha=0.92,
    )

    _draw_hex_layers(right_ax, extent=1.0, t_norm=progress)
    spiral_theta = np.linspace(0.0, 7.0 * np.pi, 1200)
    growth = 0.25 + 0.52 * unfold
    spiral_radius = 0.15 * np.exp(growth * spiral_theta)
    spiral_x = spiral_radius * np.cos(spiral_theta)
    spiral_y = spiral_radius * np.sin(spiral_theta)
    right_ax.plot(
        spiral_x,
        spiral_y,
        color=(0.98, 0.78, 0.21, 0.7),
        linewidth=2.4,
        zorder=6,
    )

    particle_theta = PARTICLE_PHASE + progress * 0.65 + unfold * 1.8
    radial_growth = PARTICLE_RADIAL * (0.4 + 0.6 * smootherstep(max(progress - 0.12, 0.0) / 0.72))
    px = 0.12 * radial_growth * np.cos(particle_theta)
    py = 0.12 * radial_growth * np.sin(particle_theta)
    base_color = np.column_stack([
        0.06 + 0.3 * unfold,
        0.32 + 0.4 * unfold,
        0.8 + 0.15 * unfold,
        0.26 + 0.35 * unfold,
    ])
    right_ax.scatter(
        px,
        py,
        s=8 + 14 * unfold,
        c=base_color,
        marker="h",
        linewidths=0.0,
        alpha=0.85,
        zorder=5,
    )

    right_text = right_phase_a if progress < 0.65 else right_phase_b

    fig_scale = math.sqrt(
        (fig.bbox.width / FIG_PIXEL_WIDTH) * (fig.bbox.height / FIG_PIXEL_HEIGHT)
    )
    body_range = _scale_font_range(BODY_FONT_RANGE, fig_scale)
    panel_pixel_height = PANEL_LEFT["height"] * FIG_PIXEL_HEIGHT
    panel_pixel_width = PANEL_LEFT["width"] * FIG_PIXEL_WIDTH

    safe_x = SAFE_INSET_X_FRAC
    safe_y = SAFE_INSET_Y_FRAC
    margin_x_frac = TEXT_MARGIN_PX / panel_pixel_width
    margin_y_frac = TEXT_MARGIN_PX / panel_pixel_height
    pad_x_frac = TEXT_PAD_PX / panel_pixel_width
    pad_y_frac = TEXT_PAD_PX / panel_pixel_height
    box_width_frac = min(TEXT_MAX_WIDTH_FRAC, 1.0 - 2 * (safe_x + margin_x_frac))

    _render_text_box(
        left_ax,
        left_text,
        anchor=(safe_x + margin_x_frac, 1.0 - safe_y - margin_y_frac),
        width_frac=box_width_frac,
        pad_x_frac=pad_x_frac,
        pad_y_frac=pad_y_frac,
        font_range=body_range,
        panel_pixel_width=panel_pixel_width,
        panel_pixel_height=panel_pixel_height,
    )
    _render_text_box(
        right_ax,
        right_text,
        anchor=(1.0 - safe_x - margin_x_frac - box_width_frac, 1.0 - safe_y - margin_y_frac),
        width_frac=box_width_frac,
        pad_x_frac=pad_x_frac,
        pad_y_frac=pad_y_frac,
        font_range=body_range,
        panel_pixel_width=panel_pixel_width,
        panel_pixel_height=panel_pixel_height,
        align="right",
    )

    # Footnote overlays
    left_ax.text(
        safe_x + margin_x_frac,
        safe_y + margin_y_frac,
        profile["left_foot"],  # type: ignore[index]
        transform=left_ax.transAxes,
        ha="left",
        va="center",
        fontsize=_scale_font_range(H2_FONT_RANGE, fig_scale)[0],
        color="#f4f6ff",
        bbox=dict(facecolor=(0.07, 0.07, 0.12, 0.72), edgecolor="none", pad=6),
    )
    right_ax.text(
        1.0 - safe_x - margin_x_frac,
        safe_y + margin_y_frac,
        profile["right_foot"],  # type: ignore[index]
        transform=right_ax.transAxes,
        ha="right",
        va="center",
        fontsize=_scale_font_range(H2_FONT_RANGE, fig_scale)[0],
        color="#f4f6ff",
        bbox=dict(facecolor=(0.04, 0.08, 0.12, 0.72), edgecolor="none", pad=6),
    )

    _draw_divider(divider_ax)
    _render_footer(
        footer_ax,
        fig_scale=fig_scale,
        panel_pixel_height=FOOTER["height"] * FIG_PIXEL_HEIGHT,
        title_text=profile["footer_title"],  # type: ignore[index]
        subtitle_text=profile["footer_subtitle"],  # type: ignore[index]
    )

    fig.canvas.draw()
    buffer = np.asarray(fig.canvas.buffer_rgba())
    return Image.fromarray(buffer[..., :3])


def render_frames(cfg: AnimationConfig) -> List[Image.Image]:
    fig = plt.figure(figsize=cfg.figsize, dpi=cfg.dpi)
    fig.patch.set_facecolor("#050505")

    left_rect = [PANEL_LEFT["x"], PANEL_LEFT["y"], PANEL_LEFT["width"], PANEL_LEFT["height"]]
    right_rect = [PANEL_RIGHT["x"], PANEL_RIGHT["y"], PANEL_RIGHT["width"], PANEL_RIGHT["height"]]
    divider_rect = [DIVIDER["x"], DIVIDER["y"], DIVIDER["width"], DIVIDER["height"]]
    footer_rect = [FOOTER["x"], FOOTER["y"], FOOTER["width"], FOOTER["height"]]

    axes = {
        "left": fig.add_axes(left_rect),
        "right": fig.add_axes(right_rect),
        "divider": fig.add_axes(divider_rect),
        "footer": fig.add_axes(footer_rect),
    }

    frames: List[Image.Image] = []
    for frame_idx in range(cfg.total_frames):
        frame = update_frame(fig, axes, frame_idx, cfg)
        frames.append(frame)
    plt.close(fig)
    return frames


# ---------------------------------------------------------------------------
# Audio synthesis
# ---------------------------------------------------------------------------


def _synthesize_music(cfg: AnimationConfig) -> np.ndarray:
    sample_rate = VOICE_SAMPLE_RATE
    total_samples = int(cfg.duration * sample_rate)
    t = np.linspace(0.0, cfg.duration, total_samples, endpoint=False)

    base_freq = 42.0
    base = 0.28 * np.sin(2 * np.pi * base_freq * t) * np.exp(-t / (cfg.duration * 1.2))

    pad_freqs = (65.41, 103.83, 174.61)
    pad = sum(np.sin(2 * np.pi * freq * t) for freq in pad_freqs) / len(pad_freqs)
    pad *= np.clip((t / cfg.duration) ** 1.2, 0, 1) * 0.18

    pulses = np.zeros_like(t)
    pulse_times = np.linspace(0.5, cfg.duration - 0.5, 9)
    width = int(sample_rate * 0.45)
    window = np.hanning(width * 2)[:width]
    for onset in pulse_times:
        idx = int(onset * sample_rate)
        end = min(idx + width, total_samples)
        pulses[idx:end] += 0.22 * window[: end - idx] * np.sin(2 * np.pi * (55.0 + 20.0 * (onset / cfg.duration)) * t[idx:end])

    music = base + pad + pulses
    max_val = np.max(np.abs(music))
    if max_val > 0:
        music /= max_val
    return music


def _write_wav(path: Path, samples: np.ndarray, sample_rate: int = VOICE_SAMPLE_RATE) -> None:
    pcm = np.clip(samples, -1.0, 1.0)
    pcm = (pcm * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wav_writer:
        wav_writer.setnchannels(1)
        wav_writer.setsampwidth(2)
        wav_writer.setframerate(sample_rate)
        wav_writer.writeframes(pcm.tobytes())


def _tts_with_pyttsx3(text: str, outfile: Path, language: str) -> bool:
    try:
        import pyttsx3
    except ImportError:
        return False
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    target_voice = None
    for voice in voices:
        if language == "de" and "de" in voice.id.lower():
            target_voice = voice.id
            break
        if language == "en" and any(tag in voice.id.lower() for tag in ["en", "us", "gb"]):
            target_voice = voice.id
            break
        if language == "it" and "it" in voice.id.lower():
            target_voice = voice.id
            break
    if target_voice:
        engine.setProperty("voice", target_voice)
    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1.0)
    engine.save_to_file(text, str(outfile))
    engine.runAndWait()
    return outfile.exists() and outfile.stat().st_size > 0


def _tts_with_edge_tts(text: str, outfile: Path, language: str) -> bool:
    if shutil.which("edge-tts") is None:
        return False
    voice_map = {
        "de": "de-DE-KatjaNeural",
        "en": "en-US-AriaNeural",
        "it": "it-IT-IsabellaNeural",
    }
    voice = voice_map.get(language, "en-US-AriaNeural")
    cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(outfile)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return False
    return outfile.exists() and outfile.stat().st_size > 0


def _tts_with_espeak(text: str, outfile: Path, language: str) -> bool:
    if shutil.which("espeak") is None:
        return False
    lang_code = {"de": "de", "en": "en", "it": "it"}.get(language, "en")
    cmd = ["espeak", "-v", lang_code, "-s", "150", "-p", "40", "-a", "170", "-w", str(outfile), text]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return False
    return outfile.exists() and outfile.stat().st_size > 0


def _generate_voiceover(text_lines: Sequence[Tuple[float, str]], cfg: AnimationConfig, outdir: Path) -> Optional[Path]:
    voice_path = outdir / f"{cfg.basename}_voice.wav"
    combined_path = tempfile.NamedTemporaryFile(delete=False, suffix="_voice.wav")
    combined_path.close()
    tmp_files: List[Path] = []

    for idx, (_, line) in enumerate(text_lines):
        tmp_path = Path(combined_path.name).with_name(f"voice_line_{idx}.wav")
        success = _tts_with_edge_tts(line, tmp_path, cfg.language)
        if not success:
            success = _tts_with_pyttsx3(line, tmp_path, cfg.language)
        if not success:
            success = _tts_with_espeak(line, tmp_path, cfg.language)
        if not success:
            continue
        tmp_files.append(tmp_path)

    if not tmp_files:
        return None

    merged = np.zeros(int(cfg.duration * VOICE_SAMPLE_RATE), dtype=np.float32)
    for (start, _), path in zip(text_lines, tmp_files):
        with contextlib.closing(wave.open(str(path), "rb")) as wav:
            frames = wav.readframes(wav.getnframes())
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
            sr = wav.getframerate()
        if sr != VOICE_SAMPLE_RATE:
            continue
        start_idx = int(start * VOICE_SAMPLE_RATE)
        end_idx = min(start_idx + data.size, merged.size)
        merged[start_idx:end_idx] += data[: end_idx - start_idx]

    max_val = np.max(np.abs(merged))
    if max_val > 0:
        merged /= max_val

    _write_wav(voice_path, merged, VOICE_SAMPLE_RATE)
    for tmp in tmp_files:
        tmp.unlink(missing_ok=True)
    Path(combined_path.name).unlink(missing_ok=True)
    return voice_path


def _duck_audio(music: np.ndarray, voice: np.ndarray, strength: float = 0.35) -> np.ndarray:
    if voice.size == 0:
        return music
    envelope = np.abs(voice)
    envelope = np.convolve(envelope, np.ones(4410) / 4410, mode="same")
    duck = 1.0 - np.clip(envelope * strength, 0.0, 0.8)
    ducked_music = music * duck
    mix = ducked_music + voice * 0.95
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix /= max_val
    return mix


def generate_audio(music_path: Path, voice_path: Optional[Path], mixed_path: Path, cfg: AnimationConfig) -> None:
    music = _synthesize_music(cfg)
    _write_wav(music_path, music, VOICE_SAMPLE_RATE)

    voice = np.zeros_like(music)
    if voice_path and voice_path.exists():
        with contextlib.closing(wave.open(str(voice_path), "rb")) as wav:
            frames = wav.readframes(wav.getnframes())
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
            sr = wav.getframerate()
        if sr == VOICE_SAMPLE_RATE:
            voice[: min(voice.size, data.size)] = data[: voice.size]

    composite = _duck_audio(music, voice)
    _write_wav(mixed_path, composite, VOICE_SAMPLE_RATE)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def save_gif(outfile: Path, frames: Sequence[Image.Image], cfg: AnimationConfig) -> None:
    duration = 1.0 / cfg.fps
    if imageio is not None:
        imageio.mimsave(outfile, frames, duration=duration)
    else:  # pragma: no cover - Pillow fallback
        first, *rest = frames
        first.save(outfile, save_all=True, append_images=rest, duration=int(duration * 1000), loop=0)
    print(f"INFO: Saved GIF → {outfile}")


def save_mp4(outfile: Path, frames: Sequence[Image.Image], audio_path: Path, cfg: AnimationConfig) -> None:
    if imageio is None:
        print("WARN: imageio/ffmpeg unavailable – skipping MP4 export")
        return

    arrays = [np.array(frame) for frame in frames]
    writer_args = dict(fps=cfg.fps, codec="libx264", format="FFMPEG", macro_block_size=None)
    try:
        with imageio.get_writer(outfile, audio_path=str(audio_path), **writer_args) as writer:
            for arr in arrays:
                writer.append_data(arr)
    except TypeError:
        # Fallback without audio parameter (older imageio)
        with imageio.get_writer(outfile, **writer_args) as writer:
            for arr in arrays:
                writer.append_data(arr)
    print(f"INFO: Saved MP4 → {outfile}")


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Big Bang vs. SSZ comparison animation")
    parser.add_argument("--duration", type=float, default=25.0, help="Animation duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--outdir", type=Path, default=Path("/mnt/data"))
    parser.add_argument("--basename", type=str, default="ssz_vs_bigbang")
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--language", type=str, default="de", choices=sorted(LANGUAGE_PROFILES.keys()))
    return parser.parse_args()


def ensure_outdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    setup_stdout_utf8()
    args = parse_args()
    cfg = AnimationConfig(
        duration=args.duration,
        fps=args.fps,
        dpi=args.dpi,
        outdir=args.outdir,
        basename=args.basename,
        language=args.language,
    )
    ensure_outdir(cfg.outdir)

    print("INFO: Rendering frames …")
    frames = render_frames(cfg)

    gif_path = cfg.outdir / f"{cfg.basename}.gif"
    mp4_path = cfg.outdir / f"{cfg.basename}.mp4"
    music_path = cfg.outdir / f"{cfg.basename}_music.wav"
    schedule = cfg.profile["voice_schedule"]  # type: ignore[index]
    voice_path = _generate_voiceover(schedule, cfg, cfg.outdir)
    mixed_audio = cfg.outdir / f"{cfg.basename}.wav"

    print("INFO: Generating audio track …")
    generate_audio(music_path, voice_path, mixed_audio, cfg)

    print("INFO: Writing GIF …")
    save_gif(gif_path, frames, cfg)

    print("INFO: Writing MP4 …")
    save_mp4(mp4_path, frames, mixed_audio, cfg)

    print("INFO: Done. Outputs saved to", cfg.outdir)


if __name__ == "__main__":
    main()
