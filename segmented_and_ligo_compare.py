#!/usr/bin/env python3
import subprocess
import os
import pandas as pd

# 1) Liste der Ereignisse (O1–O3 GWOSC-Katalog)
events = [
    "GW150914", "GW151012", "GW151226",
    "GW170104", "GW170608", "GW170814", "GW170817",
    "GW190408_181802", "GW190412", "GW190413_052954",
    "GW190421_213856", "GW190424_180648", "GW190425",
    "GW190426_152155", "GW190503_185404", "GW190512_180714",
    "GW190517_055101", "GW190519_153544", "GW190521",
    # …du kannst hier die komplette Liste aus GWOSC ergänzen
]

detector = "H1"
duration = 32             # Sekunden um das Ereignis
outdir = "data"           # Arbeitsverzeichnis für Downloads & SST-Output
master_results = []

for evt in events:
    print(f"\n=== Bearbeite {evt} ===")
    # a) Offizielle LIGO-Daten holen
    subprocess.run([
        "python", "fetch_missing_ligo.py",
        "event", "--event", evt,
        "--detector", detector,
        "--duration", str(duration),
        "--outdir", outdir
    ], check=True)

    # b) SST-Signal erzeugen (Beispiel-Aufruf; passe ggf. Parameter an)
    subprocess.run([
        "python", "segmented_mass.py",
        "--input", os.path.join(outdir, f"{detector}-{evt}-segmented_input.hdf5"),
        "--output", os.path.join(outdir, f"{evt}_segmented_output.hdf5")
    ], check=True)

    # c) Vergleichsskript ausführen
    outcsv = f"compare_{evt}.csv"
    subprocess.run([
        "python", "segmented_ligo_compare_fixed.py",
        "--detector", detector,
        "--start",    str(get_gps_time(evt) - duration//2),
        "--end",      str(get_gps_time(evt) + duration//2),
        "--obsfile",  os.path.join(outdir, f"{detector}_{evt}_GWOSC.hdf5"),
        "--sstfile",  os.path.join(outdir, f"{evt}_segmented_output.hdf5"),
        "--outcsv",   outcsv
    ], check=True)

    # d) CSV einlesen und markieren
    df = pd.read_csv(outcsv)
    df["Event"] = evt
    master_results.append(df)

# 2) Alle Ergebnisse zusammenführen und speichern
all_df = pd.concat(master_results, ignore_index=True)
all_df.to_csv("compare_all_events.csv", index=False)
print("\n✅ Alle Vergleiche in compare_all_events.csv gespeichert.")
