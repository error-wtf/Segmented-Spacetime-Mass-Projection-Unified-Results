#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSZ cosmology model parameterisations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from ssz_cosmo_core import ModelContext, BackgroundParams, NullOmegaContribution, NullGrowthModifier


@dataclass
class ModelAParams:
    alpha_ssz: float = 0.0
    beta: float = 0.0
    gamma: float = 0.0


class ModelAOmega:
    def omega_ssz(self, z: float, base_E: float, params: ModelAParams) -> float:
        return params.alpha_ssz * (base_E ** params.beta) * (1.0 + z) ** params.gamma


@dataclass
class ModelBParams:
    eta_ssz: float = 0.0
    beta_g: float = 0.0


class ModelBGrowth:
    def damping_term(self, z: float, E_z: float, params: ModelBParams) -> float:
        return params.eta_ssz * (E_z ** params.beta_g)


MODEL_REGISTRY: Dict[str, Tuple[type, type]] = {
    "A": (ModelAOmega, NullGrowthModifier),
    "B": (NullOmegaContribution, ModelBGrowth),
}


def build_context(model_key: str, background: BackgroundParams, extra: dict) -> ModelContext:
    if model_key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model key {model_key}")
    omega_cls, growth_cls = MODEL_REGISTRY[model_key]
    if model_key == "A":
        params = ModelAParams(**{k: extra.get(k, getattr(ModelAParams, k)) for k in ModelAParams.__annotations__.keys()})
        omega_provider = omega_cls()
        growth_provider = NullGrowthModifier()
    else:
        params = ModelBParams(**{k: extra.get(k, getattr(ModelBParams, k)) for k in ModelBParams.__annotations__.keys()})
        omega_provider = NullOmegaContribution()
        growth_provider = growth_cls()
    return ModelContext(background=background, omega_provider=omega_provider, growth_modifier=growth_provider, extra_params=params)
