#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Video Renderer - Generates visual animations from YAML timelines
NO TEXT OVERLAYS - Pure visual storytelling

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, FFMpegWriter
from pathlib import Path
import yaml
from typing import Dict, Tuple

# UTF-8 setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Physics constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
C_LIGHT = 299792458.0  # m/s

# ============================================================================
# VISUAL ELEMENTS
# ============================================================================

class BigBangAnimation:
    """Left panel: Classical ΛCDM Big Bang visualization"""
    
    def __init__(self, width=0.48, height=1.0):
        self.width = width
        self.height = height
        self.colors = ['#ffcc00', '#ff6600', '#ff3300', '#441144']
        
    def render_frame(self, ax, t_norm: float):
        """Render single frame at normalized time t_norm ∈ [0,1]"""
        ax.clear()
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.axis('off')
        
        # Background gradient
        gradient = np.linspace(0, 1, 256).reshape(256, 1)
        ax.imshow(
            gradient,
            extent=[0, self.width, 0, self.height],
            aspect='auto',
            cmap=plt.cm.twilight,
            alpha=0.3
        )
        
        # Radial explosion from center
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Expanding particles
        n_particles = 150
        expansion_factor = t_norm ** 0.7  # Slower initial expansion
        
        for i in range(n_particles):
            angle = 2 * np.pi * i / n_particles + t_norm * 0.5
            radius = expansion_factor * 0.4 * self.width
            
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            # Color shifts with time
            color_idx = int((i / n_particles + t_norm) * len(self.colors)) % len(self.colors)
            color = self.colors[color_idx]
            
            # Size decreases with distance
            size = 50 * (1 - expansion_factor * 0.8)
            
            ax.scatter(x, y, c=color, s=size, alpha=0.6)
        
        # Central glow (singularity)
        if t_norm < 0.3:
            glow_size = 2000 * (1 - t_norm / 0.3)
            ax.scatter(
                center_x, center_y,
                c='#ffffff',
                s=glow_size,
                alpha=0.5 * (1 - t_norm / 0.3)
            )


class SSZSegmentedAnimation:
    """Right panel: Segmented Spacetime with φ-spiral"""
    
    def __init__(self, width=0.48, height=1.0):
        self.width = width
        self.height = height
        self.colors = ['#00ccff', '#1a1f2b', '#f7b733', '#4ecdc4']
        
    def render_frame(self, ax, t_norm: float):
        """Render segmented spacetime with φ-based structure"""
        ax.clear()
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.axis('off')
        
        # Background
        ax.set_facecolor('#0a1f2e')
        
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Hexagonal segment grid
        n_rings = 5
        hex_radius = 0.05 * self.width
        
        for ring in range(n_rings):
            ring_radius = (ring + 1) * hex_radius * 1.5
            n_segments = 6 * max(ring, 1)
            
            for i in range(n_segments):
                angle = 2 * np.pi * i / n_segments + t_norm * 0.3
                x = center_x + ring_radius * np.cos(angle)
                y = center_y + ring_radius * np.sin(angle)
                
                # Hexagon vertices
                hex_angles = np.linspace(0, 2*np.pi, 7) + angle
                hex_x = x + hex_radius * np.cos(hex_angles)
                hex_y = y + hex_radius * np.sin(hex_angles)
                
                # Color based on ring and phase
                color_idx = (ring + int(t_norm * 10)) % len(self.colors)
                color = self.colors[color_idx]
                
                alpha = 0.3 + 0.2 * np.sin(t_norm * 2 * np.pi + ring)
                
                ax.fill(hex_x, hex_y, color=color, alpha=alpha, edgecolor='#ffffff', linewidth=0.5)
        
        # φ-Spiral overlay
        theta = np.linspace(0, 4 * np.pi, 500)
        r = 0.05 * self.width * PHI ** (theta / (2 * np.pi) - 2)
        
        # Rotate with time
        rotation = t_norm * 2 * np.pi
        spiral_x = center_x + r * np.cos(theta + rotation)
        spiral_y = center_y + r * np.sin(theta + rotation)
        
        # Gradient along spiral
        colors_spiral = plt.cm.viridis(np.linspace(0, 1, len(spiral_x)))
        
        for i in range(len(spiral_x) - 1):
            ax.plot(
                spiral_x[i:i+2],
                spiral_y[i:i+2],
                color=colors_spiral[i],
                linewidth=2,
                alpha=0.7
            )
        
        # Orbital particles
        n_particles = 80
        for i in range(n_particles):
            orbit_angle = 2 * np.pi * i / n_particles + t_norm * 4 * np.pi
            orbit_radius = 0.15 * self.width * (1 + 0.3 * np.sin(t_norm * 2 * np.pi))
            
            px = center_x + orbit_radius * np.cos(orbit_angle)
            py = center_y + orbit_radius * np.sin(orbit_angle)
            
            ax.scatter(px, py, c='#f7b733', s=30, alpha=0.8, edgecolors='white', linewidths=0.5)


# ============================================================================
# MAIN RENDERER
# ============================================================================

def render_dual_panel_video(
    output_file: Path,
    audio_file: Path,
    duration_s: float,
    fps: int = 30
):
    """Render dual-panel animation with synchronized audio"""
    
    print(f"Rendering video:")
    print(f"  Duration: {duration_s:.2f}s @ {fps} fps")
    print(f"  Frames: {int(duration_s * fps)}")
    
    # Setup figure
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor='black')
    
    # Left panel (ΛCDM)
    ax_left = fig.add_axes([0.00, 0.00, 0.48, 1.00])
    bigbang = BigBangAnimation()
    
    # Right panel (SSZ)
    ax_right = fig.add_axes([0.52, 0.00, 0.48, 1.00])
    ssz = SSZSegmentedAnimation()
    
    # Divider
    ax_div = fig.add_axes([0.48, 0.00, 0.04, 1.00])
    ax_div.axis('off')
    gradient_div = np.linspace(0, 1, 256).reshape(1, 256)
    ax_div.imshow(
        gradient_div,
        extent=[0, 1, 0, 1],
        aspect='auto',
        cmap=plt.cm.gray,
        alpha=0.5
    )
    
    total_frames = int(duration_s * fps)
    
    def update_frame(frame_num):
        """Update animation frame"""
        t_norm = frame_num / total_frames
        
        # Render both panels
        bigbang.render_frame(ax_left, t_norm)
        ssz.render_frame(ax_right, t_norm)
        
        # Progress indicator
        if frame_num % 30 == 0:
            print(f"  Frame {frame_num}/{total_frames} ({100*t_norm:.1f}%)")
        
        return ax_left, ax_right
    
    # Create animation
    anim = FuncAnimation(
        fig,
        update_frame,
        frames=total_frames,
        interval=1000/fps,
        blit=False
    )
    
    # Save as video (no audio yet)
    temp_video = output_file.with_suffix('.temp.mp4')
    
    writer = FFMpegWriter(
        fps=fps,
        codec='libx264',
        bitrate=18000,
        extra_args=['-pix_fmt', 'yuv420p']
    )
    
    print("  Writing video frames...")
    anim.save(str(temp_video), writer=writer, dpi=100)
    plt.close(fig)
    
    print("  Adding audio track...")
    # Merge video + audio with ffmpeg
    import subprocess
    subprocess.run([
        'ffmpeg',
        '-i', str(temp_video),
        '-i', str(audio_file),
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        '-y', str(output_file)
    ], check=True, capture_output=True)
    
    # Cleanup temp file
    temp_video.unlink()
    
    print(f"✓ Video saved: {output_file}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='SSZ Video Renderer - Generate visual animations'
    )
    parser.add_argument('--language', required=True, choices=['de', 'en', 'it'])
    parser.add_argument('--timeline', type=Path, required=True)
    parser.add_argument('--audio', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--duration', type=float, required=True)
    parser.add_argument('--fps', type=int, default=30)
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"SSZ Video Renderer - {args.language.upper()}")
    print(f"{'='*70}")
    
    # Verify inputs
    if not args.timeline.exists():
        print(f"✗ Timeline not found: {args.timeline}")
        return 1
    
    if not args.audio.exists():
        print(f"✗ Audio not found: {args.audio}")
        return 1
    
    # Render video
    try:
        render_dual_panel_video(
            args.output,
            args.audio,
            args.duration,
            args.fps
        )
        return 0
    except Exception as e:
        print(f"✗ Rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
