$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoName = Split-Path -Leaf $Root
$BackendName = "ittybitty"
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"
New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null

Write-Host "=== ${RepoName} Tauri Release Build ===" -ForegroundColor Cyan

# Step 1: TypeScript lint gate + frontend build
$frontendDirs = @("web_sota", "webapp/frontend", "webapp")
foreach ($dir in $frontendDirs) {
    $frontend = Join-Path $Root $dir
    if (Test-Path "$frontend\package.json") {
        Write-Host "-> [1/4] Building frontend ($dir)..." -ForegroundColor Yellow
        Push-Location $frontend
        npm install --silent 2>$null

        Write-Host "  tsc --noEmit..." -ForegroundColor Gray
        $tscOut = npx tsc --noEmit 2>&1
        $tscExit = $LASTEXITCODE
        if ($tscExit -ne 0) {
            Write-Host "  TypeScript compilation FAILED - fix errors before building NSIS" -ForegroundColor Red
            Write-Host $tscOut
            throw "TypeScript compilation failed - fix all errors before building NSIS installer"
        }

        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
        Pop-Location
        break
    }
}

# Step 2: PyInstaller backend (onefile)
Write-Host "-> [2/4] PyInstaller backend..." -ForegroundColor Yellow
Push-Location $Root
uv sync --extra dev
if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }
Write-Host "  Ensuring PyInstaller in project venv..." -ForegroundColor Gray
uv pip install pyinstaller | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Failed to install PyInstaller" }
$pi = uv run python -m PyInstaller --version 2>&1
Write-Host "  PyInstaller: $pi" -ForegroundColor Gray
$specFile = "$Root\${BackendName}-backend.spec"
if (Test-Path $specFile) {
    # Patch fastmcp to not crash on missing metadata (dist-info stripped below)
    $fm = "$Root\.venv\Lib\site-packages\fastmcp\__init__.py"
    if (Test-Path $fm) {
        $c = Get-Content $fm -Raw
        if ($c -match 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)') {
            $replacement = @'
except PackageNotFoundError:
    try:
        __version__ = _version("fastmcp")
    except PackageNotFoundError:
        __version__ = "0.0.0"
'@
            $c = $c -replace 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)', $replacement
            Set-Content $fm -Value $c -Encoding utf8
            Write-Host "  Patched fastmcp metadata fallback" -ForegroundColor Yellow
        }
    }
    Remove-Item -Recurse -Force "$Root\build\${BackendName}-backend" -ErrorAction SilentlyContinue
    Remove-Item -Force "$Root\dist\${BackendName}-backend.exe" -ErrorAction SilentlyContinue
    uv run python -m PyInstaller "$specFile" --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
} else {
    Write-Host "  WARNING: spec file not found at $specFile - using existing backend exe if present" -ForegroundColor DarkYellow
}
Pop-Location

# Step 3: Embed in Tauri resources (+ dev fallback)
Write-Host "-> [3/4] Embedding backend..." -ForegroundColor Yellow
$backendExe = Join-Path $Root "dist\${BackendName}-backend.exe"
if (-not (Test-Path $backendExe)) { throw "Backend exe not found at $backendExe - PyInstaller step failed" }
Copy-Item $backendExe (Join-Path $ResourceDir "${BackendName}-backend.exe") -Force
Copy-Item $backendExe (Join-Path $DevDir "${BackendName}-backend-$Triple.exe") -Force
Write-Host "  Backend exe: $((Get-Item $backendExe).Length / 1MB) MB"

# Bundle .env into installer if it exists (survives reinstall, no manual copy needed)
$dotEnvFile = Join-Path $Root ".env"
if (Test-Path $dotEnvFile) {
    Copy-Item $dotEnvFile (Join-Path $ResourceDir ".env") -Force
    $dotEnvBytes = (Get-Item $dotEnvFile).Length
    Write-Host "  Bundled .env: $dotEnvBytes bytes" -ForegroundColor Green
} else {
    Write-Host "  WARNING: No .env at repo root - create one from .env.example for credentials" -ForegroundColor DarkYellow
    Set-Content -Path (Join-Path $ResourceDir ".env") -Value "# Empty - configure via Settings page" -Encoding utf8
    Write-Host "  Created placeholder .env in resources" -ForegroundColor Green
}

# Step 4: Single NSIS installer
Write-Host "-> [4/4] Tauri NSIS bundle..." -ForegroundColor Yellow
Push-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
npx @tauri-apps/cli build --bundles nsis
if ($LASTEXITCODE -ne 0) { throw "Tauri build failed with exit code $LASTEXITCODE" }
Pop-Location

# Stage to repo dist/
$distDir = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$nsisDir = "$PSScriptRoot\target\release\bundle\nsis"
if (Test-Path $nsisDir) { Copy-Item "$nsisDir\*-setup.exe" "$distDir\" -Force }
$strayExe = "$PSScriptRoot\target\release\${BackendName}-backend.exe"
if (Test-Path $strayExe) { Remove-Item $strayExe -Force; Write-Host "  Cleaned stray: $strayExe" -ForegroundColor DarkGray }

Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "Ship: $nsisDir\*.exe"
