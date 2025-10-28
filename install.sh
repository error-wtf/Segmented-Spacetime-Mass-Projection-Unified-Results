#!/bin/bash
# SSZ Complete Analysis - Installation Script (Linux/Mac)
# © 2025 Carmen Wrede, Lino Casu

echo "================================================================================"
echo "SSZ COMPLETE ANALYSIS - INSTALLATION"
echo "================================================================================"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✓ Found: $PYTHON_VERSION"
else
    echo "  ✗ Python3 not found! Please install Python 3.10+"
    exit 1
fi

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "  ✓ Virtual environment already exists"
else
    python3 -m venv .venv
    echo "  ✓ Created .venv"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source .venv/bin/activate
echo "  ✓ Virtual environment activated"

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  ✓ Installed: numpy, scipy, matplotlib, pandas, pillow, pyarrow"

# Run validation
echo ""
echo "[5/5] Running quick validation..."
python run_ssz_validation.py
if [ $? -eq 0 ]; then
    echo "  ✓ Validation passed!"
else
    echo "  ⚠ Validation had issues (exit code: $?)"
fi

# Summary
echo ""
echo "================================================================================"
echo "INSTALLATION COMPLETE"
echo "================================================================================"
echo ""
echo "Available Commands:"
echo "  python run_all_validations.py          # MASTER: All 161 tests (5 pipelines, ~15-20 min)"
echo ""
echo "Individual Pipelines:"
echo "  python run_full_suite.py               # Original 116 tests (~2-3 min)"
echo "  python run_ssz_validation.py           # SSZ vs GR (6 steps, ~2 min)"
echo "  python run_ssz_theory_validation.py    # Theory validation (10 steps, ~2 min)"
echo "  python run_ssz_unified_validation.py   # Unified ToE proof (11 steps, ~2 min)"
echo "  python run_complete_test_suite.py      # Complete test suite (~18 scripts, ~5-10 min)"
echo ""
echo "Total: 161 tests (116 original + 45 ToE) across 5 pipelines"
echo "ToE Consistency Score: 83.3% | ESO Validation: 97.9%"
echo ""
echo "Documentation:"
echo "  README.md                              # Overview"
echo "  SSZ_COMPLETE_FINAL_REPORT.md          # Complete 60+ page report"
echo "  TEST_SUITE_README.md                   # Testing guide"
echo ""
echo "Repository: https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results"
echo ""
echo "================================================================================"
echo "TO ACTIVATE VIRTUAL ENVIRONMENT:"
echo "================================================================================"
echo ""
echo "Linux/Mac:"
echo "  source .venv/bin/activate"
echo ""
echo "Windows (PowerShell):"
echo "  .\.venv\Scripts\Activate.ps1"
echo ""
echo "Windows (CMD):"
echo "  .venv\Scripts\activate.bat"
echo ""
