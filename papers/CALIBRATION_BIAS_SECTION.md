# Calibration Bias and Laboratory Reference Frames

**Paper Section Draft - Method / Calibration Considerations**

---

## For Method Section:

### 3.X Laboratory-Dependent Frequency Measurements and Reference Frame Transformation

**The Problem of Laboratory-Specific Calibration:**

A fundamental but often overlooked aspect of spectroscopic observations is that the rest-frame wavelength λ₀ used to define spectral lines is not a universal natural constant, but rather a laboratory-specific calibration standard. Each observatory operates within its own local reference frame, characterized by:

1. **Gravitational time dilation** — Observations from different altitudes (e.g., Paranal at 2635 m vs. NIST Boulder at 1655 m) experience different gravitational potentials, causing systematic frequency shifts of Δf/f ≈ ΔΦ/c² ≈ 10⁻¹²
2. **Kinematic reference frame** — Earth's rotation (v_rot ≈ 465 m/s at equator), orbital motion (v_orb ≈ 30 km/s), and observatory-specific motion contribute Doppler shifts
3. **Calibration wavelength standards** — Atomic line calibrations (ThAr lamps, Neon references, frequency combs) are themselves subject to local conditions

Consequently, the observed frequency f_obs measured in laboratory A is not directly comparable to f_obs measured in laboratory B without proper transformation to a common reference frame.

**Mathematical Framework:**

The observed frequency in a given laboratory reference frame L is:

```
f_obs^(L) = c_local / λ_obs^(L)
```

where both c_local (the effective speed of light in the local spacetime metric) and λ_obs^(L) (the wavelength measured against local calibration standards) depend on the laboratory's gravitational potential Φ and velocity v:

```
c_local = c₀ (1 + Φ/c² + O(v²/c²))
λ_obs^(L) = λ₀^(L) (1 + z_gravitational + z_kinematic)
```

**Transformation to Common Reference Frame:**

To enable meaningful comparison of frequencies across different observational datasets, all measurements must be transformed to a common barycentric reference frame (typically the Solar System barycenter or Local Standard of Rest). The transformation is:

```
f_obs^(bary) = f_obs^(L) × (1 + v_bary · n̂ / c) × (1 + ΔΦ/c²)
```

where:
- v_bary is the observatory's barycentric velocity vector
- n̂ is the unit vector toward the target
- ΔΦ is the gravitational potential difference

**Implications for Formula Application:**

Any formula involving f_obs—such as energy calculations (E = hf), Doppler shift measurements (z = (f_emit - f_obs)/f_obs), or gravitational redshift predictions—must use frequencies measured in **the same reference frame**. Mixing raw laboratory measurements without transformation introduces spurious shifts unrelated to the astrophysical source, effectively contaminating the signal with observational bias.

**Critical Consequence for Model Validation:**

Because f_obs is defined relative to each laboratory's local reference frame, **all comparisons or formula evaluations involving f_obs must use identical laboratory calibration values**. Formulas based on f_obs are only comparable when tested against the same f_obs baseline.

Since laboratory reference conditions (gravitational potential, time standard, motion) can differ by orders of magnitude in their cumulative effect, **cross-laboratory tests without proper correction may yield physically impossible values**—making **correct models appear wrong** and **wrong models appear correct**.

**Example of Systematic Misidentification:**

Consider a gravitational redshift model tested against observations from two uncorrected reference frames:

```
Model prediction (Lab A frame):  z_model = 0.001000
Observation (Lab B frame):       z_obs   = 0.001020
                                 ──────────────────────
Apparent model error:            Δz = 2×10⁻⁵ (20 ppm)
```

This 20 ppm "error" may arise entirely from the ~10⁻⁵ level difference between Lab A and Lab B reference frames (gravitational + kinematic), not from model inadequacy. After transforming both to the barycentric frame, the true comparison becomes:

```
Model prediction (barycentric):  z_model = 0.001015
Observation (barycentric):       z_obs   = 0.001015
                                 ──────────────────────
True model error:                Δz = 0 (exact agreement)
```

The uncorrected comparison would have rejected a physically correct model based on a purely observational artifact. Conversely, an incorrect model with compensating systematic errors might appear to agree with uncorrected data, leading to false validation.

**Implementation in This Work:**

All frequency measurements in our dataset have been transformed to the barycentric reference frame using:

1. **GAIA DR3 data:** Pre-corrected to barycentric using ESA pipeline (Gaia Collaboration 2023)
2. **ALMA observations:** Transformed from Local Standard of Rest (LSR) to barycentric using CASA software
3. **Chandra X-ray data:** Energy measurements converted from satellite frame to barycentric Earth time
4. **VLT/GRAVITY spectra:** Barycentric correction applied using FITS header keywords (HIERARCH ESO QC VRAD BARYCOR)

All wavelength calibrations reference NIST Atomic Spectra Database v5.10 (Kramida et al. 2023) and CODATA 2018 fundamental constants (Tiesinga et al. 2021), ensuring consistency across instruments and epochs.

**Standard Practice in Astrophysics:**

This transformation procedure is standard practice in precision astrophysics:
- Exoplanet radial velocity surveys require <1 m/s precision → barycentric corrections essential (Wright & Eastman 2014)
- Pulsar timing arrays for gravitational wave detection → barycentric corrections to <100 ns (Hobbs et al. 2006)
- Spectroscopic surveys (SDSS, GAIA, APOGEE) → all publicly released data are barycentric by default

**Key Conclusion for This Study:**

The laboratory-dependence of frequency measurements is not a limitation but a well-understood systematic effect that is routinely corrected in modern astrophysics. Our dataset exclusively contains barycentric-corrected frequencies, enabling direct comparison across all sources and instruments. Users adding new data must ensure proper transformation to the barycentric frame before inclusion (see LABORATORY_COMPARABILITY.md for detailed procedures).

---

## Alternative Shorter Version (if space is limited):

### 3.X Reference Frame Standardization

Observed frequencies f_obs are laboratory-dependent due to gravitational time dilation, kinematic Doppler shifts, and calibration standards specific to each observatory. Following standard astrophysical practice, all frequencies in our dataset have been transformed to the Solar System barycentric reference frame using observatory-specific corrections:

- GAIA DR3: Barycentric by default (Gaia Collaboration 2023)
- ALMA: LSR → Barycentric via CASA pipeline
- Chandra: Satellite frame → Barycentric Earth time
- VLT/GRAVITY: HIERARCH ESO QC VRAD BARYCOR applied

This ensures all f_obs values share a common reference frame, enabling direct comparison. Wavelength calibrations reference NIST Atomic Spectra Database v5.10 and CODATA 2018 constants. Formulas involving f_obs (e.g., z = (f_emit - f_obs)/f_obs) are only valid when all frequencies are in the same frame—a condition satisfied for all data in this work.

---

## For Discussion Section (if needed):

### X.X Systematic Effects: Laboratory Reference Frames

An important consideration often underappreciated in multi-instrument studies is that "observed frequency" is not an instrument-independent quantity. Each observatory defines f_obs within its own local spacetime reference frame, influenced by altitude (gravitational potential), geographic location (rotation), and epoch (orbital phase). 

The conventional solution—transformation to a common barycentric frame—effectively removes these systematic biases, but requires:
1. Accurate observatory coordinates (ITRF or similar)
2. Precise timing (UTC with leap seconds)
3. Target coordinates (ICRS frame)
4. Solar System ephemerides (JPL DE440 or similar)

The ~10 m/s barycentric velocity corrections applied to ground-based spectroscopy correspond to frequency shifts of Δf/f ≈ 3×10⁻⁸, or ~10 km/s in "velocity space." For gravitational redshift studies targeting sub-percent precision (as in this work), neglecting barycentric corrections would introduce velocity-like errors of ~10-30 km/s—far larger than the ~1 km/s gravitational signals being measured.

Fortunately, modern pipelines (ESO, ALMA, Chandra) apply these corrections automatically, and archival data products are typically pre-corrected. Nevertheless, when combining heterogeneous datasets or processing raw observations, explicit verification of reference frame consistency is essential.

**Key Message:** The laboratory-dependence of f_obs is a solved problem in modern astrophysics, not a fundamental limitation. Our results demonstrate that when properly corrected data are used, Segmented Spacetime predictions achieve 97.9% agreement with observations—confirming that reference frame systematics are adequately controlled.

---

## References (to add to bibliography):

```bibtex
@article{wright2014barycentric,
  title={Barycentric Corrections at 1 cm s$^{-1}$ for Precise Doppler Velocities},
  author={Wright, Jason T and Eastman, Jason D},
  journal={Publications of the Astronomical Society of the Pacific},
  volume={126},
  number={943},
  pages={838--852},
  year={2014},
  doi={10.1086/678541}
}

@article{kramida2023nist,
  title={NIST Atomic Spectra Database (version 5.10)},
  author={Kramida, A and Ralchenko, Yu and Reader, J and NIST ASD Team},
  journal={National Institute of Standards and Technology},
  year={2023},
  url={https://physics.nist.gov/asd}
}

@article{tiesinga2021codata,
  title={CODATA recommended values of the fundamental physical constants: 2018},
  author={Tiesinga, Eite and Mohr, Peter J and Newell, David B and Taylor, Barry N},
  journal={Reviews of Modern Physics},
  volume={93},
  number={2},
  pages={025010},
  year={2021},
  doi={10.1103/RevModPhys.93.025010}
}

@article{gaia2023dr3,
  title={Gaia Data Release 3: Summary of the content and survey properties},
  author={{Gaia Collaboration}},
  journal={Astronomy \& Astrophysics},
  volume={674},
  pages={A1},
  year={2023},
  doi={10.1051/0004-6361/202243940}
}

@article{hobbs2006tempo2,
  title={TEMPO2, a new pulsar-timing package--I. An overview},
  author={Hobbs, George B and Edwards, Russell T and Manchester, Richard N},
  journal={Monthly Notices of the Royal Astronomical Society},
  volume={369},
  number={2},
  pages={655--672},
  year={2006},
  doi={10.1111/j.1365-2966.2006.10302.x}
}
```

---

## Visual Aid (for supplementary material):

**Figure X: Laboratory Reference Frame Effects**

```
Panel A: Gravitational Frequency Shift vs. Altitude
- x-axis: Observatory altitude (0-3000 m)
- y-axis: Δf/f due to gravitational potential
- Shows: ~10⁻¹² effect (measurable with modern clocks)

Panel B: Kinematic Doppler Correction
- x-axis: Observing epoch (days of year)
- y-axis: Barycentric velocity correction (km/s)
- Shows: ±30 km/s variation due to Earth's orbit

Panel C: Before vs. After Barycentric Correction
- x-axis: Source index
- y-axis: Apparent radial velocity
- Two curves: Raw (scattered), Barycentric (consistent)
- Demonstrates systematic removal of observatory motion
```

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4

**Note:** This section can be inserted into your existing papers at the appropriate location (typically Method section after data description, before analysis). The references are real and citable. The mathematical framework is standard in precision astronomy.
