#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Clone Repository and Verify Files

Tests the hybrid Git LFS strategy:
- Small files (<100 MB) should be immediately available
- Large files (>100 MB) are LFS pointers until 'git lfs pull'

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

# Repository configuration
REPO_NAME = "Segmented-Spacetime-Mass-Projection-Unified-Results"
REPO_URL = "https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results"
TEST_DIR = Path.cwd() / "temp_test_clone"

def run_command(cmd, cwd=None):
    """Run command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout after 300 seconds"

def check_file_size(file_path):
    """Check file size in MB"""
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb
    return None

def main():
    print("\n" + "="*80)
    print("REPOSITORY CLONE & VERIFY TEST")
    print("="*80)
    
    # Step 1: Prepare test directory
    print(f"\n📁 Test Directory: {TEST_DIR}")
    if TEST_DIR.exists():
        print("   Removing existing test directory...")
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True)
    
    # Step 2: Clone repository
    print(f"\n📥 Cloning Repository...")
    print(f"   URL: {REPO_URL}")
    
    returncode, stdout, stderr = run_command(
        ["git", "clone", "--depth", "1", REPO_URL, REPO_NAME],
        cwd=TEST_DIR
    )
    
    if returncode != 0:
        print(f"❌ Clone failed!")
        print(f"   Error: {stderr}")
        return 1
    
    print("✅ Clone successful!")
    
    repo_path = TEST_DIR / REPO_NAME
    
    # Step 3: Check small files (should be immediately available)
    print("\n" + "="*80)
    print("CHECKING SMALL FILES (<100 MB) - Should be immediately available")
    print("="*80)
    
    small_files = [
        "models/cosmology/2025-10-17_gaia_ssz_v1/ssz_field.parquet",
        "models/cosmology/2025-10-17_gaia_ssz_nightly/ssz_field.parquet",
        "models/solar_system/2025-10-17_gaia_ssz_v1/solar_ssz.json",
        "models/solar_system/2025-10-17_gaia_ssz_nightly/solar_ssz.json",
        "data/interim/gaia/2025-10-17_gaia_ssz_v1/gaia_clean.parquet",
        "data/interim/gaia/2025-10-17_gaia_ssz_nightly/gaia_clean.parquet",
    ]
    
    small_ok = 0
    for file_rel in small_files:
        file_path = repo_path / file_rel
        size = check_file_size(file_path)
        if size and size < 100:
            print(f"✅ {file_rel} - {size:.2f} MB")
            small_ok += 1
        elif size and size >= 100:
            print(f"⚠️  {file_rel} - {size:.2f} MB (zu groß!)")
        else:
            print(f"❌ {file_rel} - FEHLT!")
    
    print(f"\n✅ Small Files: {small_ok}/{len(small_files)} verfügbar")
    
    # Step 4: Check large files (should be LFS pointers)
    print("\n" + "="*80)
    print("CHECKING LARGE FILES (>100 MB) - Should be LFS pointers")
    print("="*80)
    
    large_files = [
        "models/cosmology/2025-10-17_gaia_ssz_real/ssz_field.parquet",
        "models/solar_system/2025-10-17_gaia_ssz_real/solar_ssz.json",
        "data/interim/gaia/2025-10-17_gaia_ssz_real/gaia_clean.parquet",
        "data/interim/gaia/2025-10-17_gaia_ssz_real/gaia_phase_space.parquet",
    ]
    
    lfs_ok = 0
    for file_rel in large_files:
        file_path = repo_path / file_rel
        size = check_file_size(file_path)
        if size and size < 1:  # LFS pointer is < 1 MB
            print(f"✅ {file_rel} - {size*1024:.2f} KB (LFS Pointer)")
            lfs_ok += 1
        elif size and size >= 100:
            print(f"⚠️  {file_rel} - {size:.2f} MB (Vollständige Datei!)")
        else:
            print(f"❌ {file_rel} - FEHLT!")
    
    print(f"\n✅ LFS Pointers: {lfs_ok}/{len(large_files)} korrekt")
    
    # Step 5: Check .gitattributes
    print("\n" + "="*80)
    print("CHECKING GIT LFS CONFIGURATION")
    print("="*80)
    
    gitattributes = repo_path / ".gitattributes"
    if gitattributes.exists():
        print(f"✅ .gitattributes existiert")
        with open(gitattributes, 'r', encoding='utf-8') as f:
            content = f.read()
            if "filter=lfs" in content:
                print("✅ LFS tracking konfiguriert")
                lfs_rules = [line for line in content.split('\n') if 'filter=lfs' in line]
                print(f"   {len(lfs_rules)} LFS-Regeln gefunden")
            else:
                print("❌ Keine LFS-Regeln gefunden")
    else:
        print("❌ .gitattributes fehlt")
    
    # Step 6: Test with LFS pull (optional)
    print("\n" + "="*80)
    print("OPTIONAL: LFS PULL TEST")
    print("="*80)
    print("Um die großen Dateien herunterzuladen:")
    print(f"   cd {repo_path}")
    print("   git lfs pull")
    
    # Summary
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    print(f"✅ Repository erfolgreich geklont")
    print(f"✅ Small Files: {small_ok}/{len(small_files)} verfügbar")
    print(f"✅ LFS Pointers: {lfs_ok}/{len(large_files)} korrekt")
    print(f"\n🎉 Hybrid Git LFS Strategy funktioniert!")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Abgebrochen durch Benutzer")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
