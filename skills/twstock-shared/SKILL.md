---
name: twstock-shared
description: "Shared conventions, output formats, and token-saving tips for all twstock-cli skills."
version: 1.0.0
metadata:
  category: "foundation"
  requires:
    bins: ["twstock"]
---

# twstock-cli Shared Conventions

Common patterns and conventions referenced by all twstock-cli skills. Read this before using any other skill.

## Output Format

All `twstock` commands return a JSON envelope:

```json
{"ok": true, "data": [{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}]}
```

Error responses:

```json
{"ok": false, "error": {"code": "api_error", "message": "TWSE API returned 503"}}
```

Exit codes: `0` = success, `1` = API error, `2` = validation error, `3` = network error.

## Token-Saving Guardrails

Every skill workflow MUST follow these rules to minimize token consumption:

1. **Always use `--fields`** to select only needed columns. Saves 5-10x tokens.
   ```bash
   twstock fetch stock.bwibbu-all --json --fields "Code,Name,DividendYield,PEratio"
   ```

2. **Always use `--json`** for machine-readable output (auto-detected when piped).

3. **Use `--code`** to filter by stock code when analyzing specific stocks.
   ```bash
   twstock fetch stock.stock-day-all --json --code 2330
   ```

4. **Use `--limit`** for sampling before fetching full datasets.
   ```bash
   twstock fetch stock.stock-day-all --json --limit 5
   ```

5. **Use `--normalize`** to get clean numbers instead of parsing strings.
   ```bash
   # Without: {"ClosingPrice": "595.00", "TradeVolume": "36,317,450"}
   # With:    {"ClosingPrice": 595.0, "TradeVolume": 36317450}
   twstock fetch stock.stock-day-all --json --normalize
   ```

6. **Use `--dry-run`** to preview the request URL before fetching.

## Endpoint Discovery

Before guessing endpoint names, search first:

```bash
# Search by keyword (Chinese or English)
twstock endpoints --search "股利" --json
twstock endpoints --search "dividend" --json

# Filter by category
twstock endpoints --category stock --json

# Inspect field schema
twstock schema stock.bwibbu-all --json
```

## Endpoint Reference Formats

Three ways to reference any endpoint:

| Format | Example |
|--------|---------|
| Dotted name | `stock.stock-day-all` |
| Raw API path | `/exchangeReport/STOCK_DAY_ALL` |
| API code | `STOCK_DAY_ALL` |

## ROC Date System

TWSE uses Republic of China (ROC) calendar dates:

- ROC year + 1911 = Gregorian year
- `1150313` = ROC year 115, month 03, day 13 = **2026-03-13**
- Use `--normalize` to auto-convert ROC dates to ISO 8601 format

## Categories

| Category | Count | Description |
|----------|-------|-------------|
| `stock` | 44 | Trading data, indices, margins, warrants |
| `company` | 86 | Fundamentals, governance, ESG, revenue |
| `broker` | 9 | Broker data, ETF rankings |
| `other` | 4 | Bonds, news, fund data |

## Common Field Names

Stock endpoints use English field names:
- `Code`, `Name`, `TradeVolume`, `TradeValue`, `OpeningPrice`, `HighestPrice`, `LowestPrice`, `ClosingPrice`, `Change`, `Transaction`
- `PEratio`, `DividendYield`, `PBratio`

Company endpoints use Chinese field names:
- `公司代號`, `公司名稱`, `產業別`, `董事長`, `總經理`
- `營業收入-當月營收`, `營業收入-去年同月增減(%)`
- `股利年度`, `股東配發-盈餘分配之現金股利(元/股)`

Use `twstock schema <endpoint> --json` to discover exact field names.

## Error Handling

- **API errors (exit 1):** TWSE may return 503 during high-traffic periods. Wait and retry.
- **Validation errors (exit 2):** Check endpoint name with `twstock endpoints --search`.
- **Network errors (exit 3):** Verify internet connectivity.
- **Empty data:** Some endpoints return empty arrays outside business hours or on holidays. Check `stock.holidayschedule` for trading calendar.

## Notes

- TWSE OpenAPI is public and free — no authentication required.
- Data updates after market close (typically after 14:30 Taiwan time, UTC+8).
- All values from TWSE are strings by default. Use `--normalize` for numeric conversion.
- SSL verification is disabled due to known TWSE certificate issues. Data is public market data.
