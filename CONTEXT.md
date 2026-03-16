# twse-cli Context

## What This Tool Does

twse-cli is a CLI tool that wraps Taiwan Stock Exchange (TWSE) OpenAPI with 143 endpoints.
It's designed for AI agents to efficiently query stock market data with minimal token consumption.

## Installation

```bash
uv tool install twse-cli
```

## Core Commands

```bash
# Fetch any endpoint (143 available)
twse fetch <endpoint> --json [--fields F] [--code C] [--limit N] [--normalize] [--ndjson] [--raw]

# Discover endpoints
twse endpoints --json [--search K] [--category C] [--with-fields]

# Inspect endpoint schema
twse schema <endpoint> --json

# Version info
twse version
```

## Endpoint Reference Formats

```bash
twse fetch stock.stock-day-all        # dotted name
twse fetch /exchangeReport/STOCK_DAY_ALL  # raw API path
twse fetch STOCK_DAY_ALL              # API code
```

## Output Formats

- `--json`: Standard envelope `{"ok": true, "data": [...]}`
- `--ndjson`: Newline-delimited JSON (one record per line)
- `--raw`: Bare JSON array (no envelope wrapper)
- `--normalize`: Convert string→number, ROC dates→ISO 8601

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error |
| 2 | Validation error |
| 3 | Network error |

## Data Notes

- All TWSE values are strings by default (use `--normalize` to convert)
- ROC dates: `1150313` = 2026-03-13 (ROC year + 1911 = Gregorian)
- Categories: stock (44), company (86), broker (9), other (4)

## Security

Read-only tool. Inputs validated (control chars, path traversal, injection). Outputs sanitized (control chars stripped). See AGENTS.md for full security model.
