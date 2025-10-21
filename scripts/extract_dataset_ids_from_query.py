#!/usr/bin/env python3
"""
Extract dataset IDs from ESO query results.

After performing a query on https://archive.eso.org/, you get a table with results.
This script helps extract the Dataset IDs from that table.

Usage:
    1. Save ESO query results as CSV (click "Download" → CSV)
    2. Run: python scripts/extract_dataset_ids_from_query.py query_results.csv

Output:
    - Prints dataset IDs (one per line)
    - Ready to paste into download_eso_fits.sh DATASETS array
"""

import argparse
import csv
import sys
from pathlib import Path


def extract_dataset_ids(csv_file, column_name='DP.ID'):
    """
    Extract dataset IDs from ESO query CSV.
    
    Parameters
    ----------
    csv_file : Path
        Path to CSV file from ESO query
    column_name : str
        Name of column containing dataset IDs
        Common names: 'DP.ID', 'Dataset ID', 'dp_id'
    
    Returns
    -------
    list of str
        Dataset IDs
    """
    dataset_ids = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Find correct column name (case-insensitive)
        headers = reader.fieldnames
        matching_col = None
        
        for header in headers:
            if column_name.lower() in header.lower():
                matching_col = header
                break
        
        if not matching_col:
            print(f"ERROR: Column '{column_name}' not found", file=sys.stderr)
            print(f"Available columns: {', '.join(headers)}", file=sys.stderr)
            return []
        
        # Extract IDs
        for row in reader:
            dataset_id = row.get(matching_col, '').strip()
            if dataset_id and dataset_id != '':
                dataset_ids.append(dataset_id)
    
    return dataset_ids


def main():
    parser = argparse.ArgumentParser(
        description='Extract dataset IDs from ESO query CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from query results
  python scripts/extract_dataset_ids_from_query.py eso_query.csv
  
  # Output to file
  python scripts/extract_dataset_ids_from_query.py eso_query.csv > dataset_ids.txt
  
  # Specify column name
  python scripts/extract_dataset_ids_from_query.py eso_query.csv --column "Dataset ID"
        """
    )
    parser.add_argument('csv_file', type=Path, help='ESO query results CSV file')
    parser.add_argument('--column', default='DP.ID', help='Column name for dataset IDs (default: DP.ID)')
    parser.add_argument('--format', choices=['list', 'bash'], default='list',
                       help='Output format: list (one per line) or bash (array)')
    args = parser.parse_args()
    
    if not args.csv_file.exists():
        print(f"ERROR: File not found: {args.csv_file}", file=sys.stderr)
        return 1
    
    dataset_ids = extract_dataset_ids(args.csv_file, args.column)
    
    if not dataset_ids:
        print("No dataset IDs found", file=sys.stderr)
        return 1
    
    print(f"# Found {len(dataset_ids)} dataset IDs from {args.csv_file.name}", file=sys.stderr)
    print("", file=sys.stderr)
    
    if args.format == 'list':
        # Simple list (one per line)
        for dataset_id in dataset_ids:
            print(dataset_id)
    
    elif args.format == 'bash':
        # Bash array format
        print("DATASETS=(")
        for dataset_id in dataset_ids:
            print(f'    "{dataset_id}"')
        print(")")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
