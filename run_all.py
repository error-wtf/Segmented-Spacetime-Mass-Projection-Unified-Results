#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

# --- Immer im Skriptverzeichnis arbeiten ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# --- Windows: Konsole auf UTF-8 setzen ---
if os.name == "nt":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.system("")  # ANSI/Unicode-Fix

def run_cmd(cmd):
    """Führt ein Python-Skript im aktuellen Repo-Verzeichnis aus"""
    print(f"\n[RUN] {sys.executable} {' '.join(cmd)}\n")
    result = subprocess.run([sys.executable] + cmd, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(cmd)}")
        sys.exit(result.returncode)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-mode", choices=["skip", "full"], default="skip", help="Fetch data or skip.")
    ap.add_argument("--csv", type=str, default="real_data_full.csv", help="Path to CSV.")
    ap.add_argument("--out-dir", type=str, default="results", help="Output directory.")
    ap.add_argument("--prefer-z", action="store_true", help="Prefer z calculation.")
    ap.add_argument("--top", type=int, default=10, help="Top N results.")
    ap.add_argument("--token", type=str, default=os.environ.get("ESO_TOKEN", ""), help="ESO Bearer token.")
    args = ap.parse_args()

    # Output dir anlegen
    os.makedirs(args.out_dir, exist_ok=True)

    print("[INFO] Using working directory:", BASE_DIR)

    # 1. Optional Daten holen
    if args.fetch_mode == "full":
        run_cmd(["fetch_eso_br_gamma.py", "--token", args.token])

    # 2. PI-Bridge
    run_cmd([
        "segspace_enhanced_pi_bridge.py",
        "--csv", args.csv,
        "--seg-mode", "hybrid",
        "--pi-source", "chud",
        "--prec", "200",
        "--chud-terms", "16",
        *(["--prefer-z"] if args.prefer_z else []),
        "--top", str(args.top)
    ])

    # 3. Mass Validate
    run_cmd([
        "segmented_all_mass_validate.py",
        "--csv", args.csv,
        "--out-dir", args.out_dir
    ])

    # 4. Bound Energy
    run_cmd([
        "segmented_all_bound_energy.py",
        "--csv", args.csv,
        "--out-dir", args.out_dir
    ])

if __name__ == "__main__":
    main()

