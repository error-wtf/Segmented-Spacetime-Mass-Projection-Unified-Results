#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproducibility Checker

Verifies that examples, tests, and instructions are reproducible

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import re

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

def check_install_scripts(root):
    """Check installation script completeness"""
    checks = []
    
    # Check for install scripts
    install_ps1 = root / 'install.ps1'
    install_sh = root / 'install.sh'
    
    checks.append({
        'item': 'Windows install script',
        'file': 'install.ps1',
        'exists': install_ps1.exists(),
        'type': 'installation'
    })
    
    checks.append({
        'item': 'Linux/Mac install script',
        'file': 'install.sh',
        'exists': install_sh.exists(),
        'type': 'installation'
    })
    
    # Check README for install instructions
    readme = root / 'README.md'
    if readme.exists():
        with open(readme, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        has_install = 'install' in content.lower()
        checks.append({
            'item': 'Installation instructions in README',
            'file': 'README.md',
            'exists': has_install,
            'type': 'documentation'
        })
    
    return checks

def check_test_infrastructure(root):
    """Check test reproducibility infrastructure"""
    checks = []
    
    # Check for test runner
    test_runner = root / 'run_full_suite.py'
    checks.append({
        'item': 'Main test runner',
        'file': 'run_full_suite.py',
        'exists': test_runner.exists(),
        'type': 'testing'
    })
    
    # Check for pytest.ini
    pytest_ini = root / 'pytest.ini'
    checks.append({
        'item': 'Pytest configuration',
        'file': 'pytest.ini',
        'exists': pytest_ini.exists(),
        'type': 'testing'
    })
    
    # Check for requirements
    requirements = root / 'requirements.txt'
    checks.append({
        'item': 'Python dependencies',
        'file': 'requirements.txt',
        'exists': requirements.exists(),
        'type': 'dependencies'
    })
    
    return checks

def check_example_reproducibility(root):
    """Check if examples are reproducible"""
    checks = []
    
    # Check for example scripts
    example_patterns = ['example*.py', '*_example.py', 'demo*.py']
    
    example_count = 0
    for pattern in example_patterns:
        example_count += len(list(root.glob(f'**/{pattern}')))
    
    checks.append({
        'item': 'Example scripts',
        'count': example_count,
        'exists': example_count > 0,
        'type': 'examples'
    })
    
    # Check for data files
    data_dir = root / 'data'
    checks.append({
        'item': 'Data directory',
        'file': 'data/',
        'exists': data_dir.exists(),
        'type': 'data'
    })
    
    return checks

def check_documentation_completeness(root):
    """Check documentation for reproducibility"""
    checks = []
    
    key_docs = [
        ('README.md', 'Main README'),
        ('CONTRIBUTING.md', 'Contributing guide'),
        ('TROUBLESHOOTING.md', 'Troubleshooting guide'),
        ('docs/QUICK_START.md', 'Quick start guide')
    ]
    
    for filepath, name in key_docs:
        full_path = root / filepath
        checks.append({
            'item': name,
            'file': filepath,
            'exists': full_path.exists(),
            'type': 'documentation'
        })
    
    return checks

def main():
    """Check reproducibility of the project"""
    print("="*80)
    print("REPRODUCIBILITY CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    
    # Run all checks
    print("Checking installation infrastructure...")
    install_checks = check_install_scripts(root)
    
    print("Checking test infrastructure...")
    test_checks = check_test_infrastructure(root)
    
    print("Checking examples...")
    example_checks = check_example_reproducibility(root)
    
    print("Checking documentation...")
    doc_checks = check_documentation_completeness(root)
    
    all_checks = install_checks + test_checks + example_checks + doc_checks
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'REPRODUCIBILITY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Reproducibility Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        
        total = len(all_checks)
        passed = sum(1 for c in all_checks if c['exists'])
        
        f.write(f"- **Total Checks:** {total}\n")
        f.write(f"- **Passed:** {passed}\n")
        f.write(f"- **Success Rate:** {passed/total*100:.1f}%\n\n")
        
        if passed == total:
            f.write("✅ **Fully reproducible!**\n\n")
        elif passed >= total * 0.8:
            f.write("✅ **Highly reproducible**\n\n")
        else:
            f.write("⚠️  **Needs improvement for reproducibility**\n\n")
        
        f.write("---\n\n")
        
        # Detailed results
        f.write("## 📋 Detailed Checks\n\n")
        
        categories = {
            'installation': 'Installation Infrastructure',
            'testing': 'Test Infrastructure',
            'dependencies': 'Dependencies',
            'examples': 'Examples',
            'data': 'Data Files',
            'documentation': 'Documentation'
        }
        
        for cat_key, cat_name in categories.items():
            cat_checks = [c for c in all_checks if c.get('type') == cat_key]
            if cat_checks:
                f.write(f"### {cat_name}\n\n")
                for check in cat_checks:
                    status = '✅' if check['exists'] else '❌'
                    f.write(f"{status} **{check['item']}**")
                    if 'file' in check:
                        f.write(f" (`{check['file']}`)")
                    if 'count' in check:
                        f.write(f" - {check['count']} found")
                    f.write("\n")
                f.write("\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 🎯 Reproducibility Best Practices\n\n")
        f.write("### For Users\n")
        f.write("- Clear installation instructions\n")
        f.write("- Automated setup scripts\n")
        f.write("- Complete dependency lists\n")
        f.write("- Working examples\n\n")
        
        f.write("### For Developers\n")
        f.write("- Comprehensive test suite\n")
        f.write("- CI/CD configuration\n")
        f.write("- Development environment docs\n")
        f.write("- Code style guidelines\n\n")
        
        f.write("### For Researchers\n")
        f.write("- Data availability\n")
        f.write("- Analysis scripts\n")
        f.write("- Expected results documented\n")
        f.write("- Methodology clearly described\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_reproducibility.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print(f"Reproducibility: {passed}/{total} checks passed ({passed/total*100:.1f}%)")

if __name__ == '__main__':
    main()
