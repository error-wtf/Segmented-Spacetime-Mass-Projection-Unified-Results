#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Animation Master Pipeline - Audio-First Workflow
Generates multi-language animations (DE/EN/IT) with TTS-driven timing

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import json
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# UTF-8 setup for Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================================
# CONFIGURATION
# ============================================================================

VOICEOVER_TEXTS = {
    'de': {
        'title': 'Von der Singularität zur Segmentierung',
        'sentences': [
            'Zwei Perspektiven auf den Anfang: Singularität oder segmentierte Ordnung.',
            'Links das klassische Lambda C D M: der Beginn als unendliche Dichte; die Expansion kühlt das All.',
            'Die „Explosion" ist eine Metapher: Energie breitet sich aus, während Raum entsteht.',
            'Singularitäten sind mathematisch heikel und physikalisch schwer fassbar.',
            'Rechts die segmentierte Raumzeit: kein Punkt, sondern eine geordnete Ursprungsschicht.',
            'Raum entsteht durch Segmentierung; Expansion ist Entfaltung, kein Knall.',
            'Resonanzen halten Dichten endlich – die Dynamik bleibt stabil.',
            'Beide Modelle passen zur beobachteten Expansion und zu Ferndaten.',
            'Doch S S Z vermeidet die unendliche Dichte und ersetzt sie durch Struktur.',
            'Fazit: kein Knall aus dem Nichts, sondern ein Beginn der Ordnung.',
        ]
    },
    'en': {
        'title': 'From Singularity to Segmentation',
        'sentences': [
            'Two views of the beginning: singularity or segmented order.',
            'On the left, standard Lambda C D M: an initial infinite density; expansion cools the cosmos.',
            'The "explosion" is a metaphor: energy spreads as space emerges.',
            'Singularities are mathematically tricky and physically opaque.',
            'On the right, segmented spacetime: not a point, but an ordered origin layer.',
            'Space forms by segmentation; expansion is unfolding, not a bang.',
            'Resonances keep densities finite—the dynamics remain stable.',
            'Both models agree with the observed expansion and distance data.',
            'But S S Z avoids infinite density by replacing it with structure.',
            'Conclusion: not a bang from nothing, but a beginning of order.',
        ]
    },
    'it': {
        'title': 'Dalla Singolarità alla Segmentazione',
        'sentences': [
            'Due visioni dell\'inizio: singolarità o ordine segmentato.',
            'A sinistra, Lambda C D M classico: densità iniziale infinita; l\'espansione raffredda il cosmo.',
            'L\'"esplosione" è una metafora: l\'energia si diffonde mentre nasce lo spazio.',
            'Le singolarità sono matematicamente delicate e fisicamente oscure.',
            'A destra, spazio-tempo segmentato: non un punto, ma uno strato d\'origine ordinato.',
            'Lo spazio emerge per segmentazione; l\'espansione è dispiegamento, non un botto.',
            'Le risonanze mantengono finite le densità; la dinamica resta stabile.',
            'Entrambi concordano con l\'espansione osservata e le distanze cosmiche.',
            'Ma S S Z evita la densità infinita sostituendola con la struttura.',
            'Conclusione: non un botto dal nulla, ma l\'inizio dell\'ordine.',
        ]
    }
}

# TTS voice settings for espeak-ng
ESPEAK_VOICES = {
    'de': {'voice': 'de+f3', 'speed': 165, 'pitch': 40, 'amplitude': 175},
    'en': {'voice': 'en+f3', 'speed': 165, 'pitch': 40, 'amplitude': 175},
    'it': {'voice': 'it+f3', 'speed': 165, 'pitch': 40, 'amplitude': 175},
}

# Directories
BASE_DIR = Path(r'D:\SSZ_Render')
AUDIO_DIR = BASE_DIR / 'audio'
VIDEO_DIR = BASE_DIR / 'video'
YAML_DIR = BASE_DIR / 'timelines'
FINAL_DIR = BASE_DIR / 'final'
LOGS_DIR = BASE_DIR / 'logs'

# ============================================================================
# STEP 1: TTS GENERATION
# ============================================================================

def ensure_directories():
    """Create all required directories"""
    for d in [AUDIO_DIR, VIDEO_DIR, YAML_DIR, FINAL_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print("✓ Directories created")


def check_espeak() -> bool:
    """Check if espeak-ng is available"""
    try:
        result = subprocess.run(
            ['espeak-ng', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print(f"✓ espeak-ng found: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    # Try WSL fallback
    try:
        result = subprocess.run(
            ['wsl', 'espeak-ng', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print(f"✓ espeak-ng found via WSL: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ espeak-ng not found! Install with:")
    print("  - Windows: choco install espeak-ng")
    print("  - WSL: sudo apt install espeak-ng")
    return False


def generate_tts_audio(language: str, use_wsl: bool = False) -> Path:
    """Generate TTS audio for a specific language"""
    print(f"\n{'='*70}")
    print(f"Generating TTS Audio: {language.upper()}")
    print(f"{'='*70}")
    
    voice_cfg = ESPEAK_VOICES[language]
    sentences = VOICEOVER_TEXTS[language]['sentences']
    
    # Create temp directory for sentence clips
    temp_dir = AUDIO_DIR / f'temp_{language}'
    temp_dir.mkdir(exist_ok=True)
    
    # Generate individual sentence clips
    wav_files = []
    for i, sentence in enumerate(sentences, 1):
        wav_file = temp_dir / f'part_{i:02d}.wav'
        
        cmd = [
            'wsl' if use_wsl else 'espeak-ng',
        ]
        if use_wsl:
            cmd.append('espeak-ng')
        
        cmd.extend([
            '-v', voice_cfg['voice'],
            '-s', str(voice_cfg['speed']),
            '-p', str(voice_cfg['pitch']),
            '-a', str(voice_cfg['amplitude']),
            '-w', str(wav_file),
            sentence
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            wav_files.append(wav_file)
            print(f"  [{i:02d}/10] {sentence[:60]}...")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to generate part {i}: {e}")
            raise
    
    # Merge all parts with silence between sentences
    print("\n  Merging audio clips...")
    output_file = AUDIO_DIR / f'ssz_intro_{language}.wav'
    
    # Create silence file (300ms)
    silence_file = temp_dir / 'silence.wav'
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
        '-t', '0.30', '-y', str(silence_file)
    ], capture_output=True, check=True)
    
    # Create concat list
    concat_file = temp_dir / 'concat.txt'
    with open(concat_file, 'w', encoding='utf-8') as f:
        for wav in wav_files:
            f.write(f"file '{wav.absolute()}'\n")
            f.write(f"file '{silence_file.absolute()}'\n")
    
    # Concatenate with ffmpeg
    subprocess.run([
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        '-af', 'highpass=f=60,dynaudnorm=f=150:g=10,aformat=sample_rates=48000:channel_layouts=stereo',
        '-ar', '48000', '-ac', '2', '-acodec', 'pcm_s16le',
        '-y', str(output_file)
    ], capture_output=True, check=True)
    
    print(f"✓ Audio saved: {output_file}")
    return output_file


# ============================================================================
# STEP 2: AUDIO ANALYSIS
# ============================================================================

def analyze_audio_duration(audio_file: Path) -> float:
    """Get exact duration of audio file in seconds"""
    with wave.open(str(audio_file), 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration


def create_duration_manifest(audio_files: Dict[str, Path]) -> Path:
    """Create JSON manifest with audio durations"""
    manifest = {}
    
    print(f"\n{'='*70}")
    print("Audio Duration Analysis")
    print(f"{'='*70}")
    
    for lang, audio_file in audio_files.items():
        duration = analyze_audio_duration(audio_file)
        manifest[lang] = {
            'duration_s': round(duration, 2),
            'audio_file': str(audio_file.name)
        }
        print(f"  {lang.upper()}: {duration:.2f} seconds")
    
    manifest_file = BASE_DIR / 'durations.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Manifest saved: {manifest_file}")
    return manifest_file


# ============================================================================
# STEP 3: YAML TIMELINE GENERATION
# ============================================================================

def create_yaml_timeline(language: str, duration_s: float) -> Path:
    """Create YAML timeline adapted to audio duration"""
    
    # Distribute duration across scenes
    intro_duration = duration_s * 0.15
    main_duration = duration_s * 0.70
    outro_duration = duration_s * 0.15
    
    yaml_content = f"""# SSZ Animation Timeline - {language.upper()}
# Auto-generated from audio duration: {duration_s:.2f}s

metadata:
  title: "{VOICEOVER_TEXTS[language]['title']}"
  language: {language}
  total_duration: {duration_s:.2f}
  fps: 30
  resolution: [1920, 1080]

scenes:
  - name: intro
    duration: {intro_duration:.2f}
    description: "Fade in with title"
    visuals:
      - type: dual_panel
        left:
          background: "#1a0a2e"
          effect: fade_in
        right:
          background: "#0a1f2e"
          effect: fade_in
      - type: title_overlay
        text: "{VOICEOVER_TEXTS[language]['title']}"
        position: bottom_center
        font_size: 38
        color: "#ffffff"
        shadow: "rgba(0,0,0,0.6)"
  
  - name: main_comparison
    duration: {main_duration:.2f}
    description: "ΛCDM vs SSZ visualization"
    visuals:
      - type: dual_panel
        left:
          title: "ΛCDM Model"
          background: "#ffcc00"
          animation: radial_explosion
          particles: 150
          glow: true
        right:
          title: "Segmented Spacetime (SSZ)"
          background: "#00ccff"
          animation: phi_spiral
          segments: 12
          hex_grid: true
          orbital_particles: 80
      - type: divider
        width: 4
        color: ["#050505", "#1e1e1e"]
        position: center
  
  - name: outro
    duration: {outro_duration:.2f}
    description: "Fade out with credits"
    visuals:
      - type: dual_panel
        left:
          effect: fade_out
        right:
          effect: fade_out
      - type: credits
        text: "© 2025 Carmen Wrede, Lino Casu"
        position: bottom_right
        font_size: 18
        color: "#cccccc"

# No text overlays in video - all narration via audio
# Colors palette:
#   ΛCDM: ["#ffcc00", "#ff6600", "#441144"]
#   SSZ: ["#00ccff", "#1a1f2b", "#f7b733"]
"""
    
    yaml_file = YAML_DIR / f'ssz_anim_{language}.yaml'
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"  ✓ Timeline created: {yaml_file.name}")
    return yaml_file


# ============================================================================
# STEP 4: VIDEO RENDERING
# ============================================================================

def render_video(language: str, timeline_file: Path, audio_file: Path, duration_s: float) -> Path:
    """Render final MP4 video with synchronized audio"""
    
    print(f"\n{'='*70}")
    print(f"Rendering Video: {language.upper()}")
    print(f"{'='*70}")
    print(f"  Duration: {duration_s:.2f}s")
    print(f"  Timeline: {timeline_file.name}")
    print(f"  Audio: {audio_file.name}")
    
    output_file = VIDEO_DIR / f'ssz_intro_{language}.mp4'
    
    # Call the actual renderer script (to be created next)
    cmd = [
        sys.executable,
        str(Path(__file__).parent / 'ssz_video_renderer.py'),
        '--language', language,
        '--timeline', str(timeline_file),
        '--audio', str(audio_file),
        '--output', str(output_file),
        '--duration', str(duration_s)
    ]
    
    try:
        subprocess.run(cmd, check=True, encoding='utf-8', errors='replace')
        print(f"✓ Video rendered: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"✗ Rendering failed: {e}")
        raise


# ============================================================================
# STEP 5: FINALIZATION
# ============================================================================

def create_preview_collage(video_files: Dict[str, Path]) -> Path:
    """Create side-by-side preview GIF of all three languages"""
    
    print(f"\n{'='*70}")
    print("Creating Preview Collage")
    print(f"{'='*70}")
    
    gif_output = FINAL_DIR / 'ssz_intro_trilanguage.gif'
    
    # Extract first 5 seconds from each video
    temp_clips = []
    for lang, video in video_files.items():
        temp_clip = FINAL_DIR / f'temp_{lang}.mp4'
        subprocess.run([
            'ffmpeg', '-i', str(video), '-t', '5',
            '-vf', 'scale=640:360', '-r', '10',
            '-y', str(temp_clip)
        ], capture_output=True, check=True)
        temp_clips.append(temp_clip)
    
    # Stack horizontally
    subprocess.run([
        'ffmpeg',
        '-i', str(temp_clips[0]),
        '-i', str(temp_clips[1]),
        '-i', str(temp_clips[2]),
        '-filter_complex', '[0:v][1:v][2:v]hstack=inputs=3[out]',
        '-map', '[out]',
        '-r', '10', '-y', str(gif_output)
    ], capture_output=True, check=True)
    
    # Cleanup temp files
    for clip in temp_clips:
        clip.unlink()
    
    print(f"✓ Preview GIF created: {gif_output}")
    return gif_output


def create_final_manifest(durations: Dict, video_files: Dict[str, Path]) -> Path:
    """Create final manifest with all outputs"""
    
    manifest = {
        'created_by': 'WindSurf Automation v2',
        'verified_by': 'Carmen & Lino',
        'language_order': ['de', 'en', 'it'],
        'durations': durations,
        'outputs': {
            lang: {
                'video': str(video.name),
                'size_mb': round(video.stat().st_size / 1024 / 1024, 2)
            }
            for lang, video in video_files.items()
        }
    }
    
    manifest_file = FINAL_DIR / 'manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Final manifest: {manifest_file}")
    return manifest_file


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='SSZ Animation Master Pipeline - Audio-First Workflow'
    )
    parser.add_argument(
        '--languages',
        nargs='+',
        default=['de', 'en', 'it'],
        choices=['de', 'en', 'it'],
        help='Languages to generate (default: all)'
    )
    parser.add_argument(
        '--use-wsl',
        action='store_true',
        help='Use espeak-ng via WSL'
    )
    parser.add_argument(
        '--skip-audio',
        action='store_true',
        help='Skip audio generation (use existing files)'
    )
    parser.add_argument(
        '--skip-render',
        action='store_true',
        help='Skip video rendering (only generate audio & timelines)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("SSZ ANIMATION MASTER PIPELINE")
    print("Audio-First Multi-Language Workflow")
    print("="*70)
    print(f"Languages: {', '.join(args.languages)}")
    print(f"Base Directory: {BASE_DIR}")
    print("="*70 + "\n")
    
    # Step 0: Setup
    ensure_directories()
    
    if not args.skip_audio:
        if not check_espeak():
            print("\n✗ Cannot proceed without espeak-ng!")
            sys.exit(1)
    
    # Step 1: Generate TTS Audio
    audio_files = {}
    if not args.skip_audio:
        for lang in args.languages:
            try:
                audio_files[lang] = generate_tts_audio(lang, args.use_wsl)
            except Exception as e:
                print(f"✗ Failed to generate audio for {lang}: {e}")
                with open(LOGS_DIR / f'tts_fallback_{lang}.txt', 'w') as f:
                    f.write(str(e))
                raise
    else:
        # Use existing audio files
        for lang in args.languages:
            audio_file = AUDIO_DIR / f'ssz_intro_{lang}.wav'
            if audio_file.exists():
                audio_files[lang] = audio_file
            else:
                print(f"✗ Audio file not found: {audio_file}")
                sys.exit(1)
    
    # Step 2: Analyze Audio Durations
    manifest_file = create_duration_manifest(audio_files)
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        durations = json.load(f)
    
    # Step 3: Generate YAML Timelines
    print(f"\n{'='*70}")
    print("Generating YAML Timelines")
    print(f"{'='*70}")
    
    timeline_files = {}
    for lang in args.languages:
        duration = durations[lang]['duration_s']
        timeline_files[lang] = create_yaml_timeline(lang, duration)
    
    # Step 4: Render Videos
    video_files = {}
    if not args.skip_render:
        for lang in args.languages:
            try:
                video_files[lang] = render_video(
                    lang,
                    timeline_files[lang],
                    audio_files[lang],
                    durations[lang]['duration_s']
                )
            except Exception as e:
                print(f"✗ Failed to render video for {lang}: {e}")
                raise
        
        # Step 5: Create Preview & Manifest
        if len(video_files) == 3:
            create_preview_collage(video_files)
        
        create_final_manifest(durations, video_files)
    
    # Final Summary
    print(f"\n{'='*70}")
    print("PIPELINE COMPLETE")
    print(f"{'='*70}")
    print(f"Audio files: {len(audio_files)}")
    print(f"Timelines: {len(timeline_files)}")
    print(f"Videos: {len(video_files)}")
    print(f"\nOutputs saved to: {BASE_DIR}")
    print(f"{'='*70}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
