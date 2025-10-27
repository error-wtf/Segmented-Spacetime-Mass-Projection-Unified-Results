#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Trilingual Video Scripts - Part 4 (Black Hole) + Part 5 (Stellar Nucleosynthesis)
Erweitert die bestehenden 3 Teile um zwei weitere wissenschaftliche Segmente
"""

# ============================================================================
# PART 4: BLACK HOLE SEGMENTED SPACETIME
# ============================================================================

PART4_AUDIO_TEXTS = {
    'de': """
Schwarze Löcher in SSZ: Keine Singularität, sondern maximale Segmentdichte.
Am Ereignishorizont steigt die K-Segmentauflösung. 
Zeitdilatation und Redshift entstehen durch Raumzeitstruktur.
Photonensphäre und Orbits bleiben stabil – beobachtbar bei Sagittarius A Stern.
""",
    
    'en': """
Black holes in SSZ: No singularity, but maximum segment density.
At the event horizon, K-segment resolution increases.
Time dilation and redshift emerge from spacetime structure.
Photon sphere and orbits remain stable – observable at Sagittarius A star.
""",
    
    'it': """
Buchi neri in SSZ: Nessuna singolarità, ma massima densità di segmenti.
All'orizzonte degli eventi aumenta la risoluzione K-segmenti.
Dilatazione temporale e redshift emergono dalla struttura spazio-temporale.
Sfera fotonica e orbite restano stabili – osservabile in Sagittarius A stella.
"""
}

# ============================================================================
# PART 5: STELLAR NUCLEOSYNTHESIS - LIFE PREREQUISITES
# ============================================================================

PART5_AUDIO_TEXTS = {
    'de': """
Leben braucht schwere Elemente: Kohlenstoff, Sauerstoff, Eisen.
Sie entstehen in Sternen durch Fusion – der Kohlenstoff-Sauerstoff-Zyklus.
SSZ beschreibt die Raumzeit im Sterninneren: Hohe Segmentdichte, Fusionszone stabil.
Supernovae verteilen diese Elemente – Grundlage für Planeten und Leben.
""",
    
    'en': """
Life requires heavy elements: Carbon, oxygen, iron.
They form in stars through fusion – the carbon-oxygen cycle.
SSZ describes spacetime inside stars: High segment density, stable fusion zone.
Supernovae distribute these elements – foundation for planets and life.
""",
    
    'it': """
La vita richiede elementi pesanti: Carbonio, ossigeno, ferro.
Si formano nelle stelle tramite fusione – il ciclo carbonio-ossigeno.
SSZ descrive lo spazio-tempo all'interno delle stelle: Alta densità di segmenti, zona di fusione stabile.
Le supernovae distribuiscono questi elementi – fondamento per pianeti e vita.
"""
}

# ============================================================================
# VIDEO CONFIGURATION - EXTENDED TO 5 PARTS
# ============================================================================

VIDEO_CONFIG = {
    'fps': 30,
    'resolution': (1920, 1080),
    'parts': [
        {
            'id': 1,
            'name': 'intro',
            'gif': 'ssz_intro_{lang}.gif',  # Singularity vs Segmentation
            'duration_de': 19.0,
            'duration_en': 18.5,
            'duration_it': 19.5,
            'audio_file': 'part1_intro_{lang}.mp3'
        },
        {
            'id': 2,
            'name': 'cosmo',
            'gif': 'ssz_cosmo_anim.gif',  # Cosmological Evidence
            'duration_de': 19.0,
            'duration_en': 18.5,
            'duration_it': 19.5,
            'audio_file': 'part2_cosmo_{lang}.mp3'
        },
        {
            'id': 3,
            'name': 'stability',
            'gif': 'ssz_proof_anim_v6.gif',  # Mathematical Stability
            'duration_de': 19.5,
            'duration_en': 19.0,
            'duration_it': 20.0,
            'audio_file': 'part3_stability_{lang}.mp3'
        },
        {
            'id': 4,
            'name': 'blackhole',
            'gif': 'blackhole_segmented_spacetime.gif',  # Black Hole SSZ
            'duration_de': 20.0,
            'duration_en': 19.5,
            'duration_it': 20.5,
            'audio_file': 'part4_blackhole_{lang}.mp3'
        },
        {
            'id': 5,
            'name': 'nucleosynthesis',
            'gif': 'ssz_stellar_nucleosynthesis.gif',  # Stellar Life Prerequisites (NEU!)
            'duration_de': 20.5,
            'duration_en': 20.0,
            'duration_it': 21.0,
            'audio_file': 'part5_nucleosynthesis_{lang}.mp3'
        }
    ],
    'languages': ['de', 'en', 'it'],
    'voices': {
        'de': 'de-DE-KatjaNeural',     # Deutsche Stimme
        'en': 'en-GB-SoniaNeural',     # Britische Stimme
        'it': 'it-IT-ElsaNeural'       # Italienische Stimme
    }
}

# ============================================================================
# COMPLETE SCRIPT COLLECTION
# ============================================================================

ALL_AUDIO_TEXTS = {
    'part1_intro': {
        'de': """
Klassisches Big-Bang-Modell: Singularität, unendliche Dichte.
Segmentierte Raumzeit: Raum entsteht durch Segmentierung.
Keine Singularität. Endliche Dichten. Stabilität von Anfang an.
""",
        'en': """
Classical Big Bang model: Singularity, infinite density.
Segmented Spacetime: Space emerges through segmentation.
No singularity. Finite densities. Stability from the start.
""",
        'it': """
Modello Big Bang classico: Singolarità, densità infinita.
Spazio-Tempo Segmentato: Lo spazio emerge dalla segmentazione.
Nessuna singolarità. Densità finite. Stabilità dall'inizio.
"""
    },
    
    'part2_cosmo': {
        'de': """
Kosmologische Beobachtungen: Hubble-Expansion, akustische Oszillationen, Supernovae.
SSZ passt zu allen Daten. Lambda A Kopplungsparameter erklärt Dunkle Energie.
Kompatibel mit Planck, SDSS, WMAP.
""",
        'en': """
Cosmological observations: Hubble expansion, acoustic oscillations, supernovae.
SSZ fits all data. Lambda A coupling explains dark energy.
Compatible with Planck, SDSS, WMAP.
""",
        'it': """
Osservazioni cosmologiche: Espansione Hubble, oscillazioni acustiche, supernovae.
SSZ si adatta a tutti i dati. Lambda A accoppiamento spiega energia oscura.
Compatibile con Planck, SDSS, WMAP.
"""
    },
    
    'part3_stability': {
        'de': """
Mathematischer Beweis: C2 Metrik, glatte Kontinuität.
K-Segment Auflösung steuerbar. Stabilitätsbereich für Lambda A ermittelt.
Kein Instabilitätswachstum. Physikalisch konsistent.
""",
        'en': """
Mathematical proof: C2 metric, smooth continuity.
K-segment resolution controllable. Stability range for Lambda A determined.
No instability growth. Physically consistent.
""",
        'it': """
Prova matematica: Metrica C2, continuità smooth.
Risoluzione K-segmenti controllabile. Range stabilità per Lambda A determinato.
Nessuna crescita instabilità. Fisicamente consistente.
"""
    },
    
    'part4_blackhole': PART4_AUDIO_TEXTS,
    
    'part5_nucleosynthesis': PART5_AUDIO_TEXTS
}

# ============================================================================
# METADATA
# ============================================================================

METADATA = {
    'title': {
        'de': 'SSZ Kosmologie – Vom Big Bang bis zur Entstehung von Leben',
        'en': 'SSZ Cosmology – From Big Bang to Origin of Life',
        'it': 'SSZ Cosmologia – Dal Big Bang all\'Origine della Vita'
    },
    'description': {
        'de': '''Wissenschaftliche Animation über Segmentierte Raumzeit (SSZ).

Teil 1 (0:00): Singularität vs. Segmentierung
Teil 2 (0:19): Kosmologische Beobachtungen
Teil 3 (0:38): Mathematischer Stabilitätsbeweis
Teil 4 (0:58): Schwarze Löcher in SSZ
Teil 5 (1:18): Stellare Nukleosynthese – Leben

© 2025 Carmen Wrede, Lino Casu
https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results''',
        
        'en': '''Scientific animation about Segmented Spacetime (SSZ).

Part 1 (0:00): Singularity vs. Segmentation
Part 2 (0:19): Cosmological Observations
Part 3 (0:38): Mathematical Stability Proof
Part 4 (0:58): Black Holes in SSZ
Part 5 (1:18): Stellar Nucleosynthesis – Life

© 2025 Carmen Wrede, Lino Casu
https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results''',
        
        'it': '''Animazione scientifica sullo Spazio-Tempo Segmentato (SSZ).

Parte 1 (0:00): Singolarità vs. Segmentazione
Parte 2 (0:19): Osservazioni Cosmologiche
Parte 3 (0:38): Prova Matematica di Stabilità
Parte 4 (0:58): Buchi Neri in SSZ
Parte 5 (1:18): Nucleosintesi Stellare – Vita

© 2025 Carmen Wrede, Lino Casu
https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results'''
    },
    'total_duration': {
        'de': '~99 seconds',
        'en': '~97 seconds', 
        'it': '~101 seconds'
    }
}

if __name__ == '__main__':
    print("="*80)
    print("SSZ TRILINGUAL VIDEO SCRIPTS - EXTENDED TO 5 PARTS")
    print("="*80)
    print("\nVideo Configuration:")
    print(f"  Parts: {len(VIDEO_CONFIG['parts'])}")
    print(f"  Languages: {', '.join(VIDEO_CONFIG['languages'])}")
    print(f"  FPS: {VIDEO_CONFIG['fps']}")
    print(f"  Resolution: {VIDEO_CONFIG['resolution']}")
    
    print("\n" + "-"*80)
    print("PART OVERVIEW:")
    print("-"*80)
    
    for part in VIDEO_CONFIG['parts']:
        print(f"\nPart {part['id']}: {part['name'].upper()}")
        print(f"  GIF: {part['gif']}")
        print(f"  Duration DE: {part['duration_de']}s")
        print(f"  Duration EN: {part['duration_en']}s")
        print(f"  Duration IT: {part['duration_it']}s")
        
        # Preview audio text
        part_key = f"part{part['id']}_{part['name']}"
        if part_key in ALL_AUDIO_TEXTS:
            print(f"\n  Audio Preview (DE):")
            text_de = ALL_AUDIO_TEXTS[part_key]['de'].strip()
            lines = [line.strip() for line in text_de.split('\n') if line.strip()]
            for line in lines[:2]:  # First 2 lines
                print(f"    {line}")
    
    print("\n" + "="*80)
    print("Total Duration Estimate:")
    for lang in ['de', 'en', 'it']:
        total = sum(p[f'duration_{lang}'] for p in VIDEO_CONFIG['parts'])
        print(f"  {lang.upper()}: ~{total:.1f}s")
    
    print("\n" + "="*80)
    print("✅ Script configuration complete!")
    print("="*80)
