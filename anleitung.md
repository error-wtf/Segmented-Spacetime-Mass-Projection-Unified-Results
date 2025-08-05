````markdown
# Anleitung zur Nutzung des „Segmented LIGO Compare“ Workflows

Diese Anleitung zeigt Schritt für Schritt, wie du  
1. die notwendigen Python-Pakete installierst,  
2. offizielle LIGO‐Daten herunterlädst,  
3. dein Segment-Spacetime-Signal erzeugst,  
4. beides vergleichst  
und 5. die Ergebnisse interpretierst.

---

## 1. Voraussetzungen

- **Python 3.8+**  
- **Git** (optional, um Repositories zu klonen)  
- Schreibrechte im Arbeitsverzeichnis  

---

## 2. Installation der Python-Abhängigkeiten

```bash
# 1) Erstelle und aktiviere ggf. eine virtuelle Umgebung:
python3 -m venv venv
source venv/bin/activate

# 2) Installiere die benötigten Pakete:
pip install gwpy gwosc h5py numpy pandas matplotlib
````

---

## 3. Herunterladen der offiziellen LIGO-Strain-Daten

Wir verwenden das mitgelieferte Skript `fetch_missing_ligo.py`.

### 3.1 Download per GPS-Zeitbereich

```bash
# Beispiel: GW150914, H1-Detektor, GPS 1126257415–1126257447
python fetch_missing_ligo.py time \
    --detector H1 \
    --start 1126257415 --end 1126257447 \
    --outdir data/GW150914_time/
```

**Ergebnis:** In `data/GW150914_time/` liegt nun z. B.

```
H-H1_GWOSC_4KHZ_R1-1126257415-4096.hdf5
```

---

## 4. Erzeugen deines Segment-Spacetime-Signals

Ersetze `your_segmented_output.hdf5` durch den Pfad zu deinem .hdf5-Output,
der dein segment-spacetime-Signal enthält.

> **Hinweis:** Dieses Skript ist individuell – stelle sicher, dass dein HDF5
> eine Dataset-Gruppe namens `/strain` enthält.

```bash
# Beispiel (Pseudocode):
python dein_segmented_spacetime_generator.py \
    --input-strain data/GW150914_time/H-H1_GWOSC_4KHZ_R1-1126257415-4096.hdf5 \
    --output data/GW150914_time/segmented_output.hdf5 \
    --window 100
```

---

## 5. Vergleich beider Signale

Nutze das fertige Vergleichs-Skript `segmented_ligo_compare_fixed.py`:

```bash
python segmented_ligo_compare_fixed.py \
  --detector H1 \
  --start 1126257415 --end 1126257447 \
  --obsfile  data/GW150914_time/H-H1_GWOSC_4KHZ_R1-1126257415-4096.hdf5 \
  --sstfile  data/GW150914_time/segmented_output.hdf5 \
  --outcsv   compare.csv
```

* `--obsfile`: Pfad zur offiziellen LIGO-HDF5
* `--sstfile`: Pfad zum selbst erzeugten SST-HDF5
* `--outcsv`: Name der Ausgabedatei (CSV)

Nach dem Lauf findest du in `compare.csv` drei Spalten:

| time     | h\_obs      | h\_sst     | residual  |
| -------- | ----------- | ---------- | --------- |
| GPS-Zeit | LIGO-Strain | SST-Strain | Differenz |

---

## 6. Interpretation der Ergebnisse

1. **residual = 0**
   Dein SST-Signal deckt das offizielle Signal exakt ab.
2. **kleine Residuen (< 1e-23)**
   Reproduziert, aber mit minimalem numerischem Rauschen.
3. **größere Residuen**
   Prüfe Window-Länge, Samplingrate oder Offset in deinem Generator.

---

## 7. Troubleshooting

* **„KeyError“ beim Zugriff auf HDF5-Gruppen**
  → Prüfe Gruppennamen (z. B. `/H1/Strain` vs. `/strain`).
* **„ValueError: Cannot find dataset…“**
  → Prüfe die GPS-Zeitgrenzen und die verfügbaren Dateien in `data/`.
* **Andere Fehler**
  → Lies die Fehlermeldung, vergewissere dich, dass die Pfade korrekt sind.

---

## 8. Weiterführende Tipps

* Plotte die Residuen mit Python/Matplotlib, um systematische Abweichungen zu erkennen.
* Vergleiche mehrere Events (z. B. GW151226, GW170104) mit identischem Workflow.
* Automatisiere den Prozess in einem Makefile oder Notebook.

---

Viel Erfolg bei der Reproduktion deiner SST-Analysen!
Falls du noch Fragen hast, melde dich gerne.
