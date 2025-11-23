#!/usr/bin/env python3
"""
Sample Database Queries for AI-102 Study Guide
Demonstrates common queries for study tracking and analytics

USAGE:
    python sample_queries.py --db sqlite --database ai102.db
    python sample_queries.py --db postgres --host localhost --user username --password pass --database ai102
"""

import argparse
import sys


def connect_database(db_type, **kwargs):
    """Connect to database and return connection"""
    if db_type == 'sqlite':
        import sqlite3
        return sqlite3.connect(kwargs['database'])
    elif db_type == 'postgres':
        import psycopg2
        return psycopg2.connect(
            host=kwargs['host'],
            user=kwargs['user'],
            password=kwargs['password'],
            database=kwargs['database']
        )
    elif db_type == 'mysql':
        import mysql.connector
        return mysql.connector.connect(
            host=kwargs['host'],
            user=kwargs['user'],
            password=kwargs['password'],
            database=kwargs['database']
        )


def run_query(conn, query, description):
    """Run a query and display results"""
    print(f"\n{'=' * 80}")
    print(f"{description}")
    print(f"{'=' * 80}")

    cursor = conn.cursor()
    cursor.execute(query)

    # Get column names
    columns = [desc[0] for desc in cursor.description]
    print("\n" + " | ".join(columns))
    print("-" * 80)

    # Fetch and display results
    rows = cursor.fetchall()
    if not rows:
        print("(No results)")
    else:
        for row in rows:
            print(" | ".join(str(col) for col in row))

    cursor.close()
    print(f"\nRows returned: {len(rows)}")


def main():
    parser = argparse.ArgumentParser(description='Sample queries for AI-102 study guide database')
    parser.add_argument('--db', choices=['postgres', 'mysql', 'sqlite'], required=True)
    parser.add_argument('--host', help='Database host')
    parser.add_argument('--user', help='Database user')
    parser.add_argument('--password', help='Database password')
    parser.add_argument('--database', required=True, help='Database name or file')

    args = parser.parse_args()

    # Connect to database
    print("Connecting to database...")
    conn_params = {'database': args.database}
    if args.host:
        conn_params['host'] = args.host
    if args.user:
        conn_params['user'] = args.user
    if args.password:
        conn_params['password'] = args.password

    conn = connect_database(args.db, **conn_params)
    print("✓ Connected!")

    # Query 1: Topic Overview
    run_query(conn, """
        SELECT
            topic_area,
            percentage_weight,
            COUNT(DISTINCT s.skill_id) as num_skills,
            COUNT(ss.sub_skill_id) as num_sub_skills
        FROM topic_areas t
        LEFT JOIN skills s ON t.topic_id = s.topic_id
        LEFT JOIN sub_skills ss ON s.skill_id = ss.skill_id
        GROUP BY t.topic_id, topic_area, percentage_weight
        ORDER BY t.topic_id
    """, "TOPIC OVERVIEW - All exam topics with counts")

    # Query 2: All Skills in a Topic
    run_query(conn, """
        SELECT
            t.topic_area,
            s.skill,
            COUNT(ss.sub_skill_id) as num_sub_skills
        FROM topic_areas t
        JOIN skills s ON t.topic_id = s.topic_id
        LEFT JOIN sub_skills ss ON s.skill_id = ss.skill_id
        WHERE t.topic_id = 'TOPIC-001'
        GROUP BY t.topic_area, s.skill_id, s.skill
        ORDER BY s.skill_id
    """, "SKILLS IN FIRST TOPIC AREA - Detailed breakdown")

    # Query 3: Sub-skills with References
    run_query(conn, """
        SELECT
            t.topic_area,
            s.skill,
            ss.sub_skill,
            ss.reference_links
        FROM sub_skills ss
        JOIN skills s ON ss.skill_id = s.skill_id
        JOIN topic_areas t ON ss.topic_id = t.topic_id
        WHERE ss.reference_links != ''
        LIMIT 10
    """, "SUB-SKILLS WITH REFERENCE LINKS - First 10")

    # Query 4: Change Log
    run_query(conn, """
        SELECT
            change_type,
            change_description,
            change_date
        FROM change_log
        ORDER BY change_id
    """, "CHANGE LOG - Exam update history")

    # Query 5: Skills by Topic (Hierarchy)
    run_query(conn, """
        SELECT
            t.topic_area,
            t.percentage_weight,
            s.skill,
            COUNT(ss.sub_skill_id) as sub_skills_count
        FROM topic_areas t
        LEFT JOIN skills s ON t.topic_id = s.topic_id
        LEFT JOIN sub_skills ss ON s.skill_id = ss.skill_id
        GROUP BY t.topic_id, t.topic_area, t.percentage_weight, s.skill_id, s.skill
        ORDER BY t.topic_id, s.skill_id
        LIMIT 20
    """, "HIERARCHICAL VIEW - Topics > Skills > Sub-skill counts")

    # Query 6: Find specific sub-skills
    run_query(conn, """
        SELECT
            t.topic_area,
            s.skill,
            ss.sub_skill
        FROM sub_skills ss
        JOIN skills s ON ss.skill_id = s.skill_id
        JOIN topic_areas t ON ss.topic_id = t.topic_id
        WHERE LOWER(ss.sub_skill) LIKE '%responsible ai%'
           OR LOWER(ss.sub_skill) LIKE '%ethical%'
    """, "SEARCH - Sub-skills related to 'Responsible AI'")

    # Query 7: Statistics
    run_query(conn, """
        SELECT
            'Total Topics' as metric,
            COUNT(DISTINCT topic_id) as count
        FROM topic_areas
        UNION ALL
        SELECT
            'Total Skills',
            COUNT(DISTINCT skill_id)
        FROM skills
        UNION ALL
        SELECT
            'Total Sub-Skills',
            COUNT(DISTINCT sub_skill_id)
        FROM sub_skills
        UNION ALL
        SELECT
            'Sub-Skills with References',
            COUNT(DISTINCT sub_skill_id)
        FROM sub_skills
        WHERE reference_links != ''
    """, "OVERALL STATISTICS - Dataset summary")

    # Close connection
    conn.close()
    print(f"\n{'=' * 80}")
    print("✓ All queries completed successfully!")
    print(f"{'=' * 80}\n")

    print("\nNext Steps:")
    print("  • Modify these queries for your specific needs")
    print("  • Add user progress tracking using study_progress table")
    print("  • Create custom views for your study application")
    print("  • Build quiz questions from sub_skills")
    print("\nSee setup_database.sql for table schemas and additional views")


if __name__ == '__main__':
    main()
