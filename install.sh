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
    print_step "[7/9] Running test suite..."
    if [ "$DRY_RUN" = false ]; then
        # Run ALL tests with full output
        print_info "Running ALL tests (root + tests/ + scripts/tests/)..."
        echo ""
        
        ALL_PASSED=true
        
        # Root-level tests (run as Python scripts, not pytest)
        echo -e "${CYAN}Root-level SSZ tests:${NC}"
        for test in test_ppn_exact.py test_vfall_duality.py test_energy_conditions.py \
                    test_c1_segments.py test_c2_segments_strict.py test_c2_curvature_proxy.py \
                    test_utf8_encoding.py; do
            if [ -f "$test" ]; then
                echo -n "  $test "
                if $PYTHON_CMD "$test" > /dev/null 2>&1; then
                    echo -e "${GREEN}PASSED${NC}"
                else
                    echo -e "${RED}FAILED${NC}"
                    ALL_PASSED=false
                fi
            fi
        done
        echo ""
        
        # pytest tests (tests/ and scripts/tests/)
        echo -e "${CYAN}Pytest test suites:${NC}"
        $PYTHON_CMD -m pytest tests/ scripts/tests/ -v --tb=short --disable-warnings
        
        if [ $? -ne 0 ]; then
            ALL_PASSED=false
        fi
        
        echo ""
        if [ "$ALL_PASSED" = true ]; then
            print_success "✓ All tests passed"
        else
            echo -e "${RED}✗ Some tests FAILED - Fix before continuing!${NC}"
            exit 1
        fi
    else
        print_info "[DRY-RUN] Would run: All tests (root, tests/, scripts/tests/)"
    fi
else
    echo ""
    print_step "[7/9] Skipping tests (--skip-tests flag)"
fi

# Step 8: Verify installation
echo ""
print_step "[8/9] Verifying installation..."
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

# Step 9: Generate complete summary (tests, papers, analyses, MD outputs)
if [ "$SKIP_TESTS" = false ]; then
    echo ""
    print_step "[9/9] Generating complete summary and outputs..."
    if [ "$DRY_RUN" = false ]; then
        print_info "Creating comprehensive summary..."
        
        # 1. Test Summary
        SUMMARY_SCRIPT="ci/summary-all-tests.py"
        if [ -f "$SUMMARY_SCRIPT" ]; then
            echo -e "${CYAN}  [1/5] Test summary...${NC}"
            if $PYTHON_CMD "$SUMMARY_SCRIPT" > /dev/null 2>&1; then
                print_success "    [OK] Test results summary generated"
            else
                print_warn "    [WARN] Could not generate test summary"
            fi
        fi
        
        # 2. Count validation papers
        echo -e "${CYAN}  [2/5] Validation papers...${NC}"
        PAPERS_VALIDATION="papers/validation"
        if [ -d "$PAPERS_VALIDATION" ]; then
            VALIDATION_COUNT=$(find "$PAPERS_VALIDATION" -name "*.md" | wc -l)
            print_success "    [OK] $VALIDATION_COUNT validation papers available"
        fi
        
        # 3. Count theory papers
        echo -e "${CYAN}  [3/5] Theory papers...${NC}"
        PAPERS_THEORY="docs/theory"
        if [ -d "$PAPERS_THEORY" ]; then
            THEORY_COUNT=$(find "$PAPERS_THEORY" -name "*.md" | wc -l)
            print_success "    [OK] $THEORY_COUNT theory papers available"
        fi
        
        # 4. Check analysis reports
        echo -e "${CYAN}  [4/5] Analysis reports...${NC}"
        REPORTS_DIR="reports"
        if [ -d "$REPORTS_DIR" ]; then
            REPORT_COUNT=$(find "$REPORTS_DIR" -name "*.md" 2>/dev/null | wc -l)
            if [ "$REPORT_COUNT" -gt 0 ]; then
                print_success "    [OK] $REPORT_COUNT analysis reports found"
            else
                echo -e "${CYAN}    [INFO] No reports yet (run python run_all_ssz_terminal.py to generate)${NC}"
            fi
        fi
        
        # 5. Complete MD outputs catalog
        echo -e "${CYAN}  [5/5] Complete MD catalog...${NC}"
        ALL_MD_COUNT=$(find . -name "*.md" -not -path "./.venv/*" -not -path "./node_modules/*" 2>/dev/null | wc -l)
        print_success "    [OK] $ALL_MD_COUNT total MD files available"
        echo -e "${CYAN}    [INFO] Run ./print_all_analysis.sh to view ALL outputs${NC}"
        
        echo ""
        print_success "Summary ready! Available outputs:"
        echo -e "${NC}    - Test results: ci/test_summary.html (if generated)${NC}"
        echo -e "${NC}    - Papers: papers/validation/ + docs/theory/${NC}"
        echo -e "${NC}    - Reports: reports/ (after running analysis)${NC}"
        echo -e "${NC}    - Complete: Run ./print_all_analysis.sh for everything${NC}"
    else
        print_info "[DRY-RUN] Would generate complete summary and outputs"
    fi
else
    echo ""
    print_step "[9/9] Skipping summary generation (--skip-tests flag)"
fi

# Summary
echo ""
print_header "INSTALLATION COMPLETE"
echo ""
echo -e "${YELLOW}Quick Start - All Test Scripts:${NC}"
echo -e "  1. Activate venv:   source .venv/bin/activate"
echo ""
echo -e "${CYAN}  Root-Level SSZ Tests (Python scripts):${NC}"
echo -e "    python test_ppn_exact.py              # PPN parameters β=γ=1"
echo -e "    python test_vfall_duality.py          # Dual velocity invariant"
echo -e "    python test_energy_conditions.py      # WEC/DEC/SEC"
echo -e "    python test_c1_segments.py            # C1 continuity"
echo -e "    python test_c2_segments_strict.py     # C2 strict"
echo -e "    python test_c2_curvature_proxy.py     # C2 + curvature proxy"
echo -e "    python test_utf8_encoding.py          # UTF-8 validation"
echo ""
echo -e "${CYAN}  Full Test Suite:${NC}"
echo -e "    python run_full_suite.py              # All tests + analysis (~10-15 min)"
echo -e "    python run_full_suite.py --quick      # Essential tests only (~2 min)"
echo ""
echo -e "${CYAN}  Complete SSZ Analysis (20+ scripts in pipeline):${NC}"
echo -e "    python run_all_ssz_terminal.py        # Full SSZ pipeline (~10-15 min)"
echo -e "      → Runs: segspace_all_in_one_extended, covariant tests,"
echo -e "        PPN tests, shadow predictions, QNM, φ-lattice, v_fall,"
echo -e "        Lagrangian tests, stress-energy, theory calculations"
echo -e "      → See SSZ_COMPLETE_PIPELINE.md for full 20+ script list"
echo ""
echo -e "${CYAN}  Example Data Analysis (SegWave):${NC}"
echo -e "    ssz-rings --csv data/observations/G79_29+0_46_CO_NH3_rings.csv --v0 12.5 --fit-alpha"
echo -e "    ssz-rings --csv data/observations/CygnusX_DiamondRing_CII_rings.csv --v0 1.3"
echo ""
echo -e "${CYAN}  Additional Analysis Scripts:${NC}"
echo -e "    python scripts/analysis/eht_shadow_comparison.py    # EHT comparison matrix"
echo -e "    python scripts/analysis/redshift_robustness.py      # Redshift robustness"
echo -e "    python scripts/ring_temperature_to_velocity.py      # Ring temperature analysis"
echo -e "    python ci/summary-all-tests.py                      # Complete test summary"
echo -e "    python ci/summary_visualize.py                      # Visualization dashboard"
echo ""
echo -e "${CYAN}  Print ALL Markdown (Papers + Reports + Summaries + Outputs):${NC}"
echo -e "    ssz-print-md --root . --order path    # All MD files, alphabetically"
echo -e "    ssz-print-md --root . --order depth   # All MD files, shallow-first"
echo -e "    ssz-print-md --root papers            # Only validation papers"
echo -e "    ssz-print-md --root reports           # Only analysis reports"
echo -e "    ssz-print-md --root docs              # Only theory papers"
echo ""
echo -e "${YELLOW}Resources:${NC}"
echo -e "${CYAN}  - Validation Papers: papers/validation/ (11 files)${NC}"
echo -e "${CYAN}  - Theory Papers:     docs/theory/ (21 files)${NC}"
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
