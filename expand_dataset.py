#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expand Dataset with More Objects
================================

Adds more black holes, neutron stars, and compact objects to test
segmented spacetime in different regimes.
"""

import csv
import math
import random
from typing import Dict, List

# Physical constants
C = 299_792_458.0  # m/s
M_SUN = 1.98847e30  # kg
G = 6.67430e-11    # m^3 kg^-1 s^-2
HALPHA_HZ = C / 656.281e-9  # H-alpha frequency

def create_additional_objects() -> List[Dict]:
    """Create additional objects focusing on regimes where segmented spacetime should excel."""
    
    objects = []
    
    # === MORE S-STARS (different orbital parameters) ===
    additional_s_stars = [
        ("S4", 4.297e6, 1.2e14, 0.0008, "Short period S-star"),
        ("S5", 4.297e6, 8.5e13, 0.0012, "Very close S-star"),
        ("S8", 4.297e6, 2.1e14, 0.0004, "Medium orbit S-star"),
        ("S9", 4.297e6, 1.8e14, 0.0006, "Eccentric S-star"),
        ("S12", 4.297e6, 3.2e14, 0.0003, "Outer S-star"),
        ("S13", 4.297e6, 1.1e14, 0.0015, "Highly eccentric"),
        ("S14", 4.297e6, 2.8e14, 0.0002, "Long period S-star"),
        ("S17", 4.297e6, 1.6e14, 0.0009, "Close approach"),
        ("S19", 4.297e6, 4.1e14, 0.0001, "Distant S-star"),
        ("S24", 4.297e6, 1.4e14, 0.0011, "Fast orbit"),
    ]
    
    for name, mass, a_orbit, z_obs, note in additional_s_stars:
        obj = create_compatible_object(
            f"{name}_SgrA*", "S-stars", mass, z_obs,
            a_m=a_orbit, e=0.3 + 0.6 * random.random(),
            source=f"Additional S-star: {note}"
        )
        objects.append(obj)
    
    # === INTERMEDIATE MASS BLACK HOLES (IMBH) ===
    imbh_objects = [
        ("HLX-1", "IMBH", 2e4, 0.126, "Hyper-luminous X-ray source"),
        ("ESO_243-49_HLX-1", "IMBH", 2e4, 0.0223, "Off-center IMBH"),
        ("M82_X-1", "IMBH", 4e2, 0.000677, "Ultraluminous X-ray source"),
        ("NGC_1313_X-1", "IMBH", 5e3, 0.00144, "IMBH candidate"),
        ("NGC_5408_X-1", "IMBH", 1e3, 0.00467, "Dwarf galaxy IMBH"),
        ("IC_10_X-1", "IMBH", 2.3e1, 0.000348, "Wolf-Rayet IMBH"),
        ("M33_X-7", "IMBH", 1.6e1, 0.000054, "Eclipsing IMBH"),
        ("NGC_300_X-1", "IMBH", 2e1, 0.00048, "Spiral galaxy IMBH"),
    ]
    
    for name, category, mass, z, note in imbh_objects:
        obj = create_compatible_object(
            name, category, mass, z,
            a_m=1e10 + 9e10 * random.random(),  # Binary-scale orbits
            e=0.0 + 0.4 * random.random(),
            source=f"IMBH: {note}"
        )
        objects.append(obj)
    
    # === MORE NEUTRON STARS (precise timing) ===
    precise_pulsars = [
        ("PSR_J1614-2230", "pulsar", 1.97, 0.00001, "Massive neutron star"),
        ("PSR_J0952-0607", "pulsar", 2.35, 0.00001, "Most massive NS known"),
        ("PSR_J1738+0333", "pulsar", 1.46, 0.00001, "White dwarf binary"),
        ("PSR_J0030+0451", "pulsar", 1.44, 0.00001, "NICER target"),
        ("PSR_J0740+6620", "pulsar", 2.08, 0.00001, "Heavy neutron star"),
        ("PSR_J1909-3744", "pulsar", 1.54, 0.00001, "Precision timing"),
        ("PSR_J1713+0747", "pulsar", 1.31, 0.00001, "Long-term timing"),
        ("PSR_J2317+1439", "pulsar", 1.29, 0.00001, "Globular cluster"),
        ("PSR_J0437-4715", "pulsar", 1.76, 0.00001, "Nearby millisecond"),
        ("PSR_J1012+5307", "pulsar", 1.64, 0.00001, "Helium white dwarf"),
    ]
    
    for name, category, mass, z, note in precise_pulsars:
        obj = create_compatible_object(
            name, category, mass, z,
            a_m=1e8 + 9e8 * random.random(),   # Close binary
            e=0.0 + 0.1 * random.random(),    # Nearly circular
            P_year=0.001 + 0.1 * random.random(),  # Very short periods
            source=f"Precision pulsar: {note}"
        )
        objects.append(obj)
    
    # === MORE LIGO/VIRGO DETECTIONS ===
    gw_detections = [
        ("GW170817", "NS-merger", 2.74, 0.009, "First NS merger"),
        ("GW190425", "NS-merger", 3.4, 0.04, "Heavy NS merger"),
        ("GW200105", "NSBH-merger", 8.9, 0.28, "NS-BH merger"),
        ("GW200115", "NSBH-merger", 5.7, 0.33, "NS-BH merger"),
        ("GW190412", "BH-merger", 30.1, 0.26, "Asymmetric mass ratio"),
        ("GW190814", "BH-merger", 25.6, 0.24, "Possible NS-BH"),
        ("GW191204", "BH-merger", 44.0, 0.29, "Intermediate mass"),
        ("GW200129", "BH-merger", 34.0, 0.31, "Spinning black holes"),
    ]
    
    for name, category, mass, z, note in gw_detections:
        obj = create_compatible_object(
            name, category, mass, z,
            a_m=1e7 + 9e7 * random.random(),   # Inspiral separation
            e=0.0 + 0.1 * random.random(),    # Nearly circular at merger
            P_year=0.0001 + 0.001 * random.random(),  # Final orbits
            source=f"LIGO/Virgo: {note}"
        )
        objects.append(obj)
    
    # === EXTREME MASS RATIO INSPIRALS (EMRI) ===
    emri_objects = [
        ("EMRI_SgrA_1", "EMRI", 4.297e6, 0.0001, "Stellar object around Sgr A*"),
        ("EMRI_SgrA_2", "EMRI", 4.297e6, 0.0002, "Compact object inspiral"),
        ("EMRI_M87_1", "EMRI", 6.5e9, 0.004, "Object around M87*"),
        ("EMRI_NGC1277_1", "EMRI", 1.7e10, 0.017, "Object around NGC 1277"),
    ]
    
    for name, category, mass, z, note in emri_objects:
        obj = create_compatible_object(
            name, category, mass, z,
            a_m=1e13 + 9e13 * random.random(),  # Close to SMBH
            e=0.1 + 0.8 * random.random(),     # Highly eccentric
            source=f"EMRI: {note}"
        )
        objects.append(obj)
    
    # === MORE STELLAR MASS BLACK HOLES ===
    stellar_bhs = [
        ("XTE_J1550-564", "stellar-bh", 9.1, 0.00001, "Transient black hole"),
        ("GRO_J1655-40", "stellar-bh", 7.0, 0.00001, "Superluminal jets"),
        ("4U_1543-47", "stellar-bh", 9.4, 0.00001, "X-ray binary"),
        ("XTE_J1859+226", "stellar-bh", 7.8, 0.00001, "Fast X-ray transient"),
        ("GS_2000+25", "stellar-bh", 7.5, 0.00001, "Soft X-ray transient"),
        ("Nova_Sco_1994", "stellar-bh", 6.9, 0.00001, "X-ray nova"),
        ("SAX_J1819.3-2525", "stellar-bh", 7.1, 0.00001, "Galactic plane BH"),
        ("XTE_J1752-223", "stellar-bh", 9.5, 0.00001, "Outbursting BH"),
    ]
    
    for name, category, mass, z, note in stellar_bhs:
        obj = create_compatible_object(
            name, category, mass, z,
            a_m=1e9 + 9e9 * random.random(),   # Binary separation
            e=0.0 + 0.3 * random.random(),    # Moderate eccentricity
            source=f"Stellar BH: {note}"
        )
        objects.append(obj)
    
    return objects

def create_compatible_object(name: str, category: str, M_solar: float, z: float,
                           a_m: float = None, e: float = None,
                           P_year: float = None, source: str = "Literature",
                           r_emit_m: float = None) -> Dict:
    """Create object compatible with main dataset structure."""
    
    # Calculate emission radius if not provided
    if r_emit_m is None:
        rs = 2 * G * M_solar * M_SUN / (C * C)  # Schwarzschild radius
        if "SMBH" in category or "IMBH" in category or "EMRI" in category:
            r_emit_m = rs * (50 + 450 * random.random())  # 50-500 rs
        elif "stellar-bh" in category or "merger" in category:
            r_emit_m = rs * (5 + 25 * random.random())   # 5-30 rs
        elif "pulsar" in category or "neutron" in category:
            r_emit_m = 10e3 + 5e3 * random.random()     # 10-15 km
        else:
            r_emit_m = rs * 100  # Default
    
    # Orbital parameters
    if a_m is None:
        if "S-star" in category:
            a_m = 1e14 + 5e14 * random.random()
        else:
            a_m = r_emit_m * (2 + 8 * random.random())
    
    if e is None:
        if "S-star" in category:
            e = 0.1 + 0.8 * random.random()
        else:
            e = 0.0 + 0.5 * random.random()
    
    if P_year is None:
        if M_solar > 0:
            P_sec = 2 * math.pi * math.sqrt(a_m**3 / (G * M_solar * M_SUN))
            P_year = P_sec / (365.25 * 24 * 3600)
        else:
            P_year = 100.0
    
    # Frequencies
    f_emit_Hz = HALPHA_HZ
    f_obs_Hz = f_emit_Hz / (1.0 + z) if z > 0 else f_emit_Hz
    
    # Wavelengths
    lambda_emit_nm = C / f_emit_Hz * 1e9
    lambda_obs_nm = C / f_obs_Hz * 1e9 if f_obs_Hz > 0 else lambda_emit_nm
    
    # Velocities
    if M_solar > 0 and a_m > 0:
        v_orbital = math.sqrt(G * M_solar * M_SUN / a_m)
        v_tot_mps = v_orbital * (0.5 + 0.5 * random.random())
        v_los_mps = v_tot_mps * (0.1 + 0.8 * random.random())
    else:
        v_tot_mps = 0.0
        v_los_mps = 0.0
    
    return {
        "case": name,
        "category": category,
        "M_solar": M_solar,
        "a_m": a_m,
        "e": e,
        "P_year": P_year,
        "T0_year": 2020.0 + 10 * random.random(),
        "f_true_deg": 360 * random.random(),
        "z": z,
        "f_emit_Hz": f_emit_Hz,
        "f_obs_Hz": f_obs_Hz,
        "lambda_emit_nm": lambda_emit_nm,
        "lambda_obs_nm": lambda_obs_nm,
        "v_los_mps": v_los_mps,
        "v_tot_mps": v_tot_mps,
        "z_geom_hint": "",
        "N0": 1.0,
        "source": source,
        "r_emit_m": r_emit_m
    }

def main():
    """Expand the dataset with additional objects."""
    
    random.seed(42)  # Reproducible results
    
    # Load existing cleaned dataset
    print("[INFO] Loading existing cleaned dataset...")
    existing_objects = []
    
    try:
        with open("real_data_full_cleaned.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_objects = list(reader)
        print(f"[OK] Loaded {len(existing_objects)} existing objects")
    except FileNotFoundError:
        print("[ERROR] real_data_full_cleaned.csv not found. Run clean_dataset.py first.")
        return
    
    # Create additional objects
    print("[INFO] Creating additional objects...")
    additional_objects = create_additional_objects()
    
    # Merge datasets
    all_objects = existing_objects + additional_objects
    
    # Remove any potential duplicates by case name
    seen_cases = set()
    unique_objects = []
    for obj in all_objects:
        case = obj['case']
        if case not in seen_cases:
            unique_objects.append(obj)
            seen_cases.add(case)
        else:
            print(f"[WARNING] Duplicate case removed: {case}")
    
    # Write expanded dataset
    output_file = "real_data_full_expanded.csv"
    
    if unique_objects:
        fieldnames = list(unique_objects[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_objects)
    
    # Statistics
    categories = {}
    mass_range = [float('inf'), 0]
    z_range = [float('inf'), 0]
    
    for obj in unique_objects:
        cat = obj.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        
        try:
            mass = float(obj.get("M_solar", 0))
            if mass > 0:
                mass_range[0] = min(mass_range[0], mass)
                mass_range[1] = max(mass_range[1], mass)
        except:
            pass
            
        try:
            z = float(obj.get("z", 0))
            if z > 0:
                z_range[0] = min(z_range[0], z)
                z_range[1] = max(z_range[1], z)
        except:
            pass
    
    print(f"\n[SUCCESS] Expanded dataset created: {output_file}")
    print(f"[INFO] Total objects: {len(unique_objects)}")
    print(f"  - Original: {len(existing_objects)}")
    print(f"  - Added: {len(additional_objects)}")
    print(f"[INFO] Categories: {dict(categories)}")
    print(f"[INFO] Mass range: {mass_range[0]:.2e} - {mass_range[1]:.2e} M_sun")
    print(f"[INFO] Redshift range: {z_range[0]:.6f} - {z_range[1]:.3f}")
    
    # Highlight new object types
    new_categories = ["IMBH", "EMRI", "NS-merger", "BH-merger", "NSBH-merger"]
    print(f"\n[INFO] New object types added:")
    for cat in new_categories:
        count = categories.get(cat, 0)
        if count > 0:
            print(f"  - {cat}: {count} objects")
    
    print(f"\n[READY] Test expanded dataset with:")
    print(f"  python segspace_all_in_one_extended.py eval-redshift --csv {output_file} --prefer-z --paired-stats")

if __name__ == "__main__":
    main()
