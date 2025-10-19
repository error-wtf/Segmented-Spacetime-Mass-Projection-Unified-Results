#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Documentation Completeness Checker

Verifies that physics tests have comprehensive documentation

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

# Essential test documentation elements
REQUIRED_ELEMENTS = {
    'test_purpose': [
        'test', 'verify', 'check', 'validate',
        'measure', 'compare', 'ensure'
    ],
    'physics_concepts': [
        'physical', 'interpretation', 'meaning',
        'GR', 'general relativity', 'schwarzschild',
        'energy condition', 'metric', 'curvature'
    ],
    'expected_results': [
        'expect', 'should', 'result', 'outcome',
        'prediction', 'theoretical', 'value'
    ],
    'interpretation': [
        'interpretation', 'means', 'indicates',
        'shows', 'demonstrates', 'proves'
    ],
    'references': [
        'see', 'reference', 'compare', 'documented',
        'described in', 'formula', 'equation'
    ]
}

def analyze_test_file(filepath):
    """Analyze a test Python file for documentation"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Check docstrings
        docstrings = re.findall(r'"""[\s\S]*?"""', content)
        total_docstring_lines = sum(ds.count('\n') for ds in docstrings)
        
        # Check comments
        comments = re.findall(r'#.*$', content, re.MULTILINE)
        
        # Check for "Physical Interpretation" sections
        phys_interp = len(re.findall(r'[Pp]hysical [Ii]nterpretation', content))
        
        # Check for assert statements
        asserts = len(re.findall(r'assert ', content))
        
        # Check for print statements explaining results
        result_prints = len(re.findall(r'print\(["\'].*[Rr]esult', content))
        
        # Category coverage
        coverage = {}
        content_lower = content.lower()
        for category, keywords in REQUIRED_ELEMENTS.items():
            found = sum(1 for kw in keywords if kw in content_lower)
            coverage[category] = {
                'found': found,
                'total': len(keywords),
                'coverage': found / len(keywords) if keywords else 0
            }
        
        return {
            'docstrings': len(docstrings),
            'docstring_lines': total_docstring_lines,
            'comments': len(comments),
            'physical_interpretations': phys_interp,
            'asserts': asserts,
            'result_explanations': result_prints,
            'coverage': coverage,
            'size_kb': filepath.stat().st_size / 1024,
            'lines': content.count('\n')
        }
    except Exception as e:
        return None

def analyze_test_doc(filepath):
    """Analyze test documentation markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Check for test lists
        test_lists = len(re.findall(r'^\s*[-*]\s+test', content, re.MULTILINE | re.IGNORECASE))
        
        # Check for results/outcomes
        results_sections = len(re.findall(r'result|outcome|finding', content, re.IGNORECASE))
        
        # Check for physics explanations
        physics_exp = len(re.findall(r'physical|interpretation|GR|relativity', content, re.IGNORECASE))
        
        return {
            'test_lists': test_lists,
            'results_sections': results_sections,
            'physics_explanations': physics_exp,
            'size_kb': filepath.stat().st_size / 1024,
            'lines': content.count('\n')
        }
    except Exception as e:
        return None

def main():
    """Check test documentation completeness"""
    print("="*80)
    print("TEST DOCUMENTATION COMPLETENESS CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Find test Python files
    test_files = []
    for pattern in ['test_*.py', '*_test.py']:
        test_files.extend(root.glob(f'**/{pattern}'))
    
    # Find test documentation
    test_docs = []
    for pattern in ['*TEST*.md', '*test*.md']:
        test_docs.extend(root.glob(pattern))
        test_docs.extend((root / 'tests').glob('**/*.md'))
    
    test_files = [f for f in test_files if '__pycache__' not in str(f)]
    test_docs = list(set(test_docs))
    
    print(f"Found {len(test_files)} test files (.py)")
    print(f"Found {len(test_docs)} test documentation files (.md)")
    print()
    
    # Analyze test files
    print("Analyzing test files...")
    test_results = {}
    for test_file in sorted(test_files)[:20]:  # Limit to first 20 for speed
        rel_path = test_file.relative_to(root)
        analysis = analyze_test_file(test_file)
        if analysis:
            test_results[str(rel_path)] = analysis
    
    # Analyze test docs
    print("Analyzing test documentation...")
    doc_results = {}
    for doc_file in sorted(test_docs):
        rel_path = doc_file.relative_to(root)
        analysis = analyze_test_doc(doc_file)
        if analysis:
            doc_results[str(rel_path)] = analysis
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'TEST_DOCUMENTATION_COMPLETENESS.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Test Documentation Completeness Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Test Files Analyzed:** {len(test_results)}\n")
        f.write(f"**Test Docs Analyzed:** {len(doc_results)}\n\n")
        f.write("---\n\n")
        
        # Statistics
        f.write("## 📊 Test Code Documentation\n\n")
        
        if test_results:
            total_docstrings = sum(r['docstrings'] for r in test_results.values())
            total_comments = sum(r['comments'] for r in test_results.values())
            total_phys_interp = sum(r['physical_interpretations'] for r in test_results.values())
            total_asserts = sum(r['asserts'] for r in test_results.values())
            
            f.write(f"- **Total Test Files:** {len(test_results)}\n")
            f.write(f"- **Docstrings:** {total_docstrings} ({total_docstrings/len(test_results):.1f} avg/file)\n")
            f.write(f"- **Comments:** {total_comments} ({total_comments/len(test_results):.1f} avg/file)\n")
            f.write(f"- **Physical Interpretations:** {total_phys_interp}\n")
            f.write(f"- **Assert Statements:** {total_asserts}\n\n")
            
            # Category coverage across all files
            f.write("### Documentation Coverage\n\n")
            
            category_totals = {}
            for category in REQUIRED_ELEMENTS.keys():
                found_total = sum(r['coverage'][category]['found'] for r in test_results.values())
                possible_total = sum(r['coverage'][category]['total'] for r in test_results.values())
                coverage = (found_total / possible_total * 100) if possible_total > 0 else 0
                category_totals[category] = coverage
            
            f.write("| Category | Coverage |\n")
            f.write("|----------|----------|\n")
            for cat, pct in category_totals.items():
                filled = int(pct / 10)
                bar = '█' * filled + '░' * (10 - filled)
                f.write(f"| {cat.replace('_', ' ').title()} | `[{bar}]` {pct:.1f}% |\n")
            f.write("\n")
        
        # Best documented tests
        f.write("## 🏆 Best Documented Tests\n\n")
        
        if test_results:
            # Calculate documentation score
            for filepath, data in test_results.items():
                score = (
                    data['docstring_lines'] * 2 +
                    data['comments'] +
                    data['physical_interpretations'] * 10 +
                    data['result_explanations'] * 5
                )
                data['doc_score'] = score
            
            top_tests = sorted(test_results.items(), key=lambda x: -x[1]['doc_score'])[:10]
            
            f.write("| Test File | Docstrings | Phys. Interp. | Score |\n")
            f.write("|-----------|------------|---------------|-------|\n")
            for filepath, data in top_tests:
                name = Path(filepath).name
                docs = data['docstrings']
                phys = data['physical_interpretations']
                score = data['doc_score']
                f.write(f"| {name} | {docs} | {phys} | {score} |\n")
            f.write("\n")
        
        # Test documentation files
        f.write("## 📄 Test Documentation Files\n\n")
        
        if doc_results:
            total_test_lists = sum(r['test_lists'] for r in doc_results.values())
            total_results = sum(r['results_sections'] for r in doc_results.values())
            total_physics = sum(r['physics_explanations'] for r in doc_results.values())
            
            f.write(f"- **Total Doc Files:** {len(doc_results)}\n")
            f.write(f"- **Test Lists:** {total_test_lists}\n")
            f.write(f"- **Results Sections:** {total_results}\n")
            f.write(f"- **Physics Explanations:** {total_physics}\n\n")
            
            # List docs
            f.write("### Documentation Files\n\n")
            for filepath, data in sorted(doc_results.items()):
                name = Path(filepath).name
                size = data['size_kb']
                f.write(f"- **{name}** ({size:.1f} KB) - {data['test_lists']} tests listed\n")
            f.write("\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### High Priority\n\n")
        
        if test_results:
            poorly_doc = [(f, d) for f, d in test_results.items() 
                         if d['physical_interpretations'] == 0]
            if poorly_doc:
                f.write(f"- **Add Physical Interpretations** to {len(poorly_doc)} tests\n")
                f.write("  - Every physics test should explain what results mean\n")
                f.write("  - Add 'Physical Interpretation:' sections\n")
                f.write("  - Compare with theoretical predictions\n\n")
        
        f.write("### Medium Priority\n\n")
        f.write("- Expand docstrings with physics context\n")
        f.write("- Add expected value ranges\n")
        f.write("- Include GR comparisons\n\n")
        
        f.write("### Low Priority\n\n")
        f.write("- Add more inline comments\n")
        f.write("- Create test result visualizations\n")
        f.write("- Cross-reference theory docs\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_test_documentation.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print("Summary:")
    if test_results:
        print(f"  Test files: {len(test_results)}")
        print(f"  Physical interpretations: {sum(r['physical_interpretations'] for r in test_results.values())}")
        print(f"  Average doc score: {sum(r.get('doc_score', 0) for r in test_results.values()) / len(test_results):.1f}")
    if doc_results:
        print(f"  Doc files: {len(doc_results)}")

if __name__ == '__main__':
    main()
