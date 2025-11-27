#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Sweep
===============

Grid and adaptive sweeps for the SSZ stabilization criterion versus direct gain.
Builds upon the numerical kernels used in ssz_proof_check.py and extends them with
parameter grids, boundary searches, and reporting utilities.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import csv
import json
import math
import os
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

try:
    import matplotlib.pyplot as plt  # type: ignore

    HAS_MATPLOTLIB = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_MATPLOTLIB = False

import bisect

PI = math.pi
TWO_PI = 2.0 * math.pi


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
    R: float = 0.98
    Kappa: float = 0.05
    phi: float = 1.618033988749895
    r0: float = 1.0
    theta_samples: int = 2000
    segment_mode: str = "uniform"


# ---------------------------------------------------------------------------
# Core kernels
# ---------------------------------------------------------------------------

def r_theta(theta: float, params: Parameters) -> float:
    return params.r0 * (params.phi ** (theta / (PI / 2.0)))

def sigma_theta(theta: float, params: Parameters) -> float:
    return params.sigma0 * (params.phi ** (theta / (PI / 2.0)))

def gamma_loc(theta: float, params: Parameters) -> float:
    omega_local = params.omega - params.m * params.Omega0 * (1.0 + params.eta * math.cos(theta))
    denominator = max(1e-12, r_theta(theta, params) ** params.alpha)
    numerator = params.m * params.Omega0 * math.sin(theta)
    return math.tanh(numerator / denominator) * omega_local

def trapezoid_integral(func, params: Parameters) -> float:
    n = max(8, params.theta_samples)
    h = TWO_PI / n
    total = 0.5 * (func(0.0, params) + func(TWO_PI, params))
    for k in range(1, n):
        theta = k * h
        total += func(theta, params)
    return total * h

def uniform_segment_angles(params: Parameters) -> List[float]:
    return [TWO_PI * k / params.K for k in range(params.K)]

def weighted_segment_angles(params: Parameters, resolution: int = 4096) -> List[float]:
    samples = max(resolution, params.theta_samples * 2)
    step = TWO_PI / samples
    cumulative = [0.0]
    total = 0.0
    for idx in range(samples):
        theta = idx * step
        total += sigma_theta(theta, params)
        cumulative.append(total)
    if total == 0.0:
        return uniform_segment_angles(params)
    targets = [total * k / params.K for k in range(params.K)]
    angles: List[float] = []
    for target in targets:
        pos = bisect.bisect_left(cumulative, target)
        if pos == 0:
            angles.append(0.0)
            continue
        if pos >= len(cumulative):
            angles.append(TWO_PI)
            continue
        left_val = cumulative[pos - 1]
        right_val = cumulative[pos]
        fraction = 0.0 if right_val == left_val else (target - left_val) / (right_val - left_val)
        theta_left = (pos - 1) * step
        angle = theta_left + fraction * step
        angles.append(min(TWO_PI, max(0.0, angle)))
    return angles

def get_segment_angles(params: Parameters) -> List[float]:
    mode = params.segment_mode.lower()
    if mode == "weighted":
        return weighted_segment_angles(params)
    return uniform_segment_angles(params)


# ---------------------------------------------------------------------------
# Gain and bounds
# ---------------------------------------------------------------------------

def compute_Xi(params: Parameters) -> float:
    def integrand(theta: float, p: Parameters) -> float:
        return abs(gamma_loc(theta, p))
    integral_abs = trapezoid_integral(integrand, params)
    Omega_max = params.Omega0 * (1.0 + params.epsilon)
    L = trapezoid_integral(lambda th, p: r_theta(th, p), params)
    correction = params.alpha * max(0.0, params.m * Omega_max - params.omega) - params.eta
    Xi = correction * L + math.log(max(1e-12, params.R * (1.0 - params.Kappa)))
    return Xi + integral_abs

def compute_logG(params: Parameters) -> float:
    integral_gamma = trapezoid_integral(lambda th, p: gamma_loc(th, p), params)
    angles = get_segment_angles(params)
    damping_sum = 0.0
    for theta in angles:
        damping_sum += params.lambda_A * sigma_theta(theta, params)
    log_mirror = params.K * math.log(max(1e-12, params.R * (1.0 - params.Kappa)))
    log_G = integral_gamma - damping_sum + log_mirror
    return log_G

def evaluate_stability(params: Parameters) -> Dict[str, float]:
    Xi = compute_Xi(params)
    logG = compute_logG(params)
    lhs = params.lambda_A * params.K * params.sigma0
    stable_criterion = lhs > Xi
    stable_direct = logG < 0.0
    return {
        "lambda_A": params.lambda_A,
        "K": params.K,
        "Omega0": params.Omega0,
        "Xi": Xi,
        "logG": logG,
        "lhs": lhs,
        "stable_criterion": bool(stable_criterion),
        "stable_direct": bool(stable_direct),
        "agree": bool(stable_criterion == stable_direct),
    }


# ---------------------------------------------------------------------------
# Sweeps and boundary searches
# ---------------------------------------------------------------------------

def run_grid_sweep(base: Parameters,
                   lambda_grid: Sequence[float],
                   k_grid: Sequence[int],
                   omega_grid: Sequence[float]) -> List[Dict[str, float]]:
    results: List[Dict[str, float]] = []
    for lam in lambda_grid:
        for K in k_grid:
            for omega0 in omega_grid:
                params = replace(base, lambda_A=lam, K=K, Omega0=omega0)
                results.append(evaluate_stability(params))
    return results

def bisection_lambda_crit(base: Parameters,
                          K: int,
                          Omega0: float,
                          lambda_max: float,
                          target: str,
                          tol: float = 1e-4,
                          max_iter: int = 40) -> Optional[float]:
    params = replace(base, K=K, Omega0=Omega0)
    left, right = 0.0, lambda_max
    setattr(params, "lambda_A", left)
    eval_left = evaluate_stability(params)
    left_ok = eval_left["stable_direct"] if target == "direct" else eval_left["stable_criterion"]
    setattr(params, "lambda_A", right)
    eval_right = evaluate_stability(params)
    right_ok = eval_right["stable_direct"] if target == "direct" else eval_right["stable_criterion"]
    if not right_ok:
        return None
    if left_ok:
        return left
    for _ in range(max_iter):
        mid = 0.5 * (left + right)
        setattr(params, "lambda_A", mid)
        eval_mid = evaluate_stability(params)
        mid_ok = eval_mid["stable_direct"] if target == "direct" else eval_mid["stable_criterion"]
        if mid_ok:
            right = mid
        else:
            left = mid
        if right - left < tol:
            break
    return max(0.0, right)

def integer_binary_search_K(base: Parameters,
                            lambda_A: float,
                            Omega0: float,
                            K_min: int,
                            K_max: int,
                            target: str) -> Optional[int]:
    def is_stable(K_value: int) -> bool:
        params = replace(base, lambda_A=lambda_A, Omega0=Omega0, K=K_value)
        res = evaluate_stability(params)
        return res["stable_direct"] if target == "direct" else res["stable_criterion"]
    low = max(2, K_min)
    high = max(low, K_max)
    if not is_stable(high):
        return None
    while low < high:
        mid = (low + high) // 2
        if is_stable(mid):
            high = mid
        else:
            low = mid + 1
    return high

def find_boundaries(base: Parameters,
                    omega_grid: Sequence[float],
                    lambda_max: float,
                    K_max: int) -> List[Dict[str, float]]:
    boundaries: List[Dict[str, float]] = []
    for omega0 in omega_grid:
        lambda_crit_criterion = bisection_lambda_crit(base, base.K, omega0, lambda_max, target="criterion")
        lambda_crit_direct = bisection_lambda_crit(base, base.K, omega0, lambda_max, target="direct")
        K_crit_criterion = integer_binary_search_K(base, base.lambda_A, omega0, 2, K_max, target="criterion")
        K_crit_direct = integer_binary_search_K(base, base.lambda_A, omega0, 2, K_max, target="direct")
        boundaries.append({
            "Omega0": omega0,
            "lambdaA_crit_criterion": lambda_crit_criterion,
            "lambdaA_crit_direct": lambda_crit_direct,
            "K_crit_criterion": K_crit_criterion,
            "K_crit_direct": K_crit_direct,
        })
    return boundaries


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def write_csv(path: Path, rows: List[Dict[str, float]], fieldnames: Sequence[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def summarize_results(results: List[Dict[str, float]]) -> Dict[str, float]:
    total = len(results)
    agree = sum(1 for r in results if r["agree"])
    disagree_points = [r for r in results if not r["agree"]]
    summary = {
        "total_points": total,
        "agreements": agree,
        "agreement_ratio": (agree / total) if total else 0.0,
        "disagreements": len(disagree_points),
        "max_lambdaA_discrepancy": max((abs(r["Xi"] - r["lhs"]) for r in disagree_points), default=0.0),
    }
    return summary

def build_heatmap_matrix(results: List[Dict[str, float]],
                         lambda_grid: Sequence[float],
                         k_grid: Sequence[int]) -> List[List[float]]:
    matrix = [[0.0 for _ in lambda_grid] for _ in k_grid]
    index_map = {(round(r["lambda_A"], 6), int(r["K"])): r for r in results}
    for i, K in enumerate(k_grid):
        for j, lam in enumerate(lambda_grid):
            key = (round(lam, 6), int(K))
            res = index_map.get(key)
            if res:
                matrix[i][j] = 1.0 if res["stable_direct"] else 0.0
    return matrix

def maybe_plot_outputs(output_dir: Path,
                       lambda_grid: Sequence[float],
                       k_grid: Sequence[int],
                       results: List[Dict[str, float]],
                       boundaries: List[Dict[str, float]]) -> None:
    if not HAS_MATPLOTLIB:
        return
    heatmap = build_heatmap_matrix(results, lambda_grid, k_grid)
    plt.figure(figsize=(8, 6))
    plt.imshow(heatmap, origin="lower", aspect="auto",
               extent=[min(lambda_grid), max(lambda_grid), min(k_grid), max(k_grid)],
               cmap="viridis")
    plt.colorbar(label="Stable (direct)")
    plt.xlabel("lambda_A")
    plt.ylabel("K")
    plt.title("SSZ Stability Heatmap (direct criterion)")
    plt.tight_layout()
    plt.savefig(output_dir / "heatmap_stability.png", dpi=180)
    plt.close()
    omega_values = [b["Omega0"] for b in boundaries]
    criterion_vals = [b["lambdaA_crit_criterion"] or math.nan for b in boundaries]
    direct_vals = [b["lambdaA_crit_direct"] or math.nan for b in boundaries]
    plt.figure(figsize=(7, 4))
    plt.plot(omega_values, criterion_vals, "o-", label="criterion")
    plt.plot(omega_values, direct_vals, "s--", label="direct")
    plt.xlabel("Omega0")
    plt.ylabel("lambda_A crit")
    plt.title("Boundary comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "boundary_lambdaA_vs_K.png", dpi=180)
    plt.close()


# ---------------------------------------------------------------------------
# CLI utilities
# ---------------------------------------------------------------------------

def load_base_parameters(input_path: Optional[Path], fallback_dir: Path) -> Parameters:
    source: Optional[Path] = None
    if input_path and input_path.exists():
        source = input_path
    else:
        candidate = fallback_dir / "proof_report.json"
        if candidate.exists():
            source = candidate
    if source:
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)
        payload = data.get("base_parameters", data)
        return Parameters(**payload)
    return Parameters()

def update_params_from_args(params: Parameters, args: argparse.Namespace) -> Parameters:
    updated = params
    if args.theta_samples:
        updated = replace(updated, theta_samples=args.theta_samples)
    if args.segment_mode:
        updated = replace(updated, segment_mode=args.segment_mode)
    if args.lambdaA is not None:
        updated = replace(updated, lambda_A=args.lambdaA)
    if args.K is not None:
        updated = replace(updated, K=args.K)
    if args.Omega0 is not None:
        updated = replace(updated, Omega0=args.Omega0)
    if args.R is not None:
        updated = replace(updated, R=args.R)
    if args.Kappa is not None:
        updated = replace(updated, Kappa=args.Kappa)
    return updated


def parse_float_grid(spec: Optional[str], default: Sequence[float]) -> List[float]:
    if not spec:
        return list(default)
    text = spec.strip()
    if text.startswith("linspace:"):
        body = text.split(":", 1)[1]
        parts = [p.strip() for p in body.split(",") if p.strip()]
        if len(parts) != 3:
            raise ValueError("linspace specification must be linspace:start,stop,count")
        start, stop = float(parts[0]), float(parts[1])
        count = int(float(parts[2]))
        if count < 2:
            return [start, stop]
        step = (stop - start) / (count - 1)
        return [start + i * step for i in range(count)]
    values = [float(p.strip()) for p in text.split(",") if p.strip()]
    return values


def parse_int_grid(spec: Optional[str], default: Sequence[int]) -> List[int]:
    if not spec:
        return list(default)
    text = spec.strip()
    values = [int(float(p.strip())) for p in text.split(",") if p.strip()]
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="SSZ proof sweep tool")
    parser.add_argument("--grid", action="store_true", help="Execute full parameter grid sweep")
    parser.add_argument("--find-lambdaA-crit", action="store_true", help="Find lambda_A critical values via bisection")
    parser.add_argument("--find-K-crit", action="store_true", help="Find K critical values via integer search")
    parser.add_argument("--input", type=str, help="Optional JSON with base parameters")
    parser.add_argument("--output", type=str, default="d:/extended_results/proof_reports", help="Directory for reports")
    parser.add_argument("--theta-samples", type=int, help="Number of theta samples for integration")
    parser.add_argument("--segment-mode", choices=["uniform", "weighted"], help="Segment placement mode")
    parser.add_argument("--lambdaA", type=float, help="Override lambda_A")
    parser.add_argument("--K", type=int, help="Override K")
    parser.add_argument("--Omega0", type=float, help="Override Omega0")
    parser.add_argument("--R", type=float, help="Override mirror reflectivity R")
    parser.add_argument("--Kappa", type=float, help="Override coupling loss Kappa")
    parser.add_argument("--lambda-max", type=float, default=0.2, help="Upper bound for lambda_A bisection")
    parser.add_argument("--K-max", type=int, default=128, help="Upper bound for K search")
    parser.add_argument("--lambda-grid", type=str, help="Comma list or linspace:start,stop,count for lambda_A grid")
    parser.add_argument("--K-grid", type=str, help="Comma-separated list for K grid")
    parser.add_argument("--Omega0-grid", type=str, help="Comma list or linspace:start,stop,count for Omega0 grid")

    args = parser.parse_args()
    output_dir = ensure_output_dir(Path(args.output))
    base_params = load_base_parameters(Path(args.input) if args.input else None, output_dir)
    base_params = update_params_from_args(base_params, args)

    lambda_grid = parse_float_grid(args.lambda_grid, [0.0, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05])
    k_grid = parse_int_grid(args.K_grid, [8, 16, 24, 32, 40, 48, 64])
    omega_grid = parse_float_grid(args.Omega0_grid, [0.2, 0.3, 0.4])

    performed_any_action = False
    summary_payload: Dict[str, object] = {
        "base_parameters": asdict(base_params),
        "actions": [],
    }

    if args.grid or (not args.find_lambdaA_crit and not args.find_K_crit):
        performed_any_action = True
        grid_results = run_grid_sweep(base_params, lambda_grid, k_grid, omega_grid)
        write_csv(output_dir / "proof_sweep_results.csv", grid_results,
                  ["lambda_A", "K", "Omega0", "Xi", "logG", "lhs", "stable_criterion", "stable_direct", "agree"])
        summary = summarize_results(grid_results)
        summary_payload["grid_results"] = summary
        summary_payload["actions"].append("grid")
        boundaries = find_boundaries(base_params, omega_grid, args.lambda_max, args.K_max)
        write_csv(output_dir / "stability_boundaries.csv", boundaries,
                  ["Omega0", "lambdaA_crit_criterion", "lambdaA_crit_direct", "K_crit_criterion", "K_crit_direct"])
        summary_payload["boundaries"] = boundaries
        maybe_plot_outputs(output_dir, lambda_grid, k_grid, grid_results, boundaries)
        agree_pct = summary.get("agreement_ratio", 0.0) * 100.0
        print(f"[GRID] points={summary.get('total_points', 0)} -> agree(criterion,direct)={agree_pct:.1f}%")
        for item in boundaries:
            print("[BOUNDARY] Omega0={:.2f}: lambdaA_crit (criterion)={} (direct)={}".format(
                item["Omega0"], item["lambdaA_crit_criterion"], item["lambdaA_crit_direct"]))
            print("[BOUNDARY] Omega0={:.2f}: K_crit (criterion)={} (direct)={}".format(
                item["Omega0"], item["K_crit_criterion"], item["K_crit_direct"]))

    if args.find_lambdaA_crit:
        performed_any_action = True
        K_value = args.K if args.K is not None else base_params.K
        Omega0_value = args.Omega0 if args.Omega0 is not None else base_params.Omega0
        criterion_val = bisection_lambda_crit(base_params, K_value, Omega0_value, args.lambda_max, target="criterion")
        direct_val = bisection_lambda_crit(base_params, K_value, Omega0_value, args.lambda_max, target="direct")
        record = {
            "K": K_value,
            "Omega0": Omega0_value,
            "lambdaA_crit_criterion": criterion_val,
            "lambdaA_crit_direct": direct_val,
        }
        summary_payload.setdefault("lambdaA_crit_search", []).append(record)
        print("[LAMBDA_CRIT] K={} Omega0={}: criterion={} direct={}".format(
            K_value, Omega0_value, criterion_val, direct_val))

    if args.find_K_crit:
        performed_any_action = True
        lambda_value = args.lambdaA if args.lambdaA is not None else base_params.lambda_A
        Omega0_value = args.Omega0 if args.Omega0 is not None else base_params.Omega0
        criterion_val = integer_binary_search_K(base_params, lambda_value, Omega0_value, 2, args.K_max, target="criterion")
        direct_val = integer_binary_search_K(base_params, lambda_value, Omega0_value, 2, args.K_max, target="direct")
        record = {
            "lambda_A": lambda_value,
            "Omega0": Omega0_value,
            "K_crit_criterion": criterion_val,
            "K_crit_direct": direct_val,
        }
        summary_payload.setdefault("K_crit_search", []).append(record)
        print("[K_CRIT] lambda_A={} Omega0={}: criterion={} direct={}".format(
            lambda_value, Omega0_value, criterion_val, direct_val))

    if not performed_any_action:
        print("No action requested. Use --grid, --find-lambdaA-crit, or --find-K-crit.")

    with open(output_dir / "proof_sweep_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)
    print(f"[OK] Outputs stored in {output_dir}")


if __name__ == "__main__":  # pragma: no cover
    main()
