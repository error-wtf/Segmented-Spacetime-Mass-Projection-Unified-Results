# Troubleshooting Guide

**Common issues and solutions for SSZ Projection Suite**

---

## 🔧 Installation Issues

### 1. Python Version Mismatch

**Problem:** `ModuleNotFoundError` or syntax errors

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.8+

# If not, install Python 3.10+
# Windows: Download from python.org
# Linux: sudo apt install python3.10
```

### 2. Missing Dependencies

**Problem:** `ImportError: No module named 'numpy'`

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or individually
pip install numpy pandas matplotlib astropy scipy
```

### 3. UTF-8 Encoding Errors (Windows)

**Problem:** `UnicodeEncodeError` when running tests

**Solution:**
```bash
# Set environment variable
set PYTHONIOENCODING=utf-8

# Or in PowerShell
$env:PYTHONIOENCODING = "utf-8"

# Or add to script:
import os
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
```

---

## 📊 Data Issues

### 4. Missing Data Files

**Problem:** `FileNotFoundError: data/real_data_full.csv`

**Solution:**
```bash
# Data files should be in repository
# If missing, check:
ls data/

# Download if needed (see DATA_FETCHING_README.md)
```

### 5. Planck Data Missing

**Problem:** Planck CMB tests failing

**Solution:**
```bash
# Auto-fetch Planck data (2GB)
python scripts/fetch_planck.py

# Or download manually from:
# https://pla.esac.esa.int/pla/
```

---

## 🧪 Test Issues

### 6. Pytest Crashes

**Problem:** `ValueError: I/O operation on closed file`

**Solution:**
```bash
# Don't use --disable-warnings flag
# WRONG: pytest --disable-warnings
# RIGHT:
pytest -s -v --tb=short
```

### 7. Tests Timeout

**Problem:** Tests hang or timeout

**Solution:**
```bash
# Increase timeout or run specific tests
pytest tests/test_specific.py -v

# Or run tests directly (no pytest needed)
python tests/test_ppn_exact.py
```

---

## 🌐 Cross-Platform Issues

### 8. Path Separators (Windows vs Linux)

**Problem:** File not found on different OS

**Solution:**
```python
# Use pathlib (already in code)
from pathlib import Path
path = Path('data') / 'file.csv'  # Works on all platforms
```

### 9. Line Endings (CRLF vs LF)

**Problem:** Git warnings about line endings

**Solution:**
```bash
# Configure git
git config --global core.autocrlf true  # Windows
git config --global core.autocrlf input # Linux/Mac
```

---

## 📈 Performance Issues

### 10. Slow Analysis

**Problem:** SSZ analysis takes too long

**Solution:**
```bash
# Use smaller dataset for testing
python scripts/ssz_analysis.py --sample 1000

# Or enable caching
python scripts/ssz_analysis.py --use-cache
```

### 11. Memory Issues

**Problem:** `MemoryError` on large datasets

**Solution:**
```python
# Process in chunks
# Code already handles this in most scripts

# Or increase available memory
# Close other applications
```

---

## 🔍 Analysis Issues

### 12. NaN or Inf Values

**Problem:** `RuntimeWarning: invalid value encountered`

**Solution:**
```python
# Check data quality
df.describe()
df.isnull().sum()

# Filter invalid values (already done in code)
df = df[np.isfinite(df['column'])]
```

### 13. Plotting Fails

**Problem:** `No display name and no $DISPLAY environment variable`

**Solution:**
```python
# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Or for Colab/Jupyter
%matplotlib inline
```

---

## 🐛 Known Issues

### 14. Subprocess Output Missing (Fixed)

**Status:** ✅ RESOLVED in v1.2

**Was:** Windows subprocess output not visible  
**Fix:** Explicit stdout binding

### 15. DataFrame Column Names

**Status:** ✅ RESOLVED in v1.2

**Was:** `KeyError: 'mass_msun'`  
**Fix:** Flexible column detection

---

## 📞 Getting Help

**If issue not listed here:**

1. Check existing documentation:
   - [INSTALL_README.md](INSTALL_README.md)
   - [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md)
   - [DATA_FETCHING_README.md](DATA_FETCHING_README.md)

2. Check test reports:
   - [TEST_SUITE_VERIFICATION.md](TEST_SUITE_VERIFICATION.md)

3. Search commit history:
   - [GIT_COMMIT_SUMMARY.md](GIT_COMMIT_SUMMARY.md)
   - Look for similar bug fixes

4. Create GitHub issue:
   - Include error message
   - Include OS and Python version
   - Include minimal reproduction steps

---

## 🔄 Quick Diagnostic

**Run this to diagnose common issues:**

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E 'numpy|pandas|astropy'

# Check data files
ls -lh data/

# Run quick test
python -c "import numpy; import pandas; print('OK')"

# Test UTF-8
python -c "print('φ π τ α β γ')"
```

---

**Last Updated:** 2025-10-20  
**Version:** 1.0

© 2025 Carmen Wrede & Lino Casu
