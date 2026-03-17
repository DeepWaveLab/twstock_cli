# Copilot Instructions for twstock-cli

## Project Overview

twstock-cli is a Python CLI tool wrapping Taiwan Stock Exchange (TWSE) OpenAPI.
It provides agent-friendly access to 143 stock market endpoints.

## Tech Stack

- Python 3.12+, Click (CLI), httpx (HTTP), Rich (terminal output)
- Package manager: uv + Hatchling
- Tests: pytest, ruff for linting

## Key Commands

```bash
twstock fetch <endpoint> --json        # Fetch data from any endpoint
twstock endpoints --search "keyword"   # Discover endpoints
twstock schema <endpoint> --json       # Inspect endpoint fields/types
```

## Code Architecture

- `twstock_cli/cli.py` — Click root group with LazyGroup for domain shortcuts
- `twstock_cli/client.py` — TWStockClient with httpx, retry, rate limiting
- `twstock_cli/endpoints.py` — Registry of 143 EndpointDef dataclasses
- `twstock_cli/output.py` — Envelope, TTY detection, field filtering
- `twstock_cli/normalize.py` — Data normalization (string→number, ROC→ISO)
- `twstock_cli/schema.py` — Runtime schema introspection
- `twstock_cli/commands/_factory.py` — Dynamic command generation from registry

## Conventions

- All output follows `{"ok": true, "data": [...]}` envelope format
- Exit codes: 0=success, 1=API error, 2=validation, 3=network
- TTY-aware: Rich tables for humans (stderr), JSON for agents (stdout)
- Domain shortcuts delegate to `twstock fetch` pipeline
- Input validation: control chars, path traversal, injection patterns rejected
- Output sanitization: control chars stripped from API response strings

## Guardrails

- Always use `--fields` to select only needed columns (saves tokens)
- Use `--limit 5` for data exploration before fetching full datasets
- Use `--dry-run` to preview requests before executing
- Search endpoints first with `--search` before guessing names
- Use `--help-json` to discover flags programmatically
