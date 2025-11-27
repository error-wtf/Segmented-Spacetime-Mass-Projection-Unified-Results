#!/bin/bash
# Cleanup Script für SSZ Projekt (Linux/Mac)
# © 2025 Carmen Wrede & Lino Casu

echo "🧹 SSZ Project Cleanup"
echo "============================================================"

# 1. Clean Python cache
echo -e "\n[1/3] Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "  ✓ Cache cleaned"

# 2. Check for syntax errors
echo -e "\n[2/3] Checking for syntax errors..."
errors=0
total=0

for file in tests/*.py scripts/tests/*.py tests/cosmos/*.py; do
    if [ -f "$file" ]; then
        total=$((total + 1))
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo "  ✓ $(basename $file)"
        else
            echo "  ✗ $(basename $file)"
            errors=$((errors + 1))
        fi
    fi
done

if [ $errors -eq 0 ]; then
    echo "  ✓ All files passed syntax check"
else
    echo "  ✗ $errors files have syntax errors"
fi

# 3. Summary
echo -e "\n[3/3] Summary"
echo "============================================================"
echo "  Cache: Cleaned"
echo "  Syntax: $((total - errors))/$total files OK"

if [ $errors -eq 0 ]; then
    echo -e "\n✅ Cleanup complete - Ready for testing!"
else
    echo -e "\n⚠️  Cleanup complete - Fix syntax errors before testing"
fi

echo "============================================================"
