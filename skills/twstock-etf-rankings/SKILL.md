---
name: twstock-etf-rankings
description: "View ETF regular investment (定期定額) rankings and OTC fund data to track where retail money flows."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# ETF Rankings (定期定額)

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

View ETF regular investment (定期定額) rankings and OTC fund market data to understand where Taiwan retail investors are systematically allocating capital.

## Preconditions

- `twstock` CLI installed and accessible
- Rankings data is updated monthly

## Background

定期定額 (fixed-term fixed-amount investing) is a massive trend in Taiwan:
- Monthly investment amounts reached NT$16.7 billion in 2025
- Primarily used for ETF purchases through broker automatic deduction
- Rankings reveal which ETFs attract the most systematic retail capital
- TSMC (2330) and high-dividend ETFs consistently top the charts
- Most popular ETFs trade on TWSE, but some newer ETFs trade on TPEX

## Workflow

### Step 1: Fetch ETF Regular Investment Rankings

```bash
twstock fetch broker.etfrank --json
```

Returns the monthly ranking of ETFs by number of regular investment accounts and transaction amounts.

### Step 2: Identify Top ETFs

From the rankings, note the top ETFs by:
- **Account count** — Most popular by number of investors
- **Transaction amount** — Most capital flowing in

### Step 3: Fetch OTC Fund Daily Quotes

```bash
twstock fetch otc_fund.latest --json
```

Returns daily quotes for TPEX-listed funds/ETFs — covers OTC-traded funds not in the TWSE rankings.

### Step 4: Fetch OTC Fund Market Overview

```bash
twstock fetch otc_fund.market-highlight --json
```

Returns OTC fund market overview including trading activity and highlights.

### Step 5 (Optional): Cross-Reference with Valuation

For top-ranked ETFs, check current pricing:

```bash
# TWSE-listed ETFs
twstock fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,ClosingPrice,Change,TradeVolume" --normalize

# TPEX-listed ETFs
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --normalize
```

### Step 6 (Optional): Check Dividend Yield of Top ETFs

```bash
# TWSE-listed ETFs
twstock fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,DividendYield,PEratio" --normalize

# TPEX-listed ETFs
twstock fetch otc.mainboard-peratio-analysis --json --code <CODE> --normalize
```

## Expected Output

1. **Top 10 ETFs by popularity** — Ranked by account count
2. **Capital flow leaders** — ETFs receiving the most monthly investment
3. **OTC fund activity** — TPEX-listed fund trading and highlights
4. **Trend analysis** — Which ETFs are gaining/losing popularity month-over-month
5. **Yield comparison** — Current dividend yield of popular ETFs

## Common Top ETFs

| Code | Name | Exchange | Category |
|------|------|----------|----------|
| 0050 | 元大台灣50 | TWSE | Market cap weighted |
| 0056 | 元大高股息 | TWSE | High dividend |
| 00878 | 國泰永續高股息 | TWSE | ESG + High dividend |
| 00919 | 群益台灣精選高息 | TWSE | High dividend |
| 00929 | 復華台灣科技優息 | TWSE | Monthly dividend |
| 006208 | 富邦台50 | TWSE | Market cap weighted |

## Troubleshooting

### Rankings appear stale
- Rankings are published monthly, typically in the first week of the month.
- The data reflects the prior month's activity.

### ETF code not found in other endpoints
- Some ETFs may not appear in `stock.bwibbu-all` (valuation data). Try `stock.stock-day-all` for price data.
- TPEX-listed ETFs won't appear in TWSE endpoints — use `otc.*` endpoints instead.

## See Also

- [twstock-dividend-screener](../twstock-dividend-screener/SKILL.md) — Screen individual stocks for dividends
- [persona-dividend-investor](../persona-dividend-investor/SKILL.md) — Dividend investing mindset
- [twstock-stock-compare](../twstock-stock-compare/SKILL.md) — Compare ETFs side-by-side

## Notes

- 定期定額 rankings are a leading indicator of retail investor sentiment and preferences.
- Monthly-distribution ETFs (月配息) like 00929 have seen explosive growth since 2024.
- Younger investors increasingly prefer ETFs over individual stock picking.
- Use this data to understand market trends and popular investment themes.
- Check OTC fund data (Steps 3-4) for newer or niche ETFs that may not appear in the main rankings.
