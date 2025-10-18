"""Shared constants and unit helpers for cosmological SSZ simulations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

import numpy as np


@dataclass(frozen=True)
class GAIACoordinateFrame:
    """Metadata describing the coordinate frame of GAIA/VizieR ephemerides.

    Attributes
    ----------
    frame : Literal["ICRS", "BARY", "HELIO"]
        Name of the coordinate frame. GAIA typically uses ``ICRS`` (barycentric).
    origin : Literal["barycentric", "heliocentric"]
        Physical origin of the coordinates. ``barycentric`` is suitable for
        direct GAIA ingestion; ``heliocentric`` can be derived as needed.
    units : Mapping[str, str]
        Mapping of quantity names to SI-based unit strings (e.g. metres, seconds).
    epoch : float
        Reference epoch (Julian Date) of the dataset. All ephemeris timestamps
        should be referenced relative to this epoch.
    """

    frame: Literal["ICRS", "BARY", "HELIO"]
    origin: Literal["barycentric", "heliocentric"]
    units: Mapping[str, str]
    epoch: float


DEFAULT_UNITS: Mapping[str, str] = {
    "length": "m",
    "velocity": "m/s",
    "time": "JD",
    "mass": "kg",
}

# Default GAIA DR3 coordinate frame specification (barycentric ICRS).
GAIA_DR3_FRAME = GAIACoordinateFrame(
    frame="ICRS",
    origin="barycentric",
    units={**DEFAULT_UNITS},
    epoch=2457388.5,  # GAIA DR3 reference epoch (J2015.5)
)


def astronomical_unit() -> float:
    """Return the astronomical unit in metres (IAU 2012 value)."""

    return 149_597_870_700.0


def julian_century() -> float:
    """Return the length of a Julian century in days."""

    return 36_525.0


def to_barycentric(positions: np.ndarray, origin: Literal["barycentric", "heliocentric"],
                   sun_position: np.ndarray | None) -> np.ndarray:
    """Convert positions to the barycentric frame if necessary.

    Parameters
    ----------
    positions : np.ndarray
        Array of shape ``(..., 3)`` containing position vectors.
    origin : {"barycentric", "heliocentric"}
        Origin of the supplied coordinates.
    sun_position : np.ndarray or None
        Barycentric position of the Sun at the same epoch as ``positions``. Only
        required when converting from heliocentric coordinates.

    Returns
    -------
    np.ndarray
        Positions expressed in the barycentric frame.
    """

    if origin == "barycentric":
        return positions
    if sun_position is None:
        raise ValueError("sun_position must be provided when converting from heliocentric coordinates")
    return positions + sun_position
