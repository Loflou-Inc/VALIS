@echo off
ECHO Updating memory...

REM Try several common Python paths
SET PYTHON_PATHS=C:\Users\Caledonia333\anaconda3\python.exe;C:\Users\loflou\anaconda3\python.exe;C:\Python310\python.exe;C:\Python39\python.exe;C:\Users\loflou\AppData\Local\Programs\Python\Python310\python.exe

SET FOUND_PYTHON=0
SET PYTHON_EXE=

FOR %%p IN (%PYTHON_PATHS%) DO (
    IF EXIST "%%p" (
        SET PYTHON_EXE=%%p
        SET FOUND_PYTHON=1
        GOTO PYTHON_FOUND
    )
)

:PYTHON_FOUND

IF %FOUND_PYTHON% EQU 0 (
    ECHO Python not found in standard locations.
    ECHO Trying system Python...
    
    WHERE python > NUL 2>&1
    IF %ERRORLEVEL% EQU 0 (
        python F:\MEMORY_DEV\simple_update_memory.py %*
    ) ELSE (
        ECHO Python not found. Logging memory update to fallback file.
        ECHO %* >> F:\MEMORY_DEV\memory_store\memory_updates_fallback.txt
    )
) ELSE (
    "%PYTHON_EXE%" F:\MEMORY_DEV\simple_update_memory.py %*
)
