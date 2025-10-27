#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Video Production - Finale Audiotexte (wissenschaftlich korrekt & knapp)
Angepasst an vorhandene GIFs: ssz_scientific, ssz_cosmo_anim, ssz_proof_anim_v6

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

# =============================================================================
# TEIL 1: Intro (ssz_scientific_de/en/it.gif)
# Vergleich ΛCDM vs. SSZ - Grundkonzept
# =============================================================================

PART1_SCRIPTS = {
    'de': {
        'title': 'Singularität vs. Segmentierung',
        'segments': [
            {
                'time': 0.0,
                'duration': 6.0,
                'text': (
                    "Das klassische Modell beginnt mit unendlicher Dichte. "
                    "Eine mathematische Singularität, die physikalisch problematisch ist."
                )
            },
            {
                'time': 6.5,
                'duration': 6.5,
                'text': (
                    "Die Segmentierte Raumzeit zeigt: Raum entsteht durch Segmentierung, "
                    "nicht durch Explosion. Endliche Dichten überall."
                )
            },
            {
                'time': 13.5,
                'duration': 5.5,
                'text': (
                    "Keine Singularität bedeutet: Stabilität vom ersten Moment an. "
                    "Das Universum entfaltet sich aus geometrischer Ordnung."
                )
            }
        ],
        'total_duration': 19.0
    },
    
    'en': {
        'title': 'Singularity vs. Segmentation',
        'segments': [
            {
                'time': 0.0,
                'duration': 5.5,
                'text': (
                    "The classical model starts with infinite density. "
                    "A mathematical singularity that's physically problematic."
                )
            },
            {
                'time': 6.0,
                'duration': 6.5,
                'text': (
                    "Segmented spacetime shows: space emerges through segmentation, "
                    "not explosion. Finite densities everywhere."
                )
            },
            {
                'time': 13.0,
                'duration': 5.5,
                'text': (
                    "No singularity means: stability from the very beginning. "
                    "The universe unfolds from geometric order."
                )
            }
        ],
        'total_duration': 18.5
    },
    
    'it': {
        'title': 'Singolarità vs. Segmentazione',
        'segments': [
            {
                'time': 0.0,
                'duration': 6.0,
                'text': (
                    "Il modello classico inizia con densità infinita. "
                    "Una singolarità matematica fisicamente problematica."
                )
            },
            {
                'time': 6.5,
                'duration': 7.0,
                'text': (
                    "Lo spazio-tempo segmentato mostra: lo spazio nasce dalla segmentazione, "
                    "non dall'esplosione. Densità finite ovunque."
                )
            },
            {
                'time': 14.0,
                'duration': 5.5,
                'text': (
                    "Nessuna singolarità significa: stabilità dal primo istante. "
                    "L'universo si dispiega dall'ordine geometrico."
                )
            }
        ],
        'total_duration': 19.5
    }
}


# =============================================================================
# TEIL 2: Kosmologie (ssz_cosmo_anim.gif)
# Hubble, BAO, Supernova-Daten - SSZ passt zu Beobachtungen
# =============================================================================

PART2_SCRIPTS = {
    'de': {
        'title': 'Kosmologische Evidenz',
        'segments': [
            {
                'time': 0.0,
                'duration': 6.5,
                'text': (
                    "Hubble-Diagramm, barionische akustische Oszillationen, Supernovae: "
                    "Alle Beobachtungen passen zur Segmentierten Raumzeit."
                )
            },
            {
                'time': 7.0,
                'duration': 6.0,
                'text': (
                    "Die Expansion ist real. Aber sie kommt nicht aus einer Singularität, "
                    "sondern aus der Entspannung segmentierter Struktur."
                )
            },
            {
                'time': 13.5,
                'duration': 5.5,
                'text': (
                    "Dunkle Energie wird geometrisch erklärt: "
                    "als Resonanz zwischen Raumsegmenten."
                )
            }
        ],
        'total_duration': 19.0
    },
    
    'en': {
        'title': 'Cosmological Evidence',
        'segments': [
            {
                'time': 0.0,
                'duration': 6.0,
                'text': (
                    "Hubble diagram, baryon acoustic oscillations, supernovae: "
                    "All observations fit segmented spacetime."
                )
            },
            {
                'time': 6.5,
                'duration': 6.0,
                'text': (
                    "Expansion is real. But it doesn't come from a singularity, "
                    "but from relaxation of segmented structure."
                )
            },
            {
                'time': 13.0,
                'duration': 5.5,
                'text': (
                    "Dark energy is explained geometrically: "
                    "as resonance between space segments."
                )
            }
        ],
        'total_duration': 18.5
    },
    
    'it': {
        'title': 'Evidenza Cosmologica',
        'segments': [
            {
                'time': 0.0,
                'duration': 6.5,
                'text': (
                    "Diagramma di Hubble, oscillazioni acustiche barioniche, supernovae: "
                    "Tutte le osservazioni si adattano allo spazio-tempo segmentato."
                )
            },
            {
                'time': 7.0,
                'duration': 6.5,
                'text': (
                    "L'espansione è reale. Ma non proviene da una singolarità, "
                    "ma dal rilassamento della struttura segmentata."
                )
            },
            {
                'time': 14.0,
                'duration': 5.5,
                'text': (
                    "L'energia oscura è spiegata geometricamente: "
                    "come risonanza tra segmenti spaziali."
                )
            }
        ],
        'total_duration': 19.5
    }
}


# =============================================================================
# TEIL 3: Stabilität (ssz_proof_anim_v6.gif)
# Lambda_A, K-Segmente, Stabilitätskriterien
# =============================================================================

PART3_SCRIPTS = {
    'de': {
        'title': 'Mathematische Stabilität',
        'segments': [
            {
                'time': 0.0,
                'duration': 7.0,
                'text': (
                    "Stabilitätsanalyse zeigt: Ab einem kritischen Kopplungsparameter "
                    "wird die Raumzeit stabil. Keine chaotische Explosion."
                )
            },
            {
                'time': 7.5,
                'duration': 6.0,
                'text': (
                    "Bei hoher Segmentauflösung entstehen Resonanzen, "
                    "die die Struktur ordnen. Das ist der Ursprung der Gravitation."
                )
            },
            {
                'time': 14.0,
                'duration': 5.5,
                'text': (
                    "Der Anfang war kein Knall, sondern der Übergang "
                    "zu selbst-organisierender Geometrie."
                )
            }
        ],
        'total_duration': 19.5
    },
    
    'en': {
        'title': 'Mathematical Stability',
        'segments': [
            {
                'time': 0.0,
                'duration': 6.5,
                'text': (
                    "Stability analysis shows: above a critical coupling parameter, "
                    "spacetime becomes stable. No chaotic explosion."
                )
            },
            {
                'time': 7.0,
                'duration': 6.0,
                'text': (
                    "At high segment resolution, resonances emerge "
                    "that organize structure. This is the origin of gravity."
                )
            },
            {
                'time': 13.5,
                'duration': 5.5,
                'text': (
                    "The beginning wasn't a bang, but the transition "
                    "to self-organizing geometry."
                )
            }
        ],
        'total_duration': 19.0
    },
    
    'it': {
        'title': 'Stabilità Matematica',
        'segments': [
            {
                'time': 0.0,
                'duration': 7.0,
                'text': (
                    "L'analisi di stabilità mostra: sopra un parametro di accoppiamento critico, "
                    "lo spazio-tempo diventa stabile. Nessuna esplosione caotica."
                )
            },
            {
                'time': 7.5,
                'duration': 6.5,
                'text': (
                    "Ad alta risoluzione di segmenti emergono risonanze "
                    "che organizzano la struttura. Questa è l'origine della gravità."
                )
            },
            {
                'time': 14.5,
                'duration': 5.5,
                'text': (
                    "L'inizio non fu un'esplosione, ma la transizione "
                    "verso una geometria auto-organizzante."
                )
            }
        ],
        'total_duration': 20.0
    }
}


# =============================================================================
# METADATA für Video-Produktion
# =============================================================================

VIDEO_CONFIG = {
    'part1': {
        'gif_source': 'ssz_scientific_{lang}.gif',  # {lang} = de/en/it
        'fps_target': 30,
        'resolution': (1920, 1080)
    },
    'part2': {
        'gif_source': 'ssz_cosmo_anim.gif',  # Sprachneutral
        'fps_target': 30,
        'resolution': (1920, 1080)
    },
    'part3': {
        'gif_source': 'ssz_proof_anim_v6.gif',  # Sprachneutral
        'fps_target': 30,
        'resolution': (1920, 1080)
    }
}


# =============================================================================
# Audio-Konfiguration (High Quality)
# =============================================================================

AUDIO_CONFIG = {
    'sample_rate': 48000,  # Professional quality
    'channels': 2,  # Stereo
    'bit_depth': 24,  # High quality
    'format': 'wav',
    'tts_engine': 'edge-tts',  # Beste Qualität
    'voices': {
        'de': 'de-DE-KatjaNeural',
        'en': 'en-US-AriaNeural',
        'it': 'it-IT-IsabellaNeural'
    },
    'rate': '+0%',  # Normal speed
    'pitch': '+0Hz',  # Normal pitch
    'volume': '+0%'  # Normal volume
}


if __name__ == '__main__':
    # Ausgabe der Script-Längen zur Verifikation
    print("="*80)
    print("SSZ VIDEO SCRIPTS - FINAL")
    print("="*80)
    
    for part_name, part_data in [
        ('PART 1: Intro', PART1_SCRIPTS),
        ('PART 2: Kosmologie', PART2_SCRIPTS),
        ('PART 3: Stabilität', PART3_SCRIPTS)
    ]:
        print(f"\n{part_name}")
        print("-"*80)
        for lang in ['de', 'en', 'it']:
            total = part_data[lang]['total_duration']
            segments = len(part_data[lang]['segments'])
            print(f"  {lang.upper()}: {total:.1f}s ({segments} Segmente)")
    
    print("\n" + "="*80)
    print("AUDIO CONFIG")
    print("="*80)
    print(f"Sample Rate: {AUDIO_CONFIG['sample_rate']} Hz")
    print(f"Bit Depth: {AUDIO_CONFIG['bit_depth']} bit")
    print(f"Channels: {AUDIO_CONFIG['channels']} (Stereo)")
    print(f"TTS Engine: {AUDIO_CONFIG['tts_engine']}")
    print("\nVoices:")
    for lang, voice in AUDIO_CONFIG['voices'].items():
        print(f"  {lang.upper()}: {voice}")
