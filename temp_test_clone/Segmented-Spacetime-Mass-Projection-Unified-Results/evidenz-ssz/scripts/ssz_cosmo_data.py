#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data loading utilities for SSZ cosmology validation."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

DEFAULT_DATA_DIR = Path("/mnt/data")

ALIAS_MAP = {
    "redshift": "z",
    "zd": "z",
    "mu_th": "mu",
    "muobs": "mu",
    "mu_err": "mu_err",
    "dmu": "mu_err",
    "dv_by_rd": "DV_by_rd",
    "dv": "DV",
    "dv/rd": "DV_by_rd",
    "dm_by_rd": "DM_by_rd",
    "dh_by_rd": "DH_by_rd",
    "ell_a": "ell_A",
    "la": "ell_A",
    "sigma_fs8": "err",
    "fsigma8": "fs8",
    "surface_brightness": "SB",
}


def _apply_aliases(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "_")
        if key in ALIAS_MAP:
            rename_map[col] = ALIAS_MAP[key]
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def _read_csv_or_none(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        return _apply_aliases(df)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to read {path}: {exc}") from exc


def _synthetic_sn() -> pd.DataFrame:
    z = np.linspace(0.01, 1.5, 25)
    mu = 5 * np.log10((1 + z) * 3000 * z) + 25
    err = np.full_like(mu, 0.15)
    return pd.DataFrame({"z": z, "mu": mu, "mu_err": err})


def _synthetic_bao() -> pd.DataFrame:
    z = np.array([0.106, 0.35, 0.57, 1.0])
    dv_rd = np.array([2.98, 6.5, 8.8, 11.5])
    err = np.array([0.12, 0.3, 0.4, 0.6])
    return pd.DataFrame({"z": z, "DV_by_rd": dv_rd, "err": err})


def _synthetic_cmb() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ell_A": [301.0],
            "err_ell_A": [0.9],
            "R": [1.75],
            "err_R": [0.03],
        }
    )


def _synthetic_fs8() -> pd.DataFrame:
    z = np.linspace(0.1, 1.0, 10)
    fs8 = 0.5 + 0.2 * np.exp(-z)
    err = np.full_like(fs8, 0.05)
    return pd.DataFrame({"z": z, "fs8": fs8, "err": err})


def _synthetic_tolman() -> pd.DataFrame:
    z = np.linspace(0.1, 1.8, 12)
    sb = 1e3 * (1 + z) ** -4
    noise = np.random.default_rng(42).normal(0, 50, size=z.size)
    return pd.DataFrame({"z": z, "SB": sb + noise, "err": np.full_like(sb, 60)})


def _synthetic_bbn() -> pd.DataFrame:
    return pd.DataFrame({"N_eff": [3.0], "err": [0.3]})


@dataclass
class DataBundle:
    sn: Tuple[pd.DataFrame, Dict]
    bao: Tuple[pd.DataFrame, Dict]
    cmb: Tuple[pd.DataFrame, Dict]
    bbn: Tuple[pd.DataFrame, Dict]
    fs8: Tuple[pd.DataFrame, Dict]
    tolman: Tuple[pd.DataFrame, Dict]


class DataRepository:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR

    def _resolve(self, stem: str) -> Path:
        return self.data_dir / f"{stem}.csv"

    def _load_or_synth(self, stem: str, synth_fn) -> Tuple[pd.DataFrame, Dict]:
        df = _read_csv_or_none(self._resolve(stem))
        if df is None:
            df = synth_fn()
            meta = {"source": "synthetic"}
        else:
            meta = {"source": "csv", "path": str(self._resolve(stem))}
        return df, meta

    def load_sn(self) -> Tuple[pd.DataFrame, Dict]:
        df, meta = self._load_or_synth("sn", _synthetic_sn)
        needed = {"z", "mu", "mu_err"}
        missing = needed - set(df.columns)
        if missing:
            raise ValueError(f"SN dataset missing columns: {missing}")
        return df, meta

    def load_bao(self) -> Tuple[pd.DataFrame, Dict]:
        df, meta = self._load_or_synth("bao", _synthetic_bao)
        if "cov" in df.columns:
            try:
                meta["cov"] = json.loads(df["cov"].iloc[0])
            except Exception:
                pass
        return df, meta

    def load_cmb(self) -> Tuple[pd.DataFrame, Dict]:
        df, meta = self._load_or_synth("cmb", _synthetic_cmb)
        return df, meta

    def load_bbn(self) -> Tuple[pd.DataFrame, Dict]:
        df, meta = self._load_or_synth("bbn", _synthetic_bbn)
        return df, meta

    def load_fs8(self) -> Tuple[pd.DataFrame, Dict]:
        df, meta = self._load_or_synth("fs8", _synthetic_fs8)
        return df, meta

    def load_tolman(self) -> Tuple[pd.DataFrame, Dict]:
        df, meta = self._load_or_synth("tolman", _synthetic_tolman)
        return df, meta

    def load_all(self) -> DataBundle:
        return DataBundle(
            sn=self.load_sn(),
            bao=self.load_bao(),
            cmb=self.load_cmb(),
            bbn=self.load_bbn(),
            fs8=self.load_fs8(),
            tolman=self.load_tolman(),
        )
