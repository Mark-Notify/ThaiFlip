param(
  [string]$Python = "python",
  [string]$Root = "..",
  [string]$AppDir = "..\app"
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path "$Root\.venv")) { & $Python -m venv "$Root\.venv" }
& "$Root\.venv\Scripts\pip" install --upgrade pip
& "$Root\.venv\Scripts\pip" install -r "$Root\requirements.txt"

& "$Root\.venv\Scripts\pyinstaller" --clean --noconfirm ".\thaiflip.spec"
Write-Host "Build done → dist\ThaiFlip\ThaiFlip.exe"
