@echo off
REM VALIS SYSTEM STATUS CHECKER
REM Check what's currently running before starting new instances

echo ================================================================
echo VALIS SYSTEM STATUS CHECK
echo Checking all known services to avoid duplicate instances
echo ================================================================

echo.
echo [CHECKING MAIN VALIS SERVICES]
echo.

REM Test Main VALIS Server (port 3001)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3001/api/health' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[RUNNING] Main VALIS Server: port 3001' } catch { Write-Host '[STOPPED] Main VALIS Server: port 3001' }"

REM Test Mr. Fission (port 8001)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/fission/health' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[RUNNING] Mr. Fission: port 8001' } catch { Write-Host '[STOPPED] Mr. Fission: port 8001' }"

REM Test Garden Gate (port 8002)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8002/api/persona/health' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[RUNNING] Garden Gate: port 8002' } catch { Write-Host '[STOPPED] Garden Gate: port 8002' }"

REM Test Cloud Soul (port 8000)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[RUNNING] Cloud Soul: port 8000' } catch { Write-Host '[STOPPED] Cloud Soul: port 8000' }"

REM Test Local LLM (port 8080)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/health' -TimeoutSec 2 -ErrorAction Stop; Write-Host '[RUNNING] Local LLM (Mistral): port 8080' } catch { Write-Host '[STOPPED] Local LLM (Mistral): port 8080' }"

echo.
echo [CHECKING FOR PYTHON PROCESSES]
echo.

REM Check for Python processes that might be VALIS-related
tasklist /FI "IMAGENAME eq python.exe" 2>nul | findstr "python.exe"
if errorlevel 1 (
    echo [INFO] No python.exe processes found
) else (
    echo [FOUND] Python processes detected - may include VALIS services
)

echo.
echo [CHECKING FOR CMD WINDOWS]
echo.

REM Check for command prompt windows (our services run in cmd windows)
tasklist /FI "IMAGENAME eq cmd.exe" 2>nul | findstr "cmd.exe"
if errorlevel 1 (
    echo [INFO] No cmd.exe processes found
) else (
    echo [FOUND] Command prompt windows detected - may include VALIS services
)

echo.
echo ================================================================
echo STATUS SUMMARY
echo ================================================================
echo.
echo If you see [RUNNING] services above, they're already active.
echo If you see [STOPPED] services, they need to be started.
echo.
echo SAFE TO RUN STARTUP: Only if ALL services show [STOPPED]
echo.
echo ================================================================

pause
