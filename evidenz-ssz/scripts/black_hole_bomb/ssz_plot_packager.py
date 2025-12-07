#!/usr/bin/env python3
"""
SSZ Plot Packager
=================
Generate publication-ready figures from the extended SSZ parameter scan and GR bridge outputs.

Outputs (written to d:/extended_results/plots/):
  - stabilization_heatmap_K64.png
  - delta_metrics_barplot.png
  - gr_correlation_scatter.png
  - amplitude_trace_best_mode.png

Perfect-Pair Mathematics Style (Casu & Wrede 2025)
© 2025 Carmen Wrede, Lino Casu
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
# Try d:/ first, fallback to local directory if not available
if Path('d:/extended_results').exists():
    DATA_DIR = Path('d:/extended_results')
else:
    DATA_DIR = Path('extended_results')
    DATA_DIR.mkdir(parents=True, exist_ok=True)

PLOTS_DIR = DATA_DIR / 'plots'
SCAN_CSV = DATA_DIR / 'parameter_scan_results.csv'
SUMMARY_JSON = DATA_DIR / 'scan_summary.json'
BRIDGE_JSON = DATA_DIR / 'gr_bridge_summary.json'
GROWTH_CSV = DATA_DIR.parent / 'growth_best_mode.csv'

PLOTS_DIR.mkdir(parents=True, exist_ok=True)
plt.style.use('dark_background')
sns.set_theme(style='darkgrid')

# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def load_dataframe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Missing required file: {path}')
    if path.suffix.lower() == '.csv':
        return pd.read_csv(path)
    raise ValueError(f'Unsupported file type: {path}')

def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f'Missing required file: {path}')
    with open(path, 'r') as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# PLOT BUILDERS
# ---------------------------------------------------------------------------

def figure_stabilization_heatmap(df: pd.DataFrame) -> None:
    subset = df[df['K_segments'] == 64]
    omegas = sorted(subset['Omega0'].unique())
    
    # Check if we have data to plot
    if len(omegas) == 0:
        print("[WARNING] No data available for K_segments=64, skipping heatmap")
        return
    
    fig, axes = plt.subplots(1, len(omegas), figsize=(5 * len(omegas), 4), sharey=True)
    if len(omegas) == 1:
        axes = [axes]

    vmin = subset['stabilization_index'].min()
    vmax = subset['stabilization_index'].max()

    for ax, omega in zip(axes, omegas):
        block = subset[subset['Omega0'] == omega]
        pivot = block.pivot(index='lambda_phi', columns='lambda_A', values='stabilization_index')
        sns.heatmap(pivot, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax, annot=True, fmt='.2f')
        ax.set_title(f'K=64, Omega0={omega:.2f}')
        ax.set_xlabel('lambda_A')
        ax.set_ylabel('lambda_phi')

    fig.suptitle('Stabilization Index S (K=64)', fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    outfile = PLOTS_DIR / 'stabilization_heatmap_K64.png'
    fig.savefig(outfile, dpi=250)
    plt.close(fig)
    print(f'[OK] {outfile}')

def figure_delta_barplot(summary: dict) -> None:
    rows = []
    for tag, label in [('top3_stabilizing', 'Stabilizing'), ('top3_destabilizing', 'Destabilizing')]:
        for item in summary[tag]:
            rows.append({
                'category': label,
                'rank': len(rows) + 1,
                'lambda_A': item['lambda_A'],
                'lambda_phi': item['lambda_phi'],
                'K_segments': item['K_segments'],
                'Omega0': item['Omega0'],
                'dUnstable': item['delta_unstable'],
                'dlogG': item['avg_delta_log_G'],
            })
    table = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)
    sns.barplot(data=table, x='rank', y='dUnstable', hue='category', ax=axes[0])
    axes[0].set_title('Delta Unstable Modes (Top 3)')
    axes[0].set_xlabel('Rank')
    axes[0].set_ylabel('dUnstable')

    sns.barplot(data=table, x='rank', y='dlogG', hue='category', ax=axes[1])
    axes[1].set_title('Average delta log(G) (Top 3)')
    axes[1].set_xlabel('Rank')
    axes[1].set_ylabel('dlogG')

    for ax in axes:
        ax.legend(loc='best')
        ax.grid(True, alpha=0.2)

    fig.suptitle('Top Stabilizing vs Destabilizing Metrics', fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    outfile = PLOTS_DIR / 'delta_metrics_barplot.png'
    fig.savefig(outfile, dpi=250)
    plt.close(fig)
    print(f'[OK] {outfile}')

def rebuild_bridge_metrics(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    ref_modes = [(0.10, 2), (0.20, 3), (0.30, 4)]
    for _, row in df.iterrows():
        lambda_A = float(row['lambda_A'])
        lambda_phi = float(row['lambda_phi'])
        K_seg = int(row['K_segments'])
        Omega0 = float(row['Omega0'])
        segment_proxy = K_seg * lambda_phi
        for omega, m in ref_modes:
            threshold = m * Omega0
            margin = threshold - omega
            normalized_gain = np.nan
            if margin > 0:
                normalized_gain = row['avg_delta_log_G'] / margin
            records.append({
                'lambda_A': lambda_A,
                'lambda_phi': lambda_phi,
                'K_segments': K_seg,
                'Omega0': Omega0,
                'segment_proxy': segment_proxy,
                'stabilization_index': row['stabilization_index'],
                'normalized_gain': normalized_gain,
                'omega_ref': omega,
                'm_ref': m,
            })
    return pd.DataFrame(records)

def figure_gr_scatter(df: pd.DataFrame) -> None:
    bridge_df = rebuild_bridge_metrics(df)
    bridge_df = bridge_df.dropna(subset=['normalized_gain'])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.scatterplot(data=bridge_df, x='normalized_gain', y='stabilization_index', hue='omega_ref', style='m_ref', ax=axes[0])
    axes[0].set_title('Normalized Gain vs Stabilization Index')
    axes[0].set_xlabel('normalized_gain')
    axes[0].set_ylabel('stabilization_index')

    sns.scatterplot(data=bridge_df, x='segment_proxy', y='stabilization_index', hue='omega_ref', style='m_ref', ax=axes[1])
    axes[1].set_title('Segment Proxy vs Stabilization Index')
    axes[1].set_xlabel('segment_proxy (K * lambda_phi)')
    axes[1].set_ylabel('stabilization_index')

    for ax in axes:
        ax.grid(True, alpha=0.2)

    fig.suptitle('SSZ vs GR Alignment Diagnostics', fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    outfile = PLOTS_DIR / 'gr_correlation_scatter.png'
    fig.savefig(outfile, dpi=250)
    plt.close(fig)
    print(f'[OK] {outfile}')

def figure_amplitude_trace(path: Path) -> None:
    if not path.exists():
        print(f'[WARN] Missing growth trace: {path} (skipping amplitude plot)')
        return
    growth_df = pd.read_csv(path)
    if {'roundtrip', 'amplitude'} - set(growth_df.columns):
        print(f'[WARN] growth file missing required columns: {path}')
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(growth_df['roundtrip'], growth_df['amplitude'], color='cyan', linewidth=2)
    ax.set_yscale('log')
    ax.set_xlabel('Roundtrip')
    ax.set_ylabel('Amplitude (log scale)')
    ax.set_title('Amplitude Trace (Best Mode)')
    ax.grid(True, alpha=0.3)

    outfile = PLOTS_DIR / 'amplitude_trace_best_mode.png'
    fig.tight_layout()
    fig.savefig(outfile, dpi=250)
    plt.close(fig)
    print(f'[OK] {outfile}')

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    try:
        scan_df = load_dataframe(SCAN_CSV)
        summary = load_json(SUMMARY_JSON)
        
        # Validate data before plotting
        if scan_df.empty:
            print(f'[WARNING] Empty dataframe from {SCAN_CSV}, skipping plots')
            return
        
        if BRIDGE_JSON.exists():
            load_json(BRIDGE_JSON)  # ensures file is present; data is recomputed directly from scan_df

        figure_stabilization_heatmap(scan_df)
        figure_delta_barplot(summary)
        figure_gr_scatter(scan_df)
        figure_amplitude_trace(GROWTH_CSV)

        print('\n[OK] Plot packager complete. Figures stored in d:/extended_results/plots/')
        
    except FileNotFoundError as e:
        print(f'[SKIP] Missing required data files: {e}')
        print('       Run ssz_parameter_scan.py first to generate data.')
        sys.exit(0)  # Exit gracefully, not an error
    except Exception as e:
        print(f'[ERROR] Plot generation failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
