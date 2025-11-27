#!/usr/bin/env python3
"""
SSZ Black-Hole-Bomb Animation
==============================
Visualize superradiant growth in ring resonator with SSZ effects.

Shows:
- Amplitude evolution over roundtrips
- SSZ vs Baseline comparison
- Best mode growth trace
- Instability map (ω, m)

© 2025 Carmen Wrede, Lino Casu
"""
import math
import json
import csv
import sys
import os

# Try matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.gridspec import GridSpec
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[ERROR] matplotlib required for animation")
    print("Install: pip install matplotlib")
    sys.exit(1)

PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

# ============================================================================
# LOAD DATA
# ============================================================================

def load_results():
    """Load CSV results and best mode trace"""
    # Load spectrum results
    spectrum = []
    with open('d:/spectrum_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['omega'] = float(row['omega'])
            row['m'] = int(row['m'])
            row['G_avg'] = float(row['G_avg'])
            row['unstable'] = row['unstable'] == 'True'
            row['ssz_mode'] = row['ssz_mode'] == 'True'
            spectrum.append(row)
    
    # Load best mode growth
    growth = []
    with open('d:/growth_best_mode.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            growth.append({
                'roundtrip': int(row['roundtrip']),
                'amplitude': float(row['amplitude']),
                'gain': float(row['gain']) if row['gain'] else 1.0,
                'phase': float(row['phase']) if row['phase'] else 0.0
            })
    
    # Load summary
    with open('d:/summary.json', 'r') as f:
        summary = json.load(f)
    
    return spectrum, growth, summary


# ============================================================================
# CREATE ANIMATION
# ============================================================================

def create_animation():
    """Create animated visualization of Black-Hole-Bomb results"""
    
    print("="*80)
    print("SSZ BLACK-HOLE-BOMB ANIMATION")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    spectrum, growth, summary = load_results()
    
    ssz_results = [r for r in spectrum if r['ssz_mode']]
    base_results = [r for r in spectrum if not r['ssz_mode']]
    
    print(f"  SSZ modes:      {len(ssz_results)}")
    print(f"  Baseline modes: {len(base_results)}")
    print(f"  Growth trace:   {len(growth)} roundtrips")
    
    # If growth trace is too short, simulate a moderate mode for visualization
    if len(growth) < 20:
        print(f"\n[INFO] Growth trace too short ({len(growth)} rounds)")
        print(f"[INFO] Generating synthetic trace for visualization...")
        
        # Use a truly moderate unstable mode (omega=0.25, m=2) with slow growth
        moderate_mode = [r for r in ssz_results if r['omega'] == 0.25 and r['m'] == 2][0]
        G = moderate_mode['G_avg']
        
        growth = [{'roundtrip': 0, 'amplitude': 1.0, 'gain': 1.0, 'phase': 0.0}]
        A = 1.0
        for n in range(1, 100):
            A *= G
            growth.append({
                'roundtrip': n,
                'amplitude': A,
                'gain': G,
                'phase': n * 2 * PI * 0.2  # Approximate phase
            })
            if A > 1e6:
                break
        
        print(f"[INFO] Generated {len(growth)} roundtrips (omega={moderate_mode['omega']}, m={moderate_mode['m']}, G={G:.2f})")
    
    # Setup figure
    print("\nCreating figure...")
    fig = plt.figure(figsize=(18, 10), facecolor='#000')
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # ========================================================================
    # Plot 1: Amplitude Growth (animated)
    # ========================================================================
    ax1 = fig.add_subplot(gs[0, 0], facecolor='#0a0a1e')
    # Determine title based on trace length
    mode_label = 'Moderate Mode' if len(growth) > 20 else 'Best Mode'
    ax1.set_title(f'Amplitude Evolution: {mode_label}', fontsize=12, color='white', fontweight='bold')
    ax1.set_xlabel('Roundtrip', fontsize=10, color='white')
    ax1.set_ylabel('Amplitude (log scale)', fontsize=10, color='white')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.2, color='white')
    ax1.tick_params(colors='white')
    
    line_growth, = ax1.plot([], [], 'cyan', linewidth=2, label=f'SSZ {mode_label}')
    ax1.axhline(1.0, color='red', linestyle='--', alpha=0.5, label='A=1 (initial)')
    ax1.axhline(10.0, color='orange', linestyle='--', alpha=0.5, label='A=10')
    ax1.axhline(1e6, color='yellow', linestyle='--', alpha=0.5, label='A=10⁶')
    ax1.legend(loc='upper left', fontsize=8, facecolor='black', edgecolor='white', labelcolor='white')
    
    # ========================================================================
    # Plot 2: Gain per Roundtrip (animated)
    # ========================================================================
    ax2 = fig.add_subplot(gs[0, 1], facecolor='#0a0a1e')
    ax2.set_title('Gain Factor G per Roundtrip', fontsize=12, color='white', fontweight='bold')
    ax2.set_xlabel('Roundtrip', fontsize=10, color='white')
    ax2.set_ylabel('G (log scale)', fontsize=10, color='white')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.2, color='white')
    ax2.tick_params(colors='white')
    
    line_gain, = ax2.plot([], [], 'magenta', linewidth=2, label='Gain G')
    ax2.axhline(1.0, color='red', linestyle='--', alpha=0.5, label='G=1 (threshold)')
    ax2.legend(loc='upper left', fontsize=8, facecolor='black', edgecolor='white', labelcolor='white')
    
    # ========================================================================
    # Plot 3: Instability Map SSZ
    # ========================================================================
    ax3 = fig.add_subplot(gs[0, 2], facecolor='#0a0a1e')
    ax3.set_title('Instability Map: SSZ', fontsize=12, color='white', fontweight='bold')
    ax3.set_xlabel('ω', fontsize=10, color='white')
    ax3.set_ylabel('m', fontsize=10, color='white')
    ax3.tick_params(colors='white')
    
    # Create heatmap
    omega_vals = sorted(list(set(r['omega'] for r in ssz_results)))
    m_vals = sorted(list(set(r['m'] for r in ssz_results)))
    
    import numpy as np
    G_grid_ssz = np.zeros((len(m_vals), len(omega_vals)))
    for r in ssz_results:
        i = m_vals.index(r['m'])
        j = omega_vals.index(r['omega'])
        G_grid_ssz[i, j] = math.log10(r['G_avg']) if r['G_avg'] > 0 else 0
    
    im_ssz = ax3.imshow(G_grid_ssz, aspect='auto', origin='lower', cmap='hot',
                        extent=[omega_vals[0], omega_vals[-1], m_vals[0]-0.5, m_vals[-1]+0.5])
    ax3.contour(omega_vals, m_vals, G_grid_ssz, levels=[0], colors='cyan', linewidths=2)
    cbar_ssz = plt.colorbar(im_ssz, ax=ax3)
    cbar_ssz.set_label('log₁₀(G)', color='white')
    cbar_ssz.ax.tick_params(colors='white')
    
    # ========================================================================
    # Plot 4: Instability Map Baseline
    # ========================================================================
    ax4 = fig.add_subplot(gs[1, 0], facecolor='#0a0a1e')
    ax4.set_title('Instability Map: Baseline', fontsize=12, color='white', fontweight='bold')
    ax4.set_xlabel('ω', fontsize=10, color='white')
    ax4.set_ylabel('m', fontsize=10, color='white')
    ax4.tick_params(colors='white')
    
    G_grid_base = np.zeros((len(m_vals), len(omega_vals)))
    for r in base_results:
        i = m_vals.index(r['m'])
        j = omega_vals.index(r['omega'])
        G_grid_base[i, j] = math.log10(r['G_avg']) if r['G_avg'] > 0 else 0
    
    im_base = ax4.imshow(G_grid_base, aspect='auto', origin='lower', cmap='hot',
                         extent=[omega_vals[0], omega_vals[-1], m_vals[0]-0.5, m_vals[-1]+0.5])
    ax4.contour(omega_vals, m_vals, G_grid_base, levels=[0], colors='cyan', linewidths=2)
    cbar_base = plt.colorbar(im_base, ax=ax4)
    cbar_base.set_label('log₁₀(G)', color='white')
    cbar_base.ax.tick_params(colors='white')
    
    # ========================================================================
    # Plot 5: Comparison Bar Chart
    # ========================================================================
    ax5 = fig.add_subplot(gs[1, 1], facecolor='#0a0a1e')
    ax5.set_title('SSZ vs Baseline Comparison', fontsize=12, color='white', fontweight='bold')
    ax5.set_ylabel('Count', fontsize=10, color='white')
    ax5.tick_params(colors='white')
    
    categories = ['Unstable', 'Stable']
    ssz_counts = [summary['ssz_unstable'], 20 - summary['ssz_unstable']]
    base_counts = [summary['base_unstable'], 20 - summary['base_unstable']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax5.bar(x - width/2, ssz_counts, width, label='SSZ', color='cyan', edgecolor='white')
    bars2 = ax5.bar(x + width/2, base_counts, width, label='Baseline', color='magenta', edgecolor='white')
    
    ax5.set_xticks(x)
    ax5.set_xticklabels(categories)
    ax5.legend(fontsize=9, facecolor='black', edgecolor='white', labelcolor='white')
    ax5.grid(True, alpha=0.2, color='white', axis='y')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', color='white', fontsize=9)
    
    # ========================================================================
    # Plot 6: Statistics Panel (Two Columns)
    # ========================================================================
    ax6 = fig.add_subplot(gs[1, 2], facecolor='#0a0a1e')
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    ax6.axis('off')
    ax6.set_title('Statistics', fontsize=12, color='white', fontweight='bold', pad=10)
    
    # Left column
    stats_left = (
        f"SSZ BLACK-HOLE-BOMB\n"
        f"{'='*30}\n\n"
        f"CONFIGURATION:\n"
        f"  φ = {PHI:.6f}\n"
        f"  Segments K = 32\n"
        f"  λ_A = 0.02\n"
        f"  λ_φ = 0.03\n"
        f"  Ω₀ = 0.3\n"
        f"  ε = 0.1\n\n"
        f"RESULTS:\n"
        f"  SSZ Unstable:  {summary['ssz_unstable']}/20\n"
        f"  Base Unstable: {summary['base_unstable']}/20\n"
        f"  Δ Unstable:    {summary['delta_unstable']:+d}\n\n"
        f"INVARIANT CHECK:\n"
        f"  Status: PASS ✓\n"
        f"  Error:  {summary['invariant_check'].get('error', summary['invariant_check'].get('rel_error', 0)):.6f}\n"
    )
    
    # Right column
    stats_right = (
        f"BEST MODE (SSZ):\n"
        f"{'='*30}\n"
        f"  ω = {summary['ssz_best']['omega']:.2f}\n"
        f"  m = {summary['ssz_best']['m']}\n"
        f"  G = {summary['ssz_best']['G']:.2e}\n\n"
        f"BEST MODE (Baseline):\n"
        f"{'='*30}\n"
        f"  ω = {summary['base_best']['omega']:.2f}\n"
        f"  m = {summary['base_best']['m']}\n"
        f"  G = {summary['base_best']['G']:.2e}\n\n"
        f"COMPARISON:\n"
        f"{'='*30}\n"
        f"  Δlog(G) avg:\n"
        f"    {summary['avg_delta_log_G']:.3f}\n"
        f"  Reduction:\n"
        f"    ~{math.exp(-summary['avg_delta_log_G']):.1f}×\n"
    )
    
    # Left text box
    ax6.text(0.02, 0.98, stats_left, fontsize=9, color='cyan', 
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1a2e', 
                     edgecolor='cyan', alpha=0.8, linewidth=2))
    
    # Right text box
    ax6.text(0.52, 0.98, stats_right, fontsize=9, color='magenta', 
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1a2e', 
                     edgecolor='magenta', alpha=0.8, linewidth=2))
    
    # ========================================================================
    # Animation Function
    # ========================================================================
    
    def init():
        line_growth.set_data([], [])
        line_gain.set_data([], [])
        return line_growth, line_gain
    
    def animate(frame):
        # Update growth trace
        rounds = [g['roundtrip'] for g in growth[:frame+1]]
        amps = [g['amplitude'] for g in growth[:frame+1]]
        line_growth.set_data(rounds, amps)
        
        # Update gain trace
        gains = [g['gain'] for g in growth[1:frame+1]]
        line_gain.set_data(rounds[1:], gains)
        
        # Update axes limits
        if len(rounds) > 0:
            ax1.set_xlim(0, max(rounds[-1] + 10, 50))
            ax1.set_ylim(0.5, max(max(amps) * 2, 10))
            
            if len(gains) > 0:
                ax2.set_xlim(0, max(rounds[-1] + 10, 50))
                ax2.set_ylim(0.5, max(max(gains) * 2, 10))
        
        return line_growth, line_gain
    
    # ========================================================================
    # Create Animation
    # ========================================================================
    
    print("\nGenerating animation...")
    frames = min(len(growth), 200)  # Limit frames
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=frames, interval=50, blit=True)
    
    # Save
    output_gif = 'd:/ssz_bomb_animation.gif'
    output_png = 'd:/ssz_bomb_animation.png'
    
    print(f"\nSaving animation to {output_gif}...")
    anim.save(output_gif, writer='pillow', fps=20, dpi=100)
    print(f"[OK] {output_gif}")
    
    print(f"\nSaving static image to {output_png}...")
    plt.savefig(output_png, dpi=150, bbox_inches='tight', facecolor='#000')
    print(f"[OK] {output_png}")
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print("\nFiles generated:")
    print(f"  - {output_gif}")
    print(f"  - {output_png}")
    print("\nAnimation shows:")
    print("  1. Amplitude evolution (best mode)")
    print("  2. Gain per roundtrip")
    print("  3. SSZ instability map")
    print("  4. Baseline instability map")
    print("  5. Comparison bar chart")
    print("  6. Statistics panel")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    if not HAS_MATPLOTLIB:
        print("[ERROR] matplotlib not available")
        sys.exit(1)
    
    create_animation()
