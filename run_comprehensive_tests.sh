#!/usr/bin/env bash
# Runner for Comprehensive SSZ Real Data Tests
# Linux/macOS version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================================"
echo "SEGMENTED SPACETIME - COMPREHENSIVE TEST RUNNER"
echo "================================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Python: $(python3 --version)"
echo "================================================================================"
echo ""

# Parse arguments
VERBOSE=""
HTML=""
OBJECT=""
RADIUS=""
OUTPUT="test_results"

while [[ $# -gt 0 ]]; do
    case $1 in
        --html)
            HTML="--html"
            shift
            ;;
        --object)
            OBJECT="$2"
            shift 2
            ;;
        --radius)
            RADIUS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--html] [--object OBJ] [--radius R] [--output DIR] [-v]"
            exit 1
            ;;
    esac
done

# Build pytest command
CMD="python3 -X utf8 -m pytest tests/test_ssz_real_data_comprehensive.py"

# Add filters
if [ -n "$OBJECT" ]; then
    CMD="$CMD -k $OBJECT"
    echo "→ Filtering for object: $OBJECT"
fi

if [ -n "$RADIUS" ]; then
    CMD="$CMD -k $RADIUS"
    echo "→ Filtering for radius: ${RADIUS}r_s"
fi

# Add verbosity
if [ -n "$VERBOSE" ]; then
    CMD="$CMD -v -s"
    echo "→ Verbose mode enabled"
else
    CMD="$CMD -v"
fi

# Add HTML report
if [ -n "$HTML" ]; then
    mkdir -p "$OUTPUT"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    HTML_PATH="$OUTPUT/test_report_$TIMESTAMP.html"
    CMD="$CMD --html=$HTML_PATH --self-contained-html"
    echo "→ HTML report will be saved to: $HTML_PATH"
fi

# Add JUnit XML
mkdir -p "$OUTPUT"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
JUNIT_PATH="$OUTPUT/junit_$TIMESTAMP.xml"
CMD="$CMD --junitxml=$JUNIT_PATH"
echo "→ JUnit XML will be saved to: $JUNIT_PATH"

echo ""
echo "================================================================================"
echo "RUNNING TESTS"
echo "================================================================================"
echo "Command: $CMD"
echo "================================================================================"
echo ""

# Run tests
eval $CMD
EXIT_CODE=$?

echo ""
echo "================================================================================"
echo "TEST EXECUTION COMPLETE"
echo "================================================================================"
echo "Exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "Status: ✓ ALL TESTS PASSED"
else
    echo "Status: ✗ SOME TESTS FAILED"
fi

if [ -n "$HTML" ] && [ -f "$HTML_PATH" ]; then
    echo ""
    echo "→ HTML report: $HTML_PATH"
fi

echo "→ JUnit XML: $JUNIT_PATH"
echo "================================================================================"
echo ""

exit $EXIT_CODE
