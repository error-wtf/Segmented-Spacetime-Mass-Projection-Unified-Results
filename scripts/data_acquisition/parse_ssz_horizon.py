#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse SSZ Horizon Report to JSON Config

Extracts r_φ, A_H, κ_seg from SSZ horizon/Hawking test reports
and creates JSON config for hawking_proxy_fit.py

Usage:
    python parse_ssz_horizon.py --report horizon_hawking_proxy_report.md --out ssz_config.json

Input:
    - SSZ report (Markdown from test_horizon_hawking_predictions.py)
    
Output:
    - JSON config with r_phi_m, A_H_m2, kappa_seg_per_m

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import argparse
import json
import re
import sys
import os

# UTF-8 Setup (Windows compatibility)
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')


def main():
    """
    Parse SSZ horizon report to extract key parameters
    
    Looks for:
    - r_phi_est: Photon sphere radius (m)
    - A_H: Horizon area (m²)
    - kappa_seg: Surface gravity proxy (m⁻¹)
    """
    ap = argparse.ArgumentParser(
        description='Parse SSZ horizon report to JSON config'
    )
    ap.add_argument('--report', required=True,
                    help='Input SSZ report (Markdown)')
    ap.add_argument('--out', default='ssz_config.json',
                    help='Output JSON config (default: ssz_config.json)')
    args = ap.parse_args()

    # Read report
    print(f"Reading report: {args.report}")
    try:
        with open(args.report, 'r', encoding='utf-8') as f:
            txt = f.read()
    except FileNotFoundError:
        print(f"ERROR: Report file not found: {args.report}")
        print(f"Generate one with: python scripts/tests/test_horizon_hawking_predictions.py")
        sys.exit(1)

    # Helper function to extract numerical values
    def grab(pattern, description):
        """
        Extract numerical value from text using regex
        
        Parameters:
            pattern: Regex pattern with one capture group for the number
            description: Human-readable description for error messages
        
        Returns:
            Float value or None if not found
        """
        m = re.search(pattern, txt, re.IGNORECASE | re.MULTILINE)
        if m:
            try:
                value = float(m.group(1))
                print(f"  Found {description}: {value:.6e}")
                return value
            except (ValueError, IndexError):
                print(f"  WARNING: Could not parse {description}")
                return None
        else:
            print(f"  WARNING: {description} not found in report")
            return None

    # Extract parameters with multiple pattern variants
    print("\nExtracting parameters...")
    
    # r_phi (photon sphere radius)
    r_phi = grab(r'r_phi_est.*?:\s*([0-9.+eE-]+)\s*m', 'r_φ')
    if r_phi is None:
        r_phi = grab(r'r_φ.*?:\s*([0-9.+eE-]+)\s*m', 'r_φ (alt)')
    if r_phi is None:
        r_phi = grab(r'photon.*?radius.*?:\s*([0-9.+eE-]+)', 'photon radius')
    
    # A_H (horizon area)
    A_H = grab(r'A_H.*?:\s*([0-9.+eE-]+)\s*m\^?2', 'A_H')
    if A_H is None:
        A_H = grab(r'horizon.*?area.*?:\s*([0-9.+eE-]+)', 'horizon area')
    
    # kappa_seg (surface gravity proxy)
    kappa = grab(r'kappa_seg.*?:\s*([0-9.+eE-]+)', 'κ_seg')
    if kappa is None:
        kappa = grab(r'κ_seg.*?:\s*([0-9.+eE-]+)', 'κ_seg (alt)')
    if kappa is None:
        kappa = grab(r'surface.*?gravity.*?:\s*([0-9.+eE-]+)', 'surface gravity')

    # Try to extract source metadata
    source = None
    M_solar = None
    
    source_match = re.search(r'source.*?:\s*([^\n]+)', txt, re.IGNORECASE)
    if source_match:
        source = source_match.group(1).strip()
        print(f"  Found source: {source}")
    
    mass_match = re.search(r'M.*?solar.*?:\s*([0-9.+eE-]+)', txt, re.IGNORECASE)
    if mass_match:
        M_solar = float(mass_match.group(1))
        print(f"  Found M_solar: {M_solar:.6e}")

    # Build output dictionary
    out = {
        'r_phi_m': r_phi,
        'A_H_m2': A_H,
        'kappa_seg_per_m': kappa
    }
    
    # Add metadata if found
    if source:
        out['source'] = source
    if M_solar:
        out['M_solar'] = M_solar
    
    # Add extraction timestamp
    from datetime import datetime
    out['extracted_from'] = args.report
    out['extraction_time'] = datetime.now().isoformat()

    # Save to JSON
    print(f"\nWriting config: {args.out}")
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ Configuration extracted:")
    print("="*60)
    for key, val in out.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.6e}")
        else:
            print(f"  {key}: {val}")
    print("="*60)
    
    # Validation warnings
    if r_phi is None or A_H is None or kappa is None:
        print("\n⚠️  WARNING: Some parameters could not be extracted!")
        print("   The report may not be in the expected format.")
        print("   Check the report file and regex patterns.")
    else:
        print("\n✅ All parameters successfully extracted!")
        print(f"   Ready for: python scripts/analysis/hawking_proxy_fit.py --ssz {args.out}")


if __name__ == '__main__':
    main()
