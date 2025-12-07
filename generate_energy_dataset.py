#!/usr/bin/env python3
"""
Generate Large Energy Dataset for Maximum Density Testing
Creates 1000 objects across all physical regimes for comprehensive validation

Authors: Carmen Wrede & Lino Casu
License: ANTI-CAPITALIST SOFTWARE LICENSE v1.4
Date: 2025-12-07
"""

import numpy as np
import csv
from pathlib import Path

# Physical constants
c = 299792458.0  # m/s
G = 6.67430e-11  # m^3 kg^-1 s^-2
M_sun = 1.989e30  # kg

def generate_comprehensive_dataset(n_objects=1000):
    """Generate comprehensive dataset across all physical regimes"""
    
    print("="*80)
    print("GENERATING COMPREHENSIVE ENERGY DATASET")
    print("="*80)
    print(f"Target: {n_objects} objects across all regimes")
    print("")
    
    objects = []
    
    # Distribution across regimes (percentages)
    n_weak = int(n_objects * 0.40)      # 40% weak field (stars, planets)
    n_moderate = int(n_objects * 0.30)  # 30% moderate (white dwarfs, neutron stars)
    n_strong = int(n_objects * 0.20)    # 20% strong field (stellar BH, IMBH)
    n_extreme = int(n_objects * 0.10)   # 10% extreme (SMBH, M87*)
    
    print(f"Distribution:")
    print(f"  Weak Field:     {n_weak:4d} objects (planets, stars)")
    print(f"  Moderate Field: {n_moderate:4d} objects (compact objects)")
    print(f"  Strong Field:   {n_strong:4d} objects (stellar BH)")
    print(f"  Extreme Field:  {n_extreme:4d} objects (SMBH)")
    print("")
    
    obj_id = 1
    
    # ========================================================================
    # WEAK FIELD REGIME (Planets, Stars)
    # ========================================================================
    print(f"Generating {n_weak} weak field objects...")
    
    # Planets (Earth-like to Jupiter-like)
    for i in range(n_weak // 4):
        M = np.random.uniform(5.97e24, 1.898e27)  # Earth to Jupiter
        R = np.random.uniform(6.371e6, 7.0e7)      # Earth to Jupiter radius
        v = np.random.uniform(0, 5e4)              # 0-50 km/s
        name = f"Planet_{i+1}"
        objects.append((obj_id, name, M, R, v, "planet"))
        obj_id += 1
    
    # Solar-mass stars
    for i in range(n_weak // 4):
        M = np.random.uniform(0.08, 100) * M_sun  # 0.08-100 M_sun
        R = np.random.uniform(7e8, 7e9)            # ~1-10 R_sun
        v = np.random.uniform(0, 1e5)              # 0-100 km/s
        name = f"Star_{i+1}"
        objects.append((obj_id, name, M, R, v, "star"))
        obj_id += 1
    
    # Red giants
    for i in range(n_weak // 4):
        M = np.random.uniform(0.5, 10) * M_sun
        R = np.random.uniform(7e10, 7e11)  # 100-1000 R_sun
        v = np.random.uniform(0, 5e4)
        name = f"RedGiant_{i+1}"
        objects.append((obj_id, name, M, R, v, "red_giant"))
        obj_id += 1
    
    # Main sequence variety
    for i in range(n_weak - 3*(n_weak//4)):
        M = np.random.uniform(0.1, 50) * M_sun
        R = np.random.uniform(7e7, 1e10)
        v = np.random.uniform(0, 2e5)
        name = f"MainSeq_{i+1}"
        objects.append((obj_id, name, M, R, v, "main_sequence"))
        obj_id += 1
    
    # ========================================================================
    # MODERATE FIELD REGIME (Compact Objects)
    # ========================================================================
    print(f"Generating {n_moderate} moderate field objects...")
    
    # White dwarfs
    for i in range(n_moderate // 2):
        M = np.random.uniform(0.17, 1.4) * M_sun  # Chandrasekhar limit
        R = np.random.uniform(5e6, 1e7)            # ~Earth-sized
        v = np.random.uniform(1e5, 5e6)            # High velocities
        name = f"WhiteDwarf_{i+1}"
        objects.append((obj_id, name, M, R, v, "white_dwarf"))
        obj_id += 1
    
    # Neutron stars
    for i in range(n_moderate // 2):
        M = np.random.uniform(1.1, 2.3) * M_sun  # TOV limit ~2.3
        R = np.random.uniform(1e4, 1.5e4)        # 10-15 km
        v = np.random.uniform(1e6, 1e7)          # Very high
        name = f"NeutronStar_{i+1}"
        objects.append((obj_id, name, M, R, v, "neutron_star"))
        obj_id += 1
    
    # ========================================================================
    # STRONG FIELD REGIME (Stellar Black Holes, IMBH)
    # ========================================================================
    print(f"Generating {n_strong} strong field objects...")
    
    # Stellar black holes
    for i in range(n_strong // 2):
        M = np.random.uniform(3, 100) * M_sun
        r_s = 2 * G * M / c**2
        R = np.random.uniform(1.5, 10) * r_s  # 1.5-10 r_s
        v = np.random.uniform(1e7, 5e7)
        name = f"StellarBH_{i+1}"
        objects.append((obj_id, name, M, R, v, "stellar_bh"))
        obj_id += 1
    
    # Intermediate mass BH
    for i in range(n_strong // 2):
        M = np.random.uniform(100, 1e5) * M_sun
        r_s = 2 * G * M / c**2
        R = np.random.uniform(1.5, 20) * r_s
        v = np.random.uniform(5e7, 1e8)
        name = f"IMBH_{i+1}"
        objects.append((obj_id, name, M, R, v, "imbh"))
        obj_id += 1
    
    # ========================================================================
    # EXTREME FIELD REGIME (SMBH)
    # ========================================================================
    print(f"Generating {n_extreme} extreme field objects...")
    
    for i in range(n_extreme):
        M = np.random.uniform(1e6, 1e10) * M_sun  # 10^6 to 10^10 M_sun
        r_s = 2 * G * M / c**2
        R = np.random.uniform(1.2, 50) * r_s
        v = np.random.uniform(1e8, 2.5e8)  # Up to ~0.83c
        name = f"SMBH_{i+1}"
        objects.append((obj_id, name, M, R, v, "smbh"))
        obj_id += 1
    
    print(f"\nTotal objects generated: {len(objects)}")
    return objects


def save_dataset(objects, filename="data/energy_dataset_1000.csv"):
    """Save dataset to CSV"""
    
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print(f"SAVING DATASET: {filepath}")
    print("="*80)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "ID",
            "Name",
            "Mass_kg",
            "Radius_m",
            "Velocity_m/s",
            "Type",
            "Mass_Msun",
            "Schwarzschild_radius_m",
            "R/r_s"
        ])
        
        # Data rows
        for obj_id, name, M, R, v, obj_type in objects:
            r_s = 2 * G * M / c**2
            M_msun = M / M_sun
            R_over_rs = R / r_s
            
            writer.writerow([
                obj_id,
                name,
                f"{M:.6e}",
                f"{R:.6e}",
                f"{v:.6e}",
                obj_type,
                f"{M_msun:.6e}",
                f"{r_s:.6e}",
                f"{R_over_rs:.6e}"
            ])
    
    # Statistics
    file_size = filepath.stat().st_size
    
    print(f"[OK] Dataset saved!")
    print(f"     File: {filepath.resolve()}")
    print(f"     Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"     Rows: {len(objects)} objects + 1 header")
    
    # Regime statistics
    types = {}
    for _, _, _, _, _, obj_type in objects:
        types[obj_type] = types.get(obj_type, 0) + 1
    
    print(f"\n   Breakdown:")
    for obj_type, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"     {obj_type:15s}: {count:4d} objects")
    
    print("="*80)
    return filepath


def print_sample_objects(objects, n=10):
    """Print sample objects from dataset"""
    
    print("\n" + "="*80)
    print(f"SAMPLE OBJECTS (first {n})")
    print("="*80)
    
    print(f"{'ID':>4} {'Name':20} {'Mass (Msun)':>12} {'R/r_s':>10} {'Type':15}")
    print("-"*80)
    
    for i, (obj_id, name, M, R, v, obj_type) in enumerate(objects[:n]):
        r_s = 2 * G * M / c**2
        M_msun = M / M_sun
        R_over_rs = R / r_s
        print(f"{obj_id:4d} {name:20} {M_msun:12.3e} {R_over_rs:10.3f} {obj_type:15}")
    
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPREHENSIVE ENERGY DATASET GENERATOR")
    print("="*80)
    print("Purpose: Generate 1000 objects for maximum density testing")
    print("Coverage: All physical regimes from planets to SMBH")
    print("Output: CSV file ready for energy framework validation")
    print("")
    
    # Generate dataset
    objects = generate_comprehensive_dataset(n_objects=1000)
    
    # Print samples
    print_sample_objects(objects, n=20)
    
    # Save to CSV
    filepath = save_dataset(objects)
    
    print("\n[SUCCESS] DATASET GENERATION COMPLETE!")
    print(f"          Ready for energy framework testing with maximum density")
    print(f"          File: {filepath.resolve()}")
    print("")
    print("="*80)
