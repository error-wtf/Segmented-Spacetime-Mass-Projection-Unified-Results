# ci/fix_repo_paths.py
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

TEXT_EXT = {
    ".py",".ipynb",".json",".yaml",".yml",".toml",".ini",".cfg",
    ".md",".txt",".ps1",".bat",".sh",".psm1",
}
EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "data\\raw", "data/raw", "node_modules"}

# Windows + Unix absolute Pfade erkennen
ABS_PATTERNS = [
    re.compile(r"[A-Za-z]:\\\\[^\\n\\r]+"),      # Windows: C:\..., H:\...
    re.compile(r"[A-Za-z]:/[^\\n\\r]+"),         # Windows mit /
    re.compile(r"/(?:[^/\\n\\r]+/)+[^\\s\"\']+") # Unix: /home/.../file
]

# Projektwurzelvarianten, die ersetzt werden sollen (anpassen/erweitern)
PROJECT_ROOT_HINTS = [
    r"${REPO_ROOT}",
    r"${REPO_ROOT}_bak_",
    r"${REPO_ROOT}",
]

def is_text_file(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXT

def should_skip(p: Path) -> bool:
    parts = {part for part in p.parts}
    return any(d in parts for d in EXCLUDE_DIRS)

def replace_roots(content: str) -> tuple[str, int]:
    count = 0
    # Spezifische Projektwurzel-Hints -> ${REPO_ROOT} (für Konfigs/MD)
    for hint in PROJECT_ROOT_HINTS:
        new_content, n = re.subn(re.escape(hint), "${REPO_ROOT}", content, flags=re.IGNORECASE)
        if n:
            content, count = new_content, count + n
    # Generische absolute Pfade markieren: wir ersetzen nicht blind,
    # sondern kommentieren sie an, damit der Autor manuell prüft.
    for pat in ABS_PATTERNS:
        matches = list(pat.finditer(content))
        # Nur warnen, nicht automatisch ändern (außerhalb unserer Root-Hints)
        # -> alternativ: nach Bedarf automatisch in ${REPO_ROOT}/rel umschreiben.
        count += len(matches)
    return content, count

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = ap.parse_args()

    root = Path(args.root).resolve()
    changed_total = 0
    flagged_total = 0

    for p in root.rglob("*"):
        if p.is_dir() or should_skip(p) or not is_text_file(p):
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_txt, flagged = replace_roots(txt)
        flagged_total += flagged
        if new_txt != txt and not args.dry_run:
            p.write_text(new_txt, encoding="utf-8")
            changed_total += 1
        elif new_txt != txt:
            changed_total += 1
            print(f"[DRY] would change: {p}")
    print(f"[OK] Processed. files_changed={changed_total}, occurrences_flagged={flagged_total}")
    if flagged_total and args.dry_run:
        print("[INFO] Re-run without --dry-run to apply safe replacements.")

if __name__ == "__main__":
    sys.exit(main())
