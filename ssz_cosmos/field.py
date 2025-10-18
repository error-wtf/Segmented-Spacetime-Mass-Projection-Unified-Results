"""Multi-body SSZ field computations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np

from ssz_unified_suite import SSZCore

from .constants import GAIA_DR3_FRAME


@dataclass
class BodyState:
    """State of a body at a specific epoch."""

    name: str
    position: np.ndarray
    mass_kg: float
    alpha: float
    kappa: float


class MultiBodyField:
    """Superpose SSZ fields from multiple bodies."""

    def __init__(self, core: Optional[SSZCore] = None) -> None:
        self.core = core or SSZCore()

    def sigma(self, points: np.ndarray, states: Iterable[BodyState]) -> np.ndarray:
        points = np.asarray(points)
        sigma_total = np.zeros(points.shape[:-1])
        for state in states:
            rs = self.core.schwarzschild_radius(state.mass_kg)
            rphi = self.core.r_phi(state.mass_kg)
            distances = np.linalg.norm(points - state.position, axis=-1)
            sigma_body = self.core.sigma(distances, state.mass_kg)
            sigma_total += sigma_body
        return sigma_total

    def tau(self, points: np.ndarray, states: Iterable[BodyState]) -> np.ndarray:
        sigma_total = self.sigma(points, states)
        # For now use global alpha (can be made per-body by weighting)
        alpha = np.mean([state.alpha for state in states])
        return self.core.const.PHI ** (-alpha * sigma_total)

    def refractive_index(self, points: np.ndarray, states: Iterable[BodyState]) -> np.ndarray:
        sigma_total = self.sigma(points, states)
        kappa = np.mean([state.kappa for state in states])
        return 1.0 + kappa * sigma_total
