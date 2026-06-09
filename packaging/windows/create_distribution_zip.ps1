param(
  [ValidateSet("gpu", "cpu")]
  [string]$Edition = "gpu",
  [switch]$IncludeModel
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$sourceDir = Join-Path $projectRoot "dist\LocalWhisperDictation"
$releaseRoot = Join-Path $projectRoot "dist\releases"
$editionName = if ($Edition -eq "cpu") { "LocalWhisperDictation-cpu" } else { "LocalWhisperDictation-gpu" }
$editionDir = Join-Path $releaseRoot $editionName
$zipPath = Join-Path $releaseRoot "$editionName.zip"
$profile = if ($Edition -eq "cpu") { "cpu-small-en.json" } else { "gpu-large-v3.json" }
$profilePath = Join-Path $projectRoot "packaging\profiles\$profile"

if (-not (Test-Path $sourceDir)) {
  throw "Missing $sourceDir. Run packaging\windows\build.ps1 first."
}
if (-not (Test-Path $profilePath)) {
  throw "Missing profile $profilePath."
}

if (Test-Path $editionDir) {
  Remove-Item -LiteralPath $editionDir -Recurse -Force
}
if (Test-Path $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

New-Item -ItemType Directory -Path $editionDir -Force | Out-Null
Copy-Item -Path (Join-Path $sourceDir "*") -Destination $editionDir -Recurse -Force
Copy-Item -LiteralPath $profilePath -Destination (Join-Path $editionDir "settings.json") -Force

$launcherPath = Join-Path $editionDir "Run Local Whisper Dictation.bat"
@"
@echo off
set "LOCAL_DICTATION_CONFIG=%~dp0settings.json"
start "" "%~dp0LocalWhisperDictation.exe"
"@ | Set-Content -Path $launcherPath -Encoding ASCII

if ($IncludeModel) {
  $settings = Get-Content $profilePath -Raw | ConvertFrom-Json
  $modelSource = Join-Path $projectRoot ("models\faster-whisper-" + $settings.model_name)
  $modelTarget = Join-Path $editionDir ("models\faster-whisper-" + $settings.model_name)
  if (-not (Test-Path $modelSource)) {
    throw "Missing local model $modelSource. Download it first or omit -IncludeModel."
  }
  New-Item -ItemType Directory -Path (Split-Path $modelTarget -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $modelSource -Destination $modelTarget -Recurse -Force
}

Compress-Archive -Path $editionDir -DestinationPath $zipPath -Force
Write-Output "Created $zipPath"
