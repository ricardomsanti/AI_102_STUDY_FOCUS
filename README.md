# AI-102 Study Guide Extraction & Structuring Toolkit

Complete automated toolkit for extracting, structuring, and normalizing Microsoft AI-102 exam study guide content into machine-readable formats ready for database ingestion, advanced querying, and gamification.

## Overview

This project provides **three different methods** to extract and structure the complete AI-102 exam study guide into a comprehensive, normalized dataset:

1. **Browser Extraction** - JavaScript console script (recommended)
2. **HTML/PDF Parser** - Parse locally saved files
3. **Manual Input** - Structured JSON template

All methods produce identical output formats optimized for:
- Database ingestion (SQL, NoSQL)
- Study tracking applications
- Gamification engines
- Learning management systems
- Flashcard generators
- Progress tracking

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Method 1: Browser Extraction (Easiest)

1. Visit: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102
2. Open browser console (F12)
3. Run: `browser_extraction_script.js`
4. Save output to `ai102_raw_data.json`

### Method 2: HTML/PDF Parser

```bash
# Save the study guide page as HTML or PDF, then:
python html_pdf_parser.py study_guide.html
```

### Method 3: Manual Input

Edit `manual_input_template.json` with content from the study guide.

### Validate & Normalize

```bash
python validate_and_normalize.py ai102_raw_data.json
```

**Outputs:**
- `validated_data.json` - Normalized JSON with unique IDs
- `database_ready.csv` - Flattened for database import
- `change_log.csv` - Exam change history
- `statistics.json` - Dataset statistics

## Features

### Comprehensive Extraction
- ✅ All 6 topic areas with percentage weights
- ✅ All skills and sub-skills (200+ items)
- ✅ Reference documentation links
- ✅ Complete change log
- ✅ Exam metadata

### Structured Output
- ✅ Hierarchical JSON with unique IDs
- ✅ Normalized relational structure
- ✅ CSV exports for database import
- ✅ JSON schema validation
- ✅ Annotation fields for gamification

### Database Ready
- ✅ SQL-compatible schema
- ✅ PostgreSQL import scripts
- ✅ MongoDB compatible
- ✅ SQLite support
- ✅ Unique identifiers for all entities

## Data Structure

```json
{
  "metadata": {
    "exam_code": "AI-102",
    "exam_title": "Designing and Implementing a Microsoft Azure AI Solution",
    "extraction_date": "2025-11-23T...",
    "exam_update_date": "April 2025"
  },
  "topic_areas": [
    {
      "topic_id": "TOPIC-001",
      "topic_area": "Plan and manage an Azure AI solution",
      "percentage_weight": "20-25%",
      "skills": [
        {
          "skill_id": "SKILL-0001",
          "skill": "Select the appropriate Azure AI Foundry services",
          "sub_skills": [
            {
              "sub_skill_id": "SUBSKILL-00001",
              "sub_skill": "Select the appropriate service for a generative AI solution",
              "reference_links": ["https://..."],
              "annotation": ""
            }
          ]
        }
      ]
    }
  ],
  "change_log": [...]
}
```

## Files

| File | Purpose |
|------|---------|
| `browser_extraction_script.js` | Extract content directly from browser |
| `html_pdf_parser.py` | Parse saved HTML/PDF files |
| `validate_and_normalize.py` | Validate and normalize extracted data |
| `schema.json` | JSON schema for validation |
| `manual_input_template.json` | Template for manual entry |
| `requirements.txt` | Python dependencies |
| `EXTRACTION_GUIDE.md` | Complete documentation |

## Documentation

See **[EXTRACTION_GUIDE.md](EXTRACTION_GUIDE.md)** for:
- Detailed instructions for each method
- Database integration guides
- SQL schemas
- Troubleshooting
- Gamification setup
- Complete workflow diagrams

## Example Outputs

### Statistics
```
Total Topic Areas: 6
Total Skills: 24
Total Sub-Skills: 145
Total Reference Links: 87
```

### Topic Breakdown
```
Plan and manage an Azure AI solution (20-25%)
  Skills: 4
  Sub-skills: 23

Implement decision-support solutions (10-15%)
  Skills: 3
  Sub-skills: 18

[... and 4 more topic areas]
```

## Database Integration

### PostgreSQL
```sql
CREATE TABLE sub_skills (
    sub_skill_id VARCHAR(20) PRIMARY KEY,
    skill_id VARCHAR(20),
    topic_id VARCHAR(20),
    sub_skill TEXT NOT NULL,
    reference_links TEXT,
    annotation TEXT
);
```

### Import CSV
```bash
\copy sub_skills FROM 'database_ready.csv' CSV HEADER;
```

### MongoDB
```bash
mongoimport --db ai102 --collection study_guide --file validated_data.json
```

## Gamification Support

Each sub-skill includes an `annotation` field for tracking study progress:

```json
{
  "annotation": {
    "status": "completed|in_progress|not_started|mastered",
    "confidence_level": 4,
    "last_reviewed": "2025-11-20",
    "attempts": 3,
    "notes": "..."
  }
}
```

## Use Cases

- **Study Tracking Apps** - Monitor progress across all exam topics
- **Flashcard Generators** - Auto-generate flashcards from sub-skills
- **Quiz Engines** - Build practice tests weighted by topic percentage
- **Learning Analytics** - Track weak areas and study time
- **Spaced Repetition** - Schedule reviews based on mastery level
- **Team Training** - Track organization-wide certification progress

## Requirements

- Python 3.7+
- beautifulsoup4
- PyPDF2
- jsonschema

## License

This extraction toolkit is provided for educational purposes.

AI-102 exam content © Microsoft Corporation.

## Support

For detailed instructions, troubleshooting, and examples, see [EXTRACTION_GUIDE.md](EXTRACTION_GUIDE.md).
