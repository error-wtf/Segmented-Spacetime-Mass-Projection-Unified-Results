#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Check v6
==================

Single-point SSZ stability diagnostics with deterministic segment placement,
floating-point safeguards, and logging.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import csv
import json
import math
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Dict

import numpy as np

# Numerical tolerances
EPS = 1e-9
BOUND_TOL = 1e-6
MIN_LOG_ARG = 1e-12

# Geometry constants
TWO_PI = 2.0 * math.pi
HALF_PI = math.pi / 2.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def clean_float(value: float) -> float:
    return float(f"{value:.12g}")


def resolve_output_dir() -> Path:
    preferred = Path("/mnt/data")
    if preferred.exists() and preferred.is_dir():
        return preferred
    return Path.cwd()


@dataclass
class Parameters:
    alpha: float = 2.5
    eta: float = 0.0
    omega: float = 0.25
    m: int = 4
    Omega0: float = 0.30
    epsilon: float = 0.2
    q: float = 3.0
    lambda_A: float = 0.02
    K: int = 32
    sigma0: float = 0.4
    R: float = 0.9999
    Kappa: float = 1e-5
    phi: float = 1.618034
    r0: float = 1.0
    theta_samples: int = 4096
    segment_mode: str = "uniform"

    @classmethod
    def from_json(cls, path: Path) -> "Parameters":
        with open(path, "r", encoding="utf-8") as handle:
            return cls(**json.load(handle))


# ---------------------------------------------------------------------------
# Geometry and gain helpers
# ---------------------------------------------------------------------------


def theta_grid(params: Parameters) -> np.ndarray:
    return np.linspace(0.0, TWO_PI, params.theta_samples, endpoint=False, dtype=np.float64)


def phi_power(theta: np.ndarray, params: Parameters) -> np.ndarray:
    return np.power(params.phi, theta / HALF_PI, dtype=np.float64)


def r_theta(theta: np.ndarray, params: Parameters) -> np.ndarray:
    return params.r0 * phi_power(theta, params)


def sigma_theta(theta: np.ndarray, params: Parameters) -> np.ndarray:
    return params.sigma0 * phi_power(theta, params)


def Omega_theta(theta: np.ndarray, params: Parameters) -> np.ndarray:
    return params.Omega0 * (1.0 + params.epsilon * np.cos(params.q * theta, dtype=np.float64))


def gamma_loc(theta: np.ndarray, params: Parameters) -> np.ndarray:
    gain = np.maximum(0.0, params.m * Omega_theta(theta, params) - params.omega)
    return params.alpha * gain - params.eta


def integrate_over_theta(values: np.ndarray, params: Parameters) -> float:
    dx = TWO_PI / params.theta_samples
    return float(np.trapezoid(values, dx=dx))


# ---------------------------------------------------------------------------
# Segment placement
# ---------------------------------------------------------------------------


def weighted_segment_angles(params: Parameters, resolution: int = 16384) -> np.ndarray:
    theta = np.linspace(0.0, TWO_PI, resolution, endpoint=False, dtype=np.float64)
    sigma_vals = sigma_theta(theta, params)
    cumulative = np.cumsum(sigma_vals)
    total = cumulative[-1]
    if total <= MIN_LOG_ARG:
        return np.linspace(0.0, TWO_PI, params.K, endpoint=False, dtype=np.float64)
    targets = np.linspace(0.0, total, params.K, endpoint=False, dtype=np.float64)
    angles = np.empty(params.K, dtype=np.float64)
    for idx, target in enumerate(targets):
        pos = int(np.clip(np.searchsorted(cumulative, target, side="left"), 1, resolution - 1))
        left_val = cumulative[pos - 1]
        right_val = cumulative[pos]
        frac = 0.0 if right_val == left_val else (target - left_val) / (right_val - left_val)
        theta_left = theta[pos - 1]
        angles[idx] = np.clip(theta_left + frac * (TWO_PI / resolution), 0.0, TWO_PI)
    return angles


def segment_angles(params: Parameters) -> np.ndarray:
    if params.segment_mode.lower() == "weighted":
        return weighted_segment_angles(params)
    return np.linspace(0.0, TWO_PI, params.K, endpoint=False, dtype=np.float64)


# ---------------------------------------------------------------------------
# Gain, Xi, and stability diagnostics
# ---------------------------------------------------------------------------


def compute_L(params: Parameters) -> float:
    return integrate_over_theta(r_theta(theta_grid(params), params), params)


def compute_Xi(params: Parameters) -> float:
    Omega_max = params.Omega0 * (1.0 + params.epsilon)
    drive = params.alpha * max(0.0, params.m * Omega_max - params.omega) - params.eta
    L = compute_L(params)
    log_mirror = math.log(max(MIN_LOG_ARG, params.R * (1.0 - params.Kappa)))
    return drive * L + log_mirror


def compute_logG(params: Parameters) -> Dict[str, float]:
    theta = theta_grid(params)
    integral_gamma = integrate_over_theta(gamma_loc(theta, params) * r_theta(theta, params), params)
    angles = segment_angles(params)
    sigma_vals = sigma_theta(angles, params)
    damping_sum = params.lambda_A * float(np.sum(sigma_vals))
    log_mirror = math.log(max(MIN_LOG_ARG, params.R * (1.0 - params.Kappa)))
    logG = integral_gamma - damping_sum + log_mirror
    return {
        "logG": logG,
        "integral_gamma": integral_gamma,
        "damping_sum": damping_sum,
        "log_mirror": log_mirror,
    }


def evaluate(params: Parameters) -> Dict[str, float]:
    Xi = compute_Xi(params)
    gain_data = compute_logG(params)
    logG = gain_data["logG"]
    lhs = params.lambda_A * params.K * params.sigma0
    stable_direct = logG < -EPS
    stable_criterion = lhs > Xi + EPS
    result = {
        "lambda_A": params.lambda_A,
        "K": params.K,
        "Omega0": params.Omega0,
        "Xi": Xi,
        "logG": logG,
        "lhs": lhs,
        "G": math.exp(logG),
        "stable_direct": bool(stable_direct),
        "stable_criterion": bool(stable_criterion),
        "near_boundary": abs(logG) <= BOUND_TOL,
        "criterion_margin": lhs - Xi,
    }
    result.update(gain_data)
    return result


# ---------------------------------------------------------------------------
# Logging utilities
# ---------------------------------------------------------------------------


LOG_FIELDS = [
    "alpha",
    "eta",
    "omega",
    "m",
    "epsilon",
    "q",
    "lambda_A",
    "K",
    "Omega0",
    "sigma0",
    "R",
    "Kappa",
    "phi",
    "r0",
    "segment_mode",
    "Xi",
    "logG",
    "lhs",
    "G",
    "stable_direct",
    "stable_criterion",
    "near_boundary",
    "criterion_margin",
    "integral_gamma",
    "damping_sum",
    "log_mirror",
]


def append_log_row(output_dir: Path, params: Parameters, result: Dict[str, float]) -> None:
    log_path = output_dir / "proof_check_log_v6.csv"
    file_exists = log_path.exists()
    record = {field: None for field in LOG_FIELDS}
    for field in (
        "alpha",
        "eta",
        "omega",
        "m",
        "epsilon",
        "q",
        "lambda_A",
        "K",
        "Omega0",
        "sigma0",
        "R",
        "Kappa",
        "phi",
        "r0",
        "segment_mode",
    ):
        record[field] = getattr(params, field) if hasattr(params, field) else None
    for field in (
        "Xi",
        "logG",
        "lhs",
        "G",
        "stable_direct",
        "stable_criterion",
        "near_boundary",
        "criterion_margin",
        "integral_gamma",
        "damping_sum",
        "log_mirror",
    ):
        record[field] = result[field]
    with open(log_path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({k: (float(v) if isinstance(v, (int, float)) else v) for k, v in record.items()})


# ---------------------------------------------------------------------------
# CLI handling
# ---------------------------------------------------------------------------


def add_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--alpha", type=float)
    parser.add_argument("--eta", type=float)
    parser.add_argument("--omega", type=float)
    parser.add_argument("--m", type=int)
    parser.add_argument("--Omega0", type=float)
    parser.add_argument("--epsilon", type=float)
    parser.add_argument("--q", type=float)
    parser.add_argument("--lambdaA", type=float)
    parser.add_argument("--K", type=int)
    parser.add_argument("--sigma0", type=float)
    parser.add_argument("--R", type=float)
    parser.add_argument("--kappa", type=float)
    parser.add_argument("--phi", type=float)
    parser.add_argument("--r0", type=float)
    parser.add_argument("--theta-samples", type=int)
    parser.add_argument("--segment-mode", choices=["uniform", "weighted"])


def apply_overrides(base: Parameters, args: argparse.Namespace) -> Parameters:
    overrides = {}
    for field in (
        "alpha",
        "eta",
        "omega",
        "m",
        "Omega0",
        "epsilon",
        "q",
        "lambdaA",
        "K",
        "sigma0",
        "R",
        "kappa",
        "phi",
        "r0",
        "theta_samples",
    ):
        value = getattr(args, field, None)
        if value is not None:
            key = "Kappa" if field == "kappa" else ("lambda_A" if field == "lambdaA" else field)
            overrides[key] = value
    if args.segment_mode:
        overrides["segment_mode"] = args.segment_mode
    updated = replace(base, **overrides)
    return replace(
        updated,
        lambda_A=clean_float(updated.lambda_A),
        Omega0=clean_float(updated.Omega0),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SSZ proof check v6")
    parser.add_argument("--input", type=str, help="Optional JSON parameter file")
    parser.add_argument("--output", type=str, help="Optional JSON output path")
    parser.add_argument("--no-json", action="store_true", help="Skip writing JSON output")
    add_overrides(parser)
    args = parser.parse_args()

    params = Parameters()
    if args.input:
        params = Parameters.from_json(Path(args.input))
    params = apply_overrides(params, args)

    result = evaluate(params)
    print(json.dumps({k: (float(v) if isinstance(v, (int, float)) else v) for k, v in result.items()}, indent=2))

    output_dir = resolve_output_dir()
    append_log_row(output_dir, params, result)

    if args.no_json:
        return

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = output_dir / "proof_check_result_v6.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "parameters": asdict(params),
        "result": {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in result.items()},
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"[OK] JSON written to {output_path}")


if __name__ == "__main__":
    main()
