$ErrorActionPreference = "Stop"

$targetDir = Join-Path $env:LOCALAPPDATA "Programs\LocalWhisperDictation"
$programsShortcut = Join-Path ([Environment]::GetFolderPath("Programs")) "Local Whisper Dictation.lnk"
$startupShortcut = Join-Path ([Environment]::GetFolderPath("Startup")) "Local Whisper Dictation.lnk"

$installedProcesses = Get-Process -Name "LocalWhisperDictation" -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -and $_.Path.StartsWith($targetDir, [System.StringComparison]::OrdinalIgnoreCase) }
foreach ($process in $installedProcesses) {
  Stop-Process -Id $process.Id -Force
}

foreach ($path in @($programsShortcut, $startupShortcut)) {
  if (Test-Path $path) {
    Remove-Item -LiteralPath $path -Force
  }
}

if (Test-Path $targetDir) {
  Remove-Item -LiteralPath $targetDir -Recurse -Force
}

Write-Output "Removed Local Whisper Dictation current-user install."
