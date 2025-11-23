#!/bin/bash
# AI-102 Study Guide Extraction - Quick Start Script

set -e  # Exit on error

echo "======================================"
echo "AI-102 Study Guide Extraction Toolkit"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Install dependencies
echo ""
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Interactive menu
echo ""
echo "======================================"
echo "Choose extraction method:"
echo "======================================"
echo "1. Browser Extraction (Recommended)"
echo "2. HTML/PDF Parser"
echo "3. Manual Input"
echo "4. Skip extraction (I already have data)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}=== BROWSER EXTRACTION METHOD ===${NC}"
        echo ""
        echo "Follow these steps:"
        echo "1. Open: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102"
        echo "2. Open browser Developer Tools (F12)"
        echo "3. Go to Console tab"
        echo "4. Copy contents of: browser_extraction_script.js"
        echo "5. Paste into console and press Enter"
        echo "6. Save the downloaded file as: ai102_raw_data.json"
        echo ""
        read -p "Press Enter when you have saved ai102_raw_data.json..."

        if [ ! -f "ai102_raw_data.json" ]; then
            echo -e "${RED}ERROR: ai102_raw_data.json not found${NC}"
            echo "Please save the file and run this script again"
            exit 1
        fi

        INPUT_FILE="ai102_raw_data.json"
        ;;

    2)
        echo ""
        echo -e "${YELLOW}=== HTML/PDF PARSER METHOD ===${NC}"
        echo ""
        echo "First, save the study guide page:"
        echo "  Browser: File > Save As > Webpage, Complete"
        echo "  Or: Print to PDF"
        echo ""
        read -p "Enter path to HTML or PDF file: " file_path

        if [ ! -f "$file_path" ]; then
            echo -e "${RED}ERROR: File not found: $file_path${NC}"
            exit 1
        fi

        echo ""
        echo -e "${BLUE}Parsing $file_path...${NC}"
        python3 html_pdf_parser.py "$file_path"

        INPUT_FILE="ai102_structured_data.json"
        ;;

    3)
        echo ""
        echo -e "${YELLOW}=== MANUAL INPUT METHOD ===${NC}"
        echo ""
        echo "Edit the file: manual_input_template.json"
        echo "Fill in all skills and sub-skills from the study guide"
        echo ""
        read -p "Press Enter when you've completed the template..."

        INPUT_FILE="manual_input_template.json"

        if [ ! -f "$INPUT_FILE" ]; then
            echo -e "${RED}ERROR: $INPUT_FILE not found${NC}"
            exit 1
        fi
        ;;

    4)
        echo ""
        read -p "Enter path to your JSON data file: " INPUT_FILE

        if [ ! -f "$INPUT_FILE" ]; then
            echo -e "${RED}ERROR: File not found: $INPUT_FILE${NC}"
            exit 1
        fi
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Validate and normalize
echo ""
echo -e "${BLUE}Validating and normalizing data...${NC}"
python3 validate_and_normalize.py "$INPUT_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Data validated and normalized successfully!${NC}"
else
    echo -e "${RED}ERROR: Validation failed${NC}"
    exit 1
fi

# Database import
echo ""
echo "======================================"
echo "Database Import (Optional)"
echo "======================================"
echo "1. PostgreSQL"
echo "2. MySQL"
echo "3. SQLite"
echo "4. Skip database import"
echo ""
read -p "Enter choice [1-4]: " db_choice

case $db_choice in
    1)
        read -p "PostgreSQL host [localhost]: " PG_HOST
        PG_HOST=${PG_HOST:-localhost}

        read -p "PostgreSQL user: " PG_USER
        read -sp "PostgreSQL password: " PG_PASS
        echo ""
        read -p "Database name [ai102]: " PG_DB
        PG_DB=${PG_DB:-ai102}

        echo ""
        echo -e "${BLUE}Setting up PostgreSQL database...${NC}"
        PGPASSWORD=$PG_PASS psql -h $PG_HOST -U $PG_USER -d postgres -c "CREATE DATABASE $PG_DB;" 2>/dev/null || true
        PGPASSWORD=$PG_PASS psql -h $PG_HOST -U $PG_USER -d $PG_DB -f setup_database.sql

        echo ""
        echo -e "${BLUE}Importing data to PostgreSQL...${NC}"
        python3 import_to_database.py validated_data.json --db postgres \
            --host $PG_HOST --user $PG_USER --password $PG_PASS --database $PG_DB
        ;;

    2)
        read -p "MySQL host [localhost]: " MY_HOST
        MY_HOST=${MY_HOST:-localhost}

        read -p "MySQL user: " MY_USER
        read -sp "MySQL password: " MY_PASS
        echo ""
        read -p "Database name [ai102]: " MY_DB
        MY_DB=${MY_DB:-ai102}

        echo ""
        echo -e "${BLUE}Importing data to MySQL...${NC}"
        python3 import_to_database.py validated_data.json --db mysql \
            --host $MY_HOST --user $MY_USER --password $MY_PASS --database $MY_DB
        ;;

    3)
        read -p "SQLite database file [ai102.db]: " SQLITE_DB
        SQLITE_DB=${SQLITE_DB:-ai102.db}

        echo ""
        echo -e "${BLUE}Importing data to SQLite...${NC}"
        python3 import_to_database.py validated_data.json --db sqlite --database $SQLITE_DB
        ;;

    4)
        echo "Skipping database import"
        ;;
esac

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Generated files:"
echo "  • validated_data.json - Normalized JSON data"
echo "  • database_ready.csv - CSV for database import"
echo "  • change_log.csv - Change log data"
echo "  • statistics.json - Dataset statistics"
echo ""
echo "Next steps:"
echo "  • Review statistics.json for dataset overview"
echo "  • Use validated_data.json in your application"
echo "  • Query database for study tracking"
echo ""
echo "Documentation: See EXTRACTION_GUIDE.md"
echo ""
