#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the impact of φ (golden ratio) based geometry on paired test results

φ = (1+√5)/2 ≈ 1.618 is the GEOMETRIC FOUNDATION of segmented spacetime:
- φ-spiral geometry provides self-similar scaling
- Natural boundary at r_φ = (φ/2)r_s emerges from geometry  
- φ-derived mass corrections Δ(M) = A*exp(-α*rs) + B

Compares three modes:
1. hybrid (WITH φ-based geometry: φ/2 boundary + Δ(M)) - DEFAULT
2. geodesic (WITHOUT φ-based corrections, pure GR)
3. hint (ONLY z_geom_hint if available)

This demonstrates that φ-based geometry is FUNDAMENTAL (not optional).
"""
import subprocess
import json
from pathlib import Path

print("="*80)
print("TESTING PHI CORRECTION IMPACT ON PAIRED TEST")
print("="*80)
print()

modes = {
    "hybrid": "WITH phi corrections (Delta(M) = A*exp(-alpha*rs) + B)",
    "geodesic": "WITHOUT phi corrections (pure GR)",
    "hint": "ONLY z_geom_hint (if available)"
}

results = {}

for mode, description in modes.items():
    print(f"\n{'='*80}")
    print(f"MODE: {mode} - {description}")
    print(f"{'='*80}\n")
    
    cmd = [
        'python', 'segspace_all_in_one_extended.py',
        '--outdir', f'agent_out_{mode}',
        'eval-redshift',
        '--csv', 'data/real_data_emission_lines.csv',
        '--paired-stats',
        '--mode', mode
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              encoding='utf-8', errors='replace', timeout=60)
        
        # Read results
        result_file = Path(f'agent_out_{mode}/reports/redshift_paired_stats.json')
        if result_file.exists():
            with open(result_file) as f:
                stats = json.load(f)
            
            n_pairs = stats.get('N_pairs', 0)
            n_seg_better = stats.get('N_Seg_better', 0)
            share = stats.get('share_Seg_better', 0)
            p_value = stats.get('binom_two_sided_p', 1.0)
            
            print(f"Results:")
            print(f"  SEG wins: {n_seg_better}/{n_pairs} ({share*100:.1f}%)")
            print(f"  p-value: {p_value:.4f}")
            
            if p_value < 0.05:
                print(f"  [SIGNIFICANT] (p < 0.05)")
            else:
                print(f"  [Not significant] (p >= 0.05)")
            
            results[mode] = {
                'n_pairs': n_pairs,
                'n_seg_better': n_seg_better,
                'share': share,
                'p_value': p_value
            }
        else:
            print(f"  [ERROR] Could not read results from {result_file}")
            results[mode] = None
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        results[mode] = None

print(f"\n{'='*80}")
print("COMPARISON SUMMARY")
print(f"{'='*80}\n")

if all(results.values()):
    print(f"{'Mode':<15} {'SEG Wins':<15} {'Win %':<10} {'p-value':<12} {'Significance'}")
    print("-"*80)
    
    for mode, description in modes.items():
        r = results[mode]
        if r:
            sig = "YES (p<0.05)" if r['p_value'] < 0.05 else "No (p>=0.05)"
            print(f"{mode:<15} {r['n_seg_better']}/{r['n_pairs']:<10} {r['share']*100:>6.1f}%   {r['p_value']:>8.4f}    {sig}")
    
    print()
    print("="*80)
    print("PHI CORRECTION IMPACT")
    print("="*80)
    
    hybrid_share = results['hybrid']['share']
    geodesic_share = results['geodesic']['share']
    
    improvement = (hybrid_share - geodesic_share) * 100
    
    print(f"\nWithout phi (geodesic): {geodesic_share*100:.1f}% wins")
    print(f"With phi (hybrid):      {hybrid_share*100:.1f}% wins")
    print(f"\nImprovement from phi:   {improvement:+.1f} percentage points")
    
    if improvement > 0:
        print(f"\n[YES] Phi corrections HELP! They add {improvement:.1f}% to win rate.")
    elif improvement < 0:
        print(f"\n[NO] Phi corrections HURT! They reduce win rate by {abs(improvement):.1f}%.")
    else:
        print(f"\n[NEUTRAL] Phi corrections have no net effect on win rate.")
    
    print(f"\nStatistical significance:")
    print(f"  Hybrid (with phi):   p = {results['hybrid']['p_value']:.4f}")
    print(f"  Geodesic (no phi):   p = {results['geodesic']['p_value']:.4f}")

print("\n" + "="*80)
print("Analysis complete!")
print("="*80)
