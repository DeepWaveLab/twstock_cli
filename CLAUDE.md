# twstock-cli

## Project Overview

twstock-cli is a Python CLI wrapping Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX) APIs — stock market data for both exchanges. Designed for AI agents to query efficiently with minimal token consumption.

## Tech Stack

- **Language:** Python 3.12+
- **CLI:** Click (with LazyGroup for deferred subcommand loading)
- **HTTP:** httpx (sync, with retry transport)
- **Terminal:** Rich (tables to stderr for humans, JSON to stdout for agents)
- **Package manager:** uv + Hatchling
- **Linting:** ruff (line-length 140)
- **Testing:** pytest (markers: `integration`, `smoke`, `twse`, `tpex`, `web`)

## Key Files

- `twstock_cli/cli.py` — Click root group, top-level commands (fetch, endpoints, schema, version, serve)
- `twstock_cli/endpoints.py` — Registry of 359 `EndpointDef` dataclasses (single source of truth)
- `twstock_cli/commands/_factory.py` — Dynamically generates Click commands from endpoint registry
- `twstock_cli/client.py` — TWStockClient with httpx, 3x retry, rate limiting
- `twstock_cli/normalize.py` — String→number, ROC dates→ISO 8601 conversion
- `twstock_cli/sanitize.py` — Output sanitization (control chars stripped from API responses)
- `twstock_cli/validate.py` — Input validation (control chars, path traversal, injection patterns)
- `twstock_cli/cache.py` — Disk cache for API responses (~/.cache/twstock-cli/)
- `twstock_cli/schema.py` — Endpoint field inspection with inferred types
- `twstock_cli/output.py` — TTY-aware output (Rich tables for humans, JSON for agents)
- `twstock_cli/help_json.py` — Structured `--help-json` metadata output
- `twstock_cli/serve.py` — MCP server mode (FastMCP, stdio transport)
- `AGENTS.md` — Agent-facing instructions with command guardrails

## Development Commands

```bash
uv sync                          # Install dependencies
uv run pytest                    # Run unit tests
uv run pytest -m integration     # Run all integration tests (TWSE+TPEX+Web)
uv run pytest -m smoke           # Run smoke tests for all 359 endpoints
uv run pytest -m twse            # Run TWSE-only integration tests
uv run pytest -m tpex            # Run TPEX-only integration tests
uv run pytest -m web             # Run Web API integration tests
uv run ruff check twstock_cli/   # Lint
uv run ruff format twstock_cli/  # Format
```

## Conventions

- All output follows `{"ok": true, "data": [...]}` envelope format
- Exit codes: 0=success, 1=API error, 2=validation, 3=network
- TTY-aware: Rich tables (stderr) for humans, JSON (stdout) for agents
- Input validation: control chars, path traversal, injection patterns rejected
- Output sanitization: control chars stripped from API response strings
- Stock endpoints use English field names (`Code`, `Name`, `ClosingPrice`)
- Company endpoints use Chinese field names (`公司代號`, `公司名稱`, `營業收入-當月營收`)

## Skills

When a user asks about Taiwan stock market data, use the skills in `skills/` to compose multi-step workflows. Each skill is a `SKILL.md` file with step-by-step instructions.

**Always read `skills/twstock-shared/SKILL.md` first** for conventions and token-saving rules.

### When to use which skill

| User intent | Skill to use |
|-------------|-------------|
| "How's the market today?" | `skills/twstock-market-overview/SKILL.md` |
| "Tell me about stock 2330" / any specific stock | `skills/twstock-stock-lookup/SKILL.md` |
| "Tell me about stock 6510" / any OTC stock | `skills/twstock-stock-lookup/SKILL.md` |
| "How's the OTC market?" / 上櫃 | `skills/twstock-market-overview/SKILL.md` |
| "Find high dividend stocks" / 存股 | `skills/twstock-dividend-screener/SKILL.md` |
| "What are institutions buying?" / 三大法人 | `skills/twstock-institutional-flow/SKILL.md` |
| "Show me revenue growth leaders" | `skills/twstock-revenue-tracker/SKILL.md` |
| "Compare TSMC vs MediaTek" / any stock comparison | `skills/twstock-stock-compare/SKILL.md` |
| "When is the ex-dividend date?" / 除權息 | `skills/twstock-ex-dividend-calendar/SKILL.md` |
| "Give me full company analysis" / due diligence | `skills/twstock-company-profile/SKILL.md` |
| "What's the margin sentiment?" / 融資融券 | `skills/twstock-margin-sentiment/SKILL.md` |
| "What ETFs are popular?" / 定期定額 | `skills/twstock-etf-rankings/SKILL.md` |

All skills now cover both TWSE (上市) and TPEX (上櫃) markets. The `twstock-shared` skill documents all 359 endpoints across 17 groups with exchange detection patterns.

### Persona skills (for broader analysis)

- `skills/persona-stock-analyst/SKILL.md` — Systematic top-down analysis framework (TWSE + TPEX)
- `skills/persona-dividend-investor/SKILL.md` — 存股 income investing mindset (both exchanges)

### Token-saving rules (always follow)

1. Always use `--fields` to select only needed columns
2. Always use `--json` for structured output
3. Use `--code` to filter by stock code
4. Use `--limit` for sampling before full fetches
5. Use `--normalize` for clean numbers
6. Use `--dry-run` to preview before fetching
7. Search endpoints first: `twstock endpoints --search <keyword> --json`
8. Use Web API `--date` for historical per-stock data: `twstock fetch web.stock-day --date YYYYMMDD --stock-no CODE --json`
9. For OTC stocks, use `otc.*` and `otc_company.*` endpoints (see `twstock-shared` for full mapping)
