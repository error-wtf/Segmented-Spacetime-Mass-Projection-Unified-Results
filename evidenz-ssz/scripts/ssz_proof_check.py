#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Check
===============

Single-point evaluation of the SSZ stability criterion with floating-point
tolerances and the corrected mirror term (applied once per roundtrip).

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import json
import math
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Dict, List

import numpy as np

EPS = 1e-9
LOG_TOL = 1e-6
RES_TOL = 1e-6
MIN_LOG_ARG = 1e-12

TWO_PI = 2.0 * math.pi
HALF_PI = math.pi / 2.0


def clean_float(value: float) -> float:
    return float(f"{value:.12g}")


@dataclass
class Parameters:
    alpha: float = 0.8
    eta: float = 0.05
    omega: float = 0.25
    m: int = 2
    Omega0: float = 0.3
    epsilon: float = 0.1
    q: float = 2.0
    lambda_A: float = 0.02
    K: int = 32
    sigma0: float = 1.0
    R: float = 0.999
    Kappa: float = 0.001
    phi: float = 1.618033988749895
    r0: float = 1.0
    theta_samples: int = 4096
    segment_mode: str = "uniform"

    @classmethod
    def from_json(cls, path: str) -> "Parameters":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


# ---------------------------------------------------------------------------
# Geometry and helper utilities
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
    return float(np.trapz(values, dx=TWO_PI / params.theta_samples))


def segment_angles(params: Parameters, mode: str) -> List[float]:
    if mode.lower() == "weighted":
        resolution = max(params.theta_samples * 2, 4096)
        theta = np.linspace(0.0, TWO_PI, resolution, endpoint=False, dtype=np.float64)
        sigma_vals = sigma_theta(theta, params)
        cumulative = np.cumsum(sigma_vals)
        total = cumulative[-1]
        if total <= MIN_LOG_ARG:
            return [TWO_PI * k / params.K for k in range(params.K)]
        targets = np.linspace(0.0, total, params.K, endpoint=False, dtype=np.float64)
        angles = []
        for target in targets:
            idx = np.searchsorted(cumulative, target, side="left")
            idx = min(max(idx, 1), len(theta) - 1)
            left_val = cumulative[idx - 1]
            right_val = cumulative[idx]
            fraction = 0.0 if right_val == left_val else (target - left_val) / (right_val - left_val)
            theta_left = theta[idx - 1]
            angle = theta_left + fraction * (TWO_PI / resolution)
            angles.append(float(np.clip(angle, 0.0, TWO_PI)))
        return angles
    return [TWO_PI * k / params.K for k in range(params.K)]


# ---------------------------------------------------------------------------
# Gain and analytic bounds
# ---------------------------------------------------------------------------

def compute_L(params: Parameters) -> float:
    theta = theta_grid(params)
    return integrate_over_theta(r_theta(theta, params), params)


def compute_Xi(params: Parameters) -> float:
    Omega_max = params.Omega0 * (1.0 + params.epsilon)
    drive = params.alpha * max(0.0, params.m * Omega_max - params.omega) - params.eta
    L = compute_L(params)
    mirror = math.log(max(MIN_LOG_ARG, params.R * (1.0 - params.Kappa)))
    return drive * L + mirror


def compute_logG(params: Parameters, mode: str) -> Dict[str, float]:
    theta = theta_grid(params)
    integral_gamma = integrate_over_theta(gamma_loc(theta, params) * r_theta(theta, params), params)
    angles = segment_angles(params, mode)
    sigma_vals = sigma_theta(np.array(angles, dtype=np.float64), params)
    damping_sum = params.lambda_A * float(np.sum(sigma_vals))
    log_mirror = math.log(max(MIN_LOG_ARG, params.R * (1.0 - params.Kappa)))
    logG = integral_gamma - damping_sum + log_mirror
    return {
        "logG": logG,
        "integral_gamma": integral_gamma,
        "damping_sum": damping_sum,
        "log_mirror": log_mirror,
    }


def evaluate_stability(params: Parameters) -> Dict[str, float]:
    Xi = compute_Xi(params)
    gain_data = compute_logG(params, params.segment_mode)
    logG = gain_data["logG"]
    lhs = params.lambda_A * params.K * params.sigma0
    stable_direct = logG < -EPS
    near_boundary = abs(logG) <= LOG_TOL
    stable_criterion = lhs > Xi + EPS
    resonant = abs(params.omega - params.m * params.Omega0) <= RES_TOL
    result = {
        "lambda_A": params.lambda_A,
        "K": params.K,
        "Omega0": params.Omega0,
        "Xi": Xi,
        "logG": logG,
        "lhs": lhs,
        "stable_direct": bool(stable_direct),
        "stable_criterion": bool(stable_criterion),
        "near_boundary": bool(near_boundary),
        "criterion_margin": lhs - Xi,
        "resonant": bool(resonant),
    }
    result.update(gain_data)
    return result


# ---------------------------------------------------------------------------
# Parameter sweep utilities
# ---------------------------------------------------------------------------

def sweep_parameter_space(base: Parameters,
                          lambda_values: List[float],
                          k_values: List[int],
                          omega0_values: List[float]) -> List[Dict[str, float]]:
    results: List[Dict[str, float]] = []
    for lam in lambda_values:
        for K in k_values:
            for omega0 in omega0_values:
                params = replace(base, lambda_A=lam, K=K, Omega0=omega0)
                params.lambda_A = clean_float(params.lambda_A)
                params.Omega0 = clean_float(params.Omega0)
                results.append(evaluate_stability(params))
    return results


# ---------------------------------------------------------------------------
# Reporting utilities
# ---------------------------------------------------------------------------

def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_result(result: Dict[str, float]) -> str:
    status = "stable" if result["stable_direct"] and result["stable_criterion"] else "unstable"
    return (
        f"{status.upper()}: direct={result['stable_direct']} criterion={result['stable_criterion']} "
        f"| lambda_A={result['lambda_A']:.5f} | K={int(result['K'])} | Omega0={result['Omega0']:.5f} "
        f"| G={math.exp(result['logG']):.6f} | logG={result['logG']:.6e} | Xi={result['Xi']:.6f} | lhs={result['lhs']:.6f}"
    )


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SSZ stability proof checker")
    parser.add_argument("--input", type=str, help="Optional JSON file with parameters")
    parser.add_argument("--output", type=str, default="d:/extended_results/proof_reports",
                        help="Directory for JSON report output")
    parser.add_argument("--no-sweep", action="store_true", help="Skip parameter sweep")
    args = parser.parse_args()

    base_params = Parameters()
    if args.input:
        base_params = Parameters.from_json(args.input)

    primary = evaluate_stability(base_params)
    print(format_result(primary))

    output_dir = ensure_output_dir(Path(args.output))
    report_path = output_dir / "proof_report.json"
    report = {
        "base_parameters": asdict(base_params),
        "primary_result": primary,
    }

    if not args.no_sweep:
        factors = [0.5, 1.0, 1.5, 2.0]
        lambda_values = sorted({clean_float(base_params.lambda_A * f) for f in factors})
        k_values = sorted({max(1, int(base_params.K * f)) for f in (0.5, 1.0, 1.5)})
        omega_factors = [0.8, 1.0, 1.2]
        omega0_values = sorted({clean_float(base_params.Omega0 * f) for f in omega_factors})

        sweep_results = sweep_parameter_space(base_params, lambda_values, k_values, omega0_values)
        report["sweep_results"] = sweep_results
        agreements = sum(1 for r in sweep_results if r["stable_direct"] == r["stable_criterion"])
        report["summary"] = {
            "agreements": agreements,
            "total": len(sweep_results),
        }

        print(f"\nSweep summary: {agreements} / {len(sweep_results)} decisions agree")
        if sweep_results:
            print("First sweep sample:")
            print(format_result(sweep_results[0]))

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Report written to {report_path}")


if __name__ == "__main__":
    main()
