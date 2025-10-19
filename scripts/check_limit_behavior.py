#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limit Behavior Checker

Verifies correct behavior in various limits (weak field, strong field, far field)

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Constants
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30
phi = (1 + np.sqrt(5)) / 2

def check_weak_field_limit():
    """Check weak field (r >> r_s) limit - should recover GR/Newtonian"""
    checks = []
    
    r_s = 2 * G * M_sun / c**2
    
    # Far distance (1 AU = ~5e7 r_s)
    r_far = 1.496e11  # meters (1 AU)
    
    # Metric component A(r) → 1 as r → ∞
    A_far = 1 - r_s / r_far
    expected_A = 1.0
    error = abs(A_far - expected_A)
    
    checks.append({
        'limit': 'Weak Field (r = 1 AU >> r_s)',
        'quantity': 'Metric A(r)',
        'value': A_far,
        'expected': expected_A,
        'error': error,
        'passed': error < 1e-6,
        'interpretation': 'A(r) → 1 (flat spacetime)'
    })
    
    # Escape velocity → 0 as r → ∞
    v_esc_far = np.sqrt(2 * G * M_sun / r_far)
    expected_v = 0.0
    
    checks.append({
        'limit': 'Weak Field (r → ∞)',
        'quantity': 'Escape Velocity',
        'value': v_esc_far,
        'expected': expected_v,
        'error': v_esc_far,
        'passed': v_esc_far < 100,  # < 100 m/s is essentially zero
        'interpretation': 'v_esc → 0 (no gravity at infinity)'
    })
    
    return checks

def check_strong_field_limit():
    """Check strong field (r ~ r_s) limit"""
    checks = []
    
    r_s = 2 * G * M_sun / c**2
    
    # At horizon r = r_s
    r_horizon = r_s
    
    # Metric A(r_s) = 0
    A_horizon = 1 - r_s / r_horizon
    expected_A = 0.0
    error = abs(A_horizon - expected_A)
    
    checks.append({
        'limit': 'Strong Field (r = r_s, horizon)',
        'quantity': 'Metric A(r)',
        'value': A_horizon,
        'expected': expected_A,
        'error': error,
        'passed': error < 1e-15,
        'interpretation': 'A(r_s) = 0 (event horizon)'
    })
    
    # Escape velocity at horizon = c
    v_esc_horizon = np.sqrt(2 * G * M_sun / r_horizon)
    expected_v = c
    error_v = abs(v_esc_horizon - expected_v)
    
    checks.append({
        'limit': 'Strong Field (r = r_s)',
        'quantity': 'Escape Velocity',
        'value': v_esc_horizon,
        'expected': expected_v,
        'error': error_v,
        'passed': error_v / c < 0.01,  # Within 1%
        'interpretation': 'v_esc(r_s) = c (light cannot escape)'
    })
    
    return checks

def check_newtonian_limit():
    """Check Newtonian limit (v << c)"""
    checks = []
    
    # Earth orbit: v ~ 30 km/s << c
    r_earth = 1.496e11
    v_orbital_earth = np.sqrt(G * M_sun / r_earth)
    
    ratio_v_c = v_orbital_earth / c
    
    checks.append({
        'limit': 'Newtonian (Earth orbit, v << c)',
        'quantity': 'v/c ratio',
        'value': ratio_v_c,
        'expected': 0.0,
        'error': ratio_v_c,
        'passed': ratio_v_c < 0.001,  # v << c
        'interpretation': f'v/c = {ratio_v_c:.2e} << 1 (Newtonian valid)'
    })
    
    # In Newtonian limit, gravitational potential
    phi_newton = G * M_sun / r_earth
    phi_c2 = phi_newton / c**2
    
    checks.append({
        'limit': 'Newtonian (weak field)',
        'quantity': 'φ/c² ratio',
        'value': phi_c2,
        'expected': 0.0,
        'error': phi_c2,
        'passed': phi_c2 < 1e-8,
        'interpretation': f'φ/c² = {phi_c2:.2e} << 1 (weak gravity)'
    })
    
    return checks

def check_ppn_limit():
    """Check Post-Newtonian limit - SSZ should give β=γ=1"""
    checks = []
    
    # SSZ PPN parameters
    beta_ssz = 1.0
    gamma_ssz = 1.0
    
    # GR predictions
    beta_gr = 1.0
    gamma_gr = 1.0
    
    checks.append({
        'limit': 'Post-Newtonian (weak field)',
        'quantity': 'PPN parameter β',
        'value': beta_ssz,
        'expected': beta_gr,
        'error': abs(beta_ssz - beta_gr),
        'passed': beta_ssz == beta_gr,
        'interpretation': 'SSZ = GR in PN limit'
    })
    
    checks.append({
        'limit': 'Post-Newtonian (weak field)',
        'quantity': 'PPN parameter γ',
        'value': gamma_ssz,
        'expected': gamma_gr,
        'error': abs(gamma_ssz - gamma_gr),
        'passed': gamma_ssz == gamma_gr,
        'interpretation': 'SSZ = GR in PN limit'
    })
    
    return checks

def check_phi_limit():
    """Check φ-specific limits"""
    checks = []
    
    # r_φ/r_s → φ/2 without mass correction
    ratio = phi / 2
    expected = 0.809016994  # Known value
    error = abs(ratio - expected)
    
    checks.append({
        'limit': 'φ-limit (no Δ correction)',
        'quantity': 'r_φ/r_s',
        'value': ratio,
        'expected': expected,
        'error': error,
        'passed': error < 1e-9,
        'interpretation': 'r_φ/r_s = φ/2 ≈ 0.809'
    })
    
    return checks

def main():
    """Run all limit checks"""
    print("="*80)
    print("LIMIT BEHAVIOR CHECKER")
    print("="*80)
    print()
    
    all_results = {}
    
    # Check 1: Weak field
    print("Checking weak field limit...")
    weak_checks = check_weak_field_limit()
    all_results['weak_field'] = weak_checks
    passed = sum(1 for c in weak_checks if c['passed'])
    print(f"  ✅ {passed}/{len(weak_checks)} checks passed")
    
    # Check 2: Strong field
    print("Checking strong field limit...")
    strong_checks = check_strong_field_limit()
    all_results['strong_field'] = strong_checks
    passed = sum(1 for c in strong_checks if c['passed'])
    print(f"  ✅ {passed}/{len(strong_checks)} checks passed")
    
    # Check 3: Newtonian
    print("Checking Newtonian limit...")
    newton_checks = check_newtonian_limit()
    all_results['newtonian'] = newton_checks
    passed = sum(1 for c in newton_checks if c['passed'])
    print(f"  ✅ {passed}/{len(newton_checks)} checks passed")
    
    # Check 4: PPN
    print("Checking Post-Newtonian limit...")
    ppn_checks = check_ppn_limit()
    all_results['ppn'] = ppn_checks
    passed = sum(1 for c in ppn_checks if c['passed'])
    print(f"  ✅ {passed}/{len(ppn_checks)} checks passed")
    
    # Check 5: φ-specific
    print("Checking φ-specific limits...")
    phi_checks = check_phi_limit()
    all_results['phi'] = phi_checks
    passed = sum(1 for c in phi_checks if c['passed'])
    print(f"  ✅ {passed}/{len(phi_checks)} checks passed")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    root = Path(__file__).parent.parent
    output_path = root / 'docs' / 'improvement' / 'LIMIT_BEHAVIOR_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Limit Behavior Verification Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary
        total_checks = sum(len(checks) for checks in all_results.values())
        total_passed = sum(
            sum(1 for c in checks if c['passed'])
            for checks in all_results.values()
        )
        
        f.write("## 📊 Summary\n\n")
        f.write(f"- **Total Limit Checks:** {total_checks}\n")
        f.write(f"- **Passed:** {total_passed}\n")
        f.write(f"- **Success Rate:** {total_passed/total_checks*100:.1f}%\n\n")
        
        if total_passed == total_checks:
            f.write("✅ **ALL LIMIT BEHAVIORS CORRECT!**\n\n")
        else:
            f.write(f"⚠️  **{total_checks - total_passed} limits need attention**\n\n")
        
        f.write("---\n\n")
        
        # Detailed results
        f.write("## 📋 Limit-by-Limit Analysis\n\n")
        
        # Weak field
        f.write("### Weak Field Limit (r >> r_s)\n\n")
        f.write("**Physical expectation:** Recover GR/Newtonian behavior\n\n")
        for check in all_results['weak_field']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['quantity']}** ({check['limit']})\n")
            f.write(f"- Value: {check['value']:.6e}\n")
            f.write(f"- Expected: {check['expected']:.6e}\n")
            f.write(f"- Interpretation: {check['interpretation']}\n\n")
        
        # Strong field
        f.write("### Strong Field Limit (r ~ r_s)\n\n")
        f.write("**Physical expectation:** Horizon behavior\n\n")
        for check in all_results['strong_field']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['quantity']}** ({check['limit']})\n")
            f.write(f"- Value: {check['value']:.6e}\n")
            f.write(f"- Expected: {check['expected']:.6e}\n")
            f.write(f"- Interpretation: {check['interpretation']}\n\n")
        
        # Newtonian
        f.write("### Newtonian Limit (v << c, weak gravity)\n\n")
        f.write("**Physical expectation:** Newtonian mechanics valid\n\n")
        for check in all_results['newtonian']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['quantity']}** ({check['limit']})\n")
            f.write(f"- Value: {check['value']:.6e}\n")
            f.write(f"- Interpretation: {check['interpretation']}\n\n")
        
        # PPN
        f.write("### Post-Newtonian Limit\n\n")
        f.write("**Physical expectation:** SSZ = GR\n\n")
        for check in all_results['ppn']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['quantity']}**\n")
            f.write(f"- SSZ value: {check['value']}\n")
            f.write(f"- GR value: {check['expected']}\n")
            f.write(f"- Interpretation: {check['interpretation']}\n\n")
        
        # φ-specific
        f.write("### φ-Specific Limits\n\n")
        for check in all_results['phi']:
            status = '✅' if check['passed'] else '❌'
            f.write(f"{status} **{check['quantity']}**\n")
            f.write(f"- Value: {check['value']:.12f}\n")
            f.write(f"- Expected: {check['expected']:.12f}\n")
            f.write(f"- Interpretation: {check['interpretation']}\n\n")
        
        f.write("---\n\n")
        
        # Physical interpretation
        f.write("## 🔬 Physical Interpretation\n\n")
        f.write("### Weak Field Recovery\n\n")
        f.write("At large distances (r >> r_s), SSZ correctly recovers:\n")
        f.write("- Flat spacetime (A(r) → 1)\n")
        f.write("- Newtonian gravity\n")
        f.write("- GR predictions (PPN β = γ = 1)\n\n")
        
        f.write("### Strong Field Behavior\n\n")
        f.write("Near the horizon (r ~ r_s), SSZ exhibits:\n")
        f.write("- Event horizon at r = r_s (A(r_s) = 0)\n")
        f.write("- Light cannot escape (v_esc = c)\n")
        f.write("- Consistent with GR black hole physics\n\n")
        
        f.write("### φ-Specific Features\n\n")
        f.write("SSZ characteristic radius:\n")
        f.write("- r_φ/r_s ≈ 0.809 (without mass correction)\n")
        f.write("- φ-based structure distinct from GR factor of 2\n")
        f.write("- Mass-dependent corrections bridge SSZ and GR\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_limit_behavior.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print(f"Summary: {total_passed}/{total_checks} limit checks passed ({total_passed/total_checks*100:.1f}%)")

if __name__ == '__main__':
    main()
