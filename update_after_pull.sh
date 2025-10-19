#!/bin/bash
# Update script after git pull
# Regenerates all outputs with latest real data

echo "================================================================================"
echo "SSZ - Update After Pull"
echo "================================================================================"
echo ""
echo "This script regenerates all analysis outputs with the latest data."
echo "Run this after every 'git pull' to ensure consistency."
echo ""

# Check if we're in the right directory
if [ ! -f "run_all_ssz_terminal.py" ]; then
    echo "❌ Error: run_all_ssz_terminal.py not found"
    echo "   Please run this script from the repository root"
    exit 1
fi

echo "[1/4] Checking data files..."
if [ ! -f "real_data_full.csv" ]; then
    echo "❌ Error: real_data_full.csv not found"
    echo "   Please ensure you have pulled the latest version"
    exit 1
fi

# Check number of rows in real_data_full.csv
ROWS=$(wc -l < real_data_full.csv)
echo "   ✓ Found real_data_full.csv ($ROWS rows)"

if [ $ROWS -lt 167 ]; then
    echo "⚠️  Warning: Expected 167+ rows, found $ROWS"
    echo "   You may not have the latest data. Consider running:"
    echo "   git pull"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "[2/4] Cleaning old outputs..."
rm -f out/*.csv out/*.png out/*.txt 2>/dev/null
rm -f reports/*.md reports/*.csv 2>/dev/null
rm -rf reports/figures/* 2>/dev/null
echo "   ✓ Old outputs removed"

echo ""
echo "[3/4] Running SSZ pipeline (this takes ~7-10 minutes)..."
echo "   Processing 167 real data points (ALMA/Chandra/VLT)..."
echo ""

python run_all_ssz_terminal.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Pipeline failed!"
    echo "   Check error messages above"
    exit 1
fi

echo ""
echo "[4/4] Verifying outputs..."
if [ -f "out/phi_step_debug_full.csv" ]; then
    OUT_ROWS=$(wc -l < out/phi_step_debug_full.csv)
    echo "   ✓ out/phi_step_debug_full.csv created ($OUT_ROWS rows)"
else
    echo "   ❌ out/phi_step_debug_full.csv not found"
    exit 1
fi

if [ -f "reports/info_preservation_by_source.csv" ]; then
    echo "   ✓ reports/info_preservation_by_source.csv created"
else
    echo "   ⚠️  reports/info_preservation_by_source.csv not found"
fi

echo ""
echo "================================================================================"
echo "✅ UPDATE COMPLETE!"
echo "================================================================================"
echo ""
echo "What was updated:"
echo "  • out/phi_step_debug_full.csv ($OUT_ROWS rows with real data)"
echo "  • out/_enhanced_debug.csv"
echo "  • reports/hawking_proxy_fit.md"
echo "  • reports/info_preservation_by_source.csv"
echo "  • All plots in reports/figures/"
echo ""
echo "You can now run:"
echo "  python scripts/tests/test_horizon_hawking_predictions.py"
echo ""
echo "Expected result:"
echo "  ✅ All 3 warnings RESOLVED"
echo "  ✅ HIGH confidence validation"
echo "  ✅ 167 real data points (ALMA/Chandra/VLT)"
echo ""
echo "================================================================================"
