# Copilot Instructions for twse-cli

## Project Overview

twse-cli is a Python CLI tool wrapping Taiwan Stock Exchange (TWSE) OpenAPI.
It provides agent-friendly access to 143 stock market endpoints.

## Tech Stack

- Python 3.12+, Click (CLI), httpx (HTTP), Rich (terminal output)
- Package manager: uv + Hatchling
- Tests: pytest, ruff for linting

## Key Commands

```bash
twse fetch <endpoint> --json        # Fetch data from any endpoint
twse endpoints --search "keyword"   # Discover endpoints
twse schema <endpoint> --json       # Inspect endpoint fields/types
```

## Code Architecture

- `twse_cli/cli.py` — Click root group with LazyGroup for domain shortcuts
- `twse_cli/client.py` — TWSEClient with httpx, retry, rate limiting
- `twse_cli/endpoints.py` — Registry of 143 EndpointDef dataclasses
- `twse_cli/output.py` — Envelope, TTY detection, field filtering
- `twse_cli/normalize.py` — Data normalization (string→number, ROC→ISO)
- `twse_cli/schema.py` — Runtime schema introspection
- `twse_cli/commands/_factory.py` — Dynamic command generation from registry

## Conventions

- All output follows `{"ok": true, "data": [...]}` envelope format
- Exit codes: 0=success, 1=API error, 2=validation, 3=network
- TTY-aware: Rich tables for humans (stderr), JSON for agents (stdout)
- Domain shortcuts delegate to `twse fetch` pipeline
