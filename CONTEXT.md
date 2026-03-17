# twstock-cli Context

## What This Tool Does

twstock-cli is a CLI tool that wraps Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX) APIs with 359 endpoints.
It's designed for AI agents to efficiently query stock market data with minimal token consumption.

## Installation

```bash
uv tool install twstock-cli
```

## Core Commands

```bash
# Fetch any endpoint (359 available)
twstock fetch <endpoint> --json [--fields F] [--code C] [--limit N] [--normalize] [--ndjson] [--raw] [--dry-run] [--stdin]

# Discover endpoints
twstock endpoints --json [--search K] [--category C] [--with-fields]

# Inspect endpoint schema
twstock schema <endpoint> --json [--dry-run]

# Structured command metadata
twstock <command> --help-json

# Version info
twstock version
```

## Endpoint Reference Formats

```bash
twstock fetch stock.stock-day-all        # dotted name
twstock fetch /exchangeReport/STOCK_DAY_ALL  # raw API path
twstock fetch STOCK_DAY_ALL              # API code
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
- Categories: `stock` (45), `company` (86), `broker` (9), `other` (4), `otc` (64), `otc_company` (29), `otc_index` (18), `otc_esg` (16), `otc_financial` (32), `otc_warrant` (16), `otc_bond` (8), `otc_broker` (8), `otc_esb` (5), `otc_gisa` (5), `otc_fund` (3), `otc_gold` (3), `web` (8)

## Security

Read-only tool. Contacts three hosts: `openapi.twse.com.tw` (TWSE), `www.tpex.org.tw` (TPEX), `www.twse.com.tw` (Web). Inputs validated (control chars, path traversal, injection). Outputs sanitized (control chars stripped). See AGENTS.md for full security model.
