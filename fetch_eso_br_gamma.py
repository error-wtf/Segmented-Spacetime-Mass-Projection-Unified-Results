#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_eso_br_gamma.py
---------------------
Programmatischer Fetch von S2/S0-2 Spektren aus dem ESO Science Archive (astroquery-ESO),
Extraktion des Brackett-γ-Linienzentrums je Epoche und Berechnung von f_obs und z.

FUNKTION
- Sucht nach SPECTRUM/SCIENCE-Products in K-Band (ca. 2.0–2.4 µm) um Sgr A* bzw. Zielnamen ("S2", "S0-2").
- Lädt die Datensätze (Phase 3 bevorzugt), parselt 1D-Spektren und findet das Brγ-Linienzentrum.
- Schreibt CSV: epoch(MJD), instrument, lambda0_um, f_emit_Hz, f_obs_Hz, z, source, notes.

ANFORDERUNGEN
- Python 3.9+
- numpy, pandas, astropy, astroquery, scipy (optional, für Savitzky-Golay-Glättung)
Install: pip install numpy pandas astropy astroquery scipy

AUTHENTIFIZIERUNG
- Für manche ESO-Downloads ist ein Login notwendig.
  Setze Umgebungsvariablen:
    ESO_USERNAME=dein_user
    ESO_PASSWORD=dein_pass

BEISPIELE
- Standard (Name "S2", 5' Radius, nur SINFONI/GRAVITY, max 15 Dateien):
    python fetch_eso_br_gamma.py --target S2 --radius 5m --instruments SINFONI GRAVITY --max 15 --out s2_br_gamma.csv

- Positionssuche (Koordinaten Sgr A*; 10' Radius):
    python fetch_eso_br_gamma.py --ra 266.416837 --dec -29.007810 --radius 10m --out s2_pos.csv

- Nur parsen, ohne erneut zu laden (lokaler Ordner mit FITS):
    python fetch_eso_br_gamma.py --local-dir ./eso_spectra --out parsed.csv --skip-download

HINWEISE
- Die automatische Linienfindung nutzt ein lokales Minimum (Absorptionslinie) nahe 2.1661 µm.
  Für Emissionslinien kann --line-type emission gesetzt werden.
- IFU-Datacubes (z. B. SINFONI) werden übersprungen, wenn kein 1D-Produkt vorliegt.
- Robustheit: Das Script protokolliert Warnungen und fährt fort, wenn einzelne Dateien nicht lesbar sind.

(c) 2025 Lino Casu & Carmen Wrede. MIT-kompatibel (oder Projektlizenz) – bitte im Repo anpassen.
"""
import os
import sys
import argparse
import math
from typing import Optional, List, Tuple

import numpy as np
import pandas as pd

from astropy.io import fits
from astropy.table import Table
import astropy.units as u
from astropy.time import Time
from astropy.constants import c, h, G
from astropy.coordinates import SkyCoord

# SciPy ist optional – für Glättung/Peak-Refinement
try:
    from scipy.signal import savgol_filter
    SCIPY_OK = True
except Exception:
    SCIPY_OK = False

# astroquery
from astroquery.eso import Eso
from astroquery.simbad import Simbad

SPEED_OF_LIGHT = c.to(u.m/u.s).value  # 299792458.0
PLANCK = h.to(u.J*u.s).value

# Brackett-γ Referenz (Vakuum)
BRGAMMA_LAMBDA0_UM = 2.1661  # µm
BRGAMMA_LAMBDA0_M = BRGAMMA_LAMBDA0_UM * 1e-6  # m
BRGAMMA_F_EMIT_HZ = SPEED_OF_LIGHT / BRGAMMA_LAMBDA0_M


def parse_sexagesimal_radius(s: str) -> u.Quantity:
    """
    Parse Radius-Eingabe mit Suffixen: 's' (arcsec), 'm' (arcmin), 'd' (deg).
    Beispiele: '5m' -> 5 arcmin, '30s' -> 30 arcsec, '0.2d' -> 0.2 deg
    """
    s = s.strip().lower()
    if s.endswith('s'):
        return float(s[:-1]) * u.arcsec
    if s.endswith('m'):
        return float(s[:-1]) * u.arcmin
    if s.endswith('d'):
        return float(s[:-1]) * u.deg
    # default: arcmin
    return float(s) * u.arcmin


def setup_eso() -> Eso:
    eso = Eso()
    # Login falls vorhanden
    user = os.environ.get("ESO_USERNAME")
    pwd = os.environ.get("ESO_PASSWORD")
    if user and pwd:
        try:
            eso.login(user, pwd)
            print(f"[INFO] ESO login ok für Benutzer '{user}'")
        except Exception as e:
            print(f"[WARN] ESO-Login fehlgeschlagen: {e}")
    eso.ROW_LIMIT = 5000
    # Bevorzugt Phase 3
    eso.MAIN_ARCHIVE = True
    eso.QUALITY_CHECK = True
    return eso


def resolve_target(name: str) -> Optional[SkyCoord]:
    try:
        custom = Simbad()
        custom.add_votable_fields('ra(d)', 'dec(d)')
        t = custom.query_object(name)
        if t is None:
            print(f"[WARN] SIMBAD konnte Ziel '{name}' nicht finden.")
            return None
        ra = float(t['RA_d'][0])
        dec = float(t['DEC_d'][0])
        print(f"[INFO] SIMBAD '{name}' → RA={ra:.6f}, Dec={dec:.6f}")
        return SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    except Exception as e:
        print(f"[WARN] SIMBAD-Fehler für '{name}': {e}")
        return None


def query_products(eso: Eso,
                   coord: SkyCoord,
                   radius: u.Quantity,
                   instruments: List[str]) -> Table:
    """
    Sucht nach SPECTRUM/SCIENCE Produkten nahe Position.
    """
    all_rows = None
    for inst in instruments:
        print(f"[INFO] Suche in Instrument='{inst}' um RA={coord.ra.deg:.6f}, Dec={coord.dec.deg:.6f}, r={radius.to(u.arcmin)}")
        try:
            tab = eso.query_instrument(
                instrument=inst,
                coord=coord,
                radius=radius,
                column_filters={
                    'DP.TYPE': 'SCIENCE'
                },
                columns=['DP.ID', 'DP.TYPE', 'TARGET', 'RA', 'DEC', 'MJD-OBS', 'INS.MODE',
                         'INS.DET1.WLEN.START', 'INS.DET1.WLEN.END', 'OBS.NAME', 'TPL.ID',
                         'DP.DPR.TYPE', 'ARCFILE']
            )
        except Exception as e:
            print(f"[WARN] query_instrument Fehler für {inst}: {e}")
            continue

        if tab is None or len(tab) == 0:
            print(f"[INFO] Keine Datensätze für {inst}.")
            continue

        # Filter auf spektrale Produkte (grob über Wellenlängenbereich K-Band 1.95–2.45 µm)
        # Manche Tabellen haben die Spalten nicht; dann heuristisch behalten.
        keep = []
        for row in tab:
            try:
                wl_start = float(row.get('INS.DET1.WLEN.START', np.nan))
                wl_end = float(row.get('INS.DET1.WLEN.END', np.nan))
                if np.isnan(wl_start) or np.isnan(wl_end):
                    keep.append(True)  # unklar → behalten
                else:
                    # Wellenlänge in nm? ESO variiert je nach Instrument;
                    # SINFONI-Key ist oft in nm. Wir akzeptieren 1950–2450 nm als K-Band.
                    # Falls in µm, ist es 1.95–2.45.
                    if wl_start > 100:  # vermutlich nm
                        in_k = (wl_start <= 2450) and (wl_end >= 1950)
                    else:  # vermutlich µm
                        in_k = (wl_start <= 2.45) and (wl_end >= 1.95)
                    keep.append(in_k)
            except Exception:
                keep.append(True)
        tab2 = tab[np.where(np.array(keep))[0]]

        if all_rows is None:
            all_rows = tab2
        else:
            all_rows = Table(np.hstack([all_rows, tab2])) if len(tab2) > 0 else all_rows

    if all_rows is None:
        all_rows = Table(names=('DP.ID', 'ARCFILE', 'MJD-OBS', 'TARGET', 'RA', 'DEC', 'INS.MODE', 'DP.TYPE'))
    return all_rows


def retrieve_products(eso: Eso, dpids: List[str], max_files: Optional[int], dest_dir: str) -> List[str]:
    if max_files is not None and len(dpids) > max_files:
        dpids = dpids[:max_files]
    print(f"[INFO] Lade {len(dpids)} Datensätze…")
    os.makedirs(dest_dir, exist_ok=True)
    files = []
    try:
        paths = eso.retrieve_data(dpids, destination=dest_dir, continuation=True)
        # eso.retrieve_data kann eine Liste von Pfaden oder eine einzelne Zeichenfolge zurückgeben
        if isinstance(paths, list):
            files = paths
        elif isinstance(paths, str):
            files = [paths]
        else:
            print(f"[WARN] Unerwarteter Rückgabewert von retrieve_data: {type(paths)}")
    except Exception as e:
        print(f"[WARN] Download-Fehler: {e}")
    # Filter auf existierende Dateien
    files = [p for p in files if p and os.path.exists(p)]
    print(f"[INFO] Lokale Dateien: {len(files)}")
    return files


def load_spectrum_1d(path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Versucht, 1D-Spektrum aus FITS zu lesen. Erwartet Wellenlängen (µm) und Flux (arb).
    """
    try:
        with fits.open(path, memmap=False) as hdul:
            # Heuristiken: Daten liegen oft in 1. EXT oder als BINTABLE mit Spalten WAVE/FLUX
            for hdu in hdul:
                if isinstance(hdu, fits.BinTableHDU):
                    cols = [c.lower() for c in hdu.columns.names]
                    if 'wavelength' in cols:
                        w = hdu.data['wavelength']
                    elif 'wave' in cols:
                        w = hdu.data['wave']
                    elif 'lambda' in cols:
                        w = hdu.data['lambda']
                    else:
                        w = None

                    if 'flux' in cols:
                        f = hdu.data['flux']
                    elif 'intensity' in cols:
                        f = hdu.data['intensity']
                    else:
                        f = None

                    if w is not None and f is not None:
                        w = np.array(w).astype(float)
                        f = np.array(f).astype(float)
                        # Einheit raten: oft µm oder nm; hier auf µm bringen
                        if np.nanmedian(w) > 100:  # nm → µm
                            w_um = w / 1000.0
                        else:
                            w_um = w
                        return w_um, f

                if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
                    # 1D-Spektrum als Bild mit WCS? Versuchen, CRVAL/CDLT Keys zu lesen
                    hdr = hdu.header
                    data = hdu.data
                    if data is None:
                        continue
                    arr = np.squeeze(np.array(data))
                    if arr.ndim == 1:
                        n = arr.shape[0]
                        crval = hdr.get('CRVAL1')
                        cdelt = hdr.get('CDELT1') or hdr.get('CD1_1')
                        crpix = hdr.get('CRPIX1', 1.0)
                        unit = hdr.get('CUNIT1', '').lower()
                        if crval is not None and cdelt is not None:
                            pix = np.arange(n, dtype=float) + 1.0
                            w = crval + (pix - crpix) * cdelt
                            # Einheit interpretieren
                            if unit in ('angstrom', 'a', 'ang'):
                                w_um = w * 1e-4
                            elif unit in ('nm', 'nanometer'):
                                w_um = w / 1000.0
                            elif unit in ('um', 'micron', 'micrometer', 'micrometre'):
                                w_um = w
                            else:
                                # fallback: nm, wenn Werte > 100
                                w_um = w/1000.0 if np.nanmedian(w) > 100 else w
                            f = arr.astype(float)
                            return w_um, f
            return None
    except Exception as e:
        print(f"[WARN] Konnte Spektrum aus '{path}' nicht lesen: {e}")
        return None


def find_line_center_lambda_um(w_um: np.ndarray,
                               f: np.ndarray,
                               lambda0_um: float = BRGAMMA_LAMBDA0_UM,
                               window_um: float = 0.12,
                               line_type: str = 'absorption') -> Optional[float]:
    """
    Findet das Linienzentrum nahe lambda0_um.
    - window_um: Halbbreite des Suchfensters (Default ±0.12 µm → robust bis ~6000 km/s)
    - line_type: 'absorption' (Minimum) oder 'emission' (Maximum)
    """
    if w_um is None or f is None or len(w_um) < 5:
        return None
    w = np.array(w_um, dtype=float)
    y = np.array(f, dtype=float)

    # optional glätten
    if SCIPY_OK and len(y) >= 31:
        try:
            y_s = savgol_filter(y, window_length=31, polyorder=2, mode='interp')
        except Exception:
            y_s = y
    else:
        y_s = y

    mask = (w >= (lambda0_um - window_um)) & (w <= (lambda0_um + window_um))
    if not np.any(mask):
        return None
    ww = w[mask]
    yy = y_s[mask]

    if line_type.lower().startswith('abs'):
        idx = np.nanargmin(yy)
    else:
        idx = np.nanargmax(yy)

    if idx is None:
        return None
    return float(ww[int(idx)])


def mjd_from_header(path: str) -> Optional[float]:
    try:
        with fits.open(path, memmap=False) as hdul:
            hdr = hdul[0].header
            mjd = hdr.get('MJD-OBS') or hdr.get('MJDOBS') or None
            if mjd is not None:
                return float(mjd)
            # Versuch aus DATE-OBS
            dateobs = hdr.get('DATE-OBS')
            if dateobs:
                t = Time(dateobs, format='isot', scale='utc')
                return float(t.mjd)
    except Exception:
        pass
    return None


def run(args):
    np.seterr(all='ignore')

    # Zielposition
    coord = None
    if args.target:
        coord = resolve_target(args.target)
    if coord is None and args.ra is not None and args.dec is not None:
        coord = SkyCoord(ra=float(args.ra)*u.deg, dec=float(args.dec)*u.deg, frame='icrs')

    if coord is None:
        print("[ERROR] Keine Zielkoordinaten gefunden (weder --target noch --ra/--dec).")
        sys.exit(2)

    radius = parse_sexagesimal_radius(args.radius)

    eso = setup_eso()

    # Produkte suchen
    products = query_products(eso, coord=coord, radius=radius, instruments=args.instruments)
    if products is None or len(products) == 0:
        print("[ERROR] Keine passenden Produkte gefunden.")
        sys.exit(1)

    # DP.IDs extrahieren
    dpids = []
    arcfiles = []
    for row in products:
        dp = row.get('DP.ID', None)
        af = row.get('ARCFILE', None)
        if dp:
            dpids.append(dp)
        elif af:
            # retrieve_data akzeptiert auch ARCFILE in manchen Fällen
            dpids.append(af)
        if af:
            arcfiles.append(af)

    print(f"[INFO] Gefundene Produkte gesamt: {len(dpids)}")

    files = []
    if not args.skip_download:
        files = retrieve_products(eso, dpids=dpids, max_files=args.max, dest_dir=args.dest)
    else:
        print("[INFO] Download übersprungen (--skip-download).")

    # Zusätzlich lokale Dateien parsen
    if args.local_dir:
        for root, _, fnames in os.walk(args.local_dir):
            for fn in fnames:
                if fn.lower().endswith(('.fits', '.fits.gz')):
                    files.append(os.path.join(root, fn))

    # Doppelte entfernen
    files = sorted(list({os.path.abspath(f) for f in files if os.path.exists(f)}))

    if len(files) == 0:
        print("[ERROR] Keine lokalen FITS-Dateien zum Parsen gefunden.")
        sys.exit(1)

    print(f"[INFO] Parsen von {len(files)} Dateien…")

    rows = []
    for p in files:
        spec = load_spectrum_1d(p)
        if spec is None:
            print(f"[WARN] Überspringe (kein 1D-Spektrum): {p}")
            continue
        w_um, f = spec
        lam_obs = find_line_center_lambda_um(
            w_um, f,
            lambda0_um=BRGAMMA_LAMBDA0_UM,
            window_um=args.window,
            line_type=args.line_type
        )
        mjd = mjd_from_header(p)

        if lam_obs is None:
            print(f"[WARN] Keine Brγ-Linie gefunden in: {p}")
            continue

        f_emit = BRGAMMA_F_EMIT_HZ
        f_obs = SPEED_OF_LIGHT / (lam_obs * 1e-6)
        z = (f_emit / f_obs) - 1.0  # identisch zu (lam_obs - lam0)/lam0

        rows.append({
            'epoch_mjd': mjd if mjd is not None else np.nan,
            'instrument': 'AUTO',
            'lambda0_um': BRGAMMA_LAMBDA0_UM,
            'f_emit_Hz': f_emit,
            'lambda_obs_um': lam_obs,
            'f_obs_Hz': f_obs,
            'z': z,
            'source_file': os.path.basename(p),
            'notes': f'line_type={args.line_type} window={args.window}um'
        })

    if len(rows) == 0:
        print("[ERROR] Keine Linienmessungen extrahiert.")
        sys.exit(1)

    df = pd.DataFrame(rows).sort_values(by=['epoch_mjd', 'source_file'])
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"[OK] Geschrieben: {args.out}")
    print(df.head(10).to_string(index=False))


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ESO-Fetch + Brγ-Extraktion für S2/S0-2 → CSV (f_obs, z)")
    g_t = p.add_argument_group("Ziel/Region")
    g_t.add_argument("--target", type=str, default="S2", help="Zielname (SIMBAD), z. B. S2 oder S0-2")
    g_t.add_argument("--ra", type=float, help="RA [deg] (falls kein --target)")
    g_t.add_argument("--dec", type=float, help="Dec [deg] (falls kein --target)")
    g_t.add_argument("--radius", type=str, default="5m", help="Suchradius: 30s, 5m, 0.2d (Default: 5m)")

    g_i = p.add_argument_group("Instrument/Download")
    g_i.add_argument("--instruments", nargs="+", default=["SINFONI", "GRAVITY"], help="Instrumente (Default: SINFONI GRAVITY)")
    g_i.add_argument("--max", type=int, default=20, help="Maximale Anzahl Downloads (Default 20)")
    g_i.add_argument("--dest", type=str, default="./eso_spectra", help="Download-Verzeichnis")
    g_i.add_argument("--skip-download", action="store_true", help="Download überspringen, nur lokale Dateien parsen")
    g_i.add_argument("--local-dir", type=str, default="", help="Lokales Verzeichnis mit FITS (zusätzlich parsen)")

    g_l = p.add_argument_group("Linienfindung/Brγ")
    g_l.add_argument("--window", type=float, default=0.12, help="Suchfenster ±window [µm] um λ0=2.1661 µm (Default 0.12)")
    g_l.add_argument("--line-type", type=str, default="absorption", choices=["absorption", "emission"], help="Absorptions- oder Emissionslinie")

    g_o = p.add_argument_group("Ausgabe")
    g_o.add_argument("--out", type=str, default="s2_br_gamma.csv", help="Ziel-CSV")

    return p


if __name__ == "__main__":
    parser = build_argparser()
    args = parser.parse_args()
    run(args)
