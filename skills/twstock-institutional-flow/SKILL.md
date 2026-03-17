---
name: twstock-institutional-flow
description: "Track 三大法人 (foreign investors, investment trusts, proprietary dealers) across both TWSE and TPEX, with Web API historical data."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Institutional Flow (三大法人)

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Track the three major institutional investor groups — foreign investors (外資), investment trusts (投信), and proprietary dealers (自營商) — across both TWSE and TPEX markets, with Web API historical per-stock data.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available (institutional data updates after market close)

## Background

三大法人 (three major institutional investors) account for approximately 40% of total market volume. Their combined trading direction is a primary signal for Taiwan retail investors:

- **外資 (Foreign Investors):** Largest institutional group. Net buying is a strong bullish signal.
- **投信 (Investment Trusts):** Domestic mutual funds. Follow trends and sector rotation.
- **自營商 (Proprietary Dealers):** Broker proprietary trading desks. Often short-term oriented.

TPEX has 7 dedicated institutional endpoints providing granular OTC institutional data not available on TWSE.

## Workflow

### TWSE Institutional Data

#### Step 1: Fetch Foreign Investor Sector Holdings

```bash
twstock fetch stock.mi-qfiis-cat --json
```

Shows foreign investor holding ratios by TWSE industry sector.

#### Step 2: Fetch Top 20 Foreign Investor Holdings

```bash
twstock fetch stock.mi-qfiis-sort-20 --json
```

Lists the top 20 TWSE stocks with highest foreign investor holdings.

### TPEX Institutional Data

#### Step 3: Fetch OTC Institutional Daily Net Trading

```bash
twstock fetch otc.3insti-daily-trading --json
```

Shows daily institutional net buy/sell amounts for the OTC market.

#### Step 4: Fetch OTC Institutional Summary

```bash
twstock fetch otc.3insti-summary --json
```

Shows total institutional buy/sell amounts and net trading for OTC.

#### Step 5: Fetch OTC Foreign Investor Trading

```bash
twstock fetch otc.3insti-qfii-trading --json
```

Shows foreign investor (外資) buy/sell details in the OTC market.

#### Step 6: Fetch OTC Foreign Investor Holdings Ranking

```bash
twstock fetch otc.3insti-qfii --json
```

Lists OTC stocks ranked by foreign investor holding ratio.

#### Step 7: Fetch OTC Foreign Investor by Sector

```bash
twstock fetch otc.3insti-qfii-industry --json
```

Shows foreign investor holdings by OTC industry sector.

#### Step 8 (Optional): Fetch OTC Dealer and Investment Trust Data

```bash
twstock fetch otc.3insti-dealer-trading --json
twstock fetch otc.3insti-trading --json
```

Dealer (自營商) and investment trust (投信) net trading in OTC market.

### Web API — Historical Per-Stock Institutional Data

#### Step 9 (Optional): Fetch Per-Stock Institutional Flow by Date

```bash
# Foreign investors by stock (specific date)
twstock fetch web.twt38u --date 20260317 --json

# Investment trusts by stock
twstock fetch web.twt43u --date 20260317 --json

# Dealers by stock
twstock fetch web.twt44u --date 20260317 --json

# Institutional summary
twstock fetch web.bfi82u --date 20260317 --json
```

Web API provides historical institutional data that the daily endpoints don't retain.

### Step 10: Cross-Reference with Price

For stocks with notable institutional activity, check price movement:

```bash
# TWSE stock
twstock fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,ClosingPrice,Change,TradeVolume" --normalize

# TPEX stock
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --normalize
```

## Expected Output

1. **TWSE institutional overview**
   - Foreign investor sector holdings and top 20 stocks
   - Key over/underweight sectors

2. **TPEX institutional overview**
   - OTC institutional net buy/sell summary
   - Top OTC stocks by foreign investor concentration
   - OTC sector-level institutional positioning

3. **Combined signals**
   - Are institutions buying/selling both markets in the same direction?
   - Divergence between TWSE and TPEX institutional flow can signal sector rotation
   - Notable stock-level institutional activity (from Web API)

## Troubleshooting

### Data not updated
- Institutional data typically updates after 15:00 Taiwan time.
- Weekend queries return the most recent trading day's data.

### Web API returns empty for a date
- That date may be a holiday or weekend. Try the previous trading day.

## See Also

- [twstock-market-overview](../twstock-market-overview/SKILL.md) — Includes institutional data as part of daily snapshot
- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Individual stock details

## Notes

- Foreign investor (外資) flow is the single most-watched institutional indicator in Taiwan.
- Net foreign buying for 3+ consecutive days is considered a strong bullish signal.
- Investment trust (投信) buying often precedes domestic retail interest.
- TPEX's 7 dedicated institutional endpoints provide richer granularity than TWSE's sector-level data.
- Use Web API (Step 9) to build multi-day institutional flow trends for specific stocks.
- Use this skill daily after market close for institutional flow monitoring.
