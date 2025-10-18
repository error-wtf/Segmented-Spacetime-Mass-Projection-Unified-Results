"""High-level orchestration for SSZ cosmological simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from .bodies import BodyCatalog, BodyDefinition
from .ephemerides import EphemerisLoader, EphemerisSeries
from .field import BodyState, MultiBodyField


@dataclass
class SimulationConfig:
    start_jd: float
    end_jd: float
    step_days: float = 1.0
    grid_points: Optional[np.ndarray] = None  # optional precomputed sampling grid


@dataclass
class SimulationResult:
    jd: float
    sigma: np.ndarray
    tau: np.ndarray
    refractive_index: np.ndarray


class SSZCosmicSimulator:
    """Run SSZ cosmological simulations across multiple bodies and epochs."""

    def __init__(self, catalog: BodyCatalog) -> None:
        self.catalog = catalog
        self.loader = EphemerisLoader()
        self.field = MultiBodyField()
        self.ephemerides: Dict[str, EphemerisSeries] = {}

    def load_ephemeris(self, body_name: str, path: Path | str, provider: str = "gaia") -> None:
        body = self.catalog.get(body_name)
        if provider == "gaia":
            series = self.loader.from_gaia_csv(path, body_name)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        self.ephemerides[body_name] = series

    def states_at(self, jd: float) -> List[BodyState]:
        states: List[BodyState] = []
        for body in self.catalog.list():
            series = self.ephemerides.get(body.name)
            if series is None:
                continue
            pos = series.interpolate(jd)
            states.append(BodyState(body.name, pos, body.mass_kg, body.alpha, body.kappa))
        return states

    def run(self, config: SimulationConfig) -> Iterable[SimulationResult]:
        if config.grid_points is None:
            raise ValueError("grid_points must be provided for simulation")
        jd_values = np.arange(config.start_jd, config.end_jd + config.step_days, config.step_days)
        for jd in jd_values:
            states = self.states_at(jd)
            if not states:
                continue
            sigma = self.field.sigma(config.grid_points, states)
            tau = self.field.tau(config.grid_points, states)
            n = self.field.refractive_index(config.grid_points, states)
            yield SimulationResult(jd=jd, sigma=sigma, tau=tau, refractive_index=n)
