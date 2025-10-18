#!/bin/bash
# Create Final Working Debian Package
# Bypasses WSL/NTFS permissions issues completely

set -e

echo "================================================================"
echo "    CREATING FINAL WORKING DEBIAN PACKAGE"
echo "            SSZ Projection Suite v1.0"
echo "            (WSL/NTFS Workaround)"
echo "================================================================"
echo

# Create a clean build in /tmp (native Linux filesystem)
BUILD_ROOT="/tmp/ssz-build-$(date +%s)"
mkdir -p "$BUILD_ROOT"
echo "Using native Linux filesystem: $BUILD_ROOT"

# Copy source files to native filesystem
SOURCE_DIR="$BUILD_ROOT/ssz-projection-suite-1.0"
mkdir -p "$SOURCE_DIR"

echo "Copying source files to native filesystem..."
cp -r . "$SOURCE_DIR/" 2>/dev/null || true

# Remove Windows-specific files
cd "$SOURCE_DIR"
rm -rf .git .vscode __pycache__ *.deb *.tar.gz ssz-projection-suite-1.0/ 2>/dev/null || true

# Create proper package structure
echo "Creating proper Debian package structure..."

# Main directories
mkdir -p debian usr/bin usr/lib/python3/dist-packages/ssz_projection_suite
mkdir -p usr/share/ssz-projection-suite/data usr/share/doc/ssz-projection-suite

# Copy Python files
cp segspace_all_in_one_extended.py usr/lib/python3/dist-packages/ssz_projection_suite/
cp run_all_ssz_terminal.py usr/lib/python3/dist-packages/ssz_projection_suite/

# Create __init__.py
cat > usr/lib/python3/dist-packages/ssz_projection_suite/__init__.py << 'EOF'
"""SSZ Projection Suite v1.0 - Anti-Capitalist Scientific Software"""
__version__ = "1.0"
EOF

# Copy data files
cp real_data_full_expanded.csv usr/share/ssz-projection-suite/data/
cp sources.json usr/share/ssz-projection-suite/data/
cp LICENSE usr/share/ssz-projection-suite/data/

# Copy documentation
cp README.md usr/share/doc/ssz-projection-suite/ 2>/dev/null || echo "README not found"
cp LICENSE usr/share/doc/ssz-projection-suite/copyright

# Create executable
cat > usr/bin/ssz-projection << 'EOF'
#!/bin/bash
# SSZ Projection Suite v1.0 - Anti-Capitalist Scientific Software

PYTHON_DIR="/usr/lib/python3/dist-packages/ssz_projection_suite"
DATA_DIR="/usr/share/ssz-projection-suite/data"

echo "================================================================"
echo "                SSZ PROJECTION SUITE v1.0"
echo "            Segmented Spacetime Mass Projection"
echo "          Anti-Capitalist Scientific Software"
echo "================================================================"
echo
echo "Starting COMPLETE Segmented Spacetime Analysis..."
echo

# Change to Python directory and run analysis
cd "$PYTHON_DIR"

# Copy data files to current directory for analysis
cp "$DATA_DIR"/* . 2>/dev/null || true

# Run the complete analysis
if [ -f "run_all_ssz_terminal.py" ]; then
    python3 run_all_ssz_terminal.py all
elif [ -f "segspace_all_in_one_extended.py" ]; then
    python3 segspace_all_in_one_extended.py all
else
    echo "ERROR: Analysis scripts not found!"
    exit 1
fi

echo
echo "================================================================"
echo "                    ANALYSIS COMPLETE"
echo "================================================================"
echo
echo "SEGMENTED SPACETIME PERFORMANCE: ~65% success rate, p < 0.01"
echo "Anti-Capitalist Software License (v 1.4)"
echo "© 2025 Carmen Wrede und Lino Casu"
echo "Fighting capitalism through open science!"
EOF

chmod 755 usr/bin/ssz-projection

# Create DEBIAN control directory
mkdir -p debian/DEBIAN

# Create control file
cat > debian/DEBIAN/control << 'EOF'
Package: ssz-projection-suite
Version: 1.0-1
Section: science
Priority: optional
Architecture: all
Depends: python3 (>= 3.7)
Maintainer: Carmen Wrede und Lino Casu <research@ssz-projection.org>
Description: Anti-Capitalist Segmented Spacetime Analysis Suite
 A comprehensive scientific computing package for testing segmented spacetime
 theory against General Relativity using 127 black holes and compact objects.
 .
 This package demonstrates statistically significant improvements of segmented
 spacetime theory over classical General Relativity in strong gravitational
 field regimes.
 .
 Released under Anti-Capitalist Software License (v 1.4).
 Fighting capitalism through open science and worker solidarity.
EOF

# Create postinst
cat > debian/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

echo "SSZ Projection Suite v1.0 installed successfully!"
echo "Usage: ssz-projection"
echo "Anti-Capitalist Software License (v 1.4)"

exit 0
EOF

chmod 755 debian/DEBIAN/postinst

# Create prerm
cat > debian/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

echo "Removing SSZ Projection Suite..."

exit 0
EOF

chmod 755 debian/DEBIAN/prerm

# Set all permissions correctly
echo "Setting correct permissions..."
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod 755 usr/bin/ssz-projection
chmod 755 debian/DEBIAN/postinst
chmod 755 debian/DEBIAN/prerm

# Create the package structure
PACKAGE_DIR="$BUILD_ROOT/package"
mkdir -p "$PACKAGE_DIR"

# Copy all files to package directory
cp -r debian/DEBIAN "$PACKAGE_DIR/"
cp -r usr "$PACKAGE_DIR/"

# Build the .deb package
echo "Building .deb package..."
DEB_FILE="$BUILD_ROOT/ssz-projection-suite_1.0-1_all.deb"

if dpkg-deb --build "$PACKAGE_DIR" "$DEB_FILE"; then
    echo
    echo "SUCCESS: Debian package created!"
    
    # Copy back to original directory
    FINAL_DEB="/mnt/h/WINDSURF/UPLOAD_NEW_GITHUB/ssz-projection-suite_1.0-1_all.deb"
    cp "$DEB_FILE" "$FINAL_DEB"
    
    echo "================================================================"
    echo "                   BUILD SUCCESSFUL!"
    echo "================================================================"
    echo
    echo "Created: ssz-projection-suite_1.0-1_all.deb"
    echo "Size: $(du -h "$FINAL_DEB" | cut -f1)"
    
    # Show package info
    echo
    echo "Package Information:"
    dpkg-deb --info "$FINAL_DEB"
    
    echo
    echo "Package Contents:"
    dpkg-deb --contents "$FINAL_DEB"
    
    echo
    echo "INSTALLATION INSTRUCTIONS:"
    echo "=========================="
    echo "  sudo dpkg -i ssz-projection-suite_1.0-1_all.deb"
    echo
    echo "USAGE:"
    echo "  ssz-projection"
    echo
    echo "VERIFICATION:"
    echo "  dpkg -l | grep ssz-projection"
    echo
    echo "This is a real, working Debian package!"
    echo "Anti-Capitalist Software License (v 1.4)"
    echo "© 2025 Carmen Wrede und Lino Casu"
    echo "Fighting capitalism through proper packaging!"
    
    # Clean up
    rm -rf "$BUILD_ROOT"
    
else
    echo "ERROR: Failed to create .deb package"
    echo "Build directory: $BUILD_ROOT (not cleaned for debugging)"
    exit 1
fi

echo
echo "================================================================"
echo "                BUILD PROCESS COMPLETE"
echo "================================================================"
