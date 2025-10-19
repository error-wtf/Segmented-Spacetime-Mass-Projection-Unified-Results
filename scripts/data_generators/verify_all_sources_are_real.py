#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify ALL Sources Are Real Data

Checks every single row in real_data_full.csv to ensure
NO SYNTHETIC DATA claim is scientifically accurate.

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import pandas as pd
import sys
import io

# UTF-8 Setup
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Known REAL data sources with paper references
VERIFIED_REAL = {
    'M87*': {
        'count': 10,
        'paper': 'EHT Collaboration, ApJL 875, L1 (2019)',
        'instrument': 'ALMA/EHT',
        'verified': True
    },
    'Cyg': {  # Cygnus X-1
        'count': 10,
        'paper': 'Gou et al., ApJ 701, 1076 (2009)',
        'instrument': 'Chandra',
        'verified': True
    },
    'S2': {
        'count': 10,
        'paper': 'GRAVITY Collaboration, A&A 615, L15 (2018)',
        'instrument': 'VLT/GRAVITY',
        'verified': True
    }
}

# Keywords that indicate potentially synthetic/placeholder data
SUSPICIOUS_KEYWORDS = [
    'synthetic', 'placeholder', 'template', 'dummy', 
    'test', 'example', 'demo', 'mock', 'fake'
]

def classify_source(source_name, case_name):
    """Classify if a source is real, suspicious, or unknown"""
    
    # Check for verified real sources
    for verified_key in VERIFIED_REAL.keys():
        if verified_key.lower() in str(source_name).lower():
            return 'VERIFIED_REAL', VERIFIED_REAL[verified_key]
    
    # Check for suspicious keywords
    full_text = f"{source_name} {case_name}".lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in full_text:
            return 'SUSPICIOUS', {'reason': f'Contains keyword: {keyword}'}
    
    # Check if it looks like a real astronomical object
    # Real sources typically have: catalog names, coordinates, designations
    real_patterns = [
        'NGC', 'Messier', 'M ', 'IC ', 'UGC', 'Mrk',  # Galaxy catalogs
        'PSR', 'pulsar',  # Pulsars
        'Sgr A*', 'SgrA',  # Sgr A*
        'GRB', 'GW',  # Transients
        'HD ', 'HIP ', 'TYC',  # Star catalogs
        'IRAS', 'SDSS',  # Survey catalogs
        '3C ', 'PKS',  # Radio catalogs
        'Quasar', 'QSO',  # Quasars
        'SNR', 'supernova',  # Supernovae
        'black hole', 'BH', 'SMBH',  # Black holes
        'AGN', 'Seyfert',  # Active galaxies
    ]
    
    for pattern in real_patterns:
        if pattern.lower() in full_text:
            return 'LIKELY_REAL', {'pattern': pattern}
    
    return 'UNKNOWN', {'needs_verification': True}

def main():
    """Verify all sources"""
    
    print("="*80)
    print("VERIFY ALL SOURCES ARE REAL DATA")
    print("="*80)
    print(f"\nClaim: 'NO SYNTHETIC DATA - all from peer-reviewed observations'")
    print(f"Task: Verify this claim for ALL 177 rows")
    
    # Load
    df = pd.read_csv('real_data_full.csv')
    print(f"\nLoaded: {len(df)} rows")
    
    # Classify all sources
    classifications = {
        'VERIFIED_REAL': [],
        'LIKELY_REAL': [],
        'UNKNOWN': [],
        'SUSPICIOUS': []
    }
    
    print(f"\nClassifying sources...")
    for idx, row in df.iterrows():
        source = row['source']
        case = row['case'] if 'case' in row else ''
        classification, info = classify_source(source, case)
        classifications[classification].append({
            'index': idx,
            'source': source,
            'case': case,
            'info': info
        })
    
    # Report
    print(f"\n" + "="*80)
    print("CLASSIFICATION RESULTS")
    print("="*80)
    
    print(f"\n✅ VERIFIED REAL DATA ({len(classifications['VERIFIED_REAL'])} rows):")
    verified_sources = {}
    for item in classifications['VERIFIED_REAL']:
        src = item['source']
        if src not in verified_sources:
            verified_sources[src] = 0
        verified_sources[src] += 1
    
    for src, count in verified_sources.items():
        info = None
        for key in VERIFIED_REAL.keys():
            if key.lower() in src.lower():
                info = VERIFIED_REAL[key]
                break
        if info:
            print(f"  {src}: {count} rows")
            print(f"    Paper: {info['paper']}")
            print(f"    Instrument: {info['instrument']}")
    
    print(f"\n✓ LIKELY REAL DATA ({len(classifications['LIKELY_REAL'])} rows):")
    likely_sources = {}
    for item in classifications['LIKELY_REAL']:
        src = item['source']
        pattern = item['info'].get('pattern', 'unknown')
        if src not in likely_sources:
            likely_sources[src] = {'count': 0, 'pattern': pattern}
        likely_sources[src]['count'] += 1
    
    for src, data in sorted(likely_sources.items()):
        print(f"  {src}: {data['count']} rows (pattern: {data['pattern']})")
    
    print(f"\n⚠️  UNKNOWN SOURCES ({len(classifications['UNKNOWN'])} rows):")
    unknown_sources = {}
    for item in classifications['UNKNOWN']:
        src = item['source']
        if src not in unknown_sources:
            unknown_sources[src] = 0
        unknown_sources[src] += 1
    
    for src, count in sorted(unknown_sources.items()):
        print(f"  {src}: {count} rows - NEEDS VERIFICATION!")
    
    print(f"\n🚨 SUSPICIOUS DATA ({len(classifications['SUSPICIOUS'])} rows):")
    if len(classifications['SUSPICIOUS']) > 0:
        for item in classifications['SUSPICIOUS']:
            print(f"  {item['source']}: {item['info']['reason']}")
            print(f"    Row {item['index']}: {item['case']}")
    else:
        print(f"  None found")
    
    # Summary
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total = len(df)
    verified = len(classifications['VERIFIED_REAL'])
    likely = len(classifications['LIKELY_REAL'])
    unknown = len(classifications['UNKNOWN'])
    suspicious = len(classifications['SUSPICIOUS'])
    
    print(f"\nTotal rows: {total}")
    print(f"  Verified real: {verified} ({verified/total*100:.1f}%)")
    print(f"  Likely real:   {likely} ({likely/total*100:.1f}%)")
    print(f"  Unknown:       {unknown} ({unknown/total*100:.1f}%)")
    print(f"  Suspicious:    {suspicious} ({suspicious/total*100:.1f}%)")
    
    # Verdict
    print(f"\n" + "="*80)
    print("VERDICT")
    print("="*80)
    
    if suspicious > 0:
        print(f"\n🚨 CLAIM VIOLATION!")
        print(f"   Found {suspicious} suspicious rows with synthetic/placeholder keywords")
        print(f"   These MUST be removed or replaced with real data!")
    elif unknown > 50:
        print(f"\n⚠️  CLAIM UNCERTAIN!")
        print(f"   {unknown} rows have unknown provenance")
        print(f"   Need to verify these are from real papers")
    elif verified + likely == total:
        print(f"\n✅ CLAIM VERIFIED!")
        print(f"   All {total} rows appear to be real astronomical data")
    else:
        print(f"\n⚠️  CLAIM NEEDS VERIFICATION!")
        print(f"   Some rows need manual verification")
    
    # Recommendations
    print(f"\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if suspicious > 0:
        print(f"\n1. IMMEDIATELY remove/replace {suspicious} suspicious rows")
    
    if unknown > 0:
        print(f"\n2. Verify {unknown} unknown sources:")
        print(f"   - Check if they are in published papers")
        print(f"   - Add references to Sources.md")
        print(f"   - Or remove if provenance unclear")
    
    print(f"\n3. For all 'LIKELY_REAL' sources:")
    print(f"   - Find paper references")
    print(f"   - Add to Sources.md")
    print(f"   - Verify data values match papers")
    
    print(f"\n" + "="*80)

if __name__ == '__main__':
    main()
