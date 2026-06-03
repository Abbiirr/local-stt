$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runBat = Join-Path $projectRoot "run.bat"
$startup = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startup "Local Whisper Dictation.lnk"

if (-not (Test-Path $runBat)) {
  throw "run.bat not found at $runBat"
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $runBat
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 7
$shortcut.Description = "Start Local Whisper Dictation"
$shortcut.Save()

Write-Output "Created startup shortcut: $shortcutPath"
