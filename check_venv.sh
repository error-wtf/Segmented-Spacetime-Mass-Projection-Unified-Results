#!/bin/bash
# Check if running inside virtual environment
# Usage: source check_venv.sh

if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  WARNING: Not running in virtual environment!"
    echo ""
    echo "Python packages (pyarrow, etc.) are installed in .venv/"
    echo "but you're using system Python."
    echo ""
    echo "To activate the virtual environment:"
    echo "  source .venv/bin/activate"
    echo ""
    echo "Then run your command again."
    echo ""
    return 1 2>/dev/null || exit 1
else
    echo "✓ Virtual environment active: $VIRTUAL_ENV"
    return 0 2>/dev/null || exit 0
fi
