#!/usr/bin/env python3
"""
AI-102 Data Validator and Normalizer
Validates extracted data against schema and normalizes for database ingestion

USAGE:
    python validate_and_normalize.py <input_json_file>

OUTPUT:
    - validated_data.json (validated and normalized data)
    - database_ready.csv (flattened for database import)
    - change_log.csv (change log in tabular format)
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def validate_data(data: Dict[str, Any]) -> List[str]:
    """Validate data structure and return list of errors"""
    errors = []

    # Check required top-level keys
    required_keys = ['metadata', 'topic_areas', 'change_log']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    if 'metadata' in data:
        meta = data['metadata']
        if 'exam_code' not in meta:
            errors.append("Missing metadata.exam_code")
        elif meta['exam_code'] != 'AI-102':
            errors.append(f"Invalid exam_code: {meta['exam_code']}")

    if 'topic_areas' in data:
        if not isinstance(data['topic_areas'], list):
            errors.append("topic_areas must be an array")
        elif len(data['topic_areas']) == 0:
            errors.append("topic_areas array is empty")
        else:
            for idx, topic in enumerate(data['topic_areas']):
                if 'topic_area' not in topic:
                    errors.append(f"Topic {idx}: missing topic_area")
                if 'percentage_weight' not in topic:
                    errors.append(f"Topic {idx}: missing percentage_weight")
                if 'skills' not in topic:
                    errors.append(f"Topic {idx}: missing skills")
                elif not isinstance(topic['skills'], list):
                    errors.append(f"Topic {idx}: skills must be an array")
                else:
                    for skill_idx, skill in enumerate(topic['skills']):
                        if 'skill' not in skill:
                            errors.append(f"Topic {idx}, Skill {skill_idx}: missing skill name")
                        if 'sub_skills' not in skill:
                            errors.append(f"Topic {idx}, Skill {skill_idx}: missing sub_skills")

    return errors


def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and clean data"""
    normalized = json.loads(json.dumps(data))  # Deep copy

    # Add unique IDs
    topic_id = 1
    skill_id = 1
    sub_skill_id = 1

    for topic in normalized.get('topic_areas', []):
        topic['topic_id'] = f"TOPIC-{topic_id:03d}"
        topic_id += 1

        for skill in topic.get('skills', []):
            skill['skill_id'] = f"SKILL-{skill_id:04d}"
            skill['topic_id'] = topic['topic_id']
            skill_id += 1

            for sub_skill in skill.get('sub_skills', []):
                sub_skill['sub_skill_id'] = f"SUBSKILL-{sub_skill_id:05d}"
                sub_skill['skill_id'] = skill['skill_id']
                sub_skill['topic_id'] = topic['topic_id']

                # Ensure arrays and defaults
                if 'reference_links' not in sub_skill:
                    sub_skill['reference_links'] = []
                if 'annotation' not in sub_skill:
                    sub_skill['annotation'] = ''

                sub_skill_id += 1

    # Normalize change log
    for idx, change in enumerate(normalized.get('change_log', [])):
        change['change_id'] = f"CHANGE-{idx+1:03d}"
        if 'change_type' not in change:
            change['change_type'] = 'Update'
        if 'change_date' not in change:
            change['change_date'] = normalized['metadata'].get('exam_update_date', 'Unknown')

    return normalized


def export_to_csv(data: Dict[str, Any], output_dir: str = '.'):
    """Export data to CSV files for database import"""
    output_path = Path(output_dir)

    # Export flattened sub-skills
    subskills_file = output_path / 'database_ready.csv'
    with open(subskills_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'sub_skill_id', 'skill_id', 'topic_id',
            'topic_area', 'percentage_weight',
            'skill', 'sub_skill',
            'reference_links', 'annotation'
        ])

        for topic in data.get('topic_areas', []):
            for skill in topic.get('skills', []):
                for sub_skill in skill.get('sub_skills', []):
                    writer.writerow([
                        sub_skill['sub_skill_id'],
                        sub_skill['skill_id'],
                        sub_skill['topic_id'],
                        topic['topic_area'],
                        topic['percentage_weight'],
                        skill['skill'],
                        sub_skill['sub_skill'],
                        '|'.join(sub_skill.get('reference_links', [])),
                        sub_skill.get('annotation', '')
                    ])

    # Export change log
    changelog_file = output_path / 'change_log.csv'
    with open(changelog_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['change_id', 'change_description', 'change_date', 'change_type'])

        for change in data.get('change_log', []):
            writer.writerow([
                change.get('change_id', ''),
                change.get('change_description', ''),
                change.get('change_date', ''),
                change.get('change_type', 'Update')
            ])

    return subskills_file, changelog_file


def generate_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate statistics about the dataset"""
    stats = {
        'total_topic_areas': len(data.get('topic_areas', [])),
        'total_skills': 0,
        'total_sub_skills': 0,
        'total_reference_links': 0,
        'topic_breakdown': []
    }

    for topic in data.get('topic_areas', []):
        topic_stats = {
            'topic_area': topic.get('topic_area', ''),
            'percentage_weight': topic.get('percentage_weight', ''),
            'skills_count': len(topic.get('skills', [])),
            'sub_skills_count': 0
        }

        for skill in topic.get('skills', []):
            stats['total_skills'] += 1
            sub_skills_count = len(skill.get('sub_skills', []))
            topic_stats['sub_skills_count'] += sub_skills_count
            stats['total_sub_skills'] += sub_skills_count

            for sub_skill in skill.get('sub_skills', []):
                stats['total_reference_links'] += len(sub_skill.get('reference_links', []))

        stats['topic_breakdown'].append(topic_stats)

    return stats


def main():
    if len(sys.argv) < 2:
        print("USAGE: python validate_and_normalize.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    file_path = Path(input_file)

    if not file_path.exists():
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)

    print(f"Loading {file_path.name}...")

    # Load data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate
    print("\nValidating data structure...")
    errors = validate_data(data)

    if errors:
        print("\n❌ VALIDATION ERRORS:")
        for error in errors:
            print(f"  • {error}")
        print("\nPlease fix errors before proceeding.")
        sys.exit(1)

    print("✓ Validation passed!")

    # Normalize
    print("\nNormalizing data...")
    normalized_data = normalize_data(data)
    print("✓ Normalization complete!")

    # Save normalized JSON
    output_json = 'validated_data.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved: {output_json}")

    # Export to CSV
    print("\nExporting to CSV...")
    csv1, csv2 = export_to_csv(normalized_data)
    print(f"✓ Saved: {csv1}")
    print(f"✓ Saved: {csv2}")

    # Generate statistics
    print("\nGenerating statistics...")
    stats = generate_statistics(normalized_data)

    print("\n=== STATISTICS ===")
    print(f"Total Topic Areas: {stats['total_topic_areas']}")
    print(f"Total Skills: {stats['total_skills']}")
    print(f"Total Sub-Skills: {stats['total_sub_skills']}")
    print(f"Total Reference Links: {stats['total_reference_links']}")

    print("\n=== TOPIC BREAKDOWN ===")
    for topic_stat in stats['topic_breakdown']:
        print(f"\n{topic_stat['topic_area']} ({topic_stat['percentage_weight']})")
        print(f"  Skills: {topic_stat['skills_count']}")
        print(f"  Sub-skills: {topic_stat['sub_skills_count']}")

    # Save statistics
    stats_file = 'statistics.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"\n✓ Statistics saved to: {stats_file}")

    print("\n✅ All processing complete!")
    print("\nFiles generated:")
    print(f"  1. {output_json} - Validated and normalized JSON")
    print(f"  2. database_ready.csv - Flattened data for database import")
    print(f"  3. change_log.csv - Change log in tabular format")
    print(f"  4. {stats_file} - Dataset statistics")


if __name__ == '__main__':
    main()
