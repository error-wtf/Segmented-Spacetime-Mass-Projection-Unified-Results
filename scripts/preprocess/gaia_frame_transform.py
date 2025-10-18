from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import logging
import numpy as np
import pandas as pd
import yaml
from astropy import units as u
from astropy.coordinates import Galactocentric, SkyCoord
from astropy.table import Table


@dataclass
class FrameConfig:
    run_id: str
    interim_root: Path
    frame_config: Dict[str, object]
    output_path: Path


@dataclass
class FrameSummary:
    total: int
    velocity_3d: int
    velocity_tan_only: int
    velocity_none: int


LOG = logging.getLogger("GAIA_FRAME")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert GAIA catalog to galactic and galactocentric frames")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--interim-root", default=Path("data/interim/gaia"), type=Path)
    parser.add_argument("--frame-config", default=Path("configs/cosmology_frame.yaml"), type=Path)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def load_frame_config(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Frame config missing: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_config(args: argparse.Namespace) -> FrameConfig:
    root = args.interim_root / args.run_id
    input_path = root / "gaia_clean.parquet"
    if not input_path.exists():
        raise FileNotFoundError(f"Clean catalog missing: {input_path}")
    frame_cfg = load_frame_config(args.frame_config)
    out_path = Path(args.output) if args.output else root / "gaia_phase_space.parquet"
    return FrameConfig(args.run_id, root, frame_cfg, out_path)


def load_dataframe(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    table = Table.read(path)
    return table.to_pandas()


def construct_galactocentric(frame_cfg: Dict[str, object]) -> Galactocentric:
    params = frame_cfg.get("icrs_to_galactic", {})
    return Galactocentric(
        galcen_distance=params.get("solar_radius_kpc", 8.2) * u.kpc,
        z_sun=params.get("solar_height_pc", 25.0) * u.pc,
        galcen_v_sun=[
            params.get("solar_motion_kms", {}).get("U", 11.1) * u.km / u.s,
            params.get("solar_motion_kms", {}).get("V", 12.24) * u.km / u.s,
            params.get("solar_motion_kms", {}).get("W", 7.25) * u.km / u.s,
        ],
    )


def transform_frame(df: pd.DataFrame, frame_cfg: Dict[str, object]) -> pd.DataFrame:
    distance_pc = df["distance_pc"].to_numpy(dtype=float)
    pmra = df["pmra"].to_numpy(dtype=float)
    pmdec = df["pmdec"].to_numpy(dtype=float)
    radial = df["radial_velocity"].to_numpy(dtype=float) if "radial_velocity" in df else np.full(len(df), np.nan)

    coord_pos = SkyCoord(
        ra=df["ra"].to_numpy() * u.deg,
        dec=df["dec"].to_numpy() * u.deg,
        distance=distance_pc * u.pc,
        frame="icrs",
    )

    gal = coord_pos.galactic
    df["l_deg"] = gal.l.degree
    df["b_deg"] = gal.b.degree

    gc_frame = construct_galactocentric(frame_cfg)
    galcen_pos = coord_pos.transform_to(gc_frame)

    df["x_kpc"] = galcen_pos.x.to(u.kpc).value
    df["y_kpc"] = galcen_pos.y.to(u.kpc).value
    df["z_kpc"] = galcen_pos.z.to(u.kpc).value

    has_pm = np.isfinite(pmra) & np.isfinite(pmdec)
    has_dist = np.isfinite(distance_pc) & (distance_pc > 0)
    has_rv = np.isfinite(radial)
    mask_tan_any = has_pm & has_dist
    mask_3d = mask_tan_any & has_rv
    mask_tan_only = mask_tan_any & ~has_rv

    vx = np.full(len(df), np.nan)
    vy = np.full(len(df), np.nan)
    vz = np.full(len(df), np.nan)

    if mask_3d.any():
        coord_vel = SkyCoord(
            ra=df.loc[mask_3d, "ra"].to_numpy() * u.deg,
            dec=df.loc[mask_3d, "dec"].to_numpy() * u.deg,
            distance=distance_pc[mask_3d] * u.pc,
            pm_ra_cosdec=pmra[mask_3d] * u.mas / u.yr,
            pm_dec=pmdec[mask_3d] * u.mas / u.yr,
            radial_velocity=radial[mask_3d] * u.km / u.s,
            frame="icrs",
        )
        galcen_vel = coord_vel.transform_to(gc_frame)
        vx[mask_3d] = galcen_vel.v_x.to(u.km / u.s).value
        vy[mask_3d] = galcen_vel.v_y.to(u.km / u.s).value
        vz[mask_3d] = galcen_vel.v_z.to(u.km / u.s).value

    v_tan = np.full(len(df), np.nan)
    if mask_tan_any.any():
        mu_total = np.hypot(pmra[mask_tan_any], pmdec[mask_tan_any])
        v_tan[mask_tan_any] = 4.74047 * mu_total * (distance_pc[mask_tan_any] / 1000.0)

    df["v_x_kms"] = vx
    df["v_y_kms"] = vy
    df["v_z_kms"] = vz
    df["v_tan_kms"] = v_tan

    summary = FrameSummary(
        total=len(df),
        velocity_3d=int(mask_3d.sum()),
        velocity_tan_only=int(mask_tan_only.sum()),
        velocity_none=int((~mask_tan_any).sum()),
    )
    return df, summary


def write_dataframe(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def emit_summary(summary: FrameSummary, path: Path) -> None:
    lines = [
        "[FRAME] galcen positions: OK",
        (
            "[FRAME] v_xyz computed: {velocity_3d:,} rows | "
            "v_tan only: {velocity_tan_only:,} rows | "
            "no velocity: {velocity_none:,} rows"
        ).format(
            velocity_3d=summary.velocity_3d,
            velocity_tan_only=summary.velocity_tan_only,
            velocity_none=summary.velocity_none,
        ),
        f"[FRAME] outfile: {path}",
    ]
    for line in lines:
        if LOG and LOG.hasHandlers():
            LOG.info(line)
        print(line)


def main() -> None:
    args = parse_args()
    cfg = build_config(args)
    df = load_dataframe(cfg.interim_root / "gaia_clean.parquet")
    df, summary = transform_frame(df, cfg.frame_config)
    write_dataframe(df, cfg.output_path)
    emit_summary(summary, cfg.output_path)


if __name__ == "__main__":
    main()
