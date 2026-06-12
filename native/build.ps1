#!/usr/bin/env pwsh
# Full release: webapp (Tauri API base) → PyInstaller sidecar → NSIS installer.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Native = $PSScriptRoot
$Port = 11054
$Version = (Select-String -Path "$Root\pyproject.toml" -Pattern '^version = "(.+)"' | ForEach-Object { $_.Matches.Groups[1].Value })

Write-Host "==> roughcutvideos native build v$Version" -ForegroundColor Cyan
Write-Host ""

Get-Process -Name "roughcut-backend","roughcut-native" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[1/5] Building webapp (VITE_API_BASE=http://127.0.0.1:$Port)..." -ForegroundColor Green
Push-Location "$Root\webapp"
try {
    $env:VITE_API_BASE = "http://127.0.0.1:$Port"
    if (-not (Test-Path "node_modules\.bin\tsc.cmd")) {
        Write-Host "    npm install (node_modules incomplete)" -ForegroundColor Gray
        npm install --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw "npm install failed (exit $LASTEXITCODE)" }
    }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
    Remove-Item Env:VITE_API_BASE -ErrorAction SilentlyContinue
}
$distIndex = Join-Path $Root "webapp\dist\index.html"
if (-not (Test-Path $distIndex)) {
    Write-Host "ERROR: webapp build failed — missing $distIndex" -ForegroundColor Red
    exit 1
}

Write-Host "[2/5] Freezing Python backend..." -ForegroundColor Green
pwsh -NoLogo -File "$Native\build-sidecar.ps1"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[3/5] Smoke test frozen backend..." -ForegroundColor Green
$backendExe = Join-Path $Root "dist\roughcut-backend.exe"
$env:VIDEOGEN_PORT = "$Port"
$env:VIDEOGEN_TAURI = "1"
$p = Start-Process -FilePath $backendExe -PassThru -WindowStyle Hidden
try {
    $ready = $false
    for ($i = 0; $i -lt 45; $i++) {
        try {
            $h = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 3
            if ($h.StatusCode -eq 200) { $ready = $true; break }
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $ready) { throw "Backend /health did not respond within 45s" }
    $null = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/v1/providers" -UseBasicParsing -TimeoutSec 15
    Write-Host "    Smoke OK: /health + /api/v1/providers" -ForegroundColor Gray
} finally {
    if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    Get-Process -Name "roughcut-backend" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Remove-Item Env:VIDEOGEN_TAURI -ErrorAction SilentlyContinue
}

Write-Host "[4/5] Building Tauri NSIS installer..." -ForegroundColor Green
Push-Location $Native
try {
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx --yes @tauri-apps/cli build
    if ($LASTEXITCODE -ne 0) { throw "tauri build failed (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
}

Remove-Item -Force "$Native\target\release\roughcut-backend.exe" -ErrorAction SilentlyContinue

Write-Host "[5/5] Staging release asset..." -ForegroundColor Green
$installers = @(Get-ChildItem "$Native\target\release\bundle\nsis\*-setup.exe" -ErrorAction SilentlyContinue)
if ($installers.Count -eq 0) {
    Write-Host "ERROR: NSIS installer not found under native/target/release/bundle/nsis/" -ForegroundColor Red
    exit 1
}
$installer = $installers | Where-Object { $_.Name -like "*$Version*" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $installer) {
    $installer = $installers | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Write-Host "    WARN: no NSIS bundle matched v$Version; using newest: $($installer.Name)" -ForegroundColor Yellow
}

$releaseDir = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$releaseName = "roughcutvideos-$Version-x64-setup.exe"
$releasePath = Join-Path $releaseDir $releaseName
Copy-Item -Force $installer.FullName $releasePath

Write-Host ""
Write-Host "==> SHIP THIS (single-file NSIS):" -ForegroundColor Green
Write-Host "    $releasePath" -ForegroundColor White
Write-Host "    Size: $('{0:N1}' -f ((Get-Item $releasePath).Length / 1MB)) MB" -ForegroundColor Gray
Write-Host ""
Write-Host "Upload: gh release upload v$Version `"$releasePath`" --clobber" -ForegroundColor Cyan
