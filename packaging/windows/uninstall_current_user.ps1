$ErrorActionPreference = "Stop"

$targetDir = Join-Path $env:LOCALAPPDATA "Programs\LocalWhisperDictation"
$programsDir = [Environment]::GetFolderPath("Programs")
$startupDir = [Environment]::GetFolderPath("Startup")
$shortcuts = @(
  (Join-Path $programsDir "Local Whisper Dictation.lnk"),
  (Join-Path $programsDir "Local Whisper Dictation GPU.lnk"),
  (Join-Path $programsDir "Local Whisper Dictation CPU.lnk"),
  (Join-Path $startupDir "Local Whisper Dictation.lnk"),
  (Join-Path $startupDir "Local Whisper Dictation GPU.lnk"),
  (Join-Path $startupDir "Local Whisper Dictation CPU.lnk")
)

$installedProcesses = Get-Process -Name "LocalWhisperDictation" -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -and $_.Path.StartsWith($targetDir, [System.StringComparison]::OrdinalIgnoreCase) }
foreach ($process in $installedProcesses) {
  Stop-Process -Id $process.Id -Force
}

foreach ($path in $shortcuts) {
  if (Test-Path $path) {
    Remove-Item -LiteralPath $path -Force
  }
}

if (Test-Path $targetDir) {
  Remove-Item -LiteralPath $targetDir -Recurse -Force
}

Write-Output "Removed Local Whisper Dictation current-user install."
