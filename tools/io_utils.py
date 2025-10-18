#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I/O Utilities for SSZ Suite - Safe File Operations & Manifest Management

Ensures reproducibility and safety:
- Write-scope limited to agent_out/ and reports/
- SHA256 checksums for all artifacts
- Manifest tracking with metadata

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import json
import hashlib
import os
import time
from pathlib import Path
from datetime import datetime


# CRITICAL: Only allow writes to these directories
ALLOWED_DIRS = ["agent_out", "reports"]


def safe_path(path: str) -> Path:
    """
    Validate that write path is within allowed directories
    
    Args:
        path: File path to validate
    
    Returns:
        Path: Validated absolute path
    
    Raises:
        RuntimeError: If path is outside allowed directories
    
    Security:
        Prevents accidental writes to system directories
        Enforces reproducibility constraints
    """
    p = Path(path).resolve()
    
    # Check if path starts with any allowed directory
    for base in ALLOWED_DIRS:
        base_path = Path(base).resolve()
        try:
            p.relative_to(base_path)
            return p  # Path is within allowed directory
        except ValueError:
            continue  # Try next allowed directory
    
    # Path is not in any allowed directory
    raise RuntimeError(
        f"Unsafe write path: {p}\n"
        f"Only writes to {ALLOWED_DIRS} are permitted.\n"
        f"This ensures reproducibility and prevents data loss."
    )


def sha256_file(path: str) -> str:
    """
    Calculate SHA256 hash of a file
    
    Args:
        path: File path
    
    Returns:
        str: Hexadecimal SHA256 hash
    
    Note:
        Reads file in 1MB chunks for memory efficiency
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):  # 1MB chunks
            h.update(chunk)
    return h.hexdigest()


def sha256_string(text: str) -> str:
    """Calculate SHA256 hash of a string"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def safe_write_text(path: str, text: str, encoding='utf-8'):
    """
    Safely write text to file with validation
    
    Args:
        path: Output file path
        text: Text content to write
        encoding: Text encoding (default: utf-8)
    
    Returns:
        str: Absolute path of written file
    
    Security:
        - Validates path is in allowed directory
        - Creates parent directories if needed
        - UTF-8 encoding by default (Windows-safe)
    """
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with open(p, "w", encoding=encoding) as f:
        f.write(text)
    
    return str(p)


def safe_write_json(path: str, data: dict, indent=2):
    """
    Safely write JSON to file
    
    Args:
        path: Output file path
        data: Dictionary to serialize
        indent: JSON indentation (default: 2)
    
    Returns:
        str: Absolute path of written file
    """
    text = json.dumps(data, ensure_ascii=False, indent=indent)
    return safe_write_text(path, text)


def safe_write_csv(path: str, header: list, rows: list):
    """
    Safely write CSV to file
    
    Args:
        path: Output file path
        header: List of column names
        rows: List of lists (data rows)
    
    Returns:
        str: Absolute path of written file
    """
    import csv
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    
    return str(p)


def update_manifest(manifest_path: str, update_dict: dict):
    """
    Update manifest file with new entries
    
    Args:
        manifest_path: Path to manifest JSON file
        update_dict: Dictionary with updates to merge
    
    Behavior:
        - Loads existing manifest if present
        - Merges updates (shallow merge)
        - Special handling for "artifacts" key (extends list)
        - Writes updated manifest back to file
    
    Example:
        update_manifest("reports/MANIFEST.json", {
            "meta": {"seed": 42},
            "artifacts": [{"role": "test", "path": "test.csv"}]
        })
    """
    p = safe_path(manifest_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing manifest
    data = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # Corrupted manifest, start fresh
            data = {}
    
    # Merge updates
    for key, value in update_dict.items():
        if key == "artifacts":
            # Extend artifacts list instead of replacing
            data.setdefault("artifacts", []).extend(value)
        else:
            # Replace other keys
            data[key] = value
    
    # Write updated manifest
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def register_artifact(manifest_path: str, role: str, path: str, 
                      format: str = None, metadata: dict = None):
    """
    Register an artifact in the manifest
    
    Args:
        manifest_path: Path to manifest JSON file
        role: Artifact role (e.g., "figure", "table", "posterior")
        path: Path to artifact file
        format: File format (e.g., "png", "csv", "json")
        metadata: Optional additional metadata
    
    Returns:
        dict: Artifact entry
    """
    artifact = {
        "role": role,
        "path": str(Path(path).as_posix()),  # Use forward slashes
        "sha256": sha256_file(path) if Path(path).exists() else None,
        "format": format or Path(path).suffix[1:],  # Remove leading dot
        "created_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    if metadata:
        artifact["metadata"] = metadata
    
    update_manifest(manifest_path, {"artifacts": [artifact]})
    
    return artifact


def create_manifest(manifest_path: str, meta: dict = None, params: dict = None):
    """
    Create a new manifest file with metadata
    
    Args:
        manifest_path: Path to manifest JSON file
        meta: Metadata dictionary (git commit, python version, etc.)
        params: Parameters dictionary (settings used in run)
    
    Returns:
        str: Path to created manifest
    """
    manifest = {
        "meta": meta or {},
        "params": params or {},
        "artifacts": [],
        "status": "in_progress"
    }
    
    # Add creation timestamp
    manifest["meta"]["created_utc"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return safe_write_json(manifest_path, manifest)


def finalize_manifest(manifest_path: str, status: str = "success", 
                      error: str = None):
    """
    Mark manifest as complete
    
    Args:
        manifest_path: Path to manifest JSON file
        status: Final status ("success", "failed", "partial")
        error: Error message if status is "failed"
    """
    update_data = {
        "status": status,
        "completed_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    if error:
        update_data["error"] = error
    
    update_manifest(manifest_path, update_data)


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists (with safety check)
    
    Args:
        path: Directory path
    
    Returns:
        Path: Validated directory path
    """
    p = safe_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
