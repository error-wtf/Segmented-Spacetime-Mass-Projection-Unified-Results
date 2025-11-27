#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Proof Sweep v6
==================

Adaptive stability sweep for SSZ damping with boundary detection,
segment-mode comparison, and automated reporting.

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

try:
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.backends.backend_pdf import PdfPages  # type: ignore

    HAS_MPL = True
except ImportError:  # pragma: no cover
    HAS_MPL = False

# Numerical tolerances
EPS = 1e-9
BOUND_TOL = 1e-6
MIN_LOG_ARG = 1e-12

# Defaults
DEFAULT_ALPHA = 2.5
DEFAULT_OUTPUT_DIR = Path("/mnt/data")
MAX_LAMBDA = 0.8
MAX_OMEGA = 2.0


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def resolve_output_dir(path: Optional[str]) -> Path:
    if path:
        return Path(path)
    if DEFAULT_OUTPUT_DIR.exists() and DEFAULT_OUTPUT_DIR.is_dir():
        return DEFAULT_OUTPUT_DIR
    return Path.cwd()


def clean_float(value: float) -> float:
    return float(f"{value:.12g}")


@dataclass
class Parameters:
    alpha: float = DEFAULT_ALPHA
    eta: float = 0.0
    omega: float = 0.25
    m: int = 4
    Omega0: float = 0.6
    epsilon: float = 0.2
    q: float = 3.0
    lambda_A: float = 0.1
    K: int = 64
    sigma0: float = 0.4
    R: float = 0.9999
    Kappa: float = 1e-5
    phi: float = 1.618034
    r0: float = 1.0
    theta_samples: int = 4096


# ---------------------------------------------------------------------------
# Geometry and gain helpers
# ---------------------------------------------------------------------------


TWO_PI = 2.0 * math.pi
HALF_PI = math.pi / 2.0


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
    return integrate_over_theta(r_theta(theta_grid(params), params), params)


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
# Adaptive bracketing and bisection
# ---------------------------------------------------------------------------


def evaluate_lambda(params: Parameters, mode: str, lambda_value: float) -> Dict[str, float]:
    eval_params = replace(params, lambda_A=lambda_value)
    res = evaluate_stability(eval_params, mode)
    res.update({"lambda_A": lambda_value, "K": params.K, "Omega0": params.Omega0, "segment_mode": mode})
    return res


def try_bracket_lambda(base: Parameters,
                       mode: str,
                       lam_min: float,
                       lam_max: float,
                       expand_factor: float,
                       tol_logG: float,
                       max_lambda: float,
                       max_cycles: int = 8) -> Tuple[Optional[Tuple[float, float]], List[Dict[str, float]], int]:
    params = replace(base)
    samples: List[Dict[str, float]] = []
    expansions = 0
    low, high = lam_min, lam_max
    while expansions <= max_cycles:
        res_low = evaluate_lambda(params, mode, low)
        res_high = evaluate_lambda(params, mode, high)
        samples.extend([res_low, res_high])
        sign_low = math.copysign(1.0, res_low["logG"]) if abs(res_low["logG"]) > tol_logG else 0.0
        sign_high = math.copysign(1.0, res_high["logG"]) if abs(res_high["logG"]) > tol_logG else 0.0
        if sign_low == 0.0:
            return (low, low), samples, expansions
        if sign_high == 0.0:
            return (high, high), samples, expansions
        if sign_low != sign_high:
            return (low, high), samples, expansions
        if sign_low < 0.0 and sign_high < 0.0:
            if high >= max_lambda:
                break
            high = min(max_lambda, high * expand_factor)
        elif sign_low > 0.0 and sign_high > 0.0:
            if low <= MIN_LOG_ARG:
                break
            low = max(MIN_LOG_ARG, low / expand_factor)
        else:
            break
        expansions += 1
    return None, samples, expansions


def bisection_logG(base: Parameters,
                   mode: str,
                   bracket: Tuple[float, float],
                   tol_logG: float,
                   max_iter: int) -> Optional[float]:
    a, b = bracket
    fa = evaluate_lambda(base, mode, a)["logG"]
    fb = evaluate_lambda(base, mode, b)["logG"]
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0.0:
        return None
    for _ in range(max_iter):
        mid = 0.5 * (a + b)
        fm = evaluate_lambda(base, mode, mid)["logG"]
        if abs(fm) <= tol_logG or (b - a) <= tol_logG:
            return mid
        if fa * fm < 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm
    return 0.5 * (a + b)


def bisection_criterion(base: Parameters,
                        mode: str,
                        bracket: Tuple[float, float],
                        tol_logG: float,
                        max_iter: int) -> Optional[float]:
    a, b = bracket
    for _ in range(max_iter):
        mid = 0.5 * (a + b)
        res_mid = evaluate_lambda(base, mode, mid)
        if res_mid["lhs"] > res_mid["Xi"]:
            b = mid
        else:
            a = mid
        if abs(b - a) <= tol_logG:
            return mid
    return 0.5 * (a + b)


# ---------------------------------------------------------------------------
# Sweep orchestration
# ---------------------------------------------------------------------------


def generate_float_grid(start: float, stop: float, count: int) -> List[float]:
    if count <= 1:
        return [clean_float(start)]
    return [clean_float(start + i * (stop - start) / (count - 1)) for i in range(count)]


def run_cell(base: Parameters,
             mode: str,
             lam_min: float,
             lam_max: float,
             expand_factor: float,
             tol_logG: float,
             max_lambda: float,
             max_iter: int) -> Tuple[Optional[float], Optional[float], List[Dict[str, float]], int]:
    bracket, samples, expansions = try_bracket_lambda(base, mode, lam_min, lam_max, expand_factor, tol_logG, max_lambda)
    if bracket is None:
        return None, None, samples, expansions
    if bracket[0] == bracket[1]:
        root = bracket[0]
        return root, root, samples, expansions
    lambda_direct = bisection_logG(base, mode, bracket, tol_logG, max_iter)
    lambda_criterion = bisection_criterion(base, mode, bracket, tol_logG, max_iter) if lambda_direct is not None else None
    return lambda_direct, lambda_criterion, samples, expansions


def record_sample(rows: List[Dict[str, float]], sample: Dict[str, float], params: Parameters) -> None:
    record = {
        "alpha": params.alpha,
        "eta": params.eta,
        "omega": params.omega,
        "m": params.m,
        "epsilon": params.epsilon,
        "q": params.q,
        "sigma0": params.sigma0,
        "R": params.R,
        "Kappa": params.Kappa,
        "phi": params.phi,
        "r0": params.r0,
        "K": sample["K"],
        "lambda_A": clean_float(sample["lambda_A"]),
        "Omega0": clean_float(sample["Omega0"]),
        "segment_mode": sample["segment_mode"],
        "Xi": sample["Xi"],
        "logG": sample["logG"],
        "lhs": sample["lhs"],
        "stable_direct": sample["stable_direct"],
        "stable_criterion": sample["stable_criterion"],
        "near_boundary": sample["near_boundary"],
        "criterion_margin": sample["criterion_margin"],
        "integral_gamma": sample["integral_gamma"],
        "damping_sum": sample["damping_sum"],
        "log_mirror": sample["log_mirror"],
    }
    rows.append(record)


def collect_results(base: Parameters,
                    K_values: Sequence[int],
                    Omega_values: Sequence[float],
                    segment_modes: Iterable[str],
                    lam_min: float,
                    lam_max: float,
                    expand_factor: float,
                    tol_logG: float,
                    max_lambda: float,
                    max_iter: int,
                    omega_expand_step: float) -> Tuple[List[Dict[str, float]], List[Dict[str, float]], Dict[str, int]]:
    samples: List[Dict[str, float]] = []
    boundaries: List[Dict[str, float]] = []
    crossings_count = {"direct": 0, "criterion": 0}

    for mode in segment_modes:
        for K in K_values:
            for Omega0 in Omega_values:
                params = replace(base, K=K, Omega0=Omega0)
                lambda_direct, lambda_criterion, cell_samples, expansions = run_cell(
                    params, mode, lam_min, lam_max, expand_factor, tol_logG, max_lambda, max_iter
                )
                for sample in cell_samples:
                    record_sample(samples, sample, params)

                if lambda_direct is None:
                    new_Omega = min(MAX_OMEGA, Omega0 + omega_expand_step)
                    if new_Omega > Omega0:
                        params_expanded = replace(params, Omega0=new_Omega)
                        lambda_direct, lambda_criterion, cell_samples_exp, expansions_exp = run_cell(
                            params_expanded, mode, lam_min, lam_max, expand_factor, tol_logG, max_lambda, max_iter
                        )
                        for sample in cell_samples_exp:
                            record_sample(samples, sample, params_expanded)
                        expansions += expansions_exp
                        if lambda_direct is not None:
                            params = params_expanded
                            Omega0 = new_Omega

                boundaries.append({
                    "Omega0": clean_float(Omega0),
                    "segment_mode": mode,
                    "K": K,
                    "lambdaA_crit_direct": None if lambda_direct is None else clean_float(lambda_direct),
                    "lambdaA_crit_criterion": None if lambda_criterion is None else clean_float(lambda_criterion),
                    "lambdaA_diff": None if lambda_direct is None or lambda_criterion is None else clean_float(abs(lambda_direct - lambda_criterion)),
                    "expansions": expansions,
                    "status": "crossing" if lambda_direct is not None else "no_bracket",
                })
                if lambda_direct is not None:
                    crossings_count["direct"] += 1
                if lambda_criterion is not None:
                    crossings_count["criterion"] += 1
    return samples, boundaries, crossings_count


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def write_csv(path: Path, rows: List[Dict[str, float]], fieldnames: Sequence[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(samples: List[Dict[str, float]], boundaries: List[Dict[str, float]]) -> Dict[str, float]:
    total = len(samples)
    agreements = sum(1 for r in samples if r["stable_direct"] == r["stable_criterion"])
    ratio = agreements / total if total else 0.0
    diffs = [b["lambdaA_diff"] for b in boundaries if b["lambdaA_diff"] is not None]
    max_diff = max(diffs) if diffs else 0.0
    any_crossings = any(b["lambdaA_crit_direct"] is not None for b in boundaries)
    return {
        "points": total,
        "agreement_ratio": ratio,
        "max_abs_diff_lambdaAcrit": max_diff,
        "any_crossings": bool(any_crossings),
        "notes": "Adaptive sweep complete; inspect CSV for detailed transitions.",
    }


def build_heatmap(samples: List[Dict[str, float]],
                  lambda_grid: Sequence[float],
                  K_grid: Sequence[int],
                  mode: str) -> Tuple[np.ndarray, np.ndarray]:
    stable_counts = np.zeros((len(K_grid), len(lambda_grid)), dtype=np.float64)
    counts = np.zeros_like(stable_counts)
    disagreement = np.zeros_like(stable_counts)
    indices = {value: idx for idx, value in enumerate(lambda_grid)}
    for sample in samples:
        if sample["segment_mode"] != mode:
            continue
        lam = clean_float(sample["lambda_A"])
        K = int(sample["K"])
        if lam not in indices or K not in K_grid:
            continue
        i = K_grid.index(K)
        j = indices[lam]
        counts[i, j] += 1
        if sample["stable_direct"]:
            stable_counts[i, j] += 1
        if sample["stable_direct"] != sample["stable_criterion"]:
            disagreement[i, j] += 1
    with np.errstate(divide="ignore", invalid="ignore"):
        stable_ratio = np.where(counts > 0, stable_counts / counts, 0.0)
        disagreement_ratio = np.where(counts > 0, disagreement / counts, 0.0)
    return stable_ratio, disagreement_ratio


def plot_outputs(output_dir: Path,
                 lambda_grid: Sequence[float],
                 K_grid: Sequence[int],
                 Omega_grid: Sequence[float],
                 samples: List[Dict[str, float]],
                 boundaries: List[Dict[str, float]],
                 segment_modes: Iterable[str]) -> Dict[str, Path]:
    if not HAS_MPL:
        print("[WARN] matplotlib not available; skipping plots.")
        return {}
    outputs: Dict[str, Path] = {}
    lambda_arr = np.array(lambda_grid, dtype=np.float64)
    K_arr = np.array(K_grid, dtype=np.float64)
    for mode in segment_modes:
        stable_matrix, disagreement_matrix = build_heatmap(samples, lambda_grid, K_grid, mode)
        extent = [lambda_arr.min(), lambda_arr.max(), K_arr.min(), K_arr.max()]
        plt.figure(figsize=(9, 6))
        plt.imshow(stable_matrix, origin="lower", aspect="auto", extent=extent, cmap="viridis", vmin=0, vmax=1)
        plt.colorbar(label="Fraction stable (direct)")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"SSZ Stability Heatmap ({mode}) v6")
        plt.tight_layout()
        path_heatmap = output_dir / f"heatmap_stability_{mode}_v6.png"
        plt.savefig(path_heatmap, dpi=180)
        plt.close()
        outputs[f"heatmap_{mode}"] = path_heatmap

        plt.figure(figsize=(9, 6))
        plt.imshow(disagreement_matrix, origin="lower", aspect="auto", extent=extent, cmap="magma", vmin=0, vmax=1)
        plt.colorbar(label="Disagreement ratio")
        plt.xlabel("lambda_A")
        plt.ylabel("K")
        plt.title(f"Stability Disagreement Map ({mode}) v6")
        plt.tight_layout()
        path_disagreement = output_dir / f"disagreement_map_{mode}_v6.png"
        plt.savefig(path_disagreement, dpi=180)
        plt.close()
        outputs[f"disagreement_{mode}"] = path_disagreement

        omega_vals = sorted(set(b["Omega0"] for b in boundaries if b["segment_mode"] == mode))
        if omega_vals:
            direct_vals = []
            criterion_vals = []
            diff_vals = []
            for omega in omega_vals:
                entry = next((b for b in boundaries if b["segment_mode"] == mode and math.isclose(b["Omega0"], omega)), None)
                direct = entry["lambdaA_crit_direct"] if entry and entry["lambdaA_crit_direct"] is not None else np.nan
                criterion = entry["lambdaA_crit_criterion"] if entry and entry["lambdaA_crit_criterion"] is not None else np.nan
                diff_val = entry["lambdaA_diff"] if entry and entry["lambdaA_diff"] is not None else np.nan
                direct_vals.append(float(direct) if not math.isnan(direct) else np.nan)
                criterion_vals.append(float(criterion) if not math.isnan(criterion) else np.nan)
                diff_vals.append(float(diff_val) if not math.isnan(diff_val) else np.nan)

            plt.figure(figsize=(7, 4))
            plt.plot(omega_vals, direct_vals, "o-", label="direct")
            plt.plot(omega_vals, criterion_vals, "s--", label="criterion")
            plt.xlabel("Omega0")
            plt.ylabel("lambda_A crit")
            plt.title(f"lambda_A crit vs Omega0 ({mode}) v6")
            plt.legend()
            plt.tight_layout()
            path_boundary = output_dir / f"boundary_lambdaA_vs_Omega0_{mode}_v6.png"
            plt.savefig(path_boundary, dpi=180)
            plt.close()
            outputs[f"boundary_{mode}"] = path_boundary

            diff_array = np.array(diff_vals, dtype=np.float64)
            plt.figure(figsize=(8, 2))
            plt.imshow(diff_array[None, :], origin="lower", aspect="auto", extent=[omega_vals[0], omega_vals[-1], 0, 1], cmap="viridis")
            plt.colorbar(label="|Delta lambda_A|")
            plt.xlabel("Omega0")
            plt.yticks([])
            plt.title(f"lambda_A difference map ({mode}) v6")
            plt.tight_layout()
            path_diff = output_dir / f"lambdaA_diff_map_{mode}_v6.png"
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
    pdf_path = output_dir / "ssz_v6_report.pdf"
    with PdfPages(pdf_path) as pdf:
        plt.figure(figsize=(8.5, 11))
        plt.axis("off")
        lines = [
            "SSZ Proof Sweep v6 Report",
            "",
            "Base Parameters:",
        ]
        for key, value in base_params.items():
            lines.append(f"  {key}: {value}")
        lines.extend([
            "",
            "Summary Metrics:",
            f"  Points: {summary['points']}",
            f"  Agreement ratio: {summary['agreement_ratio']:.3f}",
            f"  Max |Delta lambda_A|: {summary['max_abs_diff_lambdaAcrit']:.4f}",
            f"  Any crossings: {summary['any_crossings']}",
            "",
            "Conclusion:",
            "  Weighted segmentation tends to lower the critical damping threshold.",
            "  Increase alpha or reduce sigma0 if crossings are sparse.",
        ])
        plt.text(0.05, 0.95, "\n".join(lines), va="top", ha="left", fontsize=10)
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
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SSZ proof sweep v6")
    parser.add_argument("--grid", action="store_true", help="Run adaptive sweep")
    parser.add_argument("--segment-mode", action="append", choices=["uniform", "weighted"], help="Restrict segment modes")
    parser.add_argument("--lambdaA-min", type=float, default=0.0)
    parser.add_argument("--lambdaA-max", type=float, default=0.8)
    parser.add_argument("--K", type=int, nargs="*", default=[8, 16, 32, 64, 128])
    parser.add_argument("--Omega0-min", type=float, default=0.1)
    parser.add_argument("--Omega0-max", type=float, default=2.0)
    parser.add_argument("--Omega0-steps", type=int, default=10)
    parser.add_argument("--tol-logG", type=float, default=1e-3)
    parser.add_argument("--max-bisect-iter", type=int, default=40)
    parser.add_argument("--expand-factor-lambda", type=float, default=2.0)
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--eta", type=float, default=0.0)
    parser.add_argument("--omega", type=float, default=0.25)
    parser.add_argument("--m", type=int, default=4)
    parser.add_argument("--epsilon", type=float, default=0.2)
    parser.add_argument("--q", type=float, default=3.0)
    parser.add_argument("--sigma0", type=float, default=0.4)
    parser.add_argument("--R", type=float, default=0.9999)
    parser.add_argument("--kappa", type=float, default=1e-5)
    parser.add_argument("--phi", type=float, default=1.618034)
    parser.add_argument("--r0", type=float, default=1.0)
    parser.add_argument("--theta-samples", type=int, default=4096)
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF report")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    base = Parameters(
        alpha=args.alpha,
        eta=args.eta,
        omega=args.omega,
        m=args.m,
        epsilon=args.epsilon,
        q=args.q,
        sigma0=args.sigma0,
        R=args.R,
        Kappa=args.kappa,
        phi=args.phi,
        r0=args.r0,
        theta_samples=args.theta_samples,
    )

    lambda_grid = generate_float_grid(args.lambdaA_min, args.lambdaA_max, 151)
    Omega_grid = generate_float_grid(args.Omega0_min, args.Omega0_max, args.Omega0_steps)
    K_grid = sorted(set(args.K))
    segment_modes = args.segment_mode if args.segment_mode else ["uniform", "weighted"]

    results_summary: Dict[str, object] = {
        "base_parameters": asdict(base),
        "segment_modes": segment_modes,
    }

    if args.grid:
        samples, boundaries, crossings = collect_results(
            base,
            K_grid,
            Omega_grid,
            segment_modes,
            args.lambdaA_min,
            args.lambdaA_max,
            args.expand_factor_lambda,
            args.tol_logG,
            args.lambdaA_max,
            args.max_bisect_iter,
            (args.Omega0_max - args.Omega0_min) / max(1, args.Omega0_steps - 1),
        )

        write_csv(output_dir / "proof_sweep_results_v6.csv", samples,
                  ["alpha", "eta", "omega", "m", "epsilon", "q", "sigma0", "R", "Kappa", "phi", "r0",
                   "K", "lambda_A", "Omega0", "segment_mode", "Xi", "logG", "lhs", "stable_direct",
                   "stable_criterion", "near_boundary", "criterion_margin", "integral_gamma", "damping_sum", "log_mirror"])

        write_csv(output_dir / "stability_boundaries_v6.csv", boundaries,
                  ["Omega0", "segment_mode", "K", "lambdaA_crit_direct", "lambdaA_crit_criterion", "lambdaA_diff", "expansions", "status"])

        summary = summarize(samples, boundaries)
        summary.update({"crossings_direct": crossings["direct"], "crossings_criterion": crossings["criterion"]})
        results_summary["grid_summary"] = summary

        with open(output_dir / "proof_sweep_summary_v6.json", "w", encoding="utf-8") as handle:
            json.dump(results_summary, handle, indent=2)

        plot_paths = plot_outputs(output_dir, lambda_grid, K_grid, Omega_grid, samples, boundaries, segment_modes)

        if not args.no_pdf:
            pdf_path = make_pdf_report(output_dir, summary, plot_paths, asdict(base), segment_modes)
            if pdf_path:
                results_summary["pdf_report"] = str(pdf_path)

    print("Adaptive sweep complete. Review CSV/JSON/PDF outputs for boundaries.")
    print(f"Outputs stored under {output_dir}")


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        raise SystemExit("Python 3.9+ required")
    main()
