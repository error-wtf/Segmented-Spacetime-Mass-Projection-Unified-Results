#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Sweep v4
==================

Robust stability grid and boundary search for SSZ damping with floating-point
safeguards, deterministic segment placement, and optional self-tests.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import csv
import json
import math
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:  # Optional plotting dependency
    import matplotlib.pyplot as plt  # type: ignore

    HAS_MPL = True
except ImportError:  # pragma: no cover
    HAS_MPL = False

# Numerical tolerances
EPS = 1e-9
BOUND_TOL = 1e-6
MIN_LOG_ARG = 1e-12

# Integration constants
PI = math.pi
TWO_PI = 2.0 * math.pi
HALF_PI = math.pi / 2.0

DEFAULT_OUTPUT_DIR = Path("d:/extended_results/proof_reports")


def clean_float(value: float) -> float:
    return float(f"{value:.12g}")


@dataclass
class Parameters:
    alpha: float = 1.2
    eta: float = 0.0
    omega: float = 0.20
    m: int = 4
    Omega0: float = 0.3
    epsilon: float = 0.2
    q: float = 3.0
    lambda_A: float = 0.02
    K: int = 8
    sigma0: float = 0.5
    R: float = 0.9999
    Kappa: float = 1e-5
    phi: float = 1.618033988749895
    r0: float = 1.0
    theta_samples: int = 4096


# ---------------------------------------------------------------------------
# Geometry helpers
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


def segment_angles(params: Parameters, mode: str) -> np.ndarray:
    if mode.lower() == "weighted":
        return weighted_segment_angles(params)
    return np.linspace(0.0, TWO_PI, params.K, endpoint=False, dtype=np.float64)


# ---------------------------------------------------------------------------
# Gain, Xi, and stability diagnostics
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


def evaluate_stability(params: Parameters, mode: str) -> Dict[str, float]:
    Xi = compute_Xi(params)
    gain_data = compute_logG(params, mode)
    logG = gain_data["logG"]
    lhs = params.lambda_A * params.K * params.sigma0
    stable_direct = logG < -EPS
    stable_criterion = lhs > Xi + EPS
    return {
        "Xi": Xi,
        "logG": logG,
        "lhs": lhs,
        "stable_direct": bool(stable_direct),
        "stable_criterion": bool(stable_criterion),
        "near_boundary": abs(logG) <= BOUND_TOL,
        "criterion_margin": lhs - Xi,
        **gain_data,
    }


# ---------------------------------------------------------------------------
# Utility functions for grids and bracketing
# ---------------------------------------------------------------------------


def generate_float_grid(start: float, stop: float, count: int) -> List[float]:
    if count <= 1:
        return [clean_float(start)]
    return [clean_float(start + i * (stop - start) / (count - 1)) for i in range(count)]


def bracket_and_bisect(func, a: float, b: float, tol: float = 1e-6, max_iter: int = 60) -> Optional[float]:
    fa = func(a)
    fb = func(b)
    if fa * fb > 0.0:
        return None
    left, right = a, b
    f_left, f_right = fa, fb
    for _ in range(max_iter):
        mid = 0.5 * (left + right)
        f_mid = func(mid)
        if abs(f_mid) <= tol or (right - left) <= tol:
            return mid
        if f_left * f_mid <= 0.0:
            right, f_right = mid, f_mid
        else:
            left, f_left = mid, f_mid
    return mid


def integer_binary_search_K(base: Parameters,
                            lambda_A: float,
                            Omega0: float,
                            mode: str,
                            target: str,
                            K_min: int = 1,
                            K_max: int = 256) -> Optional[int]:
    def is_stable(K_val: int) -> bool:
        params = replace(base, lambda_A=lambda_A, Omega0=Omega0, K=K_val)
        res = evaluate_stability(params, mode)
        return res["stable_direct"] if target == "direct" else res["stable_criterion"]

    low, high = max(1, K_min), max(K_min, K_max)
    if not is_stable(high):
        return None
    while low < high:
        mid = (low + high) // 2
        if is_stable(mid):
            high = mid
        else:
            low = mid + 1
    return high


# ---------------------------------------------------------------------------
# Sweep and boundary calculations
# ---------------------------------------------------------------------------


def run_grid_sweep(base: Parameters,
                   lambda_grid: Sequence[float],
                   k_grid: Sequence[int],
                   omega_grid: Sequence[float],
                   segment_modes: Iterable[str]) -> List[Dict[str, float]]:
    results: List[Dict[str, float]] = []
    for mode in segment_modes:
        for Omega0 in omega_grid:
            for K in k_grid:
                for lam in lambda_grid:
                    params = replace(base, lambda_A=lam, K=K, Omega0=Omega0)
                    params = replace(params, lambda_A=clean_float(params.lambda_A), Omega0=clean_float(params.Omega0))
                    eval_res = evaluate_stability(params, mode)
                    record = {
                        "omega": params.omega,
                        "m": params.m,
                        "Omega0": params.Omega0,
                        "epsilon": params.epsilon,
                        "q": params.q,
                        "R": params.R,
                        "Kappa": params.Kappa,
                        "phi": params.phi,
                        "r0": params.r0,
                        "sigma0": params.sigma0,
                        "K": params.K,
                        "lambda_A": params.lambda_A,
                        "segment_mode": mode,
                    }
                    record.update(eval_res)
                    results.append(record)
    return results


def bisection_lambda_crit(base: Parameters,
                          K: int,
                          Omega0: float,
                          mode: str,
                          target: str,
                          lam_max: float = 0.2,
                          tol: float = 1e-6) -> Optional[float]:
    def func(lam: float) -> float:
        params = replace(base, K=K, Omega0=Omega0, lambda_A=lam)
        res = evaluate_stability(params, mode)
        return res["logG"] if target == "direct" else res["criterion_margin"]

    result = bracket_and_bisect(func, 0.0, lam_max, tol=tol)
    return clean_float(result) if result is not None else None


def compute_boundaries(base: Parameters,
                       omega_grid: Sequence[float],
                       segment_modes: Iterable[str],
                       lam_max: float,
                       K_max: int) -> List[Dict[str, float]]:
    boundaries: List[Dict[str, float]] = []
    for mode in segment_modes:
        for Omega0 in omega_grid:
            lam_direct = bisection_lambda_crit(base, base.K, Omega0, mode, "direct", lam_max)
            lam_crit = bisection_lambda_crit(base, base.K, Omega0, mode, "criterion", lam_max)
            K_direct = integer_binary_search_K(base, base.lambda_A, Omega0, mode, "direct", 1, K_max)
            K_crit = integer_binary_search_K(base, base.lambda_A, Omega0, mode, "criterion", 1, K_max)
            boundaries.append({
                "Omega0": clean_float(Omega0),
                "segment_mode": mode,
                "K_reference": base.K,
                "lambdaA_crit_direct": lam_direct,
                "lambdaA_crit_criterion": lam_crit,
                "K_crit_direct": K_direct,
                "K_crit_criterion": K_crit,
                "lambdaA_diff": None if lam_direct is None or lam_crit is None else clean_float(abs(lam_direct - lam_crit)),
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
            writer.writerow({k: (float(v) if isinstance(v, (int, float)) else v) for k, v in row.items()})


def summarize(results: List[Dict[str, float]], boundaries: List[Dict[str, float]]) -> Dict[str, float]:
    total = len(results)
    agreements = sum(1 for r in results if r["stable_direct"] == r["stable_criterion"])
    ratio = agreements / total if total else 0.0
    diffs = [b["lambdaA_diff"] for b in boundaries if b["lambdaA_diff"] is not None]
    max_diff = max(diffs) if diffs else 0.0
    return {
        "points": total,
        "agreement_ratio": ratio,
        "max_abs_diff_lambdaAcrit": max_diff,
        "notes": "See CSV outputs for detailed stability bands.",
    }


def build_heatmap(results: List[Dict[str, float]],
                  lambda_grid: Sequence[float],
                  k_grid: Sequence[int],
                  mode: str) -> Tuple[np.ndarray, np.ndarray]:
    stable = np.zeros((len(k_grid), len(lambda_grid)), dtype=np.float64)
    disagreement = np.zeros_like(stable)
    lookup = {}
    for r in results:
        if r["segment_mode"] == mode:
            lookup[(clean_float(r["lambda_A"]), int(r["K"]))] = r
    for i, K in enumerate(k_grid):
        for j, lam in enumerate(lambda_grid):
            key = (clean_float(lam), int(K))
            entry = lookup.get(key)
            if entry:
                stable[i, j] = 1.0 if entry["stable_direct"] else 0.0
                disagreement[i, j] = 1.0 if entry["stable_direct"] != entry["stable_criterion"] else 0.0
    return stable, disagreement


def plot_outputs(output_dir: Path,
                 lambda_grid: Sequence[float],
                 k_grid: Sequence[int],
                 omega_grid: Sequence[float],
                 results: List[Dict[str, float]],
                 boundaries: List[Dict[str, float]],
                 segment_modes: Iterable[str]) -> None:
    if not HAS_MPL:
        return
    lambda_arr = np.array(lambda_grid, dtype=np.float64)
    k_arr = np.array(k_grid, dtype=np.float64)
    for mode in segment_modes:
        stable_matrix, disagreement_matrix = build_heatmap(results, lambda_grid, k_grid, mode)
        extent = [lambda_arr.min(), lambda_arr.max(), k_arr.min(), k_arr.max()]
        plt.figure(figsize=(9, 6))
        plt.imshow(stable_matrix, origin="lower", aspect="auto", extent=extent, cmap="viridis")
        plt.colorbar(label="Stable (direct)")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"SSZ Stability Heatmap ({mode}) v4")
        plt.tight_layout()
        plt.savefig(output_dir / f"heatmap_stability_{mode}_v4.png", dpi=180)
        plt.close()

        plt.figure(figsize=(9, 6))
        plt.imshow(disagreement_matrix, origin="lower", aspect="auto", extent=extent, cmap="magma")
        plt.colorbar(label="Disagreement")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"Stability Disagreement Map ({mode}) v4")
        plt.tight_layout()
        plt.savefig(output_dir / f"disagreement_map_{mode}_v4.png", dpi=180)
        plt.close()

        omega_vals = sorted({b["Omega0"] for b in boundaries if b["segment_mode"] == mode})
        direct_vals = [next((b["lambdaA_crit_direct"] for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), math.nan) for omega in omega_vals]
        criterion_vals = [next((b["lambdaA_crit_criterion"] for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), math.nan) for omega in omega_vals]
        plt.figure(figsize=(7, 4))
        plt.plot(omega_vals, direct_vals, "o-", label="direct")
        plt.plot(omega_vals, criterion_vals, "s--", label="criterion")
        plt.xlabel("Omega0")
        plt.ylabel("lambda_A crit")
        plt.title(f"lambda_A crit vs Omega0 ({mode}) v4")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"boundary_lambdaA_vs_Omega0_{mode}_v4.png", dpi=180)
        plt.close()


# ---------------------------------------------------------------------------
# Self-test utilities
# ---------------------------------------------------------------------------


def run_self_tests(base: Parameters, lambda_grid: Sequence[float], k_grid: Sequence[int], omega_grid: Sequence[float]) -> None:
    # Mirror fix check
    log_mirror_ref = math.log(max(MIN_LOG_ARG, base.R * (1.0 - base.Kappa)))
    params = base
    gain_data = compute_logG(params, "uniform")
    assert abs(gain_data["log_mirror"] - log_mirror_ref) <= 1e-12

    # Agreement ratio check using a tiny grid
    mini_results = run_grid_sweep(base, lambda_grid[:5], k_grid[:3], omega_grid[:2], ["uniform"])
    agreements = sum(1 for r in mini_results if r["stable_direct"] == r["stable_criterion"])
    ratio = agreements / len(mini_results) if mini_results else 1.0
    assert ratio >= 0.8

    # Monotonicity check (lambdaA crit increasing with Omega0 in uniform mode)
    boundaries = compute_boundaries(base, omega_grid[:5], ["uniform"], 0.1, 64)
    uniform_bounds = [b for b in boundaries if b["segment_mode"] == "uniform" and b["lambdaA_crit_direct"] is not None]
    if len(uniform_bounds) >= 2:
        lam_vals = [b["lambdaA_crit_direct"] for b in uniform_bounds]
        if all(v is not None for v in lam_vals):
            diffs = np.diff(lam_vals)
            assert np.all(diffs >= -1e-6)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SSZ proof sweep v4")
    parser.add_argument("--grid", action="store_true", help="Run full parameter grid sweep")
    parser.add_argument("--find-lambdaA-crit", action="store_true", help="Locate lambda_A critical values")
    parser.add_argument("--find-K-crit", action="store_true", help="Locate K critical values")
    parser.add_argument("--self-test", action="store_true", help="Run embedded self-tests and exit")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--theta-samples", type=int, default=4096, help="Theta sample count")
    parser.add_argument("--segment-mode", action="append", choices=["uniform", "weighted"], help="Segment mode(s) to include")
    parser.add_argument("--lambdaA", type=float, help="Reference lambda_A for boundary searches")
    parser.add_argument("--K", type=int, help="Reference K for boundary searches")
    parser.add_argument("--Omega0", type=float, help="Reference Omega0 for boundary searches")
    parser.add_argument("--lambda-max", type=float, default=0.2, help="Upper bound for lambda_A searches")
    parser.add_argument("--K-max", type=int, default=256, help="Upper bound for K searches")
    parser.add_argument("--no-grid", action="store_true", help="Skip automatic grid sweep")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()
    output_dir = ensure_output_dir(Path(args.output))
    base = Parameters(theta_samples=args.theta_samples)
    if args.lambdaA is not None:
        base = replace(base, lambda_A=args.lambdaA)
    if args.K is not None:
        base = replace(base, K=args.K)
    if args.Omega0 is not None:
        base = replace(base, Omega0=args.Omega0)

    segment_modes = args.segment_mode if args.segment_mode else ["uniform", "weighted"]
    lambda_grid = generate_float_grid(0.0, 0.15, 301)
    k_grid = [1, 2, 4, 8, 12, 16, 24, 32]
    omega_grid = generate_float_grid(0.1, 0.6, 11)

    if args.self_test:
        run_self_tests(base, lambda_grid, k_grid, omega_grid)
        print("Self-tests passed.")
        return

    summary_data: Dict[str, object] = {
        "base_parameters": asdict(base),
        "segment_modes": segment_modes,
        "actions": [],
    }

    if args.grid and not args.no_grid:
        results = run_grid_sweep(base, lambda_grid, k_grid, omega_grid, segment_modes)
        write_csv(output_dir / "proof_sweep_results_v4.csv", results,
                  ["omega", "m", "Omega0", "epsilon", "q", "R", "Kappa", "phi", "r0", "sigma0",
                   "K", "lambda_A", "segment_mode", "Xi", "logG", "lhs", "stable_direct",
                   "stable_criterion", "near_boundary", "criterion_margin", "integral_gamma",
                   "damping_sum", "log_mirror"])
        boundaries = compute_boundaries(base, omega_grid, segment_modes, args.lambda_max, args.K_max)
        write_csv(output_dir / "stability_boundaries_v4.csv", boundaries,
                  ["Omega0", "segment_mode", "K_reference", "lambdaA_crit_direct", "lambdaA_crit_criterion",
                   "K_crit_direct", "K_crit_criterion", "lambdaA_diff"])
        summary_metrics = summarize(results, boundaries)
        summary_data["grid_summary"] = summary_metrics
        summary_data["actions"].append("grid")
        plot_outputs(output_dir, lambda_grid, k_grid, omega_grid, results, boundaries, segment_modes)
        agree_pct = summary_metrics.get("agreement_ratio", 0.0) * 100.0
        print(f"[GRID] points={summary_metrics.get('points', 0)} -> agreement={agree_pct:.1f}%")
        for boundary in boundaries:
            diff = boundary.get("lambdaA_diff")
            if diff is not None:
                print(f"[BOUND] Omega0={boundary['Omega0']:.2f} ({boundary['segment_mode']}): "
                      f"lambdaAcrit(dir)={boundary['lambdaA_crit_direct']} "
                      f"lambdaAcrit(crit)={boundary['lambdaA_crit_criterion']} diff={diff}")

    if args.find_lambdaA_crit:
        K_val = args.K if args.K is not None else base.K
        Omega_val = args.Omega0 if args.Omega0 is not None else base.Omega0
        entries = []
        for mode in segment_modes:
            lam_dir = bisection_lambda_crit(base, K_val, Omega_val, mode, "direct", args.lambda_max)
            lam_crit = bisection_lambda_crit(base, K_val, Omega_val, mode, "criterion", args.lambda_max)
            entries.append({
                "segment_mode": mode,
                "K": K_val,
                "Omega0": Omega_val,
                "lambdaA_crit_direct": lam_dir,
                "lambdaA_crit_criterion": lam_crit,
            })
            print(f"[LAMBDA_CRIT] mode={mode} K={K_val} Omega0={Omega_val}: direct={lam_dir} criterion={lam_crit}")
        summary_data.setdefault("lambdaA_crit_search", []).extend(entries)

    if args.find_K_crit:
        lam_val = args.lambdaA if args.lambdaA is not None else base.lambda_A
        Omega_val = args.Omega0 if args.Omega0 is not None else base.Omega0
        entries = []
        for mode in segment_modes:
            K_dir = integer_binary_search_K(base, lam_val, Omega_val, mode, "direct", 1, args.K_max)
            K_crit = integer_binary_search_K(base, lam_val, Omega_val, mode, "criterion", 1, args.K_max)
            entries.append({
                "segment_mode": mode,
                "lambda_A": lam_val,
                "Omega0": Omega_val,
                "K_crit_direct": K_dir,
                "K_crit_criterion": K_crit,
            })
            print(f"[K_CRIT] mode={mode} lambda_A={lam_val} Omega0={Omega_val}: direct={K_dir} criterion={K_crit}")
        summary_data.setdefault("K_crit_search", []).extend(entries)

    with open(output_dir / "proof_sweep_summary_v4.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print("Synopsis: lambda_A crit rises with Omega0 and decreases with K; weighted segments shift boundaries downward.")
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    main()
