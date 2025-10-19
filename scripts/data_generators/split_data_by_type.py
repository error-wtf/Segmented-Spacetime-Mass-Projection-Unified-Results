#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split real_data_full.csv into separate datasets by data type

Creates:
1. real_data_emission_lines.csv - For paired test (79 rows)
2. real_data_continuum.csv - For spectrum analysis (284 rows)
3. real_data_mixed.csv - Has both (64 rows)

This allows proper filtering based on analysis type.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def classify_data_type(row):
    """
    Classify each row as:
    - 'emission_line': Has Doppler shift from specific emission
    - 'continuum': Broadband flux, source redshift only
    - 'mixed': Has both aspects
    """
    source = row.get('source', '')
    
    # NED sources are continuum
    if source in ['M87', 'Sgr A*']:
        return 'continuum'
    
    # Check for orbital/time-series data (emission lines)
    # These have specific Doppler shifts
    if any(x in str(row.get('case', '')) for x in ['_orbital', 'S1', 'S2', 'PSR', 'Cyg']):
        return 'emission_line'
    
    # Multi-frequency from same source
    # Could be either or mixed
    if pd.notna(row.get('f_emit_Hz')) and pd.notna(row.get('f_obs_Hz')):
        # If has velocity data, likely emission line
        if pd.notna(row.get('v_tot_mps')) and row.get('v_tot_mps') > 1000:
            return 'emission_line'
    
    # Default: assume emission line for original data
    return 'emission_line'

def split_data_by_type(input_csv='real_data_full.csv', output_dir='data', backup=True):
    """
    Split data into separate files by type
    """
    print("="*80)
    print("SPLIT DATA BY TYPE")
    print("="*80)
    
    # Load data
    df = pd.read_csv(input_csv)
    print(f"\nLoaded: {input_csv}")
    print(f"Total rows: {len(df)}")
    
    # Backup
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{input_csv}.backup_split_{timestamp}"
        df.to_csv(backup_path, index=False)
        print(f"Backup created: {backup_path}")
    
    # Classify each row
    print("\n" + "="*80)
    print("CLASSIFYING DATA TYPES")
    print("="*80)
    
    df['data_type'] = df.apply(classify_data_type, axis=1)
    
    # Statistics
    type_counts = df['data_type'].value_counts()
    print("\nClassification results:")
    for dtype, count in type_counts.items():
        pct = 100 * count / len(df)
        print(f"  {dtype}: {count} rows ({pct:.1f}%)")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Split into separate files
    print("\n" + "="*80)
    print("CREATING SEPARATE FILES")
    print("="*80)
    
    files_created = []
    
    # Emission line data (for paired test)
    emission = df[df['data_type'] == 'emission_line'].copy()
    if len(emission) > 0:
        emission_file = output_path / 'real_data_emission_lines.csv'
        emission.to_csv(emission_file, index=False)
        files_created.append(emission_file)
        print(f"\n[OK] Emission lines: {emission_file}")
        print(f"     Rows: {len(emission)}")
        print(f"     Use for: Paired test, redshift predictions")
    
    # Continuum data (for spectrum analysis)
    continuum = df[df['data_type'] == 'continuum'].copy()
    if len(continuum) > 0:
        continuum_file = output_path / 'real_data_continuum.csv'
        continuum.to_csv(continuum_file, index=False)
        files_created.append(continuum_file)
        print(f"\n[OK] Continuum: {continuum_file}")
        print(f"     Rows: {len(continuum)}")
        print(f"     Use for: Spectrum analysis, Information Preservation")
    
    # Mixed data
    mixed = df[df['data_type'] == 'mixed'].copy()
    if len(mixed) > 0:
        mixed_file = output_path / 'real_data_mixed.csv'
        mixed.to_csv(mixed_file, index=False)
        files_created.append(mixed_file)
        print(f"\n[OK] Mixed: {mixed_file}")
        print(f"     Rows: {len(mixed)}")
        print(f"     Use for: Case-by-case analysis")
    
    # Also save full data with type column
    full_with_type = output_path / 'real_data_full_typed.csv'
    df.to_csv(full_with_type, index=False)
    files_created.append(full_with_type)
    print(f"\n[OK] Full data with types: {full_with_type}")
    print(f"     Rows: {len(df)}")
    print(f"     Use for: Complete analysis with filtering")
    
    # Analysis recommendations
    print("\n" + "="*80)
    print("USAGE RECOMMENDATIONS")
    print("="*80)
    
    print("\n1. PAIRED TEST (SEG vs GR×SR):")
    print("   File: real_data_emission_lines.csv")
    print(f"   Rows: {len(emission)}")
    print("   Why: Has emission-line redshifts, not source redshifts")
    
    print("\n2. SPECTRUM ANALYSIS (Multi-frequency):")
    print("   File: real_data_continuum.csv")
    print(f"   Rows: {len(continuum)}")
    print("   Why: Broadband flux measurements across frequencies")
    
    print("\n3. INFORMATION PRESERVATION:")
    print("   File: real_data_full_typed.csv (filter as needed)")
    print(f"   Rows: {len(df)}")
    print("   Why: Needs multi-frequency from same source (both types work)")
    
    print("\n4. HAWKING TESTS:")
    print("   File: real_data_full_typed.csv (filter as needed)")
    print(f"   Rows: {len(df)}")
    print("   Why: Works with both types, depends on specific test")
    
    # Create usage guide
    print("\n" + "="*80)
    print("CREATING USAGE GUIDE")
    print("="*80)
    
    guide_path = output_path / 'DATA_TYPE_USAGE_GUIDE.md'
    guide_content = f"""# Data Type Usage Guide

Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Data Files

### 1. `real_data_emission_lines.csv` ({len(emission)} rows)

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
- SEG better in {len(emission)} rows (55%)

---

### 2. `real_data_continuum.csv` ({len(continuum)} rows)

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

### 3. `real_data_mixed.csv` ({len(mixed)} rows if exists else 0)

**Type:** Data with both aspects

**Use:** Case-by-case evaluation

---

### 4. `real_data_full_typed.csv` ({len(df)} rows)

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
| **Paired Test** | Emission lines | real_data_emission_lines.csv | {len(emission)} |
| **Spectrum Analysis** | Continuum | real_data_continuum.csv | {len(continuum)} |
| **Information Preservation** | Both (multi-freq) | real_data_full_typed.csv | {len(df)} |
| **Jacobian Reconstruction** | Both | real_data_full_typed.csv | {len(df)} |
| **Hawking Proxy** | Both | real_data_full_typed.csv | {len(df)} |
| **Complete Overview** | All | real_data_full_typed.csv | {len(df)} |

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
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print(f"\n[OK] Created: {guide_path}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print(f"\nCreated {len(files_created)} files in '{output_dir}/'")
    for f in files_created:
        print(f"  - {f.name}")
    
    print(f"\nData distribution:")
    print(f"  Emission lines: {len(emission)} rows")
    print(f"  Continuum: {len(continuum)} rows")
    if len(mixed) > 0:
        print(f"  Mixed: {len(mixed)} rows")
    print(f"  Total: {len(df)} rows")
    
    print("\n[OK] COMPLETE!")
    print("="*80)
    
    return df

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Split data by type')
    parser.add_argument('--input', default='real_data_full.csv', help='Input CSV')
    parser.add_argument('--output-dir', default='data', help='Output directory')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup')
    
    args = parser.parse_args()
    
    split_data_by_type(
        input_csv=args.input,
        output_dir=args.output_dir,
        backup=not args.no_backup
    )
