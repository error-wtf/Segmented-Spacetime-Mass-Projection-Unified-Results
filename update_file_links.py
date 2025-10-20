#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update file references to include GitHub links
"""
import re
import sys
import os
from pathlib import Path

# Force UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

# Base GitHub URL
GITHUB_BASE = "https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results/blob/main"

# File mappings: filename -> full GitHub URL
FILE_LINKS = {
    "EQUILIBRIUM_RADIUS_SOLUTION.md": f"{GITHUB_BASE}/EQUILIBRIUM_RADIUS_SOLUTION.md",
    "RAPIDITY_IMPLEMENTATION.md": f"{GITHUB_BASE}/RAPIDITY_IMPLEMENTATION.md",
    "perfect_equilibrium_analysis.py": f"{GITHUB_BASE}/perfect_equilibrium_analysis.py",
    "PERFECT_SEG_ANALYSIS_GUIDE.md": f"{GITHUB_BASE}/PERFECT_SEG_ANALYSIS_GUIDE.md",
    "perfect_seg_analysis.py": f"{GITHUB_BASE}/perfect_seg_analysis.py",
    "PERFECT_PAIRED_TEST_GUIDE.md": f"{GITHUB_BASE}/PERFECT_PAIRED_TEST_GUIDE.md",
    "perfect_paired_test.py": f"{GITHUB_BASE}/perfect_paired_test.py",
}

def update_markdown_file(filepath):
    """Update a markdown file to link file references"""
    content = filepath.read_text(encoding='utf-8')
    original = content
    updated = False
    
    for filename, url in FILE_LINKS.items():
        # Pattern 1: `filename` -> [`filename`](url)
        pattern1 = rf'`{re.escape(filename)}`(?!\()'  # ` but not already linked
        if re.search(pattern1, content):
            content = re.sub(pattern1, f'[`{filename}`]({url})', content)
            updated = True
            print(f"  Updated: `{filename}` -> linked version")
        
        # Pattern 2: **filename** -> **[filename](url)**
        pattern2 = rf'\*\*{re.escape(filename)}\*\*(?!\()'
        if re.search(pattern2, content):
            content = re.sub(pattern2, f'**[{filename}]({url})**', content)
            updated = True
            print(f"  Updated: **{filename}** -> linked version")
        
        # Pattern 3: - filename -> - [{filename}]({url})
        pattern3 = rf'^(\s*[-•]\s+){re.escape(filename)}(?!\])'
        if re.search(pattern3, content, re.MULTILINE):
            content = re.sub(pattern3, rf'\1[{filename}]({url})', content, flags=re.MULTILINE)
            updated = True
            print(f"  Updated: list item {filename} -> linked version")
    
    if updated:
        filepath.write_text(content, encoding='utf-8')
        return True
    return False

def main():
    """Update all markdown files"""
    here = Path(__file__).parent
    md_files = list(here.glob("*.md"))
    
    # Also include docs/
    md_files.extend(here.glob("docs/*.md"))
    md_files.extend(here.glob("tests/*.md"))
    
    print(f"Found {len(md_files)} markdown files to check\n")
    
    updated_count = 0
    for md_file in md_files:
        # Skip some files that might have intentionally plain text
        if md_file.name.startswith('.'):
            continue
        
        print(f"Checking: {md_file.name}")
        if update_markdown_file(md_file):
            updated_count += 1
    
    print(f"\n✅ Updated {updated_count} files with GitHub links")

if __name__ == "__main__":
    main()
