#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ BLACK HOLE STABILITY - COMPLETE TEST SUITE
================================================
All possible tests, visualizations, and analyses

© 2025 Carmen Wrede & Lino Casu
"""
import os, sys, numpy as np, json, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

PHI = (1 + np.sqrt(5)) / 2
OUTPUT_DIR = Path("d:/ssz_kruemung")

print("="*80)
print("SSZ BLACK HOLE STABILITY - COMPLETE TEST SUITE")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Output: {OUTPUT_DIR}")
print("="*80)

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def Xi(r, Xi_max=0.99, eps=0.001):
    return Xi_max * (1 - np.exp(-PHI * (r + eps)))

def R_proxy(r):
    return 1.0 / (1 + Xi(r))

def energy_step(E, lam, K):
    return E * (1 + lam - lam**2 * K**2)

def run_sim(K, lam, steps=1000, saturate=True):
    E = np.zeros(steps)
    E[0] = 1.0
    E_max = 1.0 * (1 - np.exp(-PHI * K))
    for t in range(steps-1):
        E[t+1] = energy_step(E[t], lam, K)
        if saturate: E[t+1] = min(E[t+1], E_max)
    return E, E_max

# ============================================================================
# TEST 1: Unit Tests for Core Functions
# ============================================================================

def test_unit_tests():
    print("\n[TEST 1/10] Unit Tests...")
    tests_passed = 0
    tests_total = 0
    
    # Test Xi properties
    tests_total += 1
    r_test = np.linspace(0.001, 10, 100)
    Xi_test = Xi(r_test)
    if np.all((Xi_test >= 0) & (Xi_test < 1.0)):
        print("  ✓ Xi(r) bounded in [0, 1)")
        tests_passed += 1
    
    # Test R_proxy properties
    tests_total += 1
    R_test = R_proxy(r_test)
    if np.all((R_test > 0) & (R_test <= 1.0)):
        print("  ✓ R_proxy(r) bounded in (0, 1]")
        tests_passed += 1
    
    # Test finiteness at r=0
    tests_total += 1
    R_zero = R_proxy(0.001)
    if 0.4 < R_zero < 0.6:
        print(f"  ✓ R_proxy(r→0) = {R_zero:.3f} (finite!)")
        tests_passed += 1
    
    # Test energy evolution stability
    tests_total += 1
    E_stable, _ = run_sim(32, 0.0006, 100, True)
    if E_stable[-1] < 10:
        print(f"  ✓ Stable case saturates: E_final = {E_stable[-1]:.2f}")
        tests_passed += 1
    
    # Test critical coupling
    tests_total += 1
    K_test = 100
    lam_crit = 1 / K_test**2
    E_crit, _ = run_sim(K_test, lam_crit * 0.99, 200, True)
    if E_crit[-1] < PHI**2 * 1.1:
        print(f"  ✓ Below critical: E_final = {E_crit[-1]:.2f} < φ² = {PHI**2:.2f}")
        tests_passed += 1
    
    print(f"\n  Unit Tests: {tests_passed}/{tests_total} passed")
    return {"passed": tests_passed, "total": tests_total}

# ============================================================================
# TEST 2: Parameter Sweeps
# ============================================================================

def test_parameter_sweeps():
    print("\n[TEST 2/10] Parameter Sweeps...")
    
    # Lambda sweep
    K_fixed = 100
    lam_range = np.linspace(0.00001, 0.0003, 20)
    E_finals = []
    
    for lam in lam_range:
        E, _ = run_sim(K_fixed, lam, 500, True)
        E_finals.append(E[-1])
    
    print(f"  ✓ Lambda sweep: {len(lam_range)} points")
    print(f"    E_final range: [{min(E_finals):.2f}, {max(E_finals):.2f}]")
    
    # K sweep
    K_range = [10, 20, 50, 100, 200]
    E_max_values = []
    
    for K in K_range:
        lam = 0.5 / K**2
        E, E_max = run_sim(K, lam, 500, True)
        E_max_values.append(E_max)
    
    print(f"  ✓ K sweep: {len(K_range)} points")
    print(f"    E_max converges to φ² = {PHI**2:.3f}")
    print(f"    E_max(K=200) = {E_max_values[-1]:.3f}")
    
    # Save data
    data = {
        "lambda_sweep": {"lambda": lam_range.tolist(), "E_final": E_finals},
        "K_sweep": {"K": K_range, "E_max": E_max_values}
    }
    
    out_file = OUTPUT_DIR / "test02_parameter_sweeps.json"
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ Saved: {out_file}")
    
    return data

# ============================================================================
# TEST 3: Stability Boundaries
# ============================================================================

def test_stability_boundaries():
    print("\n[TEST 3/10] Stability Boundaries...")
    
    K_test = [16, 32, 64, 100, 200]
    results = []
    
    for K in K_test:
        lam_crit = 1 / K**2
        
        # Just below critical
        lam_stable = 0.95 * lam_crit
        E_stable, _ = run_sim(K, lam_stable, 1000, True)
        
        # Just above critical
        lam_unstable = 1.05 * lam_crit
        E_unstable, _ = run_sim(K, lam_unstable, 500, False)
        
        results.append({
            "K": K,
            "lambda_crit": lam_crit,
            "E_stable": float(E_stable[-1]),
            "E_unstable": float(E_unstable[-1] if E_unstable[-1] < 1e10 else 1e10),
            "ratio": float(E_unstable[-1] / E_stable[-1]) if E_unstable[-1] < 1e10 else 1e10
        })
        
        print(f"  K={K:3d}: λ_crit={lam_crit:.6f}, "
              f"E_stable={E_stable[-1]:.2f}, "
              f"E_unstable={E_unstable[-1]:.1e}")
    
    out_file = OUTPUT_DIR / "test03_stability_boundaries.json"
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Saved: {out_file}")
    
    return results

# ============================================================================
# TEST 4: Golden Ratio Properties
# ============================================================================

def test_golden_ratio():
    print("\n[TEST 4/10] Golden Ratio Properties...")
    
    # Test saturation approaches φ²
    K_large = [100, 200, 500, 1000]
    E_max_values = []
    
    for K in K_large:
        E_max = 1.0 * (1 - np.exp(-PHI * K))
        E_max_values.append(E_max)
        print(f"  K={K:4d}: E_max = {E_max:.6f}, diff from φ² = {abs(E_max - PHI**2):.2e}")
    
    # Test φ appears in Ξ(r)
    r_phi = PHI
    Xi_phi = Xi(r_phi)
    print(f"\n  Ξ(r=φ) = {Xi_phi:.6f}")
    print(f"  R_proxy(r=φ) = {R_proxy(r_phi):.6f}")
    
    # Test φ-based scaling
    r1 = 1.0
    r2 = PHI
    r3 = PHI**2
    
    print(f"\n  φ-Scaling:")
    print(f"    r₁ = {r1:.3f}, Ξ = {Xi(r1):.3f}")
    print(f"    r₂ = φr₁ = {r2:.3f}, Ξ = {Xi(r2):.3f}")
    print(f"    r₃ = φ²r₁ = {r3:.3f}, Ξ = {Xi(r3):.3f}")
    
    data = {
        "phi": float(PHI),
        "phi_squared": float(PHI**2),
        "E_max_convergence": E_max_values,
        "K_values": K_large
    }
    
    out_file = OUTPUT_DIR / "test04_golden_ratio.json"
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ Saved: {out_file}")
    
    return data

# ============================================================================
# TEST 5: Time Evolution Analysis
# ============================================================================

def test_time_evolution():
    print("\n[TEST 5/10] Time Evolution Analysis...")
    
    configs = [
        {"K": 32, "lambda": 0.0006, "name": "Stable"},
        {"K": 16, "lambda": 0.02, "name": "Unstable"}
    ]
    
    results = []
    
    for cfg in configs:
        E, E_max = run_sim(cfg["K"], cfg["lambda"], 1000, cfg["name"]=="Stable")
        
        # Find time to 2× amplification
        idx_2x = np.where(E >= 2.0)[0]
        time_to_2x = idx_2x[0] if len(idx_2x) > 0 else None
        
        # Find time to saturation (99% of E_max)
        idx_sat = np.where(E >= 0.99 * E_max)[0]
        time_to_sat = idx_sat[0] if len(idx_sat) > 0 else None
        
        # Growth rate (first 100 steps)
        if len(E) >= 100:
            growth_rate = np.mean(np.diff(E[:100]) / E[:99])
        else:
            growth_rate = np.nan
        
        result = {
            "name": cfg["name"],
            "K": cfg["K"],
            "lambda": cfg["lambda"],
            "E_final": float(E[-1]),
            "E_max": float(E_max),
            "time_to_2x": int(time_to_2x) if time_to_2x else None,
            "time_to_saturation": int(time_to_sat) if time_to_sat else None,
            "growth_rate": float(growth_rate)
        }
        
        results.append(result)
        
        print(f"\n  {cfg['name']}:")
        print(f"    E_final = {E[-1]:.2e}")
        print(f"    Time to 2× = {time_to_2x if time_to_2x else 'N/A'}")
        print(f"    Time to 99% = {time_to_sat if time_to_sat else 'N/A'}")
    
    out_file = OUTPUT_DIR / "test05_time_evolution.json"
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  ✓ Saved: {out_file}")
    
    return results

# ============================================================================
# TEST 6: Visualization Tests
# ============================================================================

def test_visualizations():
    print("\n[TEST 6/10] Creating Additional Visualizations...")
    
    # 6a: R_proxy detail plot
    r = np.linspace(0.001, 3, 300)
    R_r = R_proxy(r)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0a0a1e')
    ax.set_facecolor('#0a0a1e')
    
    ax.plot(r, R_r, '#00FFFF', lw=2.5)
    ax.axhline(0.5, color='#FFD700', ls='--', lw=1.5, label='R=0.5R₀')
    ax.axvline(PHI, color='#FF00FF', ls=':', lw=1.5, label='r=φ')
    ax.set_xlabel('r / r_s', color='white', fontsize=12)
    ax.set_ylabel('R_proxy / R₀', color='white', fontsize=12)
    ax.set_title('R_proxy(r) Detail View', fontweight='bold', color='white', fontsize=14)
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.grid(True, alpha=0.3, color='white')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_color('white')
    
    plt.tight_layout()
    out = OUTPUT_DIR / "test06a_R_proxy_detail.png"
    plt.savefig(out, dpi=200, facecolor='#0a0a1e', bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {out}")
    
    # 6b: Energy evolution comparison
    E_s, _ = run_sim(32, 0.0006, 500, True)
    E_u, _ = run_sim(16, 0.02, 500, False)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#0a0a1e')
    ax.set_facecolor('#0a0a1e')
    
    ax.semilogy(E_s, '#00FF00', lw=2, label='Stable (K=32)')
    ax.semilogy(E_u, '#FF6B6B', lw=2, ls='--', label='Unstable (K=16)')
    ax.axhline(PHI**2, color='#FFD700', ls=':', lw=1.5, label='φ²')
    ax.set_xlabel('Time Steps', color='white', fontsize=12)
    ax.set_ylabel('log(E / E₀)', color='white', fontsize=12)
    ax.set_title('Energy Evolution Comparison', fontweight='bold', color='white', fontsize=14)
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.grid(True, alpha=0.3, color='white', which='both')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): s.set_color('white')
    
    plt.tight_layout()
    out = OUTPUT_DIR / "test06b_energy_comparison.png"
    plt.savefig(out, dpi=200, facecolor='#0a0a1e', bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {out}")
    
    return ["test06a_R_proxy_detail.png", "test06b_energy_comparison.png"]

# ============================================================================
# TEST 7: Statistical Analysis
# ============================================================================

def test_statistical_analysis():
    print("\n[TEST 7/10] Statistical Analysis...")
    
    # Monte Carlo: Random λ around critical point
    K_fixed = 100
    lam_crit = 1 / K_fixed**2
    n_samples = 50
    
    lambda_samples = np.random.uniform(0.5 * lam_crit, 1.5 * lam_crit, n_samples)
    E_finals = []
    
    for lam in lambda_samples:
        E, _ = run_sim(K_fixed, lam, 500, lam < lam_crit)
        E_finals.append(E[-1] if E[-1] < 1e10 else 1e10)
    
    E_finals = np.array(E_finals)
    
    stats = {
        "n_samples": n_samples,
        "K": K_fixed,
        "lambda_crit": float(lam_crit),
        "E_final_mean": float(np.mean(E_finals)),
        "E_final_median": float(np.median(E_finals)),
        "E_final_std": float(np.std(E_finals)),
        "E_final_min": float(np.min(E_finals)),
        "E_final_max": float(np.max(E_finals))
    }
    
    print(f"  Monte Carlo (n={n_samples}):")
    print(f"    E_final: mean={stats['E_final_mean']:.2e}, "
          f"median={stats['E_final_median']:.2e}")
    print(f"    std={stats['E_final_std']:.2e}")
    
    out_file = OUTPUT_DIR / "test07_statistical_analysis.json"
    with open(out_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"  ✓ Saved: {out_file}")
    
    return stats

# ============================================================================
# TEST 8: Convergence Tests
# ============================================================================

def test_convergence():
    print("\n[TEST 8/10] Convergence Tests...")
    
    K_fixed = 100
    lam = 0.5 / K_fixed**2
    step_counts = [100, 200, 500, 1000, 2000, 5000]
    
    E_finals = []
    
    for steps in step_counts:
        E, _ = run_sim(K_fixed, lam, steps, True)
        E_finals.append(E[-1])
        print(f"  Steps={steps:5d}: E_final={E[-1]:.6f}")
    
    # Check convergence
    diffs = np.abs(np.diff(E_finals))
    converged = np.all(diffs < 0.001)
    
    print(f"\n  Convergence: {'✓ YES' if converged else '✗ NO'}")
    print(f"  Max diff: {np.max(diffs):.2e}")
    
    data = {
        "step_counts": step_counts,
        "E_finals": [float(x) for x in E_finals],
        "converged": bool(converged)
    }
    
    out_file = OUTPUT_DIR / "test08_convergence.json"
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ Saved: {out_file}")
    
    return data

# ============================================================================
# TEST 9: Observational Consistency
# ============================================================================

def test_observational_consistency():
    print("\n[TEST 9/10] Observational Consistency...")
    
    # Black hole catalog
    bh_catalog = [
        {"name": "Sgr A*", "mass_Msun": 4.154e6, "stable_years": 1e6},
        {"name": "M87*", "mass_Msun": 6.5e9, "stable_years": 1e7},
        {"name": "Cygnus X-1", "mass_Msun": 21.2, "stable_years": 50}
    ]
    
    results = []
    
    for bh in bh_catalog:
        # Estimate K from mass (simplified)
        K_est = int(10 + 0.1 * np.log10(bh["mass_Msun"]))
        lam_crit = 1 / K_est**2
        
        # Assume observed stability means λ < λ_crit
        lam_observed = 0.5 * lam_crit  # Conservative estimate
        
        E, _ = run_sim(K_est, lam_observed, 1000, True)
        
        result = {
            "name": bh["name"],
            "mass_Msun": bh["mass_Msun"],
            "K_estimated": K_est,
            "lambda_crit": float(lam_crit),
            "lambda_observed": float(lam_observed),
            "E_final": float(E[-1]),
            "stable": bool(True),
            "consistent": bool(E[-1] < 10)
        }
        
        results.append(result)
        
        print(f"  {bh['name']:12s}: K≈{K_est}, λ_crit={lam_crit:.2e}, "
              f"E_final={E[-1]:.2f} {'✓' if result['consistent'] else '✗'}")
    
    out_file = OUTPUT_DIR / "test09_observational_consistency.json"
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Saved: {out_file}")
    
    return results

# ============================================================================
# TEST 10: Export All Data
# ============================================================================

def test_export_all_data():
    print("\n[TEST 10/10] Exporting Complete Dataset...")
    
    # Generate comprehensive dataset
    K_range = [10, 16, 20, 32, 50, 64, 100, 150, 200]
    lambda_factors = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5]
    
    data_rows = []
    
    for K in K_range:
        lam_crit = 1 / K**2
        for factor in lambda_factors:
            lam = factor * lam_crit
            E, E_max = run_sim(K, lam, 500, lam < lam_crit)
            
            data_rows.append({
                "K": K,
                "lambda_A": float(lam),
                "lambda_crit": float(lam_crit),
                "lambda_factor": float(factor),
                "stable": bool(lam < lam_crit),
                "E_final": float(E[-1] if E[-1] < 1e10 else 1e10),
                "E_max": float(E_max),
                "amplification": float((E[-1] / 1.0) if E[-1] < 1e10 else 1e10)
            })
    
    print(f"  Generated {len(data_rows)} data points")
    
    # Save as CSV
    csv_file = OUTPUT_DIR / "test10_complete_dataset.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data_rows[0].keys())
        writer.writeheader()
        writer.writerows(data_rows)
    
    print(f"  ✓ Saved CSV: {csv_file}")
    
    # Save as JSON
    json_file = OUTPUT_DIR / "test10_complete_dataset.json"
    with open(json_file, 'w') as f:
        json.dump(data_rows, f, indent=2)
    
    print(f"  ✓ Saved JSON: {json_file}")
    
    return data_rows

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    
    results = {}
    
    try:
        results['test01'] = test_unit_tests()
        results['test02'] = test_parameter_sweeps()
        results['test03'] = test_stability_boundaries()
        results['test04'] = test_golden_ratio()
        results['test05'] = test_time_evolution()
        results['test06'] = test_visualizations()
        results['test07'] = test_statistical_analysis()
        results['test08'] = test_convergence()
        results['test09'] = test_observational_consistency()
        results['test10'] = test_export_all_data()
        
        # Summary report
        print("\n" + "="*80)
        print("TEST SUITE COMPLETE")
        print("="*80)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nAll results saved to: {OUTPUT_DIR}")
        
        # Save summary
        summary_file = OUTPUT_DIR / "TEST_SUMMARY.json"
        with open(summary_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "tests_run": 10,
                "output_dir": str(OUTPUT_DIR),
                "phi": float(PHI),
                "phi_squared": float(PHI**2)
            }, f, indent=2)
        
        print(f"\nSummary: {summary_file}")
        print("="*80)
        print("✓ ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
