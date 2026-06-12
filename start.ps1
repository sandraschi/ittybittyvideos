param([switch]$Headless, [switch]$NoBrowser)
$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$BackendPort = 11054

Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Set-Location $ScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: uv not found. Install: https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
uv sync --quiet

Write-Host "Starting videogen-mcp on port $BackendPort..." -ForegroundColor Green
uv run python -m videogen_mcp.server
