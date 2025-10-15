#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Test Data for Segmented Spacetime Model
================================================

Creates a synthetic dataset with proper M_solar, r_emit_m columns
based on known astrophysical objects and scaling relationships.

No external dependencies required - pure Python + CSV.
"""

import csv
import math
import random

# Physical constants
C = 299_792_458.0  # m/s
M_SUN = 1.98847e30  # kg
G = 6.67430e-11    # m^3 kg^-1 s^-2
HALPHA_HZ = C / 656.281e-9  # H-alpha frequency

# Known astrophysical objects with realistic parameters
TEMPLATE_OBJECTS = [
    # Compact objects (high precision expected)
    {"name": "Sgr_A*_S2", "category": "S-star", "M_solar": 4.297e6, "r_base": 1.5e14, "z_base": 0.0007, "v_scale": 1e6},
    {"name": "Sgr_A*_S29", "category": "S-star", "M_solar": 4.297e6, "r_base": 5.2e14, "z_base": 0.0001, "v_scale": 5e5},
    {"name": "M87_jet", "category": "jet", "M_solar": 6.5e9, "r_base": 1e15, "z_base": 0.004, "v_scale": 1e8},
    {"name": "Cygnus_X1", "category": "bh-binary", "M_solar": 21, "r_base": 1e8, "z_base": 0.00001, "v_scale": 1e7},
    
    # Quasars (moderate precision expected)  
    {"name": "3C273", "category": "quasar", "M_solar": 8.8e8, "r_base": 1e16, "z_base": 0.158, "v_scale": 5e6},
    {"name": "3C279", "category": "quasar", "M_solar": 3e8, "r_base": 8e15, "z_base": 0.536, "v_scale": 8e6},
    {"name": "PKS_1510", "category": "blazar", "M_solar": 1e9, "r_base": 2e16, "z_base": 0.361, "v_scale": 1e7},
    
    # Pulsars (high precision expected)
    {"name": "PSR_B1913+16", "category": "pulsar", "M_solar": 1.44, "r_base": 1e4, "z_base": 0.00001, "v_scale": 1e5},
    {"name": "PSR_J0737", "category": "pulsar", "M_solar": 1.34, "r_base": 1.2e4, "z_base": 0.00002, "v_scale": 2e5},
    
    # Galaxies (lower precision expected)
    {"name": "M31_core", "category": "galaxy", "M_solar": 1.4e8, "r_base": 1e18, "z_base": -0.001, "v_scale": 3e5},
    {"name": "NGC_4258", "category": "galaxy", "M_solar": 3.9e7, "r_base": 5e17, "z_base": 0.0015, "v_scale": 4e5},
]

def generate_variants(template, num_variants=5):
    """Generate multiple variants of a template object with realistic parameter variations."""
    variants = []
    
    for i in range(num_variants):
        # Add realistic variations
        mass_factor = 0.5 + random.random() * 1.0  # ±50% mass variation
        radius_factor = 0.3 + random.random() * 1.4  # ±70% radius variation  
        z_factor = 0.1 + random.random() * 1.8  # ±90% redshift variation
        v_factor = 0.2 + random.random() * 1.6  # ±80% velocity variation
        
        M_solar = template["M_solar"] * mass_factor
        r_emit_m = template["r_base"] * radius_factor
        z = abs(template["z_base"] * z_factor)  # Keep positive
        v_tot = template["v_scale"] * v_factor
        v_los = v_tot * (0.1 + 0.8 * random.random())  # 10-90% line-of-sight
        
        # Calculate frequencies from redshift
        f_emit_Hz = HALPHA_HZ
        f_obs_Hz = f_emit_Hz / (1.0 + z) if z > 0 else f_emit_Hz
        
        # Generate coordinates
        ra_deg = random.uniform(0, 360)
        dec_deg = random.uniform(-90, 90)
        
        variant = {
            "case": f"{template['name']}_var{i+1}",
            "category": template["category"],
            "M_solar": M_solar,
            "r_emit_m": r_emit_m,
            "z": z,
            "f_emit_Hz": f_emit_Hz,
            "f_obs_Hz": f_obs_Hz,
            "ra_deg": ra_deg,
            "dec_deg": dec_deg,
            "v_tot_mps": v_tot,
            "v_los_mps": v_los,
            "z_geom_hint": None,
            "notes": f"Synthetic variant of {template['name']}"
        }
        variants.append(variant)
    
    return variants

def main():
    random.seed(42)  # Reproducible results
    
    all_objects = []
    
    # Generate variants for each template
    for template in TEMPLATE_OBJECTS:
        variants = generate_variants(template, num_variants=8)
        all_objects.extend(variants)
    
    # Add some extreme cases for testing
    extreme_cases = [
        {
            "case": "Extreme_BH", "category": "extreme", "M_solar": 1e10, "r_emit_m": 1e17,
            "z": 2.5, "f_emit_Hz": HALPHA_HZ, "f_obs_Hz": HALPHA_HZ/3.5,
            "ra_deg": 180, "dec_deg": 0, "v_tot_mps": 5e7, "v_los_mps": 2e7,
            "z_geom_hint": None, "notes": "Extreme high-z test case"
        },
        {
            "case": "Nearby_NS", "category": "neutron-star", "M_solar": 1.97, "r_emit_m": 1e4,
            "z": 0.000001, "f_emit_Hz": HALPHA_HZ, "f_obs_Hz": HALPHA_HZ*0.999999,
            "ra_deg": 45, "dec_deg": 30, "v_tot_mps": 1e4, "v_los_mps": 5e3,
            "z_geom_hint": None, "notes": "Nearby neutron star"
        }
    ]
    all_objects.extend(extreme_cases)
    
    # Write to CSV
    output_file = "real_data_synthetic.csv"
    fieldnames = ["case", "category", "M_solar", "r_emit_m", "z", "f_emit_Hz", "f_obs_Hz", 
                  "ra_deg", "dec_deg", "v_tot_mps", "v_los_mps", "z_geom_hint", "notes"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_objects)
    
    print(f"[OK] Generated {len(all_objects)} synthetic objects")
    print(f"[INFO] Saved to {output_file}")
    print(f"[INFO] Object categories: {set(obj['category'] for obj in all_objects)}")
    print(f"[INFO] Mass range: {min(obj['M_solar'] for obj in all_objects):.2e} - {max(obj['M_solar'] for obj in all_objects):.2e} M_sun")
    print(f"[INFO] Redshift range: {min(obj['z'] for obj in all_objects):.6f} - {max(obj['z'] for obj in all_objects):.3f}")
    print(f"[READY] Use with: python segspace_all_in_one_extended.py eval-redshift --csv {output_file} --prefer-z --paired-stats")

if __name__ == "__main__":
    main()
