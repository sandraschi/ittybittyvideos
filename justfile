set shell := ["pwsh", "-NoProfile", "-Command"]

# One command to rule them all. Double-click start.bat or run this.
go:
    & "{{justfile_directory()}}\start.ps1"

# Bootstrap only (no launch)
bootstrap:
    uv sync --extra dev

# Run dev server
dev:
    uv run python -m videogen_mcp.server

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

# Build Tauri native desktop app (release)
build-native:
    Set-Location "{{justfile_directory()}}\native"
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    & ".\build.ps1"

# Build Tauri native app (debug, skip PyInstaller)
build-native-debug:
    Set-Location "{{justfile_directory()}}\native"
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug
