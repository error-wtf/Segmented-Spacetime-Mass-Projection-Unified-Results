#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Trilingual Video Master Pipeline
Generiert hochqualitative 3-teilige Videos in DE/IT/EN

© 2025 Carmen Wrede, Lino Casu – Forschungsteam ZS-α
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from dataclasses import dataclass

# UTF-8 setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(r'D:\SSZ_Render\trilingual')
AUDIO_DIR = BASE_DIR / 'audio'
PARTS_DIR = BASE_DIR / 'parts'
FINAL_DIR = BASE_DIR / 'final'
LOGS_DIR = BASE_DIR / 'logs'

# Alle Verzeichnisse
ALL_DIRS = [BASE_DIR, AUDIO_DIR, PARTS_DIR, FINAL_DIR, LOGS_DIR]

# Existierende GIFs (für alle Parts!)
EXISTING_GIFS = {
    'part1': {
        'de': Path(r'D:\ssz_scientific_de.gif'),
        'en': Path(r'D:\ssz_scientific_en.gif'),
        'it': Path(r'D:\ssz_scientific_it.gif')
    },
    'part2': Path(r'G:\ssz_cosmo_anim.gif'),
    'part3': Path(r'G:\ssz_proof_anim_v6.gif')
}

# Sprachen
LANGUAGES = ['de', 'en', 'it']

# Video-Einstellungen
VIDEO_CONFIG = {
    'resolution': (1920, 1080),
    'fps': 30,
    'crf': 18,  # High quality
    'preset': 'slow',
    'audio_bitrate': '320k',
    'audio_sample_rate': 48000,
}

# ============================================================================
# VOICEOVER TEXTS
# ============================================================================

VOICEOVER_TEXTS = {
    'part1': {
        'de': """
Zwei grundsätzlich verschiedene Vorstellungen vom Anfang des Universums: 
Links das klassische ΛCDM-Modell mit seiner Singularität – ein Punkt unendlicher Dichte, 
mathematisch problematisch. Die Expansion kühlt das Universum, Strukturen entstehen. 
Doch die Singularität bleibt eine Herausforderung. 

Rechts die segmentierte Raumzeit: Kein Punkt, sondern eine strukturierte Ursprungsschicht. 
Der Raum entsteht durch geordnete Segmentierung. Expansion ist Entfaltung, keine Explosion. 
Resonanzen halten die Dichte endlich – mathematisch stabil und physikalisch konsistent.
        """.strip(),
        
        'en': """
Two fundamentally different views of the universe's beginning:
On the left, the standard ΛCDM model with its singularity—a point of infinite density,
mathematically problematic. Expansion cools the universe, structures form.
But the singularity remains a challenge.

On the right, segmented spacetime: Not a point, but a structured origin layer.
Space forms through ordered segmentation. Expansion is unfolding, not explosion.
Resonances keep density finite—mathematically stable and physically consistent.
        """.strip(),
        
        'it': """
Due visioni fondamentalmente diverse dell'inizio dell'universo:
A sinistra, il modello ΛCDM standard con la sua singolarità—un punto di densità infinita,
matematicamente problematico. L'espansione raffredda l'universo, le strutture si formano.
Ma la singolarità rimane una sfida.

A destra, spaziotempo segmentato: Non un punto, ma uno strato d'origine strutturato.
Lo spazio si forma per segmentazione ordinata. L'espansione è dispiegamento, non esplosione.
Le risonanze mantengono la densità finita—matematicamente stabile e fisicamente coerente.
        """.strip(),
    },
    
    'part2': {
        'de': """
SSZ im Vergleich mit observablen Daten:

Oben links das Hubble-Diagramm: Beide Modelle – ΛCDM und SSZ – passen zur 
beobachteten Expansion. Die Rotverschiebung z zeigt identische Vorhersagen 
bis zu den entferntesten Supernovae.

Oben rechts die BAO-Distanzmetrik: Die akustischen Oszillationen des frühen 
Universums bestätigen beide Ansätze. SSZ reproduziert die CMB-Signatur präzise.

Unten: Das Wachstum kosmischer Strukturen. Der orange Punkt markiert heutige 
Beobachtungen. SSZ mit seinen Parametern – H0 gleich 70, Omega Lambda 0.7, 
Omega-M 0.3 – zeigt perfekte Übereinstimmung mit Galaxienhaufen und Filamenten.

Die Chi-Quadrat-Statistik: SSZ gleich ΛCDM. Beide Modelle erklären die Daten.
Der Unterschied liegt in der fundamentalen Physik – nicht in den Vorhersagen.
        """.strip(),
        
        'en': """
SSZ compared with observable data:

Top left, the Hubble diagram: Both models—ΛCDM and SSZ—fit the observed expansion.
Redshift z shows identical predictions out to the most distant supernovae.

Top right, BAO distance metric: The acoustic oscillations of the early universe 
confirm both approaches. SSZ reproduces the CMB signature precisely.

Bottom: The growth of cosmic structures. The orange point marks today's observations.
SSZ with its parameters—H0 equals 70, Omega Lambda 0.7, Omega-M 0.3—shows 
perfect agreement with galaxy clusters and filaments.

The chi-squared statistic: SSZ equals ΛCDM. Both models explain the data.
The difference lies in fundamental physics—not in predictions.
        """.strip(),
        
        'it': """
SSZ confrontato con dati osservabili:

In alto a sinistra, il diagramma di Hubble: Entrambi i modelli—ΛCDM e SSZ—
si adattano all'espansione osservata. Il redshift z mostra previsioni identiche 
fino alle supernove più distanti.

In alto a destra, metrica BAO: Le oscillazioni acustiche dell'universo primordiale 
confermano entrambi gli approcci. SSZ riproduce la firma CMB con precisione.

In basso: La crescita delle strutture cosmiche. Il punto arancione segna 
le osservazioni odierne. SSZ con i suoi parametri—H0 uguale 70, Omega Lambda 0.7, 
Omega-M 0.3—mostra perfetto accordo con ammassi di galassie e filamenti.

La statistica chi-quadrato: SSZ uguale ΛCDM. Entrambi i modelli spiegano i dati.
La differenza sta nella fisica fondamentale—non nelle previsioni.
        """.strip(),
    },
    
    'part3': {
        'de': """
Die mathematische Stabilität der segmentierten Raumzeit:

Oben links: Der Bruchteil stabiler Konfigurationen im Parameter-Raum. 
Der große blaue Bereich zeigt: Für Lambda-Λ zwischen 0 und 0.6 und K zwischen 
20 und 120 ist SSZ direkt stabil. Die gestrichelte Linie bei K gleich 32 
markiert unser Referenzmodell.

Oben rechts: Lambda-Λ kritisch versus Omega-Null. Keine Grenzdaten – 
das System ist universell konsistent. Kein Feintuning erforderlich.

Unten links: Die Warnung – Amplitude Evolution für instabile Parameter. 
Log G größer null bedeutet exponentielles Wachstum. Aber: SSZ vermeidet 
diese Regionen durch Konstruktion. Die physikalischen Parameter liegen 
im stabilen Bereich – Roundtrip n zeigt Langzeit-Stabilität über 50 Zyklen.

Unten rechts: Das Disagreement-Ratio. Uniform bei Lambda-Λ kleiner 0.3: 
Perfekte Übereinstimmung mit Beobachtungen. Frames gleich 180: 
Keine Instabilitäten über die gesamte Evolution.

Fazit: SSZ ist nicht nur beobachtbar äquivalent zu ΛCDM – es ist mathematisch 
robuster, frei von Singularitäten, und konsistent mit allen Daten.
        """.strip(),
        
        'en': """
The mathematical stability of segmented spacetime:

Top left: The fraction of stable configurations in parameter space.
The large blue region shows: For Lambda-Λ between 0 and 0.6 and K between 
20 and 120, SSZ is directly stable. The dashed line at K equals 32 
marks our reference model.

Top right: Lambda-Λ critical versus Omega-zero. No boundary data—
the system is universally consistent. No fine-tuning required.

Bottom left: The warning—amplitude evolution for unstable parameters.
Log G greater than zero means exponential growth. But: SSZ avoids 
these regions by construction. Physical parameters lie in the stable 
region—Roundtrip n shows long-term stability over 50 cycles.

Bottom right: The disagreement ratio. Uniform at Lambda-Λ less than 0.3:
Perfect agreement with observations. Frames equals 180:
No instabilities across entire evolution.

Conclusion: SSZ is not only observationally equivalent to ΛCDM—it is 
mathematically more robust, free from singularities, and consistent with all data.
        """.strip(),
        
        'it': """
La stabilità matematica dello spaziotempo segmentato:

In alto a sinistra: La frazione di configurazioni stabili nello spazio parametrico.
La grande regione blu mostra: Per Lambda-Λ tra 0 e 0.6 e K tra 20 e 120,
SSZ è direttamente stabile. La linea tratteggiata a K uguale 32 
segna il nostro modello di riferimento.

In alto a destra: Lambda-Λ critico versus Omega-zero. Nessun dato di confine—
il sistema è universalmente coerente. Non serve fine-tuning.

In basso a sinistra: L'avvertimento—evoluzione dell'ampiezza per parametri instabili.
Log G maggiore di zero significa crescita esponenziale. Ma: SSZ evita 
queste regioni per costruzione. I parametri fisici giacciono nella 
regione stabile—Roundtrip n mostra stabilità a lungo termine su 50 cicli.

In basso a destra: Il rapporto di disaccordo. Uniforme a Lambda-Λ minore di 0.3:
Perfetto accordo con le osservazioni. Frames uguale 180:
Nessuna instabilità lungo l'intera evoluzione.

Conclusione: SSZ non è solo osservativamente equivalente a ΛCDM—è 
matematicamente più robusto, libero da singolarità, e coerente con tutti i dati.
        """.strip(),
    }
}

# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class AudioSegment:
    """Audio-Segment mit Metadaten"""
    part: str  # 'part1', 'part2', 'part3'
    lang: str  # 'de', 'en', 'it'
    text: str
    audio_path: Path
    duration: float = 0.0

@dataclass
class VideoSegment:
    """Video-Segment mit Metadaten"""
    part: str
    lang: str
    gif_path: Path
    audio_path: Path
    mp4_path: Path
    duration: float

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def ensure_directories():
    """Erstellt alle benötigten Verzeichnisse"""
    for directory in ALL_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ {directory}")

def get_audio_duration(audio_path: Path) -> float:
    """Ermittelt Audio-Dauer mit ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"ERROR getting duration for {audio_path}: {e}")
        return 0.0

def log_progress(message: str, log_file: Path):
    """Schreibt Progress in Log-Datei"""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")
    print(message)

# ============================================================================
# MAIN PIPELINE
# ============================================================================

class TrilingualPipeline:
    """Haupt-Pipeline für trilinguales Video"""
    
    def __init__(self, tts_engine: str = 'azure'):
        self.tts_engine = tts_engine
        self.audio_segments: List[AudioSegment] = []
        self.video_segments: List[VideoSegment] = []
        self.log_file = LOGS_DIR / f'production_{self.timestamp()}.log'
        
    @staticmethod
    def timestamp():
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def step1_generate_audio(self):
        """PHASE 1: Audio-Generierung"""
        self.log("=" * 70)
        self.log("PHASE 1: Audio-Generierung")
        self.log("=" * 70)
        
        for part in ['part1', 'part2', 'part3']:
            for lang in LANGUAGES:
                text = VOICEOVER_TEXTS[part][lang]
                audio_path = AUDIO_DIR / f'{part}_{lang}.wav'
                
                self.log(f"\n→ Generiere Audio: {part} ({lang.upper()})")
                
                # Import TTS-Engine
                if self.tts_engine == 'azure':
                    from ssz_azure_tts import generate_tts_azure
                    duration = generate_tts_azure(text, lang, audio_path)
                elif self.tts_engine == 'google':
                    from ssz_google_tts import generate_tts_google
                    duration = generate_tts_google(text, lang, audio_path)
                else:
                    # Fallback: ffmpeg TTS
                    from ssz_ffmpeg_tts import generate_tts_ffmpeg
                    duration = generate_tts_ffmpeg(text, lang, audio_path)
                
                segment = AudioSegment(
                    part=part,
                    lang=lang,
                    text=text,
                    audio_path=audio_path,
                    duration=duration
                )
                self.audio_segments.append(segment)
                
                self.log(f"  ✓ {audio_path.name} ({duration:.2f}s)")
        
        self.log(f"\n✓ Audio-Generierung komplett: {len(self.audio_segments)} Dateien")
        self.save_audio_manifest()
    
    def step2_render_gifs(self):
        """PHASE 2: GIF-Anpassung mit Audio-Längen (ALLE zeitlich angepasst!)"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 2: GIF-Anpassung (schnell!)")
        self.log("=" * 70)
        
        from ssz_gif_time_adjuster import adjust_gif_speed
        
        for segment in self.audio_segments:
            gif_path = PARTS_DIR / f'{segment.part}_{segment.lang}.gif'
            
            self.log(f"\n→ Bereite GIF vor: {segment.part} ({segment.lang.upper()})")
            self.log(f"  Duration: {segment.duration:.2f}s")
            
            # Part 1: Sprachspezifische GIFs
            if segment.part == 'part1':
                if isinstance(EXISTING_GIFS['part1'], dict):
                    existing_gif = EXISTING_GIFS['part1'].get(segment.lang)
                    
                    if existing_gif and existing_gif.exists():
                        self.log(f"  Methode: Zeitliche Anpassung von {existing_gif.name}")
                        adjust_gif_speed(
                            input_gif=existing_gif,
                            target_duration=segment.duration,
                            output_gif=gif_path
                        )
                    else:
                        self.log(f"  ⚠️  WARNING: {existing_gif} nicht gefunden!")
                        self.log(f"  Fallback: Rendere neu...")
                        from ssz_gif_renderer_part1 import render_intro_gif
                        render_intro_gif(duration=segment.duration, lang=segment.lang,
                                       output_path=gif_path, fps=VIDEO_CONFIG['fps'])
            
            # Part 2 & 3: Ein GIF für alle Sprachen
            elif segment.part in EXISTING_GIFS:
                existing_gif = EXISTING_GIFS[segment.part]
                
                if not existing_gif.exists():
                    self.log(f"  ⚠️  WARNING: {existing_gif} nicht gefunden!")
                    self.log(f"  Fallback: Rendere neu...")
                    
                    if segment.part == 'part2':
                        from ssz_gif_renderer_part2 import render_cosmo_gif
                        render_cosmo_gif(duration=segment.duration, lang=segment.lang, 
                                        output_path=gif_path, fps=VIDEO_CONFIG['fps'])
                    else:
                        from ssz_gif_renderer_part3 import render_proof_gif
                        render_proof_gif(duration=segment.duration, lang=segment.lang,
                                        output_path=gif_path, fps=VIDEO_CONFIG['fps'])
                else:
                    self.log(f"  Methode: Zeitliche Anpassung von {existing_gif.name}")
                    adjust_gif_speed(
                        input_gif=existing_gif,
                        target_duration=segment.duration,
                        output_gif=gif_path
                    )
            
            self.log(f"  ✓ {gif_path.name}")
            
            # Video-Segment erstellen
            mp4_path = PARTS_DIR / f'{segment.part}_{segment.lang}.mp4'
            video_seg = VideoSegment(
                part=segment.part,
                lang=segment.lang,
                gif_path=gif_path,
                audio_path=segment.audio_path,
                mp4_path=mp4_path,
                duration=segment.duration
            )
            self.video_segments.append(video_seg)
        
        self.log(f"\n✓ GIF-Anpassung komplett: {len(self.video_segments)} Dateien")
    
    def step3_create_videos(self):
        """PHASE 3: Video-Erstellung (GIF + Audio → MP4)"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 3: Video-Erstellung")
        self.log("=" * 70)
        
        from ssz_video_concat import gif_to_mp4_with_audio
        
        for segment in self.video_segments:
            self.log(f"\n→ Erstelle MP4: {segment.part} ({segment.lang.upper()})")
            
            gif_to_mp4_with_audio(
                gif_path=segment.gif_path,
                audio_path=segment.audio_path,
                output_path=segment.mp4_path,
                crf=VIDEO_CONFIG['crf'],
                preset=VIDEO_CONFIG['preset'],
                audio_bitrate=VIDEO_CONFIG['audio_bitrate']
            )
            
            self.log(f"  ✓ {segment.mp4_path.name}")
        
        self.log(f"\n✓ Video-Erstellung komplett: {len(self.video_segments)} MP4s")
    
    def step4_concatenate_final_videos(self):
        """PHASE 4: Finale Video-Concatenation (pro Sprache)"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 4: Finale Video-Concatenation")
        self.log("=" * 70)
        
        from ssz_video_concat import concat_videos
        
        for lang in LANGUAGES:
            # Sammle alle Parts für diese Sprache
            lang_segments = [s for s in self.video_segments if s.lang == lang]
            lang_segments.sort(key=lambda s: s.part)  # part1, part2, part3
            
            video_paths = [s.mp4_path for s in lang_segments]
            output_path = FINAL_DIR / f'ssz_complete_{lang}.mp4'
            
            total_duration = sum(s.duration for s in lang_segments)
            
            self.log(f"\n→ Concateniere Final-Video: {lang.upper()}")
            self.log(f"  Parts: {[s.part for s in lang_segments]}")
            self.log(f"  Gesamtdauer: {total_duration:.2f}s")
            
            concat_videos(video_paths, output_path)
            
            self.log(f"  ✓ {output_path.name}")
        
        self.log("\n" + "=" * 70)
        self.log("✓✓✓ PRODUCTION KOMPLETT ✓✓✓")
        self.log("=" * 70)
        self.log(f"\nFinale Videos:")
        for lang in LANGUAGES:
            final_path = FINAL_DIR / f'ssz_complete_{lang}.mp4'
            if final_path.exists():
                size_mb = final_path.stat().st_size / (1024 * 1024)
                self.log(f"  • {final_path.name} ({size_mb:.1f} MB)")
    
    def save_audio_manifest(self):
        """Speichert Audio-Metadaten als JSON"""
        manifest = {
            'segments': [
                {
                    'part': s.part,
                    'lang': s.lang,
                    'audio_path': str(s.audio_path),
                    'duration': s.duration,
                    'text_preview': s.text[:100] + '...'
                }
                for s in self.audio_segments
            ]
        }
        manifest_path = AUDIO_DIR / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        self.log(f"\n✓ Audio-Manifest gespeichert: {manifest_path}")
    
    def log(self, message: str):
        """Log-Nachricht ausgeben und speichern"""
        log_progress(message, self.log_file)
    
    def run(self):
        """Führt gesamte Pipeline aus"""
        ensure_directories()
        
        self.log(f"\n{'=' * 70}")
        self.log("SSZ TRILINGUAL VIDEO PRODUCTION")
        self.log(f"{'=' * 70}")
        self.log(f"TTS-Engine: {self.tts_engine}")
        self.log(f"Sprachen: {', '.join(LANGUAGES)}")
        self.log(f"Output: {FINAL_DIR}")
        
        try:
            self.step1_generate_audio()
            self.step2_render_gifs()
            self.step3_create_videos()
            self.step4_concatenate_final_videos()
            
            self.log(f"\n✓✓✓ ERFOLG ✓✓✓")
            self.log(f"Log: {self.log_file}")
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())
            raise

# ============================================================================
# CLI
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='SSZ Trilingual Video Production Pipeline'
    )
    parser.add_argument(
        '--tts-engine',
        choices=['azure', 'google', 'ffmpeg'],
        default='azure',
        help='TTS-Engine (default: azure)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test-Mode: nur 1 Sprache, nur Part 1'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.test:
        print("\n⚠️  TEST MODE: Nur DE, nur Part 1")
        # Override globals
        global LANGUAGES
        LANGUAGES = ['de']
        global VOICEOVER_TEXTS
        VOICEOVER_TEXTS = {'part1': VOICEOVER_TEXTS['part1']}
    
    pipeline = TrilingualPipeline(tts_engine=args.tts_engine)
    pipeline.run()

if __name__ == '__main__':
    main()
