---
name: twstock-stock-compare
description: "Compare multiple stocks side-by-side on price, valuation, and revenue — supports cross-exchange TWSE vs TPEX comparison."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Stock Compare

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Compare two or more stocks side-by-side on price, valuation, and revenue metrics. Supports cross-exchange comparison (TWSE stock vs TPEX stock) and Web API historical trends.

## Preconditions

- `twstock` CLI installed and accessible
- Know the stock codes to compare (e.g., `2330` vs `6510`)

## Workflow

For each stock code in the comparison set, first determine the exchange (Step 0), then run Steps 1-3 using the appropriate endpoints.

### Step 0: Determine Exchange for Each Stock

```bash
twstock fetch stock.stock-day-all --json --code <CODE> --limit 1
```

If empty, try TPEX:

```bash
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --limit 1
```

### Step 1: Fetch Price Data

**TWSE:**
```bash
twstock fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,ClosingPrice,Change,TradeVolume,TradeValue" --normalize
```

**TPEX:**
```bash
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --normalize
```

### Step 2: Fetch Valuation Metrics

**TWSE:**
```bash
twstock fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

**TPEX:**
```bash
twstock fetch otc.mainboard-peratio-analysis --json --code <CODE> --normalize
```

### Step 3: Fetch Revenue

**TWSE:**
```bash
twstock fetch company.t187ap05-l --json --code <CODE> --fields "公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)" --normalize
```

**TPEX:**
```bash
twstock fetch otc_company.t187ap05-o --json --code <CODE> --fields "公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)" --normalize
```

### Step 4: Align and Compare

Combine the data into a comparison table:

```
| Metric          | Stock A (2330, TWSE) | Stock B (6510, TPEX) |
|-----------------|----------------------|----------------------|
| Exchange        | TWSE (上市)           | TPEX (上櫃)           |
| Closing Price   | 595.00               | 850.00               |
| Daily Change    | +5.00                | -10.00               |
| P/E Ratio       | 22.5                 | 18.3                 |
| Dividend Yield  | 2.1%                 | 3.5%                 |
| P/B Ratio       | 5.8                  | 4.2                  |
| Revenue YoY     | +15.3%               | +8.7%                |
| Trade Volume    | 36,317,450           | 1,234,567            |
```

### Step 5 (Optional): Historical Comparison via Web API

For multi-month trend comparison:

```bash
twstock fetch web.stock-day --date 20260301 --stock-no <CODE_A> --json
twstock fetch web.stock-day --date 20260301 --stock-no <CODE_B> --json
```

Compare price trends over multiple months to identify relative momentum.

### Step 6: Highlight Differences

Identify which stock is stronger on each metric:
- **Value** — Lower P/E and P/B, higher dividend yield
- **Growth** — Higher revenue YoY growth
- **Momentum** — Higher volume, positive price change
- **Liquidity** — Higher trade volume and value

## Expected Output

1. **Side-by-side comparison table** with key metrics (labeled by exchange)
2. **Relative strengths** — Which stock wins on value, growth, momentum
3. **Summary recommendation** — Context for the comparison

## Common Comparisons

| Comparison | Stocks | Context |
|------------|--------|---------|
| Semiconductor peers | 2330 vs 2454 | TSMC vs MediaTek (both TWSE) |
| Financial sector | 2881 vs 2882 | Fubon vs Cathay (both TWSE) |
| High-dividend ETFs | 0056 vs 00878 | Yuanta vs Cathay dividend ETFs |
| Cross-exchange tech | 2330 vs 5274 | TSMC (TWSE) vs 信驊 (TPEX) |
| OTC peers | 6510 vs 5274 | 精測 vs 信驊 (both TPEX) |

## Troubleshooting

### Different data availability
- Some stocks may not have all metrics available (e.g., ETFs may lack revenue data).
- Company endpoints use `公司代號` for filtering while stock endpoints use `Code`.

### Cross-exchange field name differences
- TWSE and TPEX endpoints may use different field names. Use `twstock schema <endpoint> --json` to verify.
- When comparing, normalize the metrics to common labels in the output table.

## See Also

- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Deep-dive into a single stock
- [twstock-dividend-screener](../twstock-dividend-screener/SKILL.md) — Compare dividend candidates

## Notes

- When comparing, always use `--normalize` for consistent numeric values.
- For sector-level comparison, use `twstock-market-overview` to see sector performance first.
- Limit comparisons to 3-4 stocks to keep output manageable.
- ETFs (codes starting with 00) won't have company revenue data.
- Cross-exchange comparisons are common — don't assume all stocks in a comparison are on the same exchange.
