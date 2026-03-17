---
name: twstock-shared
description: "Shared conventions, output formats, and token-saving tips for all twstock-cli skills."
version: 2.0.0
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

7. **Use Web API `--date` for historical data** instead of fetching all and filtering.
   ```bash
   twstock fetch web.stock-day --date 20260301 --stock-no 2330 --json
   ```

## Exchange Detection

Taiwan has two stock exchanges. Skills must handle both:

- **TWSE (上市):** Taiwan Stock Exchange — endpoints in `stock.*`, `company.*`, `broker.*`
- **TPEX (上櫃):** Taipei Exchange (OTC market) — endpoints in `otc.*`, `otc_company.*`, `otc_financial.*`, etc.

### Auto-detect exchange for a stock code

```
Step 0: Determine exchange
  1. twstock fetch stock.stock-day-all --json --code <CODE> --limit 1
     → If data non-empty → TWSE listed (上市)
  2. twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --limit 1
     → If data non-empty → TPEX listed (上櫃)
  3. If both empty → stock code not found or market closed
```

Stock codes are 4-digit numbers. Both TWSE and TPEX use the same format — you cannot determine exchange from the code alone. Always check.

### TWSE → TPEX Endpoint Mapping

| Purpose | TWSE Endpoint | TPEX Endpoint |
|---------|--------------|---------------|
| Daily quotes | `stock.stock-day-all` | `otc.mainboard-daily-close-quotes` |
| P/E, Yield, P/B | `stock.bwibbu-all` | `otc.mainboard-peratio-analysis` |
| Market index | `stock.mi-index` | `otc.index` |
| Margin balance | `stock.mi-margn` | `otc.mainboard-margin-balance` |
| Foreign investor by sector | `stock.mi-qfiis-cat` | `otc.3insti-qfii-industry` |
| Top foreign holdings | `stock.mi-qfiis-sort-20` | `otc.3insti-qfii` |
| Institutional daily trading | (use `stock.mi-qfiis-*`) | `otc.3insti-daily-trading` |
| Ex-dividend notice | `stock.twt48u-all` | `otc.exright-prepost` |
| Company basic info | `company.t187ap03-l` | `otc_company.t187ap03-o` |
| Monthly revenue | `company.t187ap05-l` | `otc_company.t187ap05-o` |
| Dividend history | `company.t187ap45-l` | `otc_company.t187ap39-o` |
| Income statement | `company.t187ap06-l-ci` | `otc_financial.t187ap06-o-ci` |
| Balance sheet | `company.t187ap07-l-ci` | `otc_financial.t187ap07-o-ci` |
| Board holdings | `company.t187ap11-l` | `otc_company.t187ap11-o` |
| Large shareholders | `company.t187ap02-l` | `otc_company.t187ap02-o` |
| ESG disclosure | `company.t187ap46-l-*` | `otc_esg.t187ap46-o-*` |

## Endpoint Discovery

Before guessing endpoint names, search first:

```bash
# Search by keyword (Chinese or English)
twstock endpoints --search "股利" --json
twstock endpoints --search "dividend" --json

# Filter by group
twstock endpoints --group stock --json
twstock endpoints --group otc --json
twstock endpoints --group otc_company --json
twstock endpoints --group web --json

# Inspect field schema
twstock schema stock.bwibbu-all --json
twstock schema otc.mainboard-peratio-analysis --json
```

## Endpoint Reference Formats

Three ways to reference any endpoint:

| Format | Example |
|--------|---------|
| Dotted name | `stock.stock-day-all` |
| Raw API path | `/exchangeReport/STOCK_DAY_ALL` |
| API code | `STOCK_DAY_ALL` |

## Endpoint Groups (17 groups, 359 endpoints)

### TWSE (Taiwan Stock Exchange — 上市)

| Group | Count | Description |
|-------|-------|-------------|
| `stock` | 45 | Trading data, indices, margins, warrants |
| `company` | 86 | Fundamentals, governance, ESG, revenue |
| `broker` | 9 | Broker data, ETF rankings |
| `other` | 4 | Bonds, news, fund data |

### TPEX (Taipei Exchange — 上櫃)

| Group | Count | Description |
|-------|-------|-------------|
| `otc` | 64 | OTC trading data, indices, margins, institutional |
| `otc_company` | 29 | OTC company fundamentals, revenue, dividends |
| `otc_index` | 18 | TPEX index series (TPEX50, TPEX200, High Dividend, etc.) |
| `otc_esg` | 16 | OTC ESG disclosure (16 topic categories) |
| `otc_financial` | 32 | OTC financial statements (income, balance, by industry) |
| `otc_esb` | 5 | Emerging stock board (興櫃) |
| `otc_bond` | 8 | Bond trading data |
| `otc_broker` | 8 | OTC broker trading data |
| `otc_warrant` | 16 | OTC warrant data |
| `otc_fund` | 3 | OTC fund (ETF) data |
| `otc_gold` | 3 | Gold trading data |
| `otc_gisa` | 5 | Go Incubation Board (創櫃板) |

### Web API (Historical — date-parameterized)

| Group | Count | Description |
|-------|-------|-------------|
| `web` | 8 | Historical per-stock data with `--date` and `--stock-no` params |

Web API endpoints require `--date YYYYMMDD` and optionally `--stock-no CODE`:

```bash
# Per-stock historical price
twstock fetch web.stock-day --date 20260301 --stock-no 2330 --json

# Per-stock valuation
twstock fetch web.bwibbu --date 20260301 --stock-no 2330 --json

# Per-stock revenue
twstock fetch web.fmsrfk --date 20260301 --stock-no 2330 --json

# Institutional flow by stock (date only, returns all stocks)
twstock fetch web.twt38u --date 20260317 --json   # Foreign investors
twstock fetch web.twt43u --date 20260317 --json   # Investment trusts
twstock fetch web.twt44u --date 20260317 --json   # Dealers
twstock fetch web.bfi82u --date 20260317 --json   # Summary

# Market index historical
twstock fetch web.mi-index --date 20260317 --json
```

## ROC Date System

TWSE uses Republic of China (ROC) calendar dates:

- ROC year + 1911 = Gregorian year
- `1150313` = ROC year 115, month 03, day 13 = **2026-03-13**
- Use `--normalize` to auto-convert ROC dates to ISO 8601 format
- Web API uses Gregorian dates in `YYYYMMDD` format (e.g., `20260317`)

## Common Field Names

### TWSE stock endpoints (English field names)

- `Code`, `Name`, `TradeVolume`, `TradeValue`, `OpeningPrice`, `HighestPrice`, `LowestPrice`, `ClosingPrice`, `Change`, `Transaction`
- `PEratio`, `DividendYield`, `PBratio`

### TPEX OTC endpoints (mixed Chinese/English field names)

OTC endpoints may use different field names than their TWSE counterparts. Always use `twstock schema <endpoint> --json` to discover exact field names for `--fields` filtering.

### Company endpoints (Chinese field names — both TWSE and TPEX)

- `公司代號`, `公司名稱`, `產業別`, `董事長`, `總經理`
- `營業收入-當月營收`, `營業收入-去年同月增減(%)`
- `股利年度`, `股東配發-盈餘分配之現金股利(元/股)`

## Error Handling

- **API errors (exit 1):** TWSE/TPEX may return 503 during high-traffic periods. Wait and retry.
- **Validation errors (exit 2):** Check endpoint name with `twstock endpoints --search`.
- **Network errors (exit 3):** Verify internet connectivity.
- **Empty data:** Some endpoints return empty arrays outside business hours or on holidays. Check `stock.holidayschedule` for trading calendar.

## Notes

- TWSE and TPEX OpenAPIs are public and free — no authentication required.
- Data updates after market close (typically after 14:30 Taiwan time, UTC+8).
- All values from TWSE/TPEX are strings by default. Use `--normalize` for numeric conversion.
- SSL verification is disabled due to known TWSE certificate issues. Data is public market data.
