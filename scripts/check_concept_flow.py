#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concept Flow Checker

Analyzes logical flow and dependencies in documentation

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

# Key concepts and their typical indicators
KEY_CONCEPTS = {
    'golden_ratio': ['golden ratio', 'φ', 'phi'],
    'schwarzschild': ['schwarzschild radius', 'r_s', 'event horizon'],
    'phi_radius': ['φ-radius', 'r_φ', 'r_phi', 'characteristic radius'],
    'segments': ['segment', 'segmented spacetime', 'spacetime segments'],
    'natural_boundary': ['natural boundary', 'singularity resolution'],
    'dual_velocity': ['dual velocity', 'v_esc', 'v_fall', 'velocity duality'],
    'ppn': ['ppn', 'post-newtonian', 'β', 'γ', 'beta', 'gamma'],
    'metric': ['metric', 'g_μν', 'line element', 'spacetime metric'],
    'time_dilation': ['time dilation', 'τ', 'proper time'],
    'mass_projection': ['mass projection', 'γ', 'projection coefficient']
}

def extract_concepts(text):
    """Extract concepts mentioned in text"""
    text_lower = text.lower()
    found_concepts = []
    
    for concept, indicators in KEY_CONCEPTS.items():
        for indicator in indicators:
            if indicator.lower() in text_lower:
                found_concepts.append(concept)
                break
    
    return list(set(found_concepts))

def find_first_mention(text, concept):
    """Find approximate position of first mention (paragraph number)"""
    indicators = KEY_CONCEPTS.get(concept, [])
    paragraphs = text.split('\n\n')
    
    for i, para in enumerate(paragraphs):
        para_lower = para.lower()
        for indicator in indicators:
            if indicator.lower() in para_lower:
                return i
    
    return -1

def check_prerequisites(text):
    """Check if prerequisites are mentioned"""
    prereq_indicators = [
        'prerequisite', 'requires', 'assumes', 'builds on',
        'see first', 'before reading', 'background'
    ]
    
    text_lower = text.lower()
    found = []
    
    for indicator in prereq_indicators:
        if indicator in text_lower:
            found.append(indicator)
    
    return found

def analyze_document_flow(filepath):
    """Analyze concept flow in a document"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Extract concepts
        concepts = extract_concepts(content)
        
        # Find first mentions
        concept_order = {}
        for concept in concepts:
            pos = find_first_mention(content, concept)
            if pos >= 0:
                concept_order[concept] = pos
        
        # Sort by appearance
        sorted_concepts = sorted(concept_order.items(), key=lambda x: x[1])
        
        # Check for prerequisites
        prereqs = check_prerequisites(content)
        
        # Count sections
        sections = len(re.findall(r'^#+\s', content, re.MULTILINE))
        
        # Check for examples
        examples = len(re.findall(r'example|e\.g\.|for instance', content, re.IGNORECASE))
        
        return {
            'concepts': concepts,
            'concept_count': len(concepts),
            'concept_order': sorted_concepts,
            'has_prerequisites': len(prereqs) > 0,
            'prerequisite_mentions': prereqs,
            'section_count': sections,
            'example_count': examples
        }
    except Exception as e:
        return None

def main():
    """Check concept flow in key documents"""
    print("="*80)
    print("CONCEPT FLOW CHECKER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    
    # Key documents
    key_docs = [
        'README.md',
        'docs/PHYSICS_FOUNDATIONS.md',
        'docs/MATHEMATICAL_FORMULAS.md',
        'docs/CODE_IMPLEMENTATION_GUIDE.md'
    ]
    
    results = {}
    
    print("Analyzing concept flow...")
    print()
    
    for doc_path in key_docs:
        full_path = root / doc_path
        if full_path.exists():
            print(f"Analyzing {doc_path}...", end=' ')
            analysis = analyze_document_flow(full_path)
            if analysis:
                results[doc_path] = analysis
                print(f"✅ {analysis['concept_count']} concepts")
            else:
                print("⚠️  Error")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'CONCEPT_FLOW_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Concept Flow Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Analyzed:** {len(results)}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        
        total_concepts = sum(r['concept_count'] for r in results.values())
        docs_with_prereqs = sum(1 for r in results.values() if r['has_prerequisites'])
        
        f.write(f"- **Total Concepts Found:** {total_concepts}\n")
        f.write(f"- **Documents with Prerequisites:** {docs_with_prereqs}/{len(results)}\n\n")
        
        f.write("---\n\n")
        
        # Per-document analysis
        f.write("## 📋 Document-by-Document Analysis\n\n")
        
        for doc_path, data in results.items():
            f.write(f"### {doc_path}\n\n")
            
            f.write(f"**Concepts Found:** {data['concept_count']}\n\n")
            
            if data['concept_order']:
                f.write("**Concept Introduction Order:**\n")
                for i, (concept, para) in enumerate(data['concept_order'][:10], 1):
                    f.write(f"{i}. {concept.replace('_', ' ').title()} (paragraph {para})\n")
                f.write("\n")
            
            # Prerequisites
            if data['has_prerequisites']:
                f.write(f"✅ **Prerequisites mentioned:** {', '.join(data['prerequisite_mentions'])}\n\n")
            else:
                f.write("⚠️  **No explicit prerequisites mentioned**\n\n")
            
            # Structure
            f.write(f"**Document Structure:**\n")
            f.write(f"- Sections: {data['section_count']}\n")
            f.write(f"- Examples: {data['example_count']}\n\n")
            
            # Recommendations
            f.write("**Flow Recommendations:**\n")
            
            if not data['has_prerequisites'] and data['concept_count'] > 3:
                f.write("- ⚠️  Consider adding prerequisite section for complex topics\n")
            
            if data['example_count'] < data['concept_count']:
                f.write("- ℹ️  Consider adding more examples (concepts: {}, examples: {})\n".format(
                    data['concept_count'], data['example_count']))
            
            if data['concept_count'] > 5:
                f.write("- ✅ Good concept coverage\n")
            
            f.write("\n---\n\n")
        
        # Concept dependency suggestions
        f.write("## 🔗 Suggested Concept Dependencies\n\n")
        f.write("**Recommended Reading Order:**\n\n")
        f.write("1. **Foundational Concepts** (understand first)\n")
        f.write("   - Golden Ratio φ\n")
        f.write("   - Schwarzschild radius\n")
        f.write("   - Spacetime segments\n\n")
        
        f.write("2. **Core SSZ Theory** (build on foundation)\n")
        f.write("   - φ-radius r_φ\n")
        f.write("   - Natural boundary\n")
        f.write("   - Segment density\n\n")
        
        f.write("3. **Advanced Concepts** (require foundation + core)\n")
        f.write("   - Dual velocity invariant\n")
        f.write("   - PPN parameters\n")
        f.write("   - Time dilation\n")
        f.write("   - Mass projection\n\n")
        
        f.write("4. **Mathematical Formalism** (requires all above)\n")
        f.write("   - Metric tensor\n")
        f.write("   - Energy conditions\n")
        f.write("   - Field equations\n\n")
        
        f.write("---\n\n")
        
        # Best practices
        f.write("## 📐 Best Practices for Concept Flow\n\n")
        f.write("### Do:\n")
        f.write("- ✅ Introduce simple concepts before complex ones\n")
        f.write("- ✅ State prerequisites explicitly\n")
        f.write("- ✅ Provide examples for each concept\n")
        f.write("- ✅ Link to detailed explanations\n")
        f.write("- ✅ Build progressively (simple → complex)\n\n")
        
        f.write("### Avoid:\n")
        f.write("- ❌ Using terms before defining them\n")
        f.write("- ❌ Circular dependencies\n")
        f.write("- ❌ Too many concepts at once\n")
        f.write("- ❌ Missing examples for complex ideas\n")
        f.write("- ❌ Jumping difficulty levels\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/check_concept_flow.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    print(f"Total concepts tracked: {total_concepts}")
    print(f"Documents with prerequisites: {docs_with_prereqs}/{len(results)}")

if __name__ == '__main__':
    main()
