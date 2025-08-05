#!/usr/bin/env python3
"""
fetch_ligo_posteriors.py
========================

Lädt Posterior‐Samples (HDF5) für ausgewählte LIGO/Virgo–Gravitationswellen­ereignisse
(GW150914 … GW190814) aus dem Zenodo‑Archiv herunter.

✅ Was das Skript macht
----------------------
* Legt standardmäßig ein Unterverzeichnis **./data** an (per ‑d kann ein anderer
  Pfad angegeben werden).
* Prüft, ob eine Datei bereits existiert und überspringt sie dann.
* Lädt in 1 MiB‑Chunks mit **requests** und zeigt einen hübschen Fortschrittsbalken
  via **tqdm**.
* Fängt Netzwerkfehler ab und bricht das Skript nicht komplett ab, sondern fährt
  mit dem nächsten Event fort.

💾 Voraussetzungen
-----------------
```bash
pip install requests tqdm
```

🖥️ Aufrufbeispiel
----------------
```bash
python fetch_ligo_posteriors.py              # lädt nach ./data
python fetch_ligo_posteriors.py -d ~/gw_pe   # custom‑Verzeichnis
```
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple

import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# 1)  URLs & Event‑Mapping  (PEDataRelease, mixed‑cosmo Posterior‑Samples)
# ---------------------------------------------------------------------------
FILES: List[Tuple[str, str]] = [
    (
        "GW150914",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW170104",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW170104_101158_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW170729",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW170729_185629_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW170809",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW170809_082821_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW170814",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW170814_103043_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW170823",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW170823_131358_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW190412",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW190412_053044_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW190521",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW190521_030229_PEDataRelease_mixed_cosmo.h5",
    ),
    (
        "GW190814",
        "https://zenodo.org/records/6513631/files/IGWN-GWTC2p1-v2-GW190814_211039_PEDataRelease_mixed_cosmo.h5",
    ),
]

# ---------------------------------------------------------------------------
# 2)  Hilfsfunktionen
# ---------------------------------------------------------------------------

def _download(url: str, dest: Path, chunk_size: int = 1 << 20) -> None:
    """Lädt *url* nach *dest* (chunked, mit Fortschrittsbalken)."""

    # HEAD‑Request, um Größe zu erfahren (fällt bei 302 Redirects evtl. weg)
    try:
        with requests.get(url, stream=True, allow_redirects=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            tqdm_kwargs = dict(total=total, unit="B", unit_scale=True, unit_divisor=1024)
            with tqdm(**tqdm_kwargs, desc=dest.name, ascii=" █") as bar:
                with dest.open("wb") as fh:
                    for chunk in r.iter_content(chunk_size):
                        fh.write(chunk)
                        bar.update(len(chunk))
    except Exception:
        # Lösche angefangene Datei, um saubere Restarts zu erlauben
        if dest.exists():
            dest.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# 3)  CLI Entry‑Point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Lädt LIGO/Virgo Posterior‑Samples (GWTC‑2.1 Mixed‑Cosmo)")
    parser.add_argument("-d", "--dir", default="./data", help="Zielverzeichnis (Standard: ./data)")
    args = parser.parse_args()

    target_dir = Path(args.dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    for event, url in FILES:
        dest = target_dir / Path(url).name
        if dest.exists():
            print(f"[SKIP] {event}: {dest.name} existiert bereits → übersprungen")
            continue
        print(f"[DL ] {event}: → {dest}")
        try:
            _download(url, dest)
        except requests.HTTPError as e:
            print(f"[ERR] {event}: HTTP‑Error {e.response.status_code}", file=sys.stderr)
        except Exception as e:
            print(f"[ERR] {event}: {e}", file=sys.stderr)

    print("\n✅ Fertig – alle verfügbaren Posterior‑Dateien geprüft.")


if __name__ == "__main__":
    main()
