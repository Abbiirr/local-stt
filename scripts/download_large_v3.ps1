$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$modelDir = Join-Path $projectRoot "models\faster-whisper-large-v3"
New-Item -ItemType Directory -Path $modelDir -Force | Out-Null

$files = @(
  "config.json",
  "preprocessor_config.json",
  "tokenizer.json",
  "vocabulary.json"
)

foreach ($file in $files) {
  $url = "https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main/$file`?download=true"
  $target = Join-Path $modelDir $file
  curl.exe -L --fail --retry 3 --retry-delay 5 --output $target $url
}

$modelUrl = "https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main/model.bin?download=true"
$modelTarget = Join-Path $modelDir "model.bin"

$aria2 = Get-Command aria2c.exe -ErrorAction SilentlyContinue
if ($aria2) {
  & $aria2.Source -c -x 16 -s 16 -k 4M --file-allocation=none --dir=$modelDir --out=model.bin $modelUrl
} else {
  curl.exe -L --fail --retry 3 --retry-delay 5 --continue-at - --output $modelTarget $modelUrl
}

Write-Output "Downloaded large-v3 files to $modelDir"
