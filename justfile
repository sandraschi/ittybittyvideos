set shell := ["pwsh", "-NoProfile", "-Command"]

# Bootstrap: install deps
bootstrap:
    uv sync

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
