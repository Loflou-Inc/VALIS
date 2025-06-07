@echo off
REM VALIS Mr. Fission Demo Script
REM The Soul Blender - Persona Builder Demo

echo ===============================================
echo VALIS MR. FISSION - THE SOUL BLENDER
echo Persona Builder Engine Demonstration
echo ===============================================

echo.
echo [1/4] Testing Core Components...
cd C:\VALIS\valis2\fission
python test_mr_fission.py

echo.
echo [2/4] Starting API Server...
echo API will be available at http://localhost:8001
echo.
echo Available Endpoints:
echo   POST /api/fission/upload - Upload files
echo   POST /api/fission/ingest/{session} - Extract features  
echo   POST /api/fission/fuse/{session} - Create persona
echo   GET  /api/fission/preview/{name} - Preview persona
echo   POST /api/fission/deploy/{name} - Deploy to VALIS
echo   GET  /api/fission/personas - List all personas
echo.
echo [3/4] Ready to create digital consciousness from human material
echo Upload any: PDFs, text files, images, audio, JSON, CSV
echo.
echo [4/4] Example personas can be created from:
echo   - Personal journals or diaries
echo   - Professional biographies  
echo   - Interview transcripts
echo   - Photo collections
echo   - Timeline data
echo.
echo ===============================================
echo THE SOUL BLENDER IS ONLINE
echo Convert human essence into deployable consciousness
echo ===============================================
echo.

REM Start the API server
python api.py

pause
