#!/usr/bin/env bash
# Quick runner for verbose tests with physical interpretations
# Linux/macOS version

set -e

echo "================================================================================"
echo "VERBOSE SSZ TESTS - With Physical Interpretations"
echo "================================================================================"
echo ""

# Parse arguments
if [ -z "$1" ]; then
    TEST_PATH="scripts/tests/"
    echo "No test path provided, using default: scripts/tests/"
else
    TEST_PATH="$1"
fi

echo "Test Path: $TEST_PATH"
echo ""
echo "Running pytest with verbose output and physical interpretations..."
echo "  -s            (show print output)"
echo "  -v            (verbose test names)"
echo "  --tb=short    (short tracebacks)"
echo ""
echo "================================================================================"
echo ""

# Run pytest with -s flag to show all print() outputs
python3 -X utf8 -m pytest "$TEST_PATH" -s -v --tb=short "${@:2}"

EXIT_CODE=$?

echo ""
echo "================================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: All tests passed with detailed output!"
else
    echo "FAILED: Some tests failed (exit code $EXIT_CODE)"
fi
echo "================================================================================"

exit $EXIT_CODE
