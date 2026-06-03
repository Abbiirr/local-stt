$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  throw "Missing .venv. Run install.bat first."
}

.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --windowed `
  --name LocalWhisperDictation `
  --paths src `
  --collect-data faster_whisper `
  app_launcher.py

.\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --console `
  --name LocalWhisperDictationConsole `
  --paths src `
  --collect-data faster_whisper `
  app_launcher.py

Write-Output "Built dist\LocalWhisperDictation\LocalWhisperDictation.exe"
Write-Output "Built dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe"
