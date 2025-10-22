#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Perfect Segmented Spacetime Analysis - Interactive Standalone
Rapidity-based calculations with NO 0/0 singularities
Supports custom data, all physical regimes, complete analysis

⚠️ NOTE ON LABORATORY REFERENCE FRAMES:
The "rest wavelength" (e.g. λ₀ = 656.281 nm) is NOT a universal constant but
a laboratory-defined reference value. Observed frequency f_obs depends on the
laboratory frame (gravitational potential, time standard). Any formula involving
f_obs must use data from the SAME reference frame or after proper barycentric
correction. All data here are assumed barycentric-corrected. See REFERENCE_FRAME_NOTE.md.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
from datetime import datetime

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Constants
C = 299792458  # Speed of light (m/s)
G = 6.67430e-11  # Gravitational constant (m³/kg/s²)
PHI = (1 + 5**0.5) / 2  # Golden ratio (pure Python)
M_SUN = 1.98847e30  # Solar mass (kg)

print("="*80)
print("PERFECT SEGMENTED SPACETIME ANALYSIS")
print("Rapidity-Based Calculations - NO 0/0 Singularities")
print("="*80)

# ============================================================================
# RAPIDITY CORE FUNCTIONS (Perfect Implementation)
# ============================================================================

def velocity_to_rapidity(v, c=C):
    """
    Convert velocity to rapidity (hyperbolic angle).
    chi = arctanh(v/c) - ALWAYS well-defined, NO singularities at v=0
    """
    beta = np.clip(np.asarray(v) / c, -0.99999, 0.99999)
    return np.arctanh(beta)

def rapidity_to_velocity(chi, c=C):
    """
    Convert rapidity to velocity.
    v = c*tanh(chi) - smooth everywhere including chi=0
    """
    return c * np.tanh(chi)

def bisector_rapidity(chi1, chi2):
    """
    Angular bisector (Winkelhalbierende) - natural coordinate origin.
    For opposite: chi2=-chi1 -> chi=0 WITHOUT 0/0!
    """
    return 0.5 * (chi1 + chi2)

def safe_velocity_composition(v1, v2, c=C):
    """
    Velocity addition using rapidity - NO 0/0 at equilibrium!
    REPLACES: (v1+v2)/(1-v1*v2/c^2) which fails at equilibrium
    """
    chi1 = velocity_to_rapidity(v1, c)
    chi2 = velocity_to_rapidity(v2, c)
    chi_rel = chi2 - chi1  # NO division!
    return rapidity_to_velocity(chi_rel, c)

# ============================================================================
# SEGMENTED SPACETIME PHYSICS
# ============================================================================

def schwarzschild_radius(M, G_const=G, c=C):
    """Schwarzschild radius: r_s = 2GM/c²"""
    return 2 * G_const * M / (c**2)

def keplerian_velocity(r, M, G_const=G):
    """Keplerian orbital velocity: v = sqrt(GM/r)"""
    return np.sqrt(G_const * M / r)

def escape_velocity(r, M, G_const=G):
    """Escape velocity: v_esc = sqrt(2GM/r)"""
    return np.sqrt(2 * G_const * M / r)

def compute_equilibrium_rapidity(r, M, c=C, G_const=G):
    """
    Compute equilibrium using rapidity formulation.
    NO 0/0 singularities at equilibrium points!
    """
    r_s = schwarzschild_radius(M, G_const, c)
    
    # Simple velocity estimates (improve with proper orbital mechanics)
    v_orb = min(keplerian_velocity(r, M, G_const), 0.9 * c)
    v_esc = min(escape_velocity(r, M, G_const), 0.9 * c)
    
    # Convert to rapidities
    chi_self = velocity_to_rapidity(v_orb, c)
    chi_grav = velocity_to_rapidity(-v_esc, c)  # Negative for infall
    
    # Effective rapidity (uses bisector)
    chi_eff = bisector_rapidity(chi_self, chi_grav)
    
    # Convert back
    v_eff = rapidity_to_velocity(chi_eff, c)
    gamma_eff = np.cosh(chi_eff)
    
    return {
        'r': r,
        'r_s': r_s,
        'x': r / r_s,
        'chi_self': chi_self,
        'chi_grav': chi_grav,
        'chi_eff': chi_eff,
        'v_self': v_orb,
        'v_grav': -v_esc,
        'v_eff': v_eff,
        'gamma_eff': gamma_eff,
        'is_equilibrium': abs(chi_eff) < 1e-10,
        'regime': classify_regime(r / r_s)
    }

def classify_regime(x):
    """Classify physical regime by r/r_s"""
    if x < 1.5:
        return "Very Close (r < 1.5 r_s)"
    elif 1.5 <= x < 2.0:
        return "Near Horizon (1.5-2 r_s)"
    elif 2.0 <= x <= 3.0:
        return "Photon Sphere (2-3 r_s)"
    elif 3.0 < x <= 10.0:
        return "Strong Field (3-10 r_s)"
    else:
        return "Weak Field (r > 10 r_s)"

def compute_redshift_seg(r, M, v, phi=PHI, use_rapidity=True, c=C):
    """
    Compute SEG redshift with rapidity formulation.
    
    Parameters:
    -----------
    r : float - Radius (m)
    M : float - Mass (kg)
    v : float - Observed velocity (m/s)
    phi : float - Golden ratio
    use_rapidity : bool - Use rapidity formulation (recommended!)
    c : float - Speed of light
    
    Returns:
    --------
    z_seg : float - Predicted redshift
    """
    r_s = schwarzschild_radius(M, G, c)
    
    if use_rapidity:
        # Rapidity-based (NO 0/0!)
        result = compute_equilibrium_rapidity(r, M, c, G)
        v_eff = result['v_eff']
        gamma = result['gamma_eff']
    else:
        # Traditional (may fail at equilibrium)
        v_orb = keplerian_velocity(r, M, G)
        v_esc = escape_velocity(r, M, G)
        
        # Check for near-equilibrium
        if abs(v_orb + v_esc) < 1e-6:
            print("WARNING: Near equilibrium - use rapidity formulation!")
            return np.nan
        
        v_eff = v_orb - v_esc
        gamma = 1 / np.sqrt(1 - (v_eff/c)**2) if abs(v_eff) < c else 1e10
    
    # φ-based corrections (simplified)
    x = r / r_s
    phi_factor = 1 + (phi - 1) * np.exp(-abs(x - phi/2))
    
    # Redshift calculation
    z_grav = np.sqrt(1 - r_s/r) - 1 if r > r_s else np.nan
    z_doppler = np.sqrt((1 + v/c)/(1 - v/c)) - 1
    
    z_seg = (z_grav + z_doppler) * phi_factor * gamma
    
    return z_seg

# ============================================================================
# DATA ANALYSIS
# ============================================================================

def analyze_observation(row, use_rapidity=True):
    """
    Analyze single observation with rapidity formulation.
    
    Parameters:
    -----------
    row : dict - Must contain: M_msun, r_m, z_obs
    use_rapidity : bool - Use rapidity (recommended!)
    
    Returns:
    --------
    results : dict - Complete analysis
    """
    M = row['M_msun'] * M_SUN
    r = row['r_m']
    z_obs = row['z_obs']
    
    # Equilibrium analysis
    eq = compute_equilibrium_rapidity(r, M, C, G)
    
    # Predicted redshift
    z_pred = compute_redshift_seg(r, M, 0, PHI, use_rapidity, C)
    
    # Error
    error = abs(z_pred - z_obs) if not np.isnan(z_pred) else np.nan
    
    return {
        **eq,
        'z_obs': z_obs,
        'z_pred': z_pred,
        'error': error,
        'M_msun': row['M_msun'],
        'rapidity_used': use_rapidity
    }

def analyze_dataset(df, use_rapidity=True, verbose=True):
    """
    Analyze complete dataset with rapidity formulation.
    
    Parameters:
    -----------
    df : DataFrame - Must contain: M_msun, r_m, z_obs
    use_rapidity : bool - Use rapidity (recommended!)
    verbose : bool - Print progress
    
    Returns:
    --------
    results_df : DataFrame - Complete analysis
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"ANALYZING DATASET: {len(df)} observations")
        print(f"Rapidity formulation: {'ENABLED' if use_rapidity else 'DISABLED'}")
        print(f"{'='*80}\n")
    
    results = []
    
    for idx, row in df.iterrows():
        if verbose and idx % 10 == 0:
            print(f"Processing {idx+1}/{len(df)}...", end='\r')
        
        try:
            result = analyze_observation(row.to_dict(), use_rapidity)
            results.append(result)
        except Exception as e:
            if verbose:
                print(f"WARNING: Row {idx} failed: {e}")
            results.append({
                'error': np.nan,
                'regime': 'ERROR',
                'M_msun': row.get('M_msun', np.nan)
            })
    
    if verbose:
        print(f"\nProcessing complete: {len(results)} results")
    
    results_df = pd.DataFrame(results)
    
    # Statistics by regime
    if verbose and 'regime' in results_df.columns:
        print(f"\n{'='*80}")
        print("STATISTICS BY REGIME")
        print(f"{'='*80}")
        
        for regime in results_df['regime'].unique():
            if regime == 'ERROR':
                continue
            
            subset = results_df[results_df['regime'] == regime]
            n = len(subset)
            equilibrium_count = subset['is_equilibrium'].sum()
            mean_error = subset['error'].mean()
            
            print(f"\n{regime}:")
            print(f"  n = {n}")
            print(f"  Equilibrium points: {equilibrium_count}")
            print(f"  Mean error: {mean_error:.6f}")
    
    return results_df

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_analysis():
    """Interactive analysis mode with user input"""
    print("\n" + "="*80)
    print("INTERACTIVE ANALYSIS MODE")
    print("="*80)
    
    print("\nEnter observation parameters:")
    
    # Get user input
    try:
        M_msun = float(input("Mass (solar masses, e.g., 1.0 for Sun): "))
        r_km = float(input("Radius (km, e.g., 10000): "))
        z_obs = float(input("Observed redshift (e.g., 0.01): "))
        
        M = M_msun * M_SUN
        r = r_km * 1000  # Convert to meters
        
        print(f"\n{'='*80}")
        print("ANALYSIS RESULTS")
        print(f"{'='*80}")
        
        # Equilibrium analysis
        eq = compute_equilibrium_rapidity(r, M, C, G)
        
        print(f"\nInput:")
        print(f"  M = {M_msun:.2f} M_sun = {M:.3e} kg")
        print(f"  r = {r_km:.1f} km = {r:.3e} m")
        print(f"  r_s = {eq['r_s']:.3e} m")
        print(f"  x = r/r_s = {eq['x']:.3f}")
        print(f"  Regime: {eq['regime']}")
        
        print(f"\nRapidity Analysis:")
        print(f"  chi_self = {eq['chi_self']:.6f}")
        print(f"  chi_grav = {eq['chi_grav']:.6f}")
        print(f"  chi_eff = {eq['chi_eff']:.6f}")
        print(f"  v_eff = {eq['v_eff']:.3e} m/s ({eq['v_eff']/C:.6f}c)")
        print(f"  gamma_eff = {eq['gamma_eff']:.6f}")
        print(f"  Equilibrium? {'YES' if eq['is_equilibrium'] else 'no'}")
        
        # Redshift prediction
        z_pred = compute_redshift_seg(r, M, 0, PHI, True, C)
        error = abs(z_pred - z_obs) if not np.isnan(z_pred) else np.nan
        
        print(f"\nRedshift:")
        print(f"  z_obs = {z_obs:.6f}")
        print(f"  z_pred = {z_pred:.6f}")
        print(f"  |error| = {error:.6f}")
        print(f"  Relative error = {100*error/z_obs:.2f}%")
        
        print(f"\n{'='*80}")
        
    except ValueError as e:
        print(f"ERROR: Invalid input: {e}")
    except KeyboardInterrupt:
        print("\nWARNING: Interrupted by user")

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Perfect Segmented Spacetime Analysis with Rapidity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python perfect_seg_analysis.py --interactive
  
  # Analyze CSV file
  python perfect_seg_analysis.py --csv data/my_data.csv
  
  # Single observation
  python perfect_seg_analysis.py --mass 1.0 --radius 10000 --redshift 0.01
  
  # Disable rapidity (not recommended!)
  python perfect_seg_analysis.py --csv data/my_data.csv --no-rapidity
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode with user input')
    parser.add_argument('--csv', type=str,
                       help='CSV file with columns: M_msun, r_m, z_obs')
    parser.add_argument('--mass', type=float,
                       help='Mass in solar masses')
    parser.add_argument('--radius', type=float,
                       help='Radius in km')
    parser.add_argument('--redshift', type=float,
                       help='Observed redshift')
    parser.add_argument('--no-rapidity', action='store_true',
                       help='Disable rapidity formulation (may fail at equilibrium!)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output CSV file for results')
    parser.add_argument('--verbose', '-v', action='store_true', default=True,
                       help='Verbose output')
    
    args = parser.parse_args()
    
    use_rapidity = not args.no_rapidity
    
    if args.no_rapidity:
        print("WARNING: Rapidity formulation DISABLED!")
        print("This may cause 0/0 errors at equilibrium points!")
    
    # Interactive mode
    if args.interactive:
        interactive_analysis()
        return
    
    # Single observation
    if args.mass and args.radius and args.redshift:
        M = args.mass * M_SUN
        r = args.radius * 1000
        
        row = {'M_msun': args.mass, 'r_m': r, 'z_obs': args.redshift}
        result = analyze_observation(row, use_rapidity)
        
        print(f"\n{'='*80}")
        print("SINGLE OBSERVATION ANALYSIS")
        print(f"{'='*80}")
        print(f"\nM = {args.mass:.2f} M_sun")
        print(f"r = {args.radius:.1f} km = {result['x']:.3f} r_s")
        print(f"Regime: {result['regime']}")
        print(f"\nz_obs = {args.redshift:.6f}")
        print(f"z_pred = {result['z_pred']:.6f}")
        print(f"|error| = {result['error']:.6f}")
        print(f"\nEquilibrium: {'YES' if result['is_equilibrium'] else 'no'}")
        print(f"chi_eff = {result['chi_eff']:.6f}")
        print(f"{'='*80}")
        return
    
    # CSV file
    if args.csv:
        csv_path = Path(args.csv)
        if not csv_path.exists():
            print(f"ERROR: File not found: {args.csv}")
            return
        
        print(f"Loading data from: {args.csv}")
        df = pd.read_csv(csv_path)
        
        # Validate and normalize columns
        # Support multiple column name variants
        mass_cols = ['M_msun', 'M_solar', 'mass_msun', 'M']
        radius_cols = ['r_m', 'r_emit_m', 'radius_m', 'r']
        redshift_cols = ['z_obs', 'z', 'redshift']
        
        mass_col = next((c for c in mass_cols if c in df.columns), None)
        radius_col = next((c for c in radius_cols if c in df.columns), None)
        redshift_col = next((c for c in redshift_cols if c in df.columns), None)
        
        if not all([mass_col, radius_col, redshift_col]):
            print("ERROR: Missing required data!")
            print(f"  Need: Mass (M_msun/M_solar), Radius (r_m/r_emit_m), Redshift (z_obs/z)")
            print(f"  Available columns: {list(df.columns)}")
            return
        
        # Normalize column names
        df = df.rename(columns={
            mass_col: 'M_msun',
            radius_col: 'r_m',
            redshift_col: 'z_obs'
        })
        
        # Analyze
        results_df = analyze_dataset(df, use_rapidity, args.verbose)
        
        # Save results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            results_df.to_csv(output_path, index=False)
            print(f"\nOK: Results saved to: {args.output}")
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Total observations: {len(results_df)}")
        print(f"Equilibrium points: {results_df['is_equilibrium'].sum()}")
        print(f"Mean error: {results_df['error'].mean():.6f}")
        print(f"Median error: {results_df['error'].median():.6f}")
        print(f"Rapidity used: {'YES' if use_rapidity else 'NO'}")
        print(f"{'='*80}")
        return
    
    # No arguments - show help
    parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWARNING: Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
