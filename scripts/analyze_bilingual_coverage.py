#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilingual Coverage Analysis

Analyzes which documentation files are available in both EN and DE
Identifies translation priorities and coverage gaps

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# UTF-8 für Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Windows stdout UTF-8 fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Core documentation files that should be bilingual
CORE_DOCS = {
    'theory_code': [
        'docs/PHYSICS_FOUNDATIONS.md',
        'docs/MATHEMATICAL_FORMULAS.md',
        'docs/CODE_IMPLEMENTATION_GUIDE.md',
        'docs/EXAMPLES_AND_APPLICATIONS.md',
        'docs/THEORY_AND_CODE_INDEX.md',
    ],
    'data': [
        'DATA_IMPROVEMENT_ROADMAP.md',
        'DATA_IMPROVEMENT_STATUS_REPORT.md',
        'TODO_DATA_INTEGRATION.md',
        'COMPREHENSIVE_DATA_ANALYSIS.md',
        'DATA_CHANGELOG.md',
    ],
    'testing': [
        'TEST_SUITE_VERIFICATION.md',
        'LOGGING_SYSTEM_README.md',
        'tests/README_TESTS.md',
    ],
    'installation': [
        'INSTALL_README.md',
        'COLAB_README.md',
        'CROSS_PLATFORM_COMPATIBILITY_ANALYSIS.md',
    ]
}

def find_bilingual_pairs(root):
    """Find all EN/DE documentation pairs"""
    pairs = []
    missing_translations = {'en_only': [], 'de_only': []}
    
    # Scan all markdown files
    all_md = list(root.rglob('*.md'))
    
    # Build index
    by_stem = defaultdict(list)
    for filepath in all_md:
        if any(x in str(filepath) for x in ['.venv', '__pycache__', '.git']):
            continue
        
        stem = filepath.stem
        parent = filepath.parent
        
        # Group by stem (removing _DE/_EN suffix)
        if stem.endswith('_DE'):
            base = stem[:-3]
            by_stem[(parent, base)].append(('de', filepath))
        elif stem.endswith('_EN'):
            base = stem[:-3]
            by_stem[(parent, base)].append(('en', filepath))
        else:
            # Check if EN/DE variants exist
            de_path = parent / f'{stem}_DE.md'
            en_path = parent / f'{stem}_EN.md'
            
            if de_path.exists() or en_path.exists():
                by_stem[(parent, stem)].append(('base', filepath))
                if de_path.exists():
                    by_stem[(parent, stem)].append(('de', de_path))
                if en_path.exists():
                    by_stem[(parent, stem)].append(('en', en_path))
    
    # Analyze pairs
    for (parent, base), files in by_stem.items():
        langs = {lang for lang, _ in files}
        paths = {lang: path for lang, path in files}
        
        if 'de' in langs and 'en' in langs:
            # Complete pair
            pairs.append({
                'base': base,
                'de': paths['de'],
                'en': paths['en'],
                'parent': parent
            })
        elif 'en' in langs and 'de' not in langs:
            # EN only
            missing_translations['en_only'].append(paths['en'])
        elif 'de' in langs and 'en' not in langs:
            # DE only
            missing_translations['de_only'].append(paths['de'])
    
    return pairs, missing_translations

def check_core_docs_coverage(root, pairs):
    """Check which core docs are bilingual"""
    coverage = {}
    
    for category, files in CORE_DOCS.items():
        category_coverage = []
        for doc in files:
            doc_path = root / doc
            
            # Check if exists
            if not doc_path.exists():
                category_coverage.append({
                    'file': doc,
                    'status': 'missing',
                    'bilingual': False
                })
                continue
            
            # Check if bilingual
            is_bilingual = False
            for pair in pairs:
                if str(doc_path) in [str(pair['en']), str(pair['de'])]:
                    is_bilingual = True
                    break
                # Also check base name
                if doc_path.stem in [pair['en'].stem, pair['de'].stem]:
                    is_bilingual = True
                    break
            
            category_coverage.append({
                'file': doc,
                'status': 'exists',
                'bilingual': is_bilingual
            })
        
        coverage[category] = category_coverage
    
    return coverage

def main():
    """Analyze bilingual coverage"""
    print("="*80)
    print("BILINGUAL COVERAGE ANALYSIS")
    print("="*80)
    print()
    
    # Find root
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Find bilingual pairs
    print("Analyzing bilingual coverage...")
    pairs, missing = find_bilingual_pairs(root)
    
    print(f"✅ Bilingual pairs found: {len(pairs)}")
    print(f"📄 EN-only files: {len(missing['en_only'])}")
    print(f"📄 DE-only files: {len(missing['de_only'])}")
    print()
    
    # Check core docs
    print("Checking core documentation coverage...")
    core_coverage = check_core_docs_coverage(root, pairs)
    
    total_core = sum(len(cats) for cats in CORE_DOCS.values())
    bilingual_core = sum(
        1 for cat in core_coverage.values() 
        for doc in cat if doc['bilingual']
    )
    
    print(f"Core docs bilingual: {bilingual_core}/{total_core} ({bilingual_core/total_core*100:.1f}%)")
    print()
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'BILINGUAL_COVERAGE_ANALYSIS.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Bilingual Coverage Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Bilingual Pairs:** {len(pairs)}\n")
        f.write(f"**Coverage Goal:** 95% of core documentation\n\n")
        f.write("---\n\n")
        
        # Executive summary
        f.write("## 📊 Executive Summary\n\n")
        f.write(f"- **Bilingual Pairs:** {len(pairs)} documentation sets\n")
        f.write(f"- **EN-only Files:** {len(missing['en_only'])}\n")
        f.write(f"- **DE-only Files:** {len(missing['de_only'])}\n")
        f.write(f"- **Core Docs Coverage:** {bilingual_core}/{total_core} ({bilingual_core/total_core*100:.1f}%)\n\n")
        
        # Progress bar
        pct = bilingual_core / total_core
        filled = int(pct * 20)
        bar = '█' * filled + '░' * (20 - filled)
        f.write(f"**Core Coverage:** `[{bar}]` {pct*100:.1f}%\n\n")
        f.write("---\n\n")
        
        # Core documentation breakdown
        f.write("## 🎯 Core Documentation Status\n\n")
        
        for category, docs in core_coverage.items():
            f.write(f"### {category.replace('_', ' ').title()}\n\n")
            f.write("| File | Status | Bilingual |\n")
            f.write("|------|--------|----------|\n")
            
            for doc in docs:
                status_emoji = '✅' if doc['status'] == 'exists' else '❌'
                bilingual_emoji = '✅' if doc['bilingual'] else '❌'
                f.write(f"| {doc['file']} | {status_emoji} {doc['status']} | {bilingual_emoji} |\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # Complete bilingual pairs
        f.write("## ✅ Bilingual Documentation Pairs\n\n")
        f.write(f"**Total:** {len(pairs)} complete EN ↔ DE pairs\n\n")
        
        if pairs:
            # Group by directory
            by_dir = defaultdict(list)
            for pair in pairs:
                rel_parent = pair['parent'].relative_to(root)
                by_dir[str(rel_parent)].append(pair)
            
            for directory in sorted(by_dir.keys()):
                f.write(f"### {directory}/\n\n")
                for pair in sorted(by_dir[directory], key=lambda x: x['base']):
                    f.write(f"- **{pair['base']}**\n")
                    f.write(f"  - 🇬🇧 {pair['en'].name}\n")
                    f.write(f"  - 🇩🇪 {pair['de'].name}\n\n")
        
        f.write("---\n\n")
        
        # Translation gaps
        f.write("## 📝 Translation Priorities\n\n")
        
        if missing['en_only']:
            f.write("### High Priority (EN-only, should have DE)\n\n")
            
            # Filter for core/important docs
            important = []
            for filepath in missing['en_only']:
                rel_path = filepath.relative_to(root)
                # Check if in core docs
                if any(str(rel_path) == core_doc for category in CORE_DOCS.values() for core_doc in category):
                    important.append(filepath)
            
            if important:
                f.write("**Core documentation needing translation:**\n\n")
                for filepath in important:
                    rel_path = filepath.relative_to(root)
                    size_kb = filepath.stat().st_size / 1024
                    f.write(f"- `{rel_path}` ({size_kb:.1f} KB)\n")
                f.write("\n")
            
            # Show some other EN-only files
            others = [f for f in missing['en_only'] if f not in important][:10]
            if others:
                f.write("**Other EN-only files (sample):**\n\n")
                for filepath in others:
                    rel_path = filepath.relative_to(root)
                    f.write(f"- `{rel_path}`\n")
                if len(missing['en_only']) > len(important) + 10:
                    f.write(f"\n*...and {len(missing['en_only']) - len(important) - 10} more*\n")
                f.write("\n")
        
        if missing['de_only']:
            f.write("### Medium Priority (DE-only, may need EN)\n\n")
            for filepath in missing['de_only'][:10]:
                rel_path = filepath.relative_to(root)
                f.write(f"- `{rel_path}`\n")
            if len(missing['de_only']) > 10:
                f.write(f"\n*...and {len(missing['de_only']) - 10} more*\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### 1. Complete Core Documentation (HIGH PRIORITY)\n\n")
        non_bilingual = [doc for cat in core_coverage.values() for doc in cat if not doc['bilingual']]
        if non_bilingual:
            f.write(f"- {len(non_bilingual)} core docs not yet bilingual\n")
            f.write("- Focus on Theory & Code category first\n")
            f.write("- Then Data Documentation\n")
            f.write("- Then Installation & Testing\n\n")
        else:
            f.write("- ✅ All core docs are bilingual!\n")
            f.write("- Maintain synchronization on updates\n\n")
        
        f.write("### 2. Translation Workflow\n\n")
        f.write("**For new documentation:**\n")
        f.write("1. Write in primary language (EN or DE)\n")
        f.write("2. Create translated version immediately\n")
        f.write("3. Add language switcher to both\n")
        f.write("4. Update DOCUMENTATION_INDEX\n\n")
        
        f.write("**For existing docs:**\n")
        f.write("1. Prioritize core documentation\n")
        f.write("2. Use consistent naming (_EN.md / _DE.md)\n")
        f.write("3. Ensure 1:1 content mapping\n")
        f.write("4. Verify technical terms using TERMINOLOGY_GLOSSARY\n\n")
        
        f.write("### 3. Quality Assurance\n\n")
        f.write("- Compare line counts (EN vs DE should be similar)\n")
        f.write("- Check for outdated translations\n")
        f.write("- Verify language switcher links\n")
        f.write("- Test all cross-references\n\n")
        
        f.write("### 4. Maintenance\n\n")
        f.write("- Run this analysis after major updates\n")
        f.write("- Track coverage metrics over time\n")
        f.write("- Set target: 95%+ core docs bilingual\n")
        f.write("- Document translation standards\n\n")
        
        f.write("---\n\n")
        
        # Summary
        f.write("## ✅ Summary\n\n")
        
        if bilingual_core / total_core >= 0.95:
            f.write("🎉 **EXCELLENT:** Core documentation is 95%+ bilingual!\n\n")
        elif bilingual_core / total_core >= 0.75:
            f.write("✅ **GOOD:** Most core documentation is bilingual.\n\n")
        elif bilingual_core / total_core >= 0.50:
            f.write("⚠️ **NEEDS WORK:** Core documentation coverage below 75%.\n\n")
        else:
            f.write("❌ **PRIORITY:** Core documentation needs significant translation work.\n\n")
        
        f.write(f"**Current Status:**\n")
        f.write(f"- Bilingual pairs: {len(pairs)}\n")
        f.write(f"- Core coverage: {bilingual_core}/{total_core} ({bilingual_core/total_core*100:.1f}%)\n")
        f.write(f"- Goal: 95%+ core docs bilingual\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/analyze_bilingual_coverage.py`\n")
        f.write("**Phase 1 Complete!** Ready for Phase 2: Content Completeness\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"✅ Report generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Bilingual pairs: {len(pairs)}")
    print(f"  Core coverage: {bilingual_core}/{total_core} ({bilingual_core/total_core*100:.1f}%)")
    
    if bilingual_core / total_core >= 0.95:
        print("  Status: ✅ EXCELLENT (95%+ coverage)")
    elif bilingual_core / total_core >= 0.75:
        print("  Status: ✅ GOOD (75%+ coverage)")
    else:
        print("  Status: ⚠️  NEEDS IMPROVEMENT")
    
    print()
    print("🎉 PHASE 1 COMPLETE!")
    print("   Next: Review all 5 audit reports")
    print("   Then: Start Phase 2 (Content Completeness)")

if __name__ == '__main__':
    main()
