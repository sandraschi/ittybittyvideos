# Run Playwright e2e against dev stack (:11055 UI, :11054 API).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Test-PortListening([int]$Port) {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $conn
}

if (-not (Test-PortListening 11054)) {
    Write-Host "Starting backend on :11054..."
    Start-Process -FilePath "py" -ArgumentList "-m", "videogen_mcp.server" -WorkingDirectory $Root -WindowStyle Minimized
    $deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortListening 11054) { break }
        Start-Sleep -Seconds 1
    }
    if (-not (Test-PortListening 11054)) {
        Write-Error "Backend did not start on port 11054 within 45s"
    }
}

if (-not (Test-PortListening 11055)) {
    Write-Host "Starting Vite dev UI on :11055..."
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory (Join-Path $Root "webapp") -WindowStyle Minimized
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortListening 11055) { break }
        Start-Sleep -Seconds 1
    }
    if (-not (Test-PortListening 11055)) {
        Write-Error "Vite did not start on port 11055 within 60s"
    }
}

Set-Location (Join-Path $Root "webapp")
if (-not (Test-Path "node_modules\@playwright\test")) {
    Write-Host "Installing webapp deps..."
    npm install
    npx playwright install chromium
}

Write-Host "Running Playwright e2e..."
npm run e2e
exit $LASTEXITCODE
