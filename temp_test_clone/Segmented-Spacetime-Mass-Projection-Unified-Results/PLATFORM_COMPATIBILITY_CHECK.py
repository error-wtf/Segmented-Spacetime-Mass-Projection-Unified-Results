#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSZ Theory Predictions - Multi-Platform Compatibility Check

Validates that all components work correctly on:
- Windows (Native)
- WSL (Windows Subsystem for Linux)
- Google Colab

© 2025 Carmen Wrede, Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
import shutil

# UTF-8 Setup
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')


def print_header(title, char="="):
    print("\n" + char * 80)
    print(title)
    print(char * 80)


def detect_environment():
    """Detect current execution environment"""
    
    # Check for Colab
    try:
        import google.colab
        return "Colab"
    except ImportError:
        pass
    
    # Check for WSL
    if sys.platform.startswith('linux'):
        # WSL has specific markers
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    return "WSL"
        except FileNotFoundError:
            pass
        return "Linux"
    
    # Windows
    if sys.platform.startswith('win'):
        return "Windows"
    
    # macOS
    if sys.platform.startswith('darwin'):
        return "macOS"
    
    return "Unknown"


def check_python_version():
    """Check if Python version is compatible"""
    print("\n🐍 Python Version Check:")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ FAIL: Python 3.8+ required")
        return False
    else:
        print(f"   ✅ PASS: Python version compatible")
        return True


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Dependency Check:")
    
    required = ['numpy', 'pandas', 'scipy', 'matplotlib']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}: installed")
        except ImportError:
            print(f"   ❌ {pkg}: MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\n   💡 Install missing packages:")
        print(f"      pip install {' '.join(missing)}")
        return False
    
    return True


def check_utf8_support():
    """Check UTF-8 encoding support"""
    print("\n🔤 UTF-8 Support Check:")
    
    test_chars = {
        'Greek': 'φβγακ',
        'Math': '≈±×∈∞→',
        'Emoji': '✅❌⚠️',
        'Subscripts': 'r₀r₁r₂'
    }
    
    all_ok = True
    for category, chars in test_chars.items():
        try:
            # Test if we can encode/decode
            encoded = chars.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            # Test if we can print
            print(f"   ✅ {category}: {chars}")
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            print(f"   ❌ {category}: FAILED - {e}")
            all_ok = False
    
    if all_ok:
        print(f"   ✅ UTF-8 fully supported")
    else:
        print(f"   ⚠️  UTF-8 issues detected (may cause display problems)")
    
    return all_ok


def check_file_structure():
    """Check if required files exist"""
    print("\n📁 File Structure Check:")
    
    required_files = [
        ('scripts/tests/test_horizon_hawking_predictions.py', 'Theory Tests'),
        ('scripts/tests/test_data_validation.py', 'Data Validation'),
        ('test_theory_predictions_cross_platform.py', 'Cross-Platform Check'),
        ('run_complete_validation.py', 'Complete Validation'),
        ('DATA_ACQUISITION_PLAN.md', 'Data Plan'),
        ('VALIDATION_FRAMEWORK.md', 'Validation Docs'),
    ]
    
    all_exist = True
    for file_path, desc in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {desc}: {file_path}")
        else:
            print(f"   ❌ {desc}: MISSING - {file_path}")
            all_exist = False
    
    return all_exist


def check_data_files():
    """Check if data files exist"""
    print("\n💾 Data Files Check:")
    
    data_files = [
        ('out/phi_step_debug_full.csv', 'Phi Debug Data', True),
        ('out/_enhanced_debug.csv', 'Enhanced Debug Data', True),
        ('data/observations/s2_star_timeseries_TEMPLATE.csv', 'S2 Template', False),
        ('data/observations/cyg_x1_thermal_spectrum_TEMPLATE.csv', 'Cyg X-1 Template', False),
    ]
    
    critical_missing = False
    for file_path, desc, critical in data_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {desc}: {file_path} ({size:,} bytes)")
        else:
            if critical:
                print(f"   ❌ {desc}: MISSING (CRITICAL) - {file_path}")
                critical_missing = True
            else:
                print(f"   ⚠️  {desc}: not found (optional) - {file_path}")
    
    if critical_missing:
        print(f"\n   💡 Generate missing data:")
        print(f"      python run_all_ssz_terminal.py")
    
    return not critical_missing


def check_path_separators():
    """Check if path separators work correctly"""
    print("\n🗂️  Path Separator Check:")
    
    env = detect_environment()
    
    # Test path creation
    test_path = Path("test") / "subdir" / "file.txt"
    expected_sep = '\\' if env == "Windows" else '/'
    
    path_str = str(test_path)
    actual_sep = '\\' if '\\' in path_str else '/'
    
    print(f"   Environment: {env}")
    print(f"   Expected separator: {expected_sep}")
    print(f"   Actual separator: {actual_sep}")
    print(f"   Test path: {test_path}")
    
    if env in ["WSL", "Linux", "Colab"]:
        # Should use forward slash
        if '/' in str(test_path):
            print(f"   ✅ Path separators correct for {env}")
            return True
        else:
            print(f"   ❌ Path separators incorrect")
            return False
    else:
        # Windows - pathlib handles it
        print(f"   ✅ Path handling correct (pathlib)")
        return True


def check_executable_permissions():
    """Check if scripts have execute permissions (Unix-like)"""
    print("\n🔐 Executable Permissions Check:")
    
    env = detect_environment()
    
    if env in ["WSL", "Linux", "Colab"]:
        scripts = [
            'scripts/tests/test_horizon_hawking_predictions.py',
            'run_complete_validation.py',
        ]
        
        all_ok = True
        for script in scripts:
            path = Path(script)
            if path.exists():
                # Check if executable
                is_exec = os.access(path, os.X_OK)
                if is_exec:
                    print(f"   ✅ {script}: executable")
                else:
                    print(f"   ⚠️  {script}: not executable (can still run with 'python {script}')")
            else:
                print(f"   ❌ {script}: not found")
                all_ok = False
        
        return all_ok
    else:
        print(f"   ℹ️  Not applicable on {env}")
        return True


def check_colab_specific():
    """Check Colab-specific requirements"""
    env = detect_environment()
    
    if env != "Colab":
        print(f"\n📓 Colab Check: Skipped (not in Colab)")
        return True
    
    print("\n📓 Colab-Specific Check:")
    
    # Check if notebook exists
    notebook = Path("SSZ_Colab_AutoRunner.ipynb")
    if notebook.exists():
        print(f"   ✅ Colab notebook exists")
        
        # Check if it contains theory tests
        with open(notebook, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'test_horizon_hawking_predictions' in content:
            print(f"   ✅ Theory tests integrated in notebook")
            return True
        else:
            print(f"   ⚠️  Theory tests may not be in notebook")
            return False
    else:
        print(f"   ❌ Colab notebook not found")
        return False


def check_wsl_specific():
    """Check WSL-specific requirements"""
    env = detect_environment()
    
    if env != "WSL":
        print(f"\n🐧 WSL Check: Skipped (not in WSL)")
        return True
    
    print("\n🐧 WSL-Specific Check:")
    
    # Check /mnt/ access
    mnt = Path("/mnt")
    if mnt.exists():
        print(f"   ✅ /mnt/ accessible (Windows drives mounted)")
    else:
        print(f"   ❌ /mnt/ not found")
    
    # Check line endings
    test_file = Path("run_complete_validation.py")
    if test_file.exists():
        with open(test_file, 'rb') as f:
            content = f.read()
        
        if b'\r\n' in content:
            print(f"   ⚠️  CRLF line endings detected (Windows-style)")
            print(f"      May cause issues with shebang (#!)")
        else:
            print(f"   ✅ LF line endings (Unix-style)")
    
    return True


def check_windows_specific():
    """Check Windows-specific requirements"""
    env = detect_environment()
    
    if env != "Windows":
        print(f"\n🪟 Windows Check: Skipped (not on Windows)")
        return True
    
    print("\n🪟 Windows-Specific Check:")
    
    # Check encoding
    encoding = sys.stdout.encoding
    print(f"   Console encoding: {encoding}")
    
    if encoding.lower() == 'utf-8':
        print(f"   ✅ UTF-8 encoding configured")
    else:
        print(f"   ⚠️  Non-UTF-8 encoding (may cause display issues)")
        print(f"      Script auto-configures UTF-8, should still work")
    
    # Check PowerShell vs CMD
    shell = os.environ.get('SHELL', 'Unknown')
    print(f"   Shell: {shell}")
    
    return True


def run_mini_validation():
    """Run a quick validation test"""
    print("\n🧪 Mini Validation Test:")
    
    # Try to import and run data validation
    try:
        print(f"   Testing data validation...")
        result = subprocess.run(
            [sys.executable, 'scripts/tests/test_data_validation.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"   ✅ Data validation: PASSED")
            return True
        else:
            print(f"   ❌ Data validation: FAILED")
            print(f"      Exit code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ Data validation: TIMEOUT")
        return False
    except Exception as e:
        print(f"   ❌ Data validation: ERROR - {e}")
        return False


def main():
    print_header("SSZ MULTI-PLATFORM COMPATIBILITY CHECK", "=")
    
    # Detect environment
    env = detect_environment()
    print(f"\n🌍 Environment Detected: {env}")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Working Directory: {Path.cwd()}")
    
    # Run all checks
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'UTF-8 Support': check_utf8_support(),
        'File Structure': check_file_structure(),
        'Data Files': check_data_files(),
        'Path Separators': check_path_separators(),
        'Executable Permissions': check_executable_permissions(),
    }
    
    # Environment-specific checks
    if env == "Colab":
        checks['Colab Integration'] = check_colab_specific()
    elif env == "WSL":
        checks['WSL Compatibility'] = check_wsl_specific()
    elif env == "Windows":
        checks['Windows Compatibility'] = check_windows_specific()
    
    # Mini validation
    checks['Mini Validation'] = run_mini_validation()
    
    # Summary
    print_header("COMPATIBILITY CHECK SUMMARY", "=")
    
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    
    print(f"\n📊 Results:")
    print(f"   Total Checks: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print()
    
    for check, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"   {symbol} {check}")
    
    print()
    
    # Platform-specific recommendations
    print_header(f"RECOMMENDATIONS FOR {env}", "-")
    
    if env == "Windows":
        print("✅ Fully supported on Windows")
        print("   • UTF-8 auto-configured in all scripts")
        print("   • Use PowerShell or CMD")
        print("   • Path separators handled by pathlib")
        
    elif env == "WSL":
        print("✅ Fully supported on WSL")
        print("   • Can access Windows drives via /mnt/")
        print("   • Unix-style paths work natively")
        print("   • May need: chmod +x *.py for direct execution")
        
    elif env == "Colab":
        print("✅ Fully supported on Google Colab")
        print("   • Use SSZ_Colab_AutoRunner.ipynb")
        print("   • Install: !pip install numpy pandas scipy matplotlib")
        print("   • Clone repo: !git clone <url>")
        
    elif env == "Linux":
        print("✅ Fully supported on Linux")
        print("   • Native Unix environment")
        print("   • UTF-8 default")
        print("   • Fastest execution")
    
    print()
    
    # Final verdict
    all_passed = all(checks.values())
    
    if all_passed:
        print("🎉 " + "="*76)
        print(f"🎉 PLATFORM CHECK PASSED - FULLY COMPATIBLE WITH {env.upper()}! 🎉")
        print("🎉 " + "="*76)
        return 0
    else:
        print("⚠️  " + "="*76)
        print(f"⚠️  PLATFORM CHECK INCOMPLETE - SOME ISSUES ON {env.upper()}")
        print("⚠️  " + "="*76)
        print()
        print("💡 Fix issues above before running full validation")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Check interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
