
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all.py
==========

End-to-end runner for the Segmented Spacetime pipeline:
  1) Optional data fetch (new "get-proof" or legacy "tap")
  2) π-Bridge + segmented evaluation (hybrid recommended)
  3) Outputs a compact summary (with AB gate ON/OFF comparison)

This script just orchestrates existing components:
  - fetch_eso_br_gamma.py
  - segspace_all_in_one.py

Usage examples
--------------
# Full pipeline with new API (recommended) and a timestamped results dir
python run_all.py --fetch-mode get-proof \
  --endpoint https://example.eso.org/api/get_proof \
  --since 2025-07-15 \
  --out-dir results \
  --prefer-z --top 10 --plots

# Legacy TAP fetch, then run
python run_all.py --fetch-mode tap \
  --endpoint https://tap.eso.org/tap \
  --out-dir results --prefer-z --top 10

# Skip fetch (use existing CSV) and run
python run_all.py --fetch-mode skip --csv data/real_data_full.csv \
  --out-dir results --prefer-z --top 10
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

DEF_CSV = "real_data_full.csv"

def shell(*args, **kwargs):
    """Run a subprocess, stream output, raise on error."""
    print(">>", " ".join(str(a) for a in args[0]))
    proc = subprocess.run(*args, **kwargs)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {proc.returncode}: {' '.join(args[0])}")
    return proc

def main():
    ap = argparse.ArgumentParser()
    # Fetch options
    ap.add_argument("--fetch-mode", choices=["get-proof","tap","skip"], default="get-proof",
                    help="Select data source or skip fetching.")
    ap.add_argument("--endpoint", type=str, default="",
                    help="API base URL (required for get-proof/tap).")
    ap.add_argument("--since", type=str, default=None, help="Start date (YYYY-MM-DD) for get-proof.")
    ap.add_argument("--until", type=str, default=None, help="End date (YYYY-MM-DD) for get-proof.")
    ap.add_argument("--token", type=str, default=os.environ.get("ESO_TOKEN",""), help="Bearer token (get-proof).")
    ap.add_argument("--dry-run", action="store_true", help="Do not call network; emit example rows.")
    ap.add_argument("--csv", type=str, default=DEF_CSV, help=f"CSV path to use (default: {DEF_CSV}).")

    # Run/segspace options
    ap.add_argument("--out-dir", type=str, default="segspace_results", help="Root output directory for results.")
    ap.add_argument("--seg-mode", type=str, default="hybrid", choices=["hint","deltam","hybrid","grsr"])
    ap.add_argument("--pi-source", type=str, default="chud", choices=["chud","builtin","phi"])
    ap.add_argument("--prec", type=int, default=200)
    ap.add_argument("--chud-terms", type=int, default=16)
    ap.add_argument("--prefer-z", action="store_true")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--no-emission-gate", action="store_true")
    ap.add_argument("--plots", action="store_true")

    args = ap.parse_args()

    t0 = time.time()
    root = Path(args.out_dir)
    # Timestamped subdir to avoid overwrites
    ts = time.strftime("%Y%m%d-%H%M%S")
    run_dir = root / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1) Optional fetch
    csv_path = Path(args.csv)
    sidecar_hint = ""
    if args.fetch_mode != "skip":
        if not args.endpoint:
            print("ERROR: --endpoint is required for fetch modes 'get-proof' and 'tap'.", file=sys.stderr)
            sys.exit(2)
        fetch_cmd = [
            sys.executable, "fetch_eso_br_gamma.py",
            "--mode", args.fetch_mode,
            "--endpoint", args.endpoint,
            "--out", str(run_dir / DEF_CSV)
        ]
        if args.fetch_mode == "get-proof":
            if args.since: fetch_cmd += ["--since", args.since]
            if args.until: fetch_cmd += ["--until", args.until]
            if args.token: fetch_cmd += ["--token", args.token]
        if args.dry_run: fetch_cmd += ["--dry-run"]

        shell(fetch_cmd, check=False)
        csv_path = run_dir / DEF_CSV
        sidecar = csv_path.with_suffix(csv_path.suffix + ".meta.json")
        sidecar_hint = f" (meta: {sidecar.name})" if sidecar.exists() else ""

    # 2) Run segspace_all_in_one.py (pi-bridge)
    out_dir = run_dir / "pi_bridge"
    seg_cmd = [
        sys.executable, "segspace_all_in_one.py",
        "pi-bridge",
        "--csv", str(csv_path),
        "--seg-mode", args.seg_mode,
        "--pi-source", args.pi_source,
        "--prec", str(args.prec),
        "--chud-terms", str(args.chud_terms),
        "--top", str(args.top),
        "--out", str(out_dir)
    ]
    if args.prefer_z: seg_cmd.append("--prefer-z")
    if args.no_emission_gate: seg_cmd.append("--no-emission-gate")
    if args.plots: seg_cmd.append("--plots")

    # Stream output to console and tee to file
    log_path = run_dir / "run_all.log"
    with log_path.open("w", encoding="utf-8") as logf:
        print("== RUN_ALL START ==", file=logf)
        print("CSV:", csv_path, file=logf)
        print("Fetch mode:", args.fetch_mode, file=logf)
        print("Seg cmd:", " ".join(seg_cmd), file=logf)
        logf.flush()
        proc = subprocess.run(seg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(proc.stdout)
        logf.write(proc.stdout)
        if proc.returncode != 0:
            print(proc.stdout, file=sys.stderr)
            raise SystemExit(proc.returncode)

    # 3) Collect a compact summary
    ab_summary = out_dir / "segspace_ab_summary.txt"
    ratios_on  = out_dir / "gate_on" / "segspace_ratios.csv"
    ratios_off = out_dir / "gate_off" / "segspace_ratios.csv"
    debug_csv  = out_dir / "segspace_debug.csv"

    summary_path = run_dir / "SUMMARY.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("=== Segmented Spacetime Run Summary ===\n")
        f.write(f"CSV: {csv_path.name}{sidecar_hint}\n")
        f.write(f"Output: {out_dir}\n")
        f.write(f"Seg-mode: {args.seg_mode}, pi-source: {args.pi_source}, prec: {args.prec}, chud-terms: {args.chud_terms}\n")
        f.write(f"prefer-z: {args.prefer_z}, no-emission-gate: {args.no_emission_gate}, plots: {args.plots}\n\n")
        if ab_summary.exists():
            f.write("--- AB Summary (gate ON vs OFF) ---\n")
            f.write(ab_summary.read_text(encoding="utf-8"))
        else:
            f.write("AB summary not found (older script version?).\n")
        f.write("\nArtifacts:\n")
        f.write(f" - Ratios (gate ON):  {ratios_on}\n")
        f.write(f" - Ratios (gate OFF): {ratios_off}\n")
        f.write(f" - Debug CSV:         {debug_csv}\n")
        f.write(f" - Full run log:      {log_path}\n")

    dur = time.time() - t0
    print(f"\nAll done in {dur:.1f}s")
    print(f"Results: {run_dir}")
    print(f"Summary: {summary_path}")

if __name__ == "__main__":
    main()
