#!/usr/bin/env python3
"""
SSZ Resonance Explorer - Meta-Visualization Tool
================================================
Combined Parameter Scan + Interactive Visualizer + Animation Export

Click-to-Explore workflow:
1. Run parameter scan → generate heatmap
2. Click on heatmap point → open live visualizer for that config
3. Export animated phi-spiral evolution

Perfect-Pair Mathematics Style (Casu & Wrede 2025)
© 2025 Carmen Wrede, Lino Casu
"""
import math, json, csv, sys, os
import numpy as np
from itertools import product

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.widgets import Button
    import matplotlib.animation as animation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[ERROR] matplotlib required")
    sys.exit(1)

PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

# ============================================================================
# CORE PHYSICS (reused)
# ============================================================================

def ssz_radius(theta, r0=1.0, phi=PHI):
    return r0 * (phi ** (theta / (PI / 2)))

def segment_density(theta, sigma0=1.0, phi=PHI):
    return sigma0 * (phi ** (theta / (PI / 2)))

def Omega_profile(theta, Omega0, epsilon=0.1, q=2):
    return Omega0 * (1 + epsilon * math.cos(q * theta))

def gamma_loc(theta, omega, m, Omega0, epsilon=0.1, q=2, alpha=0.8, eta=0.05):
    omega_co = omega - m * Omega_profile(theta, Omega0, epsilon, q)
    return alpha * max(0.0, -omega_co) - eta

def compute_G_for_mode(omega, m, lambda_A, lambda_phi, K_segments, Omega0, M_theta=512):
    """Fast G computation"""
    r0, phi_g, sigma0 = 1.0, PHI, 1.0
    alpha, eta = 0.8, 0.05
    R, K_coupling = 0.98, 0.02
    epsilon, q = 0.1, 2
    
    d_theta = 2 * PI / M_theta
    theta_k_list = [2 * PI * k / K_segments for k in range(K_segments)]
    
    integral_gamma = 0.0
    for i in range(M_theta):
        theta = d_theta * i
        r_theta = ssz_radius(theta, r0, phi_g)
        ds = r_theta * d_theta
        gamma_theta = gamma_loc(theta, omega, m, Omega0, epsilon, q, alpha, eta)
        integral_gamma += gamma_theta * ds
    
    log_T_A_sum = 0.0
    for theta_k in theta_k_list:
        sigma_k = segment_density(theta_k, sigma0, phi_g)
        log_T_A_sum += -lambda_A * sigma_k
    
    G = math.exp(integral_gamma + log_T_A_sum) * R * (1 - K_coupling)
    return G

def compute_amplitude_curve(omega, m, lambda_A, lambda_phi, K_segments, Omega0, N_max=50):
    """Compute amplitude evolution"""
    G = compute_G_for_mode(omega, m, lambda_A, lambda_phi, K_segments, Omega0)
    
    A_history = [1.0]
    A = 1.0
    for n in range(N_max):
        A *= G
        A_history.append(A)
        if A > 1e6 or A < 1e-6:
            break
    
    return A_history, G

# ============================================================================
# QUICK PARAMETER SCAN
# ============================================================================

def quick_scan():
    """Reduced parameter scan for interactive exploration"""
    
    print("="*80)
    print("SSZ RESONANCE EXPLORER - Quick Scan")
    print("="*80)
    
    # Reduced grid for speed
    lambda_A_grid = [0.00, 0.02, 0.05]
    lambda_phi_grid = [0.00, 0.02, 0.05]
    K_segments_grid = [16, 32]
    Omega0_grid = [0.2, 0.3, 0.4]
    
    omega_grid = [0.1, 0.15, 0.2, 0.25, 0.3]
    m_grid = [1, 2, 3, 4]
    
    total = len(lambda_A_grid) * len(lambda_phi_grid) * len(K_segments_grid) * len(Omega0_grid)
    print(f"\nScanning {total} parameter combinations...")
    
    results = []
    count = 0
    
    for lambda_A, lambda_phi, K_seg, Omega0 in product(
        lambda_A_grid, lambda_phi_grid, K_segments_grid, Omega0_grid
    ):
        count += 1
        
        # Quick analysis
        unstable_count = 0
        total_log_G = 0.0
        
        for omega in omega_grid:
            for m in m_grid:
                G = compute_G_for_mode(omega, m, lambda_A, lambda_phi, K_seg, Omega0)
                if G > 1.0:
                    unstable_count += 1
                total_log_G += math.log(G)
        
        avg_log_G = total_log_G / (len(omega_grid) * len(m_grid))
        
        results.append({
            "lambda_A": lambda_A,
            "lambda_phi": lambda_phi,
            "K_segments": K_seg,
            "Omega0": Omega0,
            "unstable_count": unstable_count,
            "avg_log_G": avg_log_G
        })
        
        print(f"  [{count:2d}/{total:2d}] lA={lambda_A:.2f}, lphi={lambda_phi:.2f}, K={K_seg}, Omega={Omega0:.1f} -> "
              f"{unstable_count} unstable, <log(G)>={avg_log_G:.2f}")
    
    print("\n[OK] Scan complete")
    return results, lambda_A_grid, lambda_phi_grid, K_segments_grid, Omega0_grid

# ============================================================================
# RESONANCE EXPLORER CLASS
# ============================================================================

class ResonanceExplorer:
    def __init__(self):
        self.scan_results = None
        self.grids = None
        self.selected_params = None
        
    def run_scan(self):
        """Run parameter scan"""
        self.scan_results, *self.grids = quick_scan()
        
    def create_interactive_heatmap(self):
        """Create clickable heatmap interface"""
        
        if self.scan_results is None:
            self.run_scan()
        
        lambda_A_grid, lambda_phi_grid, K_grid, Omega0_grid = self.grids
        
        # Create figure
        fig = plt.figure(figsize=(18, 10), facecolor='#0a0a1e')
        fig.suptitle('SSZ Resonance Explorer - Click to Explore', 
                     color='white', fontsize=16, fontweight='bold')
        
        # Create subplots for different K and Omega0 combinations
        gs = gridspec.GridSpec(len(Omega0_grid), len(K_grid), 
                              figure=fig, hspace=0.3, wspace=0.3)
        
        self.axes = []
        self.heatmaps = []
        
        for i, Omega0 in enumerate(Omega0_grid):
            for j, K in enumerate(K_grid):
                ax = fig.add_subplot(gs[i, j], facecolor='#1a1a2e')
                
                # Filter results for this K and Omega0
                filtered = [r for r in self.scan_results 
                           if r['K_segments'] == K and r['Omega0'] == Omega0]
                
                # Create heatmap grid
                heatmap_data = np.zeros((len(lambda_phi_grid), len(lambda_A_grid)))
                for r in filtered:
                    idx_A = lambda_A_grid.index(r['lambda_A'])
                    idx_phi = lambda_phi_grid.index(r['lambda_phi'])
                    heatmap_data[idx_phi, idx_A] = r['unstable_count']
                
                # Plot heatmap
                im = ax.imshow(heatmap_data, aspect='auto', origin='lower', cmap='hot',
                              extent=[lambda_A_grid[0], lambda_A_grid[-1], 
                                     lambda_phi_grid[0], lambda_phi_grid[-1]])
                
                ax.set_title(f'K={K}, Omega0={Omega0:.1f}', color='white', fontsize=10)
                ax.set_xlabel('lambda_A', color='white', fontsize=9)
                ax.set_ylabel('lambda_phi', color='white', fontsize=9)
                ax.tick_params(colors='white', labelsize=8)
                
                # Add colorbar
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('Unstable Modes', color='white')
                cbar.ax.tick_params(colors='white')
                
                self.axes.append(ax)
                self.heatmaps.append((K, Omega0))
        
        # Connect click event
        fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Add info text
        fig.text(0.5, 0.02, 'Click on any point to open Live Visualizer for that configuration',
                ha='center', color='cyan', fontsize=12, fontweight='bold')
        
        plt.show()
    
    def on_click(self, event):
        """Handle click on heatmap"""
        if event.inaxes not in self.axes:
            return
        
        # Find which subplot was clicked
        ax_idx = self.axes.index(event.inaxes)
        K, Omega0 = self.heatmaps[ax_idx]
        
        # Get clicked lambda values
        lambda_A = event.xdata
        lambda_phi = event.ydata
        
        if lambda_A is None or lambda_phi is None:
            return
        
        # Round to nearest grid point
        lambda_A_grid, lambda_phi_grid = self.grids[0], self.grids[1]
        lambda_A = min(lambda_A_grid, key=lambda x: abs(x - lambda_A))
        lambda_phi = min(lambda_phi_grid, key=lambda x: abs(x - lambda_phi))
        
        print(f"\n{'='*80}")
        print(f"SELECTED: lA={lambda_A:.2f}, lphi={lambda_phi:.2f}, K={K}, Omega0={Omega0:.1f}")
        print(f"{'='*80}")
        
        # Store selected params
        self.selected_params = {
            'lambda_A': lambda_A,
            'lambda_phi': lambda_phi,
            'K_segments': K,
            'Omega0': Omega0
        }
        
        # Open live visualizer
        self.open_live_visualizer()
    
    def open_live_visualizer(self):
        """Open live visualizer with selected parameters"""
        
        if self.selected_params is None:
            print("[ERROR] No parameters selected")
            return
        
        print("\nOpening Live Visualizer...")
        
        # Create new figure
        fig = plt.figure(figsize=(16, 9), facecolor='#0a0a1e')
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        params = self.selected_params
        omega, m = 0.25, 2  # Default mode
        
        # Panel 1: Amplitude curve
        ax1 = fig.add_subplot(gs[0, 0], facecolor='#1a1a2e')
        ax1.set_title('Amplitude Evolution', color='white', fontweight='bold')
        ax1.set_xlabel('Roundtrip', color='white')
        ax1.set_ylabel('Amplitude (log)', color='white')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.2, color='white')
        ax1.tick_params(colors='white')
        
        A_history, G = compute_amplitude_curve(omega, m, params['lambda_A'],
                                               params['lambda_phi'], 
                                               params['K_segments'], params['Omega0'])
        rounds = list(range(len(A_history)))
        ax1.plot(rounds, A_history, 'cyan', linewidth=2)
        ax1.axhline(1, color='red', linestyle='--', alpha=0.5)
        ax1.axhline(10, color='orange', linestyle='--', alpha=0.5)
        
        # Panel 2: Instability map
        ax2 = fig.add_subplot(gs[0, 1:], facecolor='#1a1a2e')
        ax2.set_title('Instability Map', color='white', fontweight='bold')
        ax2.set_xlabel('ω', color='white')
        ax2.set_ylabel('m', color='white')
        ax2.tick_params(colors='white')
        
        omega_grid = np.linspace(0.05, 0.40, 20)
        m_grid = [1, 2, 3, 4, 5]
        G_grid = np.zeros((len(m_grid), len(omega_grid)))
        
        for i, m_val in enumerate(m_grid):
            for j, omega_val in enumerate(omega_grid):
                G_val = compute_G_for_mode(omega_val, m_val, params['lambda_A'],
                                           params['lambda_phi'], params['K_segments'], 
                                           params['Omega0'])
                G_grid[i, j] = math.log10(G_val) if G_val > 0 else -6
        
        im = ax2.imshow(G_grid, aspect='auto', origin='lower', cmap='hot',
                       extent=[omega_grid[0], omega_grid[-1], m_grid[0]-0.5, m_grid[-1]+0.5])
        ax2.contour(omega_grid, m_grid, G_grid, levels=[0], colors='cyan', linewidths=2)
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('log₁₀(G)', color='white')
        cbar.ax.tick_params(colors='white')
        
        # Panel 3: phi-Spiral
        ax3 = fig.add_subplot(gs[1, 0], facecolor='#1a1a2e', projection='polar')
        ax3.set_title('phi-Spiral with Segments', color='white', fontweight='bold', pad=20)
        ax3.tick_params(colors='white')
        
        theta_vals = np.linspace(0, 2*PI, 500)
        r_vals = [ssz_radius(t) for t in theta_vals]
        sigma_vals = [segment_density(t) for t in theta_vals]
        
        colors = plt.cm.plasma(np.array(sigma_vals) / max(sigma_vals))
        for i in range(len(theta_vals)-1):
            ax3.plot(theta_vals[i:i+2], r_vals[i:i+2], color=colors[i], linewidth=2)
        
        theta_k_list = [2 * PI * k / params['K_segments'] for k in range(params['K_segments'])]
        r_k_list = [ssz_radius(t) for t in theta_k_list]
        ax3.plot(theta_k_list, r_k_list, 'co', markersize=4)
        
        # Panel 4: Segment density
        ax4 = fig.add_subplot(gs[1, 1], facecolor='#1a1a2e')
        ax4.set_title('Segment Density σ(θ)', color='white', fontweight='bold')
        ax4.set_xlabel('θ', color='white')
        ax4.set_ylabel('σ', color='white')
        ax4.tick_params(colors='white')
        ax4.grid(True, alpha=0.2, color='white')
        
        theta_plot = np.linspace(0, 2*PI, 200)
        sigma_plot = [segment_density(t) for t in theta_plot]
        ax4.plot(theta_plot, sigma_plot, 'cyan', linewidth=2)
        ax4.axhline(PHI, color='magenta', linestyle='--', alpha=0.5)
        
        # Panel 5: Info
        ax5 = fig.add_subplot(gs[1, 2], facecolor='#1a1a2e')
        ax5.axis('off')
        
        info_text = (
            f"SELECTED CONFIG:\n"
            f"{'='*30}\n"
            f"lambda_A = {params['lambda_A']:.3f}\n"
            f"lambda_phi = {params['lambda_phi']:.3f}\n"
            f"K = {params['K_segments']}\n"
            f"Omega0 = {params['Omega0']:.2f}\n\n"
            f"CURRENT MODE:\n"
            f"{'='*30}\n"
            f"omega = {omega:.2f}\n"
            f"m = {m}\n"
            f"G = {G:.4f}\n"
            f"Status: {'UNSTABLE' if G > 1 else 'STABLE'}\n"
        )
        ax5.text(0.1, 0.9, info_text, fontsize=10, color='cyan',
                family='monospace', verticalalignment='top')
        
        plt.show()
    
    def export_spiral_animation(self, filename='d:/ssz_spiral_evolution.gif'):
        """Export animated phi-spiral evolution"""
        
        if self.selected_params is None:
            print("[ERROR] No parameters selected")
            return
        
        print(f"\nExporting spiral animation to {filename}...")
        
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), 
                              subplot_kw=dict(projection='polar'), 
                              facecolor='#0a0a1e')
        ax.set_facecolor('#1a1a2e')
        
        params = self.selected_params
        K = params['K_segments']
        
        def animate(frame):
            ax.clear()
            
            # Rotate segments
            theta_offset = frame * 2 * PI / 60
            
            theta_vals = np.linspace(0, 2*PI, 500)
            r_vals = [ssz_radius(t) for t in theta_vals]
            sigma_vals = [segment_density(t + theta_offset) for t in theta_vals]
            
            colors = plt.cm.plasma(np.array(sigma_vals) / max(sigma_vals))
            for i in range(len(theta_vals)-1):
                ax.plot(theta_vals[i:i+2], r_vals[i:i+2], color=colors[i], linewidth=2)
            
            theta_k_list = [(2 * PI * k / K + theta_offset) % (2*PI) for k in range(K)]
            r_k_list = [ssz_radius(t) for t in theta_k_list]
            ax.plot(theta_k_list, r_k_list, 'co', markersize=6, markeredgewidth=2)
            
            ax.set_title(f'phi-Spiral Evolution (K={K})\nlambda_A={params["lambda_A"]:.2f}, lambda_phi={params["lambda_phi"]:.2f}',
                        color='white', fontsize=12, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.2, color='white')
            ax.tick_params(colors='white')
        
        anim = animation.FuncAnimation(fig, animate, frames=60, interval=50)
        anim.save(filename, writer='pillow', fps=20, dpi=100)
        
        plt.close()
        print(f"[OK] Animation saved: {filename}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("SSZ RESONANCE EXPLORER")
    print("="*80)
    print("\nMeta-Visualization Tool combining:")
    print("  1. Parameter Scan")
    print("  2. Interactive Heatmap")
    print("  3. Click-to-Explore Live Visualizer")
    print("  4. Animated phi-Spiral Export")
    print("\n" + "="*80)
    
    explorer = ResonanceExplorer()
    
    print("\n[1/2] Running quick parameter scan...")
    explorer.run_scan()
    
    print("\n[2/2] Creating interactive heatmap...")
    print("\nINSTRUCTIONS:")
    print("  - Click on any heatmap point to explore that configuration")
    print("  - Live visualizer will open with selected parameters")
    print("  - Close visualizer window to return to heatmap")
    
    explorer.create_interactive_heatmap()
