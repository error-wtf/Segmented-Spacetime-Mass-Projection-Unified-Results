#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminology Standardization Tool

Standardizes terminology variants across all documentation files
based on the official glossary.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
import io

# UTF-8 for Windows compatibility
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Fix stdout encoding for Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Terminology standardization rules
# Format: (pattern_to_find, standard_replacement, case_sensitive)
TERMINOLOGY_RULES = [
    # Primary terms - capitalize consistently
    (r'\bsegmented spacetime\b', 'Segmented Spacetime', False),
    (r'\bsegmented Spacetime\b', 'Segmented Spacetime', False),
    (r'\bSegmented spacetime\b', 'Segmented Spacetime', False),
    
    # Abbreviations - consistent capitalization
    (r'\bssz\b', 'SSZ', False),
    (r'\bSsz\b', 'SSZ', False),
    
    # Specific terms
    (r'\bmass projection\b', 'Mass Projection', False),
    (r'\bMass projection\b', 'Mass Projection', False),
    
    # Astronomy terms
    (r'\bevent horizon telescope\b', 'Event Horizon Telescope (EHT)', False),
    (r'\bEvent Horizon Telescope\b', 'Event Horizon Telescope (EHT)', False),
    
    # Golden ratio
    (r'\bgolden ratio\b', 'Golden Ratio', False),
    (r'\bGolden ratio\b', 'Golden Ratio', False),
    
    # Physics terms
    (r'\bgeneral relativity\b', 'General Relativity (GR)', False),
    (r'\bGeneral Relativity\b', 'General Relativity (GR)', False),
    (r'\bspecial relativity\b', 'Special Relativity (SR)', False),
    (r'\bSpecial Relativity\b', 'Special Relativity (SR)', False),
]

# Files/directories to exclude
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    '.venv',
    'venv',
    'node_modules',
    '.pytest_cache',
    'htmlcov',
    'out',
    'reports',
    'build',
    'dist',
    '*.pyc',
    '*.pyo',
]

# File extensions to process
INCLUDE_EXTENSIONS = ['.md', '.rst', '.txt']


def should_process_file(filepath: Path) -> bool:
    """Check if file should be processed."""
    # Check extension
    if filepath.suffix not in INCLUDE_EXTENSIONS:
        return False
    
    # Check exclude patterns
    path_str = str(filepath)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return False
    
    return True


def apply_terminology_rules(content: str, filepath: Path) -> Tuple[str, int]:
    """
    Apply terminology standardization rules to content.
    
    Returns:
        (modified_content, change_count)
    """
    modified = content
    changes = 0
    
    for pattern, replacement, case_sensitive in TERMINOLOGY_RULES:
        flags = 0 if case_sensitive else re.IGNORECASE
        
        # Count matches before replacement
        matches = len(re.findall(pattern, modified, flags=flags))
        
        if matches > 0:
            # Apply replacement
            modified = re.sub(pattern, replacement, modified, flags=flags)
            changes += matches
            print(f"  [{filepath.name}] {matches}x: {pattern} → {replacement}")
    
    return modified, changes


def process_directory(root_dir: Path, dry_run: bool = True) -> Dict:
    """
    Process all files in directory.
    
    Args:
        root_dir: Root directory to process
        dry_run: If True, only report changes without modifying files
    
    Returns:
        Statistics dictionary
    """
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'total_changes': 0,
        'changes_by_file': {}
    }
    
    print(f"\n{'=' * 80}")
    print(f"TERMINOLOGY STANDARDIZATION")
    print(f"{'=' * 80}")
    print(f"Mode: {'DRY RUN (no files modified)' if dry_run else 'LIVE (files will be modified)'}")
    print(f"Root: {root_dir}")
    print(f"{'=' * 80}\n")
    
    # Find all files
    for filepath in root_dir.rglob('*'):
        if not filepath.is_file():
            continue
        
        if not should_process_file(filepath):
            continue
        
        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                original = f.read()
            
            # Apply rules
            modified, change_count = apply_terminology_rules(original, filepath)
            
            stats['files_processed'] += 1
            
            if change_count > 0:
                stats['files_modified'] += 1
                stats['total_changes'] += change_count
                stats['changes_by_file'][str(filepath)] = change_count
                
                # Write modified content if not dry run
                if not dry_run:
                    with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                        f.write(modified)
                    print(f"  ✅ Modified: {filepath}")
        
        except Exception as e:
            print(f"  ❌ Error processing {filepath}: {e}")
    
    return stats


def print_summary(stats: Dict, dry_run: bool):
    """Print summary statistics."""
    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}")
    print(f"Files processed:  {stats['files_processed']}")
    print(f"Files modified:   {stats['files_modified']}")
    print(f"Total changes:    {stats['total_changes']}")
    print(f"{'=' * 80}")
    
    if dry_run and stats['files_modified'] > 0:
        print(f"\n⚠️  DRY RUN MODE - No files were modified")
        print(f"Run with --apply to actually modify files:")
        print(f"  python {__file__} --apply")
    elif not dry_run and stats['files_modified'] > 0:
        print(f"\n✅ Files successfully modified!")
        print(f"Review changes and commit if satisfied.")
    elif stats['files_modified'] == 0:
        print(f"\n✅ No terminology inconsistencies found!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize terminology across documentation'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually modify files (default: dry run)'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory to process (default: current directory)'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.root).resolve()
    
    if not root_dir.exists():
        print(f"❌ Error: Directory not found: {root_dir}")
        sys.exit(1)
    
    # Process directory
    stats = process_directory(root_dir, dry_run=not args.apply)
    
    # Print summary
    print_summary(stats, dry_run=not args.apply)
    
    return 0 if stats['total_changes'] == 0 else (1 if not args.apply else 0)


if __name__ == '__main__':
    sys.exit(main())
