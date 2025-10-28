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
pip install --quiet numpy scipy matplotlib pandas pillow
echo "  ✓ Installed: numpy, scipy, matplotlib, pandas, pillow"

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
echo "  python run_ssz_validation.py           # SSZ vs GR (6 steps, ~2 min)"
echo "  python run_ssz_theory_validation.py    # Theory validation (10 steps, ~2 min)"
echo "  python run_ssz_unified_validation.py   # Unified ToE proof (11 steps, ~2 min)"
echo "  python run_complete_test_suite.py      # All tests (~18 scripts, ~5-10 min)"
echo ""
echo "Total: 4 pipelines, 45+ validations, 83.3% ToE consistency score"
echo ""
echo "Documentation:"
echo "  README.md                              # Overview"
echo "  SSZ_COMPLETE_FINAL_REPORT.md          # Complete 60+ page report"
echo "  TEST_SUITE_README.md                   # Testing guide"
echo ""
echo "Repository: https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results"
echo ""
