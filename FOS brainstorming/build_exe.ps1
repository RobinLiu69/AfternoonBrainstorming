$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$python = Join-Path $root "..\.venv\Scripts\python.exe"
$icon = Join-Path $root "assets\icon.ico"
$dist = Join-Path $root "dist\AfternoonBrainstorming"

if (-not (Test-Path $python)) { throw "Python venv not found at $python" }
if (-not (Test-Path $icon))   { throw "icon.ico not found at $icon" }

function Remove-WithRetry($path) {
    if (-not (Test-Path $path)) { return }
    for ($i = 1; $i -le 5; $i++) {
        try { Remove-Item -Recurse -Force $path; return }
        catch {
            Write-Host "  '$path' locked, retrying ($i/5)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    throw "Could not remove '$path' (file locked). Close the game / antivirus and retry."
}

Push-Location $root
try {
    Write-Host "[1/4] Stopping any running AfternoonBrainstorming.exe..." -ForegroundColor Cyan
    Get-Process -Name AfternoonBrainstorming -ErrorAction SilentlyContinue | Stop-Process -Force

    Write-Host "[2/4] Cleaning old build/dist..." -ForegroundColor Cyan
    Remove-WithRetry (Join-Path $root "build\AfternoonBrainstorming")
    Remove-WithRetry $dist

    Write-Host "[3/4] Building exe with PyInstaller..." -ForegroundColor Cyan
    & $python -m PyInstaller --noconfirm --onedir --windowed --name AfternoonBrainstorming --icon $icon main.py

    Write-Host "[4/4] Copying config, fonts and assets next to the exe..." -ForegroundColor Cyan
    Copy-Item -Recurse -Force (Join-Path $root "config") $dist
    Copy-Item -Recurse -Force (Join-Path $root "fonts") $dist
    Copy-Item -Recurse -Force (Join-Path $root "assets") $dist

    Write-Host "Done. Output folder:" -ForegroundColor Green
    Write-Host "  $dist"
}
finally {
    Pop-Location
}
