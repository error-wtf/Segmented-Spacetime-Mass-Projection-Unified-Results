#!/bin/bash
# -*- coding: utf-8 -*-
#
# Quick Test Runner for Paper Export Tools
#
# Tests the complete paper export pipeline:
# - Plot helpers
# - Caption catalog
# - I/O utilities
# - Figure orchestrator
# - Manifest generation
#
# Usage: ./test_paper_exports.sh
#
# © 2025 Carmen Wrede, Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4

set -e  # Exit on error

echo ""
echo "================================================================================"
echo "SSZ Paper Export Tools - TEST RUNNER"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 not found!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
echo ""

# Check dependencies
echo -e "${YELLOW}[2/5] Checking dependencies...${NC}"
MISSING=()
for module in matplotlib numpy; do
    if ! python3 -c "import $module" 2>/dev/null; then
        MISSING+=($module)
        echo -e "${RED}✗ Missing: $module${NC}"
    else
        echo -e "${GREEN}✓ Found: $module${NC}"
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Installing missing packages...${NC}"
    pip3 install "${MISSING[@]}"
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Installation failed!${NC}"
        exit 1
    fi
fi
echo ""

# Clean old outputs
echo -e "${YELLOW}[3/5] Cleaning old test outputs...${NC}"
if [ -d "reports/figures/demo" ]; then
    rm -rf "reports/figures/demo"
    echo -e "${GREEN}✓ Removed old demo figures${NC}"
fi
if [ -f "reports/DEMO_MANIFEST.json" ]; then
    rm -f "reports/DEMO_MANIFEST.json"
    echo -e "${GREEN}✓ Removed old demo manifest${NC}"
fi
if [ -f "reports/figures/FIGURE_INDEX.md" ]; then
    rm -f "reports/figures/FIGURE_INDEX.md"
    echo -e "${GREEN}✓ Removed old figure index${NC}"
fi
echo ""

# Run demo
echo -e "${YELLOW}[4/5] Running demo script...${NC}"
echo ""
python3 demo_paper_exports.py
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Demo failed!${NC}"
    exit 1
fi
echo ""

# Verify outputs
echo -e "${YELLOW}[5/5] Verifying outputs...${NC}"

declare -A CHECKS=(
    ["reports/figures/demo/fig_demo_line.png"]="Line plot PNG"
    ["reports/figures/demo/fig_demo_line.svg"]="Line plot SVG"
    ["reports/figures/demo/fig_demo_scatter.png"]="Scatter plot PNG"
    ["reports/figures/demo/fig_demo_scatter.svg"]="Scatter plot SVG"
    ["reports/figures/demo/fig_demo_heatmap.png"]="Heatmap PNG"
    ["reports/figures/FIGURE_INDEX.md"]="Figure index"
    ["reports/DEMO_MANIFEST.json"]="Demo manifest"
)

ALL_GOOD=true
for path in "${!CHECKS[@]}"; do
    if [ -f "$path" ]; then
        size=$(stat -f%z "$path" 2>/dev/null || stat -c%s "$path" 2>/dev/null)
        echo -e "${GREEN}✓ ${CHECKS[$path]}: $path ($size bytes)${NC}"
    else
        echo -e "${RED}✗ MISSING: ${CHECKS[$path]}: $path${NC}"
        ALL_GOOD=false
    fi
done
echo ""

# Final verdict
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  1. View figures: ls -lh reports/figures/demo/"
    echo "  2. Check index: cat reports/figures/FIGURE_INDEX.md"
    echo "  3. Read guide: cat QUICK_START_PAPER_EXPORTS.md"
    echo "  4. Integrate: Follow PAPER_EXPORTS_README.md"
    echo ""
    exit 0
else
    echo -e "${RED}================================================================================${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED!${NC}"
    echo -e "${RED}================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  - Check Python version (need 3.7+)"
    echo "  - Verify matplotlib installation: pip3 install matplotlib"
    echo "  - Run from project root directory"
    echo "  - Check permissions on reports/ folder"
    echo ""
    exit 1
fi
