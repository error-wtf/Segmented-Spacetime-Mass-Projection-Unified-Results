# Repository Clone & Test Guide

Dieses Repository nutzt **Git LFS (Large File Storage)** für große Dateien (>100 MB).

## 1. Voraussetzungen

Stelle sicher, dass Git LFS installiert ist:

```bash
# Prüfen ob Git LFS verfügbar ist
git lfs version

# Falls nicht installiert:
# Windows: https://git-lfs.github.com/
# macOS: brew install git-lfs
# Linux: sudo apt-get install git-lfs
```

## 2. Repository klonen

### Option A: Mit allen Dateien (klein + groß)

```bash
git clone https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results
cd Segmented-Spacetime-Mass-Projection-Unified-Results
git lfs pull  # Lädt große Dateien herunter (~3.6 GB)
```

### Option B: Nur kleine Dateien (Tests sofort lauffähig)

```bash
git clone https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results
cd Segmented-Spacetime-Mass-Projection-Unified-Results
# Große Dateien NICHT herunterladen
# Tests mit v1/nightly Datasets laufen sofort!
```

## 3. Was ist verfügbar?

### Sofort nach Clone (klein, <100 MB):

#### Models:
```
models/cosmology/2025-10-17_gaia_ssz_v1/ssz_field.parquet         (0.14 MB)
models/cosmology/2025-10-17_gaia_ssz_nightly/ssz_field.parquet    (14.25 MB)
models/solar_system/2025-10-17_gaia_ssz_v1/solar_ssz.json         (0.06 MB)
models/solar_system/2025-10-17_gaia_ssz_nightly/solar_ssz.json    (0.25 MB)
```

#### Data:
```
data/interim/gaia/2025-10-17_gaia_ssz_v1/gaia_clean.parquet       (0.08 MB)
data/interim/gaia/2025-10-17_gaia_ssz_nightly/gaia_clean.parquet  (6.09 MB)
data/raw/gaia/2025-10-17_gaia_ssz_nightly/gaia_dr3_core.parquet   (3.32 MB)
data/raw/sdss/2025-10-17_gaia_ssz_nightly/sdss_catalog.parquet    (0.36 MB)
... und mehr ...
```

**Total: ~36 MB direkt verfügbar**

### Optional via `git lfs pull` (groß, >100 MB):

```
models/cosmology/2025-10-17_gaia_ssz_real/ssz_field.parquet       (1373 MB)
models/solar_system/2025-10-17_gaia_ssz_real/solar_ssz.json       (128 MB)
data/interim/gaia/2025-10-17_gaia_ssz_real/gaia_clean.parquet     (757 MB)
data/interim/gaia/2025-10-17_gaia_ssz_real/gaia_phase_space.parquet (1169 MB)
... und mehr ...
```

**Total: ~3.6 GB optional herunterladbar**

## 4. Tests ausführen

### Mit kleinen Dateien (sofort):

```bash
python run_full_suite.py
# oder
pytest tests/ -v
```

Tests mit v1/nightly Datasets laufen sofort!

### Mit allen Dateien (nach `git lfs pull`):

```bash
git lfs pull  # Erst große Dateien herunterladen
python run_full_suite.py  # Alle Tests inkl. real-data
```

## 5. Verifikation

### Lokales Setup prüfen:

```bash
python verify_lfs_setup.py
```

Sollte zeigen:
```
[SUCCESS] All large files are correctly tracked with Git LFS!
[SUCCESS] Repository is ready to push to GitHub
```

### Clone in neuem Ordner testen:

```bash
python test_clone_and_verify.py
```

Führt einen kompletten Clone-Test durch.

## 6. LFS Status prüfen

### Welche Dateien sind LFS?

```bash
git lfs ls-files
```

### LFS-Statistiken:

```bash
git lfs status
```

### Spezifische Datei prüfen:

```bash
git lfs ls-files | grep "ssz_field"
```

## 7. Troubleshooting

### Problem: "Smudge error" beim Clone

**Ursache:** Git LFS nicht installiert oder nicht initialisiert

**Lösung:**
```bash
git lfs install
git lfs pull
```

### Problem: Große Dateien sind nur Pointer (~1 KB)

**Ursache:** LFS-Objekte wurden nicht heruntergeladen

**Lösung:**
```bash
git lfs pull
```

### Problem: Tests schlagen fehl "FileNotFoundError"

**Ursache 1:** Nur LFS-Pointer vorhanden, echte Dateien fehlen

**Lösung:**
```bash
git lfs pull  # Für gaia_ssz_real Tests
```

**Ursache 2:** Tests erwarten gaia_ssz_real, aber nur v1/nightly verfügbar

**Lösung:**
```bash
# Tests nur mit kleinen Datasets:
pytest tests/ -k "not real"
```

## 8. Für Entwickler

### Neue große Datei hinzufügen:

```bash
# 1. LFS-Tracking aktivieren
git lfs track "path/to/largefile.parquet"

# 2. .gitattributes committen
git add .gitattributes

# 3. Datei hinzufügen
git add path/to/largefile.parquet
git commit -m "Add large file with LFS"

# 4. Push
git push origin main
```

### LFS-Cache leeren:

```bash
git lfs prune
```

## 9. Empfohlener Workflow

### Für normale Entwicklung:

```bash
# 1. Clone ohne große Dateien
git clone <repo-url>

# 2. Arbeite mit v1/nightly Datasets
python run_full_suite.py

# 3. Nur wenn real-data benötigt wird:
git lfs pull
```

### Für vollständige Tests:

```bash
# 1. Clone mit allen Dateien
git clone <repo-url>
cd <repo>
git lfs pull

# 2. Alle Tests
python run_full_suite.py
```

## 10. Vorteile dieser Strategie

✅ **Schneller Clone** - ~2 Minuten statt 20+ Minuten  
✅ **Tests sofort** - v1/nightly Datasets direkt verfügbar  
✅ **Optionale große Dateien** - Nur bei Bedarf herunterladen  
✅ **GitHub-kompatibel** - Keine 100 MB Limit-Probleme  
✅ **Sauber strukturiert** - Klein/groß Dateien getrennt  

---

## Support

Bei Problemen:
1. Prüfe Git LFS Status: `git lfs version`
2. Prüfe lokales Setup: `python verify_lfs_setup.py`
3. Prüfe Clone-Test: `python test_clone_and_verify.py`

---

© 2025 Carmen Wrede, Lino Casu  
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
