param(
    [switch]$Headless,
    [switch]$NoBrowser,
    [switch]$SkipInstall,
    [switch]$BackendOnly
)
$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$BackendPort = 11054

Set-Location $ScriptRoot
. (Join-Path $ScriptRoot "scripts\ensure_ffmpeg_path.ps1")

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "    OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    WARN: $msg" -ForegroundColor Yellow }

if (-not $SkipInstall) {

    # ── 1. Kill port zombies (backend only; stack clears both) ───────
    if ($BackendOnly -or $Headless) {
        Write-Step "Clearing port $BackendPort"
        Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue |
            ForEach-Object {
                Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
            }
    }

    # ── 2. Python ─────────────────────────────────────────────────────
    Write-Step "Checking Python"
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) {
        $pyVer = & python --version 2>&1
        Write-OK $pyVer
    } else {
        Write-Warn "Python not found. Installing via winget..."
        winget install Python.Python.3.13 --accept-package-agreements --accept-source-agreements --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        Write-OK "Python installed"
    }

    # ── 3. uv ─────────────────────────────────────────────────────────
    Write-Step "Checking uv"
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if ($uv) {
        Write-OK "uv found at $($uv.Source)"
    } else {
        Write-Warn "uv not found. Installing..."
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
        Write-OK "uv installed"
    }

    # ── 4. FFmpeg ─────────────────────────────────────────────────────
    Write-Step "Checking FFmpeg"
    $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffmpeg) {
        Write-OK "ffmpeg found at $($ffmpeg.Source)"
    } else {
        Write-Warn "FFmpeg not found. Installing via winget..."
        winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
            Write-Host "    FFmpeg installed but not on PATH yet. Restart your terminal after this run." -ForegroundColor Yellow
        } else {
            Write-OK "FFmpeg installed"
        }
    }

    # ── 5. .env ───────────────────────────────────────────────────────
    Write-Step "Checking .env"
    if (-not (Test-Path "$ScriptRoot\.env")) {
        Copy-Item "$ScriptRoot\.env.example" "$ScriptRoot\.env"
        Write-OK "Created .env from template"
        Write-Host ""
        Write-Host "    IMPORTANT: Edit .env with your API keys before generating videos:" -ForegroundColor Yellow
        Write-Host "      - OPENAI_API_KEY  (or use VIDEOGEN_LLM_PROVIDER=ollama for local)" -ForegroundColor Yellow
        Write-Host "      - PEXELS_API_KEY  (free at https://www.pexels.com/api/)" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-OK ".env exists"
    }

    # ── 6. Dependencies ───────────────────────────────────────────────
    Write-Step "Installing dependencies"
    uv sync --quiet
    Write-OK "All dependencies installed"
}

if ($BackendOnly -or $Headless) {
    Write-Step "Starting roughcutvideos backend on http://127.0.0.1:$BackendPort"
    Write-Host "    Dev UI:  http://127.0.0.1:11055/  (run start.bat without -BackendOnly)" -ForegroundColor White
    Write-Host "    API docs: http://127.0.0.1:$BackendPort/docs" -ForegroundColor White
    Write-Host ""
    uv run python -m videogen_mcp.server
    exit $LASTEXITCODE
}

# Fleet dev stack: Vite :11055 + API :11054 (no webapp/dist required)
$stackScript = Join-Path $ScriptRoot "webapp\start.ps1"
$stackArgs = @()
if ($NoBrowser) { $stackArgs += "-NoBrowser" }
if ($SkipInstall) { $stackArgs += "-SkipInstall" }
& $stackScript @stackArgs
