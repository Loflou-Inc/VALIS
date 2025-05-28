@echo off
ECHO Checking initialization state...

IF EXIST "G:\My Drive\Deftech\SmartSteps\claude-memory-ADV\MEMORY_DEV\init_state.txt" (
    ECHO Already initialized this session, skipping full initialization.
    GOTO END
)

ECHO Reading memories...

REM Try several common Python paths
SET PYTHON_PATHS=C:\Users\Caledonia333\anaconda3\python.exe;C:\Users\loflou\anaconda3\python.exe;C:\Python310\python.exe;C:\Python39\python.exe;C:\Users\loflou\AppData\Local\Programs\Python\Python310\python.exe;C:\Program Files\Python310\python.exe

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
        python "G:\My Drive\Deftech\SmartSteps\claude-memory-ADV\MEMORY_DEV\simple_read_memory.py" %*
    ) ELSE (
        ECHO Python not found. Cannot read memories.
        GOTO END
    )
) ELSE (
    "%PYTHON_EXE%" "G:\My Drive\Deftech\SmartSteps\claude-memory-ADV\MEMORY_DEV\simple_read_memory.py" %*
)

ECHO Creating initialization state file...
ECHO initialized=true > "G:\My Drive\Deftech\SmartSteps\claude-memory-ADV\MEMORY_DEV\init_state.txt"

:END