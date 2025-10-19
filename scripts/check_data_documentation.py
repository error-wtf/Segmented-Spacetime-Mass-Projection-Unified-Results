#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Documentation Completeness Checker

Verifies comprehensive documentation of all data sources and processing

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import re

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Essential data documentation elements
REQUIRED_ELEMENTS = {
    'data_sources': [
        'GAIA', 'real_data_full.csv', 'source catalog',
        'observation', 'dataset'
    ],
    'preprocessing': [
        'filter', 'clean', 'preprocess', 'quality check',
        'validation', 'outlier'
    ],
    'columns': [
        'column', 'field', 'variable', 'parameter',
        'f_emit', 'f_obs', 'mass', 'redshift'
    ],
    'quality': [
        'quality', 'metric', 'statistics', 'summary',
        'validation result', 'test result'
    ],
    'issues': [
        'warning', 'limitation', 'missing', 'gap',
        'todo', 'issue', 'problem'
    ]
}

def analyze_data_doc(filepath):
    """Analyze a data documentation file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().lower()
        
        results = {}
        for category, keywords in REQUIRED_ELEMENTS.items():
            found = sum(1 for kw in keywords if kw in content)
            results[category] = {
                'found': found,
                'total': len(keywords),
                'coverage': found / len(keywords) if keywords else 0
            }
        
        # Check for specific data files mentioned
        data_files = re.findall(r'[\w_]+\.csv', content, re.IGNORECASE)
        
        # Check for code examples
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        
        # Check for tables
        tables = len(re.findall(r'\|[^\n]+\|', content))
        
        return {
            'categories': results,
            'data_files_mentioned': len(set(data_files)),
            'code_examples': code_blocks,
            'tables': tables,
            'size_kb': filepath.stat().st_size / 1024,
            'lines': content.count('\n')
        }
    except Exception as e:
        return None

def main():
    """Check data documentation completeness"""
    print("="*80)
    print("DATA DOCUMENTATION COMPLETENESS CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Find all DATA-related markdown files
    data_docs = []
    for pattern in ['*DATA*.md', '*data*.md']:
        data_docs.extend(root.glob(pattern))
        data_docs.extend((root / 'data').glob('**/*.md'))
        data_docs.extend((root / 'tests').glob('**/*DATA*.md'))
    
    # Remove duplicates
    data_docs = list(set(data_docs))
    
    print(f"Found {len(data_docs)} data-related documentation files")
    print()
    
    # Analyze each
    results = {}
    for doc in sorted(data_docs):
        rel_path = doc.relative_to(root)
        print(f"Analyzing: {rel_path}...", end=' ')
        
        analysis = analyze_data_doc(doc)
        if analysis:
            results[str(rel_path)] = analysis
            print("✅")
        else:
            print("⚠️  Error")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'DATA_DOCUMENTATION_COMPLETENESS.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Data Documentation Completeness Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Analyzed:** {len(results)}\n\n")
        f.write("---\n\n")
        
        # Overall statistics
        f.write("## 📊 Overall Statistics\n\n")
        
        total_files = len(results)
        total_size = sum(r['size_kb'] for r in results.values())
        total_lines = sum(r['lines'] for r in results.values())
        
        f.write(f"- **Total Documentation Files:** {total_files}\n")
        f.write(f"- **Total Size:** {total_size:.1f} KB\n")
        f.write(f"- **Total Lines:** {total_lines:,}\n\n")
        
        # Category coverage
        f.write("### Coverage by Category\n\n")
        
        category_totals = {}
        for category in REQUIRED_ELEMENTS.keys():
            found_total = sum(r['categories'][category]['found'] for r in results.values())
            possible_total = sum(r['categories'][category]['total'] for r in results.values())
            coverage = (found_total / possible_total * 100) if possible_total > 0 else 0
            category_totals[category] = {
                'found': found_total,
                'total': possible_total,
                'coverage': coverage
            }
        
        f.write("| Category | Mentions | Coverage |\n")
        f.write("|----------|----------|----------|\n")
        for cat, data in category_totals.items():
            filled = int(data['coverage'] / 10)
            bar = '█' * filled + '░' * (10 - filled)
            f.write(f"| {cat.replace('_', ' ').title()} | {data['found']}/{data['total']} | `[{bar}]` {data['coverage']:.1f}% |\n")
        f.write("\n")
        
        # Top documents by completeness
        f.write("## 🏆 Most Comprehensive Documents\n\n")
        
        # Calculate completeness score
        for filepath, data in results.items():
            total_coverage = sum(cat['coverage'] for cat in data['categories'].values()) / len(data['categories'])
            data['completeness'] = total_coverage
        
        top_docs = sorted(results.items(), key=lambda x: -x[1]['completeness'])[:10]
        
        f.write("| Document | Size | Coverage | Features |\n")
        f.write("|----------|------|----------|----------|\n")
        for filepath, data in top_docs:
            name = Path(filepath).name
            size = data['size_kb']
            coverage = data['completeness'] * 100
            features = f"{data['code_examples']} code, {data['tables']} tables, {data['data_files_mentioned']} files"
            f.write(f"| {name} | {size:.1f}KB | {coverage:.1f}% | {features} |\n")
        f.write("\n")
        
        # Documents needing improvement
        f.write("## ⚠️  Documents Needing Enhancement\n\n")
        
        weak_docs = [(f, d) for f, d in results.items() if d['completeness'] < 0.3]
        
        if weak_docs:
            f.write(f"**Found {len(weak_docs)} documents with <30% coverage:**\n\n")
            for filepath, data in sorted(weak_docs, key=lambda x: x[1]['completeness'])[:10]:
                name = Path(filepath).name
                coverage = data['completeness'] * 100
                f.write(f"- **{name}** ({coverage:.1f}% coverage)\n")
                
                # Identify missing categories
                missing = [cat for cat, vals in data['categories'].items() 
                          if vals['coverage'] < 0.2]
                if missing:
                    f.write(f"  - Missing: {', '.join(missing)}\n")
            f.write("\n")
        else:
            f.write("✅ All documents have adequate coverage!\n\n")
        
        # Key findings
        f.write("## 🔍 Key Findings\n\n")
        
        # Data sources mentioned
        total_data_files = sum(r['data_files_mentioned'] for r in results.values())
        f.write(f"### Data Files Referenced\n\n")
        f.write(f"- **Total .csv files mentioned:** {total_data_files}\n")
        f.write(f"- **Average per document:** {total_data_files/len(results):.1f}\n\n")
        
        # Code examples
        total_code = sum(r['code_examples'] for r in results.values())
        f.write(f"### Code Examples\n\n")
        f.write(f"- **Total code blocks:** {total_code}\n")
        f.write(f"- **Documents with code:** {sum(1 for r in results.values() if r['code_examples'] > 0)}/{len(results)}\n\n")
        
        # Tables
        total_tables = sum(r['tables'] for r in results.values())
        f.write(f"### Tables\n\n")
        f.write(f"- **Total tables:** {total_tables}\n")
        f.write(f"- **Documents with tables:** {sum(1 for r in results.values() if r['tables'] > 0)}/{len(results)}\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### High Priority\n\n")
        
        if category_totals['data_sources']['coverage'] < 70:
            f.write("- **Improve data source documentation**\n")
            f.write("  - Document all input files\n")
            f.write("  - Add source provenance\n")
            f.write("  - Include access information\n\n")
        
        if category_totals['preprocessing']['coverage'] < 70:
            f.write("- **Enhance preprocessing documentation**\n")
            f.write("  - Document all cleaning steps\n")
            f.write("  - Explain quality checks\n")
            f.write("  - Add validation procedures\n\n")
        
        if category_totals['columns']['coverage'] < 70:
            f.write("- **Complete column documentation**\n")
            f.write("  - Define all data fields\n")
            f.write("  - Add units and types\n")
            f.write("  - Include examples\n\n")
        
        f.write("### Medium Priority\n\n")
        f.write("- Add more code examples\n")
        f.write("- Include data flow diagrams\n")
        f.write("- Enhance cross-references\n\n")
        
        f.write("### Low Priority\n\n")
        f.write("- Add visualizations\n")
        f.write("- Expand known issues section\n")
        f.write("- Include historical context\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_data_documentation.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Files analyzed: {len(results)}")
    print(f"  Total size: {total_size:.1f} KB")
    print(f"  Total lines: {total_lines:,}")
    print()
    print("Category Coverage:")
    for cat, data in category_totals.items():
        print(f"  {cat.replace('_', ' ').title()}: {data['coverage']:.1f}%")

if __name__ == '__main__':
    main()
