#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Readability Analyzer

Analyzes text readability using multiple metrics

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

def count_syllables(word):
    """Estimate syllable count (simple heuristic)"""
    word = word.lower()
    vowels = 'aeiou'
    syllables = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllables += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent e
    if word.endswith('e'):
        syllables -= 1
    
    # At least one syllable
    return max(1, syllables)

def flesch_reading_ease(text):
    """Calculate Flesch Reading Ease score"""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0, 0, 0
    
    # Count words
    words = []
    for sentence in sentences:
        words.extend(re.findall(r'\b[a-zA-Z]+\b', sentence))
    
    if not words:
        return 0, 0, 0
    
    # Count syllables
    total_syllables = sum(count_syllables(word) for word in words)
    
    # Calculate metrics
    word_count = len(words)
    sentence_count = len(sentences)
    
    avg_sentence_length = word_count / sentence_count
    avg_syllables_per_word = total_syllables / word_count
    
    # Flesch Reading Ease = 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
    score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    
    return score, avg_sentence_length, avg_syllables_per_word

def flesch_kincaid_grade(text):
    """Calculate Flesch-Kincaid Grade Level"""
    text = re.sub(r'```[\s\S]*?```', '', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0
    
    words = []
    for sentence in sentences:
        words.extend(re.findall(r'\b[a-zA-Z]+\b', sentence))
    
    if not words:
        return 0
    
    total_syllables = sum(count_syllables(word) for word in words)
    word_count = len(words)
    sentence_count = len(sentences)
    
    # FK Grade = 0.39(words/sentences) + 11.8(syllables/words) - 15.59
    grade = 0.39 * (word_count/sentence_count) + 11.8 * (total_syllables/word_count) - 15.59
    
    return max(0, grade)

def analyze_paragraphs(text):
    """Analyze paragraph structure"""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Split by double newline
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        return 0, 0, 0
    
    lengths = []
    for para in paragraphs:
        words = re.findall(r'\b[a-zA-Z]+\b', para)
        lengths.append(len(words))
    
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    max_length = max(lengths) if lengths else 0
    
    return len(paragraphs), avg_length, max_length

def count_technical_terms(text):
    """Count technical/jargon terms"""
    technical_terms = [
        'schwarzschild', 'metric', 'tensor', 'hamiltonian',
        'lagrangian', 'geodesic', 'curvature', 'riemann',
        'christoffel', 'covariant', 'contravariant', 'manifold',
        'topology', 'diffeomorphism', 'isometry', 'killing',
        'weyl', 'ricci', 'einstein', 'minkowski', 'lorentz',
        'poincare', 'symplectic', 'canonical', 'variational'
    ]
    
    text_lower = text.lower()
    count = sum(text_lower.count(term) for term in technical_terms)
    
    # Count as percentage of total words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    if words:
        return count, (count / len(words)) * 100
    return 0, 0

def analyze_file(filepath):
    """Analyze readability of a markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Calculate metrics
        flesch_score, avg_sent_len, avg_syll = flesch_reading_ease(content)
        fk_grade = flesch_kincaid_grade(content)
        para_count, avg_para, max_para = analyze_paragraphs(content)
        tech_count, tech_pct = count_technical_terms(content)
        
        # Interpret Flesch score
        if flesch_score >= 90:
            difficulty = 'Very Easy (5th grade)'
        elif flesch_score >= 80:
            difficulty = 'Easy (6th grade)'
        elif flesch_score >= 70:
            difficulty = 'Fairly Easy (7th grade)'
        elif flesch_score >= 60:
            difficulty = 'Standard (8-9th grade)'
        elif flesch_score >= 50:
            difficulty = 'Fairly Difficult (10-12th grade)'
        elif flesch_score >= 30:
            difficulty = 'Difficult (College)'
        else:
            difficulty = 'Very Difficult (College graduate)'
        
        return {
            'flesch_score': flesch_score,
            'difficulty': difficulty,
            'fk_grade': fk_grade,
            'avg_sentence_length': avg_sent_len,
            'avg_syllables_per_word': avg_syll,
            'paragraph_count': para_count,
            'avg_paragraph_length': avg_para,
            'max_paragraph_length': max_para,
            'technical_terms': tech_count,
            'technical_percentage': tech_pct,
            'size_kb': filepath.stat().st_size / 1024
        }
    except Exception as e:
        return None

def main():
    """Analyze readability of key documentation"""
    print("="*80)
    print("READABILITY ANALYZER")
    print("="*80)
    print()
    
    root = Path(__file__).parent.parent
    
    # Key documents to analyze
    key_docs = [
        'README.md',
        'docs/PHYSICS_FOUNDATIONS.md',
        'docs/MATHEMATICAL_FORMULAS.md',
        'docs/CODE_IMPLEMENTATION_GUIDE.md',
        'CONTRIBUTING.md',
        'TROUBLESHOOTING.md'
    ]
    
    results = {}
    
    print("Analyzing key documentation files...")
    print()
    
    for doc_path in key_docs:
        full_path = root / doc_path
        if full_path.exists():
            print(f"Analyzing {doc_path}...", end=' ')
            analysis = analyze_file(full_path)
            if analysis:
                results[doc_path] = analysis
                print(f"✅ Flesch: {analysis['flesch_score']:.1f}")
            else:
                print("⚠️  Error")
        else:
            print(f"⚠️  {doc_path} not found")
    
    print()
    print("="*80)
    print("GENERATING REPORT...")
    print("="*80)
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'READABILITY_REPORT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Readability Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Analyzed:** {len(results)}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        
        if results:
            avg_flesch = sum(r['flesch_score'] for r in results.values()) / len(results)
            avg_fk = sum(r['fk_grade'] for r in results.values()) / len(results)
            avg_sent = sum(r['avg_sentence_length'] for r in results.values()) / len(results)
            avg_tech = sum(r['technical_percentage'] for r in results.values()) / len(results)
            
            f.write(f"- **Average Flesch Score:** {avg_flesch:.1f}\n")
            f.write(f"- **Average FK Grade:** {avg_fk:.1f}\n")
            f.write(f"- **Average Sentence Length:** {avg_sent:.1f} words\n")
            f.write(f"- **Average Technical Terms:** {avg_tech:.2f}%\n\n")
            
            # Interpretation
            if avg_flesch >= 50:
                f.write("✅ **Overall: Acceptable readability for technical documentation**\n\n")
            elif avg_flesch >= 30:
                f.write("⚠️  **Overall: Challenging but appropriate for scientific content**\n\n")
            else:
                f.write("🔴 **Overall: Very difficult - consider simplification**\n\n")
        
        f.write("---\n\n")
        
        # Individual file analysis
        f.write("## 📋 File-by-File Analysis\n\n")
        
        for doc_path, data in sorted(results.items(), key=lambda x: -x[1]['flesch_score']):
            f.write(f"### {doc_path}\n\n")
            
            # Score interpretation
            if data['flesch_score'] >= 50:
                status = '✅'
            elif data['flesch_score'] >= 30:
                status = '⚠️'
            else:
                status = '🔴'
            
            f.write(f"{status} **Readability Score**\n\n")
            
            f.write(f"**Flesch Reading Ease:** {data['flesch_score']:.1f} ({data['difficulty']})\n\n")
            f.write(f"**Flesch-Kincaid Grade:** {data['fk_grade']:.1f}\n\n")
            
            f.write("**Metrics:**\n")
            f.write(f"- Average sentence length: {data['avg_sentence_length']:.1f} words\n")
            f.write(f"- Average syllables/word: {data['avg_syllables_per_word']:.2f}\n")
            f.write(f"- Paragraph count: {data['paragraph_count']}\n")
            f.write(f"- Average paragraph: {data['avg_paragraph_length']:.1f} words\n")
            f.write(f"- Longest paragraph: {data['max_paragraph_length']} words\n")
            f.write(f"- Technical terms: {data['technical_terms']} ({data['technical_percentage']:.2f}%)\n\n")
            
            # Recommendations
            f.write("**Recommendations:**\n")
            if data['avg_sentence_length'] > 25:
                f.write("- ⚠️  Consider shortening sentences (currently avg {:.1f} words)\n".format(data['avg_sentence_length']))
            if data['max_paragraph_length'] > 150:
                f.write(f"- ⚠️  Break up long paragraphs (max {data['max_paragraph_length']} words)\n")
            if data['technical_percentage'] > 5:
                f.write("- ℹ️  High technical term density - ensure all terms are explained\n")
            if data['flesch_score'] < 30:
                f.write("- 🔴 Very difficult reading level - consider adding examples and simplifications\n")
            
            if (data['avg_sentence_length'] <= 25 and 
                data['max_paragraph_length'] <= 150 and 
                data['flesch_score'] >= 30):
                f.write("- ✅ Good readability for technical documentation\n")
            
            f.write("\n---\n\n")
        
        # Guidelines
        f.write("## 📐 Readability Guidelines\n\n")
        f.write("### Flesch Reading Ease Scale\n\n")
        f.write("| Score | Difficulty | Typical Audience |\n")
        f.write("|-------|------------|------------------|\n")
        f.write("| 90-100 | Very Easy | 5th grade |\n")
        f.write("| 80-90 | Easy | 6th grade |\n")
        f.write("| 70-80 | Fairly Easy | 7th grade |\n")
        f.write("| 60-70 | Standard | 8-9th grade |\n")
        f.write("| 50-60 | Fairly Difficult | 10-12th grade |\n")
        f.write("| 30-50 | Difficult | College |\n")
        f.write("| 0-30 | Very Difficult | College graduate |\n\n")
        
        f.write("### Target Metrics (Scientific Documentation)\n\n")
        f.write("| Metric | Ideal Range | Acceptable |\n")
        f.write("|--------|-------------|------------|\n")
        f.write("| Flesch Score | 40-60 | 30-70 |\n")
        f.write("| FK Grade | 12-14 | 10-16 |\n")
        f.write("| Sentence Length | 15-20 words | 10-25 words |\n")
        f.write("| Paragraph Length | 50-100 words | <150 words |\n")
        f.write("| Technical Terms | 2-5% | <10% |\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/analyze_readability.py`\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"\n✅ Report generated: {output_path}")
    print()
    if results:
        print(f"Average Flesch Score: {avg_flesch:.1f}")
        print(f"Average FK Grade: {avg_fk:.1f}")
        print(f"Average Sentence Length: {avg_sent:.1f} words")

if __name__ == '__main__':
    main()
