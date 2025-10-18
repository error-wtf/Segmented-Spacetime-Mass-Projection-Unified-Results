# ci/check_no_abs_paths.py
from __future__ import annotations
import re, sys
from pathlib import Path

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TEXT_EXT = {".py",".ipynb",".json",".yaml",".yml",".toml",".ini",".cfg",".md",".txt",".ps1",".bat",".sh",".psm1"}
EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "data\\raw", "data/raw", "node_modules", ".pytest_cache", ".vscode", ".idea"}

ABS_PATTERNS = [
    re.compile(r"[A-Za-z]:\\\\[^\\n\\r]+"),      # Windows
    re.compile(r"[A-Za-z]:/[^\\n\\r]+"),         # Windows /
    re.compile(r"/(?:[^/\\n\\r]+/)+[^\\s\"\']+") # Unix
]

def is_text_file(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXT

def should_skip(p: Path) -> bool:
    parts = {part for part in p.parts}
    return any(d in parts for d in EXCLUDE_DIRS)

def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    offenders = []
    for p in repo.rglob("*"):
        if p.is_dir() or should_skip(p) or not is_text_file(p):
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pat in ABS_PATTERNS:
            if pat.search(txt):
                offenders.append(str(p))
                break
    if offenders:
        print("[ERROR] Absolute Pfade gefunden (Repo nicht portabel):")
        for o in sorted(set(offenders)):
            print("  -", o)
        print("\n[HINT] Verwende scripts/_repo_paths.py oder ${REPO_ROOT}.")
        return 1
    print("[OK] Keine absoluten Pfade gefunden.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
