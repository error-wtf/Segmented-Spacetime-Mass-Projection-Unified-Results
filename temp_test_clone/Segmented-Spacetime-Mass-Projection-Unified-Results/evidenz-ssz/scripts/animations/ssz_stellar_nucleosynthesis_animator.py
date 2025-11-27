#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Stellar Nucleosynthesis Animation
Zeigt die Entstehung schwerer Elemente in Sternen - Grundvoraussetzungen fürs Leben
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
from matplotlib.collections import LineCollection
import matplotlib.patheffects as path_effects

# SSZ-Farben
COLOR_SSZ = '#00D9FF'      # Cyan
COLOR_GR = '#FF6B6B'       # Red
COLOR_LAMBDA = '#FFD93D'   # Yellow
COLOR_BG = '#0a0a0a'       # Dark background
COLOR_TEXT = '#FFFFFF'     # White text

def create_stellar_nucleosynthesis_animation(output_file='ssz_stellar_nucleosynthesis.gif', 
                                            duration=20, fps=30):
    """
    Erstellt Animation der stellaren Nukleosynthese
    """
    
    frames = int(duration * fps)
    
    fig = plt.figure(figsize=(19.2, 10.8), facecolor=COLOR_BG, dpi=100)
    
    # 4 Subplots: Stern-Struktur, Fusion, Element-Produktion, SSZ-Metrik
    gs = fig.add_gridspec(2, 2, hspace=0.15, wspace=0.15,
                          left=0.05, right=0.95, top=0.93, bottom=0.07)
    
    ax1 = fig.add_subplot(gs[0, 0])  # Stern-Struktur
    ax2 = fig.add_subplot(gs[0, 1])  # Fusionsprozess
    ax3 = fig.add_subplot(gs[1, 0])  # Element-Produktion Timeline
    ax4 = fig.add_subplot(gs[1, 1])  # SSZ Segment-Dichte im Stern
    
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor(COLOR_BG)
        ax.tick_params(colors=COLOR_TEXT)
        for spine in ax.spines.values():
            spine.set_color(COLOR_TEXT)
            spine.set_linewidth(1.5)
    
    # Titel
    title = fig.suptitle('', fontsize=20, color=COLOR_TEXT, weight='bold', y=0.97)
    
    def init():
        """Initialize animation"""
        return []
    
    def animate(frame):
        """Animation frame"""
        
        # Clear axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.clear()
            ax.set_facecolor(COLOR_BG)
        
        # Progress (0 to 1)
        t = frame / frames
        
        # ====================================================================
        # SUBPLOT 1: Stellar Structure
        # ====================================================================
        
        ax1.set_xlim(-1.5, 1.5)
        ax1.set_ylim(-1.5, 1.5)
        ax1.set_aspect('equal')
        ax1.set_title('Stern-Struktur (SSZ)', fontsize=14, color=COLOR_TEXT, weight='bold')
        ax1.axis('off')
        
        # Stern (mehrere Schichten)
        layers = [
            (1.0, '#FFE66D', 'Hülle (H, He)'),
            (0.7, '#FF6B6B', 'Brennzone'),
            (0.4, '#FF3D3D', 'Kern (Fusion)'),
        ]
        
        for radius, color, label in layers:
            circle = Circle((0, 0), radius, color=color, alpha=0.6, zorder=1)
            ax1.add_patch(circle)
            if t > 0.2:
                ax1.text(0, radius + 0.1, label, ha='center', fontsize=10, 
                        color=COLOR_TEXT, weight='bold')
        
        # Kern-Aktivität (pulsierend)
        core_radius = 0.4 * (1 + 0.1 * np.sin(t * 10))
        core_circle = Circle((0, 0), core_radius, color='#FFFF00', alpha=0.8, zorder=2)
        ax1.add_patch(core_circle)
        
        # Fusionslinien (strahlenförmig)
        if t > 0.3:
            num_rays = 12
            for i in range(num_rays):
                angle = 2 * np.pi * i / num_rays + t * 5
                x = [0, 0.35 * np.cos(angle)]
                y = [0, 0.35 * np.sin(angle)]
                ax1.plot(x, y, color=COLOR_LAMBDA, linewidth=2, alpha=0.7, zorder=3)
        
        # Temperatur-Anzeige
        if t > 0.4:
            temp_text = f"T_Kern: {15 + t*5:.1f} MK"
            ax1.text(0, -1.3, temp_text, ha='center', fontsize=12, 
                    color=COLOR_LAMBDA, weight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=COLOR_BG, 
                             edgecolor=COLOR_LAMBDA, linewidth=2))
        
        # ====================================================================
        # SUBPLOT 2: Fusion Process (CNO Cycle)
        # ====================================================================
        
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        ax2.set_aspect('equal')
        ax2.set_title('CNO-Zyklus (Carbon-Nitrogen-Oxygen)', fontsize=14, 
                     color=COLOR_TEXT, weight='bold')
        ax2.axis('off')
        
        # CNO-Zyklus Elemente (im Kreis)
        elements = [
            ('¹²C', 0, '#00D9FF'),
            ('¹³N', 60, '#FF6B6B'),
            ('¹³C', 120, '#00D9FF'),
            ('¹⁴N', 180, '#FF6B6B'),
            ('¹⁵O', 240, '#FFD93D'),
            ('¹⁵N', 300, '#FF6B6B'),
        ]
        
        radius = 1.0
        active_element = int(t * len(elements)) % len(elements)
        
        for i, (elem, angle_deg, color) in enumerate(elements):
            angle = np.radians(angle_deg)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Element circle
            if t > 0.1:
                alpha = 1.0 if i == active_element else 0.5
                size = 0.25 if i == active_element else 0.2
                
                circle = Circle((x, y), size, color=color, alpha=alpha, zorder=2,
                               edgecolor=COLOR_TEXT, linewidth=2)
                ax2.add_patch(circle)
                
                # Element label
                ax2.text(x, y, elem, ha='center', va='center', fontsize=14,
                        color=COLOR_TEXT, weight='bold', zorder=3)
        
        # Arrows (Reaktionspfade)
        if t > 0.2:
            for i in range(len(elements)):
                angle1 = np.radians(elements[i][1])
                angle2 = np.radians(elements[(i+1) % len(elements)][1])
                
                x1 = radius * np.cos(angle1) * 0.75
                y1 = radius * np.sin(angle1) * 0.75
                x2 = radius * np.cos(angle2) * 0.75
                y2 = radius * np.sin(angle2) * 0.75
                
                alpha = 1.0 if i == active_element else 0.3
                
                arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                       arrowstyle='->', mutation_scale=20,
                                       color=COLOR_LAMBDA, linewidth=2, alpha=alpha,
                                       zorder=1)
                ax2.add_patch(arrow)
        
        # Center text
        if t > 0.3:
            ax2.text(0, 0, '4 ¹H → ⁴He\n+ Energie', ha='center', va='center',
                    fontsize=12, color=COLOR_TEXT, weight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=COLOR_BG,
                             edgecolor=COLOR_SSZ, linewidth=2))
        
        # ====================================================================
        # SUBPLOT 3: Element Production Timeline
        # ====================================================================
        
        ax3.set_xlim(0, 10)
        ax3.set_ylim(0, 10)
        ax3.set_title('Elemente für Leben (Timeline)', fontsize=14, 
                     color=COLOR_TEXT, weight='bold')
        ax3.set_xlabel('Zeit / Entwicklung', fontsize=11, color=COLOR_TEXT)
        ax3.set_ylabel('Atomare Masse', fontsize=11, color=COLOR_TEXT)
        
        # Timeline stages
        stages = [
            (1, 'H', 1, '#00D9FF', 'Urknall'),
            (2, 'He', 4, '#FF6B6B', 'Fusion'),
            (4, 'C', 12, '#FFD93D', 'Sterne'),
            (5, 'N', 14, '#FF6B6B', 'CNO'),
            (6, 'O', 16, '#00D9FF', 'CNO'),
            (7, 'Fe', 56, '#FF3D3D', 'Massive Sterne'),
            (9, 'Au', 197, '#FFD700', 'Supernova'),
        ]
        
        # Plot elements
        for i, (x, elem, mass, color, phase) in enumerate(stages):
            if t * 10 > x:
                # Element bar
                ax3.bar(x, mass/20, width=0.5, color=color, alpha=0.7, 
                       edgecolor=COLOR_TEXT, linewidth=1.5)
                
                # Element label
                ax3.text(x, mass/20 + 0.5, elem, ha='center', fontsize=12,
                        color=COLOR_TEXT, weight='bold')
                
                # Phase label (rotated)
                if i % 2 == 0:
                    ax3.text(x, -0.8, phase, ha='center', fontsize=9,
                            color=color, rotation=45)
        
        # Life prerequisites marker
        if t > 0.6:
            ax3.axhline(y=12/20, color=COLOR_LAMBDA, linestyle='--', 
                       linewidth=2, alpha=0.7, label='Leben: C, N, O, Fe')
            ax3.text(8, 12/20 + 0.3, '← Leben-Elemente', fontsize=10,
                    color=COLOR_LAMBDA, weight='bold')
        
        ax3.tick_params(colors=COLOR_TEXT)
        ax3.grid(True, alpha=0.2, color=COLOR_TEXT)
        
        # ====================================================================
        # SUBPLOT 4: SSZ Segment Density in Star
        # ====================================================================
        
        ax4.set_xlim(0, 10)
        ax4.set_ylim(0, 10)
        ax4.set_title('SSZ: Segment-Dichte N(r) im Stern', fontsize=14,
                     color=COLOR_TEXT, weight='bold')
        ax4.set_xlabel('Radius r/R☉', fontsize=11, color=COLOR_TEXT)
        ax4.set_ylabel('Segment-Dichte N(r)', fontsize=11, color=COLOR_TEXT)
        
        # Radial coordinate
        r = np.linspace(0.01, 10, 200)
        
        # Segment density (höher im Kern)
        K = 64  # Base resolution
        lambda_A = 0.3
        
        # Segment density: higher in core
        N_r = K * (1 + lambda_A / (r**2 + 0.1))
        
        # Plot segment density
        if t > 0.1:
            progress = min(1.0, t * 2)
            idx = int(progress * len(r))
            
            ax4.plot(r[:idx], N_r[:idx], color=COLOR_SSZ, linewidth=3,
                    label='N(r) = K(1 + λ_A/r²)')
            
            # Core region marker
            ax4.axvspan(0, 1, color=COLOR_LAMBDA, alpha=0.2, label='Fusionszone')
            
            # Lambda_A annotation
            if t > 0.5:
                ax4.text(2, 8, f'λ_A = {lambda_A}\nK = {K}',
                        fontsize=11, color=COLOR_SSZ, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor=COLOR_BG,
                                 edgecolor=COLOR_SSZ, linewidth=2))
            
            # High density region
            if t > 0.6:
                core_idx = np.where(r < 1.0)[0]
                ax4.fill_between(r[core_idx], 0, N_r[core_idx],
                                color=COLOR_LAMBDA, alpha=0.3)
                ax4.text(0.5, 5, 'Hohe\nDichte', ha='center', fontsize=10,
                        color=COLOR_TEXT, weight='bold')
        
        ax4.tick_params(colors=COLOR_TEXT)
        ax4.grid(True, alpha=0.2, color=COLOR_TEXT)
        ax4.legend(loc='upper right', fontsize=9, facecolor=COLOR_BG,
                  edgecolor=COLOR_TEXT, labelcolor=COLOR_TEXT)
        
        # ====================================================================
        # Main Title Update
        # ====================================================================
        
        if t < 0.2:
            title.set_text('Stellare Nukleosynthese – Entstehung schwerer Elemente')
        elif t < 0.5:
            title.set_text('CNO-Zyklus in Sternen – Kohlenstoff, Stickstoff, Sauerstoff')
        elif t < 0.8:
            title.set_text('Von Wasserstoff zu Eisen – Timeline der Elemente')
        else:
            title.set_text('SSZ: Segment-Dichte im Stern – Stabile Fusionszone')
        
        # Style all axes
        for ax in [ax1, ax2, ax3, ax4]:
            for spine in ax.spines.values():
                spine.set_color(COLOR_TEXT)
                spine.set_linewidth(1.5)
            ax.tick_params(colors=COLOR_TEXT, labelsize=9)
        
        return []
    
    # Create animation
    print("🎬 Erstelle Stellar Nucleosynthesis Animation...")
    print(f"   Frames: {frames}")
    print(f"   Duration: {duration}s")
    print(f"   FPS: {fps}")
    
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                  frames=frames, interval=1000/fps, blit=True)
    
    # Save
    print(f"\n💾 Speichere als {output_file}...")
    writer = animation.PillowWriter(fps=fps)
    anim.save(output_file, writer=writer, dpi=100)
    
    print(f"\n✅ Animation gespeichert: {output_file}")
    print(f"   Größe: ~{fps * duration / 10:.1f} MB (geschätzt)")
    
    plt.close()
    
    return output_file

if __name__ == '__main__':
    import sys
    import io
    
    # UTF-8 encoding fix for Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("="*80)
    print("SSZ STELLAR NUCLEOSYNTHESIS ANIMATION GENERATOR")
    print("="*80)
    print("\nErstelle Animation: Stellare Nukleosynthese")
    print("  - Stern-Struktur (Schichten, Fusionszone)")
    print("  - CNO-Zyklus (Carbon-Nitrogen-Oxygen)")
    print("  - Element-Produktion Timeline (H -> He -> C, N, O -> Fe -> Au)")
    print("  - SSZ Segment-Dichte im Sterninneren")
    print("\n" + "-"*80)
    
    output = create_stellar_nucleosynthesis_animation(
        output_file='D:/ssz_stellar_nucleosynthesis.gif',
        duration=20,
        fps=30
    )
    
    print("\n" + "="*80)
    print("✅ ANIMATION COMPLETE!")
    print("="*80)
    print(f"\nDatei: {output}")
    print("\nNächste Schritte:")
    print("  1. GIF prüfen und ggf. nach evidenz-ssz/animations/ kopieren")
    print("  2. Video-Producer mit Part 4 + Part 5 erweitern")
    print("  3. Edge-TTS Audio generieren für alle 5 Teile")
    print("\n" + "="*80)
