from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SegParams:
    rings: int = 16
    r_max_pc: float = 1200.0
    base_segments_at_r1: int = 6
    growth_rate: float = 1.15
    jitter: float = 0.0


def _ensure_df(data: pd.DataFrame | Iterable[dict]) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data
    return pd.DataFrame(list(data))


def _polar_coords(df: pd.DataFrame, x_col: str, y_col: str) -> tuple[np.ndarray, np.ndarray]:
    x = df[x_col].to_numpy(dtype=float)
    y = df[y_col].to_numpy(dtype=float)
    r = np.sqrt(x * x + y * y)
    theta = np.mod(np.arctan2(y, x), 2.0 * np.pi)
    return r, theta


def _ring_edges(params: SegParams) -> np.ndarray:
    edges = np.linspace(0.0, params.r_max_pc, params.rings + 1)
    return edges


def _segments_per_ring(params: SegParams) -> np.ndarray:
    counts = []
    base = max(params.base_segments_at_r1, 1)
    for ring_idx in range(params.rings):
        scale = params.growth_rate ** ring_idx
        counts.append(int(round(base * scale)))
    counts = np.asarray(counts, dtype=int)
    counts[counts <= 0] = 1
    return counts


def assign_segments_xy(
    df_like: pd.DataFrame | Iterable[dict],
    x_col: str,
    y_col: str,
    *,
    params: SegParams | None = None,
) -> pd.DataFrame:
    params = params or SegParams()
    df = _ensure_df(df_like).copy()
    if x_col not in df.columns or y_col not in df.columns:
        raise KeyError(f"Missing coordinate columns {x_col}/{y_col}")

    r, theta = _polar_coords(df, x_col, y_col)
    edges = _ring_edges(params)
    ring_ids = np.digitize(r, edges, right=False) - 1
    ring_ids = np.clip(ring_ids, 0, params.rings - 1)

    seg_counts = _segments_per_ring(params)
    ring_counts = seg_counts[ring_ids]
    segment_ids = np.floor(theta / (2.0 * np.pi / ring_counts)).astype(int)
    segment_ids = np.mod(segment_ids, ring_counts)

    df["ring_id"] = ring_ids
    df["segment_id"] = segment_ids
    return df
