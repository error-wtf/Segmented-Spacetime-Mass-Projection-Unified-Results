#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trilingual Video Producer für SSZ vs. Big Bang Animation
Erstellt Videos mit wissenschaftlich korrekter Audiobeschreibung in DE/EN/IT

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Dict


# UTF-8 Setup für Windows
def setup_utf8():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def run_production(
    script_path: Path,
    language: str,
    outdir: Path,
    duration: float = 25.0,
    fps: int = 30,
    dpi: int = 160
) -> bool:
    """Führt die Video-Produktion für eine Sprache aus."""
    
    basename = f"ssz_vs_bigbang_{language}"
    
    cmd = [
        sys.executable,
        str(script_path),
        "--language", language,
        "--outdir", str(outdir),
        "--basename", basename,
        "--duration", str(duration),
        "--fps", str(fps),
        "--dpi", str(dpi)
    ]
    
    print(f"\n{'='*80}")
    print(f"🎬 PRODUKTION STARTEN: {language.upper()}")
    print(f"{'='*80}")
    print(f"Output: {outdir / basename}.mp4")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            encoding='utf-8',
            errors='replace',
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        success = result.returncode == 0
        
        if success:
            print(f"\n✅ {language.upper()} erfolgreich produziert!")
        else:
            print(f"\n❌ {language.upper()} fehlgeschlagen (Exit Code: {result.returncode})")
        
        return success
        
    except Exception as e:
        print(f"\n❌ FEHLER bei {language.upper()}: {e}")
        return False


def check_dependencies() -> Dict[str, bool]:
    """Prüft, welche TTS-Engines verfügbar sind."""
    
    deps = {
        'edge-tts': False,
        'espeak': False,
        'ffmpeg': False,
        'imageio': False
    }
    
    # CLI-Tools prüfen
    import shutil
    for tool in ['edge-tts', 'espeak', 'ffmpeg']:
        deps[tool] = shutil.which(tool) is not None
    
    # Python-Module prüfen
    try:
        import imageio
        deps['imageio'] = True
    except ImportError:
        pass
    
    return deps


def print_dependency_report(deps: Dict[str, bool]) -> None:
    """Zeigt verfügbare Abhängigkeiten an."""
    
    print("\n" + "="*80)
    print("ABHÄNGIGKEITEN")
    print("="*80)
    
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"{status} {name:15s} {'verfügbar' if available else 'NICHT verfügbar'}")
    
    print()
    
    if not deps['imageio']:
        print("⚠️  WARNUNG: imageio nicht verfügbar - MP4 Export könnte fehlschlagen")
        print("   Installation: pip install imageio imageio-ffmpeg")
    
    if not any([deps['edge-tts'], deps['espeak']]):
        print("⚠️  WARNUNG: Keine TTS-Engine verfügbar - kein Voiceover möglich")
        print("   Empfehlung: pip install edge-tts")
    
    print()


def main():
    setup_utf8()
    
    # Pfade konfigurieren
    script_path = Path(__file__).parent / "ssz_bigbang_vs_ssz_anim.py"
    outdir = Path("D:/SSZ_Videos_Trilingual")
    
    if not script_path.exists():
        print(f"❌ FEHLER: Script nicht gefunden: {script_path}")
        return 1
    
    # Output-Verzeichnis erstellen
    outdir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("SSZ VS. BIG BANG - TRILINGUAL VIDEO PRODUCER")
    print("="*80)
    print(f"Script:  {script_path}")
    print(f"Output:  {outdir}")
    print()
    
    # Abhängigkeiten prüfen
    deps = check_dependencies()
    print_dependency_report(deps)
    
    # Produktions-Konfiguration
    languages = ['de', 'en', 'it']
    duration = 25.0  # Sekunden
    fps = 30
    dpi = 160
    
    # Produktion für alle Sprachen
    results: Dict[str, bool] = {}
    
    for lang in languages:
        success = run_production(
            script_path=script_path,
            language=lang,
            outdir=outdir,
            duration=duration,
            fps=fps,
            dpi=dpi
        )
        results[lang] = success
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("PRODUKTIONS-ZUSAMMENFASSUNG")
    print("="*80)
    
    for lang, success in results.items():
        status = "✅" if success else "❌"
        filename = f"ssz_vs_bigbang_{lang}.mp4"
        print(f"{status} {lang.upper():4s} - {filename}")
    
    total = len(results)
    succeeded = sum(1 for s in results.values() if s)
    
    print()
    print(f"Erfolgreich: {succeeded}/{total}")
    print(f"Output-Verzeichnis: {outdir}")
    print("="*80)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
