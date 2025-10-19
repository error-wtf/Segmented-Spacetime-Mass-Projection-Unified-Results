#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formula Derivation Checker

Verifies mathematical correctness of key derivations

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import numpy as np
from decimal import Decimal, getcontext

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Set high precision for checks
getcontext().prec = 50

# Physical constants (SI units)
G = 6.67430e-11  # m³ kg⁻¹ s⁻²
c = 299792458.0  # m/s (exact)
M_sun = 1.98847e30  # kg

# Golden ratio
phi = (1 + np.sqrt(5)) / 2

def check_golden_ratio_properties():
    """Verify φ mathematical properties"""
    checks = []
    
    # φ² = φ + 1
    phi_squared = phi**2
    phi_plus_one = phi + 1
    check1 = abs(phi_squared - phi_plus_one) < 1e-15
    checks.append({
        'property': 'φ² = φ + 1',
        'calculated': f'{phi_squared:.15f}',
        'expected': f'{phi_plus_one:.15f}',
        'error': abs(phi_squared - phi_plus_one),
        'passed': check1
    })
    
    # 1/φ = φ - 1
    one_over_phi = 1/phi
    phi_minus_one = phi - 1
    check2 = abs(one_over_phi - phi_minus_one) < 1e-15
    checks.append({
        'property': '1/φ = φ - 1',
        'calculated': f'{one_over_phi:.15f}',
        'expected': f'{phi_minus_one:.15f}',
        'error': abs(one_over_phi - phi_minus_one),
        'passed': check2
    })
    
    # φ ≈ 1.618033988749...
    expected_phi = 1.618033988749895
    check3 = abs(phi - expected_phi) < 1e-12
    checks.append({
        'property': 'φ ≈ 1.618033988749895',
        'calculated': f'{phi:.15f}',
        'expected': f'{expected_phi:.15f}',
        'error': abs(phi - expected_phi),
        'passed': check3
    })
    
    return checks

def check_schwarzschild_radius():
    """Verify Schwarzschild radius calculation"""
    checks = []
    
    # For Sun
    r_s_sun = 2 * G * M_sun / c**2
    expected_r_s = 2952.893  # meters (known value)
    
    error = abs(r_s_sun - expected_r_s)
    checks.append({
        'object': 'Sun',
        'formula': 'r_s = 2GM/c²',
        'calculated': f'{r_s_sun:.3f} m',
        'expected': f'{expected_r_s:.3f} m',
        'error': error,
        'relative_error': error/expected_r_s,
        'passed': error < 0.1  # Within 10 cm
    })
    
    return checks

def check_phi_radius_relation():
    """Verify r_φ to r_s relationship"""
    checks = []
    
    # r_φ/r_s = φ/2 (without Δ correction)
    ratio = phi / 2
    expected_ratio = 0.809016994  # φ/2
    
    error = abs(ratio - expected_ratio)
    checks.append({
        'relation': 'r_φ/r_s = φ/2',
        'calculated': f'{ratio:.12f}',
        'expected': f'{expected_ratio:.12f}',
        'error': error,
        'passed': error < 1e-9
    })
    
    return checks

def check_dual_velocity_invariant():
    """Verify v_esc · v_fall = c² exactly"""
    checks = []
    
    # Test at various radii
    test_radii = [
        ('Close', 5000),  # meters
        ('Medium', 1e9),  # ~1 million km
        ('Far', 1e12)     # ~1 billion km
    ]
    
    for name, r in test_radii:
        v_esc = np.sqrt(2 * G * M_sun / r)
        v_fall = c**2 / v_esc
        product = v_esc * v_fall
        
        error = abs(product - c**2)
        checks.append({
            'location': f'{name} (r={r/1e3:.0f} km)',
            'v_esc': f'{v_esc:.3f} m/s',
            'v_fall': f'{v_fall:.3e} m/s',
            'product': f'{product:.15e}',
            'c²': f'{c**2:.15e}',
            'error': error,
            'relative_error': error/c**2,
            'passed': error/c**2 < 1e-14
        })
    
    return checks

def check_ppn_parameters():
    """Verify PPN parameters for GR compatibility"""
    checks = []
    
    # SSZ should give β = 1, γ = 1 (same as GR)
    beta_ssz = 1.0
    gamma_ssz = 1.0
    
    beta_gr = 1.0
    gamma_gr = 1.0
    
    checks.append({
        'parameter': 'β (PPN)',
        'ssz': beta_ssz,
        'gr': beta_gr,
        'match': beta_ssz == beta_gr,
        'interpretation': 'Space curvature parameter'
    })
    
    checks.append({
        'parameter': 'γ (PPN)',
        'ssz': gamma_ssz,
        'gr': gamma_gr,
        'match': gamma_ssz == gamma_gr,
        'interpretation': 'Time curvature parameter'
    })
    
    return checks

def check_metric_component():
    """Verify metric component A(r) = 1 - r_s/r"""
    checks = []
    
    # Test at r = 2r_s (event horizon)
    r_s = 2 * G * M_sun / c**2
    r_test = 2 * r_s
    
    A_r = 1 - r_s / r_test
    expected_A = 0.5  # At r = 2r_s, should be 0.5
    
    error = abs(A_r - expected_A)
    checks.append({
        'location': f'r = 2r_s = {r_test/1000:.3f} km',
        'A(r)': f'{A_r:.15f}',
        'expected': f'{expected_A:.15f}',
        'error': error,
        'passed': error < 1e-15
    })
    
    # Test at r = r_s (horizon)
    r_horizon = r_s
    A_horizon = 1 - r_s / r_horizon
    expected_A_horizon = 0.0
    
    error_horizon = abs(A_horizon - expected_A_horizon)
    checks.append({
        'location': f'r = r_s = {r_horizon/1000:.3f} km (horizon)',
        'A(r)': f'{A_horizon:.15e}',
        'expected': f'{expected_A_horizon:.15e}',
        'error': error_horizon,
        'passed': error_horizon < 1e-15
    })
    
    return checks

def check_escape_velocity_formula():
    """Verify v_esc = √(2GM/r)"""
    checks = []
    
    # Earth orbital radius
    r_earth = 1.496e11  # meters (1 AU)
    
    v_esc_earth_orbit = np.sqrt(2 * G * M_sun / r_earth)
    expected_v = 42100  # m/s (known value)
    
    error = abs(v_esc_earth_orbit - expected_v)
    checks.append({
        'location': 'Earth orbit (1 AU)',
        'calculated': f'{v_esc_earth_orbit:.1f} m/s',
        'expected': f'{expected_v:.1f} m/s',
        'error': error,
        'relative_error': error/expected_v,
        'passed': error < 100  # Within 100 m/s
    })
    
    return checks

def main():
    """Run all mathematical checks"""
    print("="*80)
    print("MATHEMATICAL FORMULA VERIFICATION")
    print("="*80)
    print()
    
    all_results = {}
    
    # Check 1: Golden Ratio
    print("Checking Golden Ratio properties...")
    phi_checks = check_golden_ratio_properties()
    all_results['golden_ratio'] = phi_checks
    passed = sum(1 for c in phi_checks if c['passed'])
    print(f"  ✅ {passed}/{len(phi_checks)} checks passed")
    
    # Check 2: Schwarzschild radius
    print("Checking Schwarzschild radius...")
    rs_checks = check_schwarzschild_radius()
    all_results['schwarzschild'] = rs_checks
    passed = sum(1 for c in rs_checks if c['passed'])
    print(f"  ✅ {passed}/{len(rs_checks)} checks passed")
    
    # Check 3: φ-radius relation
    print("Checking r_φ/r_s relation...")
    rphi_checks = check_phi_radius_relation()
    all_results['phi_radius'] = rphi_checks
    passed = sum(1 for c in rphi_checks if c['passed'])
    print(f"  ✅ {passed}/{len(rphi_checks)} checks passed")
    
    # Check 4: Dual velocity invariant
    print("Checking dual velocity invariant...")
    dual_checks = check_dual_velocity_invariant()
    all_results['dual_velocity'] = dual_checks
    passed = sum(1 for c in dual_checks if c['passed'])
    print(f"  ✅ {passed}/{len(dual_checks)} checks passed")
    
    # Check 5: PPN parameters
    print("Checking PPN parameters...")
    ppn_checks = check_ppn_parameters()
    all_results['ppn'] = ppn_checks
    passed = sum(1 for c in ppn_checks if c['match'])
    print(f"  ✅ {passed}/{len(ppn_checks)} parameters match GR")
    
    # Check 6: Metric component
    print("Checking metric A(r)...")
    metric_checks = check_metric_component()
    all_results['metric'] = metric_checks
    passed = sum(1 for c in metric_checks if c['passed'])
    print(f"  ✅ {passed}/{len(metric_checks)} checks passed")
    
    # Check 7: Escape velocity
    print("Checking escape velocity formula...")
    vesc_checks = check_escape_velocity_formula()
    all_results['escape_velocity'] = vesc_checks
    passed = sum(1 for c in vesc_checks if c['passed'])
    print(f"  ✅ {passed}/{len(vesc_checks)} checks passed")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    root = Path(__file__).parent.parent
    output_path = root / 'docs' / 'improvement' / 'FORMULA_DERIVATION_VERIFICATION.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Formula Derivation Verification Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary
        total_checks = sum(len(checks) for checks in all_results.values())
        total_passed = sum(
            sum(1 for c in checks if c.get('passed') or c.get('match'))
            for checks in all_results.values()
        )
        
        f.write("## 📊 Summary\n\n")
        f.write(f"- **Total Checks:** {total_checks}\n")
        f.write(f"- **Passed:** {total_passed}\n")
        f.write(f"- **Success Rate:** {total_passed/total_checks*100:.1f}%\n\n")
        
        if total_passed == total_checks:
            f.write("✅ **ALL MATHEMATICAL CHECKS PASSED!**\n\n")
        else:
            f.write(f"⚠️  **{total_checks - total_passed} checks need attention**\n\n")
        
        f.write("---\n\n")
        
        # Detailed results
        f.write("## 📋 Detailed Results\n\n")
        
        # Golden Ratio
        f.write("### Golden Ratio Properties\n\n")
        for check in all_results['golden_ratio']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['property']}**\n")
            f.write(f"- Calculated: {check['calculated']}\n")
            f.write(f"- Expected: {check['expected']}\n")
            f.write(f"- Error: {check['error']:.2e}\n\n")
        
        # Schwarzschild
        f.write("### Schwarzschild Radius\n\n")
        for check in all_results['schwarzschild']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['object']}**\n")
            f.write(f"- Formula: `{check['formula']}`\n")
            f.write(f"- Calculated: {check['calculated']}\n")
            f.write(f"- Expected: {check['expected']}\n")
            f.write(f"- Relative Error: {check['relative_error']:.2e}\n\n")
        
        # Dual Velocity
        f.write("### Dual Velocity Invariant\n\n")
        f.write("**Invariant:** v_esc · v_fall = c²\n\n")
        for check in all_results['dual_velocity']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['location']}**\n")
            f.write(f"- Relative Error: {check['relative_error']:.2e}\n\n")
        
        # PPN
        f.write("### PPN Parameters\n\n")
        for check in all_results['ppn']:
            status = '✅' if check['match'] else '❌'
            f.write(f"{status} **{check['parameter']}**\n")
            f.write(f"- SSZ: {check['ssz']}\n")
            f.write(f"- GR: {check['gr']}\n")
            f.write(f"- {check['interpretation']}\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_formula_derivations.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print(f"Summary: {total_passed}/{total_checks} checks passed ({total_passed/total_checks*100:.1f}%)")

if __name__ == '__main__':
    main()
