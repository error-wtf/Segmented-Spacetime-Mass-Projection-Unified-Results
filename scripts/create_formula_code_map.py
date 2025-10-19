#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formula-to-Code Mapping Generator

Creates cross-reference between mathematical formulas and code implementations

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

# Key formulas to map
KEY_FORMULAS = {
    'golden_ratio': {
        'formula': 'φ = (1 + √5)/2',
        'search_terms': ['phi', '1.618', 'golden_ratio', 'PHI', 'GOLDEN'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'r_phi': {
        'formula': 'r_φ = φ·(GM/c²)·(1 + Δ(M)/100)',
        'search_terms': ['r_phi', 'r_φ', 'characteristic_radius', 'segment_radius'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'schwarzschild': {
        'formula': 'r_s = 2GM/c²',
        'search_terms': ['r_s', 'schwarzschild', 'r_schw', '2*G*M'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'time_dilation': {
        'formula': 'τ(x) = φ^(-α·N(x))',
        'search_terms': ['tau', 'time_dilation', 'φ**(-alpha', 'phi**(-alpha'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'segment_density': {
        'formula': 'N(x) = Σ γ_i·K_i(||x - x_i||)',
        'search_terms': ['segment_density', 'N(x)', 'density_field', 'kernel'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'refractive_index': {
        'formula': 'n(x) = 1 + κ·N(x)',
        'search_terms': ['refractive', 'n(x)', 'kappa*N', 'index'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'dual_velocity': {
        'formula': 'v_esc·v_fall = c²',
        'search_terms': ['v_esc', 'v_fall', 'escape_velocity', 'fall_velocity'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'escape_velocity': {
        'formula': 'v_esc = √(2GM/r)',
        'search_terms': ['v_esc', 'escape', 'sqrt(2*G*M'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'ppn_parameters': {
        'formula': 'β = 1, γ = 1 (GR)',
        'search_terms': ['beta', 'gamma', 'ppn', 'PPN'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    },
    'metric_A': {
        'formula': 'A(r) = 1 - r_s/r',
        'search_terms': ['A(r)', 'metric', '1 - r_s/r', 'g_tt'],
        'doc_file': 'MATHEMATICAL_FORMULAS.md'
    }
}

def find_formula_in_code(root, formula_key, search_terms):
    """Find where a formula is implemented in code"""
    implementations = []
    
    # Search Python files
    for py_file in root.glob('**/*.py'):
        if '__pycache__' in str(py_file) or 'venv' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            # Check if any search term appears
            for term in search_terms:
                if term.lower() in content.lower():
                    # Find context around the term
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            implementations.append({
                                'file': py_file.relative_to(root),
                                'line': i + 1,
                                'context': line.strip(),
                                'term': term
                            })
                            break
                    break
        except:
            continue
    
    return implementations

def main():
    """Create formula-code mapping"""
    print("="*80)
    print("FORMULA-CODE MAPPING GENERATOR")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    print(f"Mapping {len(KEY_FORMULAS)} key formulas to code...")
    print()
    
    # Find implementations for each formula
    mapping = {}
    for formula_key, formula_data in KEY_FORMULAS.items():
        print(f"Searching for: {formula_data['formula']}...", end=' ')
        
        impls = find_formula_in_code(root, formula_key, formula_data['search_terms'])
        mapping[formula_key] = {
            'formula': formula_data['formula'],
            'doc_file': formula_data['doc_file'],
            'implementations': impls,
            'found': len(impls) > 0
        }
        
        if impls:
            print(f"✅ Found {len(impls)} implementations")
        else:
            print("⚠️  Not found")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'FORMULA_CODE_MAPPING.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Formula-Code Mapping Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Formulas Mapped:** {len(KEY_FORMULAS)}\n\n")
        f.write("---\n\n")
        
        # Summary
        found_count = sum(1 for m in mapping.values() if m['found'])
        coverage = (found_count / len(KEY_FORMULAS) * 100) if KEY_FORMULAS else 0
        
        f.write("## 📊 Summary\n\n")
        f.write(f"- **Total Formulas:** {len(KEY_FORMULAS)}\n")
        f.write(f"- **Implemented:** {found_count}\n")
        f.write(f"- **Not Found:** {len(KEY_FORMULAS) - found_count}\n")
        f.write(f"- **Coverage:** {coverage:.1f}%\n\n")
        
        filled = int(coverage / 10)
        bar = '█' * filled + '░' * (10 - filled)
        f.write(f"`[{bar}]` {coverage:.1f}%\n\n")
        
        f.write("---\n\n")
        
        # Implemented formulas
        f.write("## ✅ Implemented Formulas\n\n")
        
        for formula_key, data in mapping.items():
            if data['found']:
                f.write(f"### {formula_key.replace('_', ' ').title()}\n\n")
                f.write(f"**Formula:** `{data['formula']}`\n\n")
                f.write(f"**Documented in:** {data['doc_file']}\n\n")
                f.write(f"**Implementations ({len(data['implementations'])}):**\n\n")
                
                for impl in data['implementations'][:5]:  # Limit to 5
                    f.write(f"- **{impl['file']}** (line {impl['line']})\n")
                    f.write(f"  ```python\n")
                    f.write(f"  {impl['context']}\n")
                    f.write(f"  ```\n\n")
        
        # Missing formulas
        f.write("## ⚠️  Formulas Not Found in Code\n\n")
        
        not_found = [k for k, v in mapping.items() if not v['found']]
        if not_found:
            for formula_key in not_found:
                data = mapping[formula_key]
                f.write(f"### {formula_key.replace('_', ' ').title()}\n\n")
                f.write(f"**Formula:** `{data['formula']}`\n\n")
                f.write(f"**Search terms used:** {', '.join(KEY_FORMULAS[formula_key]['search_terms'][:3])}\n\n")
                f.write("**Possible reasons:**\n")
                f.write("- Different variable names in code\n")
                f.write("- Implemented but with different syntax\n")
                f.write("- Not yet implemented\n\n")
        else:
            f.write("✅ All formulas found in code!\n\n")
        
        # Detailed mapping table
        f.write("---\n\n")
        f.write("## 📋 Complete Mapping Table\n\n")
        f.write("| Formula | Status | Files | First Implementation |\n")
        f.write("|---------|--------|-------|----------------------|\n")
        
        for formula_key, data in sorted(mapping.items()):
            name = formula_key.replace('_', ' ').title()
            status = '✅' if data['found'] else '⚠️'
            count = len(data['implementations'])
            first_file = str(data['implementations'][0]['file']).split('/')[-1] if data['implementations'] else 'N/A'
            
            f.write(f"| {name} | {status} | {count} | {first_file} |\n")
        
        f.write("\n---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### For Developers\n\n")
        
        if not_found:
            f.write(f"- **Verify {len(not_found)} formulas** not automatically found\n")
            f.write("- Check if implemented with different variable names\n")
            f.write("- Add clear comments linking code to formulas\n\n")
        
        f.write("- Add formula references in docstrings\n")
        f.write("- Use consistent variable naming (match docs)\n")
        f.write("- Comment complex calculations with formula numbers\n\n")
        
        f.write("### For Documentation\n\n")
        f.write("- Add 'Implementation:' sections to formula docs\n")
        f.write("- Link to specific code files\n")
        f.write("- Include code examples\n\n")
        
        f.write("### Cross-Reference Format\n\n")
        f.write("**In Documentation:**\n")
        f.write("```markdown\n")
        f.write("### Formula 2.1: φ-Radius\n")
        f.write("r_φ = φ·(GM/c²)·(1 + Δ(M)/100)\n\n")
        f.write("**Implemented in:**\n")
        f.write("- `core/physics.py` (calculate_r_phi)\n")
        f.write("- `tests/test_ppn_exact.py` (validation)\n")
        f.write("```\n\n")
        
        f.write("**In Code:**\n")
        f.write("```python\n")
        f.write("def calculate_r_phi(M, delta_M):\n")
        f.write('    """\n')
        f.write("    Calculate φ-radius.\n")
        f.write("    \n")
        f.write("    Formula: r_φ = φ·(GM/c²)·(1 + Δ(M)/100)\n")
        f.write("    Reference: MATHEMATICAL_FORMULAS.md, Section 2.1\n")
        f.write('    """\n')
        f.write("    phi = (1 + np.sqrt(5)) / 2\n")
        f.write("    r_s = 2 * G * M / c**2\n")
        f.write("    return phi * (r_s / 2) * (1 + delta_M / 100)\n")
        f.write("```\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/create_formula_code_map.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Formulas mapped: {len(KEY_FORMULAS)}")
    print(f"  Implemented: {found_count}/{len(KEY_FORMULAS)} ({coverage:.1f}%)")
    print(f"  Not found: {len(not_found)}")

if __name__ == '__main__':
    main()
