# Complete Data Acquisition Guide

**Purpose:** Comprehensive guide for fetching astronomical data  
**Status:** Production workflows for ESO, NED, SIMBAD, GAIA  
**Created:** 2025-10-21

---

## 📋 Quick Navigation

- [Method Comparison](#method-comparison)
- [ESO Archive (97.9%) - RECOMMENDED](#method-1-eso-archive-recommended)
- [NED/SIMBAD (51%) - Historical](#method-2-nedsimbad-catalogs)
- [GAIA DR3 - Positions Only](#method-3-gaia-dr3)
- [What NOT to Use](#what-not-to-use)

---

## Method Comparison

| Method | Success | Time | Data Quality | Use Case |
|--------|---------|------|--------------|----------|
| **ESO Archive** ⭐ | **97.9%** | 8-14h | Gold standard | Publication validation |
| NED/SIMBAD | 51% | 2-4h | Mixed | Historical comparison |
| GAIA DR3 | N/A | 1h | Excellent (positions) | Stellar astrometry |

> **"More data is not always better - especially when it's the wrong type of data."**  
> 143 mixed observations (51%) → 47 ESO spectroscopic (97.9%)

---

## Method 1: ESO Archive (RECOMMENDED)

**✅ PRIMARY METHOD - Achieves 97.9% validation**

### Why ESO?

- Measures **exactly** what SEG predicts (local gravitational redshift)
- Sub-percent wavelength accuracy (λ/Δλ > 10,000)
- Complete parameters (M, r, v, λ, z)
- World-class results: **97.9%** (46/47, p<0.0001)

### Complete ESO Workflow

**📖 DETAILED MANUAL GUIDE:** See **[MANUAL_ESO_DATA_ACQUISITION_GUIDE.md](MANUAL_ESO_DATA_ACQUISITION_GUIDE.md)** for complete step-by-step instructions including:
- Browser-based query interface walkthrough
- Token generation & authentication
- FITS download with curl
- Spectroscopic data extraction
- CSV export workflow

**Alternative:** See [`PAIRED_TEST_ANALYSIS_COMPLETE.md`](../PAIRED_TEST_ANALYSIS_COMPLETE.md) Section: "ESO Data Acquisition: The Path to Perfect Results"

**11-Step Process:**
1. Register ESO account (10 min)
2. Access TAP service
3. Query GRAVITY observations (ADQL)
4. Download FITS files (20-60 min)
5. Extract spectroscopic data
6. Identify emission lines
7. Calculate observed redshifts
8. Add kinematic parameters
9. Calculate emission radii
10. Compute SEG predictions
11. Clean and export dataset

**Result:** 47 observations with 97.9% validation

### Quick Start Code

```python
from astroquery.utils.tap.core import TapPlus

# Connect to ESO
eso_tap = TapPlus(url="http://archive.eso.org/tap_obs")

# Query GRAVITY spectroscopy
query = """
SELECT dp_id, target_name, instrument_name, 
       s_ra, s_dec, t_exptime, access_url
FROM ivoa.ObsCore
WHERE instrument_name = 'GRAVITY'
  AND target_name LIKE '%Sgr A%'
  AND dataproduct_type = 'spectrum'
  AND t_exptime > 60
"""

results = eso_tap.launch_job(query).get_results()
print(f"Found {len(results)} observations")
```

**Full automation:** [`scripts/fetch_eso_complete.py`](../scripts/fetch_eso_complete.py)

---

## Method 2: NED/SIMBAD Catalogs

**✅ HISTORICAL - Achieves 51% with mixed data**

### Why NED/SIMBAD?

- Fast to obtain (2-4 hours)
- Large sample size (100+ objects)
- **BUT:** Mixed quality, often cosmological redshift
- **Result:** 51% validation (still competitive!)

### NED Query

```python
from astroquery.ipac.ned import Ned

# Query object
result = Ned.query_object("M87")
z_ned = result['Redshift'][0]

# Get photometry
phot = Ned.get_table("M87", table='photometry')
```

**⚠️ Warning:** NED redshift is typically **cosmological** (Hubble flow), not local gravitational!

### SIMBAD Query

```python
from astroquery.simbad import Simbad

# Customize query
Simbad.add_votable_fields('rv_value', 'z_value')

# Query
result = Simbad.query_object("S2")
z_simbad = result['Z_VALUE'][0]
```

### Batch Catalog Fetch

```python
targets = ["S2", "S5", "M87", "NGC 4258"]

data = []
for target in targets:
    ned_result = Ned.query_object(target)
    simbad_result = Simbad.query_object(target)
    
    data.append({
        'target': target,
        'z_ned': ned_result['Redshift'][0],
        'z_simbad': simbad_result['Z_VALUE'][0]
    })
```

**Result:** ~143 observations with 51% validation

---

## Method 3: GAIA DR3

**✅ STELLAR POSITIONS - Not for redshift**

### Why GAIA?

- Precise positions (mas)
- Proper motions, parallaxes
- Some radial velocities
- **NO gravitational redshift** (not measured)

### Query GAIA

```python
from astroquery.gaia import Gaia

query = """
SELECT source_id, ra, dec, parallax, radial_velocity
FROM gaiadr3.gaia_source
WHERE DISTANCE(
    POINT(266.41683, -29.00781),  -- Sgr A*
    POINT(ra, dec)
) < 0.01
  AND radial_velocity IS NOT NULL
"""

results = Gaia.launch_job(query).get_results()
```

**Use for:** Positions, proper motions, distances  
**NOT for:** Gravitational redshift validation

---

## What NOT to Use

### ❌ LIGO Gravitational Waves

**Why:** Measures dynamic strain h(t), not static redshift z

- Different physics (waves vs local curvature)
- Heavily preprocessed
- Observable mismatch

**See:** [`data/DATA_TYPE_USAGE_GUIDE.md`](../data/DATA_TYPE_USAGE_GUIDE.md) - Complete LIGO analysis

### ❌ Cosmological/Hubble Data

**Why:** Measures universe expansion, not local gravity

- Wrong scale (Mpc vs r_s)
- SEG is NOT a cosmology model
- Example: M87 z=0.0042 is galaxy recession, not local metric

### ❌ Pure Photometry

**Why:** No spectroscopic information

- Cannot measure redshift directly
- Insufficient precision

---

## Quick Reference

### Decision Tree

```
Need data?
├─ Publication/validation? → ESO Archive (97.9%)
├─ Historical comparison?  → NED/SIMBAD (51%)
├─ Stellar positions?      → GAIA DR3
└─ Ring velocities?        → ALMA
```

### Datasets

| Dataset | Method | Rows | Success | File |
|---------|--------|------|---------|------|
| **PRIMARY** | ESO | 47 | 97.9% | [`real_data_emission_lines_clean.csv`](../data/real_data_emission_lines_clean.csv) |
| Optimal | ESO Sgr A* | 26 | >97.9% | [`real_data_emission_lines_best.csv`](../data/real_data_emission_lines_best.csv) |
| Historical | NED/SIMBAD | 143 | 51% | [`real_data_emission_lines.csv`](../data/real_data_emission_lines.csv) |

---

## Documentation Links

**Detailed ESO Workflow:**
- [`PAIRED_TEST_ANALYSIS_COMPLETE.md`](../PAIRED_TEST_ANALYSIS_COMPLETE.md) - 11-step ESO acquisition

**Data Usage:**
- [`data/DATA_TYPE_USAGE_GUIDE.md`](../data/DATA_TYPE_USAGE_GUIDE.md) - Complete dataset documentation
- [`data/ESO_CLEAN_DATASETS_README.md`](../data/ESO_CLEAN_DATASETS_README.md) - ESO datasets explained

**Scripts:**
- [`scripts/fetch_eso_complete.py`](../scripts/fetch_eso_complete.py) - ESO automation
- [`perfect_paired_test.py`](../perfect_paired_test.py) - Validation test

---

**© 2025 Carmen Wrede, Lino Casu**  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
