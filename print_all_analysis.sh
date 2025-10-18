#!/bin/bash
# SSZ Projection Suite - Complete Analysis Output Printer
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# This script prints ALL Markdown content in the repository:
# - Validation papers (papers/validation/)
# - Theory papers (docs/theory/)
# - Analysis reports (reports/)
# - Test summaries (reports/)
# - Root-level documentation
# - Any other MD outputs
#
# Usage:
#   chmod +x print_all_analysis.sh
#   ./print_all_analysis.sh

set -e

# Color codes
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}====================================================================================================${NC}"
echo -e "${CYAN}SSZ PROJECTION SUITE - COMPLETE MARKDOWN OUTPUT${NC}"
echo -e "${CYAN}====================================================================================================${NC}"
echo ""

# Section 1: Validation Papers (list only, no content)
echo -e "${YELLOW}[1/5] Validation Papers (papers/validation/)${NC}"
if [ -d "papers/validation" ]; then
    find papers/validation -name "*.md" | while read -r paper; do
        echo -e "${CYAN}  - $paper${NC}"
    done
    VALIDATION_COUNT=$(find papers/validation -name "*.md" | wc -l)
    echo -e "${GREEN}  Total: $VALIDATION_COUNT papers${NC}"
    echo ""
else
    echo -e "${YELLOW}  [SKIP] No validation papers found${NC}"
fi

# Section 2: Theory Papers (list only, no content)
echo -e "${YELLOW}[2/5] Theory Papers (docs/theory/)${NC}"
if [ -d "docs/theory" ]; then
    find docs/theory -name "*.md" | while read -r paper; do
        echo -e "${CYAN}  - $paper${NC}"
    done
    THEORY_COUNT=$(find docs/theory -name "*.md" | wc -l)
    echo -e "${GREEN}  Total: $THEORY_COUNT papers${NC}"
    echo ""
else
    echo -e "${YELLOW}  [SKIP] No theory papers found${NC}"
fi

# Section 3: Analysis Reports
echo -e "${YELLOW}[3/5] Analysis Reports (reports/)${NC}"
if [ -d "reports" ]; then
    ssz-print-md --root reports --order path
    echo ""
else
    echo -e "${YELLOW}  [SKIP] No reports found${NC}"
fi

# Section 4: Documentation
echo -e "${YELLOW}[4/5] Documentation (docs/*.md, root *.md)${NC}"
ssz-print-md --root docs --order path --include "*.md"
ssz-print-md --root . --include "*.md" --exclude-dirs papers docs reports tests scripts data
echo ""

# Section 5: Full Pipeline Outputs
echo -e "${YELLOW}[5/5] Pipeline Outputs (full_pipeline/)${NC}"
if [ -d "full_pipeline" ]; then
    ssz-print-md --root full_pipeline --order path
    echo ""
else
    echo -e "${YELLOW}  [SKIP] No pipeline outputs found (run python run_all_ssz_terminal.py first)${NC}"
fi

echo ""
echo -e "${CYAN}====================================================================================================${NC}"
echo -e "${GREEN}COMPLETE MARKDOWN OUTPUT FINISHED${NC}"
echo -e "${CYAN}====================================================================================================${NC}"
