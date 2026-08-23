@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ====================================================
echo  Caricamento progetto SnakeGame su GitHub...
echo ====================================================
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================
    echo  COMPLETATO! File caricati con successo su GitHub.
    echo ====================================================
) else (
    echo.
    echo [ERRORE] Il caricamento su GitHub non e andato a buon fine.
)

echo.
pause
