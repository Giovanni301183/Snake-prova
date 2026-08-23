@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Snake Game - Edizione Tkinter Standalone

REM Trova il comando Python utilizzabile (py o python o python3)
set PYTHON_CMD=
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
    ) else (
        where python3 >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=python3
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERRORE] Python non e stato trovato nel sistema!
    echo Assicurati di aver installato Python da python.org o dal Microsoft Store.
    echo.
    pause
    exit /b 1
)

%PYTHON_CMD% snake_tkinter.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRORE] Impossibile avviare la versione Tkinter.
    pause
)

