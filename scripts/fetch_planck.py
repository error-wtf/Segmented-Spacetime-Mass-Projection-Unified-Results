#!/usr/bin/env python3
"""
Fetch Planck CMB Power Spectrum Data

Downloads the Planck 2018 CMB TT power spectrum (2GB) if not already present.

Only runs if data/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt does NOT exist.
Never overwrites existing files!

Copyright © 2025
Carmen Wrede und Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import urllib.request
import os
from pathlib import Path
import sys

# UTF-8 setup for Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Planck Legacy Archive URL
PLANCK_URL = "https://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_PowerSpect_CMB-TT-full_R3.01.txt"

# Alternative mirror (if ESA server is down)
ALTERNATIVE_URL = "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/COM_PowerSpect_CMB-TT-full_R3.01.txt"

OUTPUT_DIR = Path("data/planck")
OUTPUT_FILE = OUTPUT_DIR / "COM_PowerSpect_CMB-TT-full_R3.01.txt"

def download_with_progress(url, output_path):
    """Download file with progress indicator"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {output_path}")
    print("")
    
    try:
        def report_progress(block_num, block_size, total_size):
            """Report download progress"""
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                mb_downloaded = downloaded / (1024**2)
                mb_total = total_size / (1024**2)
                bar_length = 50
                filled = int(bar_length * percent / 100)
                bar = '#' * filled + '.' * (bar_length - filled)
                print(f"\r[{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, output_path, reporthook=report_progress)
        print("\n")
        return True
    except Exception as e:
        print(f"\nError downloading: {e}")
        return False

def main():
    """Main fetch function"""
    
    # Check if file already exists
    if OUTPUT_FILE.exists():
        print(f"[OK] Planck data already exists: {OUTPUT_FILE}")
        print(f"  File size: {OUTPUT_FILE.stat().st_size / (1024**2):.1f} MB")
        print("")
        print("Skipping download (will not overwrite existing file).")
        return 0
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("PLANCK CMB POWER SPECTRUM - DATA FETCH")
    print("="*80)
    print("")
    print("Dataset: Planck 2018 Release 3")
    print("File: COM_PowerSpect_CMB-TT-full_R3.01.txt")
    print("Size: ~2 GB")
    print("Source: Planck Legacy Archive (ESA)")
    print("")
    print("This may take several minutes depending on your connection...")
    print("")
    
    # Try primary URL first
    print("Attempting download from ESA Planck Legacy Archive...")
    success = download_with_progress(PLANCK_URL, OUTPUT_FILE)
    
    # Try alternative if primary fails
    if not success:
        print("")
        print("Primary source failed. Trying alternative mirror...")
        success = download_with_progress(ALTERNATIVE_URL, OUTPUT_FILE)
    
    if success:
        file_size_mb = OUTPUT_FILE.stat().st_size / (1024**2)
        print("")
        print("="*80)
        print("[OK] Download complete!")
        print("="*80)
        print(f"File: {OUTPUT_FILE}")
        print(f"Size: {file_size_mb:.1f} MB")
        print("")
        print("The Planck data is now available for cosmological analysis.")
        print("")
        return 0
    else:
        print("")
        print("="*80)
        print("[FAILED] Download failed")
        print("="*80)
        print("")
        print("Both download sources failed. Possible reasons:")
        print("  - No internet connection")
        print("  - ESA/IPAC servers temporarily down")
        print("  - Firewall blocking download")
        print("")
        print("You can try again later with:")
        print(f"  python scripts/fetch_planck.py")
        print("")
        print("Or manually download from:")
        print(f"  {PLANCK_URL}")
        print("")
        return 1

if __name__ == "__main__":
    sys.exit(main())
