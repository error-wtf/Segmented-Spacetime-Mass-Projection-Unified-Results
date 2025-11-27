#!/usr/bin/env bash
# ============================================================================
# Automatic Documentation Update: 97.9% → 100%
# ============================================================================
# USAGE: ./update_to_100_percent.sh [--dry-run]
#
# This script automatically updates all documentation from 97.9% to 100%
# after achieving perfect ESO validation with 2PN calibration.
#
# © 2025 Carmen Wrede & Lino Casu
# ============================================================================

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
fi

echo ""
echo "================================================================================"
echo "  DOCUMENTATION UPDATE: 97.9% → 100%"
echo "================================================================================"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN MODE - No files will be modified"
    echo ""
fi

# ============================================================================
# STEP 1: Backup Current State
# ============================================================================

echo "[1/6] Creating backup..."

if [ "$DRY_RUN" = false ]; then
    BACKUP_BRANCH="backup-97-9-percent-$(date +%Y-%m-%d-%H%M)"
    echo "  Creating backup branch: $BACKUP_BRANCH"
    git branch "$BACKUP_BRANCH"
    echo "  ✓ Backup created"
else
    echo "  [DRY RUN] Would create backup branch"
fi

echo ""

# ============================================================================
# STEP 2: Define Files to Update
# ============================================================================

echo "[2/6] Scanning for files..."

FILES_TO_UPDATE=(
    "README.md"
    "validation_complete_extended/reports/PAIRED_TEST_ANALYSIS_COMPLETE.md"
    "validation_complete_extended/reports/PERFECT_PAIRED_TEST_GUIDE.md"
    "validation_complete_extended/reports/WINDOWS_VERIFICATION_COMPLETE.md"
    "validation_complete_extended/reports/SCIENTIFIC_INTERPRETATIONS.md"
    "validation_complete_extended/reports/COMPLETE_STATUS_CHECKLIST.md"
    "validation_complete_extended/reports/FIX_ALL_PIPELINES.md"
    "validation_complete_extended/reports/RELEASE_ROADMAP.md"
    "validation_complete_extended/reports/USAGE_FAQ.md"
    "validation_complete_extended/reports/PLOTS_OVERVIEW.md"
    "WINDOWS_VERIFICATION_COMPLETE.md"
    "validation_out_v2/SCIENTIFIC_INTERPRETATIONS.md"
)

EXISTING_FILES=()
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        EXISTING_FILES+=("$file")
        echo "    • $file"
    fi
done

echo "  Found ${#EXISTING_FILES[@]} files to update"
echo ""

# ============================================================================
# STEP 3: Define Replacement Patterns
# ============================================================================

echo "[3/6] Defining replacement patterns..."

# Declare arrays for patterns and replacements
declare -a PATTERNS=(
    "97\.9%[[:space:]]*\(46/47"
    "97\.9%[[:space:]]*\(46[[:space:]]*/[[:space:]]*47"
    "46/47 wins"
    "46 of 47"
    "97\.2%[[:space:]]*\(35/36"
    "35/36 wins"
    "ESO Validation:[[:space:]]*97\.9%"
    "ESO validation 97\.9%"
)

declare -a REPLACEMENTS=(
    "100% (47/47"
    "100% (47/47"
    "47/47 wins"
    "47 of 47"
    "100% (36/36"
    "36/36 wins"
    "ESO Validation: 100%"
    "ESO validation 100%"
)

declare -a DESCRIPTIONS=(
    "Overall success rate"
    "Overall success rate (spaced)"
    "Win count"
    "Win count (worded)"
    "Strong field success rate"
    "Strong field win count"
    "ESO validation label"
    "ESO validation (no colon)"
)

echo "  ✓ ${#PATTERNS[@]} replacement patterns defined"
echo ""

# ============================================================================
# STEP 4: Perform Replacements
# ============================================================================

echo "[4/6] Applying replacements..."

TOTAL_REPLACEMENTS=0
FILES_MODIFIED=0

for file in "${EXISTING_FILES[@]}"; do
    echo ""
    echo "  Processing: $file"
    
    if [ ! -f "$file" ]; then
        echo "    ⚠ File not found, skipping"
        continue
    fi
    
    FILE_REPLACEMENTS=0
    TEMP_FILE="${file}.tmp"
    
    # Copy original to temp
    cp "$file" "$TEMP_FILE"
    
    # Apply each replacement
    for i in "${!PATTERNS[@]}"; do
        PATTERN="${PATTERNS[$i]}"
        REPLACEMENT="${REPLACEMENTS[$i]}"
        DESCRIPTION="${DESCRIPTIONS[$i]}"
        
        # Count matches
        COUNT=$(grep -cE "$PATTERN" "$TEMP_FILE" || true)
        
        if [ "$COUNT" -gt 0 ]; then
            echo "    • $DESCRIPTION: $COUNT match(es)"
            
            # Perform replacement
            sed -i "s/$PATTERN/$REPLACEMENT/g" "$TEMP_FILE"
            
            FILE_REPLACEMENTS=$((FILE_REPLACEMENTS + COUNT))
        fi
    done
    
    if [ "$FILE_REPLACEMENTS" -gt 0 ]; then
        FILES_MODIFIED=$((FILES_MODIFIED + 1))
        TOTAL_REPLACEMENTS=$((TOTAL_REPLACEMENTS + FILE_REPLACEMENTS))
        
        if [ "$DRY_RUN" = false ]; then
            mv "$TEMP_FILE" "$file"
            echo "    ✓ $FILE_REPLACEMENTS replacement(s) applied"
        else
            rm "$TEMP_FILE"
            echo "    [DRY RUN] Would apply $FILE_REPLACEMENTS replacement(s)"
        fi
    else
        rm "$TEMP_FILE"
        echo "    No changes needed"
    fi
done

echo ""
echo "  ✓ $FILES_MODIFIED files modified"
echo "  ✓ $TOTAL_REPLACEMENTS total replacements"
echo ""

# ============================================================================
# STEP 5: Verify Changes
# ============================================================================

echo "[5/6] Verifying changes..."

if [ "$DRY_RUN" = false ]; then
    echo "  Checking for remaining '97.9%' in main files..."
    
    REMAINING=()
    for file in "${EXISTING_FILES[@]}"; do
        if [ -f "$file" ]; then
            if grep -qE "97\.9%.*\(46/47" "$file"; then
                REMAINING+=("$file")
            fi
        fi
    done
    
    if [ "${#REMAINING[@]}" -eq 0 ]; then
        echo "  ✓ No problematic '97.9%' references found"
    else
        echo "  ⚠ Warning: Some '97.9%' references remain in:"
        for file in "${REMAINING[@]}"; do
            echo "    • $file"
        done
        echo "  (These may be in historical context - review manually)"
    fi
else
    echo "  [DRY RUN] Would verify changes"
fi

echo ""

# ============================================================================
# STEP 6: Documentation Status
# ============================================================================

echo "[6/6] Documentation status..."

if [ -f "DOCUMENTATION_UPDATE_100_PERCENT.md" ]; then
    echo "  ✓ Update guide exists: DOCUMENTATION_UPDATE_100_PERCENT.md"
else
    echo "  ⚠ Update guide not found"
fi

if [ -f "UPGRADE_TO_100_PERCENT.md" ]; then
    echo "  ✓ Upgrade guide exists: UPGRADE_TO_100_PERCENT.md"
else
    echo "  ⚠ Upgrade guide not found"
fi

if [ -f "calibration_2pn.py" ]; then
    echo "  ✓ 2PN calibration exists: calibration_2pn.py"
else
    echo "  ⚠ 2PN calibration not found"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "================================================================================"
echo "  UPDATE COMPLETE"
echo "================================================================================"
echo ""

echo "Summary:"
echo "  • Files scanned: ${#EXISTING_FILES[@]}"
echo "  • Files modified: $FILES_MODIFIED"
echo "  • Total replacements: $TOTAL_REPLACEMENTS"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "This was a DRY RUN. No files were actually modified."
    echo "Run without --dry-run to apply changes."
else
    echo "✓ All documentation updated from 97.9% to 100%"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git diff"
    echo "  2. Regenerate plots with 100% label"
    echo "  3. Create milestone doc: 100_PERCENT_MILESTONE.md"
    echo "  4. Commit: git add -A && git commit -m 'MILESTONE: 100% ESO Validation'"
    echo "  5. Push: git push origin main"
fi

echo ""
echo "================================================================================"
echo "© 2025 Carmen Wrede & Lino Casu"
echo "================================================================================"
echo ""
