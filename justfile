set shell := ["pwsh", "-NoProfile", "-Command"]

# One command: dev stack (Vite :11055 + API :11054)
go:
    & "{{justfile_directory()}}\start.ps1"

# Backend only (MCP / headless; no Node required)
backend:
    & "{{justfile_directory()}}\start.ps1" -BackendOnly

# Bootstrap only (no launch)
bootstrap:
    uv sync --extra dev

# Run backend only (same as backend recipe)
dev:
    uv run python -m videogen_mcp.server

# Vite dev webapp (:11055)
web:
    Set-Location "{{justfile_directory()}}\webapp"
    if (Get-Command bun -ErrorAction SilentlyContinue) { bun run dev -- --port 11055 --host 127.0.0.1 } else { npm run dev -- --port 11055 --host 127.0.0.1 }

# Build webapp to webapp/dist (served by backend at /)
build-web:
    Set-Location "{{justfile_directory()}}\webapp"
    if (Get-Command bun -ErrorAction SilentlyContinue) { bun install; bun run build } else { npm install; npm run build }

# Full stack dev (backend + Vite) — same as start.bat / just go
stack:
    & "{{justfile_directory()}}\start.ps1"

# Run with MCP transport
serve:
    uv run python -m videogen_mcp.server

# Lint
lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

# Fix lint
fix:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Typecheck
typecheck:
    uv run pyright src/

# Run tests
test:
    uv run pytest tests/ -v

# Full check (lint + typecheck + test)
check: lint typecheck test

# Build Tauri NSIS installer → dist/ittybitty-{version}-x64-setup.exe
build-native:
    pwsh -NoLogo -File "{{justfile_directory()}}\native\build.ps1"

# Local GitHub release upload (NSIS + wheel)
publish-release tag="":
    $tag = if ("{{tag}}") { "{{tag}}" } else { "v$((Select-String -Path pyproject.toml -Pattern '^version = \"(.+)\"').Matches.Groups[1].Value)" }
    pwsh -NoLogo -File "{{justfile_directory()}}\scripts\publish-release-local.ps1" -Tag $tag

# Build Tauri native app (debug, skip PyInstaller)
build-native-debug:
    Set-Location "{{justfile_directory()}}\native"
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

# Sync with feature extras (plain 'uv sync' silently drops align/beats - use this instead)
sync:
    uv sync --extra align --extra beats --extra dev
