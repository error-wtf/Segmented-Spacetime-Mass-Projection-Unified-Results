from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
import yaml

from .cosmology import build_cosmo_fields

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SWEEP_CONFIG = ROOT / "configs" / "param_sweep.yaml"
DEFAULT_MODEL_ROOT = ROOT / "models" / "cosmology"


@dataclass
class SweepParams:
    alpha: float
    beta: float
    floor: float
    rotation_p: float


def load_base_catalog(
    run_id: str,
    *,
    data_root: Path | None = None,
    model_root: Path | None = None,
) -> pd.DataFrame:
    model_root = model_root or DEFAULT_MODEL_ROOT
    model_path = model_root / run_id / "ssz_field.parquet"
    if model_path.exists():
        return pd.read_parquet(model_path)

    data_root = data_root or (ROOT / "data")
    interim_path = data_root / "interim" / "gaia" / run_id / "gaia_phase_space.parquet"
    if interim_path.exists():
        return pd.read_parquet(interim_path)
    raise FileNotFoundError(
        f"Neither cosmology field nor phase-space catalog found for run_id={run_id}"
    )


def _score_fields(df: pd.DataFrame, rotation_weight: float, density_weight: float) -> Dict[str, float]:
    scores = {}
    if "gamma_seg" in df.columns:
        scores["gamma_mean"] = float(np.nanmean(df["gamma_seg"]))
    if "z_seg" in df.columns:
        scores["z_median"] = float(np.nanmedian(df["z_seg"]))
    if "vrot_mod" in df.columns:
        vrot = np.nanmean(df["vrot_mod"])
        scores["vrot_mean"] = float(vrot)
        scores["vrot_score"] = float(rotation_weight * vrot)
    if "ssz_density" in df.columns:
        density = float(np.nanmean(df["ssz_density"]))
        scores["density_mean"] = density
        scores["density_score"] = float(density_weight * density)
    return scores


def _scalar_score(scores: Dict[str, float], baseline_weight: float) -> float:
    baseline = scores.get("gamma_mean", 0.0) + scores.get("z_median", 0.0)
    return baseline_weight * baseline + scores.get("vrot_score", 0.0) + scores.get("density_score", 0.0)


def run_sweep(
    run_id: str,
    *,
    params_cfg: Path = DEFAULT_SWEEP_CONFIG,
    data_root: Path | None = None,
    model_root: Path | None = None,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    cfg = yaml.safe_load(params_cfg.read_text(encoding="utf-8"))
    grid = cfg.get("grid", {})
    scoring_cfg = cfg.get("scoring", {})

    combos: Iterable[SweepParams] = (
        SweepParams(alpha=a, beta=b, floor=f, rotation_p=p)
        for a, b, f, p in itertools.product(
            grid.get("alpha", [0.8]),
            grid.get("beta", [0.6]),
            grid.get("floor", [0.02]),
            grid.get("rotation_p", [0.5]),
        )
    )

    df_base = load_base_catalog(run_id, data_root=data_root, model_root=model_root)
    results: List[Dict[str, float]] = []

    for params in combos:
        gamma_cfg = {"alpha": params.alpha, "beta": params.beta, "floor": params.floor}
        fields = build_cosmo_fields(
            df_base,
            density_col="ssz_density" if "ssz_density" in df_base.columns else "rho",
            gamma_cfg=gamma_cfg,
            rot_power=params.rotation_p,
        )
        scores = _score_fields(
            fields,
            rotation_weight=float(scoring_cfg.get("rotation_weight", 0.5)),
            density_weight=float(scoring_cfg.get("density_weight", 0.2)),
        )
        scalar = _scalar_score(scores, float(scoring_cfg.get("baseline_weight", 1.0)))
        result = {
            "run_id": run_id,
            "alpha": params.alpha,
            "beta": params.beta,
            "floor": params.floor,
            "rotation_p": params.rotation_p,
            "score": scalar,
        }
        result.update(scores)
        results.append(result)

    df_results = pd.DataFrame(results)
    report_dir = ROOT / "reports" / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    sweep_csv = report_dir / "param_sweep_results.csv"
    df_results.to_csv(sweep_csv, index=False)

    summary = {
        "best": df_results.sort_values("score", ascending=False).head(1).to_dict(orient="records"),
        "count": len(df_results),
        "config": str(params_cfg.relative_to(ROOT)),
        "results_csv": str(sweep_csv.relative_to(ROOT)),
    }

    summary_path = report_dir / "param_sweep_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return df_results, summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run SSZ parameter sweep")
    parser.add_argument("run_id")
    parser.add_argument("--config", type=Path, default=DEFAULT_SWEEP_CONFIG)
    args = parser.parse_args()
    run_sweep(args.run_id, params_cfg=args.config)
