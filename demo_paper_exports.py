#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Paper Export Tools

Zeigt wie man die Figure-Generation verwendet.
Kann direkt ausgeführt werden zum Testen.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import numpy as np
from pathlib import Path

# UTF-8 für Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Imports
from tools.plot_helpers import line, scatter, heatmap
from tools.figure_catalog import get_caption, list_all_figures
from tools.io_utils import sha256_file, update_manifest


def demo_basic_plots():
    """Demo: Basis-Plots erstellen"""
    print("\n" + "="*80)
    print("DEMO 1: Basis-Plots")
    print("="*80)
    
    # Dummy-Daten
    x = np.arange(1, 11)
    y = 10 + 2 * x + np.random.randn(10)
    
    # Line-Plot
    print("\n[1/3] Erstelle Line-Plot...")
    paths = line(
        x, y,
        "Ring index k", "Velocity [km/s]",
        "Demo: Ring-chain velocity",
        "reports/figures/demo/fig_demo_line",
        formats=("png", "svg"),
        dpi=600,
        width_mm=160
    )
    print(f"✓ Erstellt: {paths}")
    
    # Scatter-Plot
    print("\n[2/3] Erstelle Scatter-Plot...")
    gamma = np.linspace(1.0, 2.0, 20)
    nu = 1e12 / gamma
    paths = scatter(
        gamma, nu,
        "γ", "ν_out [Hz]",
        "Demo: Frequency shift",
        "reports/figures/demo/fig_demo_scatter",
        formats=("png", "svg"),
        dpi=600
    )
    print(f"✓ Erstellt: {paths}")
    
    # Heatmap
    print("\n[3/3] Erstelle Heatmap...")
    Z = np.random.rand(10, 10)
    paths = heatmap(
        Z,
        np.arange(10), np.arange(10),
        "α", "β",
        "Demo: Parameter sweep",
        "reports/figures/demo/fig_demo_heatmap",
        formats=("png",),
        dpi=600
    )
    print(f"✓ Erstellt: {paths}")
    
    print("\n✅ Demo 1 complete!")


def demo_captions():
    """Demo: Caption-System"""
    print("\n" + "="*80)
    print("DEMO 2: Caption-System")
    print("="*80)
    
    print("\nVerfügbare Figures:")
    for name in list_all_figures():
        print(f"  - {name}")
    
    print("\nBeispiel-Captions:")
    for name in ["ringchain_v_vs_k", "gamma_log_vs_k", "posterior_corner"]:
        caption = get_caption(name, "G79")
        print(f"\n{name}:")
        print(f"  {caption[:80]}...")


def demo_manifest():
    """Demo: Manifest-System"""
    print("\n" + "="*80)
    print("DEMO 3: Manifest-System")
    print("="*80)
    
    # Erstelle Test-Manifest
    manifest_path = "reports/DEMO_MANIFEST.json"
    
    print(f"\n[1/2] Erstelle Manifest: {manifest_path}")
    
    # Sammle Test-Artifacts
    test_files = list(Path("reports/figures/demo").glob("*.png"))
    
    if not test_files:
        print("⚠️  Keine Test-Figures gefunden. Führe Demo 1 zuerst aus!")
        return
    
    artifacts = []
    for fp in test_files:
        artifacts.append({
            "role": "figure",
            "path": str(fp.as_posix()),
            "sha256": sha256_file(str(fp)),
            "format": "png"
        })
    
    print(f"[2/2] Registriere {len(artifacts)} Artifacts...")
    
    update_manifest(manifest_path, {
        "meta": {
            "demo": True,
            "test_run": True
        },
        "artifacts": artifacts
    })
    
    print(f"✓ Manifest erstellt: {manifest_path}")
    print("\n✅ Demo 3 complete!")


def demo_orchestrator():
    """Demo: Figure-Orchestrator"""
    print("\n" + "="*80)
    print("DEMO 4: Figure-Orchestrator")
    print("="*80)
    
    from tools.figure_orchestrator import finalize_figures
    
    # Mock argparse object
    class Args:
        fig = True
        fig_formats = "png,svg"
        fig_dpi = 600
        fig_width_mm = 160
        fig_out = "reports/figures"
    
    args = Args()
    
    # Dummy-Datasets
    datasets = {
        "k": np.arange(1, 11),
        "v": 12.5 + 2 * np.arange(1, 11) + np.random.randn(10) * 0.5,
        "log_gamma": np.log(1.0 + 0.1 * np.arange(1, 11)),
        "gamma": 1.0 + 0.1 * np.arange(1, 11),
        "nu_out": 1e12 / (1.0 + 0.1 * np.arange(1, 11))
    }
    
    print("\nGeneriere Figures mit Orchestrator...")
    finalize_figures(args, "DemoObject", datasets)
    
    print("\n✅ Demo 4 complete!")


def main():
    """Hauptfunktion"""
    print("="*80)
    print("SSZ Paper Export Tools - DEMO")
    print("="*80)
    
    try:
        # Demo 1: Basis-Plots
        demo_basic_plots()
        
        # Demo 2: Captions
        demo_captions()
        
        # Demo 3: Manifest
        demo_manifest()
        
        # Demo 4: Orchestrator
        demo_orchestrator()
        
        print("\n" + "="*80)
        print("✅ ALLE DEMOS ERFOLGREICH!")
        print("="*80)
        print("\nErstellte Dateien:")
        print("  - reports/figures/demo/*.png")
        print("  - reports/figures/demo/*.svg")
        print("  - reports/DEMO_MANIFEST.json")
        print("  - reports/figures/FIGURE_INDEX.md")
        print("  - reports/PAPER_EXPORTS_MANIFEST.json")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
