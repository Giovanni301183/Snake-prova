# Script PowerShell per avviare Snake Game Arcade
$location = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $location

Write-Host "Avvio Snake Game Arcade in corso..." -ForegroundColor Cyan

$pyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py"
    $pyArgs = @("-3", "main.py")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
    $pyArgs = @("main.py")
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pyCmd = "python3"
    $pyArgs = @("main.py")
} else {
    Write-Host "[ERRORE] Python non trovato!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire..."
    exit 1
}

& $pyCmd $pyArgs
