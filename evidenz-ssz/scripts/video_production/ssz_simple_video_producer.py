#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Simple Video Producer - Nutzt existierende Tools (imageio)
Erstellt Videos aus vorhandenen GIFs mit High-Quality Audio

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np

try:
    import imageio.v2 as imageio
except:
    import imageio

from ssz_video_scripts_final import (
    PART1_SCRIPTS, PART2_SCRIPTS, PART3_SCRIPTS, AUDIO_CONFIG
)


def setup_utf8():
    """UTF-8 für Windows."""
    os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def generate_audio_with_edge_tts(text: str, output_path: Path, voice: str) -> bool:
    """Generiert Audio mit edge-tts."""
    
    # Mögliche Pfade zu edge-tts
    possible_paths = [
        Path(os.path.expanduser('~')) / "AppData" / "Roaming" / "Python" / "Python310" / "Scripts" / "edge-tts.exe",
        Path(sys.executable).parent / "Scripts" / "edge-tts.exe",
        Path(sys.executable).parent / "edge-tts.exe",
    ]
    
    edge_tts_path = None
    for path in possible_paths:
        if path.exists():
            edge_tts_path = path
            break
    
    if edge_tts_path:
        cmd = [
            str(edge_tts_path),
            '--voice', voice,
            '--text', text,
            '--write-media', str(output_path)
        ]
    else:
        # Fallback: versuche es über PATH
        cmd = [
            'edge-tts',
            '--voice', voice,
            '--text', text,
            '--write-media', str(output_path)
        ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='replace'
        )
        return output_path.exists() and output_path.stat().st_size > 0
    except Exception as e:
        print(f"  ⚠️  Audio-Generierung fehlgeschlagen: {e}")
        return False


def create_complete_audio(
    part_scripts: dict,
    language: str,
    output_path: Path
) -> bool:
    """Erstellt komplettes Audio für einen Part (alle Segmente zusammen)."""
    
    voice = AUDIO_CONFIG['voices'][language]
    segments = part_scripts[language]['segments']
    
    # Kombiniere alle Texte mit Pausen
    combined_text = ""
    for i, segment in enumerate(segments):
        combined_text += segment['text']
        if i < len(segments) - 1:
            combined_text += " ... "  # Pause zwischen Segmenten
    
    print(f"  🎙️  Audio generieren: {len(combined_text)} Zeichen")
    return generate_audio_with_edge_tts(combined_text, output_path, voice)


def load_gif_as_frames(gif_path: Path, target_fps: int = 30) -> list:
    """Lädt GIF als Frame-Liste."""
    
    print(f"  📂 Lade GIF: {gif_path.name}")
    
    try:
        reader = imageio.get_reader(gif_path)
        frames = []
        for frame in reader:
            # Konvertiere zu RGB falls nötig
            if len(frame.shape) == 2:  # Grayscale
                frame = np.stack([frame]*3, axis=-1)
            elif frame.shape[2] == 4:  # RGBA
                frame = frame[:, :, :3]
            frames.append(frame)
        reader.close()
        print(f"     {len(frames)} Frames geladen")
        return frames
    except Exception as e:
        print(f"  ❌ Fehler beim Laden: {e}")
        return []


def adjust_frames_to_duration(frames: list, original_fps: int, target_duration: float, target_fps: int = 30) -> list:
    """Passt Frames an Ziel-Duration an (Loop oder Stretch)."""
    
    current_duration = len(frames) / original_fps
    target_frame_count = int(target_duration * target_fps)
    
    print(f"  ⏱️  Anpassung: {current_duration:.1f}s → {target_duration:.1f}s")
    print(f"     Frames: {len(frames)} → {target_frame_count}")
    
    if target_frame_count > len(frames):
        # Loop: Wiederhole Frames
        result = []
        while len(result) < target_frame_count:
            result.extend(frames)
        return result[:target_frame_count]
    else:
        # Stretch: Sample Frames
        indices = np.linspace(0, len(frames)-1, target_frame_count).astype(int)
        return [frames[i] for i in indices]


def create_video_with_audio(
    frames: list,
    audio_path: Path,
    output_path: Path,
    fps: int = 30
) -> bool:
    """Erstellt Video aus Frames (ohne Audio) mit imageio."""
    
    print(f"  🎥 Video erstellen (stumm): {output_path.name}")
    
    try:
        # Erstelle stummes Video
        silent_path = output_path.with_suffix('.silent.mp4')
        
        writer = imageio.get_writer(
            silent_path,
            fps=fps,
            codec='libx264',
            quality=8,  # High quality (0-10)
            pixelformat='yuv420p',
            macro_block_size=None
        )
        
        for frame in frames:
            writer.append_data(frame)
        
        writer.close()
        
        # Prüfe ob ffmpeg verfügbar ist für Audio-Merging
        try:
            import subprocess
            import shutil
            
            if shutil.which('ffmpeg'):
                # Merge Audio mit ffmpeg
                cmd = [
                    'ffmpeg', '-y',
                    '-i', str(silent_path),
                    '-i', str(audio_path),
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-shortest',
                    str(output_path)
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                silent_path.unlink()  # Lösche stummes Video
                print(f"  ✅ Video mit Audio: {output_path.name}")
            else:
                # Behalte stummes Video, Audio ist separat
                silent_path.rename(output_path)
                print(f"  ✅ Stummes Video: {output_path.name}")
                print(f"      Audio separat: {audio_path.name}")
                print(f"      (ffmpeg nicht verfügbar für Audio-Merging)")
        except:
            # Fallback: Stummes Video
            silent_path.rename(output_path)
            print(f"  ✅ Stummes Video: {output_path.name}")
            print(f"      Audio separat: {audio_path.name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Video-Erstellung fehlgeschlagen: {e}")
        return False


def produce_part(
    part_name: str,
    part_scripts: dict,
    gif_path: Path,
    language: str,
    output_dir: Path,
    temp_dir: Path
) -> Path:
    """Produziert ein Part-Video."""
    
    print(f"\n  --- {part_name.upper()} ---")
    
    # 1. Audio erstellen
    audio_path = temp_dir / f"{part_name}_{language}.mp3"
    if not create_complete_audio(part_scripts, language, audio_path):
        return None
    
    # 2. GIF laden
    frames = load_gif_as_frames(gif_path)
    if not frames:
        return None
    
    # 3. Frames an Audio-Duration anpassen
    target_duration = part_scripts[language]['total_duration']
    original_fps = 30  # Annahme für GIFs
    adjusted_frames = adjust_frames_to_duration(frames, original_fps, target_duration, 30)
    
    # 4. Video mit Audio erstellen
    output_video = output_dir / f"ssz_{part_name}_{language}.mp4"
    if create_video_with_audio(adjusted_frames, audio_path, output_video, fps=30):
        return output_video
    
    return None


def concatenate_videos_simple(video_paths: list, output_path: Path) -> bool:
    """Konkateniert Videos (einfache Methode mit imageio)."""
    
    print(f"\n  🔗 Zusammenführen zu: {output_path.name}")
    
    try:
        all_frames = []
        for video_path in video_paths:
            print(f"     Lade: {video_path.name}")
            reader = imageio.get_reader(video_path)
            for frame in reader:
                all_frames.append(frame)
            reader.close()
        
        print(f"     Gesamt: {len(all_frames)} Frames")
        
        writer = imageio.get_writer(
            output_path,
            fps=30,
            codec='libx264',
            quality=8,
            pixelformat='yuv420p'
        )
        
        for frame in all_frames:
            writer.append_data(frame)
        
        writer.close()
        print(f"  ✅ Finale Video: {output_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Zusammenführung fehlgeschlagen: {e}")
        return False


def produce_language(language: str, gif_dir: Path, output_dir: Path, temp_dir: Path):
    """Produziert alle Videos für eine Sprache."""
    
    print(f"\n{'='*80}")
    print(f"🎬 PRODUKTION: {language.upper()}")
    print(f"{'='*80}")
    
    # GIF-Pfade
    gif_paths = {
        'part1': gif_dir / f"ssz_scientific_{language}.gif",
        'part2': gif_dir / "ssz_cosmo_anim.gif",
        'part3': gif_dir / "ssz_proof_anim_v6.gif"
    }
    
    # Prüfe GIF-Verfügbarkeit
    for part, path in gif_paths.items():
        if not path.exists():
            print(f"  ⚠️  {part}: {path.name} nicht gefunden")
    
    # Produziere Parts
    part_videos = []
    
    for (part_name, part_scripts, gif_key) in [
        ('part1_intro', PART1_SCRIPTS, 'part1'),
        ('part2_cosmo', PART2_SCRIPTS, 'part2'),
        ('part3_stability', PART3_SCRIPTS, 'part3')
    ]:
        gif_path = gif_paths[gif_key]
        if not gif_path.exists():
            continue
        
        video = produce_part(part_name, part_scripts, gif_path, language, output_dir, temp_dir)
        if video:
            part_videos.append(video)
    
    # Zusammenführen
    if len(part_videos) == 3:
        final_video = output_dir / f"ssz_complete_{language}.mp4"
        concatenate_videos_simple(part_videos, final_video)
    else:
        print(f"\n  ⚠️  Nicht alle Teile erstellt ({len(part_videos)}/3)")


def main():
    setup_utf8()
    
    print("="*80)
    print("SSZ SIMPLE VIDEO PRODUCER")
    print("="*80)
    
    gif_dir = Path("D:/")
    output_dir = Path("D:/SSZ_Final_Videos")
    temp_dir = Path("D:/SSZ_Temp")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nVerzeichnisse:")
    print(f"  GIFs:   {gif_dir}")
    print(f"  Output: {output_dir}")
    print(f"  Temp:   {temp_dir}")
    
    # Produktion für alle Sprachen
    for lang in ['de', 'en', 'it']:
        produce_language(lang, gif_dir, output_dir, temp_dir)
    
    print("\n" + "="*80)
    print("✅ PRODUKTION ABGESCHLOSSEN")
    print("="*80)
    
    videos = list(output_dir.glob("ssz_complete_*.mp4"))
    if videos:
        print(f"\nErstellt ({len(videos)} Videos):")
        for v in sorted(videos):
            size_mb = v.stat().st_size / (1024*1024)
            print(f"  • {v.name} ({size_mb:.1f} MB)")
    else:
        print("\n⚠️  Keine finalen Videos erstellt")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
