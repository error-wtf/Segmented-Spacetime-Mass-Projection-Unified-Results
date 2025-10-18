# Segmented Spacetime Cosmology Suite

## Overview

This repository contains the Segmented Spacetime (SSZ) research suite, including the new cosmology pipeline that ingests Gaia data, constructs SSZ fields, embeds solar system segments, and generates interactive visualizations.

## Pipeline Summary

1. Fetch Gaia data using `scripts/gaia/fetch_gaia_adql.py` or cone search helper `scripts/gaia/fetch_gaia_conesearch.py`.
2. Preprocess outputs with `scripts/preprocess/gaia_clean_map.py` and `scripts/preprocess/gaia_frame_transform.py`.
3. Build cosmology field via `scripts/ssz/build_ssz_model.py` and solar embedding via `scripts/ssz/build_solar_system_model.py`.
4. Visualize with `scripts/viz/plot_ssz_maps.py` (cosmology) and `scripts/viz/plot_solar_ssz.py` (solar segments).
5. Run everything end-to-end with `run_gaia_ssz_pipeline.py`.

Outputs and manifests are stored under `experiments/<RUN_ID>/`, `models/cosmology/<RUN_ID>/`, and `models/solar_system/<RUN_ID>/`.
