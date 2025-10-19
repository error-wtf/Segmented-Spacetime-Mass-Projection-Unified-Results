#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Full GAIA Sample Data

Simple wrapper to fetch GAIA data using existing modules.
This script provides an easy way to download GAIA data for analysis.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import subprocess
from pathlib import Path

# UTF-8 setup for Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

def main():
    """Fetch full GAIA sample using conesearch"""
    print("="*80)
    print("GAIA FULL SAMPLE DATA FETCH")
    print("="*80)
    print()
    
    # Create output directory
    output_dir = Path("data/gaia")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Output directory: {output_dir}")
    print()
    
    # Info about available scripts
    print("Available GAIA fetch tools:")
    print("  1. scripts/gaia/fetch_gaia_adql.py      - Custom ADQL queries")
    print("  2. scripts/gaia/fetch_gaia_conesearch.py - Cone search from config")
    print()
    
    # Check if scripts exist
    adql_script = Path("scripts/gaia/fetch_gaia_adql.py")
    cone_script = Path("scripts/gaia/fetch_gaia_conesearch.py")
    
    if not adql_script.exists():
        print(f"[ERROR] {adql_script} not found")
        return 1
    
    if not cone_script.exists():
        print(f"[ERROR] {cone_script} not found")
        return 1
    
    print("[OK] GAIA fetch modules available")
    print()
    print("Examples:")
    print(f"  python {adql_script} --adql 'SELECT TOP 1000 * FROM gaiaedr3.gaia_source' \\")
    print(f"         --out data/gaia/sample.parquet --cache data/cache \\")
    print(f"         --run-id test-run")
    print()
    print(f"  python {cone_script} --config config/gaia_cones.json \\")
    print(f"         --out data/gaia --cache data/cache --run-id test-run")
    print()
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
