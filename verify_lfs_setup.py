#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Git LFS Setup in Current Repository

Checks if all large files are correctly tracked with Git LFS.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import subprocess
from pathlib import Path

def check_lfs_tracking():
    """Check which files are tracked by LFS"""
    try:
        result = subprocess.run(
            ["git", "lfs", "ls-files"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            lfs_files = [line.split()[-1] for line in result.stdout.strip().split('\n') if line]
            return lfs_files
        return []
    except:
        return []

def check_file_size(file_path):
    """Check file size in MB"""
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb
    return None

def main():
    print("\n" + "="*80)
    print("GIT LFS SETUP VERIFICATION")
    print("="*80)
    
    repo_root = Path.cwd()
    
    # Expected large files (>100 MB) that should be tracked with LFS
    large_files = {
        "models/cosmology/2025-10-17_gaia_ssz_real/ssz_field.parquet": 1373.31,
        "models/solar_system/2025-10-17_gaia_ssz_real/solar_ssz.json": 125.04,
        "data/interim/gaia/2025-10-17_gaia_ssz_real/gaia_clean.parquet": 757.11,
        "data/interim/gaia/2025-10-17_gaia_ssz_real/gaia_phase_space.parquet": 1169.17,
        "data/raw/gaia/2025-10-17_gaia_ssz_real/gaia_dr3_core.parquet": 78.83,
        "data/raw/gaia/2025-10-17_gaia_ssz_real/2025-10-17_gaia_ssz_real__part00_20251017T110038.parquet": 193.39,
        "data/raw/gaia/2025-10-17_gaia_ssz_real/test_run__part00_20251017T091550.parquet": 193.13,
        "data/raw/gaia/2025-10-17_gaia_ssz_real/gaia_quick.parquet": 0.32,
    }
    
    # Get LFS tracked files
    print("\n[*] Checking Git LFS tracked files...")
    lfs_tracked = check_lfs_tracking()
    print(f"   Found {len(lfs_tracked)} LFS tracked files")
    
    # Check each large file
    print("\n" + "="*80)
    print("LARGE FILES STATUS")
    print("="*80)
    
    all_ok = True
    for file_rel, expected_size in large_files.items():
        file_path = repo_root / file_rel
        actual_size = check_file_size(file_path)
        
        # Check if tracked by LFS
        is_lfs = any(file_rel in lfs_file for lfs_file in lfs_tracked)
        
        print(f"\n[FILE] {file_rel}")
        print(f"   Expected: {expected_size:.2f} MB")
        
        if actual_size is not None:
            print(f"   Actual:   {actual_size:.2f} MB")
            
            if is_lfs:
                print(f"   [OK] Tracked with Git LFS")
            else:
                print(f"   [ERROR] NOT tracked with Git LFS!")
                all_ok = False
        else:
            print(f"   [ERROR] File not found!")
            all_ok = False
    
    # Check .gitattributes
    print("\n" + "="*80)
    print("GIT LFS CONFIGURATION")
    print("="*80)
    
    gitattributes = repo_root / ".gitattributes"
    if gitattributes.exists():
        print("[OK] .gitattributes exists")
        with open(gitattributes, 'r', encoding='utf-8') as f:
            content = f.read()
            lfs_rules = [line for line in content.split('\n') if 'filter=lfs' in line]
            print(f"   {len(lfs_rules)} LFS tracking rules found:")
            for rule in lfs_rules:
                print(f"   - {rule.split()[0]}")
    else:
        print("[ERROR] .gitattributes not found!")
        all_ok = False
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if all_ok:
        print("[SUCCESS] All large files are correctly tracked with Git LFS!")
        print("[SUCCESS] Repository is ready to push to GitHub")
        return 0
    else:
        print("[ERROR] Some issues found!")
        print("   Please check the errors above")
        return 1

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
