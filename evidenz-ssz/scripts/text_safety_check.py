#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post-render bounds checker for SSZ vs. Big Bang animations."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import imageio.v3 as iio
import numpy as np

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

LEFT_SAFE = (
    int(0.00 * FRAME_WIDTH + 0.05 * FRAME_WIDTH),
    int(0.05 * FRAME_HEIGHT),
    int(0.48 * FRAME_WIDTH - 0.05 * FRAME_WIDTH),
    int(0.95 * FRAME_HEIGHT - 0.05 * FRAME_HEIGHT),
)
RIGHT_SAFE = (
    int(0.52 * FRAME_WIDTH),
    int(0.05 * FRAME_HEIGHT),
    int(0.48 * FRAME_WIDTH - 0.05 * FRAME_WIDTH),
    int(0.95 * FRAME_HEIGHT - 0.05 * FRAME_HEIGHT),
)
TITLE_SAFE = (
    int(0.15 * FRAME_WIDTH),
    int(0.90 * FRAME_HEIGHT),
    int(0.70 * FRAME_WIDTH),
    int(0.07 * FRAME_HEIGHT),
)
SAFE_ZONES = np.array([LEFT_SAFE, RIGHT_SAFE, TITLE_SAFE])


def _mask_outside_safe(coords: np.ndarray, safe_zones: np.ndarray) -> np.ndarray:
    x = coords[:, 1]
    y = coords[:, 0]
    mask = np.zeros(coords.shape[0], dtype=bool)
    for sx, sy, sw, sh in safe_zones:
        mask |= (x >= sx) & (x < sx + sw) & (y >= sy) & (y < sy + sh)
    return ~mask


def check_video(path: Path, *, sample_step: int, threshold: int, debug_dir: Path | None) -> List[str]:
    problems: List[str] = []
    if debug_dir is not None:
        debug_dir.mkdir(parents=True, exist_ok=True)

    for idx, frame in enumerate(iio.imiter(path, plugin="pyav")):
        if idx % sample_step != 0:
            continue
        gray = frame.mean(axis=2)
        bright = gray >= threshold
        coords = np.argwhere(bright)
        if coords.size == 0:
            continue
        outside = _mask_outside_safe(coords, SAFE_ZONES)
        if not np.any(outside):
            continue
        bad_points = coords[outside]
        problems.append(f"Frame {idx}: {bad_points.shape[0]} bright pixels outside safe zones")
        if debug_dir is not None:
            dbg = frame.copy()
            dbg[bad_points[:, 0], bad_points[:, 1]] = [255, 0, 0]
            iio.imwrite(debug_dir / f"overflow_frame_{idx:05d}.png", dbg)

    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify text stays inside safe layout zones")
    parser.add_argument("video", type=Path, help="Rendered MP4 file (1920x1080)")
    parser.add_argument("--sample-step", type=int, default=6, help="Inspect every n-th frame (default 6)")
    parser.add_argument("--threshold", type=int, default=200, help="Brightness threshold for text detection")
    parser.add_argument("--debug-dir", type=Path, default=None, help="Optional directory for debug frames")
    args = parser.parse_args()

    issues = check_video(
        args.video,
        sample_step=max(1, args.sample_step),
        threshold=max(0, min(255, args.threshold)),
        debug_dir=args.debug_dir,
    )

    if issues:
        print("TEXT_OVERFLOW_DETECTED")
        for entry in issues:
            print(entry)
    else:
        print("OK: No text overflow detected.")


if __name__ == "__main__":
    main()
