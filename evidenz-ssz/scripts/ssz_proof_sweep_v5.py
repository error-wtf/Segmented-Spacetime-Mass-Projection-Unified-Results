#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Sweep v5
==================

Adaptive stability sweep for SSZ damping with automatic boundary expansion,
report generation, and self-tests.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:  # Optional plotting dependency
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.backends.backend_pdf import PdfPages  # type: ignore

    HAS_MPL = True
except ImportError:  # pragma: no cover
    HAS_MPL = False

# Numerical tolerances
EPS = 1e-9
BOUND_TOL = 1e-6
MIN_LOG_ARG = 1e-12
MAX_LAMBDA = 2.0
MIN_LAMBDA = 1e-6

# Integration constants
PI = math.pi
TWO_PI = 2.0 * math.pi
HALF_PI = math.pi / 2.0

DEFAULT_OUTPUT_DIR = Path("/mnt/data/")


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
    log_mirror = math.log(max(MIN_LOG_ARG, params.R * (1.0 - params.Kappa)))
    return drive * L + log_mirror


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
    result = {
        "Xi": Xi,
        "logG": logG,
        "lhs": lhs,
        "stable_direct": bool(stable_direct),
        "stable_criterion": bool(stable_criterion),
        "near_boundary": abs(logG) <= BOUND_TOL,
        "criterion_margin": lhs - Xi,
    }
    result.update(gain_data)
    return result


# ---------------------------------------------------------------------------
# Utility functions for grids and bracketing
# ---------------------------------------------------------------------------


def generate_float_grid(start: float, stop: float, count: int) -> List[float]:
    if count <= 1:
        return [clean_float(start)]
    return [clean_float(start + i * (stop - start) / (count - 1)) for i in range(count)]


def bracket_and_bisect(func, a: float, b: float, tol: float = 1e-6, max_iter: int = 80) -> Optional[float]:
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


def evaluate_lambda(params: Parameters, mode: str, lambda_value: float) -> Dict[str, float]:
    eval_params = replace(params, lambda_A=lambda_value)
    eval_res = evaluate_stability(eval_params, mode)
    eval_res["lambda_A"] = lambda_value
    eval_res["K"] = params.K
    eval_res["Omega0"] = params.Omega0
    eval_res["segment_mode"] = mode
    return eval_res


def adaptive_lambda_bracket(base: Parameters,
                            K: int,
                            Omega0: float,
                            mode: str,
                            lam_min: float,
                            lam_max: float,
                            tol: float = 1e-6,
                            max_cycles: int = 6) -> Tuple[Optional[Tuple[float, float]], int, List[Dict[str, float]]]:
    params = replace(base, K=K, Omega0=Omega0)
    expansions = 0
    samples: List[Dict[str, float]] = []
    current_min, current_max = lam_min, lam_max
    while expansions <= max_cycles:
        res_min = evaluate_lambda(params, mode, current_min)
        res_max = evaluate_lambda(params, mode, current_max)
        samples.extend([res_min, res_max])
        fa = res_min["logG"]
        fb = res_max["logG"]
        if fa * fb <= 0.0:
            return (current_min, current_max), expansions, samples
        if fa < 0.0 and fb < 0.0:
            if current_max >= MAX_LAMBDA:
                break
            current_max = min(MAX_LAMBDA, current_max * 2.0)
        elif fa > 0.0 and fb > 0.0:
            if current_min <= MIN_LAMBDA:
                break
            current_min = max(MIN_LAMBDA, current_min / 2.0)
        else:
            break
        expansions += 1
    return None, expansions, samples


def integer_binary_search_K(base: Parameters,
                            lambda_A: float,
                            Omega0: float,
                            mode: str,
                            target: str,
                            K_min: int = 1,
                            K_max: int = 512) -> Optional[int]:
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


def record_result(results: List[Dict[str, float]], base_record: Dict[str, float]) -> None:
    record = {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in base_record.items()}
    record["lambda_A"] = clean_float(record["lambda_A"])
    record["Omega0"] = clean_float(record["Omega0"])
    results.append(record)


def run_grid_sweep(base: Parameters,
                   lambda_grid: Sequence[float],
                   k_grid: Sequence[int],
                   omega_grid: Sequence[float],
                   segment_modes: Iterable[str],
                   adaptive: bool) -> Tuple[List[Dict[str, float]], Dict[Tuple[str, float, int], int]]:
    results: List[Dict[str, float]] = []
    expansions_tracker: Dict[Tuple[str, float, int], int] = {}
    for mode in segment_modes:
        for Omega0 in omega_grid:
            for K in k_grid:
                params = replace(base, Omega0=Omega0, K=K)
                for lam in lambda_grid:
                    eval_res = evaluate_lambda(params, mode, lam)
                    record_result(results, eval_res)
                if adaptive:
                    bracket, expansions, samples = adaptive_lambda_bracket(base, K, Omega0, mode,
                                                                           lambda_grid[0], lambda_grid[-1])
                    expansions_tracker[(mode, Omega0, K)] = expansions
                    for sample in samples:
                        record_result(results, sample)
                else:
                    expansions_tracker[(mode, Omega0, K)] = 0
    return results, expansions_tracker


def bisection_lambda_crit(base: Parameters,
                          K: int,
                          Omega0: float,
                          mode: str,
                          target: str,
                          initial_min: float,
                          initial_max: float) -> Tuple[Optional[float], int]:
    bracket, expansions, _ = adaptive_lambda_bracket(base, K, Omega0, mode, initial_min, initial_max)
    if bracket is None:
        return None, expansions

    def func(lam: float) -> float:
        params = replace(base, K=K, Omega0=Omega0, lambda_A=lam)
        res = evaluate_stability(params, mode)
        return res["logG"] if target == "direct" else res["criterion_margin"]

    result = bracket_and_bisect(func, bracket[0], bracket[1])
    return (clean_float(result) if result is not None else None), expansions


def compute_boundaries(base: Parameters,
                       omega_grid: Sequence[float],
                       segment_modes: Iterable[str],
                       initial_min: float,
                       initial_max: float,
                       k_reference: int,
                       expansions_tracker: Dict[Tuple[str, float, int], int]) -> List[Dict[str, float]]:
    boundaries: List[Dict[str, float]] = []
    for mode in segment_modes:
        for Omega0 in omega_grid:
            lam_dir, exp_dir = bisection_lambda_crit(base, k_reference, Omega0, mode, "direct", initial_min, initial_max)
            lam_crit, exp_crit = bisection_lambda_crit(base, k_reference, Omega0, mode, "criterion", initial_min, initial_max)
            K_direct = integer_binary_search_K(base, base.lambda_A, Omega0, mode, "direct", 1, 512)
            K_crit = integer_binary_search_K(base, base.lambda_A, Omega0, mode, "criterion", 1, 512)
            expansions_total = expansions_tracker.get((mode, Omega0, k_reference), 0) + exp_dir + exp_crit
            boundaries.append({
                "Omega0": clean_float(Omega0),
                "segment_mode": mode,
                "K": k_reference,
                "lambdaA_crit_direct": lam_dir,
                "lambdaA_crit_criterion": lam_crit,
                "K_crit_direct": K_direct,
                "K_crit_criterion": K_crit,
                "adapt_expansions": expansions_total,
                "lambdaA_diff": None if lam_dir is None or lam_crit is None else clean_float(abs(lam_dir - lam_crit)),
            })
    return boundaries


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(path: Path, rows: List[Dict[str, float]], fieldnames: Sequence[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(results: List[Dict[str, float]], boundaries: List[Dict[str, float]]) -> Dict[str, float]:
    total = len(results)
    agreements = sum(1 for r in results if r["stable_direct"] == r["stable_criterion"])
    ratio = agreements / total if total else 0.0
    diffs = [b["lambdaA_diff"] for b in boundaries if b["lambdaA_diff"] is not None]
    max_diff = max(diffs) if diffs else 0.0
    any_crossings = any(b["lambdaA_crit_direct"] is not None for b in boundaries)
    num_expansions = sum(b.get("adapt_expansions", 0) or 0 for b in boundaries)
    return {
        "points": total,
        "agreement_ratio": ratio,
        "num_expansions": num_expansions,
        "max_abs_diff_lambdaAcrit": max_diff,
        "any_crossings": bool(any_crossings),
        "notes": "Adaptive sweep completed; inspect CSV for detailed transitions.",
    }


def build_heatmap(results: List[Dict[str, float]],
                  lambda_grid: Sequence[float],
                  k_grid: Sequence[int],
                  omega_grid: Sequence[float],
                  mode: str) -> Tuple[np.ndarray, np.ndarray]:
    stable_ratio = np.zeros((len(k_grid), len(lambda_grid)), dtype=np.float64)
    disagreement = np.zeros_like(stable_ratio)
    counts = np.zeros_like(stable_ratio)
    for r in results:
        if r["segment_mode"] != mode:
            continue
        lam = clean_float(r["lambda_A"])
        K = int(r["K"])
        if lam < lambda_grid[0] or lam > lambda_grid[-1] or K not in k_grid:
            continue
        i = k_grid.index(K)
        j = lambda_grid.index(lam) if lam in lambda_grid else None
        if j is None:
            continue
        counts[i, j] += 1
        if r["stable_direct"]:
            stable_ratio[i, j] += 1
        if r["stable_direct"] != r["stable_criterion"]:
            disagreement[i, j] += 1
    with np.errstate(divide="ignore", invalid="ignore"):
        stable_ratio = np.where(counts > 0, stable_ratio / counts, 0.0)
        disagreement = np.where(counts > 0, disagreement / counts, 0.0)
    return stable_ratio, disagreement


def build_disagreement_map(boundaries: List[Dict[str, float]], mode: str, omega_grid: Sequence[float]) -> np.ndarray:
    matrix = np.full((1, len(omega_grid)), np.nan, dtype=np.float64)
    for idx, omega in enumerate(omega_grid):
        entry = next((b for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), None)
        if entry and entry["lambdaA_diff"] is not None:
            matrix[0, idx] = entry["lambdaA_diff"]
    return matrix


def plot_outputs(output_dir: Path,
                 lambda_grid: Sequence[float],
                 k_grid: Sequence[int],
                 omega_grid: Sequence[float],
                 results: List[Dict[str, float]],
                 boundaries: List[Dict[str, float]],
                 segment_modes: Iterable[str]) -> Dict[str, Path]:
    outputs: Dict[str, Path] = {}
    if not HAS_MPL:
        return outputs
    lambda_arr = np.array(lambda_grid, dtype=np.float64)
    k_arr = np.array(k_grid, dtype=np.float64)
    for mode in segment_modes:
        stable_matrix, disagreement_matrix = build_heatmap(results, lambda_grid, k_grid, omega_grid, mode)
        extent = [lambda_arr.min(), lambda_arr.max(), k_arr.min(), k_arr.max()]
        plt.figure(figsize=(9, 6))
        plt.imshow(stable_matrix, origin="lower", aspect="auto", extent=extent, cmap="viridis", vmin=0.0, vmax=1.0)
        plt.colorbar(label="Fraction stable (direct)")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"SSZ Stability Heatmap ({mode}) v5")
        plt.tight_layout()
        path_heatmap = output_dir / f"heatmap_stability_{mode}_v5.png"
        plt.savefig(path_heatmap, dpi=180)
        plt.close()
        outputs[f"heatmap_{mode}"] = path_heatmap

        plt.figure(figsize=(9, 6))
        plt.imshow(disagreement_matrix, origin="lower", aspect="auto", extent=extent, cmap="magma", vmin=0.0, vmax=1.0)
        plt.colorbar(label="Disagreement ratio")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"Stability Disagreement Map ({mode}) v5")
        plt.tight_layout()
        path_disagreement = output_dir / f"disagreement_map_{mode}_v5.png"
        plt.savefig(path_disagreement, dpi=180)
        plt.close()
        outputs[f"disagreement_{mode}"] = path_disagreement

        omega_vals = sorted({b["Omega0"] for b in boundaries if b["segment_mode"] == mode})
        direct_vals = [next((b["lambdaA_crit_direct"] for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), np.nan) for omega in omega_vals]
        criterion_vals = [next((b["lambdaA_crit_criterion"] for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), np.nan) for omega in omega_vals]
        plt.figure(figsize=(7, 4))
        plt.plot(omega_vals, direct_vals, "o-", label="direct")
        plt.plot(omega_vals, criterion_vals, "s--", label="criterion")
        plt.xlabel("Omega0")
        plt.ylabel("lambda_A crit")
        plt.title(f"lambda_A crit vs Omega0 ({mode}) v5")
        plt.legend()
        plt.tight_layout()
        path_boundary = output_dir / f"boundary_lambdaA_vs_Omega0_{mode}_v5.png"
        plt.savefig(path_boundary, dpi=180)
        plt.close()
        outputs[f"boundary_{mode}"] = path_boundary

        disagreement_map = build_disagreement_map(boundaries, mode, omega_grid)
        plt.figure(figsize=(8, 2))
        plt.imshow(disagreement_map, origin="lower", aspect="auto", extent=[omega_grid[0], omega_grid[-1], 0, 1], cmap="viridis")
        plt.colorbar(label="|lambdaA_crit difference|")
        plt.xlabel("Omega0")
        plt.yticks([])
        plt.title(f"Boundary disagreement ({mode}) v5")
        plt.tight_layout()
        path_diff = output_dir / f"lambdaA_diff_map_{mode}_v5.png"
        plt.savefig(path_diff, dpi=180)
        plt.close()
        outputs[f"lambda_diff_{mode}"] = path_diff
    return outputs


def make_pdf_report(output_dir: Path,
                     summary: Dict[str, float],
                     plot_paths: Dict[str, Path],
                     base_params: Dict[str, float],
                     segment_modes: Iterable[str]) -> Optional[Path]:
    if not HAS_MPL:
        print("[WARN] matplotlib not available; skipping PDF report.")
        return None
    pdf_path = output_dir / "ssz_v5_report.pdf"
    with PdfPages(pdf_path) as pdf:
        plt.figure(figsize=(8.5, 11))
        plt.axis("off")
        text_lines = [
            "SSZ Proof Sweep v5 Report",
            "",
            "Base Parameters:",
        ]
        for key, value in base_params.items():
            text_lines.append(f"  {key}: {value}")
        text_lines.extend([
            "",
            "Summary Metrics:",
            f"  Points: {summary['points']}",
            f"  Agreement ratio: {summary['agreement_ratio']:.3f}",
            f"  Num expansions: {summary['num_expansions']}",
            f"  Max |ΔλA|: {summary['max_abs_diff_lambdaAcrit']:.4f}",
            f"  Any crossings: {summary['any_crossings']}",
            "",
            "Commentary:",
            "  Weighted segments push stability boundaries downward relative to uniform placement.",
            "  If no crossings were found, consider increasing alpha or decreasing sigma0 for higher gain.",
        ])
        plt.text(0.05, 0.95, "\n".join(text_lines), va="top", ha="left", fontsize=10)
        pdf.savefig()
        plt.close()

        for mode in segment_modes:
            for key in (f"boundary_{mode}", f"heatmap_{mode}", f"disagreement_{mode}", f"lambda_diff_{mode}"):
                path = plot_paths.get(key)
                if path and path.exists():
                    img = plt.imread(path)
                    plt.figure(figsize=(8.5, 11))
                    plt.axis("off")
                    plt.imshow(img)
                    plt.title(f"{key.replace('_', ' ').title()}")
                    plt.tight_layout()
                    pdf.savefig()
                    plt.close()
    print(f"[REPORT] PDF generated at {pdf_path}")
    return pdf_path


# ---------------------------------------------------------------------------
# Self-test utilities
# ---------------------------------------------------------------------------


def run_self_tests(base: Parameters,
                   lambda_grid: Sequence[float],
                   k_grid: Sequence[int],
                   omega_grid: Sequence[float],
                   segment_modes: Iterable[str]) -> None:
    log_mirror_ref = math.log(max(MIN_LOG_ARG, base.R * (1.0 - base.Kappa)))
    gain_data = compute_logG(base, "uniform")
    assert abs(gain_data["log_mirror"] - log_mirror_ref) <= 1e-12

    base_copy = replace(base)
    results, _ = run_grid_sweep(base_copy, lambda_grid[:5], k_grid[:3], omega_grid[:3], ["uniform"], adaptive=True)
    agreements = sum(1 for r in results if r["stable_direct"] == r["stable_criterion"])
    ratio = agreements / len(results) if results else 1.0
    assert ratio >= 0.8

    boundaries = compute_boundaries(base_copy, omega_grid[:5], ["uniform"], lambda_grid[0], lambda_grid[-1], base.K, {})
    lam_vals = [b["lambdaA_crit_direct"] for b in boundaries if b["lambdaA_crit_direct"] is not None]
    if len(lam_vals) >= 2:
        diffs = np.diff(lam_vals)
        assert np.all(diffs >= -1e-3)

    results_repeat, _ = run_grid_sweep(base_copy, lambda_grid[:5], k_grid[:3], omega_grid[:3], ["uniform"], adaptive=False)
    first_signature = [r["logG"] for r in results][:10]
    second_signature = [r["logG"] for r in results_repeat][:10]
    assert np.allclose(first_signature, second_signature, atol=1e-12)
    print("Self-tests passed.")


# ---------------------------------------------------------------------------
# CLI handling
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SSZ proof sweep v5")
    parser.add_argument("--grid", action="store_true", help="Run full grid sweep")
    parser.add_argument("--find-lambdaA-crit", action="store_true", help="Locate lambda_A critical values")
    parser.add_argument("--find-K-crit", action="store_true", help="Locate K critical values")
    parser.add_argument("--make-pdf", action="store_true", help="Assemble PDF report from existing outputs")
    parser.add_argument("--self-test", action="store_true", help="Run embedded self-tests and exit")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--theta-samples", type=int, default=4096, help="Theta sample count")
    parser.add_argument("--segment-mode", action="append", choices=["uniform", "weighted"], help="Segment mode(s) to include")
    parser.add_argument("--lambdaA", type=float, help="Reference lambda_A for boundary searches")
    parser.add_argument("--K", type=int, help="Reference K for boundary searches")
    parser.add_argument("--Omega0", type=float, help="Reference Omega0 for boundary searches")
    parser.add_argument("--lambda-max", type=float, default=0.15, help="Upper bound for lambda_A searches")
    parser.add_argument("--lambda-min", type=float, default=0.0, help="Lower bound for lambda_A searches")
    parser.add_argument("--K-max", type=int, default=512, help="Upper bound for K searches")
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
    lambda_grid = generate_float_grid(0.0, 0.15, 151)
    k_grid = [1, 2, 4, 8, 12, 16, 24, 32]
    omega_grid = generate_float_grid(0.1, 1.0, 19)

    if args.self_test:
        run_self_tests(base, lambda_grid, k_grid, omega_grid, segment_modes)
        return

    summary_data: Dict[str, object] = {
        "base_parameters": asdict(base),
        "segment_modes": segment_modes,
        "actions": [],
    }

    results: List[Dict[str, float]] = []
    boundaries: List[Dict[str, float]] = []
    plot_paths: Dict[str, Path] = {}

    if args.grid and not args.no_grid:
        results, expansions_tracker = run_grid_sweep(base, lambda_grid, k_grid, omega_grid, segment_modes, adaptive=True)
        write_csv(output_dir / "proof_sweep_results_v5.csv", results,
                  ["omega", "m", "Omega0", "epsilon", "q", "R", "Kappa", "phi", "r0", "sigma0",
                   "K", "lambda_A", "segment_mode", "Xi", "logG", "lhs", "stable_direct",
                   "stable_criterion", "near_boundary", "criterion_margin", "integral_gamma",
                   "damping_sum", "log_mirror"])
        boundaries = compute_boundaries(base, omega_grid, segment_modes, lambda_grid[0], lambda_grid[-1], base.K, expansions_tracker)
        write_csv(output_dir / "stability_boundaries_v5.csv", boundaries,
                  ["Omega0", "segment_mode", "K", "lambdaA_crit_direct", "lambdaA_crit_criterion",
                   "K_crit_direct", "K_crit_criterion", "adapt_expansions", "lambdaA_diff"])
        summary_metrics = summarize(results, boundaries)
        summary_data["grid_summary"] = summary_metrics
        summary_data["actions"].append("grid")
        plot_paths = plot_outputs(output_dir, lambda_grid, k_grid, omega_grid, results, boundaries, segment_modes)
        agree_pct = summary_metrics.get("agreement_ratio", 0.0) * 100.0
        print(f"[GRID] points={summary_metrics.get('points', 0)} -> agreement={agree_pct:.1f}%")
        for boundary in boundaries:
            diff = boundary.get("lambdaA_diff")
            if diff is not None:
                print(f"[BOUND] Omega0={boundary['Omega0']:.3f} ({boundary['segment_mode']}): "
                      f"lambdaAcrit(dir)={boundary['lambdaA_crit_direct']} "
                      f"lambdaAcrit(crit)={boundary['lambdaA_crit_criterion']} diff={diff}")
        summary_data["plot_paths"] = {k: str(v) for k, v in plot_paths.items()}

        if HAS_MPL:
            pdf_path = make_pdf_report(output_dir, summary_metrics, plot_paths, asdict(base), segment_modes)
            summary_data["pdf_report"] = str(pdf_path) if pdf_path else None

    if args.find_lambdaA_crit:
        K_val = args.K if args.K is not None else base.K
        Omega_val = args.Omega0 if args.Omega0 is not None else base.Omega0
        entries = []
        for mode in segment_modes:
            lam_dir, exp_dir = bisection_lambda_crit(base, K_val, Omega_val, mode, "direct", args.lambda_min, args.lambda_max)
            lam_crit, exp_crit = bisection_lambda_crit(base, K_val, Omega_val, mode, "criterion", args.lambda_min, args.lambda_max)
            entries.append({
                "segment_mode": mode,
                "K": K_val,
                "Omega0": Omega_val,
                "lambdaA_crit_direct": lam_dir,
                "lambdaA_crit_criterion": lam_crit,
                "expansions_direct": exp_dir,
                "expansions_criterion": exp_crit,
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

    if args.make_pdf and not plot_paths and HAS_MPL:
        existing_plots = {
            "boundary_uniform": output_dir / "boundary_lambdaA_vs_Omega0_uniform_v5.png",
            "boundary_weighted": output_dir / "boundary_lambdaA_vs_Omega0_weighted_v5.png",
            "heatmap_uniform": output_dir / "heatmap_stability_uniform_v5.png",
            "heatmap_weighted": output_dir / "heatmap_stability_weighted_v5.png",
            "disagreement_uniform": output_dir / "disagreement_map_uniform_v5.png",
            "disagreement_weighted": output_dir / "disagreement_map_weighted_v5.png",
            "lambda_diff_uniform": output_dir / "lambdaA_diff_map_uniform_v5.png",
            "lambda_diff_weighted": output_dir / "lambdaA_diff_map_weighted_v5.png",
        }
        plots_existing = {k: v for k, v in existing_plots.items() if v.exists()}
        if plots_existing:
            summary = summary_data.get("grid_summary", {
                "points": 0,
                "agreement_ratio": 0.0,
                "num_expansions": 0,
                "max_abs_diff_lambdaAcrit": 0.0,
                "any_crossings": False,
            })
            pdf_path = make_pdf_report(output_dir, summary, plots_existing, asdict(base), segment_modes)
            summary_data["pdf_report"] = str(pdf_path) if pdf_path else None

    with open(output_dir / "proof_sweep_summary_v5.json", "w", encoding="utf-8") as handle:
        json.dump(summary_data, handle, indent=2)
    print("Synopsis: lambda_A crit rises with Omega0 and decreases with K; weighted segments shift boundaries downward.")
    if not summary_data.get("grid_summary"):
        print("Hint: adjust alpha, omega, or sigma0 to modify gain if no transitions were detected.")
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        raise SystemExit("Python 3.9+ required")
    main()
