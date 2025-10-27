#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Final Video Producer - High Quality Trilingual Videos
Erstellt professionelle Videos mit angepassten GIF-Längen und High-Quality Audio

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Dict, List, Optional

# Import der finalen Scripts
from ssz_video_scripts_final import (
    PART1_SCRIPTS, PART2_SCRIPTS, PART3_SCRIPTS,
    VIDEO_CONFIG, AUDIO_CONFIG
)


def setup_utf8():
    """UTF-8 Encoding für Windows."""
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def check_dependencies() -> Dict[str, bool]:
    """Prüft verfügbare Tools."""
    import shutil
    deps = {
        'ffmpeg': shutil.which('ffmpeg') is not None,
        'ffprobe': shutil.which('ffprobe') is not None,
        'edge-tts': shutil.which('edge-tts') is not None
    }
    return deps


def get_gif_duration(gif_path: Path) -> Optional[float]:
    """Ermittelt die Dauer eines GIF."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(gif_path)
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return float(result.stdout.strip())
    except:
        return None


def generate_audio_segment(
    text: str,
    output_path: Path,
    language: str,
    voice: str
) -> bool:
    """Generiert ein Audio-Segment mit edge-tts (High Quality)."""
    
    cmd = [
        'edge-tts',
        '--voice', voice,
        '--text', text,
        '--write-media', str(output_path),
        '--rate', AUDIO_CONFIG['rate'],
        '--pitch', AUDIO_CONFIG['pitch'],
        '--volume', AUDIO_CONFIG['volume']
    ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return output_path.exists() and output_path.stat().st_size > 0
    except:
        return False


def create_part_audio(
    part_scripts: Dict,
    language: str,
    output_dir: Path,
    part_name: str
) -> Optional[Path]:
    """Erstellt das komplette Audio für einen Part."""
    
    voice = AUDIO_CONFIG['voices'][language]
    segments = part_scripts[language]['segments']
    total_duration = part_scripts[language]['total_duration']
    
    # Audio-Segmente generieren
    temp_files = []
    for i, segment in enumerate(segments):
        temp_path = output_dir / f"{part_name}_{language}_seg{i}.mp3"
        if generate_audio_segment(segment['text'], temp_path, language, voice):
            temp_files.append((segment['time'], temp_path))
        else:
            print(f"  ⚠️  Segment {i} konnte nicht erstellt werden")
    
    if not temp_files:
        return None
    
    # Audio zu WAV konvertieren und zusammenführen
    final_audio = output_dir / f"{part_name}_{language}_audio.wav"
    
    # Erstelle stilles Audio als Basis
    silent_audio = output_dir / f"{part_name}_{language}_silent.wav"
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i',
        f'anullsrc=r={AUDIO_CONFIG["sample_rate"]}:cl=stereo',
        '-t', str(total_duration),
        '-y', str(silent_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Mixe alle Segmente zusammen
    filter_complex = []
    inputs = ['-i', str(silent_audio)]
    
    for idx, (start_time, audio_file) in enumerate(temp_files):
        inputs.extend(['-i', str(audio_file)])
        filter_complex.append(f'[{idx+1}]adelay={int(start_time*1000)}|{int(start_time*1000)}[a{idx}]')
    
    # Combine all
    mix_inputs = '[0]' + ''.join([f'[a{i}]' for i in range(len(temp_files))])
    filter_complex.append(f'{mix_inputs}amix=inputs={len(temp_files)+1}:duration=longest[out]')
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filter_complex),
        '-map', '[out]',
        '-ar', str(AUDIO_CONFIG['sample_rate']),
        '-ac', str(AUDIO_CONFIG['channels']),
        str(final_audio)
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup temp files
    for _, temp_file in temp_files:
        temp_file.unlink(missing_ok=True)
    silent_audio.unlink(missing_ok=True)
    
    return final_audio if final_audio.exists() else None


def adjust_gif_to_audio(
    gif_path: Path,
    audio_duration: float,
    output_path: Path
) -> bool:
    """Passt GIF-Länge an Audio-Dauer an (stretching/looping)."""
    
    gif_duration = get_gif_duration(gif_path)
    if not gif_duration:
        print(f"  ⚠️  Konnte GIF-Dauer nicht ermitteln: {gif_path.name}")
        return False
    
    print(f"  GIF: {gif_duration:.1f}s → Audio: {audio_duration:.1f}s")
    
    if audio_duration > gif_duration:
        # Loop GIF bis Audio-Ende
        loops = int(audio_duration / gif_duration) + 1
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', str(loops),
            '-i', str(gif_path),
            '-t', str(audio_duration),
            '-vf', 'scale=1920:1080:flags=lanczos',
            '-r', '30',
            str(output_path)
        ]
    else:
        # Stretch GIF auf Audio-Länge
        speed_factor = gif_duration / audio_duration
        cmd = [
            'ffmpeg', '-y',
            '-i', str(gif_path),
            '-vf', f'setpts={speed_factor}*PTS,scale=1920:1080:flags=lanczos',
            '-r', '30',
            str(output_path)
        ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return output_path.exists()
    except:
        return False


def create_final_video(
    gif_path: Path,
    audio_path: Path,
    output_path: Path
) -> bool:
    """Kombiniert GIF und Audio zu finalem Video (High Quality)."""
    
    cmd = [
        'ffmpeg', '-y',
        '-i', str(gif_path),
        '-i', str(audio_path),
        '-c:v', 'libx264',
        '-preset', 'slow',  # Beste Qualität
        '-crf', '18',  # High quality (0-51, niedriger = besser)
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '320k',  # High quality audio
        '-ar', str(AUDIO_CONFIG['sample_rate']),
        '-shortest',
        str(output_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return output_path.exists()
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False


def concatenate_parts(
    part1_video: Path,
    part2_video: Path,
    part3_video: Path,
    output_path: Path
) -> bool:
    """Konkateniert die drei Teile zu einem finalen Video."""
    
    # Erstelle concat-Liste
    concat_file = output_path.parent / f"concat_{output_path.stem}.txt"
    with open(concat_file, 'w', encoding='utf-8') as f:
        f.write(f"file '{part1_video.absolute()}'\n")
        f.write(f"file '{part2_video.absolute()}'\n")
        f.write(f"file '{part3_video.absolute()}'\n")
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(output_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        concat_file.unlink(missing_ok=True)
        return output_path.exists()
    except:
        return False


def produce_language(language: str, gif_dir: Path, output_dir: Path, temp_dir: Path):
    """Produziert alle Videos für eine Sprache."""
    
    print(f"\n{'='*80}")
    print(f"🎬 PRODUKTION: {language.upper()}")
    print(f"{'='*80}")
    
    part_videos = []
    
    for part_num, (part_name, part_scripts, gif_template) in enumerate([
        ('part1_intro', PART1_SCRIPTS, VIDEO_CONFIG['part1']['gif_source']),
        ('part2_cosmo', PART2_SCRIPTS, VIDEO_CONFIG['part2']['gif_source']),
        ('part3_stability', PART3_SCRIPTS, VIDEO_CONFIG['part3']['gif_source'])
    ], 1):
        
        print(f"\n--- Teil {part_num}: {part_name} ---")
        
        # 1. Audio erstellen
        print(f"  🎙️  Audio generieren...")
        audio_path = create_part_audio(part_scripts, language, temp_dir, part_name)
        if not audio_path:
            print(f"  ❌ Audio-Erstellung fehlgeschlagen")
            continue
        print(f"  ✅ Audio: {audio_path.name}")
        
        # 2. GIF-Pfad bestimmen
        gif_filename = gif_template.format(lang=language)
        gif_path = gif_dir / gif_filename
        if not gif_path.exists():
            print(f"  ❌ GIF nicht gefunden: {gif_path}")
            continue
        
        # 3. GIF an Audio anpassen
        print(f"  🎞️  GIF anpassen...")
        adjusted_gif = temp_dir / f"{part_name}_{language}_adjusted.mp4"
        audio_duration = part_scripts[language]['total_duration']
        if not adjust_gif_to_audio(gif_path, audio_duration, adjusted_gif):
            print(f"  ❌ GIF-Anpassung fehlgeschlagen")
            continue
        
        # 4. Video erstellen
        print(f"  🎥 Video rendern...")
        part_video = output_dir / f"ssz_{part_name}_{language}.mp4"
        if not create_final_video(adjusted_gif, audio_path, part_video):
            print(f"  ❌ Video-Erstellung fehlgeschlagen")
            continue
        
        print(f"  ✅ {part_video.name}")
        part_videos.append(part_video)
    
    # 5. Alle Teile zusammenführen
    if len(part_videos) == 3:
        print(f"\n  🔗 Finale Zusammenführung...")
        final_video = output_dir / f"ssz_complete_{language}.mp4"
        if concatenate_parts(part_videos[0], part_videos[1], part_videos[2], final_video):
            print(f"  ✅ FINALE VIDEO: {final_video.name}")
            size_mb = final_video.stat().st_size / (1024*1024)
            print(f"     Größe: {size_mb:.1f} MB")
        else:
            print(f"  ❌ Zusammenführung fehlgeschlagen")
    else:
        print(f"  ⚠️  Nicht alle Teile verfügbar ({len(part_videos)}/3)")


def main():
    setup_utf8()
    
    print("="*80)
    print("SSZ FINAL VIDEO PRODUCER - HIGH QUALITY")
    print("="*80)
    
    # Verzeichnisse
    gif_dir = Path("D:/")
    output_dir = Path("D:/SSZ_Final_Videos")
    temp_dir = Path("D:/SSZ_Temp")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Dependencies prüfen
    deps = check_dependencies()
    print("\nAbhängigkeiten:")
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {name}")
    
    if not all(deps.values()):
        print("\n❌ Nicht alle Abhängigkeiten verfügbar!")
        print("   Installation: pip install edge-tts")
        print("   FFmpeg: https://ffmpeg.org/download.html")
        return 1
    
    # Produktion für alle Sprachen
    for lang in ['de', 'en', 'it']:
        produce_language(lang, gif_dir, output_dir, temp_dir)
    
    print("\n" + "="*80)
    print("✅ PRODUKTION ABGESCHLOSSEN")
    print("="*80)
    print(f"Output: {output_dir}")
    print("\nDateien:")
    for video_file in sorted(output_dir.glob("ssz_complete_*.mp4")):
        size_mb = video_file.stat().st_size / (1024*1024)
        print(f"  • {video_file.name} ({size_mb:.1f} MB)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
