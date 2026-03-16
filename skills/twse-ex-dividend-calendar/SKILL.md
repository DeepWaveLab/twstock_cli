---
name: twse-ex-dividend-calendar
description: "Look up the ex-dividend and ex-rights schedule for upcoming or recent distributions."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twse"]
    skills: ["twse-shared"]
---

# Ex-Dividend Calendar (除權息)

> **PREREQUISITE:** Read `../twse-shared/SKILL.md` for output format and token-saving conventions.

Look up the ex-dividend (除息) and ex-rights (除權) schedule to plan dividend capture strategies and track upcoming distributions.

## Preconditions

- `twse` CLI installed and accessible
- Most useful during dividend season (June-September)

## Background

Taiwan's ex-dividend season is highly concentrated:
- **除息 (Ex-Dividend):** Cash dividend distribution. Stock price adjusts down by dividend amount on ex-date.
- **除權 (Ex-Rights):** Stock dividend distribution. Share count increases, price adjusts accordingly.
- **填權息 (Gap Fill):** When stock price recovers to pre-ex-dividend level. Actively tracked by investors.
- Peak season: June through September, with some distributions in Q1 and Q4.

## Workflow

### Step 1: Fetch Ex-Dividend Schedule

```bash
twse fetch stock.twt48u-all --json
```

Returns the full ex-dividend and ex-rights announcement table for all listed stocks.

### Step 2: Filter by Stock Code (Optional)

For a specific stock:

```bash
twse fetch stock.twt48u-all --json --code <CODE>
```

### Step 3: Cross-Reference with Dividend Yield

Check current yield for stocks with upcoming ex-dividend dates:

```bash
twse fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,DividendYield,PEratio" --normalize
```

### Step 4: Check Dividend Distribution Details

For detailed dividend amounts:

```bash
twse fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

## Expected Output

1. **Upcoming ex-dividend dates** — Stocks with ex-dates in the coming weeks
2. **Dividend amounts** — Cash and stock dividend per share
3. **Yield at current price** — Current dividend yield for each stock
4. **Calendar view** — Sorted by date for planning

## Troubleshooting

### Empty schedule
- Ex-dividend announcements are published progressively. Early in the year, few stocks have announced.
- The bulk of announcements come in May-June for the main dividend season.

### Historical data
- The `twt48u-all` endpoint shows the current year's schedule. Historical dividend data is available via `company.t187ap45-l`.

## See Also

- [twse-dividend-screener](../twse-dividend-screener/SKILL.md) — Find high-yield stocks
- [twse-stock-lookup](../twse-stock-lookup/SKILL.md) — Full stock details for ex-dividend candidates
- [persona-dividend-investor](../persona-dividend-investor/SKILL.md) — Dividend investing mindset

## Notes

- Buy before the ex-dividend date to receive the dividend. The stock trades ex-dividend (adjusted price) on the ex-date.
- 填權息 (gap fill) performance is a critical metric — a stock that fills the gap quickly indicates strong fundamentals.
- Consider tax implications: cash dividends are subject to supplementary health insurance premium (2.11%) for amounts over NT$20,000 per payment.
- Some investors avoid buying just before ex-dividend dates if the stock historically fails to fill the gap.
