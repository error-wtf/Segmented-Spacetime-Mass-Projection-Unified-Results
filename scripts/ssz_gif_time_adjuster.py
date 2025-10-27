#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ GIF Time Adjuster - Passt existierende GIFs an Audio-Längen an

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import subprocess
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

def get_gif_duration(gif_path: Path) -> float:
    """Ermittelt Dauer eines GIFs mit ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(gif_path)],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"ERROR: Konnte GIF-Dauer nicht ermitteln: {e}")
        return 0.0

def adjust_gif_speed(
    input_gif: Path,
    target_duration: float,
    output_gif: Path
) -> None:
    """
    Passt GIF-Geschwindigkeit an Ziel-Dauer an.
    
    Args:
        input_gif: Existierendes GIF
        target_duration: Ziel-Dauer in Sekunden (Audio-Länge)
        output_gif: Output GIF-Pfad
    """
    # Aktuelle Dauer ermitteln
    current_duration = get_gif_duration(input_gif)
    
    if current_duration == 0:
        raise ValueError(f"Konnte Dauer von {input_gif} nicht ermitteln!")
    
    # Speed-Faktor berechnen
    speed_factor = current_duration / target_duration
    
    print(f"\n{'='*70}")
    print(f"GIF SPEED ADJUSTMENT")
    print(f"{'='*70}")
    print(f"Input: {input_gif.name}")
    print(f"Current Duration: {current_duration:.2f}s")
    print(f"Target Duration: {target_duration:.2f}s")
    print(f"Speed Factor: {speed_factor:.3f}x")
    print(f"Output: {output_gif.name}")
    
    # ffmpeg Kommando
    # setpts = Set Presentation TimeStamp
    # PTS * speed_factor -> langsamer wenn > 1, schneller wenn < 1
    cmd = [
        'ffmpeg',
        '-i', str(input_gif),
        '-vf', f'setpts={speed_factor}*PTS',
        '-y',  # Overwrite
        str(output_gif)
    ]
    
    print(f"\nAdjusting speed...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Verifiziere neue Dauer
        new_duration = get_gif_duration(output_gif)
        print(f"✓ New Duration: {new_duration:.2f}s")
        
        # Prüfe ob nah genug
        diff = abs(new_duration - target_duration)
        if diff > 0.5:
            print(f"⚠️  WARNING: Duration difference: {diff:.2f}s")
        else:
            print(f"✓ Duration match: ±{diff:.2f}s")
        
        size_mb = output_gif.stat().st_size / (1024 * 1024)
        print(f"✓ Output size: {size_mb:.1f} MB")
        print(f"{'='*70}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: ffmpeg failed!")
        print(f"STDERR: {e.stderr}")
        raise

def adjust_gifs_for_audio(
    input_gifs: dict,
    audio_durations: dict,
    output_dir: Path
) -> dict:
    """
    Passt mehrere GIFs an mehrere Audio-Längen an.
    
    Args:
        input_gifs: {'part2': Path, 'part3': Path}
        audio_durations: {'part2': {'de': 55.0, 'en': 52.0, 'it': 58.0}, ...}
        output_dir: Output-Verzeichnis
    
    Returns:
        Dict mit allen angepassten GIF-Pfaden
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    adjusted_gifs = {}
    
    for part, input_gif in input_gifs.items():
        if part not in audio_durations:
            print(f"⚠️  No audio durations for {part}, skipping...")
            continue
        
        adjusted_gifs[part] = {}
        
        for lang, duration in audio_durations[part].items():
            output_gif = output_dir / f'{part}_{lang}.gif'
            
            adjust_gif_speed(
                input_gif=input_gif,
                target_duration=duration,
                output_gif=output_gif
            )
            
            adjusted_gifs[part][lang] = output_gif
    
    return adjusted_gifs

# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Adjust GIF speed to match audio duration')
    parser.add_argument('--input', type=Path, required=True, help='Input GIF')
    parser.add_argument('--duration', type=float, required=True, help='Target duration (seconds)')
    parser.add_argument('--output', type=Path, required=True, help='Output GIF')
    
    args = parser.parse_args()
    
    adjust_gif_speed(
        input_gif=args.input,
        target_duration=args.duration,
        output_gif=args.output
    )
