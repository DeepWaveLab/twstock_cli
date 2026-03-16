---
name: twse-cli
description: Agent-friendly CLI for Taiwan Stock Exchange (TWSE) OpenAPI — 143 endpoints
install: uv tool install twse-cli
commands:
  - twse fetch <endpoint> --json [--fields F] [--code C] [--limit N]
  - twse endpoints --json [--search K] [--category C] [--with-fields]
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
```

## Two Core Commands

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

## Output Format

Success:
```json
{"ok": true, "data": [{"Code": "2330", "Name": "台積電", "ClosingPrice": "1865.00"}]}
```

Error:
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
- **All values are strings**: Prices like `"595.00"`, volumes like `"36317450"`

## Workflow Examples

### Find stocks with high dividend yield
```bash
# 1. Discover dividend endpoint
twse endpoints --search "殖利率" --json
# 2. Fetch PE/dividend/PB data
twse fetch stock.bwibbu-all --json --fields "Code,Name,DividendYield,PEratio"
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

## Token-Saving Tips

1. Always use `--fields` to select only needed columns
2. Use `--code` to filter by stock code (avoids downloading full dataset)
3. Use `--limit` for quick sampling
4. Search endpoints first: `twse endpoints --search <keyword> --json`
