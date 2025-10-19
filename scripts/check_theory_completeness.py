#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theory Documentation Completeness Checker

Verifies that all essential physics concepts are documented

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

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Essential physics concepts that MUST be documented
REQUIRED_CONCEPTS = {
    'fundamentals': [
        ('golden ratio', 'φ (golden ratio) definition and motivation'),
        ('segment', 'What is a segment'),
        ('natural boundary', 'Natural boundary concept'),
        ('singularity', 'Singularity problem in GR'),
    ],
    'field_equations': [
        ('segment density', 'Segment density field N(x)'),
        ('time dilation', 'Time dilation τ(x)'),
        ('metric', 'Metric tensor components'),
        ('refractive index', 'Refractive index n(x)'),
    ],
    'physical_predictions': [
        ('ppn parameters', 'PPN β and γ parameters'),
        ('schwarzschild', 'Schwarzschild radius r_s'),
        ('photon sphere', 'Photon sphere radius'),
        ('isco', 'ISCO (innermost stable circular orbit)'),
    ],
    'energy_conditions': [
        ('wec', 'Weak Energy Condition'),
        ('dec', 'Dominant Energy Condition'),
        ('sec', 'Strong Energy Condition'),
    ],
    'dual_velocities': [
        ('escape velocity', 'v_esc definition'),
        ('fall velocity', 'v_fall definition'),
        ('invariant', 'v_esc × v_fall = c²'),
    ],
    'gr_limits': [
        ('weak field', 'Weak field limit (GR recovery)'),
        ('far field', 'Far field behavior'),
        ('newtonian', 'Newtonian limit'),
    ]
}

def check_concept_coverage(filepath, concepts):
    """Check which concepts are covered in document"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().lower()
        
        results = {}
        for category, concept_list in concepts.items():
            category_results = []
            for keyword, description in concept_list:
                # Check if keyword appears in document
                found = keyword.lower() in content
                
                # For some concepts, check variants
                if not found:
                    variants = {
                        'golden ratio': ['φ', 'phi', '1.618'],
                        'segment density': ['n(x)', 'segment density', 'density field'],
                        'ppn parameters': ['ppn', 'beta', 'gamma', 'β', 'γ'],
                    }
                    if keyword in variants:
                        found = any(v in content for v in variants[keyword])
                
                category_results.append({
                    'keyword': keyword,
                    'description': description,
                    'found': found
                })
            results[category] = category_results
        
        return results
    except Exception as e:
        return {}

def check_derivation_steps(filepath):
    """Check if derivations have clear steps"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Look for derivation indicators
        derivation_markers = [
            'therefore', 'thus', 'hence', 'follows',
            'daraus folgt', 'somit', 'also',
            '→', '=>', '⇒',
            'step 1', 'step 2', 'schritt 1', 'schritt 2'
        ]
        
        marker_count = sum(content.lower().count(marker) for marker in derivation_markers)
        
        # Look for equation sequences
        equations = len(re.findall(r'[=]', content))
        
        return {
            'derivation_markers': marker_count,
            'equations': equations,
            'has_derivations': marker_count > 5
        }
    except:
        return {'has_derivations': False}

def check_examples(filepath):
    """Check if document has examples"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().lower()
        
        example_markers = [
            'example', 'beispiel', 'for instance', 'e.g.',
            'z.b.', 'zum beispiel'
        ]
        
        example_count = sum(content.count(marker) for marker in example_markers)
        
        return {
            'example_count': example_count,
            'has_examples': example_count > 0
        }
    except:
        return {'has_examples': False}

def main():
    """Check theory documentation completeness"""
    print("="*80)
    print("THEORY DOCUMENTATION COMPLETENESS CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Files to check
    files_to_check = {
        'PHYSICS_FOUNDATIONS.md': root / 'docs' / 'PHYSICS_FOUNDATIONS.md',
        'MATHEMATICAL_FORMULAS.md': root / 'docs' / 'MATHEMATICAL_FORMULAS.md',
        'CODE_IMPLEMENTATION_GUIDE.md': root / 'docs' / 'CODE_IMPLEMENTATION_GUIDE.md',
    }
    
    all_results = {}
    
    for name, filepath in files_to_check.items():
        if not filepath.exists():
            print(f"⚠️  {name}: NOT FOUND")
            continue
        
        print(f"Checking {name}...")
        
        # Check concept coverage
        coverage = check_concept_coverage(filepath, REQUIRED_CONCEPTS)
        
        # Check derivations
        derivations = check_derivation_steps(filepath)
        
        # Check examples
        examples = check_examples(filepath)
        
        all_results[name] = {
            'coverage': coverage,
            'derivations': derivations,
            'examples': examples
        }
        
        print(f"  ✅ Done")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'THEORY_COMPLETENESS_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Theory Documentation Completeness Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Checked:** {len(files_to_check)}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        
        for filename, results in all_results.items():
            f.write(f"### {filename}\n\n")
            
            # Concept coverage
            total_concepts = sum(len(cats) for cats in REQUIRED_CONCEPTS.values())
            found_concepts = sum(
                sum(1 for concept in category if concept['found'])
                for category in results['coverage'].values()
            )
            coverage_pct = (found_concepts / total_concepts * 100) if total_concepts > 0 else 0
            
            f.write(f"**Concept Coverage:** {found_concepts}/{total_concepts} ({coverage_pct:.1f}%)\n\n")
            
            # Progress bar
            filled = int(coverage_pct / 10)
            bar = '█' * filled + '░' * (10 - filled)
            f.write(f"`[{bar}]` {coverage_pct:.1f}%\n\n")
            
            # Derivations
            has_deriv = results['derivations']['has_derivations']
            f.write(f"**Derivations:** {'✅ Present' if has_deriv else '❌ Missing'}\n\n")
            
            # Examples
            has_ex = results['examples']['has_examples']
            ex_count = results['examples']['example_count']
            f.write(f"**Examples:** {'✅' if has_ex else '❌'} ({ex_count} found)\n\n")
        
        f.write("---\n\n")
        
        # Detailed breakdown
        f.write("## 📋 Detailed Concept Coverage\n\n")
        
        for filename, results in all_results.items():
            f.write(f"### {filename}\n\n")
            
            for category, concepts in results['coverage'].items():
                # Check if category has any missing concepts
                missing = [c for c in concepts if not c['found']]
                if not missing and len(concepts) > 0:
                    f.write(f"#### ✅ {category.replace('_', ' ').title()}\n\n")
                    f.write(f"All {len(concepts)} concepts documented.\n\n")
                elif missing:
                    f.write(f"#### ⚠️  {category.replace('_', ' ').title()}\n\n")
                    f.write(f"**Documented:** {len(concepts) - len(missing)}/{len(concepts)}\n\n")
                    f.write("**Missing:**\n")
                    for concept in missing:
                        f.write(f"- {concept['description']}\n")
                    f.write("\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### High Priority\n\n")
        
        # Find most critical gaps
        for filename, results in all_results.items():
            critical_missing = []
            for category in ['fundamentals', 'field_equations']:
                if category in results['coverage']:
                    missing = [c for c in results['coverage'][category] if not c['found']]
                    if missing:
                        critical_missing.extend([
                            (filename, category, c['description']) 
                            for c in missing
                        ])
            
            if critical_missing:
                f.write(f"**{filename}:**\n")
                for fname, cat, desc in critical_missing:
                    f.write(f"- Add: {desc}\n")
                f.write("\n")
        
        f.write("### Medium Priority\n\n")
        f.write("- Add more worked examples\n")
        f.write("- Expand derivation steps\n")
        f.write("- Add physical interpretations\n\n")
        
        f.write("### Low Priority\n\n")
        f.write("- Add more cross-references\n")
        f.write("- Enhance diagrams\n")
        f.write("- Add historical context\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_theory_completeness.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print("Summary:")
    for filename, results in all_results.items():
        total = sum(len(cats) for cats in REQUIRED_CONCEPTS.values())
        found = sum(
            sum(1 for c in cat if c['found'])
            for cat in results['coverage'].values()
        )
        pct = (found / total * 100) if total > 0 else 0
        print(f"  {filename}: {found}/{total} concepts ({pct:.1f}%)")

if __name__ == '__main__':
    main()
