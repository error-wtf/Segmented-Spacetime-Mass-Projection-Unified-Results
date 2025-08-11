# Sources.md

## Zweck
Dieses Dokument beschreibt die Herkunft aller in diesem Repository verwendeten S2/Sgr A*-Daten, verweist auf Primärliteratur, Archive und Programmierschnittstellen und skizziert das Reproduktions-Vorgehen.

## Datenherkunft (Provenance)
Die im Repo genutzten S2/Sgr A*-Werte wurden zunächst aus den unten verlinkten Publikationen und Archiven gescraped, lokal aufbereitet und als CSV abgelegt (z. B. `real_data_full.csv`). Die Skripte greifen derzeit nicht auf eine Live-API zu.

Dank an: GRAVITY Collaboration (ESO), ESO Science Archive, Keck Observatory Archive, NIST Atomic Spectra Database sowie CDS-Dienste (SIMBAD/VizieR).

---

## Primärliteratur (S2/S0-2, Rotverschiebung)
- https://www.aanda.org/articles/aa/full_html/2018/07/aa33718-18/aa33718-18.html
- https://www.aanda.org/articles/aa/pdf/2018/07/aa33718-18.pdf
- https://arxiv.org/abs/1807.09409
- https://www.science.org/doi/10.1126/science.aav8137
- https://www.science.org/cms/asset/9b318de9-5652-4b20-9eab-f6eadab49e35/pap.pdf
- https://arxiv.org/abs/1907.10731
- (Programm-IDs & Beobachtungsnächte) https://cds.cern.ch/record/2806198/files/2112.07478.pdf

## Linienphysik (Brackett-γ als Referenz für f_emit)
- https://physics.nist.gov/PhysRefData/ASD/lines_form.html
- https://www.nist.gov/pml/atomic-spectra-database
- https://www.gemini.edu/observing/resources/near-ir-resources/spectroscopy/hydrogen-recombination-lines

## ESO Archive & Programmatic Access
- https://archive.eso.org/
- https://archive.eso.org/scienceportal/
- https://archive.eso.org/cms/eso-data/programmatic-access.html
- https://archive.eso.org/tap_obs/examples/
- http://archive.eso.org/tap_obs
- http://archive.eso.org/tap_cat
- https://archive.eso.org/cms/eso-data/eso-programme-identification-code.html
- https://www.eso.org/sci/facilities/paranal/instruments/gravity.html

## CDS / SIMBAD / VizieR
- https://simbad.u-strasbg.fr/simbad/sim-fbasic
- https://simbad.unistra.fr/simbad/sim-tap
- https://tapvizier.u-strasbg.fr/adql/

## Keck Observatory Archive (KOA)
- https://vmkoaweb.ipac.caltech.edu/UserGuide/index.html
- https://www.ipac.caltech.edu/project/keck-archive
- https://github.com/KeckObservatoryArchive/PyKOA/

## Projekt-Repository
- https://github.com/LinoCasu/Segmented-Spacetime-Mass-Projection-Unified-Results

---

## Reproduzierbarkeit: Kurzablauf

1) Referenzlinie setzen  
Brackett-γ im Vakuum: λ0 ≈ 2.1661 µm ⇒ f_emit = c / λ0.

2) Zeitreihen beschaffen (eine von zwei Optionen)  
A) Aus Publikationen/Supplements: Tabellen/Plots der Radialgeschwindigkeit (RV) und Epochen aus den oben gelisteten Arbeiten.  
B) Aus Archiven: Objektauflösung via SIMBAD (S2/S0-2). ESO/KOA nach Programm-IDs und Instrument (GRAVITY, SINFONI, NIRC2, OSIRIS) abfragen und Spektren herunterladen.

3) Vorverarbeitung  
Linienzentrum Br-γ pro Epoche bestimmen → f_obs.  
Rotverschiebung: z = f_emit / f_obs − 1.  
Optional: klassische Kepler-RV subtrahieren, um den relativen GR-Zusatz z_rel zu isolieren.

4) CSV-Ablage (Schema-Beispiel)
epoch, instrument, lambda0_um, f_emit_Hz, f_obs_Hz, z, source, notes

## Hinweise
- Vakuum-Wellenlängen verwenden; Unterschiede zur Luft-Wellenlänge liegen hier bei ~O(10^-3).
- Für automatisierte Pipelines eignen sich `astroquery` (ESO/CDS) und `PyKOA` (Keck). Eine spätere Umstellung von „CSV-only“ auf „API-Fetch + Caching“ ist vorgesehen.
