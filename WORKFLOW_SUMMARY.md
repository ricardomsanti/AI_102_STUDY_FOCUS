# AI-102 Study Guide Extraction - Complete Workflow

## Executive Summary

This toolkit provides a complete, production-ready solution for extracting, structuring, validating, and storing Microsoft AI-102 exam study guide content. All content is transformed into machine-readable formats optimized for:

- Database storage and querying
- Study tracking applications
- Gamification systems
- Learning management platforms
- Analytics and progress reporting

## Complete File Inventory

### Core Extraction Tools

| File | Purpose | When to Use |
|------|---------|-------------|
| `browser_extraction_script.js` | JavaScript for browser console | **Primary method** - Most reliable |
| `html_pdf_parser.py` | Parse saved HTML/PDF files | When browser method fails or for offline use |
| `manual_input_template.json` | Manual data entry template | Last resort or for custom modifications |

### Data Processing

| File | Purpose | Input | Output |
|------|---------|-------|--------|
| `validate_and_normalize.py` | Validates and normalizes extracted data | Raw JSON | Validated JSON + CSV files |
| `schema.json` | JSON schema for validation | N/A | Used by validator |

### Database Integration

| File | Purpose | Supports |
|------|---------|----------|
| `setup_database.sql` | Database schema creation | PostgreSQL, MySQL, SQLite |
| `import_to_database.py` | Import data to database | PostgreSQL, MySQL, SQLite |
| `sample_queries.py` | Example database queries | All database types |

### User Tools

| File | Purpose |
|------|---------|
| `quick_start.sh` | Interactive setup wizard |
| `EXTRACTION_GUIDE.md` | Complete documentation |
| `README.md` | Project overview |
| `WORKFLOW_SUMMARY.md` | This file |

### Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git ignore patterns |

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION PHASE                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Choose Method    │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Browser     │    │  HTML/PDF     │    │    Manual     │
│  Extraction   │    │   Parser      │    │    Input      │
│               │    │               │    │               │
│ Run JS in     │    │ python        │    │ Edit JSON     │
│ console       │    │ html_pdf_     │    │ template      │
│               │    │ parser.py     │    │               │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └─────────────┬──────┴──────┬─────────────┘
                      ▼             ▼
              ┌──────────────────────────┐
              │   Raw JSON Data File     │
              │ (ai102_raw_data.json)    │
              └──────────┬───────────────┘
                         │
┌────────────────────────────────────────────────────────────────┐
│                  VALIDATION PHASE                              │
└────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ validate_and_        │
              │ normalize.py         │
              │                      │
              │ • Validates schema   │
              │ • Adds unique IDs    │
              │ • Normalizes data    │
              │ • Generates stats    │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌──────────────┐ ┌────────────┐
│ validated_    │ │ database_    │ │ change_    │
│ data.json     │ │ ready.csv    │ │ log.csv    │
│               │ │              │ │            │
│ Complete JSON │ │ Flattened    │ │ Change     │
│ with IDs      │ │ for DB       │ │ history    │
└───────┬───────┘ └──────┬───────┘ └─────┬──────┘
        │                │               │
        │                ▼               │
        │         ┌────────────┐         │
        │         │statistics. │         │
        │         │json        │         │
        │         └────────────┘         │
        │                                │
┌────────────────────────────────────────────────────────────────┐
│                  DATABASE PHASE (Optional)                     │
└────────────────────────────────────────────────────────────────┘
        │                                │
        ▼                                ▼
┌──────────────────┐          ┌──────────────────┐
│ setup_database.  │          │ import_to_       │
│ sql              │          │ database.py      │
│                  │          │                  │
│ CREATE TABLES    │──────────▶ INSERT DATA      │
└──────────────────┘          └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐   ┌──────────────┐  ┌──────────────┐
            │ PostgreSQL   │   │    MySQL     │  │   SQLite     │
            │              │   │              │  │              │
            │ Full DB      │   │ Full DB      │  │ Local file   │
            └──────┬───────┘   └──────┬───────┘  └──────┬───────┘
                   │                  │                 │
                   └──────────────────┼─────────────────┘
                                      │
┌────────────────────────────────────────────────────────────────┐
│                    USAGE PHASE                                 │
└────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │ Study App    │  │ Quiz Engine  │  │  Analytics   │
            │              │  │              │  │              │
            │ Track        │  │ Generate     │  │ Progress     │
            │ progress     │  │ questions    │  │ reports      │
            └──────────────┘  └──────────────┘  └──────────────┘
```

## Data Flow Details

### 1. Extraction Phase

**Input:** Microsoft AI-102 study guide webpage

**Process:**
- **Method 1 (Browser):** JavaScript extracts DOM elements directly
- **Method 2 (Parser):** BeautifulSoup/PyPDF2 parses saved files
- **Method 3 (Manual):** Human entry using JSON template

**Output:** Raw JSON with hierarchical structure

**Data Fields Captured:**
- Exam metadata (code, title, dates)
- Topic areas with percentage weights
- Skills under each topic
- Sub-skills with reference links
- Change log entries

### 2. Validation & Normalization Phase

**Input:** Raw JSON from extraction

**Process:**
```python
validate_and_normalize.py performs:
1. Schema validation against schema.json
2. Data integrity checks
3. Unique ID assignment:
   - TOPIC-001, TOPIC-002, ...
   - SKILL-0001, SKILL-0002, ...
   - SUBSKILL-00001, SUBSKILL-00002, ...
4. Relational linking (foreign keys in JSON)
5. CSV export with flattening
6. Statistics generation
```

**Outputs:**
- `validated_data.json` - Clean, normalized JSON
- `database_ready.csv` - Flattened for SQL import
- `change_log.csv` - Tabular change history
- `statistics.json` - Dataset metrics

**Quality Checks:**
- All required fields present
- Valid percentage weight format
- No duplicate IDs
- Proper hierarchical relationships
- Reference links validated

### 3. Database Integration Phase

**Input:** Validated JSON and CSV files

**Process:**
```bash
# Step 1: Create database schema
psql -d ai102 -f setup_database.sql

# Step 2: Import data
python import_to_database.py validated_data.json \
  --db postgres --host localhost \
  --user username --password pass \
  --database ai102
```

**Database Schema:**
```
exam_metadata (1)
    │
topic_areas (6+)
    │
    ├──▶ skills (24+)
    │       │
    │       └──▶ sub_skills (150+)
    │
change_log (variable)

study_progress (user data)
    └──▶ links to sub_skills

quiz_results (user data)
    └──▶ links to sub_skills
```

**Views Created:**
- `v_skills_hierarchy` - Complete topic ▶ skill ▶ sub-skill view
- `v_progress_by_topic` - User progress by topic
- `v_quiz_performance` - Quiz accuracy by topic
- `v_weak_areas` - Low-performance areas

### 4. Usage Phase

**Query Examples:**

```sql
-- Get all skills in a topic
SELECT skill, COUNT(*) as sub_skills
FROM skills s
JOIN sub_skills ss ON s.skill_id = ss.skill_id
WHERE s.topic_id = 'TOPIC-001'
GROUP BY skill;

-- Track user progress
SELECT
  topic_area,
  COUNT(*) as total,
  SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed
FROM study_progress sp
JOIN sub_skills ss ON sp.sub_skill_id = ss.sub_skill_id
JOIN topic_areas t ON ss.topic_id = t.topic_id
WHERE user_id = 'user123'
GROUP BY topic_area;
```

## Data Structure Details

### Complete JSON Structure

```json
{
  "metadata": {
    "exam_code": "AI-102",
    "exam_title": "Designing and Implementing a Microsoft Azure AI Solution",
    "extraction_date": "2025-11-23T00:00:00Z",
    "exam_update_date": "April 2025",
    "source_url": "https://...",
    "source_file": "study_guide.html"
  },
  "topic_areas": [
    {
      "topic_id": "TOPIC-001",
      "topic_area": "Plan and manage an Azure AI solution",
      "percentage_weight": "20-25%",
      "skills": [
        {
          "skill_id": "SKILL-0001",
          "topic_id": "TOPIC-001",
          "skill": "Select the appropriate Azure AI Foundry services",
          "sub_skills": [
            {
              "sub_skill_id": "SUBSKILL-00001",
              "skill_id": "SKILL-0001",
              "topic_id": "TOPIC-001",
              "sub_skill": "Select the appropriate service for a generative AI solution",
              "reference_links": [
                "https://learn.microsoft.com/azure/ai-services/"
              ],
              "annotation": ""
            }
          ]
        }
      ]
    }
  ],
  "change_log": [
    {
      "change_id": "CHANGE-001",
      "change_description": "Azure AI Foundry is now Microsoft Foundry",
      "change_date": "April 2025",
      "change_type": "Major",
      "skill_prior": "Azure AI Foundry services",
      "skill_current": "Microsoft Foundry services"
    }
  ]
}
```

### Database Schema (Normalized)

```sql
-- Exam metadata (1 row)
exam_metadata
  - exam_code PK
  - exam_title
  - extraction_date
  - exam_update_date

-- Topic areas (6 rows expected)
topic_areas
  - topic_id PK
  - topic_area
  - percentage_weight

-- Skills (20-30 rows expected)
skills
  - skill_id PK
  - topic_id FK
  - skill

-- Sub-skills (100-200 rows expected)
sub_skills
  - sub_skill_id PK
  - skill_id FK
  - topic_id FK
  - sub_skill
  - reference_links (pipe-delimited)
  - annotation

-- Change log (variable rows)
change_log
  - change_id PK
  - change_description
  - change_date
  - change_type
```

## Expected Dataset Size

Based on AI-102 exam structure:

| Entity | Count | Notes |
|--------|-------|-------|
| Topic Areas | 6 | Fixed by exam structure |
| Skills | 20-30 | Variable by exam version |
| Sub-Skills | 100-200 | Most granular level |
| Change Log Entries | 5-20 | Grows over time |
| Reference Links | 50-100 | Not all sub-skills have links |

## Use Case Examples

### 1. Study Tracking Application

```python
# Get user's next study item
SELECT ss.sub_skill, ss.reference_links
FROM sub_skills ss
LEFT JOIN study_progress sp ON ss.sub_skill_id = sp.sub_skill_id
  AND sp.user_id = 'user123'
WHERE sp.sub_skill_id IS NULL
  OR sp.status = 'not_started'
ORDER BY ss.topic_id, ss.skill_id, ss.sub_skill_id
LIMIT 1;
```

### 2. Weighted Quiz Generation

```python
# Generate quiz weighted by topic percentage
# Topics with 20-25% weight get 25 questions
# Topics with 10-15% weight get 15 questions
SELECT
  t.percentage_weight,
  ss.sub_skill_id,
  ss.sub_skill
FROM sub_skills ss
JOIN topic_areas t ON ss.topic_id = t.topic_id
WHERE t.percentage_weight = '20-25%'
ORDER BY RANDOM()
LIMIT 25;
```

### 3. Progress Dashboard

```python
# Get completion percentage by topic
SELECT
  topic_area,
  percentage_weight,
  ROUND(100.0 * completed / total, 2) as completion_pct
FROM v_progress_by_topic
WHERE user_id = 'user123'
ORDER BY completion_pct ASC;
```

### 4. Spaced Repetition

```python
# Find items due for review
SELECT ss.sub_skill
FROM study_progress sp
JOIN sub_skills ss ON sp.sub_skill_id = ss.sub_skill_id
WHERE sp.user_id = 'user123'
  AND sp.last_reviewed < NOW() - INTERVAL '7 days'
  AND sp.confidence_level < 4
ORDER BY sp.last_reviewed ASC
LIMIT 10;
```

## Quality Assurance Checklist

Before considering extraction complete:

- [ ] All 6 topic areas extracted
- [ ] Percentage weights present for all topics
- [ ] All skills listed under correct topics
- [ ] All sub-skill bullet points captured
- [ ] Reference links preserved where available
- [ ] Change log section extracted
- [ ] Metadata fields populated correctly
- [ ] JSON validates against schema
- [ ] Unique IDs assigned to all entities
- [ ] CSV exports generated successfully
- [ ] Statistics match manual count
- [ ] Database import successful
- [ ] Sample queries return expected results

## Troubleshooting Common Issues

### Issue: Browser script returns empty data

**Solution:**
1. Ensure page is fully loaded
2. Check console for errors
3. Try refreshing page
4. Use Method 2 (HTML parser) instead

### Issue: Validation fails

**Solution:**
```bash
# Check JSON syntax
python -m json.tool ai102_raw_data.json

# Common fixes:
# - Ensure percentage_weight format: "20-25%"
# - Check for missing required fields
# - Verify JSON structure matches schema
```

### Issue: Missing sub-skills

**Solution:**
1. Compare extracted count with manual count
2. Check if page structure changed
3. Manually add missing items to JSON
4. Re-run validation

### Issue: Database import fails

**Solution:**
```bash
# Check database connection
psql -h localhost -U username -d ai102 -c "SELECT 1;"

# Verify schema exists
psql -h localhost -U username -d ai102 -f setup_database.sql

# Check for foreign key violations
# Ensure validated_data.json has all IDs
```

## Performance Considerations

### Data Size

- JSON file: ~100-200 KB
- SQLite database: ~500 KB - 1 MB
- PostgreSQL/MySQL: Similar size

### Query Performance

- Indexed queries: < 10ms
- Full hierarchy views: < 50ms
- Complex analytics: < 100ms

### Scalability

- Single user: Any database type
- 10-100 users: SQLite or PostgreSQL
- 100+ users: PostgreSQL or MySQL
- 1000+ users: PostgreSQL with connection pooling

## Security Considerations

### Data Protection

- No PII in exam data
- User progress data should be encrypted
- Use environment variables for database credentials
- Implement proper authentication

### Database Security

```sql
-- Create read-only user
CREATE USER ai102_readonly WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai102_readonly;

-- Create app user with limited permissions
CREATE USER ai102_app WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON study_progress TO ai102_app;
GRANT SELECT ON topic_areas, skills, sub_skills TO ai102_app;
```

## Maintenance

### Updating for New Exam Versions

1. Re-run extraction when Microsoft updates exam
2. Compare with previous version using change_log
3. Update database with new content
4. Preserve user progress data
5. Notify users of changed content

### Backup Strategy

```bash
# PostgreSQL backup
pg_dump ai102 > ai102_backup_$(date +%Y%m%d).sql

# SQLite backup
sqlite3 ai102.db ".backup ai102_backup_$(date +%Y%m%d).db"

# JSON backup
cp validated_data.json validated_data_backup_$(date +%Y%m%d).json
```

## Next Steps

After setup:

1. **Verify Data Completeness**
   - Run `sample_queries.py` to test database
   - Check statistics.json for expected counts
   - Manually review key sub-skills

2. **Build Your Application**
   - Use validated_data.json for web apps
   - Query database for dynamic content
   - Implement gamification using annotation field

3. **Track Progress**
   - Populate study_progress table
   - Record quiz_results
   - Generate analytics

4. **Customize**
   - Add custom views
   - Create additional tables
   - Extend annotation schema

## Support & Documentation

- **Full Guide:** `EXTRACTION_GUIDE.md`
- **Database Schema:** `setup_database.sql`
- **Sample Queries:** `sample_queries.py`
- **Quick Start:** `quick_start.sh`

## License & Attribution

This toolkit is provided for educational purposes.

AI-102 exam content © Microsoft Corporation.

---

**Version:** 1.0
**Last Updated:** November 2025
**Compatible with:** AI-102 exam (April 2025 update)
