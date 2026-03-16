---
name: twse-etf-rankings
description: "View ETF regular investment (定期定額) rankings to track where retail money flows systematically."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twse"]
    skills: ["twse-shared"]
---

# ETF Rankings (定期定額)

> **PREREQUISITE:** Read `../twse-shared/SKILL.md` for output format and token-saving conventions.

View ETF regular investment (定期定額) rankings to understand where Taiwan retail investors are systematically allocating capital through automated monthly contributions.

## Preconditions

- `twse` CLI installed and accessible
- Rankings data is updated monthly

## Background

定期定額 (fixed-term fixed-amount investing) is a massive trend in Taiwan:
- Monthly investment amounts reached NT$16.7 billion in 2025
- Primarily used for ETF purchases through broker automatic deduction
- Rankings reveal which ETFs attract the most systematic retail capital
- TSMC (2330) and high-dividend ETFs consistently top the charts

## Workflow

### Step 1: Fetch ETF Regular Investment Rankings

```bash
twse fetch broker.etfrank --json
```

Returns the monthly ranking of ETFs by number of regular investment accounts and transaction amounts.

### Step 2: Identify Top ETFs

From the rankings, note the top ETFs by:
- **Account count** — Most popular by number of investors
- **Transaction amount** — Most capital flowing in

### Step 3 (Optional): Cross-Reference with Valuation

For top-ranked ETFs, check current pricing:

```bash
twse fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,ClosingPrice,Change,TradeVolume" --normalize
```

### Step 4 (Optional): Check Dividend Yield of Top ETFs

```bash
twse fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,DividendYield,PEratio" --normalize
```

## Expected Output

1. **Top 10 ETFs by popularity** — Ranked by account count
2. **Capital flow leaders** — ETFs receiving the most monthly investment
3. **Trend analysis** — Which ETFs are gaining/losing popularity month-over-month
4. **Yield comparison** — Current dividend yield of popular ETFs

## Common Top ETFs

| Code | Name | Category |
|------|------|----------|
| 0050 | 元大台灣50 | Market cap weighted |
| 0056 | 元大高股息 | High dividend |
| 00878 | 國泰永續高股息 | ESG + High dividend |
| 00919 | 群益台灣精選高息 | High dividend |
| 00929 | 復華台灣科技優息 | Monthly dividend |
| 006208 | 富邦台50 | Market cap weighted |

## Troubleshooting

### Rankings appear stale
- Rankings are published monthly, typically in the first week of the month.
- The data reflects the prior month's activity.

### ETF code not found in other endpoints
- Some ETFs may not appear in `stock.bwibbu-all` (valuation data). Try `stock.stock-day-all` for price data.

## See Also

- [twse-dividend-screener](../twse-dividend-screener/SKILL.md) — Screen individual stocks for dividends
- [persona-dividend-investor](../persona-dividend-investor/SKILL.md) — Dividend investing mindset
- [twse-stock-compare](../twse-stock-compare/SKILL.md) — Compare ETFs side-by-side

## Notes

- 定期定額 rankings are a leading indicator of retail investor sentiment and preferences.
- Monthly-distribution ETFs (月配息) like 00929 have seen explosive growth since 2024.
- Younger investors increasingly prefer ETFs over individual stock picking.
- Use this data to understand market trends and popular investment themes.
