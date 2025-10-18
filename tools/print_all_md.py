"""
SSZ Print All Markdown - Repo-wide Markdown content printer

Recursively collects and prints all .md files in the repository to STDOUT.
Useful for capturing complete analysis results at pipeline end.

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import os
import sys
from pathlib import Path

DEFAULT_INCLUDE = [
    "reports/**/*.md",           # Pipeline reports
    "out/**/*.md",               # Generic output folders
    "docs/**/*.md",              # Documentation and guides
    "analysis/**/*.md",          # Analysis results
    "data/processed/**/*.md",    # Processed data summaries
    "*.md"                       # Root-level MDs (e.g., RUN_SUMMARY.md)
]

DEFAULT_EXCLUDE_DIRS = {
    ".git", ".github", ".venv", "venv", "node_modules", 
    "dist", "build", "__pycache__", ".pytest_cache"
}


def read_text_limited(path: Path, max_bytes: int) -> str:
    """
    Read file with byte limit to prevent console overflow.
    
    Parameters:
    -----------
    path : File path to read
    max_bytes : Maximum bytes to read per file
    
    Returns:
    --------
    File content as string, truncated if necessary
    """
    b = path.read_bytes()
    if len(b) > max_bytes:
        head = b[:max_bytes]
        return head.decode("utf-8", errors="replace") + \
               f"\n\n[...[truncated: {len(b)-max_bytes} bytes omitted]...]"
    return b.decode("utf-8", errors="replace")


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "="*100)
    print(title)
    print("="*100)


def main(argv=None):
    """
    Main entry point for ssz-print-md command.
    
    Collects all Markdown files in repository and prints their contents
    to STDOUT with headers and size limits.
    """
    import argparse
    
    ap = argparse.ArgumentParser(
        description="Echo-print ALL Markdown files in repo to STDOUT.",
        epilog="Example: ssz-print-md --root . --order path"
    )
    ap.add_argument("--root", default=".", 
                    help="Repo root directory (default '.')")
    ap.add_argument("--include", nargs="*", default=None, 
                    help="Glob patterns to include (override defaults)")
    ap.add_argument("--exclude-dirs", nargs="*", default=None, 
                    help="Directories to exclude (override defaults)")
    ap.add_argument("--max-print-bytes", type=int, default=2_000_000, 
                    help="Per-file byte cap to prevent overflow (default 2MB)")
    ap.add_argument("--order", choices=["path", "depth"], default="path", 
                    help="Print order: path (alphabetical) or depth (shallow first)")
    ap.add_argument("--quiet-empty", action="store_true", 
                    help="Exit silently if no .md files found")
    
    args = ap.parse_args(argv)
    
    root = Path(args.root).resolve()
    includes = args.include if args.include else DEFAULT_INCLUDE
    exdirs = set(args.exclude_dirs) if args.exclude_dirs else DEFAULT_EXCLUDE_DIRS
    
    # Collect all matching .md files
    files = set()
    for pat in includes:
        for p in root.glob(pat):
            if not p.is_file():
                continue
            # Exclude files in blacklisted directories
            if any(ed in p.parts for ed in exdirs):
                continue
            if p.suffix.lower() == ".md":
                files.add(p.resolve())
    
    if not files:
        if not args.quiet_empty:
            print_header(f"ssz-print-md — root={root.as_posix()} — no Markdown files found")
        return 0
    
    # Sort files by chosen order
    def depth(p: Path):
        return len(p.relative_to(root).parts)
    
    if args.order == "depth":
        ordered = sorted(files, key=lambda p: (depth(p), p.as_posix().lower()))
    else:  # path
        ordered = sorted(files, key=lambda p: p.as_posix().lower())
    
    # Print summary header
    print_header(f"ssz-print-md — root={root.as_posix()} — files={len(ordered)}")
    
    # Print each file with header
    for p in ordered:
        try:
            rel_path = p.relative_to(root).as_posix()
            print_header(f"# FILE: {rel_path}  (markdown)")
            print(read_text_limited(p, args.max_print_bytes))
        except Exception as e:
            rel_path = p.relative_to(root).as_posix()
            print_header(f"# FILE: {rel_path}  (error)")
            print(f"(Could not read file: {e})")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
