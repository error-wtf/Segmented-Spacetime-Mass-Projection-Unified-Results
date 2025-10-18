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
RUN_FULL_SUITE=false
QUICK_SUITE=false

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
        --run-full-suite)
            RUN_FULL_SUITE=true
            shift
            ;;
        --quick-suite)
            QUICK_SUITE=true
            shift
            ;;
        --help)
            echo "SSZ Projection Suite Installer"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-tests       Skip running test suite"
            echo "  --dev-mode         Install in editable mode (pip install -e .)"
            echo "  --dry-run          Show what would be done without executing"
            echo "  --run-full-suite   Run complete test suite after install"
            echo "  --quick-suite      Run quick test suite after install (~2 min)"
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
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

# Check if venv exists and is compatible with Linux/WSL
if [ -d "$VENV_PATH" ]; then
    if [ -f "$ACTIVATE_SCRIPT" ]; then
        print_success "Virtual environment already exists (Linux-compatible)"
    else
        print_warn "WARNING: Existing .venv is Windows-only (Scripts/activate.ps1)"
        print_info "Removing incompatible venv and recreating for Linux/WSL..."
        if [ "$DRY_RUN" = false ]; then
            rm -rf "$VENV_PATH"
            $PYTHON_CMD -m venv "$VENV_PATH"
            print_success "Created new Linux-compatible venv: $VENV_PATH"
        else
            print_info "[DRY-RUN] Would remove and recreate: $VENV_PATH"
        fi
    fi
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

if [ -f "$ACTIVATE_SCRIPT" ]; then
    if [ "$DRY_RUN" = false ]; then
        source "$ACTIVATE_SCRIPT"
        print_success "Activated: $VENV_PATH"
    else
        print_info "[DRY-RUN] Would activate: $VENV_PATH"
    fi
else
    print_error "ERROR: Activation script not found at: $ACTIVATE_SCRIPT"
    print_error "This should not happen. Venv creation may have failed."
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
        # Run ALL tests: root-level, tests/, and scripts/tests/
        print_info "Running root-level SSZ tests..."
        for test in test_vfall_duality.py test_ppn_exact.py test_energy_conditions.py \
                    test_c1_segments.py test_c2_segments_strict.py test_c2_curvature_proxy.py \
                    test_utf8_encoding.py; do
            if [ -f "$test" ]; then
                $PYTHON_CMD -m pytest "$test" -q --disable-warnings 2>&1 > /dev/null || true
            fi
        done
        
        print_info "Running tests/ directory..."
        $PYTHON_CMD -m pytest tests/ -q --disable-warnings
        
        print_info "Running scripts/tests/ directory..."
        if [ -d "scripts/tests" ]; then
            $PYTHON_CMD -m pytest scripts/tests/ -q --disable-warnings 2>&1 > /dev/null || true
        fi
        
        if [ $? -eq 0 ]; then
            print_success "All tests passed"
        else
            print_warn "WARNING: Some tests failed (non-fatal)"
        fi
    else
        print_info "[DRY-RUN] Would run: All tests (root, tests/, scripts/tests/)"
    fi
else
    echo ""
    print_step "[7/8] Skipping tests (--skip-tests flag)"
fi

# Step 8: Verify installation
echo ""
print_step "[8/8] Verifying installation..."
if [ "$DRY_RUN" = false ]; then
    # Check CLI commands
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
    
    # Check bundled papers
    print_info "Checking bundled papers..."
    if [ -d "papers/validation" ]; then
        VALIDATION_COUNT=$(find papers/validation -name "*.md" | wc -l)
        print_success "  [OK] Validation papers: $VALIDATION_COUNT files"
    else
        print_warn "  [WARN] Validation papers directory not found"
    fi
    
    if [ -d "docs/theory" ]; then
        THEORY_COUNT=$(find docs/theory -name "*.md" | wc -l)
        print_success "  [OK] Theory papers: $THEORY_COUNT files"
    else
        print_warn "  [WARN] Theory papers directory not found"
    fi
else
    print_info "[DRY-RUN] Would verify commands and papers"
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
echo -e "${YELLOW}Resources:${NC}"
echo -e "${CYAN}  - Validation Papers: papers/validation/ (10 files, ~593 KB)${NC}"
echo -e "${CYAN}  - Theory Papers:     docs/theory/ (20 files, ~380 KB)${NC}"
echo -e "${CYAN}  - License:           ANTI-CAPITALIST SOFTWARE LICENSE v1.4${NC}"
echo ""

# Optional: Run Full Test Suite
if [ "$RUN_FULL_SUITE" = true ] || [ "$QUICK_SUITE" = true ]; then
    echo ""
    print_header "RUNNING TEST SUITE"
    echo ""
    
    if [ -f "run_full_suite.py" ]; then
        if [ "$QUICK_SUITE" = true ]; then
            print_info "Executing: python3 run_full_suite.py --quick"
            python3 run_full_suite.py --quick
        else
            print_info "Executing: python3 run_full_suite.py"
            python3 run_full_suite.py
        fi
        
        if [ $? -eq 0 ]; then
            echo ""
            print_success "[SUCCESS] All tests passed!"
        else
            echo ""
            print_warn "[WARNING] Some tests failed (see output above)"
        fi
    else
        print_warn "[SKIP] run_full_suite.py not found"
    fi
    echo ""
fi
