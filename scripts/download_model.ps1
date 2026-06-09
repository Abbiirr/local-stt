param(
  [Parameter(Mandatory = $true)]
  [string]$ModelName,
  [string]$Repository = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $Repository) {
  $Repository = "Systran/faster-whisper-$ModelName"
}

$modelDir = Join-Path $projectRoot "models\faster-whisper-$ModelName"
New-Item -ItemType Directory -Path $modelDir -Force | Out-Null

$files = @(
  "config.json",
  "preprocessor_config.json",
  "tokenizer.json",
  "vocabulary.json",
  "model.bin"
)

foreach ($file in $files) {
  $url = "https://huggingface.co/$Repository/resolve/main/$file`?download=true"
  $target = Join-Path $modelDir $file
  curl.exe -L --fail --retry 3 --retry-delay 5 --continue-at - --output $target $url
}

Write-Output "Downloaded $Repository files to $modelDir"
