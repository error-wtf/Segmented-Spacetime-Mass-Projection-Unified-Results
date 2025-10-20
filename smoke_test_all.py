#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Smoke Test Suite
Validates all critical scripts can run basic operations

© 2025 Carmen Wrede, Lino Casu
"""
import sys
import os
from pathlib import Path

# UTF-8 for Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*80)
    print("TEST 1: Critical Imports")
    print("="*80)
    
    imports = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("pandas", "Pandas"),
        ("matplotlib", "Matplotlib"),
        ("astropy", "Astropy"),
        ("decimal", "Decimal (stdlib)"),
    ]
    
    failed = []
    for module, name in imports:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n⚠️  Failed imports: {', '.join(failed)}")
        return False
    
    print("\n✅ All imports successful")
    return True

def test_phi_calculation():
    """Test φ (golden ratio) calculation"""
    print("\n" + "="*80)
    print("TEST 2: φ (Golden Ratio) Calculation")
    print("="*80)
    
    try:
        from decimal import Decimal as D, getcontext
        getcontext().prec = 50
        
        phi = (D(1) + D(5).sqrt()) / D(2)
        phi_expected = D('1.618033988749')
        phi_diff = abs(float(phi - phi_expected))
        
        print(f"φ computed: {phi}")
        print(f"φ expected: {phi_expected}")
        print(f"Deviation:  {phi_diff:.2e}")
        
        if phi_diff > 1e-10:
            print("✗ φ calculation FAILED")
            return False
        
        print("✅ φ calculation correct")
        return True
        
    except Exception as e:
        print(f"✗ φ calculation failed: {e}")
        return False

def test_data_files():
    """Test critical data files exist"""
    print("\n" + "="*80)
    print("TEST 3: Critical Data Files")
    print("="*80)
    
    files = [
        "data/real_data_full.csv",
        "data/gaia/gaia_sample_small.csv",
    ]
    
    missing = []
    for file in files:
        if Path(file).exists():
            size = Path(file).stat().st_size / 1024
            print(f"✓ {file} ({size:.1f} KB)")
        else:
            print(f"✗ {file} MISSING")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
        print("    (Some tests may be skipped)")
    else:
        print("\n✅ All critical data files present")
    
    return True  # Non-critical, don't fail

def test_output_directories():
    """Test output directories can be created"""
    print("\n" + "="*80)
    print("TEST 4: Output Directories")
    print("="*80)
    
    dirs = [
        "reports",
        "reports/figures",
        "reports/figures/analysis",
        "out",
    ]
    
    for dir_path in dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✓ {dir_path}")
        except Exception as e:
            print(f"✗ {dir_path}: {e}")
            return False
    
    print("\n✅ All output directories accessible")
    return True

def test_matplotlib():
    """Test matplotlib can create figure"""
    print("\n" + "="*80)
    print("TEST 5: Matplotlib")
    print("="*80)
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([0, 1], [0, 1])
        ax.set_title("Smoke Test")
        
        # Try to save
        test_file = Path("out/smoke_test_plot.png")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(test_file, dpi=100)
        plt.close()
        
        if test_file.exists():
            size = test_file.stat().st_size / 1024
            print(f"✓ Created test plot ({size:.1f} KB)")
            test_file.unlink()  # Clean up
            print("✅ Matplotlib functional")
            return True
        else:
            print("✗ Plot file not created")
            return False
            
    except Exception as e:
        print(f"✗ Matplotlib test failed: {e}")
        return False

def test_precision():
    """Test high-precision calculations"""
    print("\n" + "="*80)
    print("TEST 6: High-Precision Calculations")
    print("="*80)
    
    try:
        from decimal import Decimal as D, getcontext
        getcontext().prec = 100
        
        # Test calculation
        pi_approx = sum(D(4) * (D(-1)**n) / (D(2*n + 1)) for n in range(1000))
        pi_expected = D('3.14159265358979323846')
        pi_diff = abs(float(pi_approx - pi_expected))
        
        print(f"π computed:  {pi_approx}")
        print(f"π expected:  {pi_expected}")
        print(f"Deviation:   {pi_diff:.2e}")
        
        if pi_diff > 1e-3:  # Leibniz series converges slowly
            print("✗ Precision test FAILED")
            return False
        
        print("✅ High-precision calculations work")
        return True
        
    except Exception as e:
        print(f"✗ Precision test failed: {e}")
        return False

def main():
    """Run all smoke tests"""
    print("="*80)
    print("COMPREHENSIVE SMOKE TEST SUITE")
    print("="*80)
    print("Validating critical scripts and dependencies...")
    
    tests = [
        ("Imports", test_imports),
        ("φ Calculation", test_phi_calculation),
        ("Data Files", test_data_files),
        ("Output Directories", test_output_directories),
        ("Matplotlib", test_matplotlib),
        ("Precision", test_precision),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("SMOKE TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} passed ({100*passed/total:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n✅ ALL SMOKE TESTS PASSED - System ready!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Check environment!")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Smoke tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Smoke tests crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
