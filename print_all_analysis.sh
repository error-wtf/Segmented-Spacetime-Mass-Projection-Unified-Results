#!/bin/bash
# SSZ Projection Suite - Test Results & Analysis Output Printer
# 
# Copyright 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# This script prints ONLY test results, summaries, and analysis outputs:
# - Test summary (ci/test_summary.html)
# - Analysis reports (reports/)
# - Pipeline outputs (full_pipeline/)
#
# Documentation/Papers are available but not printed (to avoid terminal spam)
#
# Usage:
#   ./print_all_analysis.sh

# Colors
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}====================================================================================================${NC}"
echo -e "${CYAN}SSZ PROJECTION SUITE - TEST RESULTS & ANALYSIS OUTPUT${NC}"
echo -e "${CYAN}====================================================================================================${NC}"
echo ""

# Info: Available documentation (not printed)
echo -e "${YELLOW}Available Documentation (not printed to avoid spam):${NC}"
echo -e "${CYAN}  - Validation Papers: papers/validation/ (11 papers)${NC}"
echo -e "${CYAN}  - Theory Papers: docs/theory/ (21 papers)${NC}"
echo -e "${CYAN}  - README: README.md${NC}"
echo ""

# Section 1: Test Summary
echo -e "${YELLOW}[1/3] Test Summary (ci/test_summary.html)${NC}"
if [ -f "ci/test_summary.html" ]; then
    echo -e "${GREEN}  Test summary available: ci/test_summary.html${NC}"
    echo -e "${CYAN}  Open in browser to view complete test results${NC}"
    echo ""
else
    echo -e "${CYAN}  [INFO] No test summary yet (run tests with install.sh or pytest)${NC}"
    echo ""
fi

# Section 2: Analysis Reports
echo -e "${YELLOW}[2/3] Analysis Reports (reports/)${NC}"
if [ -d "reports" ]; then
    ssz-print-md --root reports --order path
    echo ""
else
    echo -e "${CYAN}  [INFO] No reports yet (run python run_all_ssz_terminal.py to generate)${NC}"
    echo ""
fi

# Section 3: Full Pipeline Outputs
echo -e "${YELLOW}[3/3] Pipeline Outputs (full_pipeline/)${NC}"
if [ -d "full_pipeline" ]; then
    ssz-print-md --root full_pipeline --order path
    echo ""
else
    echo -e "${CYAN}  [INFO] No pipeline outputs yet (run python run_all_ssz_terminal.py to generate)${NC}"
    echo ""
fi

echo ""
echo -e "${CYAN}====================================================================================================${NC}"
echo -e "${GREEN}TEST RESULTS & ANALYSIS OUTPUT COMPLETE${NC}"
echo -e "${CYAN}====================================================================================================${NC}"
