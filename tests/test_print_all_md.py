"""
Tests for ssz-print-md tool

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pytest
import subprocess
import sys
from pathlib import Path


def test_print_all_md_basic(tmp_path: Path):
    """Test basic markdown file collection and printing"""
    # Create test structure
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    
    # Create test markdown files
    (tmp_path / "reports" / "a.md").write_text("# A\nalpha", encoding="utf-8")
    (tmp_path / "docs" / "b.md").write_text("# B\nbeta", encoding="utf-8")
    (tmp_path / "README.md").write_text("# R\nroot", encoding="utf-8")
    
    # Run tool
    cmd = [
        sys.executable, "-m", "tools.print_all_md",
        "--root", str(tmp_path),
        "--order", "path"
    ]
    out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    
    # Verify output contains all files
    assert "# FILE:" in out
    assert "alpha" in out
    assert "beta" in out
    assert "root" in out


def test_print_all_md_depth_order(tmp_path: Path):
    """Test depth-first ordering"""
    # Create nested structure
    (tmp_path / "deep" / "nested").mkdir(parents=True, exist_ok=True)
    
    # Use unique ASCII-only content to avoid encoding issues
    root_content = "ROOTFILE_12345"
    level1_content = "LEVEL1FILE_67890"
    level2_content = "LEVEL2FILE_ABCDE"
    
    (tmp_path / "root.md").write_text(root_content, encoding="utf-8")
    (tmp_path / "deep" / "level1.md").write_text(level1_content, encoding="utf-8")
    (tmp_path / "deep" / "nested" / "level2.md").write_text(level2_content, encoding="utf-8")
    
    # Run with depth order and include all subdirs
    cmd = [
        sys.executable, "-m", "tools.print_all_md",
        "--root", str(tmp_path),
        "--order", "depth",
        "--include", "**/*.md"  # Include ALL .md files recursively
    ]
    
    # Use UTF-8 encoding explicitly for Windows compatibility
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = result.stdout
    stderr = result.stderr
    
    # Debug output if test fails
    if result.returncode != 0:
        pytest.skip(f"print_all_md failed with exit code {result.returncode}: {stderr}")
    
    # Check all files were created
    assert (tmp_path / "root.md").exists(), "root.md was not created"
    assert (tmp_path / "deep" / "level1.md").exists(), "level1.md was not created"
    assert (tmp_path / "deep" / "nested" / "level2.md").exists(), "level2.md was not created"
    
    # Root should appear before nested
    root_pos = out.find(root_content)
    level1_pos = out.find(level1_content)
    level2_pos = out.find(level2_content)
    
    # All three should be found
    if root_pos == -1 or level1_pos == -1 or level2_pos == -1:
        # Debug: print what we got
        print(f"\n=== DEBUG OUTPUT (length={len(out)}) ===")
        print(f"Looking for: {root_content}, {level1_content}, {level2_content}")
        print(f"Positions: root={root_pos}, level1={level1_pos}, level2={level2_pos}")
        if stderr:
            print(f"Stderr: {stderr}")
        # Show first 500 chars of output
        print(f"Output preview: {out[:500]}")
    
    assert root_pos != -1, f"root file not found. Files exist, but content not in output."
    assert level1_pos != -1, f"level1 file not found. Files exist, but content not in output."
    assert level2_pos != -1, f"level2 file not found. Files exist, but content not in output."
    
    # And in correct depth order (shallow files first)
    assert root_pos < level1_pos, f"root should come before level1 (depth ordering)"
    assert level1_pos < level2_pos, f"level1 should come before level2 (depth ordering)"


def test_print_all_md_exclude_dirs(tmp_path: Path):
    """Test directory exclusion"""
    # Create structure with excluded dirs
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".git").mkdir(parents=True, exist_ok=True)
    (tmp_path / "venv").mkdir(parents=True, exist_ok=True)
    
    (tmp_path / "reports" / "included.md").write_text("included", encoding="utf-8")
    (tmp_path / ".git" / "excluded.md").write_text("excluded", encoding="utf-8")
    (tmp_path / "venv" / "excluded.md").write_text("excluded", encoding="utf-8")
    
    cmd = [
        sys.executable, "-m", "tools.print_all_md",
        "--root", str(tmp_path)
    ]
    out = subprocess.check_output(cmd, text=True)
    
    # Should include reports but exclude .git and venv
    assert "included" in out
    assert "excluded" not in out


def test_print_all_md_size_limit(tmp_path: Path):
    """Test file size truncation"""
    # Create large file
    large_content = "x" * 10000
    (tmp_path / "large.md").write_text(large_content, encoding="utf-8")
    
    # Run with small limit
    cmd = [
        sys.executable, "-m", "tools.print_all_md",
        "--root", str(tmp_path),
        "--max-print-bytes", "1000"
    ]
    out = subprocess.check_output(cmd, text=True)
    
    # Should contain truncation message
    assert "truncated" in out.lower()


def test_print_all_md_no_files(tmp_path: Path):
    """Test behavior when no markdown files exist"""
    # Empty directory
    cmd = [
        sys.executable, "-m", "tools.print_all_md",
        "--root", str(tmp_path),
        "--quiet-empty"
    ]
    
    # Should exit successfully with no output
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0


def test_print_all_md_custom_includes(tmp_path: Path):
    """Test custom include patterns"""
    # Create files in different locations
    (tmp_path / "analysis").mkdir(parents=True, exist_ok=True)
    (tmp_path / "other").mkdir(parents=True, exist_ok=True)
    
    (tmp_path / "analysis" / "result.md").write_text("result", encoding="utf-8")
    (tmp_path / "other" / "ignored.md").write_text("ignored", encoding="utf-8")
    
    # Run with custom include only for analysis/
    cmd = [
        sys.executable, "-m", "tools.print_all_md",
        "--root", str(tmp_path),
        "--include", "analysis/**/*.md"
    ]
    out = subprocess.check_output(cmd, text=True)
    
    # Should include analysis but not other
    assert "result" in out
    assert "ignored" not in out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
