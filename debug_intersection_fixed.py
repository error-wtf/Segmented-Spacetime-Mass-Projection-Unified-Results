#!/usr/bin/env python3
"""
Debug: Why doesn't SSZ intersect with GR at alpha=1.0?
"""
import numpy as np
import matplotlib.pyplot as plt

PHI = (1 + np.sqrt(5)) / 2
G = 6.674e-11
c = 2.998e8

def schwarzschild_rs(M):
    return 2 * G * M / c**2

def xi_exponential(r, M, xi_max=1.0):
    r_s = schwarzschild_rs(M)
    return xi_max * (1 - np.exp(-r_s / r))

def time_dilation_ssz(r, M, xi_max=1.0, alpha=1.0):
    xi = xi_exponential(r, M, xi_max)
    return PHI ** (-alpha * xi)

def time_dilation_gr(r, M):
    r_s = schwarzschild_rs(M)
    return np.sqrt(1 - r_s / r)

# Test with different alpha values
M = 1.0  # normalized
r_arr = np.linspace(1.05, 6.0, 1000)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for idx, alpha in enumerate([0.5, 1.0, 1.5, 2.0]):
    ax = axes[idx //2, idx % 2]
    
    D_GR = time_dilation_gr(r_arr, M)
    D_SSZ = time_dilation_ssz(r_arr, M, xi_max=1.0, alpha=alpha)
    
    ax.plot(r_arr, D_GR, 'b-', linewidth=2, label='GR')
    ax.plot(r_arr, D_SSZ, 'r-', linewidth=2, label=f'SSZ (α={alpha})')
    ax.set_xlabel('r / r_s')
    ax.set_ylabel('Time Dilation D(r)')
    ax.set_title(f'α = {alpha}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.0])
    
    # Check if they intersect
    diff = D_SSZ - D_GR
    if np.any(diff[:-1] * diff[1:] < 0):
        # Find approximate intersection
        idx_cross = np.where(diff[:-1] * diff[1:] < 0)[0][0]
        r_star = r_arr[idx_cross]
        ax.axvline(r_star, color='green', linestyle='--', alpha=0.5)
        ax.set_title(f'α = {alpha}, r* ≈ {r_star:.3f} r_s')
    else:
        ax.set_title(f'α = {alpha} - NO INTERSECTION!')

plt.tight_layout()
plt.savefig('outputs/debug_alpha_sweep.png', dpi=150)
print("Saved: outputs/debug_alpha_sweep.png")

# Print values at r = 1.386562 (expected intersection)
r_test = 1.386562
xi_test = xi_exponential(r_test, M, xi_max=1.0)
print(f"\nAt r* = {r_test} r_s:")
print(f"  Xi = {xi_test:.6f}")
print(f"  D_GR = {time_dilation_gr(r_test, M):.6f}")
print(f"  D_SSZ (α=0.5) = {time_dilation_ssz(r_test, M, xi_max=1.0, alpha=0.5):.6f}")
print(f"  D_SSZ (α=1.0) = {time_dilation_ssz(r_test, M, xi_max=1.0, alpha=1.0):.6f}")
print(f"  D_SSZ (α=1.5) = {time_dilation_ssz(r_test, M, xi_max=1.0, alpha=1.5):.6f}")

# Find correct alpha for intersection at r* = 1.386562
from scipy.optimize import brentq

def find_alpha_for_intersection(r_star_target, M, xi_max=1.0):
    """Find alpha such that SSZ = GR at given r_star"""
    def equation(alpha):
        D_GR_target = time_dilation_gr(r_star_target, M)
        D_SSZ = time_dilation_ssz(r_star_target, M, xi_max, alpha)
        return D_SSZ - D_GR_target
    
    try:
        alpha_correct = brentq(equation, 0.1, 3.0)
        return alpha_correct
    except:
        return None

alpha_correct = find_alpha_for_intersection(1.386562, M)
if alpha_correct:
    print(f"\nCORRECT alpha for intersection at r* = 1.386562 rs: α = {alpha_correct:.6f}")
    
    # Verify
    D_GR_check = time_dilation_gr(1.386562, M)
    D_SSZ_check = time_dilation_ssz(1.386562, M, xi_max=1.0, alpha=alpha_correct)
    print(f"  Verification: D_GR = {D_GR_check:.6f}, D_SSZ = {D_SSZ_check:.6f}")
    print(f"  Difference: {abs(D_GR_check - D_SSZ_check):.2e}")

