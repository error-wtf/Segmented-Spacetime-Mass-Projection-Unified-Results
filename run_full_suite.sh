#!/bin/bash
# SSZ Projection Suite - Complete Test & Analysis Runner (Bash)
#
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# Usage:
#   ./run_full_suite.sh
#   ./run_full_suite.sh --quick
#   ./run_full_suite.sh --skip-slow-tests

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
QUICK=false
SKIP_SLOW=false
NO_ECHO=false

for arg in "$@"; do
    case $arg in
        --quick)
            QUICK=true
            shift
            ;;
        --skip-slow-tests)
            SKIP_SLOW=true
            shift
            ;;
        --no-echo-md)
            NO_ECHO=true
            shift
            ;;
        --help)
            echo "SSZ Projection Suite - Full Test Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick           Run only essential tests"
            echo "  --skip-slow-tests Skip slow/long-running tests"
            echo "  --no-echo-md      Skip MD echo at end"
            echo "  --help            Show this help"
            exit 0
            ;;
    esac
done

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Delegate to Python script (more maintainable)
ARGS=""
if [ "$QUICK" = true ]; then
    ARGS="$ARGS --quick"
fi
if [ "$SKIP_SLOW" = true ]; then
    ARGS="$ARGS --skip-slow-tests"
fi
if [ "$NO_ECHO" = true ]; then
    ARGS="$ARGS --no-echo-md"
fi

echo -e "${CYAN}Starting SSZ Full Suite Runner...${NC}"
python3 run_full_suite.py $ARGS
