#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminology Glossary Generator

Creates bilingual (EN/DE) terminology glossary
Checks consistency of technical terms across documentation

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

# Core terminology to track
CORE_TERMS = {
    'en': {
        'segmented spacetime': ['Segmented Spacetime', 'segmented spacetime', 'SSZ'],
        'segment': ['segment', 'Segment'],
        'golden ratio': ['golden ratio', 'φ', 'phi'],
        'natural boundary': ['natural boundary', 'Natural Boundary'],
        'proper time': ['proper time', 'τ', 'tau'],
        'coordinate time': ['coordinate time', 't'],
        'schwarzschild': ['Schwarzschild', 'schwarzschild'],
        'hawking': ['Hawking', 'hawking'],
        'event horizon': ['event horizon', 'Event Horizon'],
        'photon sphere': ['photon sphere', 'Photon Sphere'],
        'ppn': ['PPN', 'ppn', 'Post-Newtonian'],
    },
    'de': {
        'segmentierte raumzeit': ['Segmentierte Raumzeit', 'segmentierte Raumzeit', 'SSZ'],
        'segment': ['Segment', 'segment'],
        'goldener schnitt': ['Goldener Schnitt', 'goldener Schnitt', 'φ', 'phi'],
        'natürliche grenze': ['natürliche Grenze', 'Natürliche Grenze'],
        'eigenzeit': ['Eigenzeit', 'eigenzeit', 'τ', 'tau'],
        'koordinatenzeit': ['Koordinatenzeit', 'koordinatenzeit', 't'],
        'schwarzschild': ['Schwarzschild', 'schwarzschild'],
        'hawking': ['Hawking', 'hawking'],
        'ereignishorizont': ['Ereignishorizont', 'ereignishorizont'],
        'photonensphäre': ['Photonensphäre', 'photonensphäre'],
    }
}

# EN ↔ DE mapping
TRANSLATIONS = {
    'Segmented Spacetime': 'Segmentierte Raumzeit',
    'segment': 'Segment',
    'golden ratio': 'Goldener Schnitt',
    'natural boundary': 'natürliche Grenze',
    'proper time': 'Eigenzeit',
    'coordinate time': 'Koordinatenzeit',
    'event horizon': 'Ereignishorizont',
    'photon sphere': 'Photonensphäre',
}

def scan_terminology(filepath, lang='en'):
    """Scan file for terminology usage"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        findings = defaultdict(list)
        terms_dict = CORE_TERMS.get(lang, CORE_TERMS['en'])
        
        for concept, variants in terms_dict.items():
            for variant in variants:
                # Case-insensitive search
                pattern = re.compile(re.escape(variant), re.IGNORECASE)
                matches = pattern.findall(content)
                if matches:
                    # Track actual casing used
                    for match in matches:
                        findings[concept].append(match)
        
        return dict(findings)
    except Exception as e:
        return {}

def check_capitalization_consistency(findings):
    """Check if terms are capitalized consistently"""
    issues = []
    
    for concept, variants in findings.items():
        # Count unique casings
        unique_casings = set(variants)
        if len(unique_casings) > 2:  # Allow for some variation
            issues.append({
                'concept': concept,
                'issue': 'inconsistent_capitalization',
                'variants': list(unique_casings)[:5],  # Show max 5
                'count': len(variants)
            })
    
    return issues

def check_abbreviation_usage(content):
    """Check for undefined abbreviations"""
    # Find all-caps abbreviations
    abbrevs = re.findall(r'\b[A-Z]{2,}\b', content)
    
    # Known/OK abbreviations
    known = {
        'SSZ', 'GR', 'PPN', 'BH', 'NS', 'AGN', 'ISCO', 
        'WEC', 'DEC', 'SEC', 'SI', 'CMB', 'PDF', 'CSV',
        'EN', 'DE', 'UTF', 'URL', 'API', 'CLI', 'MD',
        'GAIA', 'NED', 'NASA', 'ESA'
    }
    
    unknown = []
    for abbr in abbrevs:
        if abbr not in known:
            unknown.append(abbr)
    
    return list(set(unknown))

def main():
    """Create terminology glossary"""
    print("="*80)
    print("TERMINOLOGY CONSISTENCY CHECK")
    print("="*80)
    print()
    
    # Find root
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Target files
    target_files = [
        root / 'docs' / 'PHYSICS_FOUNDATIONS.md',
        root / 'docs' / 'PHYSICS_FOUNDATIONS_DE.md',
        root / 'docs' / 'MATHEMATICAL_FORMULAS.md',
        root / 'docs' / 'MATHEMATICAL_FORMULAS_DE.md',
        root / 'docs' / 'CODE_IMPLEMENTATION_GUIDE.md',
        root / 'docs' / 'CODE_IMPLEMENTATION_GUIDE_DE.md',
        root / 'README.md',
    ]
    
    all_findings = {}
    all_issues = []
    unknown_abbrevs = defaultdict(set)
    
    print("Scanning files...")
    for filepath in target_files:
        if not filepath.exists():
            continue
        
        print(f"  {filepath.name}...", end=' ')
        
        # Detect language
        lang = 'de' if '_DE.md' in str(filepath) or 'Deutsch' in str(filepath) else 'en'
        
        # Scan terminology
        findings = scan_terminology(filepath, lang)
        
        if findings:
            print(f"{len(findings)} concepts found")
            all_findings[str(filepath)] = findings
            
            # Check capitalization
            issues = check_capitalization_consistency(findings)
            if issues:
                all_issues.extend([(str(filepath), issue) for issue in issues])
            
            # Check abbreviations
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            unknown = check_abbreviation_usage(content)
            if unknown:
                for abbr in unknown:
                    unknown_abbrevs[abbr].add(filepath.name)
        else:
            print("no terms found")
    
    print()
    print(f"Files scanned: {len([f for f in target_files if f.exists()])}")
    print(f"Capitalization issues: {len(all_issues)}")
    print(f"Unknown abbreviations: {len(unknown_abbrevs)}")
    print()
    
    # Generate glossary
    output_path = root / 'docs' / 'improvement' / 'TERMINOLOGY_GLOSSARY.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Terminology Glossary\n\n")
        f.write("**Bilingual (EN ↔ DE) Technical Terms**\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Analyzed:** {len([fp for fp in target_files if fp.exists()])}\n\n")
        f.write("---\n\n")
        
        # Core terminology table
        f.write("## 📖 Core Terminology (EN ↔ DE)\n\n")
        f.write("| English | German | Symbol | Usage |\n")
        f.write("|---------|--------|--------|-------|\n")
        
        for en_term, de_term in TRANSLATIONS.items():
            # Count usages
            en_count = sum(len(findings.get(en_term.lower(), [])) 
                          for findings in all_findings.values())
            f.write(f"| {en_term} | {de_term} | - | {en_count} occurrences |\n")
        
        f.write("\n### Special Symbols\n\n")
        f.write("| Symbol | English | German | Value |\n")
        f.write("|--------|---------|--------|-------|\n")
        f.write("| φ | golden ratio | Goldener Schnitt | ≈ 1.618 |\n")
        f.write("| τ | proper time | Eigenzeit | - |\n")
        f.write("| t | coordinate time | Koordinatenzeit | - |\n")
        f.write("| π | pi | Pi | ≈ 3.14159 |\n")
        f.write("| r_φ | segment radius | Segmentradius | φ·GM/c² |\n")
        f.write("| r_s | Schwarzschild radius | Schwarzschild-Radius | 2GM/c² |\n")
        f.write("\n---\n\n")
        
        # Capitalization issues
        f.write("## 🔍 Capitalization Consistency\n\n")
        
        if all_issues:
            for filepath, issue in all_issues:
                rel_path = Path(filepath).relative_to(root)
                f.write(f"### {rel_path}\n\n")
                f.write(f"**Concept:** `{issue['concept']}`\n\n")
                f.write(f"**Issue:** {issue['issue'].replace('_', ' ').title()}\n\n")
                f.write("**Variants found:**\n")
                for variant in issue['variants']:
                    f.write(f"- `{variant}`\n")
                f.write(f"\n**Total occurrences:** {issue['count']}\n\n")
                f.write("**Recommendation:** Standardize to one variant.\n\n")
        else:
            f.write("✅ No significant capitalization inconsistencies detected.\n\n")
        
        f.write("---\n\n")
        
        # Abbreviations
        f.write("## 🔤 Abbreviations\n\n")
        
        f.write("### Known Abbreviations\n\n")
        f.write("| Abbreviation | Full Term | Context |\n")
        f.write("|--------------|-----------|----------|\n")
        f.write("| SSZ | Segmented Spacetime | Theory name |\n")
        f.write("| GR | General Relativity | Comparison framework |\n")
        f.write("| PPN | Parametrized Post-Newtonian | Test framework |\n")
        f.write("| BH | Black Hole | Astrophysical object |\n")
        f.write("| ISCO | Innermost Stable Circular Orbit | Orbital mechanics |\n")
        f.write("| WEC/DEC/SEC | Weak/Dominant/Strong Energy Condition | Energy conditions |\n")
        f.write("| AGN | Active Galactic Nucleus | Data source |\n")
        f.write("| GAIA | GAIA mission | Data source |\n")
        f.write("| NED | NASA/IPAC Extragalactic Database | Data source |\n")
        f.write("\n")
        
        if unknown_abbrevs:
            f.write("### ⚠️ Potentially Undefined Abbreviations\n\n")
            f.write("These abbreviations appear in documentation but may need definition:\n\n")
            f.write("| Abbreviation | Files | Recommendation |\n")
            f.write("|--------------|-------|----------------|\n")
            for abbr, files in sorted(unknown_abbrevs.items()):
                file_list = ', '.join(list(files)[:3])
                if len(files) > 3:
                    file_list += f' (+{len(files)-3} more)'
                f.write(f"| {abbr} | {file_list} | Define at first use |\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # Usage statistics
        f.write("## 📊 Term Usage Statistics\n\n")
        
        # Aggregate all findings
        global_stats = defaultdict(int)
        for findings in all_findings.values():
            for concept, variants in findings.items():
                global_stats[concept] += len(variants)
        
        if global_stats:
            f.write("| Concept | Total Occurrences |\n")
            f.write("|---------|-------------------|\n")
            for concept in sorted(global_stats.keys(), key=lambda x: -global_stats[x]):
                f.write(f"| {concept} | {global_stats[concept]} |\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        f.write("### 1. Terminology Standardization\n\n")
        f.write("**Key decisions needed:**\n\n")
        f.write("- **'Segmented Spacetime' vs 'SSZ'**\n")
        f.write("  - Use full term in introductions\n")
        f.write("  - Use 'SSZ' in technical discussions after definition\n")
        f.write("  - Always capitalize 'Segmented Spacetime'\n\n")
        
        f.write("- **'segment' vs 'Segment'**\n")
        f.write("  - Lowercase when used as common noun\n")
        f.write("  - Capitalize when part of formal term\n")
        f.write("  - Example: 'each segment' vs 'Segment Radius'\n\n")
        
        f.write("### 2. Symbol Definitions\n\n")
        f.write("**Always define at first use:**\n\n")
        f.write("- φ (golden ratio) = (1 + √5)/2\n")
        f.write("- τ (proper time) vs t (coordinate time)\n")
        f.write("- r_φ (segment radius) vs r_s (Schwarzschild radius)\n\n")
        
        f.write("### 3. Bilingual Consistency\n\n")
        f.write("**Ensure EN ↔ DE translations match:**\n\n")
        f.write("- Review all bilingual doc pairs\n")
        f.write("- Use this glossary as reference\n")
        f.write("- Update translations where inconsistent\n\n")
        
        f.write("### 4. Next Steps\n\n")
        f.write("- [ ] Review and approve terminology choices\n")
        f.write("- [ ] Apply capitalization standards\n")
        f.write("- [ ] Define all abbreviations at first use\n")
        f.write("- [ ] Update DOCUMENTATION_INDEX with this glossary\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/create_terminology_glossary.py`\n")
        f.write("**Next:** Phase 1.4 - Cross-Reference Audit\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"✅ Glossary generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Core terms tracked: {len(TRANSLATIONS)}")
    print(f"  Files analyzed: {len(all_findings)}")
    print(f"  Capitalization issues: {len(all_issues)}")
    print(f"  Unknown abbreviations: {len(unknown_abbrevs)}")
    print()
    print("Next steps:")
    print("  1. Review TERMINOLOGY_GLOSSARY.md")
    print("  2. Decide on capitalization standards")
    print("  3. Start Phase 1.4: Cross-Reference Audit")

if __name__ == '__main__':
    main()
