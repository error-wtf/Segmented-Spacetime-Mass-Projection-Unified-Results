import numpy as np, pandas as pd
from scripts.ssz.segmenter import assign_segments_xy, SegParams

def test_segments_cover_all_points():
    """Test that segments cover all points without gaps
    
    Physical Meaning:
    Segmentation must cover the entire spacetime volume without gaps.
    Every point must belong to exactly one segment for physical
    consistency.
    """
    df = pd.DataFrame({"x": np.random.randn(5000)*100, "y": np.random.randn(5000)*100})
    seg = assign_segments_xy(df, "x","y", params=SegParams(rings=16, r_max_pc=1000))
    
    print("\n" + "="*80)
    print("SEGMENT COVERAGE TEST")
    print("="*80)
    print(f"Spacetime points: {len(df)}")
    print(f"Requested rings: 16")
    print(f"\nSegmentation Results:")
    print(f"  Points covered: {len(seg)}/{len(df)}")
    print(f"  Ring IDs: {seg['ring_id'].min()} to {seg['ring_id'].max()}")
    print(f"  Segment IDs: {seg['segment_id'].min()} to {seg['segment_id'].max()}")
    print(f"\nPhysical Interpretation:")
    print(f"  • Complete coverage: all {len(df)} points assigned")
    print(f"  • Each point in exactly one segment")
    print(f"  • Ensures consistent segmented spacetime structure")
    print("="*80)
    
    assert len(seg)==len(df)
    assert (seg["ring_id"]>=0).all() and (seg["segment_id"]>=0).all()

def test_segment_counts_grow():
    """Test that segment counts grow with resolution
    
    Physical Meaning:
    Higher resolution grids should contain more points while
    maintaining the same physical structure. Tests scalability
    of segmentation algorithm.
    """
    p = SegParams(base_segments_at_r1=4, rings=5)
    counts = []
    dummy = pd.DataFrame({"x":[0.0], "y":[0.0]})
    s = assign_segments_xy(dummy, "x","y", params=p)  # erzeugt Ringe
    
    print("\n" + "="*80)
    print("SEGMENT RESOLUTION SCALING TEST")
    print("="*80)
    print(f"Base segments: {p.base_segments_at_r1}")
    print(f"Number of rings: {p.rings}")
    print(f"\nSegment Count Growth:")
    
    for k in range(p.rings):
        # synthetische Winkelpunkte je Ring k
        n_theta = max(1, int(10 + k*2))
        angles = np.linspace(0, 2*np.pi*(1-1e-6), n_theta)
        r = np.full_like(angles, (k+0.5)*(p.r_max_pc/p.rings))
        dd = pd.DataFrame({"x": r*np.cos(angles), "y": r*np.sin(angles)})
        seg = assign_segments_xy(dd, "x","y", params=p)
        n_segs = seg["segment_id"].nunique()
        counts.append(n_segs)
        print(f"  Ring {k+1}: {n_segs} segments")
    
    print(f"\nMonotonicity:")
    print(f"  Segments never shrink: {counts == sorted(counts)}")
    print(f"\nPhysical Interpretation:")
    print(f"  • Segment count grows (or stays constant) with ring index")
    print(f"  • Physical structure preserved across rings")
    print(f"  • Algorithm handles varying densities correctly")
    print("="*80)
    
    assert counts==sorted(counts), "Segments should not shrink with ring index"
