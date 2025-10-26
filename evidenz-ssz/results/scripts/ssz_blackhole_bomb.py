#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Black-Hole-Bomb: Superradiant Ring-Resonator (Perfect-Pair Style)

Based on:
- Zel'dovich (1971): "Generation of Waves by a Rotating Body"
- Press & Teukolsky (1972): "Black-hole Bomb" (Nature 238, 211-212)
- Braidotti et al. (2024): First lab demonstration
  https://www.livescience.com/space/black-holes/physicists-create-black-hole-bomb-for-first-time-on-earth-validating-decades-old-theory

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import math, json, csv, random, sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform.startswith('win'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

DEFAULT_CONFIG = {
    "omega_grid": [0.1, 0.15, 0.2, 0.25, 0.3], "m_grid": [1, 2, 3, 4],
    "Omega0": 0.3, "epsilon": 0.1, "q": 2, "alpha": 0.8, "eta": 0.05,
    "R": 0.98, "K_coupling": 0.02, "K_segments": 32,
    "lambda_A": 0.02, "lambda_phi": 0.03,
    "sigma0": 1.0, "phi": PHI, "r0": 1.0,
    "M_theta": 2048, "N_max": 200, "seed": 1234
}

def ssz_radius(theta, r0, phi): return r0 * (phi ** (theta / (PI / 2)))
def sigma(theta, sigma0, phi): return sigma0 * (phi ** (theta / (PI / 2)))
def Omega_profile(theta, Omega0, epsilon, q): return Omega0 * (1 + epsilon * math.cos(q * theta))

def gamma_loc(theta, omega, m, Omega0, epsilon, q, alpha, eta):
    Omega_theta = Omega_profile(theta, Omega0, epsilon, q)
    omega_co = omega - m * Omega_theta
    return alpha * max(0.0, -omega_co) - eta

def one_roundtrip(A, phi_acc, omega, m, params):
    Omega0, epsilon, q = params["Omega0"], params["epsilon"], params["q"]
    alpha, eta = params["alpha"], params["eta"]
    R, K_coupling = params["R"], params["K_coupling"]
    r0, phi_g, sigma0 = params["r0"], params["phi"], params["sigma0"]
    lambda_A, lambda_phi = params["lambda_A"], params["lambda_phi"]
    K_seg, M_theta = params["K_segments"], params["M_theta"]
    
    d_theta = 2 * PI / M_theta
    theta_k_list = [2 * PI * k / K_seg for k in range(K_seg)]
    
    integral_gamma = integral_k = 0.0
    for i in range(M_theta):
        theta = d_theta * i
        r_theta = ssz_radius(theta, r0, phi_g)
        ds = r_theta * d_theta
        gamma_theta = gamma_loc(theta, omega, m, Omega0, epsilon, q, alpha, eta)
        integral_gamma += gamma_theta * ds
        integral_k += omega * d_theta
    
    log_TA_sum = dphi_SSZ_sum = 0.0
    for theta_k in theta_k_list:
        sigma_k = sigma(theta_k, sigma0, phi_g)
        log_TA_sum += -lambda_A * sigma_k
        dphi_SSZ_sum += lambda_phi * sigma_k
    
    G_round = math.exp(integral_gamma + log_TA_sum) * R * (1 - K_coupling)
    return A * G_round, phi_acc + integral_k + dphi_SSZ_sum, G_round, integral_k + dphi_SSZ_sum

def run_mode(omega, m, params):
    A, phi_acc = 1.0, 0.0
    A_history, G_history = [A], []
    rounds_to_10x = rounds_to_1e6 = None
    
    for n in range(params["N_max"]):
        A_next, phi_next, G_round, _ = one_roundtrip(A, phi_acc, omega, m, params)
        A_history.append(A_next)
        G_history.append(G_round)
        
        if rounds_to_10x is None and A_next > 10.0: rounds_to_10x = n + 1
        if rounds_to_1e6 is None and A_next > 1e6: rounds_to_1e6 = n + 1
        if A_next > 1e12 or A_next < 1e-12: break
        A, phi_acc = A_next, phi_next
    
    G_avg = math.exp(sum(math.log(max(G, 1e-100)) for G in G_history) / len(G_history)) if G_history else 1.0
    return {
        "omega": omega, "m": m, "G_avg": G_avg, "unstable": G_avg > 1.0,
        "rounds_to_10x": rounds_to_10x, "rounds_to_1e6": rounds_to_1e6,
        "A_history": A_history, "G_history": G_history
    }

def sweep(params, ssz_mode=True):
    if not ssz_mode:
        params = params.copy()
        params["lambda_A"] = params["lambda_phi"] = params["sigma0"] = 0.0
    
    results = []
    mode_name = "SSZ" if ssz_mode else "Baseline"
    print(f"\n{'='*80}\nSWEEP: {mode_name} mode\n{'='*80}")
    
    for omega in params["omega_grid"]:
        for m in params["m_grid"]:
            result = run_mode(omega, m, params)
            result.update({k: params[k] for k in ["Omega0", "epsilon", "q", "R", "K_coupling", "K_segments", "lambda_A", "lambda_phi", "sigma0", "r0", "phi", "alpha", "eta"]})
            result["ssz_mode"] = ssz_mode
            results.append(result)
            status = f"[UNSTABLE] G={result['G_avg']:.4f}" if result["unstable"] else f"[STABLE]   G={result['G_avg']:.4f}"
            print(f"  omega={omega:.2f}, m={m}: {status}")
    return results

def compare(ssz_results, base_results):
    ssz_unstable = sum(1 for r in ssz_results if r["unstable"])
    base_unstable = sum(1 for r in base_results if r["unstable"])
    ssz_best = max(ssz_results, key=lambda r: r["G_avg"])
    base_best = max(base_results, key=lambda r: r["G_avg"])
    
    delta_log_G = [math.log(sr["G_avg"]) - math.log(br["G_avg"])
                   for sr, br in zip(ssz_results, base_results)
                   if sr["omega"] == br["omega"] and sr["m"] == br["m"]]
    
    return {
        "ssz_unstable_count": ssz_unstable, "base_unstable_count": base_unstable,
        "ssz_best_G": ssz_best["G_avg"], "ssz_best_omega": ssz_best["omega"], "ssz_best_m": ssz_best["m"],
        "base_best_G": base_best["G_avg"], "base_best_omega": base_best["omega"], "base_best_m": base_best["m"],
        "avg_delta_log_G": sum(delta_log_G) / len(delta_log_G) if delta_log_G else 0.0
    }

def save_csv(results, filename):
    if not results: return
    columns = ["omega", "m", "Omega0", "epsilon", "q", "R", "K_coupling", "K_segments",
               "lambda_A", "lambda_phi", "sigma0", "r0", "phi", "alpha", "eta",
               "G_avg", "unstable", "rounds_to_10x", "rounds_to_1e6", "ssz_mode"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"[OK] Saved: {filename}")

if __name__ == "__main__":
    print("="*80)
    print("SSZ BLACK-HOLE-BOMB SIMULATOR")
    print("="*80)
    print("Perfect-Pair Mathematics (Casu & Wrede 2025)\n")
    
    random.seed(DEFAULT_CONFIG["seed"])
    with open("d:/run_config.json", "w") as f: json.dump(DEFAULT_CONFIG, f, indent=2)
    
    print("[1/3] Running SSZ sweep...")
    ssz_results = sweep(DEFAULT_CONFIG, ssz_mode=True)
    
    print("\n[2/3] Running Baseline sweep...")
    base_results = sweep(DEFAULT_CONFIG, ssz_mode=False)
    
    print("\n[3/3] Comparing results...")
    summary = compare(ssz_results, base_results)
    
    save_csv(ssz_results + base_results, "d:/spectrum_results.csv")
    with open("d:/summary.json", "w") as f: json.dump(summary, f, indent=2)
    
    print(f"\n{'='*80}\nRESULTS SUMMARY\n{'='*80}")
    print(f"SSZ:      {summary['ssz_unstable_count']} unstable modes")
    print(f"Baseline: {summary['base_unstable_count']} unstable modes")
    print(f"\nBest SSZ mode: omega={summary['ssz_best_omega']:.2f}, m={summary['ssz_best_m']}, G={summary['ssz_best_G']:.6f}")
    print(f"Best Baseline:  omega={summary['base_best_omega']:.2f}, m={summary['base_best_m']}, G={summary['base_best_G']:.6f}")
    print(f"\nAverage Delta-log(G): {summary['avg_delta_log_G']:.6f}")
    print(f"\n{'='*80}\nCOMPLETE! Files on D:\\\n{'='*80}")
