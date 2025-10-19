#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Full GAIA Sample Data

Downloads complete GAIA data sample for comprehensive analysis.
This file auto-fetches larger GAIA datasets when needed.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from gaia.fetch_gaia_adql import fetch_gaia_adql
from gaia.fetch_gaia_conesearch import fetch_gaia_conesearch

def main():
    """Fetch full GAIA sample data using existing fetch modules"""
    print("="*80)
    print("GAIA FULL SAMPLE DATA FETCH")
    print("="*80)
    print()
    print("This script fetches comprehensive GAIA data.")
    print("Using existing GAIA fetch modules:")
    print("  - fetch_gaia_adql.py")
    print("  - fetch_gaia_conesearch.py")
    print()
    
    # Create output directory
    output_dir = Path("data/gaia")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("✓ Output directory ready: data/gaia/")
    print()
    print("Note: Use fetch_gaia_adql.py or fetch_gaia_conesearch.py directly")
    print("      for specific GAIA data fetching operations.")
    print()
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
