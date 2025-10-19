from __future__ import annotations

import numpy as np

from scripts.ssz.gamma import gamma_seg_from_density, ensure_numpy


def z_from_gamma(gamma: np.ndarray | float) -> np.ndarray:
    g = np.clip(ensure_numpy(gamma), 1e-9, None)
    return (1.0 / g) - 1.0


def rotation_modifier_from_gamma(gamma: np.ndarray | float, p: float = 0.5) -> np.ndarray:
    g = np.clip(ensure_numpy(gamma), 1e-9, None)
    modifier = np.power(1.0 / g, p)
    return np.clip(modifier, 1.0, None)


def lensing_proxy_from_density(
    rho: np.ndarray | float,
    *,
    kappa_scale: float = 1.0,
    gamma_params: dict | None = None,
) -> np.ndarray:
    params = dict(alpha=1.0, beta=0.6, floor=0.02)
    if gamma_params:
        params.update(gamma_params)
    gamma = gamma_seg_from_density(rho, **params)
    base = np.clip(ensure_numpy(rho), 0.0, None)
    kappa = kappa_scale * base * (1.0 / gamma)
    return np.clip(kappa, 0.0, None)


def build_cosmo_fields(
    df,
    *,
    density_col: str = "rho",
    gamma_cfg: dict | None = None,
    kappa_scale: float = 1.0,
    rot_power: float = 0.5,
):
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        raise TypeError("build_cosmo_fields expects a pandas DataFrame")
    if density_col not in df.columns:
        raise KeyError(f"Missing density column: {density_col}")

    params = dict(alpha=0.8, beta=0.6, floor=0.02)
    if gamma_cfg:
        params.update(gamma_cfg)

    rho = df[density_col].to_numpy(dtype=float)
    gamma = gamma_seg_from_density(rho, **params)
    z_seg = z_from_gamma(gamma)
    kappa_proxy = lensing_proxy_from_density(rho, kappa_scale=kappa_scale, gamma_params=params)
    vrot_mod = rotation_modifier_from_gamma(gamma, p=rot_power)

    df = df.copy()
    df["gamma_seg"] = gamma
    df["z_seg"] = z_seg
    df["kappa_proxy"] = kappa_proxy
    df["vrot_mod"] = vrot_mod
    return df
