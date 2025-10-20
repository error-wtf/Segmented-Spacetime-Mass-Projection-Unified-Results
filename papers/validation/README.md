# Validation Papers

This directory contains converted Markdown versions of scientific papers and observational data used to validate the SSZ Segmented Radiowave Propagation module.

## Contents

### G79.29+0.46 LBV Nebula Papers
- `Ammonia_observations_in_the_LBV_nebula_G7929046_Di.pdf.md` - NH₃ observations
- `Jiménez-Esteban_2010_ApJ_713_429_(1).pdf.md` - Multi-wavelength analysis
- `0804.0266v1.pdf.md` - Archival observations
- `stu296.pdf.md` - Stellar properties

### Cygnus X Diamond Ring Papers
- `The_Diamond_Ring_in_Cygnus_X_Advanced_stage_of_an_.pdf.md` - Diamond Ring structure
- `The_AKARI_diffuse_maps.pdf.md` - Diffuse emission mapping

### SSZ Theory Application
- `Segmented_Spacetime_and_the_Origin_of_Molecular_Zones_in_Expanding_Nebulae.docx.md` - SSZ framework application

### Observational Data Descriptions
- `G79_29+0_46_CO_NH3_rings.md` - G79 dataset description
- `CygnusX_DiamondRing_CII_rings.md` - Cygnus X dataset description
- `sources_observations.md` - Combined sources manifest

## Usage

These papers are referenced by the `config/sources.yaml` configuration and can be accessed programmatically:

```python
from SSZ.segwave import load_sources_config

config = load_sources_config()
print(config['base_dir'])  # Points to papers/validation/
```

## Citation

When using these datasets, please cite the original papers listed in `data/observations/sources.json`.

## License

Original papers remain under their respective publishers' copyrights. These Markdown conversions are for research purposes only.

---

**Copyright © 2025**  
Carmen Wrede und Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
