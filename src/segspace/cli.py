"""Command-line interface for Segmented Spacetime Suite."""

from __future__ import annotations
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

# Repo-Root = site-packages/segspace -> up 2 levels = repo root
REPO = Path(__file__).resolve().parents[2]
if not (REPO / "ci" / "autorun_suite.py").exists():
    REPO = Path.cwd()


def _py():
    """Get current Python executable."""
    return sys.executable


def _run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    """Run command with error handling."""
    print(f"[RUN] {' '.join(cmd)}")
    sys.stdout.flush()
    sys.stderr.flush()
    return subprocess.run(cmd, cwd=cwd or REPO, check=check).returncode


def fetch_data():
    """Optional data fetch (avoids bundling 2GB+ datasets)."""
    print("[INFO] Data fetch (optional, can be skipped if offline)")
    ci = REPO / "ci" / "autorun_suite.py"
    
    # Check if we have a fetch-only mode
    if ci.exists():
        try:
            _run([_py(), str(ci), "--only-fetch"], check=False)
        except subprocess.CalledProcessError:
            print("[WARN] Autofetch failed (offline?). Continuing...")
    else:
        print("[INFO] No explicit fetch step found. Skipping.")


def run_all():
    """Run the complete analysis suite."""
    print("[INFO] Running complete Segmented Spacetime Suite")
    ci = REPO / "ci" / "autorun_suite.py"
    
    if ci.exists():
        try:
            _run([_py(), str(ci)])
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Suite execution failed with exit code {e.returncode}")
            sys.exit(e.returncode)
    else:
        # Fallback: run tests
        print("[WARN] ci/autorun_suite.py not found, running tests as fallback")
        tests = REPO / "scripts" / "tests"
        if tests.exists():
            try:
                _run([_py(), "-m", "pytest", str(tests), "-q", "--disable-warnings"], check=False)
            except subprocess.CalledProcessError:
                pass


def _collect_md_files() -> list[Path]:
    """Collect all Markdown reports and analyses."""
    candidates = []
    
    # Priority files
    for rel in [
        "RESULTS_ANALYSIS.md",
        "FINAL_ANALYSIS.md", 
        "SEGSPACE_CONSOLIDATED_FINDINGS.md",
        "EHT_COMPARISON_MATRIX.md",
        "QA_CHECKLIST.md",
        "output-summary.md",
        "IMPLEMENTATION_COMPLETE.md",
        "RING_TEMPERATURE_INTEGRATION.md",
    ]:
        p = REPO / rel
        if p.is_file() and p.suffix.lower() == ".md":
            candidates.append(p)
    
    # Scan output directories
    for rel in ["reports", "final_reports", "experiments", "out", "agent_out", "testergebnisse"]:
        p = REPO / rel
        if p.is_dir():
            for md in p.rglob("*.md"):
                if md.is_file():
                    candidates.append(md)
    
    # Deduplicate
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            unique.append(c)
            seen.add(c)
    
    return sorted(unique)


def print_summary():
    """Print all reports and analyses to stdout."""
    md_files = _collect_md_files()
    
    print("\n" + "=" * 80)
    print("SEGMENTED SPACETIME SUITE - SUMMARY")
    print("=" * 80 + "\n")
    
    if not md_files:
        print("[INFO] No Markdown reports found.")
    else:
        print(f"[INFO] Found {len(md_files)} report(s)\n")
        
        for md in md_files:
            try:
                rel_path = md.relative_to(REPO)
            except ValueError:
                rel_path = md
            
            print(f"\n{'-' * 80}")
            print(f"FILE: {rel_path}")
            print("-" * 80 + "\n")
            
            try:
                content = md.read_text(encoding="utf-8", errors="replace")
                print(content)
            except Exception as e:
                print(f"[ERROR] Could not read {md}: {e}")
    
    # Also print text reports from output directories
    for d in [REPO / "out", REPO / "agent_out", REPO / "reports", REPO / "final_reports"]:
        if d.exists():
            for txt in d.rglob("*.txt"):
                if txt.is_file() and txt.stat().st_size < 1024 * 1024:  # < 1MB
                    try:
                        rel_path = txt.relative_to(REPO)
                    except ValueError:
                        rel_path = txt
                    
                    print(f"\n{'-' * 80}")
                    print(f"FILE: {rel_path}")
                    print("-" * 80 + "\n")
                    
                    try:
                        content = txt.read_text(encoding="utf-8", errors="replace")
                        print(content)
                    except Exception as e:
                        print(f"[ERROR] Could not read {txt}: {e}")


def _ensure_pydeps_fallback():
    """Ensure Python dependencies (fallback if APT packages missing)."""
    try:
        import pyarrow  # noqa
    except ImportError:
        print("[INFO] pyarrow not found, attempting pip install --user")
        try:
            subprocess.run(
                [_py(), "-m", "pip", "install", "--user", "pyarrow"],
                check=False,
                capture_output=True
            )
        except Exception:
            print("[WARN] Could not install pyarrow")


def _print_license():
    """Print the Anti-Capitalist Software License."""
    license_text = """
================================================================================
ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4)
================================================================================

Copyright © 2025 Carmen Wrede and Lino Casu

This is anti-capitalist software, released for free use by individuals and
organizations that do not operate by capitalist principles.

Permission is hereby granted, free of charge, to any person or organization
(the "User") obtaining a copy of this software and associated documentation
files (the "Software"), to use, copy, modify, merge, distribute, and/or sell
copies of the Software, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in
   all copies or modified versions of the Software.

2. The User is one of the following:
   a. An individual person, laboring for themselves
   b. A non-profit organization
   c. An educational institution
   d. An organization that seeks shared profit for all of its members, and
      allows non-members to set the cost of their labor

3. If the User is an organization with owners, then all owners are workers
   and all workers are owners with equal equity and/or equal vote.

4. If the User is an organization, then the User is not law enforcement or
   military, or working for or under either.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY
KIND, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

================================================================================
"""
    print(license_text)


def main_all_with_summary_and_license():
    """Main entry point: fetch data (optional), run suite, print summary & license."""
    # Ensure Python dependencies
    _ensure_pydeps_fallback()
    
    # Optional data fetch (can be disabled with SEGSPACE_FETCH=0)
    if os.environ.get("SEGSPACE_FETCH", "1") == "1":
        try:
            fetch_data()
        except Exception as e:
            print(f"[WARN] Data fetch encountered error: {e}")
    
    # Run the analysis suite
    try:
        run_all()
    except Exception as e:
        print(f"[ERROR] Suite execution encountered error: {e}")
    
    # Print all reports
    try:
        print_summary()
    except Exception as e:
        print(f"[ERROR] Summary generation encountered error: {e}")
    
    # Print license
    _print_license()


if __name__ == "__main__":
    main_all_with_summary_and_license()
