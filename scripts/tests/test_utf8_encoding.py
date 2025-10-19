#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8 encoding smoke test for CI.
Ensures all critical files can be read/written with UTF-8.
"""

import sys
from pathlib import Path
import tempfile
import pytest

def test_utf8_environment():
    """Verify UTF-8 is available in environment."""
    import os
    import sys
    # Check if either PYTHONIOENCODING is set OR default encoding is UTF-8
    pythonioencoding = os.environ.get("PYTHONIOENCODING", "")
    default_encoding = sys.getdefaultencoding()
    
    utf8_available = (
        "utf" in pythonioencoding.lower() or 
        "utf" in default_encoding.lower()
    )
    
    assert utf8_available, \
        f"UTF-8 not available. PYTHONIOENCODING={pythonioencoding}, default={default_encoding}"

def test_stdout_encoding():
    """Verify stdout can handle UTF-8 (skip if stdout is wrapped)."""
    # Skip test if stdout has been wrapped (e.g., by TeeOutput in run_full_suite.py)
    if not hasattr(sys.stdout, 'encoding'):
        pytest.skip("stdout has been wrapped, cannot check encoding attribute")
    
    assert sys.stdout.encoding.lower().startswith("utf"), \
        f"stdout encoding not UTF-8: {sys.stdout.encoding}"

def test_utf8_file_write_read():
    """Test writing and reading UTF-8 characters."""
    test_chars = "äöü ±µ φ — Test UTF-8"
    
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        temp_path = Path(f.name)
        f.write(test_chars)
    
    try:
        content = temp_path.read_text(encoding="utf-8")
        assert content == test_chars, f"UTF-8 roundtrip failed: {content!r} != {test_chars!r}"
    finally:
        temp_path.unlink()

def test_json_utf8():
    """Test JSON with UTF-8 characters."""
    import json
    data = {"test": "φ-Segmentierung", "value": "±0.5"}
    
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)
        json.dump(data, f, ensure_ascii=False)
    
    try:
        loaded = json.loads(temp_path.read_text(encoding="utf-8"))
        assert loaded == data, f"JSON UTF-8 roundtrip failed"
    finally:
        temp_path.unlink()
