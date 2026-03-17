---
name: twstock-cli
description: Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX) — stock market data
install: uv tool install twstock-cli
security: read-only
commands:
  - twstock fetch <endpoint> --json [--fields F] [--code C] [--limit N] [--normalize] [--ndjson] [--raw] [--dry-run] [--stdin]
  - twstock endpoints --json [--search K] [--category C] [--with-fields]
  - twstock schema <endpoint> --json [--dry-run]
  - twstock serve
  - twstock version
  - twstock <command> --help-json
---

# twstock-cli — Agent Instructions

## Quick Start

```bash
# Install
uv tool install twstock-cli

# Fetch any endpoint
twstock fetch stock.stock-day-all --json

# Discover endpoints
twstock endpoints --search "dividend" --json

# Inspect schema
twstock schema stock.stock-day-all --json
```

## Core Commands

### 1. `twstock fetch <endpoint>` — Access any of 143 endpoints

```bash
# By dotted name
twstock fetch stock.stock-day-all --json

# By raw API path
twstock fetch /exchangeReport/STOCK_DAY_ALL --json

# By API code
twstock fetch STOCK_DAY_ALL --json
```

**Flags:**
- `--json` — JSON envelope to stdout (auto-detected when piped)
- `--fields "Code,Name,ClosingPrice"` — Return only these fields (saves tokens)
- `--code 2330` — Filter by stock code
- `--limit 10` — Limit number of records
- `--normalize` — Convert string→number, ROC dates→ISO 8601
- `--ndjson` — Newline-delimited JSON (one record per line)
- `--raw` — Bare JSON array (no envelope wrapper)
- `--dry-run` — Preview request as JSON without making an HTTP call
- `--stdin` — Read parameters from JSON on stdin
- `--help-json` — Output command metadata as structured JSON

### 2. `twstock endpoints` — Discover endpoints

```bash
# List all 143 endpoints
twstock endpoints --json

# Search by keyword (Chinese or English)
twstock endpoints --search "股利" --json
twstock endpoints --search "daily" --json

# Filter by category
twstock endpoints --category stock --json

# Show field definitions
twstock endpoints --search "stock.stock-day-all" --with-fields --json
```

### 3. `twstock schema <endpoint>` — Inspect endpoint fields

```bash
twstock schema stock.stock-day-all --json
# Returns: field names, inferred types, examples, non-empty percentages
```

### 4. `twstock serve` — MCP server mode

```bash
# Start as MCP server (stdio transport)
twstock serve
# Requires: uv pip install 'twstock-cli[mcp]'
```

Exposes tools: `twstock_fetch`, `twstock_endpoints`, `twstock_schema`.

## Output Formats

### JSON envelope (default for agents)
```json
{"ok": true, "data": [{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}]}
```

### NDJSON (one record per line)
```
{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}
{"Code": "2317", "Name": "鴻海", "ClosingPrice": "100.50"}
```

### Raw (bare JSON array, no envelope)
```json
[{"Code": "2330", "Name": "台積電"}, {"Code": "2317", "Name": "鴻海"}]
```

### Normalized (--normalize)
```json
{"ok": true, "data": [{"Code": "2330", "ClosingPrice": 595.0, "TradeVolume": 36317450}]}
```

### Error envelope
```json
{"ok": false, "error": {"code": "api_error", "message": "TWSE API returned 503"}}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error (TWSE returned 4xx/5xx) |
| 2 | Validation error (unknown endpoint, bad args) |
| 3 | Network error (cannot reach TWSE API) |

## Vocabulary

- **Endpoint ref**: `stock.stock-day-all`, `/exchangeReport/STOCK_DAY_ALL`, or `STOCK_DAY_ALL`
- **Categories**: `stock` (44), `company` (86), `broker` (9), `other` (4)
- **ROC dates**: `1150313` = 2026-03-13 (ROC year 115 + 1911 = 2026)
- **All values are strings**: Prices like `"595.00"`, volumes like `"36317450"` (use `--normalize` to convert)

## Workflow Examples

### Find stocks with high dividend yield
```bash
# 1. Discover dividend endpoint
twstock endpoints --search "殖利率" --json
# 2. Fetch PE/dividend/PB data with normalization
twstock fetch stock.bwibbu-all --json --fields "Code,Name,DividendYield,PEratio" --normalize
```

### Get TSMC data
```bash
twstock fetch stock.stock-day-all --json --code 2330
```

### Get company info
```bash
twstock fetch company.t187ap03-l --json --code 2330 --fields "公司代號,公司名稱,董事長,產業別"
```

### Monthly revenue
```bash
twstock fetch company.t187ap05-l --json --fields "公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)"
```

### Stream large dataset
```bash
twstock fetch stock.stock-day-all --ndjson | head -5
```

### Pipe bare array to jq
```bash
twstock fetch stock.stock-day-all --raw | jq '.[0:3]'
```

### Inspect endpoint fields before fetching
```bash
twstock schema stock.bwibbu-all --json
```

### Preview before fetching
```bash
twstock fetch stock.stock-day-all --dry-run --fields "Code,Name" --code 2330
```

### Structured input via stdin
```bash
echo '{"endpoint":"stock.stock-day-all","fields":["Code","Name"],"limit":5}' | twstock fetch --stdin --json
```

### Discover command flags programmatically
```bash
twstock fetch --help-json
twstock --help-json
twstock stock --help-json
```

## Skills

See `skills/` directory for guided multi-step workflows that compose multiple `twstock` commands:

| Skill | Description |
|-------|-------------|
| `twstock-shared` | Shared conventions, output format, token tips |
| `twstock-market-overview` | Daily market snapshot (TAIEX, top movers, margin, institutional) |
| `twstock-stock-lookup` | Comprehensive single-stock lookup |
| `twstock-dividend-screener` | Screen for high dividend yield stocks |
| `twstock-institutional-flow` | Track 三大法人 buying/selling |
| `twstock-revenue-tracker` | Monthly revenue analysis with YoY growth |
| `twstock-stock-compare` | Side-by-side stock comparison |
| `twstock-ex-dividend-calendar` | Ex-dividend schedule lookup |
| `twstock-company-profile` | Company fundamentals deep-dive |
| `twstock-margin-sentiment` | Margin balance sentiment analysis |
| `twstock-etf-rankings` | ETF regular investment rankings |
| `persona-stock-analyst` | Think like a Taiwan stock analyst |
| `persona-dividend-investor` | Think like a 存股 dividend investor |

Each skill has a `SKILL.md` file with preconditions, step-by-step workflows, and expected output.

## Token-Saving Tips

1. Always use `--fields` to select only needed columns
2. Use `--code` to filter by stock code (avoids downloading full dataset)
3. Use `--limit` for quick sampling
4. Search endpoints first: `twstock endpoints --search <keyword> --json`
5. Use `--normalize` to get clean numbers instead of string parsing
6. Use `twstock schema` to understand fields before querying
7. Use `--dry-run` to preview the request before executing
8. Use `--help-json` to discover flags without parsing help text

## Security Model

twstock-cli is a **read-only** data fetcher. Its security posture:

- **Network**: Only contacts `https://openapi.twse.com.tw/v1` (single host, HTTPS)
- **SSL**: Certificate verification disabled (`verify=False`) due to known TWSE certificate issues. MITM risk acknowledged — data is public market data, not secrets.
- **Authentication**: None. TWSE OpenAPI is public and auth-free.
- **File system**: Writes only to `~/.cache/twstock-cli/` (disk cache). No other file writes.
- **Input validation**: All user-supplied strings validated against control characters, path traversal, and injection patterns. Unknown endpoints rejected against fixed registry. Max input length: 1000 chars.
- **Output sanitization**: Control characters stripped from all API response values before output.
- **Agent trust boundary**: The agent is an untrusted operator. The CLI validates all inputs and sanitizes all outputs. The agent does not need elevated permissions.

## Command Guardrails

### fetch

```yaml
guardrails:
  - rule: always-use-fields
    severity: recommend
    message: "Always use --fields to select only needed columns. Reduces tokens by 5-10x."
  - rule: prefer-limit-for-sampling
    severity: recommend
    message: "Use --limit 5 for data exploration before fetching full datasets."
  - rule: use-dry-run-first
    severity: recommend
    message: "Use --dry-run to preview the request before executing."
  - rule: prefer-normalize
    severity: recommend
    message: "Use --normalize for clean numbers instead of parsing strings."
```

### endpoints

```yaml
guardrails:
  - rule: search-before-fetch
    severity: recommend
    message: "Search endpoints first with --search before guessing endpoint names."
  - rule: use-json-flag
    severity: recommend
    message: "Always use --json for machine-readable output."
```

### schema

```yaml
guardrails:
  - rule: inspect-before-fetch
    severity: recommend
    message: "Use 'twstock schema <endpoint> --json' to understand fields before querying."
```
