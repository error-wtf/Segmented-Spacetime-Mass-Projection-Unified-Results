#!/bin/bash
# SSZ Repository - Complete Verification Script
# Run this on Linux after git pull to verify all fixes

echo "================================================================================"
echo "SSZ REPOSITORY - VERIFICATION SCRIPT"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Function to check
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $1"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}: $1"
        ((FAIL++))
    fi
}

echo "[1/10] Checking Git Status..."
git log --oneline -3 | grep -q "c39f4f0"
check "Latest commit c39f4f0 present"

echo ""
echo "[2/10] Checking install.sh..."
grep -q "pip install --quiet -r requirements.txt" install.sh
check "install.sh uses requirements.txt"

echo ""
echo "[3/10] Checking pyarrow installation..."
python3 -c "import pyarrow; print(f'pyarrow {pyarrow.__version__}')" 2>/dev/null
check "pyarrow is installed"

echo ""
echo "[4/10] Checking run_ssz_theory_validation.py..."
grep -q "if toe_score >= 10.0:" run_ssz_theory_validation.py
check "Theory validation has 10% threshold"

echo ""
echo "[5/10] Checking run_complete_test_suite.py..."
grep -q "CLI_TOOLS = {" run_complete_test_suite.py
check "Complete suite has CLI_TOOLS skip"

echo ""
echo "[6/10] Checking run_all_validations.py..."
grep -q "1200" run_all_validations.py
check "Master runner has custom timeouts"

echo ""
echo "[7/10] Testing Pipeline 3 (Theory Validation)..."
timeout 10 python3 run_ssz_theory_validation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}: Pipeline 3 exits 0"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}: Pipeline 3 exits non-zero"
    ((FAIL++))
fi

echo ""
echo "[8/10] Testing Pipeline 4 (Unified ToE)..."
timeout 10 python3 run_ssz_unified_validation.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}: Pipeline 4 exits 0"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}: Pipeline 4 exits non-zero"
    ((FAIL++))
fi

echo ""
echo "[9/10] Checking test files syntax..."
python3 -m py_compile tests/test_segwave_core.py 2>/dev/null
check "test_segwave_core.py has valid syntax"

python3 -m py_compile tests/cosmos/test_multi_body_sigma.py 2>/dev/null
check "test_multi_body_sigma.py has valid syntax"

echo ""
echo "[10/10] Checking documentation..."
if [ -f "FIX_ALL_PIPELINES.md" ]; then
    echo -e "${GREEN}✓ PASS${NC}: FIX_ALL_PIPELINES.md exists"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}: FIX_ALL_PIPELINES.md missing"
    ((FAIL++))
fi

echo ""
echo "================================================================================"
echo "VERIFICATION RESULTS"
echo "================================================================================"
echo ""
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "You can now run:"
    echo "  python3 run_all_validations.py"
    echo ""
    echo "Expected: 5/5 pipelines PASS (100%)"
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Please run: git pull origin main"
    echo "Then run this script again."
    exit 1
fi
