# Sources.md

## Purpose

This document describes the origin of all S2/Sgr A\* data used in this repository, refers to primary literature, archives, and programmatic interfaces, and outlines the reproduction procedure.

## Data Provenance

The S2/Sgr A\* values used in the repo were initially scraped from the publications and archives linked below, processed locally, and stored as CSV files (e.g., `real_data_full.csv`). The scripts currently do not access a live API.

Acknowledgments: GRAVITY Collaboration (ESO), ESO Science Archive, Keck Observatory Archive, NIST Atomic Spectra Database, and CDS services (SIMBAD/VizieR).

---

## Primary Literature (S2/S0-2, Redshift)

* [https://www.aanda.org/articles/aa/full\_html/2018/07/aa33718-18/aa33718-18.html](https://www.aanda.org/articles/aa/full_html/2018/07/aa33718-18/aa33718-18.html)
* [https://www.aanda.org/articles/aa/pdf/2018/07/aa33718-18.pdf](https://www.aanda.org/articles/aa/pdf/2018/07/aa33718-18.pdf)
* [https://arxiv.org/abs/1807.09409](https://arxiv.org/abs/1807.09409)
* [https://www.science.org/doi/10.1126/science.aav8137](https://www.science.org/doi/10.1126/science.aav8137)
* [https://www.science.org/cms/asset/9b318de9-5652-4b20-9eab-f6eadab49e35/pap.pdf](https://www.science.org/cms/asset/9b318de9-5652-4b20-9eab-f6eadab49e35/pap.pdf)
* [https://arxiv.org/abs/1907.10731](https://arxiv.org/abs/1907.10731)
* (Program IDs & observation nights) [https://cds.cern.ch/record/2806198/files/2112.07478.pdf](https://cds.cern.ch/record/2806198/files/2112.07478.pdf)

## Line Physics (Brackett-γ as reference for f\_emit)

* [https://physics.nist.gov/PhysRefData/ASD/lines\_form.html](https://physics.nist.gov/PhysRefData/ASD/lines_form.html)
* [https://www.nist.gov/pml/atomic-spectra-database](https://www.nist.gov/pml/atomic-spectra-database)
* [https://www.gemini.edu/observing/resources/near-ir-resources/spectroscopy/hydrogen-recombination-lines](https://www.gemini.edu/observing/resources/near-ir-resources/spectroscopy/hydrogen-recombination-lines)

## ESO Archive & Programmatic Access

* [https://archive.eso.org/](https://archive.eso.org/)
* [https://archive.eso.org/scienceportal/](https://archive.eso.org/scienceportal/)
* [https://archive.eso.org/cms/eso-data/programmatic-access.html](https://archive.eso.org/cms/eso-data/programmatic-access.html)
* [https://archive.eso.org/tap\_obs/examples/](https://archive.eso.org/tap_obs/examples/)
* [http://archive.eso.org/tap\_obs](http://archive.eso.org/tap_obs)
* [http://archive.eso.org/tap\_cat](http://archive.eso.org/tap_cat)
* [https://archive.eso.org/cms/eso-data/eso-programme-identification-code.html](https://archive.eso.org/cms/eso-data/eso-programme-identification-code.html)
* [https://www.eso.org/sci/facilities/paranal/instruments/gravity.html](https://www.eso.org/sci/facilities/paranal/instruments/gravity.html)

## CDS / SIMBAD / VizieR

* [https://simbad.u-strasbg.fr/simbad/sim-fbasic](https://simbad.u-strasbg.fr/simbad/sim-fbasic)
* [https://simbad.unistra.fr/simbad/sim-tap](https://simbad.unistra.fr/simbad/sim-tap)
* [https://tapvizier.u-strasbg.fr/adql/](https://tapvizier.u-strasbg.fr/adql/)

## Keck Observatory Archive (KOA)

* [https://vmkoaweb.ipac.caltech.edu/UserGuide/index.html](https://vmkoaweb.ipac.caltech.edu/UserGuide/index.html)
* [https://www.ipac.caltech.edu/project/keck-archive](https://www.ipac.caltech.edu/project/keck-archive)
* [https://github.com/KeckObservatoryArchive/PyKOA/](https://github.com/KeckObservatoryArchive/PyKOA/)

## Project Repository

* [https://github.com/LinoCasu/Segmented-Spacetime-Mass-Projection-Unified-Results](https://github.com/LinoCasu/Segmented-Spacetime-Mass-Projection-Unified-Results)

---

## Reproducibility: Short Procedure

1. **Set reference line**
   Brackett-γ in vacuum: λ₀ ≈ 2.1661 µm ⇒ f\_emit = c / λ₀.

2. **Obtain time series (one of two options)**
   A) From publications/supplements: tables/plots of radial velocity (RV) and epochs from the works listed above.
   B) From archives: resolve object via SIMBAD (S2/S0-2). Query ESO/KOA for program IDs and instrument (GRAVITY, SINFONI, NIRC2, OSIRIS) and download spectra.

3. **Preprocessing**
   Determine Br-γ line center per epoch → f\_obs.
   Redshift: z = f\_emit / f\_obs − 1.
   Optional: subtract classical Kepler RV to isolate the relative GR term z\_rel.

4. **CSV storage (example schema)**
   `epoch, instrument, lambda0_um, f_emit_Hz, f_obs_Hz, z, source, notes`

## Notes

* Use vacuum wavelengths; differences from air wavelengths here are on the order of \~O(10^-3).
* For automated pipelines, `astroquery` (ESO/CDS) and `PyKOA` (Keck) are suitable. A later switch from “CSV-only” to “API fetch + caching” is planned.

---
Note on ALMA data access: Accessing ALMA data requires an authentication token, which means you must register an account. As of July 15, 2025, the access method has been switched from simple GET requests to a PROOF-based authentication system.

