#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest Configuration - UTF-8 Encoding (Cross-Platform: Windows & Linux)

This file configures pytest to use UTF-8 encoding, preventing
UnicodeEncodeError when tests print Greek letters (β, γ, α) and Unicode symbols (→, ₀).

Platform-specific behavior:
- Windows: Overrides cp1252 default encoding
- Linux: Reinforces existing UTF-8 default (usually not needed, but consistent)

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import sys
import os

# Set UTF-8 environment variables (cross-platform)
# On Windows: Critical for proper Unicode handling
# On Linux: Redundant but harmless (UTF-8 is already default)
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
os.environ['PYTHONUTF8'] = '1'  # Python 3.7+ UTF-8 mode

# Platform-specific stream reconfiguration
# Only needed on Windows where cp1252 is default
if sys.platform == 'win32':
    # Reconfigure stdout/stderr with UTF-8 (for pytest's capture system)
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')


def pytest_configure(config):
    """
    Pytest hook - called after command line options are parsed
    
    Ensures UTF-8 is used even if pytest reconfigures streams later.
    Cross-platform: Works on Windows and Linux.
    """
    # Set environment variables (works on both platforms)
    os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
    os.environ['PYTHONUTF8'] = '1'
