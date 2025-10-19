#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Reference Audit

Checks all internal links in markdown documentation
Identifies broken links, missing files, and cross-reference issues

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

def extract_markdown_links(filepath):
    """Extract all markdown links from file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        links = []
        
        # [text](url) format
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(pattern, content)
        for text, url in matches:
            links.append({
                'text': text,
                'url': url,
                'type': 'markdown',
                'file': str(filepath)
            })
        
        # <url> format
        pattern2 = r'<([^>]+\.(md|pdf|py|csv|txt))>'
        matches2 = re.findall(pattern2, content)
        for url, ext in matches2:
            links.append({
                'text': url,
                'url': url,
                'type': 'angle_bracket',
                'file': str(filepath)
            })
        
        return links
    except Exception as e:
        return []

def check_link_validity(link, root_dir):
    """Check if link points to valid file"""
    url = link['url']
    source_file = Path(link['file'])
    
    # Skip external URLs
    if url.startswith('http://') or url.startswith('https://'):
        return {'status': 'external', 'message': 'External URL (not checked)'}
    
    # Skip anchors within same file
    if url.startswith('#'):
        return {'status': 'anchor', 'message': 'Internal anchor (not checked)'}
    
    # Remove anchor if present
    if '#' in url:
        url = url.split('#')[0]
    
    # Skip empty
    if not url:
        return {'status': 'skip', 'message': 'Empty URL'}
    
    # Resolve relative path
    if url.startswith('/'):
        # Absolute from root
        target = root_dir / url[1:]
    else:
        # Relative to current file
        target = source_file.parent / url
    
    # Normalize path
    try:
        target = target.resolve()
    except:
        return {'status': 'error', 'message': 'Cannot resolve path'}
    
    # Check if exists
    if target.exists():
        return {'status': 'valid', 'target': str(target)}
    else:
        return {'status': 'broken', 'message': f'File not found: {target.name}'}

def main():
    """Audit cross-references"""
    print("="*80)
    print("CROSS-REFERENCE AUDIT")
    print("="*80)
    print()
    
    # Find root
    root = Path(__file__).parent.parent
    print(f"Repository root: {root}")
    print()
    
    # Find all markdown files (excluding some dirs)
    exclude_dirs = {'.venv', '__pycache__', 'node_modules', '.git'}
    md_files = []
    
    for md_file in root.rglob('*.md'):
        # Skip excluded directories
        if any(excluded in str(md_file) for excluded in exclude_dirs):
            continue
        md_files.append(md_file)
    
    print(f"Scanning {len(md_files)} markdown files...")
    print()
    
    all_links = []
    file_link_counts = {}
    
    # Extract all links
    for filepath in md_files:
        links = extract_markdown_links(filepath)
        if links:
            all_links.extend(links)
            file_link_counts[str(filepath)] = len(links)
    
    print(f"Total links found: {len(all_links)}")
    print()
    
    # Check link validity
    print("Checking link validity...")
    results = {
        'valid': [],
        'broken': [],
        'external': [],
        'anchor': [],
        'skip': [],
        'error': []
    }
    
    for link in all_links:
        result = check_link_validity(link, root)
        status = result['status']
        results[status].append({**link, **result})
    
    print()
    print(f"✅ Valid links: {len(results['valid'])}")
    print(f"❌ Broken links: {len(results['broken'])}")
    print(f"🌐 External URLs: {len(results['external'])}")
    print(f"⚓ Anchors: {len(results['anchor'])}")
    print()
    
    # Generate report
    output_path = root / 'docs' / 'improvement' / 'CROSS_REFERENCE_AUDIT.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Cross-Reference Audit Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Files Scanned:** {len(md_files)}\n")
        f.write(f"**Total Links:** {len(all_links)}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Summary\n\n")
        f.write("| Status | Count | Percentage |\n")
        f.write("|--------|-------|------------|\n")
        total = len(all_links)
        for status in ['valid', 'broken', 'external', 'anchor', 'skip', 'error']:
            count = len(results[status])
            pct = (count / total * 100) if total > 0 else 0
            emoji = {'valid': '✅', 'broken': '❌', 'external': '🌐', 
                    'anchor': '⚓', 'skip': '➖', 'error': '⚠️'}[status]
            f.write(f"| {emoji} {status.title()} | {count} | {pct:.1f}% |\n")
        f.write("\n---\n\n")
        
        # Broken links (HIGH PRIORITY)
        if results['broken']:
            f.write("## ❌ Broken Links (HIGH PRIORITY)\n\n")
            f.write(f"**Total:** {len(results['broken'])} broken links found\n\n")
            
            # Group by source file
            by_file = defaultdict(list)
            for link in results['broken']:
                rel_path = Path(link['file']).relative_to(root)
                by_file[str(rel_path)].append(link)
            
            for filepath in sorted(by_file.keys()):
                f.write(f"### {filepath}\n\n")
                for link in by_file[filepath]:
                    f.write(f"- **Link text:** `{link['text']}`\n")
                    f.write(f"  - **URL:** `{link['url']}`\n")
                    f.write(f"  - **Issue:** {link['message']}\n\n")
            
            f.write("---\n\n")
        else:
            f.write("## ✅ No Broken Links\n\n")
            f.write("All internal links are valid!\n\n")
            f.write("---\n\n")
        
        # Files with most links
        f.write("## 📈 Files with Most Links\n\n")
        top_files = sorted(file_link_counts.items(), key=lambda x: -x[1])[:15]
        if top_files:
            f.write("| File | Link Count |\n")
            f.write("|------|------------|\n")
            for filepath, count in top_files:
                rel_path = Path(filepath).relative_to(root)
                f.write(f"| {rel_path} | {count} |\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # External URLs
        if results['external']:
            f.write("## 🌐 External URLs\n\n")
            f.write(f"**Total:** {len(results['external'])} external links\n\n")
            
            # Group by domain
            by_domain = defaultdict(int)
            for link in results['external']:
                url = link['url']
                # Extract domain
                match = re.match(r'https?://([^/]+)', url)
                if match:
                    domain = match.group(1)
                    by_domain[domain] += 1
            
            if by_domain:
                f.write("### External Domains\n\n")
                f.write("| Domain | Count |\n")
                f.write("|--------|-------|\n")
                for domain in sorted(by_domain.keys(), key=lambda x: -by_domain[x])[:20]:
                    f.write(f"| {domain} | {by_domain[domain]} |\n")
                f.write("\n")
            
            f.write("**Note:** External URLs are not automatically checked. Consider periodic manual review.\n\n")
            f.write("---\n\n")
        
        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        
        if results['broken']:
            f.write("### 1. Fix Broken Links (HIGH PRIORITY)\n\n")
            f.write(f"- **Total broken:** {len(results['broken'])} links\n")
            f.write("- Review each broken link above\n")
            f.write("- Update URLs or restore missing files\n")
            f.write("- Re-run audit after fixes\n\n")
        else:
            f.write("### 1. Maintain Link Health\n\n")
            f.write("- ✅ All internal links currently valid\n")
            f.write("- Run audit after major file reorganizations\n")
            f.write("- Consider CI check for broken links\n\n")
        
        f.write("### 2. External URL Monitoring\n\n")
        f.write(f"- {len(results['external'])} external URLs present\n")
        f.write("- Consider periodic manual checks\n")
        f.write("- Use link checker tool for automation\n")
        f.write("- Archive important external content\n\n")
        
        f.write("### 3. Cross-Reference Best Practices\n\n")
        f.write("- Use relative paths for internal links\n")
        f.write("- Prefer markdown link format: `[text](url)`\n")
        f.write("- Add descriptive link text\n")
        f.write("- Keep file paths stable\n\n")
        
        f.write("### 4. Next Steps\n\n")
        f.write("- [ ] Fix all broken links\n")
        f.write("- [ ] Review external URLs\n")
        f.write("- [ ] Add link validation to CI/CD\n")
        f.write("- [ ] Document file organization standards\n\n")
        
        f.write("---\n\n")
        f.write("**Generated by:** `scripts/audit_cross_references.py`\n")
        f.write("**Next:** Phase 1.5 - Bilingual Coverage Analysis\n\n")
        f.write("© 2025 Carmen Wrede & Lino Casu\n")
    
    print(f"✅ Report generated: {output_path}")
    print()
    
    if results['broken']:
        print("⚠️  ACTION REQUIRED:")
        print(f"   {len(results['broken'])} broken links need fixing")
        print("   Review CROSS_REFERENCE_AUDIT.md for details")
    else:
        print("✅ All internal links are valid!")
    
    print()
    print("Next steps:")
    print("  1. Review CROSS_REFERENCE_AUDIT.md")
    print("  2. Fix broken links if any")
    print("  3. Start Phase 1.5: Bilingual Coverage Analysis")

if __name__ == '__main__':
    main()
