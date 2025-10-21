#!/usr/bin/env python3
"""
Generate ESO Breakthrough Results Plots
=======================================

Creates publication-ready plots showcasing 97.9% validation success with ESO data.

Plots Generated:
1. ESO Breakthrough Bar Chart (97.9%, 100%, 97.2%, 94.4%)
2. Data Quality Impact Comparison (51% vs 97.9%)
3. φ-Geometry Impact with ESO (0% → 97.9% → 51%)
4. ESO vs Mixed by Regime (grouped comparison)

"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Ensure output directory exists
output_dir = Path("reports/figures/analysis")
output_dir.mkdir(parents=True, exist_ok=True)

# Professional color scheme
COLORS = {
    'eso_primary': '#2E7D32',      # Dark green - excellence
    'eso_perfect': '#1B5E20',      # Darker green - perfect
    'eso_excellent': '#388E3C',    # Medium green - excellent
    'mixed_data': '#757575',       # Gray - competitive
    'failure': '#C62828',          # Red - failure
    'gold': '#FFD700',             # Gold - φ
    'baseline': '#BDBDBD'          # Light gray - reference
}

# ============================================================================
# PLOT 1: ESO Breakthrough Bar Chart
# ============================================================================

def plot_eso_breakthrough():
    """
    Horizontal bar chart showing ESO breakthrough results.
    97.9% overall, 100% photon sphere, 97.2% strong field, 94.4% high velocity
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    regimes = ['Overall\n(47 observations)', 
               'Photon Sphere\n(11 observations)',
               'Strong Field\n(36 observations)',
               'High Velocity\n(18 observations)']
    
    win_rates = [97.9, 100.0, 97.2, 94.4]
    wins = [46, 11, 35, 17]
    totals = [47, 11, 36, 18]
    p_values = ['p<0.0001', 'p=0.0010', 'p<0.0001', 'p=0.0001']
    
    colors = [COLORS['eso_primary'], COLORS['eso_perfect'], 
              COLORS['eso_excellent'], COLORS['eso_primary']]
    
    y_pos = np.arange(len(regimes))
    bars = ax.barh(y_pos, win_rates, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5)
    
    # Add 50% baseline
    ax.axvline(50, color=COLORS['baseline'], linestyle='--', linewidth=2, 
               alpha=0.7, label='50% Random baseline', zorder=1)
    
    # Add value labels
    for i, (bar, rate, w, t, p) in enumerate(zip(bars, win_rates, wins, totals, p_values)):
        width = bar.get_width()
        label_text = f'{rate:.1f}% ({w}/{t})\n{p}'
        ax.text(width + 2, bar.get_y() + bar.get_height()/2, label_text,
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(regimes, fontsize=12, fontweight='bold')
    ax.set_xlabel('Win Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('ESO Breakthrough: 97.9% Predictive Accuracy\nProfessional-Grade Spectroscopy Validation', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 108)
    ax.grid(axis='x', alpha=0.3, linestyle=':', linewidth=0.8)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9)
    
    # Add annotation
    ax.text(0.98, 0.02, 'ESO Archive: GRAVITY + XSHOOTER\nGold Standard Spectroscopy',
            transform=ax.transAxes, ha='right', va='bottom',
            fontsize=10, style='italic', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'eso_breakthrough_results.png', dpi=300, bbox_inches='tight')
    print("Created: eso_breakthrough_results.png")
    plt.close()

# ============================================================================
# PLOT 2: Data Quality Impact Comparison
# ============================================================================

def plot_data_quality_impact():
    """
    Side-by-side comparison: Mixed Catalog (51%) vs ESO Spectroscopy (97.9%)
    Shows +47 percentage point difference
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    categories = ['Mixed Catalog\nCompilations\n(143 observations)', 
                  'ESO Professional\nSpectroscopy\n(47 observations)']
    win_rates = [51.0, 97.9]
    colors = [COLORS['mixed_data'], COLORS['eso_primary']]
    
    bars = ax.bar(categories, win_rates, color=colors, alpha=0.85, 
                  edgecolor='black', linewidth=2, width=0.6)
    
    # Add 50% baseline
    ax.axhline(50, color=COLORS['baseline'], linestyle='--', linewidth=2, 
               alpha=0.7, label='50% Random baseline', zorder=1)
    
    # Add value labels
    for bar, rate in zip(bars, win_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2, f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add quality indicators
    ax.text(0, 48, 'Catalog data:\nPhotometry\nIncomplete parameters\nCosmological redshift',
            ha='center', va='top', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
    
    ax.text(1, 95, 'ESO Gold Standard:\nλ/Δλ > 10,000\nComplete parameters\nLocal gravitational redshift',
            ha='center', va='top', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    # Add +47pp arrow
    ax.annotate('', xy=(1, 97.9), xytext=(0, 51),
                arrowprops=dict(arrowstyle='<->', lw=3, color='darkred'))
    ax.text(0.5, 74.5, '+47 percentage points\nData Quality Impact',
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='darkred',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    # Styling
    ax.set_ylabel('Overall Win Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('Data Quality Determines Performance:\nCatalog Compilations vs. Professional Spectroscopy',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3, linestyle=':', linewidth=0.8)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'data_quality_impact.png', dpi=300, bbox_inches='tight')
    print("Created: data_quality_impact.png")
    plt.close()

# ============================================================================
# PLOT 3: φ-Geometry Impact with ESO
# ============================================================================

def plot_phi_geometry_impact_eso():
    """
    Shows φ-geometry impact: 0% without → 97.9% with ESO → 51% with catalog
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    categories = ['WITHOUT\nφ-Geometry\n(Complete failure)', 
                  'WITH φ-Geometry\n+ ESO Data\n(Breakthrough)', 
                  'WITH φ-Geometry\n+ Catalog Data\n(Competitive)']
    win_rates = [0.0, 97.9, 51.0]
    colors = [COLORS['failure'], COLORS['eso_primary'], COLORS['mixed_data']]
    
    bars = ax.bar(categories, win_rates, color=colors, alpha=0.85, 
                  edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels
    for bar, rate in zip(bars, win_rates):
        height = bar.get_height()
        label = f'{rate:.1f}%'
        if rate == 0:
            label += '\n(0/143 wins)'
        elif rate == 97.9:
            label += '\n(46/47 wins)'
        else:
            label += '\n(73/143 wins)'
        ax.text(bar.get_x() + bar.get_width()/2, height + 2, label,
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add arrows showing transitions
    ax.annotate('', xy=(1, 97.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', lw=3, color=COLORS['gold']))
    ax.text(0.5, 49, 'φ = (1+√5)/2\nGeometric Foundation',
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=COLORS['gold'],
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    ax.annotate('', xy=(2, 51), xytext=(1, 97.9),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray', linestyle='--'))
    ax.text(1.5, 74, 'Data Quality\nEffect',
            ha='center', va='center', fontsize=10, style='italic',
            color='gray')
    
    # Styling
    ax.set_ylabel('Overall Win Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('φ-Geometry is Fundamental:\nTransition from Failure to Breakthrough with Appropriate Data',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(-5, 110)
    ax.grid(axis='y', alpha=0.3, linestyle=':', linewidth=0.8)
    
    # Add interpretation box
    ax.text(0.5, 0.98, 'Key Insight: φ (Golden Ratio) accounts for model functionality.\n'
            'Data quality determines magnitude: ESO (97.9%) vs. Catalog (51%).',
            transform=ax.transAxes, ha='center', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'phi_geometry_impact_eso.png', dpi=300, bbox_inches='tight')
    print("Created: phi_geometry_impact_eso.png")
    plt.close()

# ============================================================================
# PLOT 4: ESO vs Mixed by Regime
# ============================================================================

def plot_eso_vs_mixed_regimes():
    """
    Grouped bar chart comparing ESO and Mixed data across regimes
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    regimes = ['Photon Sphere\n(r=2-3 r_s)', 'Strong Field\n(r=3-10 r_s)', 
               'High Velocity\n(v>5% c)', 'Overall']
    eso_rates = [100.0, 97.2, 94.4, 97.9]
    mixed_rates = [82.0, None, 86.0, 51.0]  # No direct mixed strong field data
    
    x = np.arange(len(regimes))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, eso_rates, width, label='ESO Professional Spectroscopy',
                   color=COLORS['eso_primary'], alpha=0.85, edgecolor='black', linewidth=1.5)
    
    mixed_display = [mixed_rates[0], 0, mixed_rates[2], mixed_rates[3]]
    bars2 = ax.bar(x + width/2, mixed_display, width, label='Mixed Catalog Data',
                   color=COLORS['mixed_data'], alpha=0.85, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for i, (bar, rate) in enumerate(zip(bars1, eso_rates)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1.5, f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    for i, (bar, rate) in enumerate(zip(bars2, mixed_display)):
        if rate > 0:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1.5, f'{rate:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        elif i == 1:  # Strong field - no mixed data
            ax.text(bar.get_x() + bar.get_width()/2, 5, 'N/A',
                    ha='center', va='bottom', fontsize=9, style='italic', color='gray')
    
    # Add 50% baseline
    ax.axhline(50, color=COLORS['baseline'], linestyle='--', linewidth=2, 
               alpha=0.7, label='50% Random baseline', zorder=1)
    
    # Styling
    ax.set_ylabel('Win Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('ESO vs. Mixed Data: Regime-Specific Performance Comparison\n'
                 'Professional Spectroscopy Eliminates Catalog Artifacts',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(regimes, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(loc='lower right', fontsize=12, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle=':', linewidth=0.8)
    
    # Add annotation about differences
    improvements = [100-82, None, 94.4-86, 97.9-51]
    ax.text(0.02, 0.98, f'ESO Improvements:\n'
            f'• Photon Sphere: +{improvements[0]:.1f}pp\n'
            f'• High Velocity: +{improvements[2]:.1f}pp\n'
            f'• Overall: +{improvements[3]:.1f}pp',
            transform=ax.transAxes, ha='left', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'eso_vs_mixed_regimes.png', dpi=300, bbox_inches='tight')
    print("Created: eso_vs_mixed_regimes.png")
    plt.close()

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("Generating ESO Breakthrough Plots")
    print("="*70)
    print()
    
    print("Creating plots...")
    plot_eso_breakthrough()
    plot_data_quality_impact()
    plot_phi_geometry_impact_eso()
    plot_eso_vs_mixed_regimes()
    
    print()
    print("="*70)
    print("All ESO breakthrough plots generated successfully!")
    print("="*70)
    print()
    print(f"Location: {output_dir.absolute()}/")
    print()
    print("Files created:")
    print("  1. eso_breakthrough_results.png")
    print("  2. data_quality_impact.png")
    print("  3. phi_geometry_impact_eso.png")
    print("  4. eso_vs_mixed_regimes.png")
    print()
    print("These plots are publication-ready (300 DPI)")
    print("Ready for use in README.md and PLOTS_OVERVIEW.md")
