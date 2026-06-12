#!/usr/bin/env pwsh
# Local release: NSIS installer (+ optional wheel) → GitHub Release asset.
param(
    [string]$Tag = "",
    [switch]$SkipTauri,
    [switch]$SkipWheel,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Version = (Select-String -Path "pyproject.toml" -Pattern '^version = "(.+)"' | ForEach-Object { $_.Matches.Groups[1].Value })
if (-not $Tag) { $Tag = "v$Version" }

if (-not (Test-Path dist)) { New-Item -ItemType Directory -Path dist | Out-Null }

if (-not $SkipWheel) {
    Write-Host "=== wheel + sdist ===" -ForegroundColor Cyan
    uv build
}

if (-not $SkipTauri -and -not $SkipBuild) {
    Write-Host "=== Tauri NSIS (native/build.ps1) ===" -ForegroundColor Cyan
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    pwsh -NoLogo -File "$Root\native\build.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} elseif (-not $SkipTauri) {
    Write-Host "=== Skipping Tauri build (-SkipBuild); using existing dist/ installer ===" -ForegroundColor Gray
}

$installer = Get-Item "dist\ittybitty-$Version-x64-setup.exe" -ErrorAction SilentlyContinue
if (-not $installer -and -not $SkipTauri) {
    throw "Expected dist\ittybitty-$Version-x64-setup.exe after Tauri build"
}

$uploads = @()
if (-not $SkipWheel) {
    $uploads += Get-Item "dist\videogen_mcp-*.whl" -ErrorAction SilentlyContinue
    $uploads += Get-Item "dist\videogen_mcp-*.tar.gz" -ErrorAction SilentlyContinue
}
if ($installer) { $uploads += $installer }

if (-not $uploads) { throw "No release files to upload" }

$releaseExists = gh release view $Tag 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "=== Creating release $Tag ===" -ForegroundColor Cyan
    gh release create $Tag --title "ittybitty $Tag" --notes "Windows NSIS installer (single-file setup.exe)."
}

Write-Host "=== Upload to $Tag ===" -ForegroundColor Cyan
foreach ($f in $uploads) {
    Write-Host "  $($f.FullName)"
    gh release upload $Tag $f.FullName --clobber
}

Write-Host "Done: https://github.com/sandraschi/ittybittyvideos/releases/tag/$Tag" -ForegroundColor Green
