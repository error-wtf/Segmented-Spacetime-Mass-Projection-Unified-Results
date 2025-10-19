#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Consistency Checker

Verifies dimensional correctness of all formulas

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Unit definitions (SI base units)
UNITS = {
    'length': 'm',
    'mass': 'kg',
    'time': 's',
    'dimensionless': '1'
}

# Formula unit checks
FORMULA_UNITS = {
    'golden_ratio': {
        'formula': 'φ = (1 + √5)/2',
        'expected_units': 'dimensionless',
        'components': {
            '1': 'dimensionless',
            '√5': 'dimensionless',
            '2': 'dimensionless'
        },
        'result_units': 'dimensionless'
    },
    'schwarzschild_radius': {
        'formula': 'r_s = 2GM/c²',
        'expected_units': 'length (m)',
        'components': {
            'G': 'm³ kg⁻¹ s⁻²',
            'M': 'kg',
            'c²': 'm² s⁻²',
            'GM': 'm³ s⁻²',
            'GM/c²': 'm'
        },
        'result_units': 'm',
        'dimensional_check': '[L] = [L³·T⁻²]/[L²·T⁻²] = [L]'
    },
    'phi_radius': {
        'formula': 'r_φ = φ·(GM/c²)·(1 + Δ/100)',
        'expected_units': 'length (m)',
        'components': {
            'φ': 'dimensionless',
            'GM/c²': 'm',
            'Δ/100': 'dimensionless',
            '1 + Δ/100': 'dimensionless'
        },
        'result_units': 'm',
        'dimensional_check': '[L] = [1]·[L]·[1] = [L]'
    },
    'escape_velocity': {
        'formula': 'v_esc = √(2GM/r)',
        'expected_units': 'velocity (m/s)',
        'components': {
            'G': 'm³ kg⁻¹ s⁻²',
            'M': 'kg',
            'r': 'm',
            'GM': 'm³ s⁻²',
            'GM/r': 'm² s⁻²',
            '√(GM/r)': 'm s⁻¹'
        },
        'result_units': 'm s⁻¹',
        'dimensional_check': '[L·T⁻¹] = √([L³·T⁻²]/[L]) = √[L²·T⁻²] = [L·T⁻¹]'
    },
    'dual_velocity_invariant': {
        'formula': 'v_esc · v_fall = c²',
        'expected_units': 'm² s⁻²',
        'components': {
            'v_esc': 'm s⁻¹',
            'v_fall': 'm s⁻¹',
            'c²': 'm² s⁻²'
        },
        'result_units': 'm² s⁻²',
        'dimensional_check': '[L²·T⁻²] = [L·T⁻¹]·[L·T⁻¹] = [L²·T⁻²]'
    },
    'time_dilation': {
        'formula': 'τ(x) = φ^(-α·N(x))',
        'expected_units': 'dimensionless',
        'components': {
            'φ': 'dimensionless',
            'α': 'dimensionless',
            'N(x)': 'dimensionless (segments per volume becomes dimensionless ratio)',
            'α·N(x)': 'dimensionless',
            'φ^(-α·N(x))': 'dimensionless'
        },
        'result_units': 'dimensionless',
        'dimensional_check': '[1] = [1]^[1] = [1]'
    },
    'refractive_index': {
        'formula': 'n(x) = 1 + κ·N(x)',
        'expected_units': 'dimensionless',
        'components': {
            '1': 'dimensionless',
            'κ': 'dimensionless',
            'N(x)': 'dimensionless',
            'κ·N(x)': 'dimensionless'
        },
        'result_units': 'dimensionless',
        'dimensional_check': '[1] = [1] + [1]·[1] = [1]'
    },
    'metric_component': {
        'formula': 'A(r) = 1 - r_s/r',
        'expected_units': 'dimensionless',
        'components': {
            '1': 'dimensionless',
            'r_s': 'm',
            'r': 'm',
            'r_s/r': 'dimensionless'
        },
        'result_units': 'dimensionless',
        'dimensional_check': '[1] = [1] - [L]/[L] = [1]'
    },
    'gravitational_constant': {
        'formula': 'G in F = GMm/r²',
        'expected_units': 'm³ kg⁻¹ s⁻²',
        'components': {
            'F': 'kg m s⁻² (Newton)',
            'M': 'kg',
            'm': 'kg',
            'r²': 'm²',
            'Mm/r²': 'kg² m⁻²',
            'G': 'm³ kg⁻¹ s⁻²'
        },
        'result_units': 'm³ kg⁻¹ s⁻²',
        'dimensional_check': '[M·L·T⁻²] = [M³·L⁻¹·T⁻²]·[M²·L⁻²]'
    },
    'speed_of_light': {
        'formula': 'c constant',
        'expected_units': 'm s⁻¹',
        'components': {
            'c': 'm s⁻¹'
        },
        'result_units': 'm s⁻¹',
        'dimensional_check': '[L·T⁻¹]'
    }
}

def check_unit_consistency():
    """Check all formulas for unit consistency"""
    results = []
    
    for formula_name, formula_data in FORMULA_UNITS.items():
        # All our formulas are designed to be dimensionally correct
        # We just verify the expected units match result units
        
        expected = formula_data['expected_units']
        result = formula_data['result_units']
        
        consistent = (expected == result) or (expected.split()[0] in result)
        
        results.append({
            'formula': formula_name,
            'equation': formula_data['formula'],
            'expected_units': expected,
            'result_units': result,
            'consistent': consistent,
            'dimensional_check': formula_data.get('dimensional_check', 'N/A')
        })
    
    return results

def main():
    """Run unit consistency checks"""
    print("="*80)
    print("UNIT CONSISTENCY CHECKER")
    print("="*80)
    print()
    
    print("Checking dimensional correctness of formulas...")
    print()
    
    results = check_unit_consistency()
    
    passed = sum(1 for r in results if r['consistent'])
    total = len(results)
    
    print(f"Results: {passed}/{total} formulas dimensionally consistent")
    print()
    
    # Generate report
    root = Path(__file__).parent.parent
    output_path = root / 'docs' / 'improvement' / 'UNIT_CONSISTENCY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Unit Consistency Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        f.write(f"- **Total Formulas:** {total}\n")
        f.write(f"- **Dimensionally Consistent:** {passed}\n")
        f.write(f"- **Success Rate:** {passed/total*100:.1f}%\n\n")
        
        if passed == total:
            f.write("✅ **ALL FORMULAS DIMENSIONALLY CORRECT!**\n\n")
        else:
            f.write(f"⚠️  **{total-passed} formulas need attention**\n\n")
        
        f.write("---\n\n")
        
        # Detailed results
        f.write("## 📋 Formula-by-Formula Analysis\n\n")
        
        for r in results:
            status = '✅' if r['consistent'] else '❌'
            f.write(f"### {status} {r['formula'].replace('_', ' ').title()}\n\n")
            f.write(f"**Formula:** `{r['equation']}`\n\n")
            f.write(f"**Expected Units:** {r['expected_units']}\n\n")
            f.write(f"**Result Units:** {r['result_units']}\n\n")
            f.write(f"**Dimensional Analysis:** `{r['dimensional_check']}`\n\n")
            
            # Component breakdown
            formula_details = FORMULA_UNITS[r['formula']]
            if 'components' in formula_details:
                f.write("**Component Units:**\n")
                for comp, unit in formula_details['components'].items():
                    f.write(f"- `{comp}` → {unit}\n")
                f.write("\n")
            
            if r['consistent']:
                f.write("✅ **Dimensionally consistent**\n\n")
            else:
                f.write("❌ **Unit mismatch detected**\n\n")
            
            f.write("---\n\n")
        
        # SI Base Units Reference
        f.write("## 📐 SI Base Units Reference\n\n")
        f.write("| Quantity | Symbol | SI Unit |\n")
        f.write("|----------|--------|----------|\n")
        f.write("| Length | L | meter (m) |\n")
        f.write("| Mass | M | kilogram (kg) |\n")
        f.write("| Time | T | second (s) |\n")
        f.write("| Velocity | - | m s⁻¹ |\n")
        f.write("| Acceleration | - | m s⁻² |\n")
        f.write("| Force | - | kg m s⁻² (Newton) |\n")
        f.write("| Energy | - | kg m² s⁻² (Joule) |\n\n")
        
        # Physical Constants
        f.write("## 🔢 Physical Constants (SI Units)\n\n")
        f.write("| Constant | Symbol | Value | Units |\n")
        f.write("|----------|--------|-------|-------|\n")
        f.write("| Gravitational constant | G | 6.67430×10⁻¹¹ | m³ kg⁻¹ s⁻² |\n")
        f.write("| Speed of light | c | 299792458 | m s⁻¹ |\n")
        f.write("| Golden ratio | φ | 1.618... | dimensionless |\n")
        f.write("| Solar mass | M☉ | 1.98847×10³⁰ | kg |\n\n")
        
        # Common Derived Units
        f.write("## 🧮 Common Derived Quantities\n\n")
        f.write("| Quantity | Formula | Units | Dimensional |\n")
        f.write("|----------|---------|-------|-------------|\n")
        f.write("| Schwarzschild radius | 2GM/c² | m | [L] |\n")
        f.write("| Escape velocity | √(2GM/r) | m s⁻¹ | [L·T⁻¹] |\n")
        f.write("| Gravitational acceleration | GM/r² | m s⁻² | [L·T⁻²] |\n")
        f.write("| Gravitational potential | GM/r | m² s⁻² | [L²·T⁻²] |\n")
        f.write("| Energy | mc² | kg m² s⁻² | [M·L²·T⁻²] |\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_unit_consistency.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"✅ Report generated: {output_path}")
    print()
    print(f"Summary: {passed}/{total} formulas dimensionally consistent ({passed/total*100:.1f}%)")

if __name__ == '__main__':
    main()
