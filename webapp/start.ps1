param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$WebRoot = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $WebRoot
$BackendPort = 11054
$FrontendPort = 11055

. (Join-Path $ProjectRoot "scripts\ensure_ffmpeg_path.ps1")

Write-Host "=== roughcut webapp ===" -ForegroundColor Cyan

foreach ($port in @($BackendPort, $FrontendPort)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.OwningProcess -gt 4) {
            Write-Host "Clearing port $port (PID $($_.OwningProcess))" -ForegroundColor Yellow
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

if (-not $FrontendOnly) {
    Write-Host "Syncing Python deps..." -ForegroundColor Cyan
    Push-Location $ProjectRoot
    uv sync --extra dev
    Pop-Location

    $ensureFfmpeg = Join-Path $ProjectRoot "scripts\ensure_ffmpeg_path.ps1"
    $backendCmd = ". '$ensureFfmpeg'; Set-Location '$ProjectRoot'; uv run python -m videogen_mcp.server"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WorkingDirectory $ProjectRoot

    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 2 -UseBasicParsing
            if ($r.StatusCode -eq 200) { $ready = $true; break }
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $ready) {
        Write-Host "Backend did not start on $BackendPort" -ForegroundColor Red
        exit 1
    }
    Write-Host "Backend ready on :$BackendPort" -ForegroundColor Green
}

if (-not $BackendOnly) {
    Set-Location $WebRoot
    if (-not (Test-Path "node_modules")) {
        if (Get-Command bun -ErrorAction SilentlyContinue) {
            bun install
        } else {
            npm install
        }
    }

    if (-not $NoBrowser) {
        $url = "http://127.0.0.1:$FrontendPort/"
        Start-Job -ScriptBlock {
            param($u)
            for ($i = 0; $i -lt 45; $i++) {
                try {
                    $null = Invoke-WebRequest -Uri $u -TimeoutSec 2 -UseBasicParsing
                    Start-Process $u
                    break
                } catch { Start-Sleep -Seconds 1 }
            }
        } -ArgumentList $url | Out-Null
    }

    if (Get-Command bun -ErrorAction SilentlyContinue) {
        bun run dev -- --port $FrontendPort --host 127.0.0.1
    } else {
        npm run dev -- --port $FrontendPort --host 127.0.0.1
    }
}
