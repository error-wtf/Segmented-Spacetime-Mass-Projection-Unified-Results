#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Quality Checker

Verifies example coverage and quality in documentation

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

def count_formulas(text):
    """Count mathematical formulas in text"""
    # Look for common formula patterns
    formulas = re.findall(r'\$.*?\$|```math[\s\S]*?```|[=].*?[A-Za-z].*?[+\-*/]', text)
    return len(formulas)

def count_code_blocks(text):
    """Count code examples"""
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    return len(code_blocks), code_blocks

def find_examples(text):
    """Find example sections"""
    example_patterns = [
        r'example:',
        r'for example',
        r'e\.g\.',
        r'### example',
        r'## example',
        r'\*\*example\*\*'
    ]
    
    examples = []
    for pattern in example_patterns:
        examples.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return len(examples)

def check_step_by_step(text):
    """Check for step-by-step explanations"""
    steps = re.findall(r'step \d+|^\d+\.|first,|second,|finally', text, re.IGNORECASE | re.MULTILINE)
    return len(steps)

def analyze_examples(filepath):
    """Analyze example quality in a document"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        formula_count = count_formulas(content)
        code_count, code_blocks = count_code_blocks(content)
        example_count = find_examples(content)
        step_count = check_step_by_step(content)
        
        # Check if code examples are complete
        complete_examples = 0
        for block in code_blocks:
            # Check for imports, main logic, output
            if 'import' in block.lower() or 'def ' in block.lower():
                complete_examples += 1
        
        return {
            'formula_count': formula_count,
            'code_block_count': code_count,
            'example_count': example_count,
            'step_by_step_count': step_count,
            'complete_code_examples': complete_examples,
            'example_to_formula_ratio': example_count / max(formula_count, 1)
        }
    except Exception as e:
        return None

def main():
    """Check example quality in documentation"""
    print("="*80)
    print("EXAMPLE QUALITY CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    
    key_docs = [
        'README.md',
        'docs/PHYSICS_FOUNDATIONS.md',
        'docs/MATHEMATICAL_FORMULAS.md',
        'docs/CODE_IMPLEMENTATION_GUIDE.md',
        'CONTRIBUTING.md',
        'TROUBLESHOOTING.md'
    ]
    
    results = {}
    
    print("Analyzing examples...")
    print()
    
    for doc_path in key_docs:
        full_path = root / doc_path
        if full_path.exists():
            print(f"Checking {doc_path}...", end=' ')
            analysis = analyze_examples(full_path)
            if analysis:
                results[doc_path] = analysis
                print(f"✅ {analysis['example_count']} examples")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'EXAMPLE_QUALITY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Example Quality Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Analyzed:** {len(results)}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        
        total_formulas = sum(r['formula_count'] for r in results.values())
        total_examples = sum(r['example_count'] for r in results.values())
        total_code = sum(r['code_block_count'] for r in results.values())
        
        f.write(f"- **Total Formulas:** {total_formulas}\n")
        f.write(f"- **Total Examples:** {total_examples}\n")
        f.write(f"- **Total Code Blocks:** {total_code}\n")
        f.write(f"- **Example/Formula Ratio:** {total_examples/max(total_formulas,1):.2f}\n\n")
        
        if total_examples / max(total_formulas, 1) >= 0.5:
            f.write("✅ **Good example coverage**\n\n")
        else:
            f.write("⚠️  **Could use more examples**\n\n")
        
        f.write("---\n\n")
        
        # Per-document analysis
        f.write("## 📋 Document Analysis\n\n")
        
        for doc_path, data in sorted(results.items()):
            f.write(f"### {doc_path}\n\n")
            
            ratio = data['example_to_formula_ratio']
            if ratio >= 0.5:
                status = '✅'
            elif ratio >= 0.25:
                status = '⚠️'
            else:
                status = '🔴'
            
            f.write(f"{status} **Example Coverage**\n\n")
            
            f.write("**Metrics:**\n")
            f.write(f"- Formulas: {data['formula_count']}\n")
            f.write(f"- Examples: {data['example_count']}\n")
            f.write(f"- Code blocks: {data['code_block_count']}\n")
            f.write(f"- Complete code examples: {data['complete_code_examples']}\n")
            f.write(f"- Step-by-step guides: {data['step_by_step_count']}\n")
            f.write(f"- Example/Formula ratio: {ratio:.2f}\n\n")
            
            # Recommendations
            f.write("**Recommendations:**\n")
            
            if ratio < 0.3 and data['formula_count'] > 5:
                f.write("- 🔴 Add more examples for formulas\n")
            
            if data['code_block_count'] > 0 and data['complete_code_examples'] == 0:
                f.write("- ⚠️  Make code examples more complete (add imports, context)\n")
            
            if data['step_by_step_count'] == 0 and data['formula_count'] > 3:
                f.write("- ℹ️  Consider adding step-by-step walkthroughs\n")
            
            if ratio >= 0.5:
                f.write("- ✅ Good example coverage\n")
            
            f.write("\n---\n\n")
        
        # Guidelines
        f.write("## 📐 Example Best Practices\n\n")
        f.write("### Good Example Should:\n")
        f.write("- ✅ Be concrete and specific\n")
        f.write("- ✅ Show realistic use case\n")
        f.write("- ✅ Include actual numbers\n")
        f.write("- ✅ Explain each step\n")
        f.write("- ✅ Show expected output\n\n")
        
        f.write("### Code Example Should:\n")
        f.write("- ✅ Be runnable (include imports)\n")
        f.write("- ✅ Show complete context\n")
        f.write("- ✅ Include comments\n")
        f.write("- ✅ Demonstrate best practices\n")
        f.write("- ✅ Handle edge cases\n\n")
        
        f.write("### Target Ratios:\n")
        f.write("- **Excellent:** Example/Formula ≥ 1.0\n")
        f.write("- **Good:** Example/Formula ≥ 0.5\n")
        f.write("- **Acceptable:** Example/Formula ≥ 0.25\n")
        f.write("- **Needs Work:** Example/Formula < 0.25\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_examples.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print(f"Total examples: {total_examples}")
    print(f"Example/Formula ratio: {total_examples/max(total_formulas,1):.2f}")

if __name__ == '__main__':
    main()
