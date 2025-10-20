#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Explanation Gap Checker

Identifies mathematical formulas and concepts that lack detailed explanations.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
import io

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Patterns to check
CHECKS = {
    'formula_without_context': {
        'pattern': r'^```\s*\n[^`]+\n```\s*$',
        'description': 'Formula without explanation before or after',
        'severity': 'medium'
    },
    'undefined_variable': {
        'pattern': r'[A-Za-z_][A-Za-z0-9_]*\([^)]*\)|[A-Z]_[a-z]+',
        'description': 'Variable that might not be defined',
        'severity': 'low'
    },
    'missing_units': {
        'pattern': r'=\s*[\d.]+\s*(?!m|s|kg|J|K|N)',
        'description': 'Number without explicit units',
        'severity': 'low'
    },
    'complex_without_breakdown': {
        'pattern': r'[∫∑∏∂∇]',
        'description': 'Complex operator without step-by-step',
        'severity': 'high'
    }
}


def analyze_file(filepath: Path) -> Dict:
    """Analyze a single file for explanation gaps."""
    
    results = {
        'file': str(filepath),
        'gaps': [],
        'score': 100
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for formulas without context
        in_code_block = False
        prev_line = ""
        next_context = False
        
        for i, line in enumerate(lines):
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                
                # Check if previous line explains formula
                if in_code_block and prev_line.strip() and not prev_line.strip().startswith('#'):
                    # Good: has context before
                    pass
                elif not in_code_block:
                    # Check if next line explains
                    if i+1 < len(lines):
                        next_line = lines[i+1].strip()
                        if not next_line or next_line.startswith('#') or next_line.startswith('**'):
                            results['gaps'].append({
                                'line': i+1,
                                'type': 'formula_without_explanation',
                                'severity': 'medium',
                                'suggestion': 'Add explanation after this formula'
                            })
                            results['score'] -= 2
            
            # Check for complex math without breakdown
            if re.search(r'[∫∑∏∂∇]', line) and not in_code_block:
                # Check if followed by derivation
                if i+2 < len(lines):
                    following = '\n'.join(lines[i+1:i+3])
                    if 'step' not in following.lower() and 'derivation' not in following.lower():
                        results['gaps'].append({
                            'line': i+1,
                            'type': 'complex_operator_no_steps',
                            'severity': 'high',
                            'suggestion': 'Add step-by-step derivation'
                        })
                        results['score'] -= 5
            
            prev_line = line
        
        # Check for "Where:" sections completeness
        where_sections = re.finditer(r'^Where:\s*$', content, re.MULTILINE)
        for match in where_sections:
            start = match.end()
            # Check next 5 lines
            section_end = content.find('\n\n', start)
            if section_end == -1:
                section_end = len(content)
            where_content = content[start:section_end]
            
            # Count definitions
            definitions = len(re.findall(r'^\s*[-•]\s+\w+', where_content, re.MULTILINE))
            if definitions < 2:
                line_num = content[:start].count('\n') + 1
                results['gaps'].append({
                    'line': line_num,
                    'type': 'incomplete_where_section',
                    'severity': 'medium',
                    'suggestion': 'Expand "Where:" section with all variables'
                })
                results['score'] -= 3
    
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
    
    return results


def main():
    """Main analysis."""
    
    # Files to check
    important_docs = [
        'docs/MATHEMATICAL_FORMULAS.md',
        'docs/PHYSICS_FOUNDATIONS.md',
        'docs/CODE_IMPLEMENTATION_GUIDE.md',
        'docs/THEORY_AND_CODE_INDEX.md'
    ]
    
    print("=" * 80)
    print("EXPLANATION GAP ANALYSIS")
    print("=" * 80)
    print()
    
    all_results = []
    
    for doc in important_docs:
        filepath = Path(doc)
        if not filepath.exists():
            print(f"⚠️  {doc} not found")
            continue
        
        print(f"📄 Analyzing: {doc}")
        results = analyze_file(filepath)
        all_results.append(results)
        
        if results['gaps']:
            print(f"   Score: {results['score']}/100")
            print(f"   Gaps found: {len(results['gaps'])}")
            for gap in results['gaps'][:3]:  # Show first 3
                print(f"   - Line {gap['line']}: {gap['type']} ({gap['severity']})")
                print(f"     → {gap['suggestion']}")
        else:
            print(f"   ✅ Score: {results['score']}/100 - No gaps found!")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    avg_score = sum(r['score'] for r in all_results) / len(all_results) if all_results else 0
    total_gaps = sum(len(r['gaps']) for r in all_results)
    
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Total Gaps: {total_gaps}")
    
    if avg_score > 90:
        print("✅ Documentation explanations are EXCELLENT!")
    elif avg_score > 80:
        print("✅ Documentation explanations are GOOD (minor improvements possible)")
    elif avg_score > 70:
        print("⚠️  Documentation explanations need SOME improvements")
    else:
        print("❌ Documentation explanations need SIGNIFICANT improvements")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
