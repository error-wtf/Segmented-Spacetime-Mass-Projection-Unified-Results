#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Full Pipeline - Timed Execution

Führt die komplette SSZ-Test-Suite mit Zeittracking aus.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import time
import subprocess
from datetime import datetime

# UTF-8 für Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

def main():
    print("="*80)
    print("🚀 SSZ FULL PIPELINE START")
    print("="*80)
    print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    start_time = time.time()
    
    # Pipeline ausführen
    result = subprocess.run(
        [sys.executable, "run_all_ssz_terminal.py"],
        stdout=sys.stdout,
        stderr=sys.stderr,
        encoding="utf-8",
        errors="replace"
    )
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    print("\n" + "="*80)
    if result.returncode == 0:
        print("✅ PIPELINE ABGESCHLOSSEN")
    else:
        print("⚠️  PIPELINE MIT FEHLERN BEENDET")
    print("="*80)
    print(f"⏱️  Laufzeit: {minutes} min {seconds} sec")
    print(f"⏰ Ende: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔢 Exit Code: {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
