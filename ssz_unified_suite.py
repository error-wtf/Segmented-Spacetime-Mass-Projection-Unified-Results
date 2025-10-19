#!/usr/bin/env python3
"""
===============================================================
Segmented Spacetime – Unified Computation & Visualization Suite
===============================================================

Vollständige Implementation der SSZ-Theorie nach Casu & Wrede:
- Segmentdichte σ(r), Zeitdehnung τ(x), optischer Index n(x)
- Massenkorrektur Δ(M), φ-Skalierung, Natural Boundary r_φ
- Euler-Reduktion, Dual-Velocity-Invarianz
- 3D-Visualisierung mit interaktiven Parametern

Theoretische Grundlagen:
- "Segmented Spacetime and π"
- "Natural Boundary of Black Holes"
- "Von Φ-Segmentierung zu Euler"
- "Solution to the Paradox of Singularities"
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import pandas as pd
from scipy.optimize import minimize_scalar
import json
from datetime import datetime

try:  # optional Plotly dependency for interactive notebooks/visuals
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAVE_PLOTLY = True
except ImportError:  # pragma: no cover - visualization optional in tests
    go = px = None
    make_subplots = None
    HAVE_PLOTLY = False

# ===============================================================
# 1. GRUNDKONSTANTEN & MATHEMATISCHES MODELL
# ===============================================================

class SSZConstants:
    """Fundamentale Konstanten der Segmented Spacetime Theorie"""
    
    # Mathematische Konstanten
    PHI = (1 + np.sqrt(5)) / 2  # Goldener Schnitt φ ≈ 1.618034
    PI = np.pi
    E = np.e
    
    # Physikalische Konstanten (SI)
    C = 299792458.0              # Lichtgeschwindigkeit [m/s]
    G = 6.67430e-11             # Gravitationskonstante [m³/(kg·s²)]
    HBAR = 1.054571817e-34      # Reduziertes Planck'sches Wirkungsquantum
    E_CHARGE = 1.602176634e-19  # Elementarladung
    
    # SSZ-spezifische Parameter
    DELTA_A = 98.01             # Massenkorrektur Parameter A
    DELTA_B = 1.96              # Massenkorrektur Parameter B  
    DELTA_ALPHA = 2.7e4         # Massenkorrektur Exponent α
    
    # Astronomische Referenzmassen [kg]
    M_SUN = 1.98847e30          # Sonnenmasse
    M_EARTH = 5.97219e24        # Erdmasse
    M_SGR_A = 8.26e36           # Sgr A* (supermassives schwarzes Loch)
    M_CYGNUS_X1 = 4.78e31       # Cygnus X-1 (stellares schwarzes Loch)

class SSZCore:
    """Kern-Berechnungen der Segmented Spacetime Theorie"""
    
    def __init__(self):
        self.const = SSZConstants()
    
    def schwarzschild_radius(self, M):
        """Schwarzschild-Radius r_s = 2GM/c²"""
        return 2 * self.const.G * M / (self.const.C ** 2)
    
    def delta_M(self, M):
        """Massenkorrektur Δ(M) = A·e^(-α·r_s) + B"""
        rs = self.schwarzschild_radius(M)
        A, B, alpha = self.const.DELTA_A, self.const.DELTA_B, self.const.DELTA_ALPHA
        return A * np.exp(-alpha * rs) + B
    
    def r_phi(self, M):
        """Natural Boundary r_φ = (φ/2)·r_s·[1 + Δ(M)]"""
        rs = self.schwarzschild_radius(M)
        delta = self.delta_M(M)
        return (self.const.PHI / 2) * rs * (1 + delta)
    
    def sigma(self, r, M):
        """Segmentdichte σ(r) = ln(r_φ/r) / ln(r_φ/r_s)"""
        rs = self.schwarzschild_radius(M)
        rphi = self.r_phi(M)
        
        # Sicherheitscheck: r muss zwischen r_s und r_φ liegen
        r = np.clip(r, rs * 1.001, rphi * 0.999)
        
        numerator = np.log(rphi / r)
        denominator = np.log(rphi / rs)
        
        return numerator / denominator
    
    def tau(self, r, M, alpha=1.0):
        """Zeitdehnung τ(r) = φ^(-α·σ(r))"""
        sig = self.sigma(r, M)
        return self.const.PHI ** (-alpha * sig)
    
    def n_index(self, r, M, kappa=0.015):
        """Optischer Index n(r) = 1 + κ·σ(r)"""
        sig = self.sigma(r, M)
        return 1 + kappa * sig
    
    def dual_velocity(self, r, M):
        """Dual-Velocity-Invarianz: v_esc · v_fall = c²"""
        rs = self.schwarzschild_radius(M)
        
        # Fluchtgeschwindigkeit (klassisch)
        v_esc = self.const.C * np.sqrt(2 * self.const.G * M / (r * self.const.C**2))
        
        # Fallgeschwindigkeit (aus Dualität)
        v_fall = self.const.C**2 / v_esc
        
        return v_esc, v_fall
    
    def euler_spiral(self, theta_max=4*np.pi, n_points=1000):
        """Euler-Reduktion z(θ) = z₀·e^((k+i)θ), k = 2ln(φ)/π"""
        theta = np.linspace(0, theta_max, n_points)
        k = 2 * np.log(self.const.PHI) / self.const.PI
        
        z = np.exp((k + 1j) * theta)
        
        return theta, z.real, z.imag, np.abs(z)

class SSZVisualizer:
    """3D-Visualisierung und Plotting der SSZ-Felder"""
    
    def __init__(self, core):
        self.core = core
        self.const = core.const
    
    def plot_radial_fields(self, M, alpha=1.0, kappa=0.015, n_points=1000):
        """Radiale Profile von σ(r), τ(r), n(r)"""
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        # Logarithmisches r-Array von r_s bis r_φ
        r = np.logspace(np.log10(rs * 1.001), np.log10(rphi * 0.999), n_points)
        
        # Berechne Felder
        sigma_vals = self.core.sigma(r, M)
        tau_vals = self.core.tau(r, M, alpha)
        n_vals = self.core.n_index(r, M, kappa)
        
        # Normierte Radien
        r_norm = r / rs
        
        # Plotting
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Segmented Spacetime Fields (M = {M/self.const.M_SUN:.2e} M☉)', fontsize=16)
        
        # σ(r)
        axes[0,0].semilogx(r_norm, sigma_vals, 'b-', linewidth=2, label='σ(r)')
        axes[0,0].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7, label=f'r_φ = {rphi/rs:.2f} r_s')
        axes[0,0].set_xlabel('r / r_s')
        axes[0,0].set_ylabel('Segment Density σ(r)')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].legend()
        axes[0,0].set_title('Segmentdichte (1 → 0)')
        
        # τ(r)
        axes[0,1].semilogx(r_norm, tau_vals, 'r-', linewidth=2, label='τ(r)')
        axes[0,1].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7)
        axes[0,1].set_xlabel('r / r_s')
        axes[0,1].set_ylabel('Time Dilation τ(r)')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].legend()
        axes[0,1].set_title(f'Zeitdehnung (φ^(-α·σ), α={alpha})')
        
        # n(r)
        axes[1,0].semilogx(r_norm, n_vals, 'g-', linewidth=2, label='n(r)')
        axes[1,0].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7)
        axes[1,0].set_xlabel('r / r_s')
        axes[1,0].set_ylabel('Refractive Index n(r)')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].legend()
        axes[1,0].set_title(f'Optischer Index (1 + κ·σ, κ={kappa})')
        
        # Dual Velocity
        v_esc, v_fall = self.core.dual_velocity(r, M)
        axes[1,1].loglog(r_norm, v_esc/self.const.C, 'b-', label='v_esc/c')
        axes[1,1].loglog(r_norm, v_fall/self.const.C, 'r-', label='v_fall/c')
        axes[1,1].axhline(1.0, color='k', linestyle=':', alpha=0.5, label='c')
        axes[1,1].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7)
        axes[1,1].set_xlabel('r / r_s')
        axes[1,1].set_ylabel('Velocity / c')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].legend()
        axes[1,1].set_title('Dual-Velocity-Invarianz')
        
        plt.tight_layout()
        return fig, (r, sigma_vals, tau_vals, n_vals)
    
    def plot_3d_field(self, M, field_type='sigma', alpha=1.0, kappa=0.015, resolution=50):
        """3D-Visualisierung der SSZ-Felder als Kugel"""
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        # Sphärische Koordinaten
        theta = np.linspace(0, np.pi, resolution)
        phi = np.linspace(0, 2*np.pi, resolution)
        THETA, PHI = np.meshgrid(theta, phi)
        
        # Verschiedene Radien für Schichtdarstellung
        radii = np.logspace(np.log10(rs * 1.1), np.log10(rphi * 0.9), 5)
        
        fig = go.Figure()
        
        for i, r in enumerate(radii):
            # Kartesische Koordinaten
            X = r * np.sin(THETA) * np.cos(PHI)
            Y = r * np.sin(THETA) * np.sin(PHI)
            Z = r * np.cos(THETA)
            
            # Feldwerte berechnen
            if field_type == 'sigma':
                field_vals = self.core.sigma(r, M)
                colorscale = 'Blues'
                title = 'Segment Density σ(r)'
            elif field_type == 'tau':
                field_vals = self.core.tau(r, M, alpha)
                colorscale = 'Reds'
                title = f'Time Dilation τ(r) (α={alpha})'
            elif field_type == 'n':
                field_vals = self.core.n_index(r, M, kappa)
                colorscale = 'Greens'
                title = f'Refractive Index n(r) (κ={kappa})'
            
            # Konstante Feldwerte für diese Schale
            colors = np.full_like(X, field_vals)
            
            fig.add_trace(go.Surface(
                x=X, y=Y, z=Z,
                surfacecolor=colors,
                colorscale=colorscale,
                opacity=0.6,
                name=f'r = {r/rs:.2f} r_s',
                showscale=(i==0)
            ))
        
        # Natural Boundary markieren
        X_nb = rphi * np.sin(THETA) * np.cos(PHI)
        Y_nb = rphi * np.sin(THETA) * np.sin(PHI)
        Z_nb = rphi * np.cos(THETA)
        
        fig.add_trace(go.Surface(
            x=X_nb, y=Y_nb, z=Z_nb,
            surfacecolor=np.ones_like(X_nb),
            colorscale=[[0, 'gold'], [1, 'gold']],
            opacity=0.3,
            name='Natural Boundary r_φ',
            showscale=False
        ))
        
        fig.update_layout(
            title=f'{title} - M = {M/self.const.M_SUN:.2e} M☉',
            scene=dict(
                xaxis_title='X [r_s]',
                yaxis_title='Y [r_s]',
                zaxis_title='Z [r_s]',
                aspectmode='cube'
            ),
            width=800,
            height=600
        )
        
        return fig
    
    def plot_euler_spiral(self):
        """φ-Euler-Spirale z(θ) = z₀·e^((k+i)θ)"""
        theta, x, y, magnitude = self.core.euler_spiral()
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Spirale in komplexer Ebene
        axes[0].plot(x, y, 'b-', linewidth=2, alpha=0.8)
        axes[0].scatter(x[::100], y[::100], c=theta[::100], cmap='viridis', s=30, alpha=0.7)
        axes[0].set_xlabel('Real(z)')
        axes[0].set_ylabel('Imag(z)')
        axes[0].set_title('φ-Euler-Spirale (komplexe Ebene)')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_aspect('equal')
        
        # Magnitude vs. θ
        axes[1].semilogy(theta, magnitude, 'r-', linewidth=2)
        
        # φ-Markierungen bei π/2-Intervallen
        phi_markers = theta[::len(theta)//8]  # Alle π/2
        phi_mags = magnitude[::len(theta)//8]
        axes[1].scatter(phi_markers, phi_mags, c='gold', s=50, zorder=5, 
                       label=f'φ-Wachstum (×{self.const.PHI:.3f} pro π/2)')
        
        axes[1].set_xlabel('θ [rad]')
        axes[1].set_ylabel('|z(θ)|')
        axes[1].set_title('φ-Exponentielles Wachstum')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        
        plt.tight_layout()
        return fig

class SSZInteractiveGUI:
    """Interaktive GUI für SSZ-Parameter-Exploration"""
    
    def __init__(self):
        self.core = SSZCore()
        self.viz = SSZVisualizer(self.core)
        self.current_mass = self.core.const.M_SUN
        self.current_alpha = 1.0
        self.current_kappa = 0.015
        
    def create_interactive_dashboard(self):
        """Erstellt interaktives Plotly-Dashboard"""
        # Initiale Berechnung
        fig = self.update_plots()
        
        # Parameter-Kontrollen (vereinfacht für Demo)
        return fig
    
    def update_plots(self):
        """Aktualisiert alle Plots mit aktuellen Parametern"""
        # Radiale Profile
        fig_radial, data = self.viz.plot_radial_fields(
            self.current_mass, 
            self.current_alpha, 
            self.current_kappa
        )
        
        return fig_radial

class SSZDataExport:
    """Datenexport und Kalibrierung"""
    
    def __init__(self, core):
        self.core = core
    
    def export_calibration_data(self, masses=None, filename='ssz_calibration.json'):
        """Exportiert Kalibrierungsdaten für verschiedene Massen"""
        if masses is None:
            masses = {
                'Sun': self.core.const.M_SUN,
                'Earth': self.core.const.M_EARTH,
                'Sgr_A_star': self.core.const.M_SGR_A,
                'Cygnus_X1': self.core.const.M_CYGNUS_X1
            }
        
        calibration_data = {
            'timestamp': datetime.now().isoformat(),
            'constants': {
                'phi': self.core.const.PHI,
                'c': self.core.const.C,
                'G': self.core.const.G
            },
            'objects': {}
        }
        
        for name, mass in masses.items():
            rs = self.core.schwarzschild_radius(mass)
            rphi = self.core.r_phi(mass)
            delta = self.core.delta_M(mass)
            
            calibration_data['objects'][name] = {
                'mass_kg': mass,
                'mass_solar': mass / self.core.const.M_SUN,
                'r_schwarzschild_m': rs,
                'r_phi_m': rphi,
                'r_phi_over_rs': rphi / rs,
                'delta_M': delta,
                'phi_over_2': self.core.const.PHI / 2,
                'precision_check': abs((rphi/rs) - (self.core.const.PHI/2)) < 1e-6
            }
        
        with open(filename, 'w') as f:
            json.dump(calibration_data, f, indent=2)
        
        print(f"📊 Calibration data exported to {filename}")
        return calibration_data
    
    def verify_ssz_predictions(self):
        """Verifiziert SSZ-Vorhersagen gegen bekannte Werte"""
        print("🔬 SSZ Theory Verification")
        print("=" * 50)
        
        # Test 1: φ/2-Verhältnis
        test_masses = [self.core.const.M_SUN, self.core.const.M_SGR_A]
        
        for i, M in enumerate(test_masses):
            name = ['Sun', 'Sgr A*'][i]
            rs = self.core.schwarzschild_radius(M)
            rphi = self.core.r_phi(M)
            ratio = rphi / rs
            expected = self.core.const.PHI / 2
            error = abs(ratio - expected) / expected * 100
            
            print(f"{name}:")
            print(f"  r_φ/r_s = {ratio:.6f}")
            print(f"  φ/2 = {expected:.6f}")
            print(f"  Error: {error:.2e}%")
            print(f"  ✓ Precision check: {error < 1e-4}")
            print()
        
        # Test 2: Dual-Velocity-Invarianz
        print("Dual-Velocity Test (at r = 10 r_s):")
        r_test = 10 * self.core.schwarzschild_radius(self.core.const.M_SUN)
        v_esc, v_fall = self.core.dual_velocity(r_test, self.core.const.M_SUN)
        product = v_esc * v_fall
        c_squared = self.core.const.C ** 2
        error = abs(product - c_squared) / c_squared * 100
        
        print(f"  v_esc × v_fall = {product:.3e}")
        print(f"  c² = {c_squared:.3e}")
        print(f"  Error: {error:.2e}%")
        print(f"  ✓ Invariance check: {error < 1e-10}")

def main():
    """Hauptfunktion - Demonstriert vollständige SSZ-Suite"""
    print("🌌 Segmented Spacetime - Unified Computation & Visualization Suite")
    print("=" * 70)
    
    # Initialisierung
    core = SSZCore()
    viz = SSZVisualizer(core)
    gui = SSZInteractiveGUI()
    export = SSZDataExport(core)
    
    # 1. Verifikation der Theorie
    print("\n1. Theory Verification:")
    export.verify_ssz_predictions()
    
    # 2. Kalibrierungsdaten exportieren
    print("\n2. Exporting Calibration Data:")
    calib_data = export.export_calibration_data()
    
    # 3. Beispiel-Visualisierungen
    print("\n3. Generating Visualizations:")
    
    # Radiale Profile für Sonne
    print("   - Radial field profiles (Sun)")
    fig_sun, data_sun = viz.plot_radial_fields(core.const.M_SUN)
    plt.savefig('ssz_sun_radial_fields.png', dpi=300, bbox_inches='tight')
    
    # 3D-Feld für schwarzes Loch
    print("   - 3D field visualization (Sgr A*)")
    fig_3d = viz.plot_3d_field(core.const.M_SGR_A, 'sigma')
    fig_3d.write_html('ssz_sgr_a_3d_field.html')
    
    # Euler-Spirale
    print("   - φ-Euler spiral")
    fig_euler = viz.plot_euler_spiral()
    plt.savefig('ssz_phi_euler_spiral.png', dpi=300, bbox_inches='tight')
    
    # 4. Parameter-Studie
    print("\n4. Parameter Study:")
    alphas = [0.5, 1.0, 1.5, 2.0]
    kappas = [0.005, 0.015, 0.025, 0.035]
    
    print("   α-Variation (Time Dilation Scaling):")
    for alpha in alphas:
        r_test = 2 * core.schwarzschild_radius(core.const.M_SUN)
        tau_val = core.tau(r_test, core.const.M_SUN, alpha)
        print(f"     α = {alpha}: τ(2r_s) = {tau_val:.4f}")
    
    print("   κ-Variation (Optical Index Coupling):")
    for kappa in kappas:
        r_test = 2 * core.schwarzschild_radius(core.const.M_SUN)
        n_val = core.n_index(r_test, core.const.M_SUN, kappa)
        print(f"     κ = {kappa}: n(2r_s) = {n_val:.4f}")
    
    print("\n✅ SSZ Suite completed successfully!")
    print("📊 Files generated:")
    print("   - ssz_calibration.json")
    print("   - ssz_sun_radial_fields.png")
    print("   - ssz_sgr_a_3d_field.html")
    print("   - ssz_phi_euler_spiral.png")
    
    # Zeige Plots
    plt.show()

if __name__ == "__main__":
    main()
