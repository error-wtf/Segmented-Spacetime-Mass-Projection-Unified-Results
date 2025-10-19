#!/usr/bin/env python3
"""
SSZ-Rings CLI Tool

Command-line interface for segmented radiowave propagation predictions.

Usage:
    ssz-rings --csv data.csv --v0 12.5 --alpha 1.0
    ssz-rings --csv data.csv --v0 12.5 --fit-alpha --out-table results.csv

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ssz.segwave import (
    predict_velocity_profile,
    predict_frequency_track,
    compute_residuals,
    compute_cumulative_gamma,
    fit_alpha,
    load_ring_data,
    save_results,
    save_report
)


def generate_report(
    df_result,
    metrics: dict | None,
    alpha: float,
    v0: float,
    beta: float,
    eta: float,
    fit_mode: bool
) -> str:
    """Generate summary report text."""
    
    lines = []
    lines.append("=" * 60)
    lines.append("SSZ RINGS - SEGMENTED RADIOWAVE PROPAGATION REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append("PARAMETERS:")
    lines.append(f"  v0 (initial velocity): {v0:.3f} km/s")
    
    if fit_mode:
        lines.append(f"  alpha (fitted): {alpha:.6f}")
    else:
        lines.append(f"  alpha (fixed): {alpha:.6f}")
    
    lines.append(f"  beta (temperature exp): {beta:.3f}")
    lines.append(f"  eta (density exp): {eta:.3f}")
    lines.append("")
    
    lines.append(f"DATA:")
    lines.append(f"  Number of rings: {len(df_result)}")
    lines.append(f"  Temperature range: {df_result['T'].min():.2f} - {df_result['T'].max():.2f} K")
    
    if 'n' in df_result.columns:
        lines.append(f"  Density range: {df_result['n'].min():.2e} - {df_result['n'].max():.2e} cm^-3")
    
    lines.append("")
    
    lines.append("PREDICTIONS:")
    lines.append(f"  v_pred range: {df_result['v_pred'].min():.3f} - {df_result['v_pred'].max():.3f} km/s")
    lines.append(f"  q_k range: {df_result['q_k'].min():.6f} - {df_result['q_k'].max():.6f}")
    lines.append("")
    
    if metrics is not None:
        lines.append("VALIDATION METRICS:")
        lines.append(f"  MAE: {metrics['mae']:.4f} km/s")
        lines.append(f"  RMSE: {metrics['rmse']:.4f} km/s")
        lines.append(f"  Max |residual|: {metrics['max_abs_residual']:.4f} km/s")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="SSZ-Rings: Segmented radiowave propagation predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fixed alpha with output
  ssz-rings --csv data/ring_data.csv --v0 12.5 --alpha 1.25 \\
            --out-table results.csv --out-report summary.txt
  
  # Fit alpha to observations
  ssz-rings --csv data/ring_data.csv --v0 12.5 --fit-alpha \\
            --out-table results.csv --out-report summary.txt
  
  # With frequency tracking
  ssz-rings --csv data/ring_data.csv --v0 12.5 --alpha 1.0 \\
            --nu-in 3.0e11 --out-table results_nu.csv

Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--csv',
        type=str,
        required=True,
        help="Path to CSV file with ring data (required columns: ring, T)"
    )
    
    parser.add_argument(
        '--v0',
        type=float,
        required=True,
        help="Initial velocity at first shell (km/s)"
    )
    
    # Alpha parameter
    alpha_group = parser.add_mutually_exclusive_group(required=True)
    alpha_group.add_argument(
        '--alpha',
        type=float,
        help="Fixed alpha parameter"
    )
    alpha_group.add_argument(
        '--fit-alpha',
        action='store_true',
        help="Fit alpha to minimize RMSE against v_obs column"
    )
    
    # Optional parameters
    parser.add_argument(
        '--beta',
        type=float,
        default=1.0,
        help="Temperature exponent (default: 1.0)"
    )
    
    parser.add_argument(
        '--eta',
        type=float,
        default=0.0,
        help="Density exponent (default: 0.0)"
    )
    
    parser.add_argument(
        '--nu-in',
        type=float,
        help="Input frequency (Hz) for frequency tracking"
    )
    
    # Output options
    parser.add_argument(
        '--out-table',
        type=str,
        help="Output CSV file for results table"
    )
    
    parser.add_argument(
        '--out-report',
        type=str,
        help="Output text file for summary report"
    )
    
    parser.add_argument(
        '--out-plot',
        type=str,
        help="Output PNG file for velocity plot (requires matplotlib)"
    )
    
    parser.add_argument(
        '--echo-all-md',
        action='store_true',
        help="After completion, print all Markdown files in repository to STDOUT"
    )
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading data from: {args.csv}")
    try:
        df = load_ring_data(args.csv)
    except Exception as e:
        print(f"ERROR: Failed to load CSV: {e}", file=sys.stderr)
        return 1
    
    rings = df['ring'].values
    T = df['T'].values
    n = df['n'].values if 'n' in df.columns else None
    v_obs = df['v_obs'].values if 'v_obs' in df.columns else None
    
    print(f"  Loaded {len(rings)} rings")
    
    # Determine alpha
    metrics = None
    
    if args.fit_alpha:
        if v_obs is None:
            print("ERROR: --fit-alpha requires 'v_obs' column in CSV", file=sys.stderr)
            return 1
        
        print("Fitting alpha parameter...")
        try:
            alpha_opt, metrics = fit_alpha(
                rings, T, args.v0, v_obs,
                n=n,
                beta=args.beta,
                eta=args.eta
            )
            print(f"  Optimal alpha = {alpha_opt:.6f}")
            print(f"  RMSE = {metrics['rmse']:.4f} km/s")
            alpha_use = alpha_opt
        except Exception as e:
            print(f"ERROR: Alpha fitting failed: {e}", file=sys.stderr)
            return 1
    else:
        alpha_use = args.alpha
        print(f"Using fixed alpha = {alpha_use:.6f}")
    
    # Predict velocity profile
    print("Computing velocity profile...")
    try:
        df_result = predict_velocity_profile(
            rings, T, args.v0,
            alpha=alpha_use,
            n=n,
            beta=args.beta,
            eta=args.eta
        )
    except Exception as e:
        print(f"ERROR: Velocity prediction failed: {e}", file=sys.stderr)
        return 1
    
    # Add observed velocities and residuals if available
    if v_obs is not None:
        df_result['v_obs'] = v_obs
        v_pred = df_result['v_pred'].values
        # Always compute full residuals dict with array for display
        residuals_full = compute_residuals(v_pred, v_obs)
        df_result['residual'] = residuals_full['residuals']
        # Update metrics if not already set from fitting
        if metrics is None:
            metrics = residuals_full
    
    # Frequency tracking if requested
    if args.nu_in is not None:
        print(f"Computing frequency track (nu_in = {args.nu_in:.3e} Hz)...")
        try:
            gamma_series = compute_cumulative_gamma(df_result['q_k'].values)
            nu_series = predict_frequency_track(args.nu_in, gamma_series)
            df_result['nu_out_Hz'] = nu_series
        except Exception as e:
            print(f"WARNING: Frequency tracking failed: {e}", file=sys.stderr)
    
    # Generate report
    report_text = generate_report(
        df_result, metrics,
        alpha_use, args.v0,
        args.beta, args.eta,
        args.fit_alpha
    )
    
    # Output results
    if args.out_table:
        print(f"Saving table to: {args.out_table}")
        try:
            save_results(df_result, args.out_table)
        except Exception as e:
            print(f"ERROR: Failed to save table: {e}", file=sys.stderr)
            return 1
    
    if args.out_report:
        print(f"Saving report to: {args.out_report}")
        try:
            save_report(report_text, args.out_report)
        except Exception as e:
            print(f"ERROR: Failed to save report: {e}", file=sys.stderr)
            return 1
    
    # Print report to console
    print()
    print(report_text)
    
    # Optional plot
    if args.out_plot:
        print(f"Generating plot: {args.out_plot}")
        try:
            from ssz.segwave.visuals import plot_velocity_comparison
            plot_velocity_comparison(
                rings,
                df_result['v_pred'].values,
                v_obs=v_obs,
                output_path=args.out_plot,
                title=f"Velocity Profile (alpha={alpha_use:.3f})"
            )
        except ImportError as e:
            print(f"WARNING: Plotting disabled: {e}", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Plotting failed: {e}", file=sys.stderr)
    
    print()
    print("[OK] SSZ-Rings completed successfully")
    
    # Optional: Echo all Markdown files in repository
    if args.echo_all_md:
        print("\n" + "="*100)
        print("ECHOING ALL MARKDOWN FILES IN REPOSITORY")
        print("="*100)
        try:
            import subprocess
            subprocess.run(
                [sys.executable, "-m", "tools.print_all_md", "--root", "."],
                check=False
            )
        except Exception as e:
            print(f"(echo-all-md failed: {e})", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
