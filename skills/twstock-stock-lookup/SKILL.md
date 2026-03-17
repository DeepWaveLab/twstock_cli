---
name: twstock-stock-lookup
description: "Comprehensive single-stock lookup — price, valuation, company info, revenue, and dividends."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Stock Lookup

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format and token-saving conventions.

Get a comprehensive view of a single stock by combining price, valuation, company fundamentals, revenue, and dividend data.

## Preconditions

- `twstock` CLI installed and accessible
- Know the stock code (e.g., `2330` for TSMC, `2317` for Hon Hai)
- If unsure of the code, search: `twstock endpoints --search "台積電" --json`

## Workflow

Replace `<CODE>` with the target stock code (e.g., `2330`).

### Step 1: Fetch Daily Price and Volume

```bash
twstock fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,TradeVolume,TradeValue,OpeningPrice,HighestPrice,LowestPrice,ClosingPrice,Change,Transaction" --normalize
```

Returns today's OHLCV (open, high, low, close, volume) data.

### Step 2: Fetch Valuation Metrics

```bash
twstock fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

Returns P/E ratio, dividend yield, and price-to-book ratio.

### Step 3: Fetch Company Profile

```bash
twstock fetch company.t187ap03-l --json --code <CODE> --fields "公司代號,公司名稱,公司簡稱,產業別,董事長,總經理,成立日期,上市日期,實收資本額"
```

Returns basic company information including industry, leadership, and listing date.

### Step 4: Fetch Latest Revenue

```bash
twstock fetch company.t187ap05-l --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年當月營收,營業收入-去年同月增減(%)"
```

Returns the most recent monthly revenue with year-over-year comparison.

### Step 5 (Optional): Fetch Dividend History

```bash
twstock fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

Returns historical dividend distribution data.

## Expected Output

Combine the data into a stock summary:

1. **Price** — Current closing price, daily change, volume, and value
2. **Valuation** — P/E ratio, dividend yield, P/B ratio
3. **Company** — Industry, chairman, CEO, listing date, capital
4. **Revenue** — Latest monthly revenue and YoY growth rate
5. **Dividends** (optional) — Recent dividend history and payout amounts

## Troubleshooting

### Stock code not found
- Verify the code exists: `twstock fetch stock.stock-day-all --json --code <CODE> --limit 1`
- Some codes are ETFs or special instruments — try searching: `twstock endpoints --search "<CODE>" --json`

### Company data returns empty
- Company endpoints (`company.*`) may have delayed updates compared to stock price endpoints.
- Some fields may be empty for recently listed companies.

## See Also

- [twstock-stock-compare](../twstock-stock-compare/SKILL.md) — Compare multiple stocks side-by-side
- [twstock-company-profile](../twstock-company-profile/SKILL.md) — Full company deep-dive with financials

## Notes

- This is the most common skill — use it whenever a user asks about a specific stock.
- TSMC (2330) is the most-queried stock, accounting for ~25-30% of TAIEX market cap.
- Steps 1-4 are the core workflow. Step 5 adds dividend history for income-focused analysis.
- All company endpoint fields use Chinese names. Use `twstock schema company.t187ap03-l --json` to discover exact field names.
