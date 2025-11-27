# Theorie & Code – Vollständige Dokumentation

**Segmented Spacetime (SSZ) – Physikalische Grundlagen & Implementierung**

© Carmen Wrede & Lino Casu, 2025  
Licensed under the Anti-Capitalist Software License v1.4

---

## 📚 Übersicht

Diese Dokumentation erklärt **alle physikalischen und mathematischen Grundlagen** der Segmented Spacetime Theorie sowie deren **vollständige Code-Implementierung**.

**Zielgruppe:**
- Physiker:innen, die die Theorie verstehen wollen
- Entwickler:innen, die den Code nachvollziehen wollen
- Studierende, die beide Aspekte lernen wollen

**Struktur:**
1. **Physikalische Grundlagen** – Was ist SSZ? Warum funktioniert es?
2. **Mathematische Formeln** – Alle Gleichungen mit Herleitungen
3. **Code-Implementierung** – Wie werden die Formeln programmiert?
4. **Beispiele & Anwendungen** – Praktische Nutzung

---

## 📖 Dokumentationsteile

### 1️⃣ [Physikalische Grundlagen](PHYSICS_FOUNDATIONS.md)

**Inhalt:**
- **Kernkonzept:** Segmentierte Raumzeit statt kontinuierlicher Raumzeit
- **Goldener Schnitt φ:** Warum φ = (1+√5)/2 zentral ist
- **Masse-Projektion:** Wie Masse die Raumzeit segmentiert
- **Zeit-Dilatation:** Gravitative Zeitverlangsamung
- **Brechungsindex:** Licht in gekrümmter Raumzeit
- **Natürliche Grenze:** Singularitäts-Vermeidung bei Schwarzen Löchern

**Lernziel:** Grundverständnis der Theorie ohne Mathematik

---

### 2️⃣ [Mathematische Formeln](MATHEMATICAL_FORMULAS.md)

**Inhalt:**
- **Segment-Radius:** r_φ = φ·GM/c² · (1 + Δ(M))
- **Δ(M)-Modell:** Massenabhängige Korrektion
- **PPN-Parameter:** β = γ = 1 (GR-Kompatibilität)
- **Dual-Geschwindigkeiten:** v_esc × v_fall = c²
- **Metrischer Tensor:** A(r) = 1 - 2U + 2U² + ε₃U³
- **Energie-Bedingungen:** WEC, DEC, SEC
- **Alle Ableitungen:** Schritt-für-Schritt Beweise

**Lernziel:** Vollständiges mathematisches Verständnis

---

### 3️⃣ [Code-Implementierung](CODE_IMPLEMENTATION_GUIDE.md)

**Inhalt:**
- **Kern-Algorithmen:** Core computation mit Erklärungen
- **Segment-Berechnung:** `rphi_from_mass()`, `delta_percent()`
- **Masse-Inversion:** Newton-Verfahren für M aus r_φ
- **Redshift-Formeln:** z_GR, z_SR, z_combined, z_seg
- **Numerische Präzision:** Decimal-Arithmetik, Fehlerbehandlung
- **Test-Framework:** Wie Physik-Tests funktionieren
- **Code-Schnipsel:** Alle wichtigen Funktionen dokumentiert

**Lernziel:** Code-Verständnis und Reproduzierbarkeit

---

### 4️⃣ [Beispiele & Anwendungen](EXAMPLES_AND_APPLICATIONS.md)

**Inhalt:**
- **Beispiel 1:** Massenberechnung für Sonne
- **Beispiel 2:** Schwarzes Loch (Sgr A*)
- **Beispiel 3:** Redshift-Analyse GAIA-Daten
- **Beispiel 4:** Multi-Ring-Validierung (G79, Cygnus X)
- **Beispiel 5:** Hawking-Strahlung Proxy
- **Anwendungsfall 1:** Galaktische Analyse
- **Anwendungsfall 2:** Kosmologische Distanzen
- **Anwendungsfall 3:** Gravitationswellen-Proxy

**Lernziel:** Praktische Anwendung der Theorie

---

## 🎯 Schnellstart

### Für Physiker:innen
```
1. PHYSICS_FOUNDATIONS.md lesen
2. MATHEMATICAL_FORMULAS.md studieren
3. Paper in papers/ lesen
```

### Für Entwickler:innen
```
1. CODE_IMPLEMENTATION_GUIDE.md lesen
2. Beispiele in EXAMPLES_AND_APPLICATIONS.md durchgehen
3. Tests in tests/ ausführen
```

### Für Studierende
```
1. Alle Dokumente in Reihenfolge lesen
2. Beispiele nachrechnen
3. Tests verstehen und modifizieren
```

---

## 🔬 Kernkonzepte im Überblick

### 1. Segmentierte Raumzeit

**Konzept:**
- Raumzeit besteht aus diskreten φ-Segmenten
- Segment-Dichte N(x) variiert mit Masse
- Zeit fließt segmentweise mit τ(x) = φ^(-α·N(x))

**Warum?**
- Erklärt Gravitation geometrisch
- Vermeidet Singularitäten
- Kompatibel mit GR im Schwach-Feld

### 2. Goldener Schnitt φ

**Definition:**
```
φ = (1 + √5)/2 ≈ 1.618033988749...
φ² = φ + 1
```

**Rolle:**
- Fundamentale Zeitstruktur
- Selbstähnliche Segmentierung
- Optimale Raumzeit-Packung

### 3. Masse-Projektion

**Formel:**
```
r_φ = φ · GM/c² · (1 + Δ(M)/100)
```

**Bedeutung:**
- r_φ: charakteristischer Radius der Masse M
- Δ(M): massenabhängige Korrektion
- Vergleich: r_s = 2GM/c² (Schwarzschild)

### 4. Dual-Geschwindigkeiten

**Invariante:**
```
v_esc(r) × v_fall(r) = c²
```

**Physik:**
- v_esc: klassische Fluchtgeschwindigkeit
- v_fall: duale Fallgeschwindigkeit (segment-basiert)
- Invariante gilt exakt (Maschinengenauigkeit!)

---

## 📊 Tests & Validierung

### Physik-Tests (35 Tests)
```
test_ppn_exact.py           - PPN Parameter β, γ
test_vfall_duality.py       - Dual-Geschwindigkeiten
test_energy_conditions.py   - Energie-Bedingungen
test_c1_segments.py         - C1-Kontinuität
test_c2_segments_strict.py  - C2-Kontinuität
test_segwave_core.py        - 16 SegWave-Tests
... (siehe PHYSICS_TESTS_COMPLETE_LIST.md)
```

### Code ausführen:
```bash
# Alle Tests
python run_full_suite.py

# Einzelner Test
python test_ppn_exact.py

# Mit Details
pytest tests/ -s -v
```

---

## 🔗 Verwandte Dokumentation

**Theorie-Papers:**
- `papers/SegmentedSpacetime-ANewPerspectiveonLightGravityandBlackHoles.md`
- `papers/DualVelocitiesinSegmentedSpacetime.md`
- `papers/Segment-BasedGroupVelocity.md`
- `papers/SegmentedSpacetimeandtheNaturalBoundaryofBlackHoles.md`

**Installation & Nutzung:**
- `README.md` – Hauptdokumentation
- `QUICKSTART.md` – Schnellstart-Anleitung
- `INSTALL.md` – Detaillierte Installation
- `TESTING_COMPLETE_GUIDE.md` – Test-Framework

**Daten & Analyse:**
- `DATA_USAGE_SUMMARY.md` – Datensatz-Beschreibung
- `COMPREHENSIVE_DATA_ANALYSIS.md` – Statistische Analysen
- `PIPELINE_OUTPUT_DOCUMENTATION.md` – Output-Formate

---

## 💡 Didaktischer Aufbau

### Niveau 1: Konzeptverständnis
→ **PHYSICS_FOUNDATIONS.md**
- Keine Formeln
- Intuitive Erklärungen
- Visualisierungen

### Niveau 2: Mathematische Grundlagen
→ **MATHEMATICAL_FORMULAS.md**
- Alle Formeln
- Herleitungen
- Beweise

### Niveau 3: Implementierung
→ **CODE_IMPLEMENTATION_GUIDE.md**
- Algorithmen
- Code-Snippets
- Best Practices

### Niveau 4: Anwendung
→ **EXAMPLES_AND_APPLICATIONS.md**
- Praktische Beispiele
- Use Cases
- Ergebnisinterpretation

---

## 🛠️ Weitere Ressourcen

**Interaktive Tools:**
- `ssz_interactive_gui.py` – GUI für SSZ-Berechnungen
- `SSZ_Full_Pipeline_Colab.ipynb` – Google Colab Notebook
- `notebooks/demo.ipynb` – Jupyter Demo

**Skripte:**
- `segspace_all_in_one_extended.py` – Haupt-Analyse
- `ssz_theory_segmented.py` – Theorie-Berechnungen
- `run_all_ssz_terminal.py` – Komplette Test-Suite

**Visualisierungen:**
- `segspace_comparison.png` – Modell-Vergleich
- `mass_binned_medians.png` – Massen-Analyse
- `figures/` – Alle generierten Plots

---

## ✅ Checkliste für Leser:innen

**Physik verstehen:**
- [ ] PHYSICS_FOUNDATIONS.md gelesen
- [ ] Kernkonzepte verstanden (Segmente, φ, Masse-Projektion)
- [ ] Mindestens 3 Paper gelesen

**Mathematik nachvollziehen:**
- [ ] MATHEMATICAL_FORMULAS.md durchgearbeitet
- [ ] Alle Ableitungen nachgerechnet
- [ ] PPN-Parameter verstanden

**Code reproduzieren:**
- [ ] CODE_IMPLEMENTATION_GUIDE.md studiert
- [ ] Installation erfolgreich (install.sh/ps1)
- [ ] Alle Tests bestanden (run_full_suite.py)
- [ ] Eigene Beispiele programmiert

**Anwenden:**
- [ ] EXAMPLES_AND_APPLICATIONS.md gelesen
- [ ] Mindestens 1 Use Case selbst durchgeführt
- [ ] Eigene Daten analysiert

---

## 📧 Kontakt & Beitrag

**Autoren:**
- Carmen Wrede
- Lino Casu

**Repository:**
- https://github.com/error-wtf/Segmented-Spacetime-Mass-Projection-Unified-Results

**Lizenz:**
- Anti-Capitalist Software License v1.4
- Siehe `LICENSE` für Details

**Beitrag:**
- Issues: Fehler melden
- Pull Requests: Verbesserungen vorschlagen
- Diskussionen: Theorie diskutieren

---

**Viel Erfolg beim Lernen! 🚀**
