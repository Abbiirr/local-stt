$ErrorActionPreference = "Stop"

$startup = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startup "Local Whisper Dictation.lnk"

if (Test-Path $shortcutPath) {
  Remove-Item -LiteralPath $shortcutPath -Force
  Write-Output "Removed startup shortcut: $shortcutPath"
} else {
  Write-Output "Startup shortcut was not present: $shortcutPath"
}
