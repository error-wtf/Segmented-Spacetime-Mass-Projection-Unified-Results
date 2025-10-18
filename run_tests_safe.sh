#!/usr/bin/env bash
# Safe Test Runner - Linux/macOS version
# For comprehensive SSZ tests that output lots of text

set -e

echo "================================================================================"
echo "SAFE TEST RUNNER"
echo "================================================================================"
echo ""

# Check if test path provided
if [ -z "$1" ]; then
    echo "ERROR: No test path provided"
    echo ""
    echo "Usage:"
    echo "  ./run_tests_safe.sh tests/test_ssz_real_data_comprehensive.py"
    echo "  ./run_tests_safe.sh scripts/tests/"
    echo "  ./run_tests_safe.sh tests/ -k \"SgrA\""
    exit 1
fi

TEST_PATH="$1"
shift  # Remove first argument

echo "Test Path: $TEST_PATH"
if [ $# -gt 0 ]; then
    echo "Extra Args: $@"
fi
echo ""
echo "Running pytest with safe flags..."
echo "  -s             (no output capture)"
echo "  --tb=short     (short tracebacks)"
echo "  -v             (verbose)"
echo ""
echo "================================================================================"
echo ""

# Run pytest with flags that prevent crashes:
# -s : Disable output capture (prevents I/O closed file error)
# --tb=short : Short tracebacks
# -v : Verbose output
python3 -X utf8 -m pytest "$TEST_PATH" -s --tb=short -v "$@"

EXIT_CODE=$?

echo ""
echo "================================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: All tests passed!"
else
    echo "FAILED: Tests failed with exit code $EXIT_CODE"
fi
echo "================================================================================"

exit $EXIT_CODE
