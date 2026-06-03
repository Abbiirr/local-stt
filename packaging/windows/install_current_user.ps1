param(
  [switch]$StartWithWindows
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$sourceDir = Join-Path $projectRoot "dist\LocalWhisperDictation"
$targetDir = Join-Path $env:LOCALAPPDATA "Programs\LocalWhisperDictation"
$exePath = Join-Path $targetDir "LocalWhisperDictation.exe"

if (-not (Test-Path $sourceDir)) {
  throw "Missing $sourceDir. Run packaging\windows\build.ps1 first."
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

$shell = New-Object -ComObject WScript.Shell
$programsDir = [Environment]::GetFolderPath("Programs")
$shortcutPath = Join-Path $programsDir "Local Whisper Dictation.lnk"
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $targetDir
$shortcut.Description = "Local Whisper Dictation"
$shortcut.Save()

if ($StartWithWindows) {
  $startupDir = [Environment]::GetFolderPath("Startup")
  $startupShortcutPath = Join-Path $startupDir "Local Whisper Dictation.lnk"
  $startupShortcut = $shell.CreateShortcut($startupShortcutPath)
  $startupShortcut.TargetPath = $exePath
  $startupShortcut.WorkingDirectory = $targetDir
  $startupShortcut.Description = "Local Whisper Dictation"
  $startupShortcut.Save()
}

Write-Output "Installed to $targetDir"
Write-Output "Created Start Menu shortcut: $shortcutPath"
if ($StartWithWindows) {
  Write-Output "Created Startup shortcut."
}
