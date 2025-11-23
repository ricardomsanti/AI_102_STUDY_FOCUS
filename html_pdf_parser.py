#!/usr/bin/env python3
"""
AI-102 Study Guide Parser
Parses HTML or PDF files containing the AI-102 study guide content

USAGE:
    python html_pdf_parser.py <input_file.html>
    python html_pdf_parser.py <input_file.pdf>

OUTPUT:
    ai102_structured_data.json
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def parse_html_file(file_path: str) -> Dict[str, Any]:
    """Parse HTML file and extract AI-102 study guide content"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: BeautifulSoup4 not installed")
        print("Install with: pip install beautifulsoup4")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    extracted_data = {
        'metadata': {
            'exam_code': 'AI-102',
            'exam_title': '',
            'extraction_date': datetime.now().isoformat(),
            'source_file': file_path,
            'exam_update_date': ''
        },
        'topic_areas': [],
        'change_log': []
    }

    # Extract title
    title_elem = soup.find(['h1', 'title'])
    if title_elem:
        extracted_data['metadata']['exam_title'] = title_elem.get_text(strip=True)

    # Extract update date
    time_elem = soup.find('time')
    if time_elem:
        extracted_data['metadata']['exam_update_date'] = time_elem.get('datetime', time_elem.get_text(strip=True))

    # Find main content
    main_content = soup.find(['main', 'article']) or soup.find(id='main-content') or soup.body

    if not main_content:
        print("WARNING: Could not find main content area")
        return extracted_data

    # Extract topic areas and skills
    current_topic_area = None
    current_skill = None

    for elem in main_content.find_all(['h2', 'h3', 'h4', 'ul', 'ol', 'table']):
        if elem.name in ['h2', 'h3', 'h4']:
            heading_text = elem.get_text(strip=True)

            # Check for percentage (indicates topic area)
            percentage_match = re.search(r'\((\d+[-–]\d+%)\)', heading_text)

            if percentage_match:
                # This is a topic area
                clean_title = re.sub(r'\((\d+[-–]\d+%)\)', '', heading_text).strip()
                current_topic_area = {
                    'topic_area': clean_title,
                    'percentage_weight': percentage_match.group(1),
                    'skills': []
                }
                extracted_data['topic_areas'].append(current_topic_area)
                current_skill = None

            elif current_topic_area and elem.name == 'h3':
                # This is a skill
                current_skill = {
                    'skill': heading_text,
                    'sub_skills': []
                }
                current_topic_area['skills'].append(current_skill)

            elif 'change' in heading_text.lower() and 'log' in heading_text.lower():
                # Change log section - will be processed below
                pass

        elif elem.name in ['ul', 'ol'] and current_skill:
            # Extract sub-skills
            for li in elem.find_all('li', recursive=False):
                sub_skill_text = li.get_text(strip=True)
                links = [a.get('href', '') for a in li.find_all('a')]

                current_skill['sub_skills'].append({
                    'sub_skill': sub_skill_text,
                    'reference_links': links,
                    'annotation': ''
                })

        elif elem.name == 'table':
            # Possible change log table
            rows = elem.find_all('tr')
            if len(rows) > 1:
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        extracted_data['change_log'].append({
                            'change_description': cells[0].get_text(strip=True),
                            'change_date': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'change_type': cells[2].get_text(strip=True) if len(cells) > 2 else 'Update'
                        })

    return extracted_data


def parse_pdf_file(file_path: str) -> Dict[str, Any]:
    """Parse PDF file and extract AI-102 study guide content"""
    try:
        import PyPDF2
    except ImportError:
        print("ERROR: PyPDF2 not installed")
        print("Install with: pip install PyPDF2")
        sys.exit(1)

    extracted_data = {
        'metadata': {
            'exam_code': 'AI-102',
            'exam_title': '',
            'extraction_date': datetime.now().isoformat(),
            'source_file': file_path,
            'exam_update_date': ''
        },
        'topic_areas': [],
        'change_log': []
    }

    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        full_text = ''

        for page in pdf_reader.pages:
            full_text += page.extract_text() + '\n'

    # Parse text line by line
    lines = full_text.split('\n')
    current_topic_area = None
    current_skill = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Check for topic area (has percentage)
        percentage_match = re.search(r'\((\d+[-–]\d+%)\)', line)
        if percentage_match:
            clean_title = re.sub(r'\((\d+[-–]\d+%)\)', '', line).strip()
            current_topic_area = {
                'topic_area': clean_title,
                'percentage_weight': percentage_match.group(1),
                'skills': []
            }
            extracted_data['topic_areas'].append(current_topic_area)
            current_skill = None

        # Check for skill (typically starts with capital, doesn't have bullet)
        elif current_topic_area and line and line[0].isupper() and not line.startswith('•'):
            current_skill = {
                'skill': line,
                'sub_skills': []
            }
            current_topic_area['skills'].append(current_skill)

        # Check for sub-skill (typically starts with bullet or lowercase)
        elif current_skill and (line.startswith('•') or line.startswith('-') or line.startswith('o')):
            sub_skill_text = line.lstrip('•-o ').strip()
            current_skill['sub_skills'].append({
                'sub_skill': sub_skill_text,
                'reference_links': [],
                'annotation': ''
            })

        i += 1

    return extracted_data


def main():
    if len(sys.argv) < 2:
        print("USAGE: python html_pdf_parser.py <input_file>")
        print("\nSupported formats: .html, .htm, .pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    file_path = Path(input_file)

    if not file_path.exists():
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)

    print(f"Parsing {file_path.name}...")

    # Determine file type and parse
    if file_path.suffix.lower() in ['.html', '.htm']:
        data = parse_html_file(str(file_path))
    elif file_path.suffix.lower() == '.pdf':
        data = parse_pdf_file(str(file_path))
    else:
        print(f"ERROR: Unsupported file type: {file_path.suffix}")
        print("Supported: .html, .htm, .pdf")
        sys.exit(1)

    # Write output
    output_file = 'ai102_structured_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Extraction complete!")
    print(f"✓ Topic areas found: {len(data['topic_areas'])}")
    print(f"✓ Change log entries: {len(data['change_log'])}")
    print(f"✓ Output saved to: {output_file}")

    # Print summary
    print("\n=== TOPIC AREAS ===")
    for topic in data['topic_areas']:
        print(f"  • {topic['topic_area']} ({topic['percentage_weight']})")
        print(f"    Skills: {len(topic['skills'])}")
        total_sub_skills = sum(len(skill['sub_skills']) for skill in topic['skills'])
        print(f"    Sub-skills: {total_sub_skills}")


if __name__ == '__main__':
    main()
