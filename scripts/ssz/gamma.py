from __future__ import annotations

import numpy as np


def gamma_seg_from_density(
    rho: np.ndarray | float,
    *,
    alpha: float = 1.0,
    beta: float = 0.5,
    floor: float = 0.02,
) -> np.ndarray:
    """Map matter density values to SSZ ``gamma`` factors.

    Higher densities should yield smaller ``gamma`` values while remaining within
    the inclusive range ``[floor, 1.0]``. A smooth, monotonic mapping keeps the
    tests deterministic and numerically stable.
    """

    rho_arr = np.asarray(rho, dtype=float)
    if floor <= 0.0 or floor > 1.0:
        raise ValueError("floor must be within (0, 1]")
    scaled = np.power(np.clip(rho_arr, 0.0, None), beta)
    decay = np.exp(-alpha * scaled)
    gamma = floor + (1.0 - floor) * decay
    return np.clip(gamma, floor, 1.0)


def ensure_numpy(x: np.ndarray | float) -> np.ndarray:
    if isinstance(x, np.ndarray):
        return x
    return np.asarray(x, dtype=float)
