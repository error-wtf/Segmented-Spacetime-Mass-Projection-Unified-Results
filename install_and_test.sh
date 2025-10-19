#!/bin/bash
# SSZ Projection Suite - Install + Full Test Suite Runner
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# This is a convenience wrapper that:
# 1. Runs the standard installation
# 2. Automatically runs the complete test suite
#
# Usage:
#   chmod +x install_and_test.sh
#   ./install_and_test.sh          # Full suite (~10-15 min)
#   ./install_and_test.sh --quick  # Quick suite (~2 min)

set -e

# Parse arguments
QUICK_MODE=false
for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --help)
            echo "SSZ Install + Test Suite Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick    Run quick test suite (~2 min)"
            echo "  --help     Show this help message"
            exit 0
            ;;
    esac
done

# Color codes
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}====================================================================================================${NC}"
echo -e "${CYAN}SSZ PROJECTION SUITE - INSTALL + TEST WORKFLOW${NC}"
echo -e "${CYAN}====================================================================================================${NC}"
echo ""

# Warning explanations
echo -e "${CYAN}[INFO] ABOUT WARNINGS DURING TESTS${NC}"
echo "----------------------------------------------------------------------------------------------------"
echo "Some tests may show warnings. This is NORMAL and EXPECTED:"
echo ""
echo "  * 'Insufficient data for Hawking spectrum fit'"
echo "    -> Expected! Data needs thermal multi-frequency at same radius"
echo "    -> Test still PASSES with informative warning"
echo ""
echo "  * 'Insufficient data for kappa_seg test'"
echo "    -> Expected! Needs very tight radial sampling (r < 3 r_s)"
echo "    -> Test still PASSES with informative warning"
echo ""
echo "  * DeprecationWarning from packages"
echo "    -> From dependencies (numpy, scipy, etc.) - ignore safely"
echo ""
echo "These warnings do NOT mean tests failed. Check for '[SUCCESS]' or '[FAILED]' in output."
echo "===================================================================================================="
echo ""

# Step 1: Run standard installation
echo -e "${YELLOW}STEP 1: Running installation...${NC}"
./install.sh

# Check if installation succeeded
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR] Installation failed${NC}"
    exit 1
fi

# Step 2: Run full test suite
echo ""
echo -e "${CYAN}====================================================================================================${NC}"
echo -e "${CYAN}STEP 2: Running full test suite...${NC}"
echo -e "${CYAN}====================================================================================================${NC}"
echo ""

if [ "$QUICK_MODE" = true ]; then
    echo -e "${YELLOW}Mode: Quick suite (~2 min)${NC}"
    python3 run_full_suite.py --quick
else
    echo -e "${YELLOW}Mode: Full suite (~10-15 min)${NC}"
    python3 run_full_suite.py
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${CYAN}====================================================================================================${NC}"
    echo -e "\033[0;32m[SUCCESS] Installation and all tests passed!${NC}"
    echo -e "${CYAN}====================================================================================================${NC}"
    exit 0
else
    echo ""
    echo -e "${CYAN}====================================================================================================${NC}"
    echo -e "${YELLOW}[WARNING] Some tests failed (see output above)${NC}"
    echo -e "${CYAN}====================================================================================================${NC}"
    exit 1
fi
