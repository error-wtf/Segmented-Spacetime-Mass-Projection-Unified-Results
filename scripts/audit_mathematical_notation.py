#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mathematical Notation Audit

Extracts and analyzes all mathematical formulas from documentation
Checks for consistency in notation, symbols, and conventions

© 2025 Carmen Wrede & Lino Casu
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import re
from collections import defaultdict

# UTF-8 für Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Windows stdout UTF-8 fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Greek letters and mathematical symbols to track
GREEK_LETTERS = {
    'α': 'alpha',
    'β': 'beta', 
    'γ': 'gamma',
    'δ': 'delta',
    'ε': 'epsilon',
    'ζ': 'zeta',
    'η': 'eta',
    'θ': 'theta',
    'κ': 'kappa',
    'λ': 'lambda',
    'μ': 'mu',
    'ν': 'nu',
    'ξ': 'xi',
    'π': 'pi',
    'ρ': 'rho',
    'σ': 'sigma',
    'τ': 'tau',
    'φ': 'phi',
    'χ': 'chi',
    'ψ': 'psi',
    'ω': 'omega',
    'Γ': 'Gamma',
    'Δ': 'Delta',
    'Θ': 'Theta',
    'Λ': 'Lambda',
    'Ξ': 'Xi',
    'Π': 'Pi',
    'Σ': 'Sigma',
    'Φ': 'Phi',
    'Ψ': 'Psi',
    'Ω': 'Omega'
}

MATH_SYMBOLS = {
    '≈': 'approximately',
    '≠': 'not equal',
    '≤': 'less than or equal',
    '≥': 'greater than or equal',
    '±': 'plus minus',
    '×': 'times',
    '÷': 'divide',
    '∈': 'element of',
    '∞': 'infinity',
    '∂': 'partial',
    '∇': 'nabla',
    '∫': 'integral',
    '∑': 'sum',
    '∏': 'product',
    '√': 'square root',
    '→': 'arrow',
    '←': 'left arrow',
    '↔': 'double arrow',
    '⇒': 'implies',
    '⇔': 'iff'
}

SUBSCRIPTS = {'₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉'}
SUPERSCRIPTS = {'⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹'}

def extract_formulas(filepath):
    """Extract mathematical formulas from markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        formulas = []
        
        # Extract inline math: $...$
        inline = re.findall(r'\$([^\$]+)\$', content)
        for formula in inline:
            formulas.append(('inline', formula.strip()))
        
        # Extract display math: $$...$$
        display = re.findall(r'\$\$([^\$]+)\$\$', content, re.DOTALL)
        for formula in display:
            formulas.append(('display', formula.strip()))
        
        # Extract code blocks with math (```math or ```latex)
        math_blocks = re.findall(r'```(?:math|latex)\n(.*?)\n```', content, re.DOTALL)
        for block in math_blocks:
            formulas.append(('block', block.strip()))
        
        return formulas
    except Exception as e:
        return []

def analyze_symbols(text):
    """Analyze Greek letters and mathematical symbols in text"""
    symbols_found = defaultdict(list)
    
    # Find Greek letters
    for char, name in GREEK_LETTERS.items():
        if char in text:
            positions = [i for i, c in enumerate(text) if c == char]
            symbols_found[f'greek_{name}'] = positions
    
    # Find math symbols
    for char, name in MATH_SYMBOLS.items():
        if char in text:
            positions = [i for i, c in enumerate(text) if c == char]
            symbols_found[f'symbol_{name}'] = positions
    
    # Find subscripts
    for char in SUBSCRIPTS:
        if char in text:
            symbols_found['subscript'].append(text.index(char))
    
    # Find superscripts
    for char in SUPERSCRIPTS:
        if char in text:
            symbols_found['superscript'].append(text.index(char))
    
    return dict(symbols_found)

def check_notation_patterns(filepath, formulas):
    """Check for specific notation patterns and consistency"""
    issues = []
    stats = defaultdict(int)
    
    for formula_type, formula in formulas:
        # Check for φ (golden ratio)
        if 'φ' in formula or 'phi' in formula.lower():
            stats['phi_usage'] += 1
            # Check if properly introduced
            if 'golden ratio' not in formula.lower() and '(1+√5)/2' not in formula:
                context = formula[:50] if len(formula) > 50 else formula
                # Only flag if φ appears without context in first occurrence
                if stats['phi_usage'] == 1:
                    issues.append({
                        'type': 'phi_definition',
                        'severity': 'low',
                        'message': f'φ used without clear definition context',
                        'context': context
                    })
        
        # Check for π
        if 'π' in formula or 'pi' in formula.lower():
            stats['pi_usage'] += 1
        
        # Check for inconsistent tau notation
        if 'τ' in formula and 't' in formula:
            # Both τ (proper time) and t (coordinate time) present
            issues.append({
                'type': 'time_notation',
                'severity': 'medium',
                'message': 'Both τ and t present - ensure distinction is clear',
                'context': formula[:80]
            })
            stats['tau_t_mixed'] += 1
        
        # Check subscript/superscript style
        if '_' in formula:  # LaTeX-style subscript
            stats['latex_subscript'] += 1
        if any(c in formula for c in SUBSCRIPTS):  # Unicode subscript
            stats['unicode_subscript'] += 1
        
        if '^' in formula:  # LaTeX-style superscript
            stats['latex_superscript'] += 1
        if any(c in formula for c in SUPERSCRIPTS):  # Unicode superscript
            stats['unicode_superscript'] += 1
        
        # Check for undefined abbreviations
        abbreviations = re.findall(r'\b[A-Z]{2,}\b', formula)
        for abbr in abbreviations:
            if abbr not in ['SI', 'GR', 'PPN', 'SSZ', 'WEC', 'DEC', 'SEC', 'BH']:
                stats[f'abbr_{abbr}'] += 1
    
    # Check for inconsistent subscript/superscript usage
    if stats['latex_subscript'] > 0 and stats['unicode_subscript'] > 0:
        issues.append({
            'type': 'subscript_style',
            'severity': 'low',
            'message': f'Mixed subscript styles: LaTeX ({stats["latex_subscript"]}) and Unicode ({stats["unicode_subscript"]})',
            'file': str(filepath)
        })
    
    if stats['latex_superscript'] > 0 and stats['unicode_superscript'] > 0:
        issues.append({
            'type': 'superscript_style',
            'severity': 'low',
            'message': f'Mixed superscript styles: LaTeX ({stats["latex_superscript"]}) and Unicode ({stats["unicode_superscript"]})',
            'file': str(filepath)
        })
    
    return issues, stats

def main():
    """Main audit function"""
    print("="*80)
    print("MATHEMATICAL NOTATION AUDIT")
    print("="*80)
    print()
    
    # Find root
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Target files (focus on theory and core docs)
    target_files = [
        root / 'docs' / 'MATHEMATICAL_FORMULAS.md',
        root / 'docs' / 'MATHEMATICAL_FORMULAS_DE.md',
        root / 'docs' / 'PHYSICS_FOUNDATIONS.md',
        root / 'docs' / 'PHYSICS_FOUNDATIONS_DE.md',
        root / 'docs' / 'CODE_IMPLEMENTATION_GUIDE.md',
        root / 'docs' / 'CODE_IMPLEMENTATION_GUIDE_DE.md',
        root / 'docs' / 'EXAMPLES_AND_APPLICATIONS.md',
        root / 'docs' / 'EXAMPLES_AND_APPLICATIONS_DE.md',
    ]
    
    # Also scan theory papers
    theory_dir = root / 'docs' / 'theory'
    if theory_dir.exists():
        target_files.extend(theory_dir.glob('*.md'))
    
    all_formulas = []
    all_issues = []
    global_stats = defaultdict(int)
    file_stats = {}
    
    print("Scanning files...")
    for filepath in target_files:
        if not filepath.exists():
            continue
        
        print(f"  {filepath.name}...", end=' ')
        formulas = extract_formulas(filepath)
        
        if formulas:
            print(f"{len(formulas)} formulas found")
            all_formulas.extend([(filepath, f) for f in formulas])
            
            # Check notation
            issues, stats = check_notation_patterns(filepath, formulas)
            all_issues.extend(issues)
            file_stats[str(filepath)] = stats
            
            # Update global stats
            for key, val in stats.items():
                global_stats[key] += val
        else:
            print("no formulas")
    
    print()
    print(f"Total formulas extracted: {len(all_formulas)}")
    print(f"Total files scanned: {len([f for f in target_files if f.exists()])}")
    print()
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'MATHEMATICAL_NOTATION_CONSISTENCY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Mathematical Notation Consistency Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Scanned:** {len([fp for fp in target_files if fp.exists()])}\n")
        f.write(f"**Formulas Found:** {len(all_formulas)}\n")
        f.write(f"**Issues Found:** {len(all_issues)}\n\n")
        f.write("---\n\n")
        
        # Summary statistics
        f.write("## 📊 Symbol Usage Statistics\n\n")
        
        f.write("### Greek Letters\n\n")
        greek_stats = {k: v for k, v in global_stats.items() if k.startswith('greek_')}
        if greek_stats:
            f.write("| Symbol | Name | Occurrences |\n")
            f.write("|--------|------|-------------|\n")
            for key in sorted(greek_stats.keys(), key=lambda x: -global_stats[x]):
                name = key.replace('greek_', '')
                symbol = [k for k, v in GREEK_LETTERS.items() if v == name][0]
                f.write(f"| {symbol} | {name} | {global_stats[key]} |\n")
        else:
            f.write("No Greek letters detected in formulas.\n")
        f.write("\n")
        
        # Special focus on φ, π, τ
        f.write("### Key Constants\n\n")
        f.write(f"- **φ (golden ratio):** {global_stats['phi_usage']} occurrences\n")
        f.write(f"- **π (pi):** {global_stats['pi_usage']} occurrences\n")
        f.write(f"- **τ vs t (time):** {global_stats['tau_t_mixed']} mixed usages\n\n")
        
        # Notation style consistency
        f.write("### Notation Style\n\n")
        f.write("**Subscripts:**\n")
        f.write(f"- LaTeX style (`_`): {global_stats['latex_subscript']} occurrences\n")
        f.write(f"- Unicode style (₀₁₂): {global_stats['unicode_subscript']} occurrences\n\n")
        
        f.write("**Superscripts:**\n")
        f.write(f"- LaTeX style (`^`): {global_stats['latex_superscript']} occurrences\n")
        f.write(f"- Unicode style (⁰¹²): {global_stats['unicode_superscript']} occurrences\n\n")
        
        if global_stats['latex_subscript'] > 0 and global_stats['unicode_subscript'] > 0:
            f.write("⚠️ **Warning:** Mixed subscript notation styles detected. Consider standardizing.\n\n")
        
        if global_stats['latex_superscript'] > 0 and global_stats['unicode_superscript'] > 0:
            f.write("⚠️ **Warning:** Mixed superscript notation styles detected. Consider standardizing.\n\n")
        
        f.write("---\n\n")
        
        # Issues found
        f.write("## 🔍 Notation Issues\n\n")
        
        if all_issues:
            # Group by severity
            high = [i for i in all_issues if i['severity'] == 'high']
            medium = [i for i in all_issues if i['severity'] == 'medium']
            low = [i for i in all_issues if i['severity'] == 'low']
            
            if high:
                f.write("### 🔴 High Priority\n\n")
                for issue in high:
                    f.write(f"**{issue['type']}:** {issue['message']}\n")
                    if 'context' in issue:
                        f.write(f"```\n{issue['context']}\n```\n\n")
            
            if medium:
                f.write("### 🟡 Medium Priority\n\n")
                for issue in medium:
                    f.write(f"**{issue['type']}:** {issue['message']}\n")
                    if 'context' in issue:
                        f.write(f"```\n{issue['context']}\n```\n\n")
            
            if low:
                f.write("### 🟢 Low Priority\n\n")
                for issue in low:
                    f.write(f"**{issue['type']}:** {issue['message']}\n")
                    if 'file' in issue:
                        f.write(f"*File:* `{issue['file']}`\n\n")
        else:
            f.write("✅ No critical notation issues detected!\n\n")
        
        f.write("---\n\n")
        
        # Per-file breakdown
        f.write("## 📁 Per-File Analysis\n\n")
        
        for filepath, stats in file_stats.items():
            if stats:
                rel_path = Path(filepath).relative_to(root)
                f.write(f"### {rel_path}\n\n")
                
                # Show top symbols used
                top_symbols = sorted(stats.items(), key=lambda x: -x[1])[:10]
                if top_symbols:
                    f.write("| Symbol/Feature | Count |\n")
                    f.write("|----------------|-------|\n")
                    for key, count in top_symbols:
                        display_key = key.replace('greek_', 'Greek: ').replace('symbol_', 'Symbol: ')
                        f.write(f"| {display_key} | {count} |\n")
                f.write("\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### 1. Notation Standardization\n\n")
        if global_stats['latex_subscript'] > global_stats['unicode_subscript']:
            f.write("- **Subscripts:** Prefer LaTeX style (`_`) for consistency\n")
        elif global_stats['unicode_subscript'] > global_stats['latex_subscript']:
            f.write("- **Subscripts:** Prefer Unicode style (₀₁₂) for consistency\n")
        else:
            f.write("- **Subscripts:** Choose one style (LaTeX or Unicode) and apply consistently\n")
        
        if global_stats['latex_superscript'] > global_stats['unicode_superscript']:
            f.write("- **Superscripts:** Prefer LaTeX style (`^`) for consistency\n\n")
        elif global_stats['unicode_superscript'] > global_stats['latex_superscript']:
            f.write("- **Superscripts:** Prefer Unicode style (⁰¹²) for consistency\n\n")
        else:
            f.write("- **Superscripts:** Choose one style (LaTeX or Unicode) and apply consistently\n\n")
        
        f.write("### 2. Symbol Definitions\n\n")
        f.write("Ensure all Greek letters and special symbols are defined at first use:\n\n")
        if global_stats['phi_usage'] > 0:
            f.write("- φ (golden ratio) = (1 + √5)/2 ≈ 1.618...\n")
        if global_stats['tau_t_mixed'] > 0:
            f.write("- Clearly distinguish τ (proper time) from t (coordinate time)\n")
        f.write("\n")
        
        f.write("### 3. Next Steps\n\n")
        f.write("- Create comprehensive notation glossary\n")
        f.write("- Standardize subscript/superscript style across all docs\n")
        f.write("- Add \"Notation\" section to MATHEMATICAL_FORMULAS.md\n")
        f.write("- Ensure bilingual consistency (EN ↔ DE)\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/audit_mathematical_notation.py`\n")
        f.write("**Next:** Phase 1.3 - Terminology Consistency Check\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"✅ Report generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Formulas analyzed: {len(all_formulas)}")
    print(f"  Issues found: {len(all_issues)}")
    print(f"  φ (golden ratio): {global_stats['phi_usage']} uses")
    print(f"  π (pi): {global_stats['pi_usage']} uses")
    print()
    print("Next steps:")
    print("  1. Review MATHEMATICAL_NOTATION_CONSISTENCY_REPORT.md")
    print("  2. Address high-priority issues")
    print("  3. Start Phase 1.3: Terminology Consistency Check")

if __name__ == '__main__':
    main()
