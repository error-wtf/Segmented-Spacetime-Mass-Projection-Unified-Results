#!/usr/bin/env python3
"""
Automatic INDEX.md Link Fixer
Fixes all 186 broken links in docs/INDEX.md
"""
import os
import re
from pathlib import Path

# Get all actual files
root_md = set(f.name for f in Path('.').glob('*.md'))
docs_md = set(f.name for f in Path('docs').glob('*.md'))
data_md = set(f.name for f in Path('data').glob('*.md'))

print(f"Found {len(root_md)} root .md files")
print(f"Found {len(docs_md)} docs .md files")
print(f"Found {len(data_md)} data .md files")

# Read INDEX.md
index_path = Path('docs/INDEX.md')
content = index_path.read_text(encoding='utf-8')

# Track fixes
fixes = []

def fix_link(match):
    """Fix a single markdown link"""
    full = match.group(0)
    text = match.group(1)
    path = match.group(2)
    
    # Skip URLs and anchors
    if path.startswith('http') or path.startswith('#'):
        return full
    
    # Extract filename
    filename = Path(path).name
    
    # Skip if it's a directory or .py file
    if path.endswith('/') or path.endswith('.py'):
        return full
    
    # Determine correct path
    if filename in docs_md:
        # File is in docs/ - use relative path
        new_path = filename
    elif filename in root_md:
        # File is in root - need ../
        new_path = f"../{filename}"
    elif filename in data_md:
        # File is in data/ - need ../data/
        new_path = f"../data/{filename}"
    elif '/' in path:
        # Check subdirectories
        if path.startswith('data/'):
            # Keep data/ paths as-is but add ../
            if not path.startswith('../'):
                new_path = f"../{path}"
            else:
                new_path = path
        elif path.startswith('docs/'):
            # Remove docs/ prefix
            new_path = path.replace('docs/', '', 1)
        elif path.startswith('../'):
            # Already has ../ - keep it
            new_path = path
        else:
            # Try to infer
            parts = path.split('/')
            if len(parts) == 2:  # e.g., "improvement/FILE.md"
                # Check if subdirectory exists
                if (Path('docs') / parts[0]).exists():
                    new_path = path  # Keep as-is
                else:
                    new_path = f"../{path}"
            else:
                new_path = path
    else:
        # Single filename not found - assume root
        new_path = f"../{filename}"
    
    # Only replace if different
    if new_path != path:
        fixes.append((path, new_path))
        return f"[{text}]({new_path})"
    
    return full

# Fix all markdown links
pattern = r'\[([^\]]+)\]\(([^)]+)\)'
new_content = re.sub(pattern, fix_link, content)

# Write back
index_path.write_text(new_content, encoding='utf-8')

print(f"\nFixed {len(fixes)} links")
print("\nSample fixes:")
for old, new in fixes[:10]:
    print(f"  {old} → {new}")

if len(fixes) > 10:
    print(f"  ... and {len(fixes) - 10} more")
