#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Markdown Conversion Quality Checker

Analyzes .pdf.md files for conversion issues and quality problems

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

class PDFMarkdownQualityChecker:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.issues = []
        self.warnings = []
        self.stats = {}
        
    def check_all(self):
        """Run all quality checks"""
        self.check_file_size()
        self.check_basic_structure()
        self.check_malformed_links()
        self.check_spacing_issues()
        self.check_encoding_issues()
        self.check_table_conversion()
        self.check_formula_markers()
        
        return {
            'filepath': str(self.filepath),
            'issues': self.issues,
            'warnings': self.warnings,
            'stats': self.stats
        }
    
    def check_file_size(self):
        """Check if file exists and has reasonable size"""
        if not self.filepath.exists():
            self.issues.append({
                'type': 'missing_file',
                'severity': 'critical',
                'message': 'File does not exist'
            })
            return
        
        size_bytes = self.filepath.stat().st_size
        size_kb = size_bytes / 1024
        
        self.stats['size_kb'] = round(size_kb, 2)
        
        if size_kb < 1:
            self.warnings.append({
                'type': 'very_small',
                'message': f'File is very small ({size_kb:.2f} KB) - may be incomplete'
            })
        elif size_kb > 10000:  # >10 MB
            self.warnings.append({
                'type': 'very_large',
                'message': f'File is very large ({size_kb:.2f} KB) - may need optimization'
            })
    
    def check_basic_structure(self):
        """Check basic markdown structure"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            lines = content.split('\n')
            self.stats['total_lines'] = len(lines)
            self.stats['total_chars'] = len(content)
            
            # Check for headings
            headings = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
            self.stats['headings'] = len(headings)
            
            if len(headings) < 3:
                self.warnings.append({
                    'type': 'few_headings',
                    'message': f'Only {len(headings)} headings found - structure may be poor'
                })
            
            # Check for code blocks
            code_blocks = re.findall(r'```[\s\S]*?```', content)
            self.stats['code_blocks'] = len(code_blocks)
            
            # Check for empty lines ratio
            empty_lines = sum(1 for line in lines if not line.strip())
            self.stats['empty_lines'] = empty_lines
            
        except Exception as e:
            self.issues.append({
                'type': 'read_error',
                'severity': 'critical',
                'message': f'Cannot read file: {e}'
            })
    
    def check_malformed_links(self):
        """Check for malformed markdown links"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Find malformed links like [text]( broken\ntext)
            malformed_patterns = [
                r'\[([^\]]+)\]\(\s*\n',  # Link broken by newline
                r'\[([^\]]+)\]\(\s+o\s+r',  # Specific issue we found
                r'\]\([^\)]{1,5}\n',  # Very short link broken by newline
            ]
            
            malformed_count = 0
            for pattern in malformed_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    malformed_count += len(matches)
                    self.issues.append({
                        'type': 'malformed_link',
                        'severity': 'high',
                        'message': f'Found {len(matches)} malformed links matching pattern',
                        'pattern': pattern,
                        'examples': matches[:3]
                    })
            
            self.stats['malformed_links'] = malformed_count
            
        except Exception as e:
            pass
    
    def check_spacing_issues(self):
        """Check for spacing/formatting issues"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            issues_found = []
            
            # Check for excessive spaces
            if 'µma n d[' in content or 'µmi s' in content:
                issues_found.append('Broken word spacing (µma n d)')
            
            # Check for missing spaces after periods
            broken_sentences = len(re.findall(r'\.\w{2,}', content))
            if broken_sentences > 10:
                issues_found.append(f'{broken_sentences} potential broken sentences')
            
            # Check for excessive whitespace
            excessive_spaces = len(re.findall(r'  {3,}', content))
            if excessive_spaces > 20:
                issues_found.append(f'{excessive_spaces} instances of excessive spacing')
            
            if issues_found:
                self.warnings.append({
                    'type': 'spacing_issues',
                    'message': ', '.join(issues_found)
                })
            
            self.stats['spacing_issues'] = len(issues_found)
            
        except Exception as e:
            pass
    
    def check_encoding_issues(self):
        """Check for encoding/unicode issues"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Check for replacement characters
            replacement_chars = content.count('\ufffd')
            if replacement_chars > 0:
                self.issues.append({
                    'type': 'encoding_issue',
                    'severity': 'medium',
                    'message': f'{replacement_chars} replacement characters (�) found'
                })
            
            # Check for common encoding artifacts
            artifacts = []
            if 'Ã©' in content:
                artifacts.append('é encoding issue')
            if 'Ã¤' in content:
                artifacts.append('ä encoding issue')
            if 'â€"' in content:
                artifacts.append('em-dash encoding issue')
            
            if artifacts:
                self.warnings.append({
                    'type': 'encoding_artifacts',
                    'message': ', '.join(artifacts)
                })
            
            self.stats['encoding_issues'] = len(artifacts)
            
        except Exception as e:
            pass
    
    def check_table_conversion(self):
        """Check table conversion quality"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Find markdown tables
            table_headers = re.findall(r'\|[^\n]+\|\n\|[-:\s|]+\|', content)
            self.stats['markdown_tables'] = len(table_headers)
            
            # Look for unconverted tables (common in PDF conversions)
            potential_tables = re.findall(r'^\w+\s+\w+\s+\w+\s+\w+$', content, re.MULTILINE)
            if len(potential_tables) > 20:
                self.warnings.append({
                    'type': 'unconverted_tables',
                    'message': f'{len(potential_tables)} potential unconverted table rows'
                })
            
        except Exception as e:
            pass
    
    def check_formula_markers(self):
        """Check for mathematical formulas"""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Count LaTeX math
            inline_math = len(re.findall(r'\$[^\$]+\$', content))
            display_math = len(re.findall(r'\$\$[^\$]+\$\$', content, re.DOTALL))
            
            # Count Greek letters (indicator of formulas)
            greek_letters = len(re.findall(r'[αβγδεζηθκλμνξπρστφχψω]', content))
            
            self.stats['inline_math'] = inline_math
            self.stats['display_math'] = display_math
            self.stats['greek_letters'] = greek_letters
            
            # Check if formulas might be unconverted
            if greek_letters > 50 and inline_math + display_math < 5:
                self.warnings.append({
                    'type': 'unconverted_formulas',
                    'message': f'{greek_letters} Greek letters but only {inline_math + display_math} LaTeX formulas'
                })
            
        except Exception as e:
            pass

def main():
    """Check all PDF.md files"""
    print("="*80)
    print("PDF-TO-MARKDOWN QUALITY CHECKER")
    print("="*80)
    print()
    
    # Find root
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Find all .pdf.md files
    pdf_md_files = []
    for pattern in ['papers/**/*.pdf.md', '*.pdf.md', 'docs/**/*.pdf.md']:
        pdf_md_files.extend(root.glob(pattern))
    
    # Remove duplicates
    pdf_md_files = list(set(pdf_md_files))
    
    print(f"Found {len(pdf_md_files)} PDF.md files")
    print()
    
    # Check each file
    results = []
    for filepath in sorted(pdf_md_files):
        rel_path = filepath.relative_to(root)
        print(f"Checking: {rel_path}...", end=' ')
        
        checker = PDFMarkdownQualityChecker(filepath)
        result = checker.check_all()
        results.append(result)
        
        issue_count = len(result['issues'])
        warning_count = len(result['warnings'])
        
        if issue_count > 0:
            print(f"❌ {issue_count} issues, {warning_count} warnings")
        elif warning_count > 0:
            print(f"⚠️  {warning_count} warnings")
        else:
            print("✅ OK")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'PDF_CONVERSION_QUALITY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# PDF to Markdown Conversion Quality Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Checked:** {len(results)}\n\n")
        f.write("---\n\n")
        
        # Summary
        total_issues = sum(len(r['issues']) for r in results)
        total_warnings = sum(len(r['warnings']) for r in results)
        
        f.write("## 📊 Summary\n\n")
        f.write(f"- **Total Files:** {len(results)}\n")
        f.write(f"- **Critical Issues:** {total_issues}\n")
        f.write(f"- **Warnings:** {total_warnings}\n")
        f.write(f"- **Clean Files:** {len([r for r in results if not r['issues'] and not r['warnings']])}\n\n")
        
        if total_issues == 0 and total_warnings == 0:
            f.write("✅ **All PDF conversions are clean!**\n\n")
        elif total_issues > 0:
            f.write("❌ **Issues found requiring attention**\n\n")
        else:
            f.write("⚠️  **Some warnings found (non-critical)**\n\n")
        
        f.write("---\n\n")
        
        # Files with issues
        problematic = [r for r in results if r['issues']]
        if problematic:
            f.write("## ❌ Files with Issues\n\n")
            for result in problematic:
                rel_path = Path(result['filepath']).relative_to(root)
                f.write(f"### {rel_path}\n\n")
                f.write(f"**Size:** {result['stats'].get('size_kb', 0):.2f} KB\n")
                f.write(f"**Lines:** {result['stats'].get('total_lines', 0):,}\n\n")
                
                for issue in result['issues']:
                    severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                    emoji = severity_emoji.get(issue['severity'], '⚠️')
                    f.write(f"{emoji} **{issue['type'].replace('_', ' ').title()}** ({issue['severity']})\n")
                    f.write(f"   - {issue['message']}\n\n")
            
            f.write("---\n\n")
        
        # Files with warnings
        warned = [r for r in results if r['warnings'] and not r['issues']]
        if warned:
            f.write("## ⚠️  Files with Warnings\n\n")
            for result in warned:
                rel_path = Path(result['filepath']).relative_to(root)
                f.write(f"### {rel_path}\n\n")
                for warning in result['warnings']:
                    f.write(f"- **{warning['type'].replace('_', ' ').title()}:** {warning['message']}\n")
                f.write("\n")
            
            f.write("---\n\n")
        
        # Statistics table
        f.write("## 📈 Conversion Statistics\n\n")
        f.write("| File | Size (KB) | Lines | Headings | Links Issues | Encoding |\n")
        f.write("|------|-----------|-------|----------|--------------|----------|\n")
        
        for result in sorted(results, key=lambda x: -x['stats'].get('size_kb', 0)):
            rel_path = Path(result['filepath']).relative_to(root).name
            size = result['stats'].get('size_kb', 0)
            lines = result['stats'].get('total_lines', 0)
            headings = result['stats'].get('headings', 0)
            link_issues = result['stats'].get('malformed_links', 0)
            encoding = result['stats'].get('encoding_issues', 0)
            
            f.write(f"| {rel_path[:40]} | {size:.1f} | {lines:,} | {headings} | {link_issues} | {encoding} |\n")
        
        f.write("\n---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        if total_issues > 0:
            f.write("### Immediate Actions Required\n\n")
            f.write("1. **Fix malformed links** in problematic files\n")
            f.write("2. **Verify encoding** for files with replacement characters\n")
            f.write("3. **Review spacing issues** in affected documents\n\n")
        
        f.write("### PDF Conversion Tool Recommendations\n\n")
        f.write("Based on issues found, consider:\n\n")
        
        if any('malformed_link' in str(r['issues']) for r in results):
            f.write("- **Link preservation:** Current tool may break links across newlines\n")
        if any('spacing' in str(r['warnings']) for r in results):
            f.write("- **Spacing normalization:** Add post-processing for word spacing\n")
        if any('encoding' in str(r['issues']) for r in results):
            f.write("- **Encoding handling:** Improve UTF-8 character handling\n")
        if any('unconverted_tables' in str(r['warnings']) for r in results):
            f.write("- **Table detection:** Improve table structure recognition\n")
        if any('unconverted_formulas' in str(r['warnings']) for r in results):
            f.write("- **Formula conversion:** Better LaTeX math detection\n")
        
        f.write("\n")
        f.write("### Tool Options\n\n")
        f.write("Consider building or using:\n")
        f.write("1. **pdf2md with post-processing** (pdfminer + custom cleanup)\n")
        f.write("2. **marker** (https://github.com/VikParuchuri/marker) - ML-based PDF to Markdown\n")
        f.write("3. **pandoc** (universal document converter)\n")
        f.write("4. **Custom Python script** with pdfplumber + regex cleanup\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_pdf_md_quality.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print("Summary:")
    print(f"  Total files: {len(results)}")
    print(f"  Issues: {total_issues}")
    print(f"  Warnings: {total_warnings}")
    print(f"  Clean: {len([r for r in results if not r['issues'] and not r['warnings']])}")
    
    if total_issues > 0:
        print("\n⚠️  Action required: Review PDF_CONVERSION_QUALITY_REPORT.md")
    elif total_warnings > 0:
        print("\n✅ No critical issues, some minor warnings")
    else:
        print("\n✅ All PDF conversions are clean!")

if __name__ == '__main__':
    main()
