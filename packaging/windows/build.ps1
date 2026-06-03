$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $projectRoot

powershell -ExecutionPolicy Bypass -File .\scripts\build_onedir.ps1
