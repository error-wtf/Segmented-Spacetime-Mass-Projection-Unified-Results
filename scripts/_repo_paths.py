# scripts/_repo_paths.py
from __future__ import annotations
import os
from pathlib import Path

# Wurzel des Repos = zwei Ebenen über dieser Datei (scripts/_repo_paths.py)
REPO: Path = Path(__file__).resolve().parents[1]

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def reports_dir(run_id: str) -> Path:
    return ensure_dir(REPO / "reports" / run_id)

def experiments_dir(run_id: str) -> Path:
    return REPO / "experiments" / run_id

def data_raw(*parts: str) -> Path:
    return REPO / "data" / "raw" / Path(*parts)

def data_interim(*parts: str) -> Path:
    return REPO / "data" / "interim" / Path(*parts)

def models_dir(*parts: str) -> Path:
    return REPO / "models" / Path(*parts)

def out_dir() -> Path:
    return ensure_dir(REPO / "out")

def vfall_out_dir() -> Path:
    return ensure_dir(REPO / "vfall_out")

def agent_out_dir() -> Path:
    return ensure_dir(REPO / "agent_out")

def resolve_env_placeholders(s: str) -> str:
    """Ersetzt ${REPO_ROOT} in Konfigstrings durch tatsächlichen Pfad."""
    return s.replace("${REPO_ROOT}", str(REPO))

def repo_relative(p: str | Path) -> Path:
    p = Path(str(p))
    try:
        return p if str(p).startswith(str(REPO)) else (REPO / p)
    except Exception:
        return REPO / p
