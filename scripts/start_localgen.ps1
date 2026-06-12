#Requires -Version 5.1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not $env:LOCALGEN_PORT) { $env:LOCALGEN_PORT = "8188" }
if (-not $env:LOCALGEN_BACKEND) { $env:LOCALGEN_BACKEND = "wan22-14b" }

Write-Host "LocalGen (2026) -> http://127.0.0.1:$($env:LOCALGEN_PORT)" -ForegroundColor Cyan
Write-Host "Backend: $($env:LOCALGEN_BACKEND)  (wan22-14b | wan22-5b | cogvideo-2b legacy)" -ForegroundColor DarkGray
Write-Host "Install: py -m pip install -e `".[localgen]`"" -ForegroundColor DarkGray
Write-Host "If WanPipeline missing: py -m pip install git+https://github.com/huggingface/diffusers" -ForegroundColor DarkGray
Write-Host ""

py -m videogen_mcp.localgen_server
