"""
I/O Module for Segmented Radiowave Propagation

Handles CSV/JSON data loading for ring temperature/velocity data.

Copyright © 2025
Carmen Wrede und Lino Casu

Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

from __future__ import annotations
import pandas as pd
import json
from pathlib import Path
from typing import Optional


def load_ring_data(
    csv_path: str | Path,
    required_columns: Optional[list] = None
) -> pd.DataFrame:
    """
    Load ring temperature/density/velocity data from CSV.
    
    Expected columns:
    - ring : Ring/shell identifier (int or string)
    - T : Temperature (K)
    - n : (Optional) Density (cm^-3)
    - v_obs : (Optional) Observed velocity (km/s)
    
    Parameters:
    -----------
    csv_path : Path to CSV file
    required_columns : List of required column names (default ['ring', 'T'])
    
    Returns:
    --------
    DataFrame with ring data
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Load CSV with UTF-8 encoding
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # Check required columns
    if required_columns is None:
        required_columns = ['ring', 'T']
    
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Missing required columns in {csv_path.name}: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )
    
    # Validate data types
    if 'T' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['T']):
            raise ValueError("Column 'T' must be numeric")
        if (df['T'] <= 0).any():
            raise ValueError("All temperatures must be positive")
    
    if 'n' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['n']):
            raise ValueError("Column 'n' must be numeric")
        if (df['n'] <= 0).any():
            raise ValueError("All densities must be positive")
    
    if 'v_obs' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['v_obs']):
            raise ValueError("Column 'v_obs' must be numeric")
    
    return df


def load_sources_manifest(
    json_path: str | Path
) -> dict:
    """
    Load data sources manifest (bibliography/DOI references).
    
    Expected format:
    {
      "SOURCE_NAME": {
        "TRACER": ["doi:...", "bib:...", ...],
        ...
      },
      ...
    }
    
    Parameters:
    -----------
    json_path : Path to sources JSON file
    
    Returns:
    --------
    Sources dictionary
    """
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Sources manifest not found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    
    if not isinstance(sources, dict):
        raise ValueError(f"Sources manifest must be a JSON object/dict, got {type(sources)}")
    
    return sources


def save_results(
    df: pd.DataFrame,
    output_path: str | Path,
    float_format: str = "%.6f"
) -> None:
    """
    Save results DataFrame to CSV with proper formatting.
    
    Parameters:
    -----------
    df : Results DataFrame
    output_path : Output CSV path
    float_format : Float formatting string (default 6 decimals)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(
        output_path,
        index=False,
        encoding='utf-8',
        float_format=float_format
    )


def save_report(
    report_text: str,
    output_path: str | Path
) -> None:
    """
    Save text report to file.
    
    Parameters:
    -----------
    report_text : Report content
    output_path : Output text file path
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
