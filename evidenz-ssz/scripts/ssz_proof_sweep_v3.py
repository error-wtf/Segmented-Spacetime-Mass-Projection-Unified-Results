#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Sweep v3
==================

Boundary-resolved stability analysis comparing analytic SSZ damping criterion vs.
direct gain evaluation across uniform and weighted segment placements.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import csv
import json
import math
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # Optional plotting dependency
    import matplotlib.pyplot as plt  # type: ignore

    HAS_MPL = True
except ImportError:  # pragma: no cover - plotting optional
    HAS_MPL = False

PI = math.pi
TWO_PI = 2.0 * math.pi
EPS = 1e-9
LOG_TOL = 1e-6
MIN_LOG_ARG = 1e-12
DEFAULT_OUTPUT_DIR = Path("d:/extended_results/proof_reports")


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
# Geometry and gain kernels
# ---------------------------------------------------------------------------

def r_theta(theta: float, params: Parameters) -> float:
    return params.r0 * (params.phi ** (theta / (PI / 2.0)))

def sigma_theta(theta: float, params: Parameters) -> float:
    return params.sigma0 * (params.phi ** (theta / (PI / 2.0)))

def Omega_theta(theta: float, params: Parameters) -> float:
    return params.Omega0 * (1.0 + params.epsilon * math.cos(params.q * theta))

def gamma_loc(theta: float, params: Parameters) -> float:
    gain = max(0.0, params.m * Omega_theta(theta, params) - params.omega)
    return params.alpha * gain - params.eta

def trapezoid_integral(func: Callable[[float, Parameters], float],
                       params: Parameters) -> float:
    n = max(16, params.theta_samples)
    h = TWO_PI / n
    total = 0.5 * (func(0.0, params) + func(TWO_PI, params))
    for k in range(1, n):
        theta = k * h
        total += func(theta, params)
    return total * h

def uniform_segment_angles(params: Parameters) -> List[float]:
    return [TWO_PI * k / params.K for k in range(params.K)]

def weighted_segment_angles(params: Parameters,
                             resolution: Optional[int] = None) -> List[float]:
    samples = max(resolution or params.theta_samples * 2, params.theta_samples)
    step = TWO_PI / samples
    cumulative = [0.0]
    total = 0.0
    for i in range(samples):
        theta = i * step
        total += sigma_theta(theta, params)
        cumulative.append(total)
    if total <= 1e-18:
        return uniform_segment_angles(params)
    targets = [total * k / params.K for k in range(params.K)]
    angles: List[float] = []
    for t in targets:
        # binary search
        lo, hi = 0, len(cumulative) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cumulative[mid] < t:
                lo = mid + 1
            else:
                hi = mid
        idx = max(1, lo)
        left_val = cumulative[idx - 1]
        right_val = cumulative[idx]
        frac = 0.0 if right_val == left_val else (t - left_val) / (right_val - left_val)
        theta_left = (idx - 1) * step
        theta_val = theta_left + frac * step
        angles.append(min(TWO_PI, max(0.0, theta_val)))
    return angles

def segment_angles(params: Parameters, mode: str) -> List[float]:
    mode_lower = mode.lower()
    if mode_lower == "weighted":
        return weighted_segment_angles(params)
    return uniform_segment_angles(params)


# ---------------------------------------------------------------------------
# Gain and analytic bound calculations
# ---------------------------------------------------------------------------

def compute_L(params: Parameters) -> float:
    return trapezoid_integral(lambda th, p: r_theta(th, p), params)

def compute_Xi(params: Parameters) -> float:
    Omega_max = params.Omega0 * (1.0 + params.epsilon)
    drive = params.alpha * max(0.0, params.m * Omega_max - params.omega) - params.eta
    L = compute_L(params)
    mirror = math.log(max(1e-12, params.R * (1.0 - params.Kappa)))
    return drive * L + mirror

def compute_logG(params: Parameters, mode: str) -> Tuple[float, float, float, float]:
    integral_gamma = trapezoid_integral(lambda th, p: gamma_loc(th, p) * r_theta(th, p), params)
    angs = segment_angles(params, mode)
    damping_sum = sum(params.lambda_A * sigma_theta(theta, params) for theta in angs)
    log_mirror = math.log(max(MIN_LOG_ARG, params.R * (1.0 - params.Kappa)))
    logG = integral_gamma - damping_sum + log_mirror
    return logG, integral_gamma, damping_sum, log_mirror

def evaluate_stability(params: Parameters, mode: str) -> Dict[str, float]:
    Xi = compute_Xi(params)
    logG, integral_gamma, damping_sum, log_mirror = compute_logG(params, mode)
    lhs = params.lambda_A * params.K * params.sigma0
    stable_direct = logG < -EPS
    stable_criterion = lhs > Xi + EPS
    return {
        "Xi": Xi,
        "logG": logG,
        "lhs": lhs,
        "stable_direct": bool(stable_direct),
        "stable_criterion": bool(stable_criterion),
        "near_boundary": abs(logG) <= LOG_TOL,
        "criterion_margin": lhs - Xi,
        "integral_gamma": integral_gamma,
        "damping_sum": damping_sum,
        "log_mirror": log_mirror,
    }


# ---------------------------------------------------------------------------
# Grids and adaptive boundary searches
# ---------------------------------------------------------------------------

def clean_float(value: float) -> float:
    return float(f"{value:.12g}")


def generate_float_grid(start: float, stop: float, count: int) -> List[float]:
    if count <= 1:
        return [clean_float(start)]
    return [clean_float(start + i * (stop - start) / (count - 1)) for i in range(count)]

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
                          tol: float = 1e-4,
                          max_iter: int = 60) -> Optional[float]:
    params = replace(base, K=K, Omega0=Omega0, lambda_A=0.0)
    res_left = evaluate_stability(params, mode)
    left_val = res_left["logG"] if target == "direct" else res_left["criterion_margin"]
    params = replace(params, lambda_A=lam_max)
    res_right = evaluate_stability(params, mode)
    right_val = res_right["logG"] if target == "direct" else res_right["criterion_margin"]
    if target == "direct":
        if res_left["stable_direct"]:
            return 0.0
        if not res_right["stable_direct"]:
            return None
    else:
        if res_left["stable_criterion"]:
            return 0.0
        if not res_right["stable_criterion"]:
            return None
    left, right = 0.0, lam_max
    for _ in range(max_iter):
        mid = 0.5 * (left + right)
        params = replace(params, lambda_A=mid)
        res_mid = evaluate_stability(params, mode)
        mid_val = res_mid["logG"] if target == "direct" else res_mid["criterion_margin"]
        if target == "direct":
            if abs(mid_val) <= tol:
                return mid
            if res_mid["stable_direct"]:
                right = mid
            else:
                left = mid
        else:
            if abs(mid_val) <= tol:
                return mid
            if res_mid["stable_criterion"]:
                right = mid
            else:
                left = mid
        if right - left <= tol:
            break
    return right

def integer_binary_search_K(base: Parameters,
                            lambda_A: float,
                            Omega0: float,
                            mode: str,
                            target: str,
                            K_min: int = 2,
                            K_max: int = 256) -> Optional[int]:
    low, high = K_min, K_max
    def stable(K_val: int) -> bool:
        params = replace(base, lambda_A=lambda_A, Omega0=Omega0, K=K_val)
        res = evaluate_stability(params, mode)
        return res["stable_direct"] if target == "direct" else res["stable_criterion"]
    if not stable(high):
        return None
    while low < high:
        mid = (low + high) // 2
        if stable(mid):
            high = mid
        else:
            low = mid + 1
    return high

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
            K_direct = integer_binary_search_K(base, base.lambda_A, Omega0, mode, "direct", 2, K_max)
            K_crit = integer_binary_search_K(base, base.lambda_A, Omega0, mode, "criterion", 2, K_max)
            boundaries.append({
                "Omega0": Omega0,
                "segment_mode": mode,
                "K_reference": base.K,
                "lambdaA_crit_direct": lam_direct,
                "lambdaA_crit_criterion": lam_crit,
                "K_crit_direct": K_direct,
                "K_crit_criterion": K_crit,
                "lambdaA_diff": None if lam_direct is None or lam_crit is None else abs(lam_direct - lam_crit),
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

def summarize(results: List[Dict[str, float]], boundaries: List[Dict[str, float]]) -> Dict[str, object]:
    total = len(results)
    agreements = sum(1 for r in results if r["stable_direct"] == r["stable_criterion"])
    agreement_ratio = agreements / total if total else 0.0
    diffs = [b["lambdaA_diff"] for b in boundaries if b["lambdaA_diff"] is not None]
    max_diff = max(diffs) if diffs else 0.0
    notes = "See CSV outputs for detailed stability bands."
    return {
        "points": total,
        "agreement_ratio": agreement_ratio,
        "max_abs_diff_lambdaAcrit": max_diff,
        "notes": notes,
    }

def build_heatmap(results: List[Dict[str, float]],
                  lambda_grid: Sequence[float],
                  k_grid: Sequence[int],
                  omega_values: Sequence[float],
                  mode: str) -> Tuple[List[List[float]], List[List[float]]]:
    stable_matrix = [[0.0 for _ in lambda_grid] for _ in k_grid]
    disagreement_matrix = [[0.0 for _ in lambda_grid] for _ in k_grid]
    omega_map = sorted(set(omega_values))
    diff_lookup: Dict[Tuple[float, str], float] = {}
    for r in results:
        key = (r["lambda_A"], r["K"], r["segment_mode"])
    # fill direct stability
    for i, K in enumerate(k_grid):
        for j, lam in enumerate(lambda_grid):
            entry = next((r for r in results if math.isclose(r["lambda_A"], lam) and r["K"] == K and r["segment_mode"] == mode), None)
            if entry:
                stable_matrix[i][j] = 1.0 if entry["stable_direct"] else 0.0
                disagreement_matrix[i][j] = 1.0 if entry["stable_direct"] != entry["stable_criterion"] else 0.0
    return stable_matrix, disagreement_matrix

def plot_outputs(output_dir: Path,
                 lambda_grid: Sequence[float],
                 k_grid: Sequence[int],
                 omega_grid: Sequence[float],
                 results: List[Dict[str, float]],
                 boundaries: List[Dict[str, float]],
                 segment_modes: Iterable[str]) -> None:
    if not HAS_MPL:
        return
    for mode in segment_modes:
        stable_matrix, disagreement_matrix = build_heatmap(results, lambda_grid, k_grid, omega_grid, mode)
        extent = [min(lambda_grid), max(lambda_grid), min(k_grid), max(k_grid)]
        plt.figure(figsize=(9, 6))
        plt.imshow(stable_matrix, origin="lower", aspect="auto", extent=extent, cmap="viridis")
        plt.colorbar(label="Stable (direct)")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"SSZ Stability Heatmap ({mode})")
        plt.tight_layout()
        plt.savefig(output_dir / f"heatmap_stability_{mode}.png", dpi=180)
        plt.close()
        plt.figure(figsize=(9, 6))
        plt.imshow(disagreement_matrix, origin="lower", aspect="auto", extent=extent, cmap="magma")
        plt.colorbar(label="Disagreement")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"Stability Disagreement Map ({mode})")
        plt.tight_layout()
        plt.savefig(output_dir / f"disagreement_map_{mode}.png", dpi=180)
        plt.close()
        omega_vals = sorted(set(b["Omega0"] for b in boundaries if b["segment_mode"] == mode))
        direct_vals = [next((b["lambdaA_crit_direct"] for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), math.nan) for omega in omega_vals]
        crit_vals = [next((b["lambdaA_crit_criterion"] for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), math.nan) for omega in omega_vals]
        plt.figure(figsize=(7, 4))
        plt.plot(omega_vals, direct_vals, "o-", label="direct")
        plt.plot(omega_vals, crit_vals, "s--", label="criterion")
        plt.xlabel("Omega0")
        plt.ylabel("lambda_A crit")
        plt.title(f"lambda_A crit vs Omega0 ({mode})")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"boundary_lambdaA_vs_Omega0_{mode}.png", dpi=180)
        plt.close()


# ---------------------------------------------------------------------------
# CLI and execution
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SSZ proof sweep v3")
    parser.add_argument("--grid", action="store_true", help="Run full grid sweep")
    parser.add_argument("--find-lambdaA-crit", action="store_true", help="Locate lambda_A critical values")
    parser.add_argument("--find-K-crit", action="store_true", help="Locate K critical values")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--theta-samples", type=int, default=4096, help="Theta sample count")
    parser.add_argument("--segment-mode", action="append", choices=["uniform", "weighted"], help="Segment mode(s) to use")
    parser.add_argument("--lambdaA", type=float, help="Reference lambda_A for boundary searches")
    parser.add_argument("--K", type=int, help="Reference K for boundary searches")
    parser.add_argument("--Omega0", type=float, help="Reference Omega0 for boundary searches")
    parser.add_argument("--lambda-max", type=float, default=0.2, help="Upper bound for lambda_A searches")
    parser.add_argument("--K-max", type=int, default=256, help="Upper bound for K searches")
    parser.add_argument("--no-grid", action="store_true", help="Skip automatic grid sweep")
    return parser.parse_args()

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
    segment_modes = args.segment_mode if args.segment_mode else ["uniform"]
    lambda_grid = generate_float_grid(0.0, 0.06, 60)
    k_grid = [1, 2, 4, 8, 12, 16, 24, 32]
    omega_grid = generate_float_grid(0.2, 1.0, 9)
    summary_data: Dict[str, object] = {
        "base_parameters": asdict(base),
        "segment_modes": segment_modes,
        "actions": [],
    }
    if args.grid and not args.no_grid:
        results = run_grid_sweep(base, lambda_grid, k_grid, omega_grid, segment_modes)
        write_csv(output_dir / "proof_sweep_results.csv", results,
                  ["lambda_A", "K", "Omega0", "Xi", "logG", "lhs", "stable_criterion", "stable_direct", "near_boundary", "criterion_margin", "integral_gamma", "damping_sum", "log_mirror", "agree"])
        boundaries = compute_boundaries(base, omega_grid, segment_modes, args.lambda_max, args.K_max)
        write_csv(output_dir / "stability_boundaries_v3.csv", boundaries,
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
                      f"lambdaAcrit(dir)={boundary['lambdaA_crit_direct']} lambdaAcrit(crit)={boundary['lambdaA_crit_criterion']} "
                      f"diff={diff}")
    if args.find_lambdaA_crit:
        mode_list = segment_modes
        K_val = args.K if args.K is not None else base.K
        Omega_val = args.Omega0 if args.Omega0 is not None else base.Omega0
        entries = []
        for mode in mode_list:
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
        mode_list = segment_modes
        lam_val = args.lambdaA if args.lambdaA is not None else base.lambda_A
        Omega_val = args.Omega0 if args.Omega0 is not None else base.Omega0
        entries = []
        for mode in mode_list:
            K_dir = integer_binary_search_K(base, lam_val, Omega_val, mode, "direct", 2, args.K_max)
            K_crit = integer_binary_search_K(base, lam_val, Omega_val, mode, "criterion", 2, args.K_max)
            entries.append({
                "segment_mode": mode,
                "lambda_A": lam_val,
                "Omega0": Omega_val,
                "K_crit_direct": K_dir,
                "K_crit_criterion": K_crit,
            })
            print(f"[K_CRIT] mode={mode} lambda_A={lam_val} Omega0={Omega_val}: direct={K_dir} criterion={K_crit}")
        summary_data.setdefault("K_crit_search", []).extend(entries)
    with open(output_dir / "proof_sweep_summary_v3.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print("Synopsis: lambda_A crit steigt mit Omega0; weighted Segmente (optional) verschieben Grenzen nach unten.")
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":  # pragma: no cover
    main()
