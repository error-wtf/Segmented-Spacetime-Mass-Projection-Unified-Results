#!/bin/bash
# SSZ Projection Suite - Linux/macOS Installation Script
# 
# Copyright © 2025
# Carmen Wrede und Lino Casu
# Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
#
# Usage:
#   ./install.sh              # Full install
#   ./install.sh --skip-tests # Skip test suite
#   ./install.sh --dev-mode   # Install in editable mode
#   ./install.sh --dry-run    # Show what would be done

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_TESTS=false
DEV_MODE=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --dev-mode)
            DEV_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "SSZ Projection Suite Installer"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-tests    Skip running test suite"
            echo "  --dev-mode      Install in editable mode (pip install -e .)"
            echo "  --dry-run       Show what would be done without executing"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            ;;
    esac
done

# Helper function for colored output
print_header() {
    echo -e "${CYAN}$(printf '=%.0s' {1..100})${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..100})${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}$1${NC}"
}

print_success() {
    echo -e "  ${GREEN}$1${NC}"
}

print_error() {
    echo -e "  ${RED}$1${NC}"
}

print_info() {
    echo -e "  ${CYAN}$1${NC}"
}

print_warn() {
    echo -e "  ${YELLOW}$1${NC}"
}

# Start installation
print_header "SSZ PROJECTION SUITE - LINUX/MACOS INSTALLER"

# Step 1: Check Python
print_step "[1/8] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    print_error "ERROR: Python not found. Install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "Found: $PYTHON_VERSION"

# Check version >= 3.8
VERSION_CHECK=$($PYTHON_CMD -c "import sys; print(1 if sys.version_info >= (3, 8) else 0)")
if [ "$VERSION_CHECK" != "1" ]; then
    print_error "ERROR: Python 3.8+ required"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
print_step "[2/8] Setting up virtual environment..."
VENV_PATH=".venv"

if [ -d "$VENV_PATH" ]; then
    print_success "Virtual environment already exists"
else
    if [ "$DRY_RUN" = false ]; then
        $PYTHON_CMD -m venv "$VENV_PATH"
        print_success "Created: $VENV_PATH"
    else
        print_info "[DRY-RUN] Would create: $VENV_PATH"
    fi
fi

# Step 3: Activate venv
echo ""
print_step "[3/8] Activating virtual environment..."
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

if [ -f "$ACTIVATE_SCRIPT" ]; then
    if [ "$DRY_RUN" = false ]; then
        source "$ACTIVATE_SCRIPT"
        print_success "Activated: $VENV_PATH"
    else
        print_info "[DRY-RUN] Would activate: $VENV_PATH"
    fi
else
    print_error "ERROR: Activation script not found"
    exit 1
fi

# Step 4: Upgrade pip
echo ""
print_step "[4/8] Upgrading pip, setuptools, wheel..."
if [ "$DRY_RUN" = false ]; then
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    print_success "Upgraded core packages"
else
    print_info "[DRY-RUN] Would upgrade: pip, setuptools, wheel"
fi

# Step 5: Install dependencies
echo ""
print_step "[5/8] Installing dependencies..."

if [ -f "requirements.txt" ]; then
    print_info "Found: requirements.txt"
    if [ "$DRY_RUN" = false ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        print_success "Installed from requirements.txt"
    else
        print_info "[DRY-RUN] Would install from requirements.txt"
    fi
elif [ -f "pyproject.toml" ]; then
    print_info "Found: pyproject.toml"
    if [ "$DRY_RUN" = false ]; then
        # Install common scientific packages
        $PYTHON_CMD -m pip install numpy scipy pandas matplotlib astropy pyyaml
        print_success "Installed core scientific packages"
    else
        print_info "[DRY-RUN] Would install core packages"
    fi
else
    print_warn "WARNING: No requirements.txt or pyproject.toml found"
fi

# Step 6: Install package
echo ""
print_step "[6/8] Installing SSZ Suite package..."
if [ "$DEV_MODE" = true ]; then
    print_info "Mode: Editable (development)"
    if [ "$DRY_RUN" = false ]; then
        $PYTHON_CMD -m pip install -e .
        print_success "Installed in editable mode"
    else
        print_info "[DRY-RUN] Would install: pip install -e ."
    fi
else
    print_info "Mode: Standard"
    if [ "$DRY_RUN" = false ]; then
        $PYTHON_CMD -m pip install .
        print_success "Installed package"
    else
        print_info "[DRY-RUN] Would install: pip install ."
    fi
fi

# Step 7: Run tests
if [ "$SKIP_TESTS" = false ]; then
    echo ""
    print_step "[7/8] Running test suite..."
    if [ "$DRY_RUN" = false ]; then
        if $PYTHON_CMD -m pytest tests/ -v --tb=short 2>&1; then
            print_success "All tests passed"
        else
            print_warn "WARNING: Some tests failed (non-fatal)"
        fi
    else
        print_info "[DRY-RUN] Would run: pytest tests/"
    fi
else
    echo ""
    print_step "[7/8] Skipping tests (--skip-tests flag)"
fi

# Step 8: Verify installation
echo ""
print_step "[8/8] Verifying installation..."
if [ "$DRY_RUN" = false ]; then
    COMMANDS=("ssz-rings --help" "ssz-print-md --help")
    for cmd in "${COMMANDS[@]}"; do
        CMD_NAME=$(echo $cmd | cut -d' ' -f1)
        print_info "Checking: $CMD_NAME"
        if eval $cmd > /dev/null 2>&1; then
            print_success "  [OK] $CMD_NAME"
        else
            print_warn "  [WARN] $CMD_NAME not available"
        fi
    done
else
    print_info "[DRY-RUN] Would verify commands"
fi

# Summary
echo ""
print_header "INSTALLATION COMPLETE"
echo ""
echo -e "${YELLOW}Quick Start:${NC}"
echo -e "${NC}  1. Activate venv: source .venv/bin/activate${NC}"
echo -e "${NC}  2. Run example:   ssz-rings --csv data/observations/G79_29+0_46_CO_NH3_rings.csv --v0 12.5 --fit-alpha${NC}"
echo -e "${NC}  3. Print all MD:  ssz-print-md --root . --order path${NC}"
echo -e "${NC}  4. View docs:     less docs/segwave_guide.md${NC}"
echo ""
echo -e "${CYAN}Validation Papers: \$SSZ_SOURCES_DIR (set via environment)${NC}"
echo -e "${CYAN}License: ANTI-CAPITALIST SOFTWARE LICENSE v1.4${NC}"
echo ""
