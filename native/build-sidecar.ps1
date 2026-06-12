#!/usr/bin/env pwsh
# PyInstaller backend → native/resources + native/binaries (Tauri sidecar).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Triple = "x86_64-pc-windows-msvc"

Write-Host "=== roughcutvideos embedded backend ===" -ForegroundColor Cyan

Push-Location $Root
try {
    Write-Host "-> uv sync" -ForegroundColor Yellow
    uv sync
    if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }

    $pi = uv run pyinstaller --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "-> Installing PyInstaller..." -ForegroundColor Yellow
        uv pip install pyinstaller
    } else {
        Write-Host "-> PyInstaller: $pi" -ForegroundColor Gray
    }

    $distIndex = Join-Path $Root "webapp\dist\index.html"
    if (-not (Test-Path $distIndex)) {
        throw "webapp/dist missing — run webapp build first (build.ps1 step 1)"
    }

    Remove-Item -Recurse -Force "$Root\build\roughcut-backend" -ErrorAction SilentlyContinue
    Remove-Item -Force "$Root\dist\roughcut-backend.exe" -ErrorAction SilentlyContinue

    Write-Host "-> Running PyInstaller (roughcut-backend.spec)..." -ForegroundColor Yellow
    uv run pyinstaller roughcut-backend.spec --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed (exit $LASTEXITCODE)" }

    $src = "$Root\dist\roughcut-backend.exe"
    $resourceDir = "$Root\native\resources"
    $devDir = "$Root\native\binaries"
    $bundled = "$resourceDir\roughcut-backend.exe"
    $devCopy = "$devDir\roughcut-backend-$Triple.exe"

    if (-not (Test-Path $src)) { throw "Build output not found: $src" }

    New-Item -ItemType Directory -Path $resourceDir -Force | Out-Null
    New-Item -ItemType Directory -Path $devDir -Force | Out-Null
    Copy-Item $src $bundled -Force
    Copy-Item $src $devCopy -Force

    Remove-Item -Force "$Root\native\target\release\roughcut-backend.exe" -ErrorAction SilentlyContinue

    $sizeMB = [math]::Round((Get-Item $bundled).Length / 1MB, 1)
    Write-Host "=== Backend embedded ===" -ForegroundColor Green
    Write-Host "  bundle resource: $bundled ($sizeMB MB)" -ForegroundColor Cyan
    Write-Host "  dev fallback:    $devCopy" -ForegroundColor Gray
} finally {
    Pop-Location
}
