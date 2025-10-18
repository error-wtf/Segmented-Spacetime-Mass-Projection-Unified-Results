import numpy as np
import pandas as pd
import pytest

from scripts.preprocess.gaia_clean_map import REQUIRED_COLUMNS, SOFT_REQUIRED_ERROR, harmonize_columns


def _base_frame() -> pd.DataFrame:
    data = {
        "source_id": [111, 222],
        "ra": [10.0, 11.0],
        "ra_error": [0.01, 0.02],
        "dec": [-5.0, 1.0],
        "dec_error": [0.01, 0.02],
        "parallax": [0.5, 0.4],
        "parallax_error": [0.1, 0.1],
        "pmra": [0.1, -0.3],
        "pmra_error": [0.02, 0.02],
        "pmdec": [-0.2, 0.4],
        "pmdec_error": [0.02, 0.02],
        "phot_g_mean_mag": [13.4, 12.1],
        "bp_rp": [0.5, 1.2],
        "ruwe": [1.0, 1.2],
    }
    return pd.DataFrame(data)


def test_harmonize_columns_preserves_required():
    df = _base_frame()
    out, report = harmonize_columns(df)
    assert len(out) == len(df)
    for col in REQUIRED_COLUMNS:
        assert col in out.columns
        assert np.isfinite(out[col]).all()
    assert not report.missing_soft
    assert report.dropped_nonfinite == 0


def test_harmonize_columns_rejects_missing_errors():
    df = _base_frame().drop(columns=["pmra_error"])
    with pytest.raises(KeyError):
        harmonize_columns(df, strict_soft=True)


def test_harmonize_columns_soft_fills_missing_errors():
    df = _base_frame().drop(columns=["pmra_error", "pmdec_error"])
    out, report = harmonize_columns(df, strict_soft=False)
    for col in SOFT_REQUIRED_ERROR:
        assert col in out.columns
    assert out["pmra_error"].isna().all()
    assert out["pmdec_error"].isna().all()
    assert set(report.missing_soft) == {"pmra_error", "pmdec_error"}
    assert report.nan_counts["pmra_error"] == len(df)
    assert report.nan_counts["pmdec_error"] == len(df)
