#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consistency Checker

Verifies terminology, naming, and cross-reference consistency

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import re
from collections import defaultdict

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Key terminology variations to check
TERMINOLOGY = {
    'phi_radius': {
        'preferred': 'φ-radius',
        'variants': ['phi-radius', 'phi radius', 'r_phi', 'r_φ'],
        'category': 'core_concept'
    },
    'schwarzschild': {
        'preferred': 'Schwarzschild radius',
        'variants': ['schwarzschild', 'r_s', 'r_schw'],
        'category': 'standard_physics'
    },
    'golden_ratio': {
        'preferred': 'golden ratio',
        'variants': ['φ', 'phi', 'golden number'],
        'category': 'mathematical'
    },
    'segment': {
        'preferred': 'spacetime segment',
        'variants': ['segment', 'space segment', 'discrete segment'],
        'category': 'core_concept'
    }
}

def check_terminology_usage(text, term_name, term_data):
    """Check consistency of terminology usage"""
    preferred = term_data['preferred']
    variants = term_data['variants']
    
    # Count occurrences
    counts = {}
    text_lower = text.lower()
    
    # Check preferred
    counts[preferred] = len(re.findall(re.escape(preferred.lower()), text_lower))
    
    # Check variants
    for variant in variants:
        counts[variant] = len(re.findall(re.escape(variant.lower()), text_lower))
    
    total = sum(counts.values())
    preferred_count = counts[preferred]
    
    consistency = (preferred_count / total * 100) if total > 0 else 100
    
    return {
        'total_uses': total,
        'preferred_uses': preferred_count,
        'consistency_pct': consistency,
        'counts': counts
    }

def check_file_naming(root):
    """Check file naming consistency"""
    issues = []
    
    # Patterns to check
    patterns = {
        'spaces': re.compile(r'.*\s+.*'),  # Spaces in filenames
        'uppercase_ext': re.compile(r'.*\.[A-Z]+$'),  # Uppercase extensions
        'mixed_case': re.compile(r'.*[a-z]+[A-Z]+.*'),  # Mixed case (not camelCase or snake_case)
    }
    
    for md_file in root.glob('**/*.md'):
        if '__pycache__' in str(md_file):
            continue
        
        name = md_file.name
        
        # Check for spaces
        if patterns['spaces'].match(name):
            issues.append({
                'file': str(md_file.relative_to(root)),
                'issue': 'Contains spaces',
                'suggestion': name.replace(' ', '_')
            })
        
        # Check for uppercase extensions
        if patterns['uppercase_ext'].match(name):
            issues.append({
                'file': str(md_file.relative_to(root)),
                'issue': 'Uppercase extension',
                'suggestion': name.lower()
            })
    
    return issues

def analyze_doc(filepath):
    """Analyze a document for consistency"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        results = {}
        for term_name, term_data in TERMINOLOGY.items():
            results[term_name] = check_terminology_usage(content, term_name, term_data)
        
        return results
    except Exception as e:
        return None

def main():
    """Check consistency across documentation"""
    print("="*80)
    print("CONSISTENCY CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    
    # Check key docs
    key_docs = [
        'README.md',
        'docs/PHYSICS_FOUNDATIONS.md',
        'docs/MATHEMATICAL_FORMULAS.md',
        'docs/QUICK_START.md'
    ]
    
    # Terminology results
    term_results = {}
    
    print("Checking terminology consistency...")
    for doc_path in key_docs:
        full_path = root / doc_path
        if full_path.exists():
            print(f"  Analyzing {doc_path}...")
            analysis = analyze_doc(full_path)
            if analysis:
                term_results[doc_path] = analysis
    
    # File naming
    print("\nChecking file naming conventions...")
    naming_issues = check_file_naming(root)
    print(f"  Found {len(naming_issues)} naming issues")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'CONSISTENCY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Consistency Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        
        # Average consistency
        all_consistencies = []
        for doc_data in term_results.values():
            for term_data in doc_data.values():
                if term_data['total_uses'] > 0:
                    all_consistencies.append(term_data['consistency_pct'])
        
        avg_consistency = sum(all_consistencies) / len(all_consistencies) if all_consistencies else 0
        
        f.write(f"- **Average Terminology Consistency:** {avg_consistency:.1f}%\n")
        f.write(f"- **Documents Analyzed:** {len(term_results)}\n")
        f.write(f"- **Terms Tracked:** {len(TERMINOLOGY)}\n")
        f.write(f"- **File Naming Issues:** {len(naming_issues)}\n\n")
        
        if avg_consistency >= 70:
            f.write("✅ **Good terminology consistency**\n\n")
        else:
            f.write("⚠️  **Terminology needs standardization**\n\n")
        
        f.write("---\n\n")
        
        # Terminology details
        f.write("## 📋 Terminology Analysis\n\n")
        
        for term_name, term_data in TERMINOLOGY.items():
            f.write(f"### {term_name.replace('_', ' ').title()}\n\n")
            f.write(f"**Preferred term:** `{term_data['preferred']}`\n\n")
            
            # Aggregate usage across docs
            total_uses = 0
            preferred_uses = 0
            
            for doc_path, doc_data in term_results.items():
                if term_name in doc_data:
                    total_uses += doc_data[term_name]['total_uses']
                    preferred_uses += doc_data[term_name]['preferred_uses']
            
            if total_uses > 0:
                consistency = (preferred_uses / total_uses * 100)
                f.write(f"**Overall consistency:** {consistency:.1f}%\n")
                f.write(f"- Total uses: {total_uses}\n")
                f.write(f"- Preferred form: {preferred_uses}\n")
                f.write(f"- Variants: {total_uses - preferred_uses}\n\n")
                
                if consistency >= 80:
                    f.write("✅ Highly consistent\n\n")
                elif consistency >= 50:
                    f.write("⚠️  Could be more consistent\n\n")
                else:
                    f.write("🔴 Needs standardization\n\n")
            else:
                f.write("ℹ️  Term not used in analyzed documents\n\n")
        
        # File naming issues
        if naming_issues:
            f.write("## 📁 File Naming Issues\n\n")
            for issue in naming_issues[:10]:  # Limit to 10
                f.write(f"**{issue['file']}**\n")
                f.write(f"- Issue: {issue['issue']}\n")
                f.write(f"- Suggestion: `{issue['suggestion']}`\n\n")
        else:
            f.write("## ✅ File Naming\n\n")
            f.write("No issues found with file naming conventions.\n\n")
        
        f.write("---\n\n")
        
        # Best practices
        f.write("## 📐 Consistency Best Practices\n\n")
        f.write("### Terminology\n")
        f.write("- Use preferred terms consistently\n")
        f.write("- Define terms on first use\n")
        f.write("- Maintain glossary for reference\n\n")
        
        f.write("### File Naming\n")
        f.write("- Use lowercase for extensions (.md not .MD)\n")
        f.write("- Use underscores or hyphens, not spaces\n")
        f.write("- Be descriptive but concise\n\n")
        
        f.write("### Cross-References\n")
        f.write("- Check links regularly\n")
        f.write("- Use relative paths when possible\n")
        f.write("- Keep reference structure flat\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_consistency.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print(f"Average consistency: {avg_consistency:.1f}%")

if __name__ == '__main__':
    main()
