
# Data Source Notes for `real_data_full.csv`

This file is produced by `fetch_eso_br_gamma.py`, which can talk to either the new
post-2025-07-15 "get_proof" API or the legacy TAP service.

## How to generate

### New pipeline (recommended)
```bash
python fetch_eso_br_gamma.py --mode get-proof \
  --endpoint https://example.eso.org/api/get_proof \
  --since 2025-07-15 \
  --out real_data_full.csv \
  --token $ESO_TOKEN
```

### Legacy TAP (fallback)
```bash
python fetch_eso_br_gamma.py --mode tap \
  --endpoint https://tap.eso.org/tap \
  --out real_data_full.csv
```

Use `--dry-run` to create a small example CSV without calling the network.

## Output schema (units)
- `case` (str): object identifier
- `category` (str): coarse class, e.g. `s-star`, `jet`, `psr`, `agn`
- `M_solar` (float): mass in solar masses
- `a_m` (float): semi-major axis in meters
- `e` (float): orbital eccentricity
- `f_deg` (float): true anomaly in degrees
- `z` (float): observed redshift (dimensionless)
- `z_geom_hint` (float): geometric/GR hint z (dimensionless)
- `r_emit_m` (float): emission radius in meters
- `v_tot_mps` (float): total speed in m/s
- `v_los_mps` (float): line-of-sight speed in m/s

A JSON sidecar `<csv>.meta.json` is written to record the endpoint, date window, and row count.
