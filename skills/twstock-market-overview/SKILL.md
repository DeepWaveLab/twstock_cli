---
name: twstock-market-overview
description: "Daily market snapshot — TAIEX index, top movers, margin balance, and institutional positioning."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Market Overview

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format and token-saving conventions.

Get a comprehensive daily market snapshot combining index performance, top-traded stocks, margin sentiment, and foreign investor positioning.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available (updates after 14:30 Taiwan time on trading days)

## Workflow

### Step 1: Fetch TAIEX Index Summary

```bash
twstock fetch stock.mi-index --json --limit 10
```

Returns market index data including closing index level, change, and volume.

### Step 2: Fetch Top 20 Most-Traded Stocks

```bash
twstock fetch stock.mi-index20 --json --fields "Code,Name,TradeVolume,TradeValue,ClosingPrice,Change"
```

Identifies the day's most active stocks by trading volume.

### Step 3: Fetch Margin Trading Balance

```bash
twstock fetch stock.mi-margn --json --limit 10
```

Shows margin financing and short-selling balances. High margin financing indicates bullish retail sentiment.

### Step 4: Fetch Foreign Investor Holdings by Sector

```bash
twstock fetch stock.mi-qfiis-cat --json
```

Shows foreign investor holding ratios by industry sector — reveals where institutional money is concentrated.

## Expected Output

Synthesize the four data sources into a market overview:

1. **Index level** — TAIEX closing index, daily change, and percentage
2. **Top movers** — Top 5 most-traded stocks with price and volume
3. **Margin sentiment** — Overall margin balance trend (bullish/bearish signal)
4. **Institutional positioning** — Sectors with highest/lowest foreign investor exposure

## Troubleshooting

### Empty data returned
- Check if today is a trading day: `twstock fetch stock.holidayschedule --json`
- Data may not be available until after market close (14:30 Taiwan time)

### Partial data
- Some endpoints update at different times. TAIEX index updates first, margin data updates later.

## See Also

- [twstock-institutional-flow](../twstock-institutional-flow/SKILL.md) — Detailed institutional tracking
- [twstock-margin-sentiment](../twstock-margin-sentiment/SKILL.md) — Deep margin analysis

## Notes

- Run this skill first before diving into individual stock analysis.
- Weekend and holiday data will return the most recent trading day's data.
- Use `--normalize` on Step 3 to get clean numeric values for margin balances.
