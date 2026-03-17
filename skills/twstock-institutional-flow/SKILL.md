---
name: twstock-institutional-flow
description: "Track 三大法人 (foreign investors, investment trusts, proprietary dealers) buying and selling patterns."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Institutional Flow (三大法人)

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format and token-saving conventions.

Track the three major institutional investor groups — foreign investors (外資), investment trusts (投信), and proprietary dealers (自營商) — to understand where institutional money is flowing.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available (institutional data updates after market close)

## Background

三大法人 (three major institutional investors) account for approximately 40% of total TWSE market volume. Their combined trading direction is a primary signal for Taiwan retail investors:

- **外資 (Foreign Investors):** Largest institutional group. Net buying is a strong bullish signal.
- **投信 (Investment Trusts):** Domestic mutual funds. Follow trends and sector rotation.
- **自營商 (Proprietary Dealers):** Broker proprietary trading desks. Often short-term oriented.

## Workflow

### Step 1: Fetch Foreign Investor Sector Holdings

```bash
twstock fetch stock.mi-qfiis-cat --json
```

Shows foreign investor holding ratios by industry sector. Identifies which sectors have the highest institutional concentration.

### Step 2: Fetch Top 20 Foreign Investor Holdings

```bash
twstock fetch stock.mi-qfiis-sort-20 --json
```

Lists the top 20 individual stocks with highest foreign investor holdings. TSMC (2330) typically leads.

### Step 3: Analyze Sector Concentration

Compare foreign investor holding percentages across sectors to identify:
- **Overweight sectors** — High holding ratio = institutional confidence
- **Underweight sectors** — Low holding ratio = potential opportunity or risk avoidance

### Step 4 (Optional): Cross-Reference with Price

For stocks with notable institutional activity, check price movement:

```bash
twstock fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,ClosingPrice,Change,TradeVolume" --normalize
```

## Expected Output

1. **Sector overview** — Foreign investor holding ratios by industry sector
2. **Top holdings** — Top 20 stocks by foreign investor concentration
3. **Key signals** — Notable changes in institutional positioning

## Troubleshooting

### Data not updated
- Institutional data typically updates after 15:00 Taiwan time.
- Weekend queries return the most recent trading day's data.

## See Also

- [twstock-market-overview](../twstock-market-overview/SKILL.md) — Includes institutional data as part of daily snapshot
- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Individual stock details

## Notes

- Foreign investor (外資) flow is the single most-watched institutional indicator in Taiwan.
- Net foreign buying for 3+ consecutive days is considered a strong bullish signal.
- Investment trust (投信) buying often precedes domestic retail interest.
- Use this skill daily after market close for institutional flow monitoring.
