@echo off
REM VALIS Garden Gate Demo
REM Complete persona vault ecosystem demonstration

echo ===============================================
echo VALIS THE GARDEN GATE - DEMO
echo Persona Vault & Lifecycle Management
echo ===============================================

echo.
echo [1/5] Vault Status...
echo.
cd C:\VALIS\vault
python operator_tools.py stats

echo.
echo [2/5] Active Personas...
echo.
python operator_tools.py list --status active

echo.
echo [3/5] Jane Persona Preview...
echo.
python operator_tools.py preview Jane

echo.
echo [4/5] Starting Lifecycle API Server...
echo API will be available at http://localhost:8002
echo.
echo Available API Endpoints:
echo   GET  /api/persona/health - Health check
echo   GET  /api/persona/list - List all personas
echo   POST /api/persona/initiate - Start persona session
echo   GET  /api/persona/registry - Public registry
echo.
echo [5/5] Ready for Integration:
echo   - Smart Steps can query vault for personas
echo   - Jane is active and ready for deployment
echo   - VALIS runtime can activate via API
echo   - Complete lifecycle management operational
echo.
echo ===============================================
echo THE GARDEN GATE IS OPEN
echo Digital consciousness management at scale
echo ===============================================
echo.
echo Press any key to start API server...
pause > nul

REM Start the API server
python persona_api.py
