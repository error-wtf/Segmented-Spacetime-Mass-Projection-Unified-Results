#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick UTF-8 Encoding Test
Verifies that subprocess calls can handle UTF-8 characters without crashes.
"""

import sys
import io

# Force UTF-8 for stdout/stderr
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import subprocess
from pathlib import Path

print("=" * 70)
print("UTF-8 Encoding Test")
print("=" * 70)

# Test special characters
test_chars = "µ (micro), — (em-dash), ± (plus-minus), € (euro), ° (degree)"
print(f"Test characters: {test_chars}")
print()

# Test subprocess with UTF-8
print("Testing subprocess.run with UTF-8 encoding...")
try:
    result = subprocess.run(
        [sys.executable, "-c", f"print('{test_chars}')"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(f"✅ Subprocess output: {result.stdout.strip()}")
    print(f"✅ Return code: {result.returncode}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print("Test complete!")
print("=" * 70)
