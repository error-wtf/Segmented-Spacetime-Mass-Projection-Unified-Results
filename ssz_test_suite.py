#!/usr/bin/env python3
"""
===============================================================
SSZ Test Suite - Comprehensive Theory Verification
===============================================================

Umfassende Test-Suite für die Segmented Spacetime Theorie:
- Mathematische Konsistenz-Tests
- Physikalische Grenzwert-Tests  
- Numerische Präzisions-Tests
- Vergleich mit bekannten Werten
- Performance-Benchmarks
"""

import numpy as np
import pytest
import time
from ssz_unified_suite import SSZCore, SSZConstants
import matplotlib.pyplot as plt

class TestSSZMathematicalConsistency:
    """Tests für mathematische Konsistenz der SSZ-Formeln"""
    
    def setup_method(self):
        """Setup für jeden Test"""
        self.core = SSZCore()
        self.const = SSZConstants()
        
    def test_phi_precision(self):
        """Test: φ = (1+√5)/2 mit hoher Präzision"""
        calculated_phi = (1 + np.sqrt(5)) / 2
        assert abs(self.const.PHI - calculated_phi) < 1e-15
        assert abs(self.const.PHI - 1.618033988749895) < 1e-15
        
    def test_schwarzschild_radius_scaling(self):
        """Test: r_s skaliert linear mit Masse"""
        masses = [self.const.M_SUN, 2*self.const.M_SUN, 10*self.const.M_SUN]
        rs_values = [self.core.schwarzschild_radius(M) for M in masses]
        
        # Verhältnisse prüfen
        assert abs(rs_values[1] / rs_values[0] - 2.0) < 1e-10
        assert abs(rs_values[2] / rs_values[0] - 10.0) < 1e-10
        
    def test_natural_boundary_ratio(self):
        """Test: r_φ/r_s ≈ φ/2 für verschiedene Massen"""
        test_masses = [
            self.const.M_SUN,
            self.const.M_SGR_A,
            self.const.M_CYGNUS_X1,
            1e20  # Kleine Masse
        ]
        
        expected_ratio = self.const.PHI / 2
        
        for M in test_masses:
            rs = self.core.schwarzschild_radius(M)
            rphi = self.core.r_phi(M)
            ratio = rphi / rs
            
            # Relative Abweichung sollte klein sein
            relative_error = abs(ratio - expected_ratio) / expected_ratio
            assert relative_error < 0.1, f"Mass {M}: ratio={ratio:.6f}, expected={expected_ratio:.6f}"
            
    def test_sigma_boundary_conditions(self):
        """Test: σ(r_s) = 1, σ(r_φ) = 0"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        # σ(r_s) sollte 1 sein (mit kleiner Toleranz wegen numerischer Stabilität)
        sigma_rs = self.core.sigma(rs * 1.001, M)  # Leicht über r_s
        assert abs(sigma_rs - 1.0) < 0.01
        
        # σ(r_φ) sollte 0 sein
        sigma_rphi = self.core.sigma(rphi * 0.999, M)  # Leicht unter r_φ
        assert abs(sigma_rphi - 0.0) < 0.01
        
    def test_sigma_monotonicity(self):
        """Test: σ(r) ist monoton fallend"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        r_values = np.logspace(np.log10(rs * 1.01), np.log10(rphi * 0.99), 100)
        sigma_values = [self.core.sigma(r, M) for r in r_values]
        
        # Prüfe, dass σ monoton fällt
        for i in range(1, len(sigma_values)):
            assert sigma_values[i] <= sigma_values[i-1], f"σ not monotonic at index {i}"
            
    def test_tau_phi_scaling(self):
        """Test: τ(r) = φ^(-α·σ(r))"""
        M = self.const.M_SUN
        r_test = 2 * self.core.schwarzschild_radius(M)
        alpha = 1.5
        
        sigma_val = self.core.sigma(r_test, M)
        tau_calculated = self.const.PHI ** (-alpha * sigma_val)
        tau_function = self.core.tau(r_test, M, alpha)
        
        assert abs(tau_calculated - tau_function) < 1e-12
        
    def test_n_index_linearity(self):
        """Test: n(r) = 1 + κ·σ(r)"""
        M = self.const.M_SUN
        r_test = 3 * self.core.schwarzschild_radius(M)
        kappa = 0.025
        
        sigma_val = self.core.sigma(r_test, M)
        n_calculated = 1 + kappa * sigma_val
        n_function = self.core.n_index(r_test, M, kappa)
        
        assert abs(n_calculated - n_function) < 1e-12

class TestSSZPhysicalLimits:
    """Tests für physikalische Grenzwerte und Plausibilität"""
    
    def setup_method(self):
        self.core = SSZCore()
        self.const = SSZConstants()
        
    def test_no_singularities(self):
        """Test: Keine Singularitäten in σ, τ, n"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        # Test-Radien nahe den Grenzen
        r_values = [rs * 1.0001, rs * 1.1, rphi * 0.9, rphi * 0.9999]
        
        for r in r_values:
            sigma = self.core.sigma(r, M)
            tau = self.core.tau(r, M, 1.0)
            n = self.core.n_index(r, M, 0.015)
            
            # Alle Werte sollten endlich und positiv sein
            assert np.isfinite(sigma), f"σ not finite at r={r}"
            assert np.isfinite(tau), f"τ not finite at r={r}"
            assert np.isfinite(n), f"n not finite at r={r}"
            
            assert sigma >= 0, f"σ negative at r={r}"
            assert tau > 0, f"τ non-positive at r={r}"
            assert n >= 1, f"n < 1 at r={r}"
            
    def test_dual_velocity_invariance(self):
        """Test: v_esc · v_fall = c²"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        
        # Test bei verschiedenen Radien
        r_values = [2*rs, 5*rs, 10*rs, 100*rs]
        
        for r in r_values:
            v_esc, v_fall = self.core.dual_velocity(r, M)
            product = v_esc * v_fall
            c_squared = self.const.C ** 2
            
            relative_error = abs(product - c_squared) / c_squared
            assert relative_error < 1e-10, f"Dual velocity invariance violated at r={r/rs:.1f}r_s"
            
    def test_time_dilation_limits(self):
        """Test: τ(r) Grenzwerte"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        alpha = 1.0
        
        # Bei r_s: τ ≈ φ^(-α)
        tau_rs = self.core.tau(rs * 1.01, M, alpha)
        expected_tau_rs = self.const.PHI ** (-alpha)
        assert abs(tau_rs - expected_tau_rs) < 0.1
        
        # Bei r_φ: τ ≈ 1
        tau_rphi = self.core.tau(rphi * 0.99, M, alpha)
        assert abs(tau_rphi - 1.0) < 0.1
        
        # τ sollte immer ≤ 1 sein
        r_test = np.logspace(np.log10(rs * 1.01), np.log10(rphi * 0.99), 50)
        for r in r_test:
            tau = self.core.tau(r, M, alpha)
            assert tau <= 1.0, f"τ > 1 at r={r}"

class TestSSZNumericalPrecision:
    """Tests für numerische Präzision und Stabilität"""
    
    def setup_method(self):
        self.core = SSZCore()
        self.const = SSZConstants()
        
    def test_mass_range_stability(self):
        """Test: Stabilität über große Massenbereiche"""
        # Massen von Elementarteilchen bis supermassive schwarze Löcher
        masses = np.logspace(10, 40, 10)  # 10^10 bis 10^40 kg
        
        for M in masses:
            try:
                rs = self.core.schwarzschild_radius(M)
                rphi = self.core.r_phi(M)
                delta = self.core.delta_M(M)
                
                # Grundlegende Plausibilitätschecks
                assert rs > 0, f"Negative r_s for M={M}"
                assert rphi > rs, f"r_φ ≤ r_s for M={M}"
                assert np.isfinite(delta), f"Non-finite Δ(M) for M={M}"
                
            except (OverflowError, ZeroDivisionError) as e:
                pytest.fail(f"Numerical instability at M={M}: {e}")
                
    def test_logarithmic_precision(self):
        """Test: Präzision der logarithmischen Berechnungen"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        # Test nahe den Grenzen
        r_close_to_rs = rs * (1 + 1e-10)
        r_close_to_rphi = rphi * (1 - 1e-10)
        
        sigma_rs = self.core.sigma(r_close_to_rs, M)
        sigma_rphi = self.core.sigma(r_close_to_rphi, M)
        
        # Sollte nahe den erwarteten Werten sein
        assert abs(sigma_rs - 1.0) < 1e-8
        assert abs(sigma_rphi - 0.0) < 1e-8
        
    def test_parameter_sensitivity(self):
        """Test: Sensitivität gegenüber Parameter-Änderungen"""
        M = self.const.M_SUN
        r_test = 2 * self.core.schwarzschild_radius(M)
        
        # Alpha-Sensitivität
        alpha_base = 1.0
        alpha_perturb = 1.0 + 1e-6
        
        tau_base = self.core.tau(r_test, M, alpha_base)
        tau_perturb = self.core.tau(r_test, M, alpha_perturb)
        
        # Kleine Änderung sollte kleine Auswirkung haben
        relative_change = abs(tau_perturb - tau_base) / tau_base
        assert relative_change < 1e-4, "Excessive sensitivity to α changes"

class TestSSZPerformance:
    """Performance-Tests für SSZ-Berechnungen"""
    
    def setup_method(self):
        self.core = SSZCore()
        self.const = SSZConstants()
        
    def test_single_calculation_speed(self):
        """Test: Geschwindigkeit einzelner Berechnungen"""
        M = self.const.M_SUN
        r = 2 * self.core.schwarzschild_radius(M)
        
        # Zeitmessung für verschiedene Funktionen
        functions = [
            ('schwarzschild_radius', lambda: self.core.schwarzschild_radius(M)),
            ('r_phi', lambda: self.core.r_phi(M)),
            ('sigma', lambda: self.core.sigma(r, M)),
            ('tau', lambda: self.core.tau(r, M, 1.0)),
            ('n_index', lambda: self.core.n_index(r, M, 0.015))
        ]
        
        for name, func in functions:
            start_time = time.time()
            for _ in range(1000):
                result = func()
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 1000
            assert avg_time < 1e-4, f"{name} too slow: {avg_time:.2e} s per call"
            
    def test_vectorized_calculations(self):
        """Test: Vektorisierte Berechnungen"""
        M = self.const.M_SUN
        rs = self.core.schwarzschild_radius(M)
        rphi = self.core.r_phi(M)
        
        # Große Arrays
        r_array = np.logspace(np.log10(rs * 1.01), np.log10(rphi * 0.99), 10000)
        
        start_time = time.time()
        sigma_array = np.array([self.core.sigma(r, M) for r in r_array])
        end_time = time.time()
        
        total_time = end_time - start_time
        assert total_time < 1.0, f"Vectorized calculation too slow: {total_time:.2f} s"
        assert len(sigma_array) == len(r_array)

class TestSSZKnownValues:
    """Tests gegen bekannte/erwartete Werte"""
    
    def setup_method(self):
        self.core = SSZCore()
        self.const = SSZConstants()
        
    def test_solar_mass_values(self):
        """Test: Bekannte Werte für Sonnenmasse"""
        M = self.const.M_SUN
        
        # Schwarzschild-Radius der Sonne
        rs = self.core.schwarzschild_radius(M)
        expected_rs = 2953.25  # Meter (bekannter Wert)
        
        relative_error = abs(rs - expected_rs) / expected_rs
        assert relative_error < 1e-4, f"Solar r_s error: {relative_error:.2e}"
        
    def test_sgr_a_star_values(self):
        """Test: Werte für Sgr A*"""
        M = self.const.M_SGR_A
        rs = self.core.schwarzschild_radius(M)
        
        # Sgr A* Schwarzschild-Radius sollte ~24 Millionen km sein
        expected_rs_range = (2e10, 3e10)  # Meter
        assert expected_rs_range[0] < rs < expected_rs_range[1]
        
    def test_phi_mathematical_properties(self):
        """Test: Mathematische Eigenschaften von φ"""
        phi = self.const.PHI
        
        # φ² = φ + 1
        assert abs(phi**2 - (phi + 1)) < 1e-14
        
        # 1/φ = φ - 1
        assert abs(1/phi - (phi - 1)) < 1e-14
        
        # φ = (1 + √5)/2
        assert abs(phi - (1 + np.sqrt(5))/2) < 1e-14

def run_comprehensive_test_suite():
    """Führt alle Tests aus und erstellt Bericht"""
    print("== SSZ Comprehensive Test Suite ==")
    print("=" * 50)
    
    # Test-Klassen
    test_classes = [
        TestSSZMathematicalConsistency,
        TestSSZPhysicalLimits,
        TestSSZNumericalPrecision,
        TestSSZPerformance,
        TestSSZKnownValues
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        
        # Instanz erstellen
        test_instance = test_class()
        test_instance.setup_method()
        
        # Alle Test-Methoden finden
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"  [PASS] {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  [FAIL] {method_name}: {str(e)}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
    
    # Zusammenfassung
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests:
        print("\nFailed Tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  {class_name}.{method_name}: {error}")
    else:
        print("\nAll tests passed!")
    
    return passed_tests == total_tests

def create_test_report():
    """Erstellt detaillierten Test-Bericht mit Plots"""
    core = SSZCore()
    const = SSZConstants()
    
    # Test verschiedene Massen
    test_masses = {
        'Proton': 1.67e-27,
        'Earth': const.M_EARTH,
        'Sun': const.M_SUN,
        'Sgr A*': const.M_SGR_A
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('SSZ Theory Test Report', fontsize=16)
    
    # Plot 1: r_φ/r_s vs Masse
    masses = list(test_masses.values())
    ratios = []
    
    for M in masses:
        rs = core.schwarzschild_radius(M)
        rphi = core.r_phi(M)
        ratios.append(rphi / rs)
    
    axes[0,0].semilogx(masses, ratios, 'bo-', markersize=8)
    axes[0,0].axhline(const.PHI/2, color='red', linestyle='--', 
                     label=f'φ/2 = {const.PHI/2:.4f}')
    axes[0,0].set_xlabel('Mass [kg]')
    axes[0,0].set_ylabel('r_φ / r_s')
    axes[0,0].set_title('Natural Boundary Ratio')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].legend()
    
    # Plot 2: σ(r) Profile
    M = const.M_SUN
    rs = core.schwarzschild_radius(M)
    rphi = core.r_phi(M)
    r = np.logspace(np.log10(rs * 1.01), np.log10(rphi * 0.99), 1000)
    sigma_vals = [core.sigma(r_val, M) for r_val in r]
    
    axes[0,1].semilogx(r/rs, sigma_vals, 'b-', linewidth=2)
    axes[0,1].set_xlabel('r / r_s')
    axes[0,1].set_ylabel('σ(r)')
    axes[0,1].set_title('Segment Density Profile')
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Dual Velocity Test
    r_test = np.logspace(np.log10(2*rs), np.log10(100*rs), 100)
    invariance_test = []
    
    for r_val in r_test:
        v_esc, v_fall = core.dual_velocity(r_val, M)
        product = v_esc * v_fall
        invariance_test.append(product / const.C**2)
    
    axes[1,0].semilogx(r_test/rs, invariance_test, 'g-', linewidth=2)
    axes[1,0].axhline(1.0, color='red', linestyle='--', label='c²')
    axes[1,0].set_xlabel('r / r_s')
    axes[1,0].set_ylabel('v_esc × v_fall / c²')
    axes[1,0].set_title('Dual Velocity Invariance')
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].legend()
    
    # Plot 4: φ-Eigenschaften
    theta, x, y, magnitude = core.euler_spiral(theta_max=2*np.pi, n_points=1000)
    
    axes[1,1].plot(x, y, 'purple', linewidth=2, alpha=0.8)
    axes[1,1].set_xlabel('Real(z)')
    axes[1,1].set_ylabel('Imag(z)')
    axes[1,1].set_title('φ-Euler Spiral')
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('ssz_test_report.png', dpi=300, bbox_inches='tight')
    print("Test report saved as 'ssz_test_report.png'")
    
    return fig

if __name__ == "__main__":
    # Führe alle Tests aus
    success = run_comprehensive_test_suite()
    
    # Erstelle visuellen Bericht
    create_test_report()
    
    # Zeige Plots
    plt.show()
    
    # Exit-Code setzen
    exit(0 if success else 1)
