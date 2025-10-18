import numpy as np, pandas as pd
from scripts.ssz.cosmology import build_cosmo_fields

def test_cosmo_fields_added():
    df = pd.DataFrame({"x":[0,1], "y":[0,1], "rho":[0.2, 5.0]})
    out = build_cosmo_fields(df, density_col="rho", gamma_cfg=dict(alpha=0.8,beta=0.6,floor=0.02))
    for c in ("gamma_seg","z_seg","kappa_proxy","vrot_mod"):
        assert c in out.columns
    assert (out["gamma_seg"].between(0.02,1.0)).all()
