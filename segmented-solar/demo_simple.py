#!/usr/bin/env python3
"""
Simple demo of Segmented Spacetime Solar System Visualization.
Creates a basic visualization without external data dependencies.
"""

import sys
import numpy as np
import pandas as pd
from src import (
    build_icosphere,
    SegmentedSpacetimeField,
    SegmentedSpacetimeVisualizer
)

def main():
    print("Segmented Spacetime Solar System - Simple Demo")
    print("=" * 50)
    
    # 1. Generate mesh
    print("1. Generating spacetime mesh...")
    vertices, faces = build_icosphere(radius=50.0, subdivisions=4)
    print(f"   Mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    # 2. Setup field calculator with simplified Solar System
    print("2. Setting up segmented spacetime field...")
    
    params = {
        'p': 2.0,           # Power-law index
        'N_bg': 0.0,        # Background density
        'N_max': 5.0,       # Maximum density
        'alpha': 1.0,       # Time dilation coupling
        'kappa': 0.015      # Refractive index coupling
    }
    
    field = SegmentedSpacetimeField(params)
    
    # Add simplified Solar System bodies
    bodies_data = [
        {"name": "Sun", "pos": [0, 0, 0], "mass_solar": 1.0, "radius_au": 0.00465},
        {"name": "Earth", "pos": [1.0, 0, 0], "mass_solar": 3e-6, "radius_au": 4.26e-5},
        {"name": "Jupiter", "pos": [5.2, 0, 0], "mass_solar": 9.54e-4, "radius_au": 4.77e-4},
        {"name": "Saturn", "pos": [9.5, 0, 0], "mass_solar": 2.86e-4, "radius_au": 4.03e-4},
    ]
    
    catalog_data = []
    positions = []
    
    for body in bodies_data:
        # Add to field calculator
        r0 = max(body["radius_au"], 1e-6)
        gamma = 1.0 if body["name"] == "Sun" else min(body["mass_solar"], 1.0)
        
        field.add_body(
            position=np.array(body["pos"]),
            mass_scaled=body["mass_solar"],
            gamma=gamma,
            r0=r0,
            r_nb=r0 * 4,
            delta=r0 * 0.8,
            name=body["name"]
        )
        
        # Add to catalog for visualization
        catalog_data.append({
            'name': body["name"],
            'mass_kg': body["mass_solar"] * 1.98847e30,
            'radius_km': body["radius_au"] * 149597870.7
        })
        positions.append(body["pos"])
    
    catalog = pd.DataFrame(catalog_data)
    positions = np.array(positions)
    
    print(f"   Added {len(bodies_data)} bodies to field")
    
    # 3. Compute fields
    print("3. Computing segmented spacetime fields...")
    N, tau, n = field.compute_all_fields(vertices)
    
    print(f"   N: min={N.min():.6f}, max={N.max():.3f}, mean={N.mean():.3f}")
    print(f"   tau: min={tau.min():.6f}, max={tau.max():.3f}, mean={tau.mean():.3f}")
    print(f"   n: min={n.min():.6f}, max={n.max():.3f}, mean={n.mean():.3f}")
    
    # 4. Create visualization
    print("4. Creating 3D visualization...")
    
    visualizer = SegmentedSpacetimeVisualizer(
        title="Segmented Spacetime — Solar System Demo (φ/π Structure)"
    )
    
    # Add mesh with field data
    field_data = {'N': N, 'tau': tau, 'n': n}
    visualizer.add_mesh(vertices, faces, field_data, default_field='N')
    
    # Add celestial bodies
    visualizer.add_bodies(catalog, positions)
    
    # Save visualization
    output_file = "segmented_spacetime_demo.html"
    visualizer.save_html(output_file)
    
    print(f"   Saved to: {output_file}")
    
    # 5. Field analysis
    print("5. Field analysis along radial profile...")
    
    # Radial profile from 0.1 to 30 AU
    r_points = np.logspace(-1, 1.5, 50)
    radial_points = np.column_stack([r_points, np.zeros_like(r_points), np.zeros_like(r_points)])
    
    N_radial, tau_radial, n_radial = field.compute_all_fields(radial_points)
    
    # Save radial profile data
    profile_df = pd.DataFrame({
        'r_AU': r_points,
        'N': N_radial,
        'tau': tau_radial,
        'n': n_radial
    })
    profile_df.to_csv("radial_profile.csv", index=False)
    
    print("   Key field values:")
    for i, r in enumerate([0.1, 1.0, 5.2, 9.5]):
        idx = np.argmin(np.abs(r_points - r))
        print(f"     r = {r:4.1f} AU: N = {N_radial[idx]:.6f}, "
              f"tau = {tau_radial[idx]:.6f}, n = {n_radial[idx]:.6f}")
    
    print("\nDemo complete!")
    print(f"Files created:")
    print(f"  - {output_file} (interactive 3D visualization)")
    print(f"  - radial_profile.csv (field values vs distance)")
    print(f"\nOpen {output_file} in your web browser to explore the segmented spacetime mesh!")

if __name__ == "__main__":
    main()
