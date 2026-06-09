param(
  [ValidateSet("gpu", "cpu")]
  [string]$Edition = "gpu",
  [switch]$StartWithWindows
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$sourceDir = Join-Path $projectRoot "dist\LocalWhisperDictation"
$targetDir = Join-Path $env:LOCALAPPDATA "Programs\LocalWhisperDictation"
$exePath = Join-Path $targetDir "LocalWhisperDictation.exe"
$launcherPath = Join-Path $targetDir "Run Local Whisper Dictation.bat"
$profile = if ($Edition -eq "cpu") { "cpu-small-en.json" } else { "gpu-large-v3.json" }
$profilePath = Join-Path $projectRoot "packaging\profiles\$profile"

if (-not (Test-Path $sourceDir)) {
  throw "Missing $sourceDir. Run packaging\windows\build.ps1 first."
}
if (-not (Test-Path $profilePath)) {
  throw "Missing profile $profilePath."
}

$installedProcesses = Get-Process -Name "LocalWhisperDictation" -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -and $_.Path.StartsWith($targetDir, [System.StringComparison]::OrdinalIgnoreCase) }
foreach ($process in $installedProcesses) {
  Stop-Process -Id $process.Id -Force
}

if (Test-Path $targetDir) {
  Remove-Item -LiteralPath $targetDir -Recurse -Force
}

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
Copy-Item -Path (Join-Path $sourceDir "*") -Destination $targetDir -Recurse -Force
Copy-Item -LiteralPath $profilePath -Destination (Join-Path $targetDir "settings.json") -Force
@"
@echo off
set "LOCAL_DICTATION_CONFIG=%~dp0settings.json"
start "" "%~dp0LocalWhisperDictation.exe"
"@ | Set-Content -Path $launcherPath -Encoding ASCII

$shell = New-Object -ComObject WScript.Shell
$programsDir = [Environment]::GetFolderPath("Programs")
$shortcutName = if ($Edition -eq "cpu") { "Local Whisper Dictation CPU.lnk" } else { "Local Whisper Dictation GPU.lnk" }
$shortcutPath = Join-Path $programsDir $shortcutName
foreach ($oldShortcut in @(
  (Join-Path $programsDir "Local Whisper Dictation.lnk"),
  (Join-Path $programsDir "Local Whisper Dictation GPU.lnk"),
  (Join-Path $programsDir "Local Whisper Dictation CPU.lnk")
)) {
  if (Test-Path $oldShortcut) {
    Remove-Item -LiteralPath $oldShortcut -Force
  }
}
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcherPath
$shortcut.WorkingDirectory = $targetDir
$shortcut.Description = "Local Whisper Dictation ($Edition)"
$shortcut.Save()

if ($StartWithWindows) {
  $startupDir = [Environment]::GetFolderPath("Startup")
  $startupShortcutPath = Join-Path $startupDir $shortcutName
  $startupShortcut = $shell.CreateShortcut($startupShortcutPath)
  $startupShortcut.TargetPath = $launcherPath
  $startupShortcut.WorkingDirectory = $targetDir
  $startupShortcut.Description = "Local Whisper Dictation ($Edition)"
  $startupShortcut.Save()
}

Write-Output "Installed to $targetDir"
Write-Output "Installed $Edition profile settings."
Write-Output "Created Start Menu shortcut: $shortcutPath"
if ($StartWithWindows) {
  Write-Output "Created Startup shortcut."
}
