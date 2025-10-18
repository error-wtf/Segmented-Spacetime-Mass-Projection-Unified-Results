from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from astropy.table import Table


@dataclass
class CleanConfig:
    run_id: str
    raw_dir: Path
    interim_dir: Path
    qa_dir: Path
    sources_config: Dict[str, object]
    strict_gaia_columns: bool = False
    quiet: bool = False


@dataclass
class HarmonizeReport:
    rows_in: int
    rows_after_finite: int
    rows_after_quality: int
    missing_soft: List[str]
    nan_counts: Dict[str, int]
    dropped_nonfinite: int
    dropped_quality: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standardize GAIA catalog outputs")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--raw-root", default=Path("data/raw/gaia"), type=Path)
    parser.add_argument("--interim-root", default=Path("data/interim/gaia"), type=Path)
    parser.add_argument("--qa-root", default=Path("experiments"), type=Path)
    parser.add_argument("--sources-config", default=Path("configs/sources.json"), type=Path)
    parser.add_argument(
        "--strict-gaia-columns",
        action="store_true",
        help="Fail if GAIA uncertainty columns are missing instead of filling them with NaN.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Emit only a compact summary instead of detailed logs.",
    )
    return parser.parse_args()


def load_sources_config(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def build_clean_config(args: argparse.Namespace) -> CleanConfig:
    run_id = args.run_id
    raw_dir = args.raw_root / run_id
    interim_dir = args.interim_root / run_id
    qa_dir = args.qa_root / run_id / "qa"
    interim_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    sources = load_sources_config(args.sources_config)
    return CleanConfig(
        run_id=run_id,
        raw_dir=raw_dir,
        interim_dir=interim_dir,
        qa_dir=qa_dir,
        sources_config=sources,
        strict_gaia_columns=args.strict_gaia_columns,
        quiet=args.quiet,
    )


def iter_input_files(raw_dir: Path) -> Iterable[Path]:
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory missing: {raw_dir}")
    for ext in ("*.parquet", "*.csv", "*.fits"):
        yield from raw_dir.glob(ext)


def read_catalog(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    table = Table.read(path)
    return table.to_pandas()


def concatenate_frames(files: Iterable[Path]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for path in files:
        frames.append(read_catalog(path))
    if not frames:
        raise ValueError("No raw GAIA files discovered")
    return pd.concat(frames, axis=0, ignore_index=True)


COLUMN_MAP = {
    "ra": "ra",
    "ra_icrs": "ra",
    "RA_ICRS": "ra",
    "dec": "dec",
    "dec_icrs": "dec",
    "DE_ICRS": "dec",
    "ra_error": "ra_error",
    "RA_ERROR": "ra_error",
    "dec_error": "dec_error",
    "DEC_ERROR": "dec_error",
    "parallax": "parallax",
    "parallax_error": "parallax_error",
    "pmra": "pmra",
    "pmra_icrs": "pmra",
    "pmra_error": "pmra_error",
    "pmdec": "pmdec",
    "pmdec_icrs": "pmdec",
    "pmdec_error": "pmdec_error",
    "radial_velocity": "radial_velocity",
    "radial_velocity_error": "radial_velocity_error",
    "phot_g_mean_mag": "phot_g_mean_mag",
    "phot_bp_mean_mag": "phot_bp_mean_mag",
    "phot_rp_mean_mag": "phot_rp_mean_mag",
    "bp_rp": "bp_rp",
    "ruwe": "ruwe",
    "astrometric_params_solved": "astrometric_params_solved",
    "astrometric_excess_noise": "astrometric_excess_noise",
    "pmra_pmdec_corr": "pmra_pmdec_corr",
    "source_id": "source_id",
    "SOURCE_ID": "source_id",
    "source": "source_id",
    "sourceid": "source_id",
    "gaia_source_id": "source_id",
}

LOG = logging.getLogger("GAIA_CLEAN")


MANDATORY = [
    "source_id",
    "ra",
    "dec",
    "parallax",
    "pmra",
    "pmdec",
    "phot_g_mean_mag",
    "bp_rp",
]
# Früher hart erzwungen → jetzt soft-required (werden aufgefüllt, wenn fehlen)
SOFT_REQUIRED_ERROR = [
    "ra_error",
    "dec_error",
    "parallax_error",
    "pmra_error",
    "pmdec_error",
]
REQUIRED_COLUMNS = MANDATORY + SOFT_REQUIRED_ERROR
NUMERIC_COLUMNS = [
    "ra",
    "ra_error",
    "dec",
    "dec_error",
    "parallax",
    "parallax_error",
    "pmra",
    "pmra_error",
    "pmdec",
    "pmdec_error",
    "phot_g_mean_mag",
    "bp_rp",
]


def harmonize_columns(
    df: pd.DataFrame,
    *,
    strict_soft: bool = False,
    logger: logging.Logger | None = None,
    quiet: bool = False,
) -> Tuple[pd.DataFrame, HarmonizeReport]:
    def _emit(level: str, message: str) -> None:
        if quiet:
            return
        if logger:
            getattr(logger, level)(message)
        else:
            print(message)

    renamed = {}
    for col in df.columns:
        key = COLUMN_MAP.get(col)
        if key and key not in renamed:
            renamed[col] = key
    df = df.rename(columns=renamed)

    missing_hard = [col for col in MANDATORY if col not in df.columns]
    if "source_id" not in df.columns:
        missing_hard = [col for col in missing_hard if col != "source_id"]
        if strict_soft:
            raise KeyError("Missing mandatory GAIA columns: source_id")
        synthesized = pd.RangeIndex(start=1, stop=len(df) + 1, step=1)
        df["source_id"] = synthesized.astype("int64")
        _emit("warning", "[GAIA-CLEAN] source_id missing -> synthesized sequential ids")
    if missing_hard:
        raise KeyError("Missing mandatory GAIA columns: " + ", ".join(sorted(missing_hard)))

    missing_soft = [col for col in SOFT_REQUIRED_ERROR if col not in df.columns]
    if missing_soft and strict_soft:
        raise KeyError(
            "Missing GAIA uncertainty columns (strict mode): "
            + ", ".join(sorted(missing_soft))
        )
    elif missing_soft:
        for col in missing_soft:
            df[col] = pd.Series([np.nan] * len(df), dtype="float64")
        _emit(
            "info",
            "[GAIA-CLEAN] Missing uncertainty columns filled with NaN: "
            + ", ".join(sorted(missing_soft)),
        )

    rows_in = len(df)
    numeric_cols = [col for col in NUMERIC_COLUMNS if col in df.columns]
    numeric = df[numeric_cols].apply(pd.to_numeric, errors="coerce") if numeric_cols else df
    required_numeric_cols = [col for col in MANDATORY if col in numeric.columns]
    if required_numeric_cols:
        finite_mask = np.isfinite(numeric[required_numeric_cols]).all(axis=1)
    else:
        finite_mask = np.ones(len(df), dtype=bool)
    dropped_nonfinite = int((~finite_mask).sum())
    if dropped_nonfinite:
        _emit(
            "warning",
            "Dropping %d GAIA rows with non-finite required values" % dropped_nonfinite,
        )
    df = df.loc[finite_mask].copy()
    rows_after_finite = len(df)

    if numeric_cols:
        df[numeric_cols] = numeric.loc[finite_mask, numeric_cols].to_numpy()

    if "ruwe" in df.columns:
        before = len(df)
        df = df[df["ruwe"] < 1.4].copy()
        dropped_quality = before - len(df)
        if dropped_quality:
            _emit("info", "RUWE<1.4 filter removed %d rows" % dropped_quality)
    else:
        dropped_quality = 0

    nan_info = {col: int(df[col].isna().sum()) for col in SOFT_REQUIRED_ERROR if col in df.columns}
    return df, HarmonizeReport(
        rows_in=rows_in,
        rows_after_finite=rows_after_finite,
        rows_after_quality=len(df),
        missing_soft=missing_soft,
        nan_counts=nan_info,
        dropped_nonfinite=dropped_nonfinite,
        dropped_quality=dropped_quality,
    )


def compute_quality_flags(df: pd.DataFrame) -> pd.Series:
    parallax_over_error = df["parallax"] / df["parallax_error"].replace(0, np.nan)
    ruwe = df.get("ruwe", np.nan)
    quality = np.full(len(df), "warn", dtype=object)
    good_mask = (parallax_over_error >= 5.0) & (ruwe <= 1.4)
    bad_mask = parallax_over_error < 2.0
    quality[good_mask] = "good"
    quality[bad_mask] = "bad"
    return pd.Series(quality, index=df.index, name="quality_flag")


def estimate_distance(df: pd.DataFrame) -> pd.DataFrame:
    parallax = df["parallax"].to_numpy(dtype=float)
    parallax_err = df["parallax_error"].to_numpy(dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        distance_pc = np.where(parallax > 0, 1e3 / parallax, np.nan)
        sigma_pc = np.where(parallax > 0, 1e3 * parallax_err / (parallax ** 2), np.nan)
    df["distance_pc"] = distance_pc
    df["distance_sigma_pc"] = sigma_pc
    return df


def add_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["parallax_over_error"] = df["parallax"] / df["parallax_error"].replace(0, np.nan)
    df["quality_flag"] = compute_quality_flags(df)
    df = estimate_distance(df)
    df["A_G"] = np.nan
    df["E_BP_RP"] = np.nan
    return df


def write_outputs(df: pd.DataFrame, cfg: CleanConfig) -> Path:
    output_path = cfg.interim_dir / "gaia_clean.parquet"
    df.to_parquet(output_path, index=False)
    return output_path


def plot_histogram(series: pd.Series, title: str, path: Path) -> None:
    plt.figure(figsize=(8, 5))
    valid = series.replace([np.inf, -np.inf], np.nan).dropna()
    if valid.empty:
        plt.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        plt.hist(valid.to_numpy(), bins=60, color="#3366cc", alpha=0.75)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def generate_qa(df: pd.DataFrame, cfg: CleanConfig) -> None:
    metrics = {
        "parallax_hist.png": (df["parallax"], "Parallax Distribution (mas)"),
        "pmra_hist.png": (df["pmra"], "Proper Motion RA (mas/yr)"),
        "pmdec_hist.png": (df["pmdec"], "Proper Motion Dec (mas/yr)"),
        "ruwe_hist.png": (df.get("ruwe", pd.Series(dtype=float)), "RUWE Distribution"),
    }
    for name, (series, title) in metrics.items():
        plot_histogram(series, title, cfg.qa_dir / name)


def _emit_summary_line(line: str, cfg: CleanConfig) -> None:
    if LOG and LOG.hasHandlers():
        LOG.info(line)
    if cfg.quiet or not (LOG and LOG.hasHandlers()):
        print(line)


def emit_summary(report: HarmonizeReport, cfg: CleanConfig, path: Path) -> None:
    rows_kept = report.rows_after_quality
    dropped_total = report.rows_in - rows_kept
    summary_lines = [
        f"[GAIA-CLEAN] rows_in={report.rows_in}, rows_kept={rows_kept}, dropped={dropped_total} "
        f"(nonfinite={report.dropped_nonfinite}, quality={report.dropped_quality})"
    ]
    if report.missing_soft:
        filled_counts = {k: report.nan_counts.get(k, 0) for k in report.missing_soft}
        summary_lines.append(
            "[GAIA-CLEAN] filled uncertainty columns with NaN: "
            + ", ".join(sorted(report.missing_soft))
            + f" | counts={filled_counts}"
        )
    else:
        summary_lines.append("[GAIA-CLEAN] required columns present: OK")
    summary_lines.append(f"[GAIA-CLEAN] outfile: {path}")

    for line in summary_lines:
        _emit_summary_line(line, cfg)


def clean_gaia_catalog(cfg: CleanConfig) -> Path:
    files = list(iter_input_files(cfg.raw_dir))
    df = concatenate_frames(files)
    df, report = harmonize_columns(
        df,
        strict_soft=cfg.strict_gaia_columns,
        logger=LOG,
        quiet=cfg.quiet,
    )
    df = add_fields(df)
    path = write_outputs(df, cfg)
    generate_qa(df, cfg)
    emit_summary(report, cfg, path)
    return path


def main() -> None:
    args = parse_args()
    cfg = build_clean_config(args)
    clean_gaia_catalog(cfg)


if __name__ == "__main__":
    main()
