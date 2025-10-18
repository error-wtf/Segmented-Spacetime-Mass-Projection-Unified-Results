#!/bin/bash
set -e

echo "========================================================================"
echo "Segmented Spacetime Suite - Debian Package Builder"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect if we're in WSL
if grep -qi microsoft /proc/version; then
    echo -e "${GREEN}✓ Running in WSL${NC}"
    IN_WSL=true
else
    echo -e "${GREEN}✓ Running in native Linux${NC}"
    IN_WSL=false
fi

# Get the repository path
if [ "$IN_WSL" = true ]; then
    # We're in WSL, repo should be in /mnt/h/...
    REPO_PATH="/mnt/h/WINDSURF/Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00"
else
    # Native Linux, use current directory
    REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

echo "Repository path: $REPO_PATH"
echo ""

# Check if repository exists
if [ ! -d "$REPO_PATH" ]; then
    echo -e "${RED}✗ Repository not found at: $REPO_PATH${NC}"
    exit 1
fi

cd "$REPO_PATH"

# Step 1: Check for required tools
echo "========================================================================"
echo "Step 1: Checking prerequisites"
echo "========================================================================"

MISSING_TOOLS=()

check_tool() {
    if ! command -v "$1" &> /dev/null; then
        MISSING_TOOLS+=("$1")
        echo -e "${YELLOW}⚠ Missing: $1${NC}"
    else
        echo -e "${GREEN}✓ Found: $1${NC}"
    fi
}

check_tool dpkg-buildpackage
check_tool debhelper
check_tool dh-python
check_tool python3

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Missing required tools. Installing...${NC}"
    echo ""
    
    sudo apt update
    sudo apt install -y \
        build-essential \
        devscripts \
        debhelper \
        dh-python \
        python3-all \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        python3-build
    
    echo -e "${GREEN}✓ Prerequisites installed${NC}"
fi

# Step 2: Install runtime dependencies (for testing)
echo ""
echo "========================================================================"
echo "Step 2: Installing runtime dependencies"
echo "========================================================================"

sudo apt install -y \
    python3-numpy \
    python3-scipy \
    python3-pandas \
    python3-astropy \
    python3-matplotlib \
    python3-yaml \
    python3-requests \
    python3-tqdm \
    python3-pytest || {
    echo -e "${YELLOW}⚠ Some dependencies failed to install (may not be critical)${NC}"
}

# Optional dependencies
sudo apt install -y python3-pyarrow python3-rich 2>/dev/null || {
    echo -e "${YELLOW}⚠ Optional dependencies not available (will use pip fallback)${NC}"
}

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Make scripts executable
echo ""
echo "========================================================================"
echo "Step 3: Setting file permissions"
echo "========================================================================"

chmod +x debian/rules
chmod +x debian/segmented-spacetime-suite-extended.postinst
chmod -x debian/segmented-spacetime-suite-extended.install

echo -e "${GREEN}✓ Permissions set${NC}"

# Step 4: Clean previous build
echo ""
echo "========================================================================"
echo "Step 4: Cleaning previous build artifacts"
echo "========================================================================"

if [ -f "../segmented-spacetime-suite-extended_1.0_all.deb" ]; then
    echo "Removing old .deb file..."
    rm -f ../segmented-spacetime-suite-extended_1.0_all.deb
fi

if [ -d "debian/segmented-spacetime-suite-extended" ]; then
    echo "Cleaning debian build directory..."
    dpkg-buildpackage -T clean 2>/dev/null || true
fi

echo -e "${GREEN}✓ Build artifacts cleaned${NC}"

# Step 5: Build package
echo ""
echo "========================================================================"
echo "Step 5: Building Debian package"
echo "========================================================================"
echo ""
echo "This will take 1-2 minutes..."
echo ""

dpkg-buildpackage -us -uc -b

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Package built successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Step 6: Verify package
echo ""
echo "========================================================================"
echo "Step 6: Verifying package"
echo "========================================================================"

DEB_FILE="../segmented-spacetime-suite-extended_1.0_all.deb"

if [ -f "$DEB_FILE" ]; then
    echo -e "${GREEN}✓ Package file exists${NC}"
    
    # Get file size
    SIZE=$(du -h "$DEB_FILE" | cut -f1)
    echo "  Size: $SIZE"
    
    # Show package info
    echo ""
    echo "Package information:"
    dpkg-deb --info "$DEB_FILE" | grep -E "(Package|Version|Architecture|Description)" || true
    
    # List contents (first 10 files)
    echo ""
    echo "Package contents (sample):"
    dpkg-deb --contents "$DEB_FILE" | head -n 10
    echo "  ..."
    
else
    echo -e "${RED}✗ Package file not found${NC}"
    exit 1
fi

# Step 7: Installation prompt
echo ""
echo "========================================================================"
echo "Build Complete!"
echo "========================================================================"
echo ""
echo -e "${GREEN}Package created: $DEB_FILE${NC}"
echo ""
echo "To install:"
echo ""
echo "  cd $(dirname "$DEB_FILE")"
echo "  sudo apt install -y ./$(basename "$DEB_FILE")"
echo ""
echo "To install WITHOUT auto-run:"
echo ""
echo "  sudo SEGSPACE_FETCH=0 apt install -y ./$(basename "$DEB_FILE")"
echo ""
echo "After installation, run:"
echo ""
echo "  segspace-run-all      # Complete suite + reports + license"
echo "  segspace-summary      # Just print reports"
echo "  segspace-fetch-data   # Fetch optional data"
echo ""

# Interactive install prompt
echo -n "Install package now? [y/N] "
read -r INSTALL_NOW

if [[ "$INSTALL_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Installing package..."
    cd ..
    sudo apt install -y ./segmented-spacetime-suite-extended_1.0_all.deb
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Package installed successfully!${NC}"
        echo ""
        echo "Verify installation:"
        echo "  which segspace-run-all"
        echo "  segspace-run-all --help"
    else
        echo -e "${RED}✗ Installation failed${NC}"
        exit 1
    fi
else
    echo ""
    echo "Skipping installation. Package is ready at:"
    echo "  $DEB_FILE"
fi

echo ""
echo "========================================================================"
echo "Done!"
echo "========================================================================"
