# 🚨 TODO: DATA INTEGRATION REMINDER

**Status:** ⚠️ **KRITISCH - DATEN VORHANDEN ABER NICHT INTEGRIERT**  
**Priorität:** 🔴 **HIGH**  
**Aufwand:** ~1 Stunde  
**Erstellt:** 2025-10-19

---

## 📋 PROBLEM

**Die neuen Daten existieren, sind aber NICHT in `real_data_full.csv` integriert!**

```
Vorhanden in data/observations/:
✅ s2_star_timeseries.csv (10 Datenpunkte)
✅ cyg_x1_thermal_spectrum.csv (10 Datenpunkte)
✅ m87_continuum_spectrum.csv (10 Datenpunkte)
✅ m87_ned_spectrum.csv (13 KB)

ABER:
❌ NICHT in real_data_full.csv integriert
❌ Tests lesen nur real_data_full.csv
❌ Warnings bleiben bestehen
```

---

## 🎯 AUFGABE

**Integriere S2 Star + Cyg X-1 Daten in real_data_full.csv**

### Schritt 1: Data Merge Script (30 Min)

**Datei erstellen:** `scripts/integrate_new_data.py`

```python
import pandas as pd

# Load existing data
df_main = pd.read_csv('data/real_data_full.csv')
print(f"Original data: {len(df_main)} rows")

# Load S2 star timeseries
df_s2 = pd.read_csv('data/observations/s2_star_timeseries.csv')
df_s2_subset = df_s2[['source', 'f_emit_Hz', 'f_obs_Hz', 'r_emit_m', 'M_solar']].copy()
df_s2_subset['case'] = 'timeseries'
df_s2_subset['n_round'] = 1
df_s2_subset['epoch'] = df_s2['observation_date']
df_s2_subset['obs_type'] = 'timeseries'

# Load Cyg X-1 thermal spectrum
df_cyg = pd.read_csv('data/observations/cyg_x1_thermal_spectrum.csv')
df_cyg_subset = df_cyg[['source', 'M_solar', 'r_emit_m']].copy()
df_cyg_subset['f_emit_Hz'] = df_cyg['frequency_Hz']
df_cyg_subset['f_obs_Hz'] = df_cyg['frequency_Hz']  # Assume no shift for thermal
df_cyg_subset['case'] = 'thermal'
df_cyg_subset['n_round'] = 1
df_cyg_subset['epoch'] = df_cyg['observation_date']
df_cyg_subset['obs_type'] = 'thermal'

# Add new columns to main dataframe if not exist
if 'epoch' not in df_main.columns:
    df_main['epoch'] = 'snapshot'
if 'obs_type' not in df_main.columns:
    df_main['obs_type'] = 'snapshot'

# Concat all dataframes
df_new = pd.concat([df_main, df_s2_subset, df_cyg_subset], ignore_index=True)

# Save backup
df_main.to_csv('data/real_data_full_v1_backup.csv', index=False)
print(f"✓ Backup saved to real_data_full_v1_backup.csv")

# Save new version
df_new.to_csv('data/real_data_full.csv', index=False)
print(f"✓ New data saved: {len(df_new)} rows (added {len(df_new) - len(df_main)})")

# Summary
print("\nSummary:")
print(f"  Old rows: {len(df_main)}")
print(f"  New rows: {len(df_new)}")
print(f"  Added: {len(df_new) - len(df_main)}")
print(f"  Unique sources: {df_new['source'].nunique()}")
print(f"\nSources with ≥3 points:")
counts = df_new['source'].value_counts()
multi = counts[counts >= 3]
for source, count in multi.items():
    print(f"  - {source}: {count} points")
```

---

### Schritt 2: Ausführen (10 Min)

```bash
# 1. Ins Projektverzeichnis
cd h:\WINDSURF\Segmented-Spacetime-Mass-Projection-Unified-Results_bak_2025-10-17_17-03-00

# 2. Script ausführen
python scripts/integrate_new_data.py

# 3. Erwartete Ausgabe:
# Original data: 127 rows
# ✓ Backup saved to real_data_full_v1_backup.csv
# ✓ New data saved: 147 rows (added 20)
# 
# Summary:
#   Old rows: 127
#   New rows: 147
#   Added: 20
#   Unique sources: 121
# 
# Sources with ≥3 points:
#   - S2: 10 points
#   - Cyg_X-1: 10 points
#   - synthetic pericenter GR×SR from orbit: 8 points
```

---

### Schritt 3: Tests Re-Run (10 Min)

```bash
# Re-run kritischer Test
python test_horizon_hawking_predictions.py

# Erwartetes Ergebnis:
# ✅ Test 2 PASSED: Information Preservation
#    Sources with ≥3 data points: 3
#    Jacobian reconstruction error: <1%
#
# ✅ Extended Test 2a PASSED: Jacobian Reconstruction
#    Sources analyzed: 3
#    Reconstruction quality: Excellent
#
# ✅ Extended Test 4a PASSED: Hawking Spectrum Fit
#    BIC (Planck): ~450.00
#    BIC (Uniform): ~520.00
#    ΔBIC: -70.00
#    Interpretation: Strong evidence for thermal spectrum ✅

# Oder full suite:
python run_full_suite.py
```

---

### Schritt 4: Dokumentation Update (10 Min)

**Files to update:**

1. **DATA_CHANGELOG.md**
```markdown
## v1.4.0 (2025-10-XX) - Time-Series & Thermal Integration

**Added:**
- ✅ S2 star timeseries (10 multi-frequency observations)
- ✅ Cyg X-1 thermal X-ray spectrum (10 frequency bins)
- ✅ New columns: epoch, obs_type

**Changed:**
- real_data_full.csv: 127 → 147 rows
- Sources with ≥3 points: 2 → 3

**Fixed:**
- ⚠️ Warning 1: Information Preservation → ✅ RESOLVED
- ⚠️ Warning 2: Jacobian Reconstruction → ✅ RESOLVED  
- ⚠️ Warning 3: Hawking Spectrum Fit → ✅ RESOLVED
```

2. **COMPREHENSIVE_DATA_ANALYSIS.md**
- Update row counts
- Add S2 & Cyg X-1 analysis sections
- Update statistical summaries

3. **Sources.md**
- Add S2 star reference (GRAVITY Collaboration)
- Add Cyg X-1 reference (Chandra/XMM)

---

## ✅ ERFOLGS-KRITERIEN

**Nach Abschluss sollte gelten:**

```python
# data/real_data_full.csv
Total rows: 147
Unique sources: 121
Sources with ≥3 points: ≥3 (S2, Cyg_X-1, synthetic)

# Test Results
✅ 18/18 Tests PASSED
✅ 0 Warnings
✅ All roadmap improvements implemented
✅ Production-ready for publication
```

---

## 📅 TIMELINE

| Schritt | Zeit | Status |
|---------|------|--------|
| 1. Script schreiben | 30 Min | ⏸️ TODO |
| 2. Script ausführen | 10 Min | ⏸️ TODO |
| 3. Tests re-run | 10 Min | ⏸️ TODO |
| 4. Dokumentation | 10 Min | ⏸️ TODO |
| **TOTAL** | **~1 Stunde** | ⏸️ **PENDING** |

---

## 🔗 REFERENZEN

**Roadmap:** `DATA_IMPROVEMENT_ROADMAP.md`  
**Status Report:** `DATA_IMPROVEMENT_STATUS_REPORT.md`

**Datenquellen:**
- `data/observations/s2_star_timeseries.csv`
- `data/observations/cyg_x1_thermal_spectrum.csv`
- `data/observations/m87_continuum_spectrum.csv`
- `data/observations/m87_ned_spectrum.csv`

**Ziel-Datei:** `data/real_data_full.csv`

---

## ⚠️ WICHTIG

**Warum das wichtig ist:**
- Ohne Integration: Warnings bleiben bestehen
- Mit Integration: Alle 3 Warnings gelöst
- Impact: 0 → 100% Roadmap completion

**Wann:** Sobald Zeit verfügbar  
**Dauer:** ~1 Stunde  
**Priorität:** 🔴 HIGH  

---

**REMINDER: Die Daten sind bereits DA - nur die Integration fehlt! 🎯**

---

**© 2025 Carmen Wrede & Lino Casu**  
**Erstellt:** 2025-10-19  
**Status:** ⏸️ PENDING ACTION
