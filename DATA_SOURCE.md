# Data Source Notes for `real_data_full.csv`

⚠️ **Token Authentication Required:** ESO data fetching requires manual token generation from ESO web portal.

**Complete workflow:** See [`docs/MANUAL_ESO_DATA_ACQUISITION_GUIDE.md`](docs/MANUAL_ESO_DATA_ACQUISITION_GUIDE.md)

This file is produced by `fetch_eso_br_gamma.py`, which requires an ESO access token.

## How to generate

### 1. Get ESO Token (Manual)
1. Log in to https://archive.eso.org/
2. Perform query via web interface
3. Request download → Copy token (valid 24-48h)

### 2. Run Fetch Script
```bash
# With token (required)
python fetch_eso_br_gamma.py --mode get-proof \
  --endpoint https://example.eso.org/api/get_proof \
  --since 2025-07-15 \
  --out real_data_full.csv \
  --token YOUR_ESO_TOKEN
```

### Legacy TAP (also requires token)
```bash
python fetch_eso_br_gamma.py --mode tap \
  --endpoint https://tap.eso.org/tap \
  --token YOUR_ESO_TOKEN \
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
