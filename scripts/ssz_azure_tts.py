#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Azure TTS Wrapper - Hochqualitative Text-to-Speech

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

# UTF-8 setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# ============================================================================
# AZURE TTS CONFIGURATION
# ============================================================================

AZURE_VOICES = {
    'de': {
        'name': 'de-DE-KatjaNeural',
        'style': 'default',  # Alternativen: 'cheerful', 'sad', 'serious'
        'rate': '+5%',  # Etwas schneller als Normal
        'pitch': '+0Hz',  # Normal
    },
    'en': {
        'name': 'en-US-JennyNeural',
        'style': 'default',
        'rate': '+5%',
        'pitch': '+0Hz',
    },
    'it': {
        'name': 'it-IT-ElsaNeural',
        'style': 'default',
        'rate': '+5%',
        'pitch': '+0Hz',
    }
}

# ============================================================================
# TTS FUNCTIONS
# ============================================================================

def generate_tts_azure(text: str, lang: str, output_path: Path) -> float:
    """
    Generiert TTS mit Azure Cognitive Services und gibt Dauer zurück.
    
    Args:
        text: Voiceover-Text
        lang: 'de', 'en', 'it'
        output_path: Output WAV-Datei
    
    Returns:
        duration: Audio-Länge in Sekunden
    """
    if lang not in AZURE_VOICES:
        raise ValueError(f"Unsupported language: {lang}")
    
    voice_config = AZURE_VOICES[lang]
    
    # Prüfe ob Azure CLI installiert ist
    try:
        subprocess.run(
            ['az', '--version'],
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Azure CLI nicht installiert!")
        print("Installation: https://docs.microsoft.com/cli/azure/install-azure-cli")
        raise
    
    # Azure TTS Command
    cmd = [
        'az', 'cognitiveservices', 'speech', 'synthesize',
        '--voice', voice_config['name'],
        '--rate', voice_config['rate'],
        '--pitch', voice_config['pitch'],
        '--text', text,
        '--output', str(output_path)
    ]
    
    print(f"  → Azure TTS: {voice_config['name']}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Audio-Länge ermitteln
        duration = get_audio_duration(output_path)
        
        return duration
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Azure TTS failed!")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise

def get_audio_duration(audio_path: Path) -> float:
    """Ermittelt Audio-Dauer mit ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"ERROR getting duration: {e}")
        return 0.0

def generate_tts_azure_with_ssml(ssml: str, output_path: Path) -> float:
    """
    Generiert TTS mit SSML (für erweiterte Kontrolle).
    
    SSML erlaubt:
    - Pausen: <break time="500ms"/>
    - Betonung: <emphasis level="strong">wichtig</emphasis>
    - Geschwindigkeit: <prosody rate="slow">langsam</prosody>
    
    Args:
        ssml: SSML-formatierter Text
        output_path: Output WAV-Datei
    
    Returns:
        duration: Audio-Länge in Sekunden
    """
    cmd = [
        'az', 'cognitiveservices', 'speech', 'synthesize',
        '--ssml', ssml,
        '--output', str(output_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        duration = get_audio_duration(output_path)
        return duration
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Azure TTS (SSML) failed!")
        print(f"STDERR: {e.stderr}")
        raise

def create_ssml(text: str, lang: str, pauses: Optional[dict] = None) -> str:
    """
    Erstellt SSML aus Plain-Text mit optionalen Pausen.
    
    Args:
        text: Plain-Text
        lang: 'de', 'en', 'it'
        pauses: Dict mit {position: duration_ms}
    
    Returns:
        ssml: SSML-formatierter Text
    """
    voice_name = AZURE_VOICES[lang]['name']
    
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">
    <voice name="{voice_name}">
        {text}
    </voice>
</speak>'''
    
    # TODO: Pausen einfügen wenn gewünscht
    
    return ssml

# ============================================================================
# AUDIO POST-PROCESSING
# ============================================================================

def normalize_audio(input_path: Path, output_path: Path, target_lufs: float = -14.0):
    """
    Normalisiert Audio auf Target-Loudness (Standard: -14 LUFS für Streaming).
    
    Args:
        input_path: Input WAV
        output_path: Output WAV (normalisiert)
        target_lufs: Target Loudness in LUFS
    """
    # Zwei-Pass: Erst messen, dann normalisieren
    
    # Pass 1: Loudness messen
    cmd_measure = [
        'ffmpeg', '-i', str(input_path),
        '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json',
        '-f', 'null', '-'
    ]
    
    try:
        result = subprocess.run(
            cmd_measure,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # JSON-Output parsen (in stderr)
        # TODO: Implementiere JSON-Parsing für präzise Normalisierung
        
        # Pass 2: Normalisieren
        cmd_normalize = [
            'ffmpeg', '-i', str(input_path),
            '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11',
            '-ar', '48000',
            '-y', str(output_path)
        ]
        
        subprocess.run(
            cmd_normalize,
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"  ✓ Audio normalisiert: {target_lufs} LUFS")
        
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Normalisierung fehlgeschlagen: {e}")
        # Fallback: Kopiere Original
        import shutil
        shutil.copy(input_path, output_path)

# ============================================================================
# TEST
# ============================================================================

def test_azure_tts():
    """Test-Funktion für Azure TTS"""
    test_dir = Path('D:/SSZ_Render/test')
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_text = "Dies ist ein Test der Azure Text-zu-Sprache Synthese. Die Qualität sollte deutlich besser sein als espeak-ng."
    
    output_path = test_dir / 'test_azure_de.wav'
    
    print("\n" + "=" * 70)
    print("AZURE TTS TEST")
    print("=" * 70)
    print(f"Text: {test_text}")
    print(f"Output: {output_path}")
    
    try:
        duration = generate_tts_azure(test_text, 'de', output_path)
        print(f"\n✓ TTS erfolgreich!")
        print(f"  Duration: {duration:.2f}s")
        print(f"  File: {output_path}")
        print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        # Normalisierte Version
        normalized_path = test_dir / 'test_azure_de_normalized.wav'
        normalize_audio(output_path, normalized_path)
        print(f"  Normalized: {normalized_path}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Test-Mode
    if '--test' in sys.argv:
        test_azure_tts()
    else:
        print("Azure TTS Wrapper - Import this module in ssz_trilingual_master.py")
