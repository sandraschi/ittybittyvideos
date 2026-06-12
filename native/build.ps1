$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"

Write-Host "==> roughcut native build pipeline" -ForegroundColor Cyan
Write-Host ""

# Step 1: Webapp is pre-built (static HTML, no build step needed)
Write-Host "[1/4] Webapp: static HTML (no build step)" -ForegroundColor Green

# Step 2: PyInstaller backend (onefile)
Write-Host "[2/4] Freezing Python backend with PyInstaller..." -ForegroundColor Green
Push-Location $Root

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    uv pip install pyinstaller
}

uv run pyinstaller `
    --onefile `
    --name roughcut-backend `
    --add-data "src/videogen_mcp;videogen_mcp" `
    --add-data "webapp/dist;webapp/dist" `
    --copy-metadata fastmcp `
    --copy-metadata fastapi `
    --hidden-import edge_tts `
    --hidden-import openai `
    --hidden-import httpx `
    --clean --noconfirm `
    run_server.py

Pop-Location

# Step 3: Copy to Tauri resources + dev binaries
Write-Host "[3/4] Embedding backend in Tauri resources..." -ForegroundColor Green
$src = "$Root\dist\roughcut-backend.exe"
if (-not (Test-Path $src)) {
    Write-Host "ERROR: PyInstaller output not found at $src" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null
Copy-Item $src "$ResourceDir\roughcut-backend.exe" -Force
Copy-Item $src "$DevDir\roughcut-backend-$Triple.exe" -Force
Write-Host "    Embedded: $('{0:N1}' -f ((Get-Item $src).Length / 1MB)) MB" -ForegroundColor Gray

# Step 4: Tauri build (NSIS installer)
Write-Host "[4/4] Building Tauri NSIS installer..." -ForegroundColor Green
Push-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
npx @tauri-apps/cli build
Pop-Location

$installer = Get-ChildItem "$PSScriptRoot\target\release\bundle\nsis\*-setup.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($installer) {
    Write-Host ""
    Write-Host "==> SHIP THIS:" -ForegroundColor Green
    Write-Host "    $($installer.FullName)" -ForegroundColor White
    Write-Host "    Size: $('{0:N1}' -f ($installer.Length / 1MB)) MB" -ForegroundColor Gray
} else {
    Write-Host "==> Installer not found. Check tauri build output above." -ForegroundColor Yellow
}
