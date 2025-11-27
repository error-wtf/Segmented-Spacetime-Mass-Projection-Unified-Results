#!/usr/bin/env python3
"""
SSZ ↔ GR Bridge Analysis
=========================
Links Segmented Spacetime stabilization metrics to classical GR superradiance scalings.

Outputs:
- d:/extended_results/gr_bridge_summary.json
- d:/extended_results/gr_bridge_report.md

Perfect-Pair Mathematics Style (Casu & Wrede 2025)
© 2025 Carmen Wrede, Lino Casu
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
DATA_DIR = Path('d:/extended_results')
SCAN_CSV = DATA_DIR / 'parameter_scan_results.csv'
SUMMARY_JSON = DATA_DIR / 'scan_summary.json'
OUTPUT_JSON = DATA_DIR / 'gr_bridge_summary.json'
OUTPUT_REPORT = DATA_DIR / 'gr_bridge_report.md'

GR_CONSTANTS = {
    'c': 299_792_458.0,          # speed of light (m/s)
    'G': 6.67430e-11,            # gravitational constant (SI)
    'M_sun': 1.98847e30,         # solar mass (kg)
}

REFERENCE_MODES = [
    {'omega': 0.10, 'm': 2},
    {'omega': 0.20, 'm': 3},
    {'omega': 0.30, 'm': 4},
]

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def load_data():
    df = pd.read_csv(SCAN_CSV)
    with open(SUMMARY_JSON, 'r') as f:
        summary = json.load(f)
    return df, summary

def classical_superradiance_threshold(m, Omega0):
    """Classical GR condition: superradiance when omega < m * Omega0"""
    return m * Omega0

def normalized_gain_metric(row, omega, m):
    """Approximate ratio of observed Δlog(G) vs. GR threshold margin."""
    threshold = classical_superradiance_threshold(m, row['Omega0'])
    margin = threshold - omega
    if margin <= 0:
        return np.nan
    return row['avg_delta_log_G'] / margin

def segment_density_proxy(K_segments, lambda_phi):
    """Proxy for φ-spiral twisting vs. GR frame dragging."""
    return K_segments * lambda_phi

def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return [to_serializable(v) for v in obj.tolist()]
    return obj


def build_bridge_metrics(df):
    records = []
    for _, row in df.iterrows():
        lambda_A = float(row['lambda_A'])
        lambda_phi = float(row['lambda_phi'])
        K_seg = int(row['K_segments'])
        Omega0 = float(row['Omega0'])
        for ref in REFERENCE_MODES:
            metric = normalized_gain_metric(row, ref['omega'], ref['m'])
            records.append({
                'lambda_A': lambda_A,
                'lambda_phi': lambda_phi,
                'K_segments': K_seg,
                'Omega0': Omega0,
                'omega_ref': ref['omega'],
                'm_ref': ref['m'],
                'normalized_gain': float(metric) if metric is not None and not np.isnan(metric) else None,
                'segment_density_proxy': float(segment_density_proxy(K_seg, lambda_phi)),
                'stabilization_index': float(row['stabilization_index']),
            })
    bridge_df = pd.DataFrame(records)
    return bridge_df

def summarize_correlations(bridge_df):
    grouped = bridge_df.groupby(['omega_ref', 'm_ref'])
    results = []
    for (omega, m), sub in grouped:
        valid = sub.dropna(subset=['normalized_gain'])
        corr = valid['normalized_gain'].corr(valid['stabilization_index'])
        seg_corr = valid['segment_density_proxy'].corr(valid['stabilization_index'])
        results.append({
            'omega_ref': omega,
            'm_ref': m,
            'corr_gain_vs_stabilization': float(corr) if not np.isnan(corr) else None,
            'corr_segment_vs_stabilization': float(seg_corr) if not np.isnan(seg_corr) else None,
            'mean_normalized_gain': float(valid['normalized_gain'].mean()) if len(valid) else None,
            'std_normalized_gain': float(valid['normalized_gain'].std()) if len(valid) else None,
        })
    return results

def identify_alignment_cases(bridge_df, summary):
    top_stab = summary['top3_stabilizing']
    top_destab = summary['top3_destabilizing']
    def extract_cases(cases):
        extracted = []
        for case in cases:
            sub = bridge_df[(bridge_df['lambda_A'] == case['lambda_A']) &
                            (bridge_df['lambda_phi'] == case['lambda_phi']) &
                            (bridge_df['K_segments'] == case['K_segments']) &
                            (bridge_df['Omega0'] == case['Omega0'])]
            avg_norm_gain = sub['normalized_gain'].mean()
            avg_seg_proxy = sub['segment_density_proxy'].mean()
            extracted.append({
                'lambda_A': float(case['lambda_A']),
                'lambda_phi': float(case['lambda_phi']),
                'K_segments': int(case['K_segments']),
                'Omega0': float(case['Omega0']),
                'stabilization_index': float(case['stabilization_index']),
                'avg_normalized_gain': float(avg_norm_gain) if not np.isnan(avg_norm_gain) else None,
                'segment_density_proxy': float(avg_seg_proxy) if not np.isnan(avg_seg_proxy) else None,
            })
        return extracted
    return extract_cases(top_stab), extract_cases(top_destab)

def export_report(correlations, align_stab, align_destab):
    lines = [
        "# SSZ <-> GR Bridge Report",
        "",
        "## Correlation Overview",
    ]
    for item in correlations:
        lines.append(f"- omega={item['omega_ref']:.2f}, m={item['m_ref']}")
        lines.append(f"  - corr(normalized_gain, S) = {item['corr_gain_vs_stabilization']}")
        lines.append(f"  - corr(segment_proxy, S) = {item['corr_segment_vs_stabilization']}")
        lines.append(f"  - mean normalized gain = {item['mean_normalized_gain']}")
        lines.append(f"  - std normalized gain = {item['std_normalized_gain']}")
        lines.append("")
    lines.append("## Top Stabilizing Configurations")
    for case in align_stab:
        lines.append(f"- lambda_A={case['lambda_A']:.2f}, lambda_phi={case['lambda_phi']:.2f}, K={case['K_segments']}, Omega0={case['Omega0']:.2f}")
        lines.append(f"  - S = {case['stabilization_index']}")
        lines.append(f"  - avg normalized gain = {case['avg_normalized_gain']}")
        lines.append(f"  - segment proxy = {case['segment_density_proxy']}")
        lines.append("")
    lines.append("## Top Destabilizing Configurations")
    for case in align_destab:
        lines.append(f"- lambda_A={case['lambda_A']:.2f}, lambda_phi={case['lambda_phi']:.2f}, K={case['K_segments']}, Omega0={case['Omega0']:.2f}")
        lines.append(f"  - S = {case['stabilization_index']}")
        lines.append(f"  - avg normalized gain = {case['avg_normalized_gain']}")
        lines.append(f"  - segment proxy = {case['segment_density_proxy']}")
        lines.append("")
    OUTPUT_REPORT.write_text("\n".join(lines))

# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df, summary = load_data()
    bridge_df = build_bridge_metrics(df)
    correlations = summarize_correlations(bridge_df)
    align_stab, align_destab = identify_alignment_cases(bridge_df, summary)

    result = {
        'correlations': correlations,
        'top_stabilizing_alignment': align_stab,
        'top_destabilizing_alignment': align_destab,
        'reference_modes': REFERENCE_MODES,
    }

    OUTPUT_JSON.write_text(json.dumps(to_serializable(result), indent=2))
    export_report(correlations, align_stab, align_destab)

    print("=" * 80)
    print("SSZ <-> GR Bridge Analysis Complete")
    print("=" * 80)
    print(f"Results JSON: {OUTPUT_JSON}")
    print(f"Report Markdown: {OUTPUT_REPORT}")

if __name__ == '__main__':
    main()
