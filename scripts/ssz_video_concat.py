#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Video Concatenation - ffmpeg Wrapper für Video-Erstellung

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# ============================================================================
# VIDEO FUNCTIONS
# ============================================================================

def gif_to_mp4_with_audio(
    gif_path: Path,
    audio_path: Path,
    output_path: Path,
    crf: int = 18,
    preset: str = 'slow',
    audio_bitrate: str = '320k',
    resolution: Optional[tuple] = None
) -> None:
    """
    Konvertiert GIF zu MP4 mit Audio.
    
    Args:
        gif_path: Input GIF
        audio_path: Input Audio (WAV)
        output_path: Output MP4
        crf: Quality (18 = high, 23 = medium, 28 = low)
        preset: Encoding speed (slow = best quality)
        audio_bitrate: Audio bitrate
        resolution: Optional (width, height) für Resize
    """
    cmd = [
        'ffmpeg',
        '-i', str(gif_path),      # Video input
        '-i', str(audio_path),    # Audio input
        '-c:v', 'libx264',        # Video codec
        '-preset', preset,
        '-crf', str(crf),
        '-pix_fmt', 'yuv420p',    # Kompatibilität
        '-c:a', 'aac',            # Audio codec
        '-b:a', audio_bitrate,
        '-ar', '48000',           # Sample rate
        '-shortest',              # Stop wenn kürzere Spur endet
    ]
    
    # Optional: Resolution anpassen
    if resolution:
        width, height = resolution
        cmd.extend(['-vf', f'scale={width}:{height}'])
    
    cmd.extend(['-y', str(output_path)])
    
    print(f"  → ffmpeg: {gif_path.name} + {audio_path.name} → {output_path.name}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"  ✓ {output_path.name} erstellt")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: ffmpeg failed!")
        print(f"STDERR: {e.stderr}")
        raise

def concat_videos(video_paths: List[Path], output_path: Path) -> None:
    """
    Concateniert mehrere MP4-Videos zu einem.
    
    Args:
        video_paths: Liste von Input-MP4s (in Reihenfolge)
        output_path: Output MP4
    """
    # Erstelle concat.txt
    concat_file = output_path.parent / f'concat_{output_path.stem}.txt'
    
    with open(concat_file, 'w', encoding='utf-8') as f:
        for video_path in video_paths:
            # ffmpeg braucht relatives oder absolutes Pfad-Format
            f.write(f"file '{video_path.absolute()}'\n")
    
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',  # Kein Re-Encoding (schnell!)
        '-y', str(output_path)
    ]
    
    print(f"  → ffmpeg concat: {len(video_paths)} videos → {output_path.name}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"  ✓ {output_path.name} erstellt")
        
        # Lösche temp concat file
        concat_file.unlink()
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: ffmpeg concat failed!")
        print(f"STDERR: {e.stderr}")
        raise

def extract_audio_from_video(video_path: Path, audio_path: Path) -> None:
    """Extrahiert Audio aus Video"""
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-vn',  # No video
        '-acodec', 'pcm_s16le',  # PCM WAV
        '-ar', '48000',
        '-y', str(audio_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Audio extraction failed: {e}")
        raise

def get_video_info(video_path: Path) -> dict:
    """Ermittelt Video-Informationen mit ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate,duration',
        '-of', 'json',
        str(video_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        import json
        data = json.loads(result.stdout)
        
        stream = data['streams'][0]
        
        # FPS berechnen (ist als Bruch: "30/1")
        fps_str = stream['r_frame_rate']
        num, den = map(int, fps_str.split('/'))
        fps = num / den
        
        return {
            'width': stream['width'],
            'height': stream['height'],
            'fps': fps,
            'duration': float(stream.get('duration', 0))
        }
        
    except Exception as e:
        print(f"ERROR getting video info: {e}")
        return {}

def create_thumbnail(video_path: Path, output_path: Path, timestamp: str = '00:00:01') -> None:
    """Erstellt Thumbnail aus Video"""
    cmd = [
        'ffmpeg',
        '-ss', timestamp,
        '-i', str(video_path),
        '-vframes', '1',
        '-vf', 'scale=640:-1',  # 640px breit, Höhe proportional
        '-y', str(output_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        print(f"  ✓ Thumbnail: {output_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Thumbnail creation failed: {e}")

def optimize_for_web(input_path: Path, output_path: Path, max_size_mb: float = 50) -> None:
    """
    Optimiert Video für Web (kleinere Dateigröße).
    
    Args:
        input_path: Input MP4
        output_path: Output MP4 (optimiert)
        max_size_mb: Maximale Dateigröße in MB
    """
    # Ermittle Video-Dauer
    info = get_video_info(input_path)
    duration = info.get('duration', 0)
    
    if duration == 0:
        print("WARNING: Konnte Duration nicht ermitteln, nutze Standard-Bitrate")
        video_bitrate = '2000k'
    else:
        # Berechne Bitrate für Ziel-Größe
        # Formel: bitrate = (file_size_bits / duration_seconds) - audio_bitrate
        target_bits = max_size_mb * 1024 * 1024 * 8  # MB → bits
        audio_bitrate_bits = 320 * 1000  # 320kbps → bps
        video_bitrate_bits = (target_bits / duration) - audio_bitrate_bits
        video_bitrate = f"{int(video_bitrate_bits / 1000)}k"
    
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-c:v', 'libx264',
        '-b:v', video_bitrate,
        '-maxrate', video_bitrate,
        '-bufsize', f"{int(float(video_bitrate[:-1]) * 2)}k",
        '-preset', 'slow',
        '-c:a', 'aac',
        '-b:a', '192k',  # Niedrigere Audio-Bitrate für Web
        '-movflags', '+faststart',  # Optimierung für Streaming
        '-y', str(output_path)
    ]
    
    print(f"  → Web-Optimierung: Target {max_size_mb}MB, Bitrate {video_bitrate}")
    
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        final_size = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {output_path.name} ({final_size:.1f} MB)")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Web optimization failed: {e}")
        raise

# ============================================================================
# TEST
# ============================================================================

def test_video_functions():
    """Test-Funktion"""
    print("\n" + "=" * 70)
    print("VIDEO CONCAT TEST")
    print("=" * 70)
    
    # TODO: Implementiere Tests wenn Test-Dateien vorhanden
    print("Test-Funktionen verfügbar:")
    print("  - gif_to_mp4_with_audio()")
    print("  - concat_videos()")
    print("  - get_video_info()")
    print("  - create_thumbnail()")
    print("  - optimize_for_web()")

if __name__ == '__main__':
    if '--test' in sys.argv:
        test_video_functions()
    else:
        print("Video Concat Wrapper - Import this module in ssz_trilingual_master.py")
