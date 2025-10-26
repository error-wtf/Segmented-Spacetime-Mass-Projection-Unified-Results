#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core cosmology utilities for SSZ background and growth calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence

import numpy as np
from numpy.typing import ArrayLike
from scipy import integrate

try:  # optional dependency for type checking
    from typing import Protocol
except ImportError:  # pragma: no cover
    Protocol = object  # type: ignore

C_LIGHT_KM_S = 299792.458
MPC_IN_KM = 3.08567758128e19 / 1000.0
T_CMB = 2.725
N_EFF = 3.046


@dataclass
class BackgroundParams:
    """ΛCDM baseline parameters."""

    H0: float = 70.0
    Omega_m: float = 0.3
    Omega_b: float = 0.05
    Omega_lambda: float = 0.7
    Omega_k: float = 0.0
    sigma8: float = 0.8

    @property
    def Omega_r(self) -> float:
        """Compute radiation density using standard scaling with T_CMB and N_eff."""

        omega_gamma = 2.469e-5 / (self.H0 / 100.0) ** 2 * (T_CMB / 2.725) ** 4
        omega_rel = omega_gamma * (1.0 + 0.2271 * N_EFF)
        return omega_rel


class GrowthModifier(Protocol):
    """Protocol for growth modification injected by SSZ models."""

    def damping_term(self, z: float, E_z: float, params: object) -> float:
        """Return the multiplicative damping coefficient acting on D'(z)."""


class OmegaSSZContribution(Protocol):
    """Protocol for background SSZ contribution."""

    def omega_ssz(self, z: float, base_E: float, params: object) -> float:
        """Return Ω_ssz(z) to be added to E(z)^2."""


class NullGrowthModifier:
    def damping_term(self, z: float, E_z: float, params: object) -> float:
        return 0.0


class NullOmegaContribution:
    def omega_ssz(self, z: float, base_E: float, params: object) -> float:
        return 0.0


@dataclass
class ModelContext:
    background: BackgroundParams
    omega_provider: OmegaSSZContribution
    growth_modifier: GrowthModifier
    extra_params: object


def _lcdm_E2(z: ArrayLike, params: BackgroundParams) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    om = params.Omega_m * (1.0 + z) ** 3
    orad = params.Omega_r * (1.0 + z) ** 4
    olum = params.Omega_lambda
    ok = params.Omega_k * (1.0 + z) ** 2
    return om + orad + olum + ok


class CosmoEngine:
    def __init__(self, context: ModelContext):
        self.context = context

    def E(self, z: ArrayLike) -> np.ndarray:
        z = np.atleast_1d(np.asarray(z, dtype=float))
        base_E2 = _lcdm_E2(z, self.context.background)
        omega_term = np.array(
            [
                self.context.omega_provider.omega_ssz(
                    zi,
                    float(np.sqrt(base)),
                    self.context.extra_params,
                )
                for zi, base in zip(z, base_E2)
            ]
        )
        e2 = np.maximum(base_E2 + omega_term, 1e-12)
        return np.sqrt(e2)

    def H(self, z: ArrayLike) -> np.ndarray:
        return self.E(z) * self.context.background.H0

    def comoving_distance(self, z: float) -> float:
        integrand: Callable[[float], float] = lambda zz: C_LIGHT_KM_S / self.H(zz)
        result, _ = integrate.quad(integrand, 0.0, float(z), epsabs=1e-6, epsrel=1e-5)
        return result

    def luminosity_distance(self, z: float) -> float:
        return (1.0 + z) * self.comoving_distance(z)

    def angular_diameter_distance(self, z: float) -> float:
        return self.luminosity_distance(z) / (1.0 + z) ** 2

    def critical_density_fraction(self, z: float) -> float:
        e = float(self.E(z))
        return e ** 2

    def sound_horizon(self) -> float:
        omega_m = self.context.background.Omega_m
        omega_b = self.context.background.Omega_b
        h = self.context.background.H0 / 100.0
        rs = 55.154 * np.exp(-72.3 * (omega_b * h ** 2) ** 0.5) / (omega_m * h ** 2) ** 0.25351
        return rs

    def H_scalar(self, z: float) -> float:
        return float(self.H(np.array([z]))[0])

    def dlnH_dz(self, z: float, step: float = 1e-4) -> float:
        zp = min(z + step, max(z + step, 0.0) + step)
        zm = max(z - step, 0.0)
        hp = self.H_scalar(zp)
        hm = self.H_scalar(zm)
        if hp <= 0 or hm <= 0:
            return 0.0
        return (np.log(hp) - np.log(hm)) / (zp - zm if zp != zm else step)

    def growth_factor(self, z: Sequence[float], params: Optional[object] = None) -> np.ndarray:
        if params is None:
            params = self.context.extra_params

        z = np.asarray(z, dtype=float)
        z_sorted_desc = np.flip(np.unique(np.sort(z)))
        z_max = max(100.0, float(z_sorted_desc[0]))
        z_span = (z_max, 0.0)

        def ode(z_var, y):
            D, Dp = y
            Ez = float(self.E(z_var))
            dlnHdz_val = self.dlnH_dz(z_var)
            damping = self.context.growth_modifier.damping_term(z_var, Ez, params)
            coeff1 = dlnHdz_val + 2.0 / (1.0 + z_var) + damping
            coeff2 = -1.5 * self.context.background.Omega_m * (1.0 + z_var) / (Ez ** 2)
            return [Dp, -coeff1 * Dp + coeff2 * D]

        D0 = 1.0 / (1.0 + z_span[0])
        Dp0 = -1.0 / (1.0 + z_span[0]) ** 2
        solution = integrate.solve_ivp(
            ode,
            z_span,
            [D0, Dp0],
            t_eval=z_sorted_desc,
            method="Radau",
            rtol=1e-5,
            atol=1e-8,
        )
        if not solution.success:
            raise RuntimeError(f"Growth integration failed: {solution.message}")
        growth_desc = solution.y[0]
        # interpolate back to requested z ordering
        growth_interp = np.interp(z, z_sorted_desc[::-1], growth_desc[::-1])
        return growth_interp

    def sigma8_z(self, z: Sequence[float]) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        growth = self.growth_factor(z)
        growth0 = float(self.growth_factor(np.array([0.0]))[0])
        sigma8_0 = self.context.background.sigma8
        return sigma8_0 * growth / growth0

    def f_sigma8(self, z: Sequence[float]) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        sigma8_vals = self.sigma8_z(z)
        growth = self.growth_factor(z)
        a = 1.0 / (1.0 + z)
        dlnD_dlnA = np.gradient(np.log(growth + 1e-12), np.log(a + 1e-12))
        return sigma8_vals * dlnD_dlnA

    def volume_distance(self, z: float) -> float:
        dm = (1.0 + z) * self.angular_diameter_distance(z)
        dh = C_LIGHT_KM_S / self.H_scalar(z)
        return (z * dm * dm * dh) ** (1.0 / 3.0)
