---
name: twse-stock-compare
description: "Compare multiple stocks side-by-side on price, valuation, and revenue metrics."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twse"]
    skills: ["twse-shared"]
---

# Stock Compare

> **PREREQUISITE:** Read `../twse-shared/SKILL.md` for output format and token-saving conventions.

Compare two or more stocks side-by-side on price, valuation, and revenue metrics to identify relative strengths and weaknesses.

## Preconditions

- `twse` CLI installed and accessible
- Know the stock codes to compare (e.g., `2330` vs `2454`)

## Workflow

For each stock code in the comparison set, run Steps 1-3. Replace `<CODE>` with each stock code.

### Step 1: Fetch Price Data

```bash
twse fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,ClosingPrice,Change,TradeVolume,TradeValue" --normalize
```

### Step 2: Fetch Valuation Metrics

```bash
twse fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

### Step 3: Fetch Revenue

```bash
twse fetch company.t187ap05-l --json --code <CODE> --fields "公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)" --normalize
```

### Step 4: Align and Compare

Combine the data into a comparison table:

```
| Metric          | Stock A (2330) | Stock B (2454) |
|-----------------|----------------|----------------|
| Closing Price   | 595.00         | 1,200.00       |
| Daily Change    | +5.00          | -10.00         |
| P/E Ratio       | 22.5           | 28.3           |
| Dividend Yield  | 2.1%           | 1.5%           |
| P/B Ratio       | 5.8            | 7.2            |
| Revenue YoY     | +15.3%         | +8.7%          |
| Trade Volume    | 36,317,450     | 5,234,123      |
```

### Step 5: Highlight Differences

Identify which stock is stronger on each metric:
- **Value** — Lower P/E and P/B, higher dividend yield
- **Growth** — Higher revenue YoY growth
- **Momentum** — Higher volume, positive price change
- **Liquidity** — Higher trade volume and value

## Expected Output

1. **Side-by-side comparison table** with key metrics
2. **Relative strengths** — Which stock wins on value, growth, momentum
3. **Summary recommendation** — Context for the comparison

## Common Comparisons

| Comparison | Stocks | Context |
|------------|--------|---------|
| Semiconductor peers | 2330 vs 2454 | TSMC vs MediaTek |
| Financial sector | 2881 vs 2882 | Fubon vs Cathay |
| High-dividend ETFs | 0056 vs 00878 | Yuanta vs Cathay dividend ETFs |
| Tech vs Traditional | 2330 vs 1301 | TSMC vs Formosa Plastics |

## Troubleshooting

### Different data availability
- Some stocks may not have all metrics available (e.g., ETFs may lack revenue data).
- Company endpoints use `公司代號` for filtering while stock endpoints use `Code`.

## See Also

- [twse-stock-lookup](../twse-stock-lookup/SKILL.md) — Deep-dive into a single stock
- [twse-dividend-screener](../twse-dividend-screener/SKILL.md) — Compare dividend candidates

## Notes

- When comparing, always use `--normalize` for consistent numeric values.
- For sector-level comparison, use `twse-market-overview` to see sector performance first.
- Limit comparisons to 3-4 stocks to keep output manageable.
- ETFs (codes starting with 00) won't have company revenue data.
