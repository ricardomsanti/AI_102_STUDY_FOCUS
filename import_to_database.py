#!/usr/bin/env python3
"""
Import AI-102 Study Guide Data to Database
Imports validated and normalized JSON data into PostgreSQL, MySQL, or SQLite

USAGE:
    # PostgreSQL
    python import_to_database.py validated_data.json --db postgres --host localhost --user username --password pass --database ai102

    # SQLite
    python import_to_database.py validated_data.json --db sqlite --database ai102.db

    # MySQL
    python import_to_database.py validated_data.json --db mysql --host localhost --user username --password pass --database ai102
"""

import sys
import json
import argparse
from typing import Dict, Any, List
from datetime import datetime


def import_to_postgres(data: Dict[str, Any], host: str, user: str, password: str, database: str):
    """Import data to PostgreSQL"""
    try:
        import psycopg2
        from psycopg2.extras import execute_batch
    except ImportError:
        print("ERROR: psycopg2 not installed")
        print("Install with: pip install psycopg2-binary")
        sys.exit(1)

    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()

    try:
        # Insert metadata
        cursor.execute("""
            INSERT INTO exam_metadata (exam_code, exam_title, extraction_date, exam_update_date, source_url, source_file)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (exam_code) DO UPDATE SET
                exam_title = EXCLUDED.exam_title,
                extraction_date = EXCLUDED.extraction_date,
                exam_update_date = EXCLUDED.exam_update_date
        """, (
            data['metadata'].get('exam_code', 'AI-102'),
            data['metadata'].get('exam_title', ''),
            data['metadata'].get('extraction_date'),
            data['metadata'].get('exam_update_date'),
            data['metadata'].get('source_url', ''),
            data['metadata'].get('source_file', '')
        ))

        # Insert topic areas
        topic_data = [
            (topic['topic_id'], topic['topic_area'], topic['percentage_weight'])
            for topic in data['topic_areas']
        ]
        execute_batch(cursor, """
            INSERT INTO topic_areas (topic_id, topic_area, percentage_weight)
            VALUES (%s, %s, %s)
            ON CONFLICT (topic_id) DO UPDATE SET
                topic_area = EXCLUDED.topic_area,
                percentage_weight = EXCLUDED.percentage_weight
        """, topic_data)

        # Insert skills
        skill_data = []
        for topic in data['topic_areas']:
            for skill in topic['skills']:
                skill_data.append((skill['skill_id'], skill['topic_id'], skill['skill']))

        execute_batch(cursor, """
            INSERT INTO skills (skill_id, topic_id, skill)
            VALUES (%s, %s, %s)
            ON CONFLICT (skill_id) DO UPDATE SET
                topic_id = EXCLUDED.topic_id,
                skill = EXCLUDED.skill
        """, skill_data)

        # Insert sub-skills
        sub_skill_data = []
        for topic in data['topic_areas']:
            for skill in topic['skills']:
                for sub_skill in skill['sub_skills']:
                    links = '|'.join(sub_skill.get('reference_links', []))
                    sub_skill_data.append((
                        sub_skill['sub_skill_id'],
                        sub_skill['skill_id'],
                        sub_skill['topic_id'],
                        sub_skill['sub_skill'],
                        links,
                        sub_skill.get('annotation', '')
                    ))

        execute_batch(cursor, """
            INSERT INTO sub_skills (sub_skill_id, skill_id, topic_id, sub_skill, reference_links, annotation)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sub_skill_id) DO UPDATE SET
                skill_id = EXCLUDED.skill_id,
                topic_id = EXCLUDED.topic_id,
                sub_skill = EXCLUDED.sub_skill,
                reference_links = EXCLUDED.reference_links,
                annotation = EXCLUDED.annotation
        """, sub_skill_data)

        # Insert change log
        change_data = [
            (
                change.get('change_id', f"CHANGE-{idx+1:03d}"),
                change.get('change_description', ''),
                change.get('change_date', ''),
                change.get('change_type', 'Update'),
                change.get('skill_prior', ''),
                change.get('skill_current', '')
            )
            for idx, change in enumerate(data.get('change_log', []))
        ]

        if change_data:
            execute_batch(cursor, """
                INSERT INTO change_log (change_id, change_description, change_date, change_type, skill_prior, skill_current)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (change_id) DO UPDATE SET
                    change_description = EXCLUDED.change_description,
                    change_date = EXCLUDED.change_date,
                    change_type = EXCLUDED.change_type
            """, change_data)

        conn.commit()
        print("✓ Data imported to PostgreSQL successfully!")

        # Print statistics
        cursor.execute("SELECT COUNT(*) FROM topic_areas")
        print(f"  Topics: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM skills")
        print(f"  Skills: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM sub_skills")
        print(f"  Sub-skills: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM change_log")
        print(f"  Change log entries: {cursor.fetchone()[0]}")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def import_to_sqlite(data: Dict[str, Any], database: str):
    """Import data to SQLite"""
    try:
        import sqlite3
    except ImportError:
        print("ERROR: sqlite3 not available")
        sys.exit(1)

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    try:
        # Create tables (simplified for SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam_metadata (
                exam_code TEXT PRIMARY KEY,
                exam_title TEXT,
                extraction_date TEXT,
                exam_update_date TEXT,
                source_url TEXT,
                source_file TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_areas (
                topic_id TEXT PRIMARY KEY,
                topic_area TEXT NOT NULL,
                percentage_weight TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL,
                skill TEXT NOT NULL,
                FOREIGN KEY (topic_id) REFERENCES topic_areas(topic_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sub_skills (
                sub_skill_id TEXT PRIMARY KEY,
                skill_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                sub_skill TEXT NOT NULL,
                reference_links TEXT,
                annotation TEXT,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
                FOREIGN KEY (topic_id) REFERENCES topic_areas(topic_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_log (
                change_id TEXT PRIMARY KEY,
                change_description TEXT,
                change_date TEXT,
                change_type TEXT,
                skill_prior TEXT,
                skill_current TEXT
            )
        """)

        # Insert data
        cursor.execute("""
            INSERT OR REPLACE INTO exam_metadata VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['metadata'].get('exam_code', 'AI-102'),
            data['metadata'].get('exam_title', ''),
            data['metadata'].get('extraction_date'),
            data['metadata'].get('exam_update_date'),
            data['metadata'].get('source_url', ''),
            data['metadata'].get('source_file', '')
        ))

        # Insert topic areas
        for topic in data['topic_areas']:
            cursor.execute("""
                INSERT OR REPLACE INTO topic_areas VALUES (?, ?, ?)
            """, (topic['topic_id'], topic['topic_area'], topic['percentage_weight']))

        # Insert skills
        for topic in data['topic_areas']:
            for skill in topic['skills']:
                cursor.execute("""
                    INSERT OR REPLACE INTO skills VALUES (?, ?, ?)
                """, (skill['skill_id'], skill['topic_id'], skill['skill']))

                # Insert sub-skills
                for sub_skill in skill['sub_skills']:
                    links = '|'.join(sub_skill.get('reference_links', []))
                    cursor.execute("""
                        INSERT OR REPLACE INTO sub_skills VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        sub_skill['sub_skill_id'],
                        sub_skill['skill_id'],
                        sub_skill['topic_id'],
                        sub_skill['sub_skill'],
                        links,
                        sub_skill.get('annotation', '')
                    ))

        # Insert change log
        for idx, change in enumerate(data.get('change_log', [])):
            cursor.execute("""
                INSERT OR REPLACE INTO change_log VALUES (?, ?, ?, ?, ?, ?)
            """, (
                change.get('change_id', f"CHANGE-{idx+1:03d}"),
                change.get('change_description', ''),
                change.get('change_date', ''),
                change.get('change_type', 'Update'),
                change.get('skill_prior', ''),
                change.get('skill_current', '')
            ))

        conn.commit()
        print("✓ Data imported to SQLite successfully!")

        # Print statistics
        cursor.execute("SELECT COUNT(*) FROM topic_areas")
        print(f"  Topics: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM skills")
        print(f"  Skills: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM sub_skills")
        print(f"  Sub-skills: {cursor.fetchone()[0]}")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def import_to_mysql(data: Dict[str, Any], host: str, user: str, password: str, database: str):
    """Import data to MySQL"""
    try:
        import mysql.connector
    except ImportError:
        print("ERROR: mysql-connector-python not installed")
        print("Install with: pip install mysql-connector-python")
        sys.exit(1)

    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()

    try:
        # Similar to PostgreSQL but with MySQL syntax
        # Insert metadata
        cursor.execute("""
            INSERT INTO exam_metadata (exam_code, exam_title, extraction_date, exam_update_date, source_url, source_file)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                exam_title = VALUES(exam_title),
                extraction_date = VALUES(extraction_date)
        """, (
            data['metadata'].get('exam_code', 'AI-102'),
            data['metadata'].get('exam_title', ''),
            data['metadata'].get('extraction_date'),
            data['metadata'].get('exam_update_date'),
            data['metadata'].get('source_url', ''),
            data['metadata'].get('source_file', '')
        ))

        # Insert topic areas
        for topic in data['topic_areas']:
            cursor.execute("""
                INSERT INTO topic_areas (topic_id, topic_area, percentage_weight)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    topic_area = VALUES(topic_area),
                    percentage_weight = VALUES(percentage_weight)
            """, (topic['topic_id'], topic['topic_area'], topic['percentage_weight']))

        # Insert skills and sub-skills
        for topic in data['topic_areas']:
            for skill in topic['skills']:
                cursor.execute("""
                    INSERT INTO skills (skill_id, topic_id, skill)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        topic_id = VALUES(topic_id),
                        skill = VALUES(skill)
                """, (skill['skill_id'], skill['topic_id'], skill['skill']))

                for sub_skill in skill['sub_skills']:
                    links = '|'.join(sub_skill.get('reference_links', []))
                    cursor.execute("""
                        INSERT INTO sub_skills (sub_skill_id, skill_id, topic_id, sub_skill, reference_links, annotation)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            skill_id = VALUES(skill_id),
                            topic_id = VALUES(topic_id),
                            sub_skill = VALUES(sub_skill),
                            reference_links = VALUES(reference_links)
                    """, (
                        sub_skill['sub_skill_id'],
                        sub_skill['skill_id'],
                        sub_skill['topic_id'],
                        sub_skill['sub_skill'],
                        links,
                        sub_skill.get('annotation', '')
                    ))

        conn.commit()
        print("✓ Data imported to MySQL successfully!")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='Import AI-102 study guide data to database')
    parser.add_argument('json_file', help='Path to validated JSON data file')
    parser.add_argument('--db', choices=['postgres', 'mysql', 'sqlite'], required=True,
                        help='Database type')
    parser.add_argument('--host', help='Database host (not needed for SQLite)')
    parser.add_argument('--user', help='Database user (not needed for SQLite)')
    parser.add_argument('--password', help='Database password (not needed for SQLite)')
    parser.add_argument('--database', required=True, help='Database name or file path (for SQLite)')

    args = parser.parse_args()

    # Load JSON data
    print(f"Loading {args.json_file}...")
    with open(args.json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Importing to {args.db}...")

    if args.db == 'postgres':
        if not all([args.host, args.user, args.password]):
            print("ERROR: --host, --user, and --password required for PostgreSQL")
            sys.exit(1)
        import_to_postgres(data, args.host, args.user, args.password, args.database)

    elif args.db == 'mysql':
        if not all([args.host, args.user, args.password]):
            print("ERROR: --host, --user, and --password required for MySQL")
            sys.exit(1)
        import_to_mysql(data, args.host, args.user, args.password, args.database)

    elif args.db == 'sqlite':
        import_to_sqlite(data, args.database)

    print("\n✅ Import complete!")


if __name__ == '__main__':
    main()
