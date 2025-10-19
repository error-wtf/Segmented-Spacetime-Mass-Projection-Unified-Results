"""Body catalog utilities for cosmological SSZ simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import json

import numpy as np
import pandas as pd


@dataclass
class BodyDefinition:
    """Container describing a gravitating body used in the SSZ cosmology model."""

    name: str
    mass_kg: float
    radius_m: float
    alpha: float = 1.0
    kappa: float = 0.015
    gamma: float = 1.0
    beta: float = 1.0
    metadata: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, float]:
        return {
            "name": self.name,
            "mass_kg": self.mass_kg,
            "radius_m": self.radius_m,
            "alpha": self.alpha,
            "kappa": self.kappa,
            "metadata": self.metadata,
            "gamma": self.gamma,
            "beta": self.beta,
        }


class BodyCatalog:
    """Utility for managing a collection of :class:`BodyDefinition` entries."""

    def __init__(self, bodies: Optional[Iterable[BodyDefinition]] = None) -> None:
        self._bodies: Dict[str, BodyDefinition] = {}
        if bodies:
            for body in bodies:
                self.add(body)

    def __contains__(self, name: str) -> bool:  # pragma: no cover - trivial
        return name.lower() in self._bodies

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._bodies)

    def add(self, body: BodyDefinition) -> None:
        if body.mass_kg <= 0:
            raise ValueError(f"body {body.name} mass must be positive")
        self._bodies[body.name.lower()] = body

    def get(self, name: str) -> BodyDefinition:
        try:
            return self._bodies[name.lower()]
        except KeyError as exc:  # pragma: no cover - simple error path
            raise KeyError(f"Body '{name}' not found in catalog") from exc

    def list(self) -> List[BodyDefinition]:
        return list(self._bodies.values())

    # -------------------------------------------------------------------------
    # Loading helpers
    # -------------------------------------------------------------------------
    @classmethod
    def from_json(cls, path: Path | str) -> "BodyCatalog":
        data = json.loads(Path(path).read_text())
        bodies = [BodyDefinition(**entry) for entry in data]
        return cls(bodies)

    @classmethod
    def from_csv(cls, path: Path | str) -> "BodyCatalog":
        df = pd.read_csv(path)
        required = {"name", "mass_kg", "radius_m"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")
        bodies = []
        for _, row in df.iterrows():
            metadata = {}
            for key in df.columns:
                if key in {"name", "mass_kg", "radius_m", "alpha", "kappa", "gamma", "beta"}:
                    continue
                value = row[key]
                if not pd.isna(value):
                    metadata[key] = float(value)
            bodies.append(
                BodyDefinition(
                    name=str(row["name"]),
                    mass_kg=float(row["mass_kg"]),
                    radius_m=float(row["radius_m"]),
                    alpha=float(row.get("alpha", 1.0)),
                    kappa=float(row.get("kappa", 0.015)),
                    gamma=float(row.get("gamma", 1.0)),
                    beta=float(row.get("beta", 1.0)),
                    metadata=metadata,
                )
            )
        return cls(bodies)

    # -------------------------------------------------------------------------
    # Convenience constructors
    # -------------------------------------------------------------------------
    @classmethod
    def solar_system_defaults(cls) -> "BodyCatalog":
        """Return approximate masses/radii for major solar-system bodies."""

        from ssz_unified_suite import SSZConstants

        const = SSZConstants()
        au = 1.0  # placeholder metadata example
        bodies = [
            BodyDefinition("Sun", const.M_SUN, 6.96342e8, metadata={"au": au}),
            BodyDefinition("Mercury", 3.3011e23, 2.4397e6),
            BodyDefinition("Venus", 4.8675e24, 6.0518e6),
            BodyDefinition("Earth", const.M_EARTH, 6.371e6),
            BodyDefinition("Mars", 6.4171e23, 3.3895e6),
            BodyDefinition("Jupiter", 1.8982e27, 6.9911e7),
            BodyDefinition("Saturn", 5.6834e26, 5.8232e7),
            BodyDefinition("Uranus", 8.6810e25, 2.5362e7),
            BodyDefinition("Neptune", 1.02413e26, 2.4622e7),
        ]
        return cls(bodies)
