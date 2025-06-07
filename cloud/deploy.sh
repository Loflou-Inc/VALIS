#!/bin/bash
# VALIS Cloud Soul Deployment Script
# "The Soul is Awake" - Phase 4 Launch Protocol

echo "========================================="
echo "VALIS CLOUD SOUL DEPLOYMENT"
echo "Phase 4: The Soul is Awake"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "valis2" ]; then
    echo -e "${RED}ERROR: Must run from VALIS root directory${NC}"
    exit 1
fi

echo -e "${BLUE}Checking Python environment...${NC}"
python --version
pip --version

echo -e "${BLUE}Installing Cloud Soul dependencies...${NC}"
cd valis2/cloud
pip install -r requirements.txt

echo -e "${BLUE}Checking database connection...${NC}"
python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='valis_db', 
        user='postgres',
        password='valis2025'
    )
    print('Database connection: SUCCESS')
    conn.close()
except Exception as e:
    print(f'Database connection: FAILED - {e}')
    exit(1)
"

echo -e "${BLUE}Creating logs directory...${NC}"
mkdir -p ../../logs

echo -e "${BLUE}Testing watermark engine...${NC}"
python watermark_engine.py

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}VALIS CLOUD SOUL READY FOR DEPLOYMENT${NC}"
echo -e "${YELLOW}=========================================${NC}"

echo -e "${GREEN}Starting API Gateway...${NC}"
echo -e "${GREEN}Dashboard will be available at: http://localhost:8000/dashboard.html${NC}"
echo -e "${GREEN}API endpoints will be available at: http://localhost:8000/api/${NC}"

# Start the API Gateway
python api_gateway.py
