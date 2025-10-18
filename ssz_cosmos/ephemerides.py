"""Ephemeris ingestion utilities for cosmological SSZ simulations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Optional

import numpy as np
import pandas as pd

from .constants import GAIACoordinateFrame, GAIA_DR3_FRAME, to_barycentric


@dataclass
class EphemerisSeries:
    """Time series of barycentric positions (and optional velocities)."""

    body_name: str
    frame: GAIACoordinateFrame
    jd: np.ndarray
    positions: np.ndarray  # shape (N, 3)
    velocities: Optional[np.ndarray] = None

    def interpolate(self, jd: float) -> np.ndarray:
        """Return linearly interpolated position for the given Julian Date."""

        idx = np.searchsorted(self.jd, jd)
        if idx == 0:
            return self.positions[0]
        if idx >= len(self.jd):
            return self.positions[-1]
        t0, t1 = self.jd[idx - 1], self.jd[idx]
        w = (jd - t0) / (t1 - t0)
        return (1 - w) * self.positions[idx - 1] + w * self.positions[idx]


class EphemerisLoader:
    """Load ephemerides from GAIA/JPL datasets into :class:`EphemerisSeries`."""

    def __init__(self, frame: GAIACoordinateFrame = GAIA_DR3_FRAME) -> None:
        self.frame = frame

    def from_gaia_csv(self, path: Path | str, body_name: str) -> EphemerisSeries:
        df = pd.read_csv(path)
        columns = {"JD", "X", "Y", "Z"}
        if not columns.issubset(df.columns):
            raise ValueError("CSV must contain JD, X, Y, Z columns")
        positions = df[["X", "Y", "Z"]].values.astype(float)
        return EphemerisSeries(
            body_name=body_name,
            frame=self.frame,
            jd=df["JD"].values.astype(float),
            positions=positions,
        )

    def from_horizons_csv(
        self,
        path: Path | str,
        body_name: str,
        sun_series: EphemerisSeries,
    ) -> EphemerisSeries:
        df = pd.read_csv(path)
        columns = {"JD", "X", "Y", "Z"}
        if not columns.issubset(df.columns):
            raise ValueError("CSV must contain JD, X, Y, Z columns")
        jd = df["JD"].values.astype(float)
        positions = df[["X", "Y", "Z"]].values.astype(float)
        # Interpolate Sun's barycentric position and convert to barycentric coordinates
        bary_positions = []
        for jd_i, pos in zip(jd, positions):
            sun_pos = sun_series.interpolate(jd_i)
            bary_positions.append(to_barycentric(pos, origin="heliocentric", sun_position=sun_pos))
        return EphemerisSeries(body_name=body_name, frame=self.frame, jd=jd, positions=np.array(bary_positions))
