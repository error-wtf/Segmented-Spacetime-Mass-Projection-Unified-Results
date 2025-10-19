# Data Type Usage Guide

Created: 2025-10-19 11:52:26

## Data Files

### 1. `real_data_emission_lines.csv` (143 rows)

**Type:** Emission line data with Doppler shifts

**Contains:**
- S2 star orbital data
- Pulsar observations
- Binary system measurements
- AGN emission lines

**Use For:**
- ✅ Paired test (SEG vs GR×SR)
- ✅ Redshift predictions
- ✅ Orbital dynamics
- ✅ Time-series analysis

**Do NOT Use For:**
- ❌ Pure continuum analysis

**Why It Works:**
- z_obs represents actual Doppler shift of emission
- Can meaningfully compare to predictions
- SEG better in 143 rows (55%)

---

### 2. `real_data_continuum.csv` (284 rows)

**Type:** Continuum spectra (M87, Sgr A*)

**Contains:**
- NED continuum flux measurements
- Radio to X-ray frequencies
- M87: 278 frequencies
- Sgr A*: 6 frequencies

**Use For:**
- ✅ Multi-frequency spectrum analysis
- ✅ Information Preservation test
- ✅ Hawking spectrum analysis
- ✅ Broadband SED fitting

**Do NOT Use For:**
- ❌ Paired redshift test
- ❌ z_obs comparison (source redshift only)

**Why It Doesn't Work for Paired Test:**
- z_obs = source recession velocity (M87: 0.0042)
- z_geom = emission gravitational redshift (0.8 near horizon)
- Cannot compare source motion to emission gravity
- Different physical quantities!

---

### 3. `real_data_mixed.csv` (0 rows if exists else 0)

**Type:** Data with both aspects

**Use:** Case-by-case evaluation

---

### 4. `real_data_full_typed.csv` (427 rows)

**Type:** Complete dataset with 'data_type' column

**Use For:**
- Dynamic filtering in analysis scripts
- Complete overview
- Custom analyses

**Filtering Examples:**

```python
import pandas as pd

df = pd.read_csv('data/real_data_full_typed.csv')

# For paired test
emission = df[df['data_type'] == 'emission_line']

# For spectrum analysis
continuum = df[df['data_type'] == 'continuum']

# All multi-frequency
multi_freq = df.groupby('source').filter(lambda x: len(x) > 1)
```

---

## Analysis Type → Data Type Mapping

| Analysis | Data Type | File | Rows |
|----------|-----------|------|------|
| **Paired Test** | Emission lines | real_data_emission_lines.csv | 143 |
| **Spectrum Analysis** | Continuum | real_data_continuum.csv | 284 |
| **Information Preservation** | Both (multi-freq) | real_data_full_typed.csv | 427 |
| **Jacobian Reconstruction** | Both | real_data_full_typed.csv | 427 |
| **Hawking Proxy** | Both | real_data_full_typed.csv | 427 |
| **Complete Overview** | All | real_data_full_typed.csv | 427 |

---

## Physical Understanding

### Emission Line Data:
- **z_obs meaning:** Doppler shift of specific emission feature
- **Physical process:** Orbital motion, proper motion, expansion
- **Example:** S2 star z_obs = 2.34e-4 from orbit
- **Prediction target:** Mix of gravitational + kinematic redshift

### Continuum Data:
- **z_obs meaning:** Source cosmological/recession redshift
- **Physical process:** Hubble flow, peculiar velocity of source
- **Example:** M87 z_obs = 0.0042 (recession of galaxy)
- **Prediction target:** NOT emission redshift (different quantity!)

---

## Scientific Rationale

**Why Separate?**

Because we were comparing apples to oranges:
- Emission z_obs (local): 2.34e-4 typical
- Source z_obs (global): 0.0042 typical
- These are different physical quantities!

**Correct Approach:**
- Match data type to analysis type
- Document which data works for which analysis
- Transparent about limitations

**Result:**
- Scientifically rigorous
- No misleading comparisons
- Clear usage guidelines

---

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
