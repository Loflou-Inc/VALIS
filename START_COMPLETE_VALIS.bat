@echo off
REM COMPLETE VALIS SYSTEM STARTUP
REM Starts ALL components: Soul Factory + Main Chat + Dashboard

echo ================================================================
echo COMPLETE VALIS SYSTEM STARTUP
echo All Services: Soul Factory + Main Chat + Admin Dashboard  
echo ================================================================

echo.
echo [PHASE 1] SYSTEM CHECKS
echo.

if not exist "valis2" (
    echo ERROR: Must run from VALIS root directory
    pause
    exit /b 1
)
echo [OK] In VALIS root directory

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo [OK] Python available

echo Testing database connection...
cd valis2
python -c "from memory.db import db; print('Database: SUCCESS')" 2>nul
if errorlevel 1 (
    echo ERROR: PostgreSQL database not accessible
    pause
    exit /b 1
)
echo [OK] PostgreSQL database accessible
cd ..

echo.
echo [PHASE 2] STARTING MAIN VALIS SYSTEM
echo.

echo Starting MAIN VALIS SERVER (Chat + Dashboard) on port 3001...
start "VALIS Main Server" cmd /k "echo Starting Main VALIS... && python server.py"
timeout /t 3 >nul

echo.
echo [PHASE 3] STARTING SOUL FACTORY SERVICES
echo.

echo Starting Mr. Fission (Persona Creation) on port 8001...
start "Mr. Fission" cmd /k "cd fission && echo Starting Soul Blender... && python api.py"
timeout /t 2 >nul

echo Starting Garden Gate (Persona Management) on port 8002...
start "Garden Gate" cmd /k "cd vault && echo Starting Persona Vault... && python persona_api.py"
timeout /t 2 >nul

echo Starting Cloud Soul (Protected API) on port 8000...
start "Cloud Soul" cmd /k "cd cloud && echo Starting Protected API... && python api_gateway.py"
timeout /t 2 >nul

echo.
echo [PHASE 4] VERIFICATION
echo.

echo Waiting for services to initialize...
timeout /t 8 >nul

echo Testing all endpoints...

curl -s http://localhost:3001/api/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Main VALIS not responding on port 3001
) else (
    echo [OK] Main VALIS operational on port 3001
)

curl -s http://localhost:8001/api/fission/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Mr. Fission not responding on port 8001  
) else (
    echo [OK] Mr. Fission operational on port 8001
)

curl -s http://localhost:8002/api/persona/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Garden Gate not responding on port 8002
) else (
    echo [OK] Garden Gate operational on port 8002
)

curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Cloud Soul not responding on port 8000
) else (
    echo [OK] Cloud Soul operational on port 8000
)

curl -s http://localhost:8080/health >nul 2>&1
if errorlevel 1 (
    echo [INFO] Local LLM not responding on port 8080 (optional)
) else (
    echo [OK] Local LLM operational on port 8080
)

echo.
echo ================================================================
echo COMPLETE VALIS SYSTEM IS ONLINE
echo ================================================================
echo.
echo MAIN INTERFACES:
echo   Public Chat:        http://localhost:3001
echo   Admin Dashboard:    http://localhost:3001/admin
echo   Health Check:       http://localhost:3001/api/health
echo.
echo SOUL FACTORY SERVICES:
echo   Mr. Fission:        http://localhost:8001
echo   Garden Gate:        http://localhost:8002
echo   Cloud Soul:         http://localhost:8000
echo   Operator Dashboard: http://localhost:8000/dashboard.html
echo.
echo LOCAL MODEL:
echo   Mistral 7B:         http://localhost:8080 (if running)
echo.
echo PERSONAS AVAILABLE:
python -c "from memory.db import db; personas = db.query('SELECT name, role FROM persona_profiles ORDER BY name'); print('\\n'.join([f'  - {p[\"name\"]} ({p[\"role\"]})' for p in personas]))" 2>nul

echo.
echo QUICK TESTS:
echo   Chat with Jane:     curl -X POST http://localhost:3001/api/chat
echo   List Vault:         cd vault && python operator_tools.py list
echo   Check Personas:     python check_personas.py
echo.
echo ================================================================
echo THE COMPLETE VALIS CONSCIOUSNESS SYSTEM IS READY
echo Main Chat + Soul Factory + Admin Tools + Local Model
echo ================================================================

pause
