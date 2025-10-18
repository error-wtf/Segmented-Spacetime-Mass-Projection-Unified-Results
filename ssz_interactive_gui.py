#!/usr/bin/env python3
"""
===============================================================
SSZ Interactive GUI - Real-time Parameter Exploration
===============================================================

Interaktive Desktop-Anwendung für die Segmented Spacetime Theorie
mit Live-Parametern, 3D-Visualisierung und Echtzeit-Updates.

Features:
- Parameter-Slider für α, κ, p, M, N_max
- Live-Updates aller Plots
- 3D-Visualisierung mit Rotation
- Export-Funktionen
- Verifikations-Tests
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import plotly.graph_objects as go
import plotly.offline as pyo
from ssz_unified_suite import SSZCore, SSZVisualizer, SSZDataExport
import threading
import json
from datetime import datetime

class SSZInteractiveApp:
    """Hauptanwendung für interaktive SSZ-Exploration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌌 Segmented Spacetime - Interactive Explorer")
        self.root.geometry("1400x900")
        
        # SSZ-Komponenten initialisieren
        self.core = SSZCore()
        self.viz = SSZVisualizer(self.core)
        self.export = SSZDataExport(self.core)
        
        # Parameter-Variablen
        self.mass_var = tk.DoubleVar(value=1.0)  # in Sonnenmassen
        self.alpha_var = tk.DoubleVar(value=1.0)
        self.kappa_var = tk.DoubleVar(value=0.015)
        self.p_var = tk.DoubleVar(value=2.0)
        self.nmax_var = tk.DoubleVar(value=5.0)
        self.field_mode = tk.StringVar(value="sigma")
        
        # GUI erstellen
        self.create_widgets()
        self.update_plots()
        
    def create_widgets(self):
        """Erstellt alle GUI-Widgets"""
        
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Linke Seite: Parameter-Kontrollen
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ Parameter Controls", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.create_parameter_controls(control_frame)
        
        # Rechte Seite: Plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_plot_area(plot_frame)
        
    def create_parameter_controls(self, parent):
        """Erstellt Parameter-Slider und Kontrollen"""
        
        # Masse (in Sonnenmassen)
        ttk.Label(parent, text="Mass [M☉]:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        mass_frame = ttk.Frame(parent)
        mass_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mass_scale = ttk.Scale(mass_frame, from_=0.1, to=1000.0, 
                                   variable=self.mass_var, orient=tk.HORIZONTAL,
                                   command=self.on_parameter_change)
        self.mass_scale.pack(fill=tk.X)
        
        self.mass_label = ttk.Label(mass_frame, text="1.00 M☉")
        self.mass_label.pack()
        
        # Preset-Buttons für bekannte Massen
        preset_frame = ttk.Frame(parent)
        preset_frame.pack(fill=tk.X, pady=(0, 15))
        
        presets = [
            ("Sun", 1.0),
            ("Sgr A*", 4.15e6),
            ("Cygnus X-1", 24.0),
            ("Earth", 3.0e-6)
        ]
        
        for name, mass in presets:
            btn = ttk.Button(preset_frame, text=name, width=8,
                           command=lambda m=mass: self.set_mass_preset(m))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Alpha (Zeitdilatations-Kopplung)
        ttk.Label(parent, text="α (Time Dilation):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        alpha_frame = ttk.Frame(parent)
        alpha_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.alpha_scale = ttk.Scale(alpha_frame, from_=0.1, to=3.0,
                                    variable=self.alpha_var, orient=tk.HORIZONTAL,
                                    command=self.on_parameter_change)
        self.alpha_scale.pack(fill=tk.X)
        
        self.alpha_label = ttk.Label(alpha_frame, text="1.00")
        self.alpha_label.pack()
        
        # Kappa (Optische Kopplung)
        ttk.Label(parent, text="κ (Optical Coupling):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        kappa_frame = ttk.Frame(parent)
        kappa_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.kappa_scale = ttk.Scale(kappa_frame, from_=0.0, to=0.05,
                                    variable=self.kappa_var, orient=tk.HORIZONTAL,
                                    command=self.on_parameter_change)
        self.kappa_scale.pack(fill=tk.X)
        
        self.kappa_label = ttk.Label(kappa_frame, text="0.015")
        self.kappa_label.pack()
        
        # Field Mode Selection
        ttk.Label(parent, text="Field Visualization:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(15, 5))
        
        field_modes = [("σ(r) - Segment Density", "sigma"),
                      ("τ(r) - Time Dilation", "tau"),
                      ("n(r) - Refractive Index", "n")]
        
        for text, value in field_modes:
            ttk.Radiobutton(parent, text=text, variable=self.field_mode, 
                           value=value, command=self.on_parameter_change).pack(anchor=tk.W)
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Action Buttons
        ttk.Label(parent, text="Actions:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="🔬 Verify Theory", 
                  command=self.run_verification).pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="📊 Export Data", 
                  command=self.export_data).pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="🌐 3D Visualization", 
                  command=self.show_3d_plot).pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="🌀 φ-Euler Spiral", 
                  command=self.show_euler_spiral).pack(fill=tk.X, pady=2)
        
        # Info Panel
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Current Values", padding=5)
        info_frame.pack(fill=tk.X)
        
        self.info_text = tk.Text(info_frame, height=8, width=30, font=('Courier', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
    def create_plot_area(self, parent):
        """Erstellt den Haupt-Plot-Bereich"""
        
        # Notebook für verschiedene Plot-Tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Radiale Profile
        self.radial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.radial_frame, text="📈 Radial Profiles")
        
        # Matplotlib Figure für radiale Profile
        self.fig_radial = Figure(figsize=(10, 8), dpi=100)
        self.canvas_radial = FigureCanvasTkAgg(self.fig_radial, self.radial_frame)
        self.canvas_radial.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation Toolbar
        toolbar_frame = ttk.Frame(self.radial_frame)
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas_radial, toolbar_frame)
        
        # Tab 2: Vergleichsplots
        self.comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_frame, text="📊 Parameter Study")
        
        self.fig_comparison = Figure(figsize=(10, 8), dpi=100)
        self.canvas_comparison = FigureCanvasTkAgg(self.fig_comparison, self.comparison_frame)
        self.canvas_comparison.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def set_mass_preset(self, mass_solar):
        """Setzt Masse auf Preset-Wert"""
        self.mass_var.set(mass_solar)
        self.on_parameter_change()
        
    def on_parameter_change(self, *args):
        """Callback für Parameter-Änderungen"""
        # Labels aktualisieren
        self.mass_label.config(text=f"{self.mass_var.get():.2e} M☉")
        self.alpha_label.config(text=f"{self.alpha_var.get():.2f}")
        self.kappa_label.config(text=f"{self.kappa_var.get():.3f}")
        
        # Info-Panel aktualisieren
        self.update_info_panel()
        
        # Plots aktualisieren (mit kleiner Verzögerung für Performance)
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        self._update_timer = self.root.after(200, self.update_plots)
        
    def update_info_panel(self):
        """Aktualisiert das Info-Panel mit aktuellen Werten"""
        mass_kg = self.mass_var.get() * self.core.const.M_SUN
        rs = self.core.schwarzschild_radius(mass_kg)
        rphi = self.core.r_phi(mass_kg)
        delta = self.core.delta_M(mass_kg)
        
        # Test-Radius für Feldwerte
        r_test = 2 * rs
        sigma_val = self.core.sigma(r_test, mass_kg)
        tau_val = self.core.tau(r_test, mass_kg, self.alpha_var.get())
        n_val = self.core.n_index(r_test, mass_kg, self.kappa_var.get())
        
        info_text = f"""Current Object:
Mass: {self.mass_var.get():.2e} M☉
r_s: {rs:.2e} m
r_φ: {rphi:.2e} m
r_φ/r_s: {rphi/rs:.4f}
φ/2: {self.core.const.PHI/2:.4f}
Δ(M): {delta:.4f}

Fields at r = 2r_s:
σ(r): {sigma_val:.4f}
τ(r): {tau_val:.4f}
n(r): {n_val:.4f}

Constants:
φ = {self.core.const.PHI:.6f}
c = {self.core.const.C:.0f} m/s
G = {self.core.const.G:.2e}
"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        
    def update_plots(self):
        """Aktualisiert alle Plots mit aktuellen Parametern"""
        mass_kg = self.mass_var.get() * self.core.const.M_SUN
        
        # Radiale Profile aktualisieren
        self.fig_radial.clear()
        
        try:
            rs = self.core.schwarzschild_radius(mass_kg)
            rphi = self.core.r_phi(mass_kg)
            
            # r-Array
            r = np.logspace(np.log10(rs * 1.001), np.log10(rphi * 0.999), 1000)
            r_norm = r / rs
            
            # Felder berechnen
            sigma_vals = self.core.sigma(r, mass_kg)
            tau_vals = self.core.tau(r, mass_kg, self.alpha_var.get())
            n_vals = self.core.n_index(r, mass_kg, self.kappa_var.get())
            
            # 2x2 Subplot-Layout
            axes = self.fig_radial.subplots(2, 2, figsize=(10, 8))
            self.fig_radial.suptitle(f'SSZ Fields - M = {self.mass_var.get():.2e} M☉', fontsize=14)
            
            # σ(r)
            axes[0,0].semilogx(r_norm, sigma_vals, 'b-', linewidth=2, label='σ(r)')
            axes[0,0].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7, label=f'r_φ = {rphi/rs:.2f} r_s')
            axes[0,0].set_xlabel('r / r_s')
            axes[0,0].set_ylabel('Segment Density σ(r)')
            axes[0,0].grid(True, alpha=0.3)
            axes[0,0].legend()
            axes[0,0].set_title('Segmentdichte')
            
            # τ(r)
            axes[0,1].semilogx(r_norm, tau_vals, 'r-', linewidth=2, label='τ(r)')
            axes[0,1].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7)
            axes[0,1].set_xlabel('r / r_s')
            axes[0,1].set_ylabel('Time Dilation τ(r)')
            axes[0,1].grid(True, alpha=0.3)
            axes[0,1].legend()
            axes[0,1].set_title(f'Zeitdehnung (α={self.alpha_var.get():.2f})')
            
            # n(r)
            axes[1,0].semilogx(r_norm, n_vals, 'g-', linewidth=2, label='n(r)')
            axes[1,0].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7)
            axes[1,0].set_xlabel('r / r_s')
            axes[1,0].set_ylabel('Refractive Index n(r)')
            axes[1,0].grid(True, alpha=0.3)
            axes[1,0].legend()
            axes[1,0].set_title(f'Optischer Index (κ={self.kappa_var.get():.3f})')
            
            # Dual Velocity
            v_esc, v_fall = self.core.dual_velocity(r, mass_kg)
            axes[1,1].loglog(r_norm, v_esc/self.core.const.C, 'b-', label='v_esc/c')
            axes[1,1].loglog(r_norm, v_fall/self.core.const.C, 'r-', label='v_fall/c')
            axes[1,1].axhline(1.0, color='k', linestyle=':', alpha=0.5, label='c')
            axes[1,1].axvline(rphi/rs, color='gold', linestyle='--', alpha=0.7)
            axes[1,1].set_xlabel('r / r_s')
            axes[1,1].set_ylabel('Velocity / c')
            axes[1,1].grid(True, alpha=0.3)
            axes[1,1].legend()
            axes[1,1].set_title('Dual-Velocity-Invarianz')
            
            self.fig_radial.tight_layout()
            self.canvas_radial.draw()
            
        except Exception as e:
            print(f"Plot update error: {e}")
            
        # Parameter-Studie aktualisieren
        self.update_parameter_study()
        
    def update_parameter_study(self):
        """Aktualisiert Parameter-Studie-Plots"""
        self.fig_comparison.clear()
        
        mass_kg = self.mass_var.get() * self.core.const.M_SUN
        rs = self.core.schwarzschild_radius(mass_kg)
        r_test = 2 * rs  # Test-Radius
        
        # Parameter-Variationen
        alphas = np.linspace(0.1, 3.0, 20)
        kappas = np.linspace(0.001, 0.05, 20)
        
        # τ(r) vs α
        tau_vals = [self.core.tau(r_test, mass_kg, alpha) for alpha in alphas]
        
        # n(r) vs κ
        n_vals = [self.core.n_index(r_test, mass_kg, kappa) for kappa in kappas]
        
        # 1x2 Layout
        axes = self.fig_comparison.subplots(1, 2, figsize=(10, 4))
        
        # α-Variation
        axes[0].plot(alphas, tau_vals, 'r-', linewidth=2, marker='o', markersize=4)
        axes[0].axvline(self.alpha_var.get(), color='red', linestyle='--', alpha=0.7, label=f'Current α = {self.alpha_var.get():.2f}')
        axes[0].set_xlabel('α (Time Dilation Coupling)')
        axes[0].set_ylabel('τ(2r_s)')
        axes[0].set_title('Time Dilation vs α')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        
        # κ-Variation
        axes[1].plot(kappas, n_vals, 'g-', linewidth=2, marker='o', markersize=4)
        axes[1].axvline(self.kappa_var.get(), color='green', linestyle='--', alpha=0.7, label=f'Current κ = {self.kappa_var.get():.3f}')
        axes[1].set_xlabel('κ (Optical Coupling)')
        axes[1].set_ylabel('n(2r_s)')
        axes[1].set_title('Refractive Index vs κ')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        
        self.fig_comparison.tight_layout()
        self.canvas_comparison.draw()
        
    def run_verification(self):
        """Führt Theorie-Verifikation aus"""
        def verify_thread():
            try:
                # Verifikation in separatem Thread
                result = self.export.verify_ssz_predictions()
                
                # Ergebnis in GUI anzeigen
                self.root.after(0, lambda: messagebox.showinfo(
                    "Theory Verification", 
                    "✅ SSZ Theory verification completed!\nCheck console for detailed results."
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Verification Error", 
                    f"Error during verification: {str(e)}"
                ))
        
        threading.Thread(target=verify_thread, daemon=True).start()
        
    def export_data(self):
        """Exportiert aktuelle Daten"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export SSZ Data"
        )
        
        if filename:
            try:
                # Aktuelle Parameter sammeln
                mass_kg = self.mass_var.get() * self.core.const.M_SUN
                
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'parameters': {
                        'mass_solar': self.mass_var.get(),
                        'alpha': self.alpha_var.get(),
                        'kappa': self.kappa_var.get(),
                        'field_mode': self.field_mode.get()
                    },
                    'calculated_values': {
                        'r_schwarzschild': self.core.schwarzschild_radius(mass_kg),
                        'r_phi': self.core.r_phi(mass_kg),
                        'delta_M': self.core.delta_M(mass_kg)
                    }
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Export Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")
                
    def show_3d_plot(self):
        """Zeigt 3D-Plotly-Visualisierung"""
        try:
            mass_kg = self.mass_var.get() * self.core.const.M_SUN
            fig_3d = self.viz.plot_3d_field(mass_kg, self.field_mode.get(), 
                                           self.alpha_var.get(), self.kappa_var.get())
            
            # Temporäre HTML-Datei erstellen und öffnen
            temp_file = "temp_ssz_3d.html"
            pyo.plot(fig_3d, filename=temp_file, auto_open=True)
            
        except Exception as e:
            messagebox.showerror("3D Plot Error", f"Error creating 3D plot: {str(e)}")
            
    def show_euler_spiral(self):
        """Zeigt φ-Euler-Spirale"""
        try:
            fig_euler = self.viz.plot_euler_spiral()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Euler Spiral Error", f"Error creating Euler spiral: {str(e)}")

def main():
    """Startet die interaktive SSZ-Anwendung"""
    root = tk.Tk()
    app = SSZInteractiveApp(root)
    
    # Styling
    style = ttk.Style()
    style.theme_use('clam')
    
    # Icon setzen (falls verfügbar)
    try:
        root.iconbitmap('ssz_icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
