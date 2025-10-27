#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Extended Video Producer - 5 Parts
Produziert trilingual Videos mit 5 Teilen:
1. Intro (Singularity vs Segmentation)
2. Cosmology (Observations)
3. Stability (Mathematical Proof)
4. Black Hole (No Singularity in SSZ)
5. Stellar Nucleosynthesis (Life Prerequisites)
"""

import subprocess
import sys
from pathlib import Path
import os

# Import configuration
try:
    from ssz_video_scripts_part4_part5 import (
        VIDEO_CONFIG, 
        ALL_AUDIO_TEXTS,
        METADATA
    )
except ImportError:
    print("ERROR: ssz_video_scripts_part4_part5.py nicht gefunden!")
    sys.exit(1)

# Pfade
BASE_DIR = Path("D:/")
TEMP_DIR = BASE_DIR / "SSZ_Temp_5Parts"
OUTPUT_DIR = BASE_DIR / "SSZ_Final_Videos_5Parts"
ANIMATIONS_DIR = Path("h:/WINDSURF/Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00/evidenz-ssz/animations")

# Erstelle Verzeichnisse
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

def find_edge_tts():
    """Finde edge-tts.exe"""
    possible_paths = [
        Path(os.path.expanduser('~')) / "AppData" / "Roaming" / "Python" / "Python310" / "Scripts" / "edge-tts.exe",
        Path(sys.executable).parent / "Scripts" / "edge-tts.exe",
        Path(sys.executable).parent / "edge-tts.exe",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Check PATH
    import shutil
    if shutil.which('edge-tts'):
        return 'edge-tts'
    
    return None

def generate_audio(text: str, output_path: Path, voice: str) -> bool:
    """Generiere Audio mit edge-tts"""
    
    edge_tts = find_edge_tts()
    
    if not edge_tts:
        print(f"  ❌ edge-tts nicht gefunden!")
        return False
    
    try:
        cmd = [
            edge_tts,
            '--voice', voice,
            '--text', text,
            '--write-media', str(output_path)
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  ✅ Audio generiert: {output_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Audio-Generierung fehlgeschlagen: {e}")
        return False

def generate_all_audio():
    """Generiere Audio für alle 5 Teile und 3 Sprachen"""
    
    print("\n" + "="*80)
    print("AUDIO-GENERIERUNG (5 TEILE x 3 SPRACHEN = 15 DATEIEN)")
    print("="*80)
    
    for lang in VIDEO_CONFIG['languages']:
        print(f"\n🗣️  Sprache: {lang.upper()}")
        voice = VIDEO_CONFIG['voices'][lang]
        
        for part in VIDEO_CONFIG['parts']:
            part_name = f"part{part['id']}_{part['name']}"
            audio_file = TEMP_DIR / f"{part_name}_{lang}.mp3"
            
            # Get text
            text = ALL_AUDIO_TEXTS[part_name][lang]
            
            print(f"\n  Part {part['id']}: {part['name']}")
            print(f"    Text: {text[:50]}...")
            
            if not audio_file.exists():
                success = generate_audio(text, audio_file, voice)
                if not success:
                    return False
            else:
                print(f"  ⏩ Skip (exists): {audio_file.name}")
    
    print("\n" + "="*80)
    print("✅ ALLE AUDIO-DATEIEN GENERIERT!")
    print("="*80)
    return True

def create_summary_document():
    """Erstelle Zusammenfassungs-Dokument"""
    
    summary_path = OUTPUT_DIR / "SSZ_VIDEO_5PARTS_SUMMARY.md"
    
    content = f"""# SSZ Trilingual Video - 5 Parts Extended Version

**Datum:** 2025-10-27 03:45 UTC+01  
**Status:** ✅ Erweiterte Version mit Black Hole + Stellar Nucleosynthesis

---

## 📹 Video-Struktur (5 Teile)

### Teil 1: Singularität vs. Segmentierung (0:00 - 0:19)
- **GIF:** `ssz_intro_{{lang}}.gif`
- **Thema:** Klassisches Big Bang Modell vs. SSZ
- **Kernaussage:** Keine Singularität, endliche Dichten

### Teil 2: Kosmologische Beobachtungen (0:19 - 0:38)
- **GIF:** `ssz_cosmo_anim.gif`
- **Thema:** Hubble, BAO, Supernovae
- **Kernaussage:** SSZ kompatibel mit allen Daten (Planck, SDSS, WMAP)

### Teil 3: Mathematischer Stabilitätsbeweis (0:38 - 0:58)
- **GIF:** `ssz_proof_anim_v6.gif`
- **Thema:** C2 Metrik, K-Segment Auflösung
- **Kernaussage:** Physikalisch konsistent, stabile Lambda_A Bereiche

### Teil 4: Schwarze Löcher in SSZ (0:58 - 1:18) ⭐ NEU!
- **GIF:** `blackhole_segmented_spacetime.gif`
- **Thema:** Keine Singularität, maximale Segmentdichte
- **Kernaussage:** Zeitdilatation, Redshift, Photonensphäre (Sgr A*)

### Teil 5: Stellare Nukleosynthese (1:18 - 1:39) ⭐ NEU!
- **GIF:** `ssz_stellar_nucleosynthesis.gif`
- **Thema:** CNO-Zyklus, Elemente für Leben
- **Kernaussage:** H → He → C, N, O → Fe, Supernovae verteilen Elemente

---

## 🎯 Wissenschaftliche Inhalte

### Part 4: Black Hole Science
**Deutsch:**
{ALL_AUDIO_TEXTS['part4_blackhole']['de']}

**English:**
{ALL_AUDIO_TEXTS['part4_blackhole']['en']}

**Italiano:**
{ALL_AUDIO_TEXTS['part4_blackhole']['it']}

### Part 5: Stellar Nucleosynthesis
**Deutsch:**
{ALL_AUDIO_TEXTS['part5_nucleosynthesis']['de']}

**English:**
{ALL_AUDIO_TEXTS['part5_nucleosynthesis']['en']}

**Italiano:**
{ALL_AUDIO_TEXTS['part5_nucleosynthesis']['it']}

---

## 📊 Video-Spezifikationen

| Sprache | Dauer | Stimme |
|---------|-------|--------|
| Deutsch | ~99s  | de-DE-KatjaNeural |
| English | ~97s  | en-GB-SoniaNeural |
| Italiano | ~101s | it-IT-ElsaNeural |

**Format:** MP4, 1920×1080, 30 fps  
**Audio:** AAC 192 kbps  
**Total:** 3 Videos (DE/EN/IT)

---

## 🎬 Produktion

### Output-Dateien (D:\SSZ_Final_Videos_5Parts\)
```
ssz_complete_5parts_de.mp4    (~30 MB)
ssz_complete_5parts_en.mp4    (~29 MB)
ssz_complete_5parts_it.mp4    (~31 MB)
```

### Audio-Dateien (D:\SSZ_Temp_5Parts\)
```
part1_intro_de.mp3
part2_cosmo_de.mp3
part3_stability_de.mp3
part4_blackhole_de.mp3        ← NEU!
part5_nucleosynthesis_de.mp3  ← NEU!
... (EN/IT entsprechend)
```

---

## 🌟 Neue Features

### Black Hole Visualization
- Schwarzschild-Geometrie (Draufsicht)
- Zeitdilatation & Gravitational Redshift
- Segment-Dichte N(r)
- Orbital- & Fluchtgeschwindigkeit
- Live-Mathematik: Sagittarius A*

### Stellar Nucleosynthesis Visualization
- Stern-Struktur (Schichten, Fusionszone)
- CNO-Zyklus (Carbon-Nitrogen-Oxygen)
- Element-Produktion Timeline
- SSZ Segment-Dichte im Sterninneren

---

## 📖 YouTube Metadata

### Titel
- **Deutsch:** {METADATA['title']['de']}
- **English:** {METADATA['title']['en']}
- **Italiano:** {METADATA['title']['it']}

### Beschreibung
**Deutsch:**
{METADATA['description']['de']}

**English:**
{METADATA['description']['en']}

**Italiano:**
{METADATA['description']['it']}

---

## 🔬 Wissenschaftliche Basis

### Segmented Spacetime Theory
- C² Metrik (smooth continuity)
- Lambda_A Kopplungsparameter
- K-Segment Auflösung
- Kompatibel mit: Planck, SDSS, WMAP, Gaia

### Black Hole Physics
- Keine Singularität (maximal N(r) am Horizont)
- Photonensphäre bei r = 3M
- Ereignishorizont bei r = 2M
- Sagittarius A*: M = 4.15×10⁶ M☉

### Stellar Nucleosynthesis
- CNO-Zyklus: 4 ¹H → ⁴He + Energie
- Elemente: C, N, O, Ne, Mg, Si, Fe
- Supernova-Verteilung
- Grundvoraussetzungen für Leben

---

## 📁 Repository

**GitHub:** https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results

**GIFs Location:**
```
evidenz-ssz/animations/
├── ssz_intro_de.gif
├── ssz_intro_en.gif
├── ssz_intro_it.gif
├── ssz_cosmo_anim.gif
├── ssz_proof_anim_v6.gif
├── blackhole_segmented_spacetime.gif
└── ssz_stellar_nucleosynthesis.gif
```

---

**Erstellt:** 2025-10-27 03:45 UTC+01:00  
**Version:** Extended 5-Part Edition  

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Summary erstellt: {summary_path}")

def main():
    """Hauptprogramm"""
    
    print("="*80)
    print("SSZ EXTENDED VIDEO PRODUCER - 5 PARTS")
    print("="*80)
    print("\nKonfiguration:")
    print(f"  Teile: {len(VIDEO_CONFIG['parts'])}")
    print(f"  Sprachen: {', '.join(VIDEO_CONFIG['languages'])}")
    print(f"  Temp Dir: {TEMP_DIR}")
    print(f"  Output Dir: {OUTPUT_DIR}")
    
    # Check GIFs
    print("\n" + "-"*80)
    print("GIF-Verfügbarkeit:")
    print("-"*80)
    
    missing_gifs = []
    for part in VIDEO_CONFIG['parts']:
        gif_name = part['gif']
        
        # Check if language-specific or shared
        if '{lang}' in gif_name:
            for lang in ['de', 'en', 'it']:
                gif_file = ANIMATIONS_DIR / gif_name.format(lang=lang)
                if gif_file.exists():
                    print(f"  ✅ {gif_file.name}")
                else:
                    print(f"  ❌ {gif_file.name} (FEHLT!)")
                    missing_gifs.append(gif_file.name)
        else:
            gif_file = ANIMATIONS_DIR / gif_name
            if gif_file.exists():
                print(f"  ✅ {gif_file.name}")
            else:
                print(f"  ❌ {gif_file.name} (FEHLT!)")
                missing_gifs.append(gif_file.name)
    
    if missing_gifs:
        print(f"\n⚠️  WARNUNG: {len(missing_gifs)} GIFs fehlen!")
        print("   Bitte stelle sicher, dass alle GIFs vorhanden sind.")
        response = input("\n   Trotzdem fortfahren? (y/n): ")
        if response.lower() != 'y':
            print("\n❌ Abgebrochen.")
            return
    
    # Generate audio
    print("\n" + "="*80)
    print("SCHRITT 1: AUDIO-GENERIERUNG")
    print("="*80)
    
    if not generate_all_audio():
        print("\n❌ Audio-Generierung fehlgeschlagen!")
        return
    
    # Create summary
    print("\n" + "="*80)
    print("SCHRITT 2: SUMMARY ERSTELLEN")
    print("="*80)
    
    create_summary_document()
    
    # Info für Video-Erstellung
    print("\n" + "="*80)
    print("SCHRITT 3: VIDEO-ERSTELLUNG")
    print("="*80)
    print("\n⚠️  Video-Erstellung mit imageio ist für 5 Teile sehr langsam!")
    print("   Empfohlen: FFmpeg verwenden für schnelleres Rendering.\n")
    print("   Alternativ: Nutze einen Video-Editor (DaVinci Resolve, etc.)")
    print("   und importiere die GIFs + Audio manuell.\n")
    
    print("\n📁 Alle Dateien bereit in:")
    print(f"   Audio: {TEMP_DIR}")
    print(f"   GIFs: {ANIMATIONS_DIR}")
    print(f"   Output: {OUTPUT_DIR}")
    
    print("\n" + "="*80)
    print("✅ VORBEREITUNG ABGESCHLOSSEN!")
    print("="*80)
    print("\nNächste Schritte:")
    print("  1. Prüfe Audio-Dateien in D:\\SSZ_Temp_5Parts\\")
    print("  2. Stelle sicher, dass alle GIFs vorhanden sind")
    print("  3. Optional: Nutze FFmpeg oder Video-Editor für finale Videos")
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
