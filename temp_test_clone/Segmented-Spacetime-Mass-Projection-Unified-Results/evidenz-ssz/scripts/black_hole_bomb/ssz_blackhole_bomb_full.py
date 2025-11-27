#!/usr/bin/env python3
# SSZ Black-Hole-Bomb: Complete Perfect-Pair Implementation
# (A) Local Propagation, (B) SSZ Transitions, (C) Mirror, (D) Instability
import math, json, csv, random, sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform.startswith('win'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

CONFIG = {
    "omega_grid": [0.1, 0.15, 0.2, 0.25, 0.3], "m_grid": [1, 2, 3, 4],
    "Omega0": 0.3, "epsilon": 0.1, "q": 2, "alpha": 0.8, "eta": 0.05,
    "R": 0.98, "K_coupling": 0.02, "K_segments": 32,
    "lambda_A": 0.02, "lambda_phi": 0.03, "sigma0": 1.0, "phi": PHI, "r0": 1.0,
    "M_theta": 2048, "N_max": 200, "seed": 1234,
    "tolerance_resonance": 1e-3, "tolerance_invariant": 0.01
}

# ============================================================================
# (A) LOCAL PROPAGATION LAW
# ============================================================================
def ssz_radius(theta, r0, phi):
    """r(θ) = r0·φ^(θ/(π/2))"""
    return r0 * (phi ** (theta / (PI / 2)))

def sigma(theta, sigma0, phi):
    """Segment density: σ(θ) = σ0·φ^(θ/(π/2))"""
    return sigma0 * (phi ** (theta / (PI / 2)))

def Omega_profile(theta, Omega0, epsilon, q):
    """Ω(θ) = Ω0[1 + ε·cos(qθ)]"""
    return Omega0 * (1 + epsilon * math.cos(q * theta))

def omega_corotating(theta, omega, m, Omega0, epsilon, q):
    """ω_co(θ) = ω - m·Ω(θ)"""
    return omega - m * Omega_profile(theta, Omega0, epsilon, q)

def gamma_loc(theta, omega, m, Omega0, epsilon, q, alpha, eta):
    """γ_loc(θ) = α·max(0,-ω_co(θ)) - η"""
    omega_co = omega_corotating(theta, omega, m, Omega0, epsilon, q)
    return alpha * max(0.0, -omega_co) - eta

# ============================================================================
# (B) SEGMENTED SPACETIME - Transition Maps
# ============================================================================
def generate_segments(K, sigma_fn, mode='uniform'):
    """Generate segment boundaries"""
    if mode == 'uniform':
        return [2 * PI * k / K for k in range(K)]
    elif mode == 'weighted':
        samples = [2 * PI * i / (K * 10) for i in range(K * 10)]
        sigma_cum = [sigma_fn(t) for t in samples]
        total = sum(sigma_cum)
        boundaries = []
        target = total / K
        current = 0.0
        for i, s in enumerate(sigma_cum):
            current += s
            if current >= target * len(boundaries) and len(boundaries) < K:
                boundaries.append(samples[i])
        return boundaries
    return [2 * PI * k / K for k in range(K)]

def transition_amplitude(theta_k, sigma0, phi, lambda_A):
    """T_A(θ_k) = exp(-λ_A·σ(θ_k))"""
    return math.exp(-lambda_A * sigma(theta_k, sigma0, phi))

def transition_phase(theta_k, sigma0, phi, lambda_phi):
    """Δφ_SSZ(θ_k) = λ_φ·σ(θ_k))"""
    return lambda_phi * sigma(theta_k, sigma0, phi)

# ============================================================================
# (C) ONE ROUNDTRIP with full arc-length integration
# ============================================================================
def one_roundtrip_full(A, phi_acc, omega, m, params):
    """Complete roundtrip with:
    - Arc-length ds = r(θ)dθ
    - Local gain ∫γ_loc(θ)ds
    - SSZ transitions ∏T_A(θ_k), ΣΔφ_SSZ(θ_k)
    - Mirror R·(1-K)
    """
    Omega0, eps, q = params["Omega0"], params["epsilon"], params["q"]
    alpha, eta = params["alpha"], params["eta"]
    R, K_coup = params["R"], params["K_coupling"]
    r0, phi_g = params["r0"], params["phi"]
    sigma0 = params["sigma0"]
    lambda_A, lambda_phi = params["lambda_A"], params["lambda_phi"]
    K_seg, M_theta = params["K_segments"], params["M_theta"]
    
    # Discretization
    d_theta = 2 * PI / M_theta
    
    # Generate segment boundaries
    sigma_fn = lambda t: sigma(t, sigma0, phi_g)
    theta_k_list = generate_segments(K_seg, sigma_fn, mode='uniform')
    
    # Integrate local gain with arc-length
    integral_gamma = 0.0
    integral_k_phase = 0.0
    
    for i in range(M_theta):
        theta = d_theta * i
        r_theta = ssz_radius(theta, r0, phi_g)
        ds = r_theta * d_theta  # Arc-length element
        
        gamma_theta = gamma_loc(theta, omega, m, Omega0, eps, q, alpha, eta)
        integral_gamma += gamma_theta * ds
        
        # Phase accumulation (wave number k ≈ ω in natural units)
        k_theta = omega  # Could add metric corrections
        integral_k_phase += k_theta * d_theta
    
    # Local gain factor
    G_local = math.exp(integral_gamma)
    
    # SSZ transition factors
    log_T_A_sum = 0.0
    dphi_SSZ_sum = 0.0
    
    for theta_k in theta_k_list:
        T_A_k = transition_amplitude(theta_k, sigma0, phi_g, lambda_A)
        log_T_A_sum += math.log(T_A_k)
        dphi_SSZ_sum += transition_phase(theta_k, sigma0, phi_g, lambda_phi)
    
    T_A_product = math.exp(log_T_A_sum)
    
    # Mirror reflectivity
    mirror_factor = R * (1 - K_coup)
    
    # Total gain this roundtrip
    G_round = G_local * T_A_product * mirror_factor
    
    # Update amplitude and phase
    A_next = A * G_round
    dphi_round = integral_k_phase + dphi_SSZ_sum
    phi_next = phi_acc + dphi_round
    
    return A_next, phi_next, G_round, dphi_round

# ============================================================================
# (D) MODE EVOLUTION with resonance check
# ============================================================================
def run_mode_full(omega, m, params):
    """Evolve mode with full tracking and resonance check"""
    N_max = params["N_max"]
    tol_res = params["tolerance_resonance"]
    
    A, phi_acc = 1.0, 0.0
    A_history, G_history, phi_history = [A], [], [phi_acc]
    
    exploded = dead = False
    rounds_to_10x = rounds_to_1e6 = None
    
    for n in range(N_max):
        A_next, phi_next, G_round, dphi_round = one_roundtrip_full(A, phi_acc, omega, m, params)
        
        A_history.append(A_next)
        G_history.append(G_round)
        phi_history.append(phi_next)
        
        if rounds_to_10x is None and A_next > 10.0:
            rounds_to_10x = n + 1
        if rounds_to_1e6 is None and A_next > 1e6:
            rounds_to_1e6 = n + 1
        
        if A_next > 1e12:
            exploded = True
            break
        if A_next < 1e-12:
            dead = True
            break
        
        A, phi_acc = A_next, phi_next
    
    # Resonance check: Δφ_round ≈ 2πℓ
    if len(G_history) > 0:
        dphi_per_round = (phi_history[-1] - phi_history[0]) / len(G_history)
        phase_mismatch = abs(dphi_per_round % (2 * PI))
        resonant = min(phase_mismatch, 2 * PI - phase_mismatch) < tol_res
        
        # Average gain
        log_G_avg = sum(math.log(max(G, 1e-100)) for G in G_history) / len(G_history)
        G_avg = math.exp(log_G_avg)
        G_final = G_history[-1]
    else:
        resonant = False
        G_avg = G_final = 1.0
    
    unstable = G_avg > 1.0
    
    return {
        "omega": omega, "m": m,
        "G_avg": G_avg, "G_final": G_final,
        "resonant": resonant, "unstable": unstable,
        "exploded": exploded, "dead": dead,
        "rounds_to_10x": rounds_to_10x,
        "rounds_to_1e6": rounds_to_1e6,
        "A_history": A_history,
        "G_history": G_history,
        "phi_history": phi_history,
        "final_rounds": len(G_history)
    }

# ============================================================================
# SWEEP & BASELINE
# ============================================================================
def sweep_full(params, ssz_mode=True):
    """Parameter sweep with full physics"""
    if not ssz_mode:
        params = params.copy()
        params["lambda_A"] = params["lambda_phi"] = params["sigma0"] = 0.0
    
    results = []
    mode_name = "SSZ" if ssz_mode else "Baseline"
    print(f"\n{'='*80}\n{mode_name} SWEEP\n{'='*80}")
    
    total = len(params["omega_grid"]) * len(params["m_grid"])
    count = 0
    
    for omega in params["omega_grid"]:
        for m in params["m_grid"]:
            count += 1
            result = run_mode_full(omega, m, params)
            
            result.update({
                "Omega0": params["Omega0"], "epsilon": params["epsilon"],
                "q": params["q"], "R": params["R"], "K_coupling": params["K_coupling"],
                "K_segments": params["K_segments"], "lambda_A": params["lambda_A"],
                "lambda_phi": params["lambda_phi"], "sigma0": params["sigma0"],
                "r0": params["r0"], "phi": params["phi"],
                "alpha": params["alpha"], "eta": params["eta"],
                "ssz_mode": ssz_mode
            })
            results.append(result)
            
            status = "UNSTABLE" if result["unstable"] else "STABLE"
            res_mark = " [RESONANT]" if result["resonant"] else ""
            print(f"[{count:2d}/{total:2d}] omega={omega:.2f}, m={m}: {status} G={result['G_avg']:.4f}{res_mark}")
    
    return results

# ============================================================================
# INVARIANT CHECK (analytical limit)
# ============================================================================
def check_invariant(params):
    """Verify analytical limit: ε=0, SSZ off"""
    print(f"\n{'='*80}\nINVARIANT CHECK\n{'='*80}")
    
    test_params = params.copy()
    test_params["epsilon"] = 0.0
    test_params["lambda_A"] = test_params["lambda_phi"] = test_params["sigma0"] = 0.0
    
    omega, m = 0.2, 2
    result = run_mode_full(omega, m, test_params)
    G_sim = result["G_avg"]
    
    # Analytical: G = exp((α·max(0,m·Ω0-ω) - η)·L) · R·(1-K)
    Omega0, alpha, eta = test_params["Omega0"], test_params["alpha"], test_params["eta"]
    R, K_coup = test_params["R"], test_params["K_coupling"]
    r0, phi_g = test_params["r0"], test_params["phi"]
    M_theta = test_params["M_theta"]
    
    # Arc length L = ∫r(θ)dθ
    d_theta = 2 * PI / M_theta
    L = sum(ssz_radius(d_theta * i, r0, phi_g) * d_theta for i in range(M_theta))
    
    gamma_uniform = alpha * max(0.0, m * Omega0 - omega) - eta
    G_analytical = math.exp(gamma_uniform * L) * R * (1 - K_coup)
    
    rel_error = abs(G_sim - G_analytical) / G_analytical
    passed = rel_error < params["tolerance_invariant"]
    
    print(f"\nTest: omega={omega}, m={m}, Omega0={Omega0} (uniform, no SSZ)")
    print(f"  G_simulated:  {G_sim:.8f}")
    print(f"  G_analytical: {G_analytical:.8f}")
    print(f"  Rel. Error:   {rel_error:.6f} ({rel_error*100:.3f}%)")
    print(f"  Tolerance:    {params['tolerance_invariant']*100:.1f}%")
    print(f"  Status:       {'PASS' if passed else 'FAIL'}")
    
    return {"G_sim": G_sim, "G_analytical": G_analytical, "error": rel_error, "passed": passed}

# ============================================================================
# COMPARISON & OUTPUT
# ============================================================================
def compare_full(ssz_results, base_results):
    """Compare SSZ vs Baseline"""
    ssz_unstable = sum(1 for r in ssz_results if r["unstable"])
    base_unstable = sum(1 for r in base_results if r["unstable"])
    
    ssz_resonant = sum(1 for r in ssz_results if r["resonant"] and r["unstable"])
    base_resonant = sum(1 for r in base_results if r["resonant"] and r["unstable"])
    
    ssz_best = max(ssz_results, key=lambda r: r["G_avg"])
    base_best = max(base_results, key=lambda r: r["G_avg"])
    
    delta_log_G = []
    for sr, br in zip(ssz_results, base_results):
        if sr["omega"] == br["omega"] and sr["m"] == br["m"]:
            delta_log_G.append(math.log(sr["G_avg"]) - math.log(br["G_avg"]))
    
    return {
        "ssz_unstable": ssz_unstable, "base_unstable": base_unstable,
        "ssz_resonant": ssz_resonant, "base_resonant": base_resonant,
        "ssz_best": {"omega": ssz_best["omega"], "m": ssz_best["m"], "G": ssz_best["G_avg"]},
        "base_best": {"omega": base_best["omega"], "m": base_best["m"], "G": base_best["G_avg"]},
        "avg_delta_log_G": sum(delta_log_G) / len(delta_log_G) if delta_log_G else 0.0,
        "delta_unstable": ssz_unstable - base_unstable
    }

def save_csv_full(results, filename):
    """Save with all fields"""
    if not results: return
    cols = ["omega", "m", "Omega0", "epsilon", "q", "R", "K_coupling", "K_segments",
            "lambda_A", "lambda_phi", "sigma0", "r0", "phi", "alpha", "eta",
            "G_avg", "G_final", "resonant", "unstable", "exploded", "dead",
            "rounds_to_10x", "rounds_to_1e6", "final_rounds", "ssz_mode"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"[OK] {filename}")

def save_best_trace(result, filename):
    """Save A vs roundtrip for best mode"""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["roundtrip", "amplitude", "gain", "phase"])
        for n in range(len(result["A_history"])):
            A = result["A_history"][n]
            G = result["G_history"][n] if n < len(result["G_history"]) else ""
            phi = result["phi_history"][n] if n < len(result["phi_history"]) else ""
            writer.writerow([n, A, G, phi])
    print(f"[OK] {filename}")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("SSZ BLACK-HOLE-BOMB: Complete Perfect-Pair Implementation")
    print("="*80)
    print("(A) Local Propagation | (B) SSZ Transitions | (C) Mirror | (D) Instability\n")
    
    random.seed(CONFIG["seed"])
    
    with open("d:/run_config.json", "w") as f:
        json.dump(CONFIG, f, indent=2)
    print("[OK] d:/run_config.json")
    
    # Invariant check
    inv_check = check_invariant(CONFIG)
    
    # SSZ sweep
    ssz_results = sweep_full(CONFIG, ssz_mode=True)
    
    # Baseline sweep
    base_results = sweep_full(CONFIG, ssz_mode=False)
    
    # Compare
    print(f"\n{'='*80}\nCOMPARISON\n{'='*80}")
    comp = compare_full(ssz_results, base_results)
    
    # Save results
    save_csv_full(ssz_results + base_results, "d:/spectrum_results.csv")
    
    # Best mode trace
    ssz_best = max(ssz_results, key=lambda r: r["G_avg"])
    save_best_trace(ssz_best, "d:/growth_best_mode.csv")
    
    # Summary
    summary = {**comp, "invariant_check": inv_check}
    with open("d:/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("[OK] d:/summary.json")
    
    # Print summary
    print(f"\n{'='*80}\nSUMMARY\n{'='*80}")
    print(f"SSZ:      {comp['ssz_unstable']} unstable ({comp['ssz_resonant']} resonant)")
    print(f"Baseline: {comp['base_unstable']} unstable ({comp['base_resonant']} resonant)")
    print(f"\nBest SSZ:      omega={comp['ssz_best']['omega']:.2f}, m={comp['ssz_best']['m']}, G={comp['ssz_best']['G']:.6f}")
    print(f"Best Baseline: omega={comp['base_best']['omega']:.2f}, m={comp['base_best']['m']}, G={comp['base_best']['G']:.6f}")
    print(f"\nAvg Delta-log(G): {comp['avg_delta_log_G']:.6f}")
    print(f"Delta unstable:   {comp['delta_unstable']:+d}")
    print(f"\nInvariant check:  {'PASS' if inv_check['passed'] else 'FAIL'} (error={inv_check['error']:.4f})")
    print(f"\n{'='*80}\nCOMPLETE\n{'='*80}")
