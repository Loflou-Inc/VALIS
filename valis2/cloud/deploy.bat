@echo off
REM VALIS Cloud Soul Deployment Script (Windows)
REM "The Soul is Awake" - Phase 4 Launch Protocol

echo =========================================
echo VALIS CLOUD SOUL DEPLOYMENT
echo Phase 4: The Soul is Awake
echo =========================================

REM Check if we're in the right directory
if not exist "valis2" (
    echo ERROR: Must run from VALIS root directory
    exit /b 1
)

echo Checking Python environment...
python --version
pip --version

echo Installing Cloud Soul dependencies...
cd valis2\cloud
pip install -r requirements.txt

echo Checking database connection...
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='valis_db', user='postgres', password='valis2025'); print('Database connection: SUCCESS'); conn.close()"

echo Creating logs directory...
mkdir ..\..\logs 2>nul

echo Testing watermark engine...
python watermark_engine.py

echo =========================================
echo VALIS CLOUD SOUL READY FOR DEPLOYMENT
echo =========================================

echo Starting API Gateway...
echo Dashboard will be available at: http://localhost:8000/dashboard.html
echo API endpoints will be available at: http://localhost:8000/api/

REM Start the API Gateway
python api_gateway.py

pause
