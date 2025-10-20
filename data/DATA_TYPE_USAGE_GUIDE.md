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
- SEG better in 73/143 rows (51%, p=0.867)
- **Stratified:** Photon sphere (r=2-3): 82% wins | Very close (r<2): 0% wins
- See STRATIFIED_PAIRED_TEST_RESULTS.md for details

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

**Why Continuum/Hubble Data Doesn't Work for Paired Test:**

**Physical Incompatibility:**
- z_obs (continuum) = Hubble flow redshift of entire source (M87: z=0.0042, d≈16.8 Mpc)
- z_pred (SEG) = Local gravitational redshift at emission radius (z~0.01-0.8 for r=10-1.5 r_s)
- These measure FUNDAMENTALLY DIFFERENT physics

**Concrete Example - M87:**
- Continuum z_obs = 0.0042 (galaxy receding at ~1,260 km/s due to Hubble expansion)
- SEG predicts: Local metric effects near M87* black hole (r ~ few r_s)
- Comparison: Testing planetary gravity (Earth-Moon distance) using galaxy cluster recession
- Problem: Not even measuring same type of redshift!

**Analogy:**
- Emission line test: "Does ball fall correctly under Earth's gravity?" (local)
- Hubble flow test: "Is the universe expanding?" (cosmological)
- SEG addresses: First question (local gravity)
- Hubble data answers: Second question (cosmology)
- Testing SEG with Hubble data: Using galaxy recession to test Newton's law of gravitation

**Mathematical Demonstration:**

For M87 continuum data:
```
z_obs (Hubble) = 0.0042
H₀ ≈ 70 km/s/Mpc
d = c·z/H₀ ≈ 16.8 Mpc (distance to M87)

SEG predicts local redshift at r:
z_local = (1 - 2GM/rc²)^(-1/2) - 1

For M87* (M ~ 6.5×10⁹ M_☉):
r = 3 r_s: z_local ≈ 0.15 (strong gravity)
r = 10 r_s: z_local ≈ 0.01 (weak field)

Problem: z_obs (0.0042) describes galaxy motion
         z_local describes spacetime curvature
         Cannot compare!
```

**Why This Matters:**
- Using Hubble data tests cosmology, not local gravity
- SEG is NOT a cosmological model
- SEG is a LOCAL spacetime geometry model
- Mixing scales invalidates physical interpretation

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

### Continuum Data (Hubble Flow):
- **z_obs meaning:** Source cosmological/recession redshift (ENTIRE galaxy/object)
- **Physical process:** Hubble expansion + peculiar velocity of source
- **Example:** M87 z_obs = 0.0042 (recession of entire galaxy at ~16.8 Mpc)
- **Prediction target:** NOT local emission redshift (completely different physics!)

**WHY HUBBLE FLOW DATA IS UNSUITABLE FOR SEG:**

1. **Different Physical Scale:**
   - Emission lines: Local process at specific radius (r ~ 1-100 r_s from black hole)
   - Hubble flow: Global recession of entire galaxy/source (distances ~ Mpc)
   - SEG models: Local spacetime curvature around compact object
   - Hubble expansion: Cosmological effect on Gpc scales

2. **Different Physical Mechanism:**
   - Emission redshift: z = (1-2GM/rc²)^(-1/2) - 1 (gravitational time dilation)
   - Hubble redshift: z = H₀·d/c (expansion of space itself)
   - SEG predicts: φ-corrected local metric effects
   - Hubble describes: Universal expansion (not modeled by SEG)

3. **Incompatible Predictions:**
   - SEG z_pred: Computed from local metric at emission radius
   - Continuum z_obs: Cosmological redshift of host galaxy
   - Comparison: Like comparing planetary orbit (km) to galaxy distance (Mpc)
   - Result: Physically meaningless to test local gravity theory with cosmological data

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

## Summary: Why Hubble/Cosmological Data is Fundamentally Unsuitable

**The Core Problem:**
SEG is a **local spacetime geometry theory** that predicts gravitational effects within ~100 r_s of compact objects. Hubble flow data measures **cosmological expansion** over Mpc-Gpc scales. These are as incompatible as testing chemistry with astronomical data.

**What Each Data Type Measures:**

| Aspect | Emission Lines (✅ Compatible) | Continuum/Hubble (❌ Incompatible) |
|--------|--------------------------------|-------------------------------------|
| **Physical Effect** | Local gravitational time dilation | Cosmological redshift (space expansion) |
| **Scale** | r ~ 1-100 r_s (km to AU) | d ~ Mpc to Gpc (10¹⁹-10²² km) |
| **Formula** | z ~ GM/rc² (local metric) | z ~ H₀d/c (Hubble law) |
| **SEG Models This?** | ✅ YES (core prediction) | ❌ NO (not a cosmology model) |
| **Example Value** | z ~ 10⁻⁴ to 1 (S2, pulsars) | z ~ 0.001 to 10 (distant galaxies) |
| **Physics Type** | Strong-field gravity | Universe expansion |

**Critical Understanding:**
- **Emission lines:** Test "Does spacetime curve correctly near this black hole?"
- **Hubble data:** Test "Is the universe expanding?"
- **SEG answers:** First question (local gravity)
- **SEG does NOT answer:** Second question (cosmology)

**Using Hubble data to test SEG is equivalent to:**
- Using galaxy redshift to test Newton's F=ma
- Using CMB temperature to test Maxwell's equations
- Using planetary motion to test quantum mechanics

**All valid data, all testing wrong phenomena!**

**Proper Use:**
- ✅ Emission lines → Test local gravity (SEG domain)
- ✅ Continuum spectra → Information preservation, Hawking radiation analogs
- ❌ Hubble flow → Cosmology (NOT SEG domain)
- ❌ LIGO strain data → Gravitational waves (different physics, see below)

---

## Data Source Evaluation: Why We Don't Use LIGO Gravitational Wave Data

**Initial Consideration (Early 2025):**

Before settling on emission-line and continuum datasets, we evaluated multiple potential data sources, including **LIGO gravitational wave strain data**. While LIGO provides Nobel Prize-winning measurements of spacetime ripples, we found this data **unsuitable for SEG redshift testing** for fundamental scientific and practical reasons.

### LIGO Data: What It Measures

**LIGO detects:**
- Gravitational wave strain: h(t) - tiny distortions in spacetime
- Binary inspiral/merger events (black holes, neutron stars)
- Time-series of strain amplitude vs time
- Frequency evolution during merger (chirp)

**Physical phenomenon:**
- Spacetime ripples propagating at speed of light
- Dynamic geometry changes (not static metric)
- Wave amplitude typically h ~ 10⁻²¹ (incredibly small)

### Why LIGO Data is Unsuitable for SEG Testing

**1. Fundamentally Different Physics:**

| Aspect | LIGO Measures | SEG Models |
|--------|---------------|------------|
| **Phenomenon** | Gravitational waves (dynamic) | Static/quasi-static spacetime geometry |
| **Observable** | Strain h(t) time-series | Redshift z from static metric |
| **Time Dependence** | Highly dynamic (milliseconds) | Static or slowly varying (orbits) |
| **Physics Type** | Wave propagation | Local curvature/time dilation |

- **SEG predicts:** Static metric corrections → gravitational redshift z
- **LIGO measures:** Dynamic strain h(t) → gravitational wave amplitude
- **Comparison:** Completely different observables!

**Analogy:** Using ocean wave heights to test predictions about water pressure at depth
- Both related to water
- Both valid physics
- Completely different phenomena

**2. Data Format Incompatibility:**

**LIGO provides:**
```
Data: h(t) strain time-series with timestamps
Format: Time → Strain amplitude
Example: GW150914 - merger signal ~0.2 seconds
```

**SEG predicts:**
```
Redshift: z = (observable - emitted) / emitted
Format: Spectral shift (dimensionless)
Example: S2 star z ~ 2.34×10⁻⁴ from orbit
```

**Problem:** 
- Cannot directly compare strain amplitude h(t) to redshift z
- Would require extensive conversion/interpretation
- Conversion assumptions would dominate uncertainty
- Result would test conversion procedure, not SEG

**3. Preprocessing Transparency Concerns:**

**LIGO Data Pipeline:**
- Raw detector output → Multiple preprocessing stages → Published strain h(t)
- Includes: Noise subtraction, glitch removal, calibration, filtering
- Preprocessing details: Partially documented but complex
- Full pipeline: Not completely transparent to external researchers

**Our Requirements:**
- ✅ Raw or minimally processed data
- ✅ Fully transparent measurement procedures
- ✅ Independently verifiable
- ✅ Clear uncertainty quantification

**LIGO strain data:**
- ❌ Heavily preprocessed (necessary for detection, but reduces transparency)
- ❌ Preprocessing pipeline complex and evolving
- ❌ Difficult to independently verify without full pipeline access
- ⚠️ Not a criticism of LIGO science (preprocessing is ESSENTIAL for GW detection)
- ⚠️ Simply doesn't meet OUR transparency requirements for THIS test

**4. Observable Mismatch:**

**What we need to test SEG:**
- Direct spectroscopic measurements (wavelengths, frequencies)
- Gravitational redshift from static/quasi-static fields
- Clear comparison: z_obs vs z_pred
- Regime stratification by r/r_s

**What LIGO provides:**
- Gravitational wave strain from dynamic events
- Merger/inspiral dynamics (not static geometry)
- Frequency evolution (chirp), not redshift
- Event-based (not regime-stratified)

**These don't align!**

**5. Scientific Focus Mismatch:**

**LIGO Science:**
- Binary inspiral/merger dynamics
- Gravitational wave propagation
- Strong-field dynamics (velocities ~ c)
- Transient events (milliseconds to seconds)

**SEG Science:**
- Static spacetime geometry
- Local gravitational redshift
- Static/quasi-static field (orbits, emission)
- Stable configurations (hours to years)

**Overlap:** Both involve strong gravity, but different aspects

### Our Data Choice: Emission Lines + Continuum Spectra

**Instead, we chose:**

**Emission Lines (NED, SIMBAD, Literature):**
- ✅ Direct spectroscopic measurements
- ✅ Transparent: wavelength → redshift (simple calculation)
- ✅ Independently verifiable (published spectra)
- ✅ Tests local gravitational redshift (SEG domain)
- ✅ Well-documented uncertainties
- ✅ Covers multiple physical regimes (r/r_s stratification)

**Continuum Spectra (NED):**
- ✅ Multi-frequency flux measurements
- ✅ For information preservation tests (different analysis)
- ✅ Direct from database (minimal processing)
- ✅ Transparently documented

**Key Advantages:**
1. **Simplicity:** Wavelength shift → redshift (basic calculation)
2. **Transparency:** Measurement procedure clear and verifiable
3. **Compatibility:** Directly tests what SEG predicts (z from static metric)
4. **Stratification:** Can organize by physical regime (r/r_s)
5. **Uncertainty:** Clear error bars on measurements

### Summary: Data Source Selection Rationale

**Evaluated:**
- ✅ Emission-line spectroscopy (NED, SIMBAD) → **CHOSEN** (local gravity)
- ✅ Continuum spectra (NED) → **CHOSEN** (information tests)
- ❌ LIGO strain data → **REJECTED** (different physics, format, preprocessing)
- ❌ Hubble/cosmological redshift → **REJECTED** (cosmology, not local gravity)

**Selection Criteria:**
1. Measures local gravitational effects (not cosmology, not dynamics)
2. Transparent, verifiable measurements
3. Directly comparable to SEG predictions
4. Allows regime stratification (r/r_s)
5. Well-documented uncertainties

**LIGO data fails criteria #1, #2, #3, #4** - not because LIGO is bad science, but because it measures different physics than what SEG models!

**Result:** 
- 143 emission-line observations for paired redshift test
- 284 continuum frequencies for information preservation
- Clear physical interpretation
- Transparent methodology
- Reproducible analysis

**Note:** This is NOT a criticism of LIGO's scientific achievements (which are extraordinary). LIGO data is perfect for gravitational wave astronomy. It's simply the wrong data type for testing a static metric prediction model like SEG.

---

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
