#!/bin/bash
# Download ESO FITS files with token authentication
#
# Usage:
#   1. Get token from ESO archive (see MANUAL_ESO_DATA_ACQUISITION_GUIDE.md Step 4)
#   2. Edit TOKEN variable below
#   3. Add dataset IDs to DATASETS array
#   4. Run: bash scripts/download_eso_fits.sh
#
# Dataset IDs come from ESO query results (Step 3)
# Look for "Dataset ID" column in query table

# ============================================================================
# CONFIGURATION - EDIT THESE
# ============================================================================

# Your ESO token (valid 24-48 hours)
# Get from: https://archive.eso.org/ → Query → Request Download
TOKEN="YOUR_TOKEN_HERE"

# Dataset IDs from ESO query results
# Format: INSTRUMENT.DATE.OBSERVATION_ID
# Example: GRAVITY.2018-05-27T03:21:09.123
DATASETS=(
    "GRAVITY.2018-05-27T03:21:09.123"
    "GRAVITY.2019-04-15T02:15:33.456"
    "GRAVITY.2020-03-10T01:45:21.789"
    # Add more dataset IDs here - one per line
)

# Output directory
OUTPUT_DIR="data/raw_fetch/eso_fits"

# ESO Data Portal base URL
BASE_URL="https://dataportal.eso.org/dataPortal/file"

# ============================================================================
# SCRIPT - DO NOT EDIT BELOW
# ============================================================================

# Check token
if [ "$TOKEN" = "YOUR_TOKEN_HERE" ]; then
    echo "ERROR: Please edit TOKEN variable in this script"
    echo "Get token from: https://archive.eso.org/"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "============================================"
echo "ESO FITS Download Script"
echo "============================================"
echo "Output directory: $OUTPUT_DIR"
echo "Number of datasets: ${#DATASETS[@]}"
echo "Token: ${TOKEN:0:20}... (truncated)"
echo ""

# Download counter
SUCCESS=0
FAILED=0

# Download each dataset
for DATASET in "${DATASETS[@]}"; do
    echo "----------------------------------------"
    echo "Dataset: $DATASET"
    
    # Build filename
    FILENAME="${DATASET}.fits.Z"
    OUTPUT_FILE="$OUTPUT_DIR/$FILENAME"
    
    # Check if already downloaded
    if [ -f "$OUTPUT_FILE" ]; then
        echo "  ✓ Already exists, skipping"
        ((SUCCESS++))
        continue
    fi
    
    # Build URL
    URL="$BASE_URL/$DATASET"
    
    # Download with curl
    echo "  Downloading..."
    HTTP_CODE=$(curl -w "%{http_code}" -o "$OUTPUT_FILE" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: application/fits" \
        --fail-with-body \
        --silent \
        --show-error \
        "$URL")
    
    # Check result
    if [ $? -eq 0 ] && [ "$HTTP_CODE" = "200" ]; then
        FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
        echo "  ✓ Downloaded (${FILE_SIZE} bytes, HTTP $HTTP_CODE)"
        ((SUCCESS++))
    else
        echo "  ✗ FAILED (HTTP $HTTP_CODE)"
        rm -f "$OUTPUT_FILE"
        ((FAILED++))
    fi
done

echo ""
echo "============================================"
echo "Download Summary"
echo "============================================"
echo "Success: $SUCCESS"
echo "Failed:  $FAILED"
echo "Total:   ${#DATASETS[@]}"
echo ""

if [ $SUCCESS -gt 0 ]; then
    echo "Decompressing FITS files..."
    cd "$OUTPUT_DIR"
    
    # Try uncompress first, fallback to gunzip
    if command -v uncompress &> /dev/null; then
        uncompress -f *.fits.Z 2>/dev/null || true
    else
        gunzip -f *.fits.Z 2>/dev/null || true
    fi
    
    FITS_COUNT=$(ls -1 *.fits 2>/dev/null | wc -l)
    echo "✓ Decompressed $FITS_COUNT FITS files"
    echo ""
    echo "Next step:"
    echo "  python scripts/process_eso_fits_to_csv.py \\"
    echo "    --fits-dir $OUTPUT_DIR \\"
    echo "    --output data/emission_lines.csv \\"
    echo "    --params data/stellar_parameters_example.json"
fi

exit 0
