#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add physical interpretations to ALL test files

This script adds print() statements with physical interpretations
to all test functions that currently only show PASSED.

Usage:
    python extend_all_tests.py --dry-run    # Preview changes
    python extend_all_tests.py              # Apply changes
"""

import re
import sys
from pathlib import Path

# Template for adding output to tests
PHYSICS_TEMPLATE = '''    
    print("\\n" + "="*80)
    print("{test_name}")
    print("="*80)
    print(f"Physical Meaning:")
    print(f"  {description}")
    print(f"\\nResult: {result}")
    print("="*80)
'''

# Test descriptions (physics meanings)
TEST_DESCRIPTIONS = {
    # test_segwave_core.py
    "test_temperature_only_basic": {
        "desc": "• q_k = (T_curr/T_prev)^β quantifies energy ratio between rings",
        "result": "q = {q:.6f} (Temperature ratio with β=1)"
    },
    "test_two_shells_alpha_one": {
        "desc": "• Velocity propagates as v_k = v_{k-1} × q_k^(-α/2)",
        "result": "v_pred = {expected_v2:.4f} km/s (SSZ ring velocity)"
    },
    
    # test_multi_body_sigma.py
    "test_two_body_sigma_superposition": {
        "desc": "• Segment density σ adds linearly for multiple bodies",
        "result": "σ_total = {sigma_total[0]:.6e} (Superposition holds)"
    },
    
    # test_ssz_invariants.py  
    "test_segment_growth_is_monotonic": {
        "desc": "• Segment density must increase monotonically with ring index",
        "result": "All growth values ≥ 0 (Monotonic)"
    },
    "test_natural_boundary_positive": {
        "desc": "• Natural boundary radius must be positive (φ-based limit)",
        "result": "All r_φ > 0 (Physical boundary)"
    },
}


def add_physics_output(test_file: Path, dry_run: bool = False):
    """Add physics output to test file"""
    
    print(f"\n{'='*80}")
    print(f"Processing: {test_file.name}")
    print(f"{'='*80}")
    
    if not test_file.exists():
        print(f"  [SKIP] File not found")
        return
    
    content = test_file.read_text(encoding='utf-8')
    original_content = content
    
    # Find all test functions
    test_pattern = r'(def (test_\w+)\([^)]*\):.*?)(?=\n    def |$)'
    matches = list(re.finditer(test_pattern, content, re.DOTALL))
    
    if not matches:
        print(f"  [SKIP] No test functions found")
        return
    
    print(f"  Found {len(matches)} test functions")
    modified = 0
    
    for match in reversed(matches):  # Reverse to preserve positions
        test_name = match.group(2)
        test_body = match.group(1)
        
        # Skip if already has print output
        if 'print(' in test_body and '='*80 in test_body:
            continue
        
        # Skip if no description available
        if test_name not in TEST_DESCRIPTIONS:
            continue
        
        desc_info = TEST_DESCRIPTIONS[test_name]
        
        # Find the assert statement
        assert_match = re.search(r'(    assert .+)', test_body)
        if not assert_match:
            continue
        
        # Create physics output block
        physics_block = f'''    
    # Physical interpretation
    print("\\n" + "="*80)
    print("{test_name.replace('_', ' ').title()}")
    print("="*80)
    print(f"Physical Meaning:")
    print(f"  {desc_info['desc']}")
    print("="*80)
    '''
        
        # Insert before the first assert
        assert_pos = assert_match.start(1)
        test_start = match.start(1)
        
        new_test_body = test_body[:assert_pos - test_start] + physics_block + test_body[assert_pos - test_start:]
        
        content = content[:match.start(1)] + new_test_body + content[match.end(1):]
        modified += 1
        print(f"    ✓ Modified: {test_name}")
    
    if modified > 0:
        if dry_run:
            print(f"\n  [DRY RUN] Would modify {modified} tests")
            print(f"  Preview (first 500 chars):")
            print(f"  {content[:500]}...")
        else:
            test_file.write_text(content, encoding='utf-8')
            print(f"\n  [SAVED] Modified {modified} tests")
    else:
        print(f"\n  [SKIP] No modifications needed")


def main():
    dry_run = '--dry-run' in sys.argv
    
    print("="*80)
    print("EXTEND ALL TESTS WITH PHYSICAL INTERPRETATIONS")
    print("="*80)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be modified\n")
    
    # Test files to process
    test_files = [
        Path("tests/test_segwave_core.py"),
        Path("tests/cosmos/test_multi_body_sigma.py"),
        Path("scripts/tests/test_ssz_invariants.py"),
        # Add more as needed
    ]
    
    for test_file in test_files:
        add_physics_output(test_file, dry_run=dry_run)
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    
    if dry_run:
        print("\n✓ Dry run complete - re-run without --dry-run to apply changes")
    else:
        print("\n✓ All test files updated")
        print("\nRun tests with: run_verbose_tests.bat")


if __name__ == "__main__":
    main()
