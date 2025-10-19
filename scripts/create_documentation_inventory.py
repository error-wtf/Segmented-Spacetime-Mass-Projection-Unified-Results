#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Inventory Generator

Creates a complete audit of all markdown documentation files
with metadata: lines, language, category, last updated, bilingual status

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import re

# UTF-8 für Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Windows stdout UTF-8 fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

def detect_language(filepath):
    """Detect if file is English, German, or bilingual"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(2000)  # First 2000 chars
            
        # Check for language indicators
        de_indicators = ['Erstellt:', 'Aktualisiert:', 'Übersicht', 'Ziel:', 'Zusammenfassung']
        en_indicators = ['Created:', 'Updated:', 'Overview', 'Goal:', 'Summary']
        
        de_count = sum(1 for ind in de_indicators if ind in content)
        en_count = sum(1 for ind in en_indicators if ind in content)
        
        if de_count > 0 and en_count > 0:
            return 'Bilingual'
        elif de_count > en_count:
            return 'DE'
        elif en_count > de_count:
            return 'EN'
        else:
            return 'Unknown'
    except Exception as e:
        return 'Error'

def categorize_file(filepath):
    """Categorize documentation file by content/location"""
    path_str = str(filepath).lower()
    filename = filepath.name.lower()
    
    # Category rules
    if 'docs/theory' in path_str or 'papers/' in path_str:
        return 'Theory/Papers'
    elif any(x in filename for x in ['physics', 'mathematical', 'theory', 'code_implementation', 'examples']):
        return 'Theory & Code'
    elif any(x in filename for x in ['data_', 'comprehensive_data', 'sources']):
        return 'Data Documentation'
    elif any(x in filename for x in ['test_', 'logging', 'verification']):
        return 'Testing'
    elif any(x in filename for x in ['install', 'colab', 'cross_platform', 'compatibility']):
        return 'Installation & Setup'
    elif any(x in filename for x in ['changelog', 'git_commit', 'bugfix', 'release']):
        return 'Release & Changes'
    elif any(x in filename for x in ['pipeline', 'summary', 'cli', 'api']):
        return 'Technical'
    elif 'readme' in filename:
        return 'README'
    else:
        return 'Other'

def count_lines(filepath):
    """Count lines in file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return len(f.readlines())
    except:
        return 0

def get_last_modified(filepath):
    """Get last modification date"""
    try:
        timestamp = os.path.getmtime(filepath)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return 'Unknown'

def check_bilingual_pair(filepath):
    """Check if file has EN/DE counterpart"""
    path = Path(filepath)
    name = path.stem
    
    if name.endswith('_DE'):
        counterpart = path.parent / (name[:-3] + '.md')
        return 'DE version' if counterpart.exists() else 'DE only'
    elif name.endswith('_EN'):
        counterpart = path.parent / (name[:-3] + '.md')
        return 'EN version' if counterpart.exists() else 'EN only'
    else:
        en_ver = path.parent / (name + '_EN.md')
        de_ver = path.parent / (name + '_DE.md')
        if en_ver.exists() and de_ver.exists():
            return 'Has both EN/DE'
        elif en_ver.exists():
            return 'Has EN version'
        elif de_ver.exists():
            return 'Has DE version'
        else:
            return 'Single version'

def main():
    """Create documentation inventory"""
    print("="*80)
    print("DOCUMENTATION INVENTORY GENERATOR")
    print("="*80)
    print()
    
    # Find root directory
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Find all .md files
    md_files = list(root.rglob('*.md'))
    print(f"Found {len(md_files)} markdown files")
    print()
    
    # Collect metadata
    inventory = []
    for filepath in md_files:
        rel_path = filepath.relative_to(root)
        
        # Skip certain directories
        if any(x in str(rel_path) for x in ['.venv', '__pycache__', 'node_modules', '.git']):
            continue
        
        metadata = {
            'path': str(rel_path),
            'filename': filepath.name,
            'category': categorize_file(filepath),
            'lines': count_lines(filepath),
            'language': detect_language(filepath),
            'last_modified': get_last_modified(filepath),
            'bilingual_status': check_bilingual_pair(filepath),
            'size_kb': filepath.stat().st_size / 1024
        }
        inventory.append(metadata)
    
    # Sort by category, then by lines (desc)
    inventory.sort(key=lambda x: (x['category'], -x['lines']))
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'DOCUMENTATION_AUDIT_REPORT.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Documentation Audit Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Repository:** Segmented-Spacetime-Mass-Projection-Unified-Results\n")
        f.write(f"**Total Files:** {len(inventory)}\n\n")
        f.write("---\n\n")
        
        # Summary statistics
        f.write("## 📊 Summary Statistics\n\n")
        
        total_lines = sum(x['lines'] for x in inventory)
        total_size = sum(x['size_kb'] for x in inventory)
        
        f.write(f"- **Total Markdown Files:** {len(inventory)}\n")
        f.write(f"- **Total Lines:** {total_lines:,}\n")
        f.write(f"- **Total Size:** {total_size:.1f} KB ({total_size/1024:.1f} MB)\n")
        f.write(f"- **Average Lines/File:** {total_lines/len(inventory):.0f}\n\n")
        
        # Language breakdown
        lang_counts = {}
        for item in inventory:
            lang = item['language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        f.write("### Language Distribution\n\n")
        for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
            pct = count / len(inventory) * 100
            f.write(f"- **{lang}:** {count} files ({pct:.1f}%)\n")
        f.write("\n")
        
        # Category breakdown
        cat_counts = {}
        cat_lines = {}
        for item in inventory:
            cat = item['category']
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            cat_lines[cat] = cat_lines.get(cat, 0) + item['lines']
        
        f.write("### Category Distribution\n\n")
        f.write("| Category | Files | Total Lines | Avg Lines |\n")
        f.write("|----------|-------|-------------|----------|\n")
        for cat in sorted(cat_counts.keys()):
            count = cat_counts[cat]
            lines = cat_lines[cat]
            avg = lines / count if count > 0 else 0
            f.write(f"| {cat} | {count} | {lines:,} | {avg:.0f} |\n")
        f.write("\n")
        
        # Bilingual status
        bil_counts = {}
        for item in inventory:
            status = item['bilingual_status']
            bil_counts[status] = bil_counts.get(status, 0) + 1
        
        f.write("### Bilingual Status\n\n")
        for status, count in sorted(bil_counts.items(), key=lambda x: -x[1]):
            pct = count / len(inventory) * 100
            f.write(f"- **{status}:** {count} files ({pct:.1f}%)\n")
        f.write("\n---\n\n")
        
        # Detailed inventory by category
        f.write("## 📋 Detailed Inventory\n\n")
        
        current_cat = None
        for item in inventory:
            if item['category'] != current_cat:
                current_cat = item['category']
                f.write(f"\n### {current_cat}\n\n")
                f.write("| File | Lines | Language | Bilingual | Last Modified |\n")
                f.write("|------|-------|----------|-----------|---------------|\n")
            
            f.write(f"| {item['path']} | {item['lines']:,} | {item['language']} | {item['bilingual_status']} | {item['last_modified']} |\n")
        
        f.write("\n---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        # Find large files (>1000 lines)
        large_files = [x for x in inventory if x['lines'] > 1000]
        if large_files:
            f.write("### Large Files (>1000 lines)\n\n")
            f.write("Consider splitting these into smaller, focused documents:\n\n")
            for item in sorted(large_files, key=lambda x: -x['lines'])[:10]:
                f.write(f"- `{item['path']}` ({item['lines']:,} lines)\n")
            f.write("\n")
        
        # Find English-only files
        en_only = [x for x in inventory if x['language'] == 'EN' and x['category'] in ['Theory & Code', 'Data Documentation', 'Testing']]
        if en_only:
            f.write("### Translation Candidates\n\n")
            f.write("Core documentation files that should be translated to German:\n\n")
            for item in sorted(en_only, key=lambda x: -x['lines'])[:15]:
                f.write(f"- `{item['path']}` ({item['lines']:,} lines, {item['category']})\n")
            f.write("\n")
        
        # Find outdated files (modified >30 days ago)
        today = datetime.now()
        outdated = []
        for item in inventory:
            if item['last_modified'] != 'Unknown':
                try:
                    mod_date = datetime.strptime(item['last_modified'], '%Y-%m-%d')
                    days_old = (today - mod_date).days
                    if days_old > 30 and item['category'] in ['Theory & Code', 'Data Documentation']:
                        outdated.append((item, days_old))
                except:
                    pass
        
        if outdated:
            f.write("### Potentially Outdated Files (>30 days)\n\n")
            f.write("Core documentation that may need review:\n\n")
            for item, days in sorted(outdated, key=lambda x: -x[1])[:10]:
                f.write(f"- `{item['path']}` (Last updated: {item['last_modified']}, {days} days ago)\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/create_documentation_inventory.py`\n")
        f.write(f"**Report Path:** `docs/improvement/DOCUMENTATION_AUDIT_REPORT.md`\n")
        f.write("\n© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"✅ Report generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Total files: {len(inventory)}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Categories: {len(cat_counts)}")
    print()
    print("Next steps:")
    print("  1. Review DOCUMENTATION_AUDIT_REPORT.md")
    print("  2. Identify translation priorities")
    print("  3. Start Phase 1.2: Mathematical Notation Audit")

if __name__ == '__main__':
    main()
