# Segmented Radiowave Propagation Guide

## Overview

The **SSZ Segwave** module implements radiowave propagation through segmented spacetime shells based on the γ_seg(r) formalism developed by Casu & Wrede. This tool predicts velocity profiles and frequency shifts in molecular ring structures around star-forming regions.

## Physical Model

### Core Formalism

The segmented spacetime framework models spacetime as a sequence of discrete shells, each with its own metric scaling factor γ_k. Radio waves propagating through these shells experience:

1. **Velocity Evolution**:
   ```
   v_k = v_{k-1} · q_k^{-α/2}
   ```
   where q_k = γ_k / γ_{k-1} is the shell-to-shell ratio.

2. **Frequency Shift**:
   ```
   ν_out(r_k) = ν_in · γ_k^{-1/2}
   ```

3. **Gamma Ratio Proxy**:
   ```
   q_k ≈ (T_k / T_{k-1})^β · (n_k / n_{k-1})^η
   ```
   
   - **T**: Temperature (K) - primary observable from molecular line emission
   - **n**: Number density (cm⁻³) - optional, from continuum or secondary tracers
   - **β**: Temperature coupling exponent (default 1.0)
   - **η**: Density coupling exponent (default 0.0)

### Calibration Parameter α

The parameter **α** controls the strength of segment-induced velocity damping:
- **α = 0**: No segmentation effect (classical propagation)
- **α = 1**: Standard segmented spacetime prediction
- **α > 1**: Enhanced segmentation coupling
- **α < 1**: Weak segmentation regime

The `--fit-alpha` mode uses RMSE minimization to determine the optimal α from observations.

## Data Format

### Input CSV Structure

The input CSV must contain:

**Required columns:**
- `ring`: Ring/shell identifier (integer or string)
- `T`: Temperature in Kelvin (float, must be > 0)

**Optional columns:**
- `n`: Number density in cm⁻³ (float, must be > 0)
- `v_obs`: Observed velocity in km/s (float) - required for `--fit-alpha`

**Example:**
```csv
ring,T,n,v_obs
1,80.5,1.2e5,8.2
2,72.3,9.8e4,9.1
3,65.8,7.5e4,10.3
4,58.2,5.2e4,11.8
5,52.1,3.8e4,13.2
```

### Sources Manifest (Optional)

A JSON file documenting data sources and references in `data/observations/sources.json`.

## CLI Usage

### Basic Syntax

```bash
ssz-rings --csv DATA.csv --v0 VELOCITY [--alpha ALPHA | --fit-alpha] [OPTIONS]
```

### Required Arguments

- `--csv PATH`: Path to CSV file with ring data
- `--v0 FLOAT`: Initial velocity at innermost shell (km/s)
- `--alpha FLOAT` **OR** `--fit-alpha`: Fixed α value or fit α to observations

### Optional Arguments

- `--beta FLOAT`: Temperature exponent (default: 1.0)
- `--eta FLOAT`: Density exponent (default: 0.0)
- `--nu-in FLOAT`: Input frequency in Hz for frequency tracking
- `--out-table PATH`: Save results table to CSV
- `--out-report PATH`: Save summary report to text file
- `--out-plot PATH`: Save velocity plot to PNG (requires matplotlib)

## Examples

### Example 1: Fixed α with Basic Output

```bash
ssz-rings --csv data/observations/ring_temperature_data.csv \
          --v0 12.5 \
          --alpha 1.25 \
          --out-table reports/rings_alpha125.csv \
          --out-report reports/summary_alpha125.txt
```

### Example 2: Fit α to Observations

```bash
ssz-rings --csv data/observations/ring_temperature_data.csv \
          --v0 12.5 \
          --fit-alpha \
          --out-table reports/rings_fitted.csv \
          --out-report reports/summary_fitted.txt \
          --out-plot reports/velocity_plot.png
```

### Example 3: Frequency Tracking

```bash
ssz-rings --csv data/observations/ring_temperature_data.csv \
          --v0 12.5 \
          --alpha 1.0 \
          --nu-in 3.0e11 \
          --out-table reports/rings_with_frequency.csv
```

## Output Interpretation

### Results Table Columns

- **ring**: Shell identifier
- **T**: Temperature (K)
- **n**: Density (cm⁻³) - if provided
- **q_k**: Gamma ratio for this shell
- **v_pred**: Predicted velocity (km/s)
- **v_obs**: Observed velocity (km/s) - if provided
- **residual**: v_pred - v_obs (km/s) - if v_obs provided
- **nu_out_Hz**: Output frequency (Hz) - if --nu-in specified

### Validation Metrics

- **MAE**: Mean Absolute Error (km/s)
- **RMSE**: Root Mean Square Error (km/s)
- **Max |residual|**: Worst-case deviation

## Python API

```python
from ssz.segwave import predict_velocity_profile, fit_alpha, load_ring_data

# Load data
df = load_ring_data("data/observations/ring_temperature_data.csv")

# Fit alpha
alpha_opt, metrics = fit_alpha(
    rings=df['ring'].values,
    T=df['T'].values,
    v0=12.5,
    v_obs=df['v_obs'].values
)

print(f"Optimal α: {alpha_opt:.4f}, RMSE: {metrics['rmse']:.4f} km/s")
```

## License

Copyright © 2025 Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
