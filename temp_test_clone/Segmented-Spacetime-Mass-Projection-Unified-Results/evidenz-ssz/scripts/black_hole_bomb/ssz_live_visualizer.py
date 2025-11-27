#!/usr/bin/env python3
"""
SSZ Black-Hole-Bomb: Interactive Live Visualizer
================================================
Dynamic exploration of φ-based segmentation effects on superradiance.

Features:
- Interactive sliders for ω, m, λ_A, λ_φ, K
- Real-time instability heatmap updates
- Amplitude curve visualization
- φ-spiral geometry overlay with segment markers

Perfect-Pair Mathematics Style (Casu & Wrede 2025)
© 2025 Carmen Wrede, Lino Casu
"""
import math, sys, os
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.widgets import Slider, Button
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[ERROR] matplotlib required")
    sys.exit(1)

PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

# ============================================================================
# CORE PHYSICS (reused from complete implementation)
# ============================================================================

def ssz_radius(theta, r0=1.0, phi=PHI):
    return r0 * (phi ** (theta / (PI / 2)))

def segment_density(theta, sigma0, phi=PHI):
    return sigma0 * (phi ** (theta / (PI / 2)))

def Omega_profile(theta, Omega0, epsilon=0.1, q=2):
    return Omega0 * (1 + epsilon * math.cos(q * theta))

def gamma_loc(theta, omega, m, Omega0, epsilon=0.1, q=2, alpha=0.8, eta=0.05):
    omega_co = omega - m * Omega_profile(theta, Omega0, epsilon, q)
    return alpha * max(0.0, -omega_co) - eta

def compute_G_for_mode(omega, m, lambda_A, lambda_phi, K_segments, Omega0, M_theta=512):
    """Fast computation of average gain G for given parameters"""
    
    # Parameters
    r0, phi_g, sigma0 = 1.0, PHI, 1.0
    alpha, eta = 0.8, 0.05
    R, K_coupling = 0.98, 0.02
    epsilon, q = 0.1, 2
    
    d_theta = 2 * PI / M_theta
    theta_k_list = [2 * PI * k / K_segments for k in range(K_segments)]
    
    # Integrate local gain
    integral_gamma = 0.0
    for i in range(M_theta):
        theta = d_theta * i
        r_theta = ssz_radius(theta, r0, phi_g)
        ds = r_theta * d_theta
        gamma_theta = gamma_loc(theta, omega, m, Omega0, epsilon, q, alpha, eta)
        integral_gamma += gamma_theta * ds
    
    # SSZ transitions
    log_T_A_sum = 0.0
    for theta_k in theta_k_list:
        sigma_k = segment_density(theta_k, sigma0, phi_g)
        log_T_A_sum += -lambda_A * sigma_k
    
    # Total gain
    G = math.exp(integral_gamma + log_T_A_sum) * R * (1 - K_coupling)
    return G

def compute_amplitude_curve(omega, m, lambda_A, lambda_phi, K_segments, Omega0, N_max=50):
    """Compute amplitude evolution over roundtrips"""
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
# INTERACTIVE VISUALIZER
# ============================================================================

class SSZLiveVisualizer:
    def __init__(self):
        self.fig = plt.figure(figsize=(16, 9), facecolor='#0a0a1e')
        self.gs = gridspec.GridSpec(3, 3, figure=self.fig, hspace=0.35, wspace=0.35,
                                    left=0.05, right=0.95, top=0.93, bottom=0.12)
        
        # Initial parameters
        self.omega = 0.25
        self.m = 2
        self.lambda_A = 0.02
        self.lambda_phi = 0.03
        self.K_segments = 32
        self.Omega0 = 0.3
        
        # Setup plots
        self.setup_plots()
        self.setup_sliders()
        self.update_all()
        
    def setup_plots(self):
        """Create all plot panels"""
        
        # Panel 1: Amplitude Evolution (top left, spans 2 rows)
        self.ax_amp = self.fig.add_subplot(self.gs[:2, 0], facecolor='#1a1a2e')
        self.ax_amp.set_title('Amplitude Evolution', color='white', fontsize=12, fontweight='bold')
        self.ax_amp.set_xlabel('Roundtrip', color='white', fontsize=10)
        self.ax_amp.set_ylabel('Amplitude (log)', color='white', fontsize=10)
        self.ax_amp.set_yscale('log')
        self.ax_amp.grid(True, alpha=0.2, color='white')
        self.ax_amp.tick_params(colors='white')
        self.line_amp, = self.ax_amp.plot([], [], 'cyan', linewidth=2)
        self.ax_amp.axhline(1, color='red', linestyle='--', alpha=0.5)
        self.ax_amp.axhline(10, color='orange', linestyle='--', alpha=0.5)
        
        # Panel 2: Instability Map (top right, spans 2 rows)
        self.ax_map = self.fig.add_subplot(self.gs[:2, 1:], facecolor='#1a1a2e')
        self.ax_map.set_title('Instability Map (ω vs m)', color='white', fontsize=12, fontweight='bold')
        self.ax_map.set_xlabel('ω', color='white', fontsize=10)
        self.ax_map.set_ylabel('m', color='white', fontsize=10)
        self.ax_map.tick_params(colors='white')
        
        # Panel 3: φ-Spiral (bottom left)
        self.ax_spiral = self.fig.add_subplot(self.gs[2, 0], facecolor='#1a1a2e', projection='polar')
        self.ax_spiral.set_title('φ-Spiral Geometry', color='white', fontsize=12, fontweight='bold', pad=20)
        self.ax_spiral.tick_params(colors='white')
        self.ax_spiral.grid(True, alpha=0.2, color='white')
        
        # Panel 4: Segment Density (bottom middle)
        self.ax_sigma = self.fig.add_subplot(self.gs[2, 1], facecolor='#1a1a2e')
        self.ax_sigma.set_title('Segment Density σ(θ)', color='white', fontsize=12, fontweight='bold')
        self.ax_sigma.set_xlabel('θ', color='white', fontsize=10)
        self.ax_sigma.set_ylabel('σ', color='white', fontsize=10)
        self.ax_sigma.tick_params(colors='white')
        self.ax_sigma.grid(True, alpha=0.2, color='white')
        
        # Panel 5: Info Box (bottom right)
        self.ax_info = self.fig.add_subplot(self.gs[2, 2], facecolor='#1a1a2e')
        self.ax_info.axis('off')
        self.text_info = self.ax_info.text(0.1, 0.9, '', fontsize=10, color='cyan',
                                          family='monospace', verticalalignment='top')
        
    def setup_sliders(self):
        """Create interactive sliders"""
        slider_color = 'lightgray'
        
        # Slider axes (bottom of figure)
        ax_omega = plt.axes([0.1, 0.06, 0.15, 0.02], facecolor=slider_color)
        ax_m = plt.axes([0.3, 0.06, 0.15, 0.02], facecolor=slider_color)
        ax_lambda_A = plt.axes([0.5, 0.06, 0.15, 0.02], facecolor=slider_color)
        ax_lambda_phi = plt.axes([0.7, 0.06, 0.15, 0.02], facecolor=slider_color)
        ax_K = plt.axes([0.1, 0.03, 0.15, 0.02], facecolor=slider_color)
        ax_Omega0 = plt.axes([0.3, 0.03, 0.15, 0.02], facecolor=slider_color)
        
        # Create sliders
        self.slider_omega = Slider(ax_omega, 'ω', 0.05, 0.40, valinit=self.omega, valstep=0.05, color='cyan')
        self.slider_m = Slider(ax_m, 'm', 1, 5, valinit=self.m, valstep=1, color='magenta')
        self.slider_lambda_A = Slider(ax_lambda_A, 'λ_A', 0.0, 0.05, valinit=self.lambda_A, valstep=0.01, color='yellow')
        self.slider_lambda_phi = Slider(ax_lambda_phi, 'λ_φ', 0.0, 0.05, valinit=self.lambda_phi, valstep=0.01, color='orange')
        self.slider_K = Slider(ax_K, 'K', 8, 64, valinit=self.K_segments, valstep=8, color='green')
        self.slider_Omega0 = Slider(ax_Omega0, 'Ω₀', 0.1, 0.5, valinit=self.Omega0, valstep=0.05, color='red')
        
        # Connect sliders to update function
        self.slider_omega.on_changed(self.on_param_change)
        self.slider_m.on_changed(self.on_param_change)
        self.slider_lambda_A.on_changed(self.on_param_change)
        self.slider_lambda_phi.on_changed(self.on_param_change)
        self.slider_K.on_changed(self.on_param_change)
        self.slider_Omega0.on_changed(self.on_param_change)
        
    def on_param_change(self, val):
        """Called when any slider changes"""
        self.omega = self.slider_omega.val
        self.m = int(self.slider_m.val)
        self.lambda_A = self.slider_lambda_A.val
        self.lambda_phi = self.slider_lambda_phi.val
        self.K_segments = int(self.slider_K.val)
        self.Omega0 = self.slider_Omega0.val
        self.update_all()
        
    def update_all(self):
        """Update all plots with current parameters"""
        
        # Update amplitude curve
        A_history, G = compute_amplitude_curve(self.omega, self.m, self.lambda_A,
                                               self.lambda_phi, self.K_segments, self.Omega0)
        rounds = list(range(len(A_history)))
        self.line_amp.set_data(rounds, A_history)
        self.ax_amp.set_xlim(0, max(len(rounds), 10))
        self.ax_amp.set_ylim(0.5, max(max(A_history)*2, 10))
        
        # Update instability map
        self.ax_map.clear()
        omega_grid = np.linspace(0.05, 0.40, 20)
        m_grid = [1, 2, 3, 4, 5]
        G_grid = np.zeros((len(m_grid), len(omega_grid)))
        
        for i, m_val in enumerate(m_grid):
            for j, omega_val in enumerate(omega_grid):
                G_val = compute_G_for_mode(omega_val, m_val, self.lambda_A,
                                           self.lambda_phi, self.K_segments, self.Omega0)
                G_grid[i, j] = math.log10(G_val) if G_val > 0 else -6
        
        im = self.ax_map.imshow(G_grid, aspect='auto', origin='lower', cmap='hot',
                               extent=[omega_grid[0], omega_grid[-1], m_grid[0]-0.5, m_grid[-1]+0.5])
        self.ax_map.contour(omega_grid, m_grid, G_grid, levels=[0], colors='cyan', linewidths=2)
        self.ax_map.plot(self.omega, self.m, 'wo', markersize=10, markeredgewidth=2)
        self.ax_map.set_title('Instability Map (ω vs m)', color='white', fontsize=12, fontweight='bold')
        self.ax_map.set_xlabel('ω', color='white', fontsize=10)
        self.ax_map.set_ylabel('m', color='white', fontsize=10)
        self.ax_map.tick_params(colors='white')
        
        # Update φ-spiral
        self.ax_spiral.clear()
        theta_vals = np.linspace(0, 2*PI, 500)
        r_vals = [ssz_radius(t) for t in theta_vals]
        sigma_vals = [segment_density(t, 1.0) for t in theta_vals]
        
        # Color by segment density
        colors = plt.cm.plasma(np.array(sigma_vals) / max(sigma_vals))
        for i in range(len(theta_vals)-1):
            self.ax_spiral.plot(theta_vals[i:i+2], r_vals[i:i+2], color=colors[i], linewidth=2)
        
        # Mark segment boundaries
        theta_k_list = [2 * PI * k / self.K_segments for k in range(self.K_segments)]
        r_k_list = [ssz_radius(t) for t in theta_k_list]
        self.ax_spiral.plot(theta_k_list, r_k_list, 'co', markersize=4)
        
        self.ax_spiral.set_title('φ-Spiral Geometry', color='white', fontsize=12, fontweight='bold', pad=20)
        self.ax_spiral.grid(True, alpha=0.2, color='white')
        self.ax_spiral.tick_params(colors='white')
        
        # Update segment density plot
        self.ax_sigma.clear()
        theta_plot = np.linspace(0, 2*PI, 200)
        sigma_plot = [segment_density(t, 1.0) for t in theta_plot]
        self.ax_sigma.plot(theta_plot, sigma_plot, 'cyan', linewidth=2)
        self.ax_sigma.axhline(PHI, color='magenta', linestyle='--', alpha=0.5, label=f'φ={PHI:.3f}')
        self.ax_sigma.axhline(PHI**2, color='yellow', linestyle='--', alpha=0.5, label=f'φ²={PHI**2:.3f}')
        self.ax_sigma.set_title('Segment Density σ(θ)', color='white', fontsize=12, fontweight='bold')
        self.ax_sigma.set_xlabel('θ', color='white', fontsize=10)
        self.ax_sigma.set_ylabel('σ', color='white', fontsize=10)
        self.ax_sigma.tick_params(colors='white')
        self.ax_sigma.legend(fontsize=8, facecolor='black', edgecolor='white', labelcolor='white')
        self.ax_sigma.grid(True, alpha=0.2, color='white')
        
        # Update info text
        unstable = "UNSTABLE" if G > 1.0 else "STABLE"
        info_text = (
            f"CURRENT MODE:\n"
            f"{'='*25}\n"
            f"ω = {self.omega:.2f}\n"
            f"m = {self.m}\n"
            f"λ_A = {self.lambda_A:.3f}\n"
            f"λ_φ = {self.lambda_phi:.3f}\n"
            f"K = {self.K_segments}\n"
            f"Ω₀ = {self.Omega0:.2f}\n\n"
            f"RESULTS:\n"
            f"{'='*25}\n"
            f"G_avg = {G:.4f}\n"
            f"Status: {unstable}\n"
            f"Rounds: {len(rounds)}\n"
            f"Final A: {A_history[-1]:.2e}\n"
        )
        self.text_info.set_text(info_text)
        
        plt.draw()
    
    def run(self):
        """Start interactive session"""
        plt.show()
    
    def save_frame(self, filename='d:/ssz_live_frame.png'):
        """Export current frame"""
        self.fig.savefig(filename, dpi=150, facecolor='#0a0a1e', bbox_inches='tight')
        print(f"[OK] Frame saved: {filename}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("SSZ LIVE VISUALIZER - Interactive Exploration")
    print("="*80)
    print("\nControls:")
    print("  - Use sliders to adjust parameters in real-time")
    print("  - White dot on instability map shows current (ω, m)")
    print("  - Cyan dots on spiral mark segment boundaries")
    print("\nStarting...")
    
    viz = SSZLiveVisualizer()
    
    # Save initial frame
    viz.save_frame()
    
    # Start interactive session
    viz.run()
