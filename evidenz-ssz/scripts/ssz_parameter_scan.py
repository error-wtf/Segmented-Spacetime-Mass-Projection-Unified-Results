#!/usr/bin/env python3
"""
SSZ Black-Hole-Bomb: Extended Parameter Scan
=============================================
Multi-parameter exploration of SSZ stabilization effects.

Scans over:
- λ_A (amplitude coupling)
- λ_φ (phase coupling)  
- K_segments (segment count)
- Ω₀ (rotation frequency)

Perfect-Pair Mathematics Style (Casu & Wrede 2025)
© 2025 Carmen Wrede, Lino Casu
"""
import math, json, csv, sys, os
from itertools import product

# Reuse all functions from complete implementation
PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

# ============================================================================
# BASE FUNCTIONS (from ssz_blackhole_bomb_complete.py)
# ============================================================================

def ssz_radius(theta, r0, phi):
    return r0 * (phi ** (theta / (PI / 2)))

def segment_density(theta, sigma0, phi):
    return sigma0 * (phi ** (theta / (PI / 2)))

def Omega_profile(theta, Omega0, epsilon, q):
    return Omega0 * (1 + epsilon * math.cos(q * theta))

def gamma_loc(theta, omega, m, Omega0, epsilon, q, alpha, eta):
    omega_co = omega - m * Omega_profile(theta, Omega0, epsilon, q)
    return alpha * max(0.0, -omega_co) - eta

def transition_amplitude(theta_k, sigma0, phi, lambda_A):
    return math.exp(-lambda_A * segment_density(theta_k, sigma0, phi))

def transition_phase(theta_k, sigma0, phi, lambda_phi):
    return lambda_phi * segment_density(theta_k, sigma0, phi)

def generate_segment_boundaries(K, sigma_fn, mode='uniform'):
    if mode == 'uniform':
        return [2 * PI * k / K for k in range(K)]
    return [2 * PI * k / K for k in range(K)]

def one_roundtrip(A, phi_acc, omega, m, params):
    Omega0, eps, q = params["Omega0"], params["epsilon"], params["q"]
    alpha, eta = params["alpha"], params["eta"]
    R, K_coup = params["R"], params["K_coupling"]
    r0, phi_g = params["r0"], params["phi"]
    sigma0 = params["sigma0"]
    lambda_A, lambda_phi = params["lambda_A"], params["lambda_phi"]
    K_seg, M_theta = params["K_segments"], params["M_theta"]
    
    d_theta = 2 * PI / M_theta
    sigma_fn = lambda t: segment_density(t, sigma0, phi_g)
    theta_k_list = generate_segment_boundaries(K_seg, sigma_fn, mode='uniform')
    
    integral_gamma = integral_k_phase = 0.0
    for i in range(M_theta):
        theta = d_theta * i
        r_theta = ssz_radius(theta, r0, phi_g)
        ds = r_theta * d_theta
        gamma_theta = gamma_loc(theta, omega, m, Omega0, eps, q, alpha, eta)
        integral_gamma += gamma_theta * ds
        integral_k_phase += omega * d_theta
    
    log_T_A_sum = dphi_SSZ_sum = 0.0
    for theta_k in theta_k_list:
        T_A_k = transition_amplitude(theta_k, sigma0, phi_g, lambda_A)
        log_T_A_sum += math.log(T_A_k)
        dphi_SSZ_sum += transition_phase(theta_k, sigma0, phi_g, lambda_phi)
    
    G_round = math.exp(integral_gamma + log_T_A_sum) * R * (1 - K_coup)
    A_next = A * G_round
    phi_next = phi_acc + integral_k_phase + dphi_SSZ_sum
    
    return A_next, phi_next, G_round, integral_k_phase + dphi_SSZ_sum

def run_mode(omega, m, params):
    N_max, A, phi_acc = params["N_max"], 1.0, 0.0
    A_history, G_history = [A], []
    
    for n in range(N_max):
        A_next, phi_next, G_round, _ = one_roundtrip(A, phi_acc, omega, m, params)
        A_history.append(A_next)
        G_history.append(G_round)
        if A_next > 1e12 or A_next < 1e-12:
            break
        A, phi_acc = A_next, phi_next
    
    if G_history:
        log_G_avg = sum(math.log(max(G, 1e-100)) for G in G_history) / len(G_history)
        G_avg = math.exp(log_G_avg)
    else:
        G_avg = 1.0
    
    return {"omega": omega, "m": m, "G_avg": G_avg, "unstable": G_avg > 1.0}

def sweep(params, ssz_mode=True):
    if not ssz_mode:
        params = params.copy()
        params["lambda_A"] = params["lambda_phi"] = params["sigma0"] = 0.0
    
    results = []
    for omega in params["omega_grid"]:
        for m in params["m_grid"]:
            result = run_mode(omega, m, params)
            results.append(result)
    return results

# ============================================================================
# EXTENDED PARAMETER SCAN
# ============================================================================

BASE_CONFIG = {
    "omega_grid": [0.1, 0.15, 0.2, 0.25, 0.3],
    "m_grid": [1, 2, 3, 4],
    "epsilon": 0.1, "q": 2,
    "alpha": 0.8, "eta": 0.05,
    "R": 0.98, "K_coupling": 0.02,
    "sigma0": 1.0, "phi": PHI, "r0": 1.0,
    "M_theta": 2048, "N_max": 200, "seed": 1234
}

# Parameter grids for scan
SCAN_GRIDS = {
    "lambda_A_grid": [0.00, 0.01, 0.02, 0.03, 0.05],
    "lambda_phi_grid": [0.00, 0.01, 0.02, 0.03, 0.05],
    "K_segments_grid": [8, 16, 32, 64],
    "Omega0_grid": [0.2, 0.3, 0.4]
}

def parameter_scan():
    """Run extended multi-parameter scan"""
    
    print("="*80)
    print("SSZ PARAMETER SCAN - Extended Analysis")
    print("="*80)
    print("\nScan dimensions:")
    for key, vals in SCAN_GRIDS.items():
        print(f"  {key}: {vals}")
    
    total = (len(SCAN_GRIDS["lambda_A_grid"]) * 
             len(SCAN_GRIDS["lambda_phi_grid"]) *
             len(SCAN_GRIDS["K_segments_grid"]) *
             len(SCAN_GRIDS["Omega0_grid"]))
    
    print(f"\nTotal configurations: {total}")
    print(f"Modes per config:     {len(BASE_CONFIG['omega_grid']) * len(BASE_CONFIG['m_grid'])}")
    print(f"Total simulations:    {total * len(BASE_CONFIG['omega_grid']) * len(BASE_CONFIG['m_grid'])}")
    
    # Create output directory
    os.makedirs("d:/extended_results", exist_ok=True)
    
    results_all = []
    count = 0
    
    print(f"\n{'='*80}\nRunning scan...\n{'='*80}")
    
    for lambda_A, lambda_phi, K_seg, Omega0 in product(
        SCAN_GRIDS["lambda_A_grid"],
        SCAN_GRIDS["lambda_phi_grid"],
        SCAN_GRIDS["K_segments_grid"],
        SCAN_GRIDS["Omega0_grid"]
    ):
        count += 1
        
        # Setup config for this parameter set
        params = BASE_CONFIG.copy()
        params.update({
            "lambda_A": lambda_A,
            "lambda_phi": lambda_phi,
            "K_segments": K_seg,
            "Omega0": Omega0
        })
        
        # Run SSZ and Baseline sweeps
        ssz_results = sweep(params, ssz_mode=True)
        base_results = sweep(params, ssz_mode=False)
        
        # Analyze results
        ssz_unstable = sum(1 for r in ssz_results if r["unstable"])
        base_unstable = sum(1 for r in base_results if r["unstable"])
        delta_unstable = ssz_unstable - base_unstable
        
        # Average Δlog(G)
        delta_log_G = []
        for sr, br in zip(ssz_results, base_results):
            if sr["omega"] == br["omega"] and sr["m"] == br["m"]:
                delta_log_G.append(math.log(sr["G_avg"]) - math.log(br["G_avg"]))
        avg_delta_log_G = sum(delta_log_G) / len(delta_log_G) if delta_log_G else 0.0
        
        # Best mode G ratio
        ssz_best_G = max(r["G_avg"] for r in ssz_results)
        base_best_G = max(r["G_avg"] for r in base_results)
        G_ratio_best = ssz_best_G / base_best_G if base_best_G > 0 else 1.0
        
        # Stabilization index: S = (Δunstable / base_unstable) + avg_delta_log_G
        if base_unstable > 0:
            S = (delta_unstable / base_unstable) + avg_delta_log_G
        else:
            S = avg_delta_log_G
        
        # Invariant error (approximate - would need separate test)
        invariant_error = 0.0  # Placeholder
        
        # Store results
        result = {
            "lambda_A": lambda_A,
            "lambda_phi": lambda_phi,
            "K_segments": K_seg,
            "Omega0": Omega0,
            "ssz_unstable": ssz_unstable,
            "base_unstable": base_unstable,
            "delta_unstable": delta_unstable,
            "avg_delta_log_G": avg_delta_log_G,
            "G_ratio_best": G_ratio_best,
            "invariant_error": invariant_error,
            "stabilization_index": S
        }
        results_all.append(result)
        
        # Progress output
        print(f"[{count:3d}/{total:3d}] lA={lambda_A:.2f}, lphi={lambda_phi:.2f}, K={K_seg:2d}, Omega={Omega0:.1f} -> "
              f"dU={delta_unstable:+d}, dlogG={avg_delta_log_G:+.3f}, S={S:+.3f}")
    
    return results_all

def analyze_and_export(results):
    """Analyze scan results and export"""
    
    print(f"\n{'='*80}\nAnalyzing results...\n{'='*80}")
    
    # Sort by stabilization index (most negative = strongest stabilization)
    results_sorted = sorted(results, key=lambda r: r["stabilization_index"])
    
    print("\nTop 3 stabilizing parameter sets:")
    for i, r in enumerate(results_sorted[:3], 1):
        print(f"  {i}. lA={r['lambda_A']:.2f}, lphi={r['lambda_phi']:.2f}, K={r['K_segments']}, Omega={r['Omega0']:.1f}")
        print(f"     S={r['stabilization_index']:.3f}, dUnstable={r['delta_unstable']:+d}, "
              f"dlogG={r['avg_delta_log_G']:.3f}")

    print("\nTop 3 destabilizing parameter sets:")
    for i, r in enumerate(results_sorted[-3:][::-1], 1):
        print(f"  {i}. lA={r['lambda_A']:.2f}, lphi={r['lambda_phi']:.2f}, K={r['K_segments']}, Omega={r['Omega0']:.1f}")
        print(f"     S={r['stabilization_index']:+.3f}, dUnstable={r['delta_unstable']:+d}, "
              f"dlogG={r['avg_delta_log_G']:.3f}")
    
    # Save CSV
    csv_file = "d:/extended_results/parameter_scan_results.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] {csv_file}")
    
    # Save JSON summary
    summary = {
        "total_configs": len(results),
        "top3_stabilizing": [
            {k: r[k] for k in ["lambda_A", "lambda_phi", "K_segments", "Omega0", 
                               "stabilization_index", "delta_unstable", "avg_delta_log_G"]}
            for r in results_sorted[:3]
        ],
        "top3_destabilizing": [
            {k: r[k] for k in ["lambda_A", "lambda_phi", "K_segments", "Omega0",
                               "stabilization_index", "delta_unstable", "avg_delta_log_G"]}
            for r in results_sorted[-3:][::-1]
        ],
        "trends": {
            "avg_stabilization_index": sum(r["stabilization_index"] for r in results) / len(results),
            "avg_delta_unstable": sum(r["delta_unstable"] for r in results) / len(results),
            "avg_delta_log_G": sum(r["avg_delta_log_G"] for r in results) / len(results)
        }
    }
    
    json_file = "d:/extended_results/scan_summary.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"[OK] {json_file}")
    
    return summary

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = parameter_scan()
    summary = analyze_and_export(results)
    
    print(f"\n{'='*80}\nCOMPLETE\n{'='*80}")
    print(f"\nPhysical Interpretation:")
    print(f"  Avg Stabilization Index: {summary['trends']['avg_stabilization_index']:.3f}")
    print(f"  Avg delta unstable modes:    {summary['trends']['avg_delta_unstable']:.2f}")
    print(f"  Avg delta log(G):             {summary['trends']['avg_delta_log_G']:.3f}")
    print(f"\nConclusion:")
    if summary['trends']['avg_stabilization_index'] < 0:
        print("  -> SSZ shows NET STABILIZING effect across parameter space")
    else:
        print("  -> SSZ shows mixed/destabilizing trends")
