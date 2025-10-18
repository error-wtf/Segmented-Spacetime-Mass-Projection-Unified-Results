#!/usr/bin/env bash
# Clear Python cache and restart fresh

echo "================================================================================"
echo "CLEARING PYTHON CACHE"
echo "================================================================================"
echo ""

# 1. Kill all Python processes
echo "[1/4] Stopping all Python processes..."
pkill -9 python3 2>/dev/null || echo "  > No Python processes running"
echo ""

# 2. Delete __pycache__ directories
echo "[2/4] Deleting __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "  > Done"
echo ""

# 3. Delete .pyc files
echo "[3/4] Deleting .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "  > Done"
echo ""

# 4. Delete .pyo files
echo "[4/4] Deleting .pyo files..."
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "  > Done"
echo ""

echo "================================================================================"
echo "CACHE CLEARED!"
echo "================================================================================"
echo ""
echo "You can now run your scripts with fresh code:"
echo "  python3 run_full_suite.py"
echo "  python3 run_all_ssz_terminal.py"
echo ""
