#!/usr/bin/env python
"""Download the Planck SMICA 2048 map archive."""
from __future__ import annotations

import argparse
import gzip
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable

import requests

DEFAULT_PLANCK_URLS = (
    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits",
    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits.gz",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch the Planck SMICA (IQU) Nside 2048 map")
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Destination path for the FITS file (e.g. data/raw/planck/<run>/planck_map.fits)",
    )
    parser.add_argument("--url", help="Override download URL")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output if it already exists",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Connection timeout in seconds",
    )
    return parser.parse_args()


def report_progress(downloaded: int, total: int | None) -> None:
    if total:
        percent = downloaded * 100.0 / total
        print(
            f"[PLANCK FETCH] Downloaded {downloaded / 1_048_576:.1f} / {total / 1_048_576:.1f} MiB ({percent:.1f}%)",
            flush=True,
        )
    else:
        print(f"[PLANCK FETCH] Downloaded {downloaded / 1_048_576:.1f} MiB", flush=True)


def download(url: str, dest: Path, timeout: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        total = response.headers.get("Content-Length")
        total_int = int(total) if total and total.isdigit() else None

        with tempfile.NamedTemporaryFile(delete=False, dir=str(dest.parent)) as tmp:
            downloaded = 0
            last_report = time.monotonic()
            for chunk in response.iter_content(chunk_size=1_048_576):  # 1 MiB
                if not chunk:
                    continue
                tmp.write(chunk)
                downloaded += len(chunk)
                now = time.monotonic()
                if now - last_report >= 3.0:
                    report_progress(downloaded, total_int)
                    last_report = now
            temp_path = Path(tmp.name)

        # final progress report if not already printed or total unknown
        report_progress(downloaded, total_int)
        shutil.move(str(temp_path), dest)


def try_download(urls: Iterable[str], dest: Path, timeout: float) -> None:
    last_error: Exception | None = None
    for url in urls:
        print(f"[PLANCK FETCH] Attempting {url}")
        try:
            download(url, dest, timeout)
            return
        except requests.HTTPError as exc:
            print(f"[PLANCK FETCH] HTTP error {exc.response.status_code} for {url}", file=sys.stderr)
            last_error = exc
        except requests.RequestException as exc:
            print(f"[PLANCK FETCH] Request failed for {url}: {exc}", file=sys.stderr)
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("Planck download failed with unknown error")


def maybe_decompress(dest: Path) -> None:
    with dest.open("rb") as fh:
        magic = fh.read(2)
    if magic != b"\x1f\x8b":
        return

    print("[PLANCK FETCH] Detected gzip archive; decompressing to FITS.", flush=True)
    temp_path = dest.with_suffix(dest.suffix + ".tmp")
    with gzip.open(dest, "rb") as src, temp_path.open("wb") as out:
        shutil.copyfileobj(src, out)
    dest.unlink()
    temp_path.rename(dest)


def main() -> int:
    args = parse_args()

    if args.output.exists() and not args.overwrite:
        print(f"[PLANCK FETCH] Output already exists at {args.output}. Use --overwrite to replace.", file=sys.stderr)
        return 0

    urls: Iterable[str]
    if args.url:
        urls = (args.url,)
    else:
        urls = DEFAULT_PLANCK_URLS

    try:
        try_download(urls, args.output, args.timeout)
    except Exception as exc:  # broad to catch RequestException or RuntimeError
        print(f"[PLANCK FETCH] Download failed: {exc}", file=sys.stderr)
        return 1

    try:
        maybe_decompress(args.output)
    except OSError as exc:
        print(f"[PLANCK FETCH] Warning: failed to inspect archive ({exc}).", file=sys.stderr)

    print(f"[PLANCK FETCH] Map saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
