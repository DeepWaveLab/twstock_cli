---
name: twse-cli
description: Agent-friendly CLI for Taiwan Stock Exchange (TWSE) OpenAPI — 143 endpoints
install: uv tool install twse-cli
commands:
  - twse fetch <endpoint> --json [--fields F] [--code C] [--limit N] [--normalize] [--ndjson] [--raw]
  - twse endpoints --json [--search K] [--category C] [--with-fields]
  - twse schema <endpoint> --json
  - twse serve
  - twse version
---

# twse-cli — Agent Instructions

## Quick Start

```bash
# Install
uv tool install twse-cli

# Fetch any endpoint
twse fetch stock.stock-day-all --json

# Discover endpoints
twse endpoints --search "dividend" --json

# Inspect schema
twse schema stock.stock-day-all --json
```

## Core Commands

### 1. `twse fetch <endpoint>` — Access any of 143 endpoints

```bash
# By dotted name
twse fetch stock.stock-day-all --json

# By raw API path
twse fetch /exchangeReport/STOCK_DAY_ALL --json

# By API code
twse fetch STOCK_DAY_ALL --json
```

**Flags:**
- `--json` — JSON envelope to stdout (auto-detected when piped)
- `--fields "Code,Name,ClosingPrice"` — Return only these fields (saves tokens)
- `--code 2330` — Filter by stock code
- `--limit 10` — Limit number of records
- `--normalize` — Convert string→number, ROC dates→ISO 8601
- `--ndjson` — Newline-delimited JSON (one record per line)
- `--raw` — Bare JSON array (no envelope wrapper)

### 2. `twse endpoints` — Discover endpoints

```bash
# List all 143 endpoints
twse endpoints --json

# Search by keyword (Chinese or English)
twse endpoints --search "股利" --json
twse endpoints --search "daily" --json

# Filter by category
twse endpoints --category stock --json

# Show field definitions
twse endpoints --search "stock.stock-day-all" --with-fields --json
```

### 3. `twse schema <endpoint>` — Inspect endpoint fields

```bash
twse schema stock.stock-day-all --json
# Returns: field names, inferred types, examples, non-empty percentages
```

### 4. `twse serve` — MCP server mode

```bash
# Start as MCP server (stdio transport)
twse serve
# Requires: uv pip install 'twse-cli[mcp]'
```

Exposes tools: `twse_fetch`, `twse_endpoints`, `twse_schema`.

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
twse endpoints --search "殖利率" --json
# 2. Fetch PE/dividend/PB data with normalization
twse fetch stock.bwibbu-all --json --fields "Code,Name,DividendYield,PEratio" --normalize
```

### Get TSMC data
```bash
twse fetch stock.stock-day-all --json --code 2330
```

### Get company info
```bash
twse fetch company.t187ap03-l --json --code 2330 --fields "公司代號,公司名稱,董事長,產業別"
```

### Monthly revenue
```bash
twse fetch company.t187ap05-l --json --fields "公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)"
```

### Stream large dataset
```bash
twse fetch stock.stock-day-all --ndjson | head -5
```

### Pipe bare array to jq
```bash
twse fetch stock.stock-day-all --raw | jq '.[0:3]'
```

### Inspect endpoint fields before fetching
```bash
twse schema stock.bwibbu-all --json
```

## Token-Saving Tips

1. Always use `--fields` to select only needed columns
2. Use `--code` to filter by stock code (avoids downloading full dataset)
3. Use `--limit` for quick sampling
4. Search endpoints first: `twse endpoints --search <keyword> --json`
5. Use `--normalize` to get clean numbers instead of string parsing
6. Use `twse schema` to understand fields before querying
