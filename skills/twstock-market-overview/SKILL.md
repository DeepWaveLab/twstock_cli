---
name: twstock-market-overview
description: "Daily market snapshot — TAIEX + TPEX indices, top movers, margin balance, and institutional positioning for both exchanges."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Market Overview

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Get a comprehensive daily market snapshot combining TWSE and TPEX index performance, top-traded stocks, margin sentiment, and institutional positioning.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available (updates after 14:30 Taiwan time on trading days)

## Workflow

### Step 1: Fetch TAIEX Index Summary (TWSE)

```bash
twstock fetch stock.mi-index --json --limit 10
```

Returns TWSE market index data including closing index level, change, and volume.

### Step 2: Fetch TPEX Index Summary (OTC)

```bash
twstock fetch otc.index --json --limit 5
```

Returns TPEX (櫃買指數) index data — the primary index for the OTC market.

### Step 3: Fetch OTC Market Highlights

```bash
twstock fetch otc.mainboard-highlight --json
```

Returns OTC market overview including trading volume, value, and number of advancing/declining stocks.

### Step 4: Fetch Top 20 Most-Traded Stocks (TWSE)

```bash
twstock fetch stock.mi-index20 --json --fields "Code,Name,TradeVolume,TradeValue,ClosingPrice,Change"
```

Identifies the day's most active TWSE stocks by trading volume.

### Step 5: Fetch Margin Trading Balance (TWSE)

```bash
twstock fetch stock.mi-margn --json --limit 10 --normalize
```

Shows TWSE margin financing and short-selling balances.

### Step 6: Fetch OTC Margin Balance

```bash
twstock fetch otc.mainboard-margin-balance --json --limit 10 --normalize
```

Shows TPEX margin financing and short-selling balances.

### Step 7: Fetch Institutional Summary (TWSE)

```bash
twstock fetch stock.mi-qfiis-cat --json
```

Shows TWSE foreign investor holding ratios by industry sector.

### Step 8: Fetch OTC Institutional Summary

```bash
twstock fetch otc.3insti-summary --json
```

Shows TPEX institutional (三大法人) buy/sell summary for the OTC market.

## Expected Output

Synthesize the data into a dual-exchange market overview:

1. **TWSE (上市)**
   - TAIEX closing index, daily change, and percentage
   - Top 5 most-traded stocks with price and volume
   - Margin balance trend (bullish/bearish signal)
   - Sectors with highest/lowest foreign investor exposure

2. **TPEX (上櫃)**
   - TPEX index closing level and daily change
   - Market highlights (advancing vs declining stocks)
   - OTC margin balance trend
   - OTC institutional net buy/sell

3. **Combined signals** — Are both markets moving in the same direction? Divergence between TWSE and TPEX can signal sector rotation.

## Troubleshooting

### Empty data returned
- Check if today is a trading day: `twstock fetch stock.holidayschedule --json`
- Data may not be available until after market close (14:30 Taiwan time)

### Partial data
- Some endpoints update at different times. TAIEX index updates first, margin data updates later.
- TPEX data may update slightly after TWSE data.

## See Also

- [twstock-institutional-flow](../twstock-institutional-flow/SKILL.md) — Detailed institutional tracking for both exchanges
- [twstock-margin-sentiment](../twstock-margin-sentiment/SKILL.md) — Deep margin analysis with OTC data

## Notes

- Run this skill first before diving into individual stock analysis.
- Weekend and holiday data will return the most recent trading day's data.
- TPEX index (櫃買指數) often moves differently from TAIEX — tech-heavy OTC stocks can diverge from the main board.
- Use `--normalize` on margin steps to get clean numeric values.
