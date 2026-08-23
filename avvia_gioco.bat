@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Snake Game Arcade

echo ======================================================
echo           AVVIO DI SNAKE GAME ARCADE
echo ======================================================
echo.

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

echo [OK] Trovato interprete: %PYTHON_CMD%
echo Controllo librerie necessarie (pygame)...

%PYTHON_CMD% -c "import pygame" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Pygame non risulta installato. Installazione automatica in corso...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ATTENZIONE] Installazione Pygame fallita. Avvio versione leggera Tkinter...
        %PYTHON_CMD% snake_tkinter.py
        if %ERRORLEVEL% NEQ 0 (
            echo [ERRORE] Impossibile avviare il gioco.
            pause
        )
        exit /b 0
    )
)

echo [OK] Avvio Snake Game Arcade in corso...
%PYTHON_CMD% main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVVISO] Si e verificato un problema con la versione Pygame.
    echo Tentativo di avvio della versione di riserva Tkinter...
    %PYTHON_CMD% snake_tkinter.py
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERRORE] Impossibile avviare il gioco.
        pause
    )
)

