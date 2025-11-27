#!/usr/bin/env bash
# Clear Python cache and restart fresh

echo "================================================================================"
echo "CLEARING PYTHON CACHE"
echo "================================================================================"
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   CLEARING ALL PYTEST & PYTHON CACHES                        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "[1/5] Deleting .pytest_cache directories..."
find . -type d -name ".pytest_cache" -print -exec rm -rf {} + 2>/dev/null

echo ""
echo "[2/5] Stopping all Python processes..."
pkill -9 python3 2>/dev/null || echo "  > No Python processes running"

echo ""
echo "[3/5] Deleting __pycache__ directories..."
find . -type d -name "__pycache__" -print -exec rm -rf {} + 2>/dev/null

echo ""
echo "[4/5] Deleting .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null

echo ""
echo "[5/5] Deleting .pyo files and test-specific caches..."
find . -type f -name "*.pyo" -delete 2>/dev/null
rm -rf tests/.pytest_cache tests/cosmos/.pytest_cache scripts/tests/.pytest_cache 2>/dev/null

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   CACHE CLEARING COMPLETE                                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo "CACHE CLEARED!"
echo "================================================================================"
echo ""
echo "You can now run your scripts with fresh code:"
echo "  python3 run_full_suite.py"
echo "  python3 run_all_ssz_terminal.py"
echo ""
