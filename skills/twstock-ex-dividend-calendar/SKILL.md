---
name: twstock-ex-dividend-calendar
description: "Look up the ex-dividend and ex-rights schedule for both TWSE and TPEX stocks."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Ex-Dividend Calendar (除權息)

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Look up the ex-dividend (除息) and ex-rights (除權) schedule for both TWSE and TPEX stocks to plan dividend capture strategies and track upcoming distributions.

## Preconditions

- `twstock` CLI installed and accessible
- Most useful during dividend season (June-September)

## Background

Taiwan's ex-dividend season is highly concentrated:
- **除息 (Ex-Dividend):** Cash dividend distribution. Stock price adjusts down by dividend amount on ex-date.
- **除權 (Ex-Rights):** Stock dividend distribution. Share count increases, price adjusts accordingly.
- **填權息 (Gap Fill):** When stock price recovers to pre-ex-dividend level. Actively tracked by investors.
- Peak season: June through September, with some distributions in Q1 and Q4.
- Both TWSE and TPEX stocks go ex-dividend — don't miss OTC ex-dividend opportunities.

## Workflow

### TWSE Ex-Dividend Schedule

#### Step 1: Fetch TWSE Ex-Dividend Schedule

```bash
twstock fetch stock.twt48u-all --json
```

Returns the full TWSE ex-dividend and ex-rights announcement table.

#### Step 2 (Optional): Filter by Stock Code

```bash
twstock fetch stock.twt48u-all --json --code <CODE>
```

### TPEX Ex-Dividend Schedule

#### Step 3: Fetch OTC Ex-Dividend Notices

```bash
twstock fetch otc.exright-prepost --json
```

Returns upcoming TPEX ex-dividend and ex-rights notices.

#### Step 4: Fetch OTC Daily Ex-Dividend Results

```bash
twstock fetch otc.exright-daily --json
```

Returns daily TPEX ex-dividend execution results (actual price adjustments).

### Dividend Details

#### Step 5: Check Dividend Distribution Details

For TWSE stocks:

```bash
twstock fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

For TPEX stocks:

```bash
twstock fetch otc_company.t187ap39-o --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

#### Step 6: Cross-Reference with Current Yield

```bash
# TWSE
twstock fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,DividendYield,PEratio" --normalize

# TPEX
twstock fetch otc.mainboard-peratio-analysis --json --code <CODE> --normalize
```

## Expected Output

1. **Upcoming ex-dividend dates** — Stocks from both exchanges with ex-dates in the coming weeks
2. **Dividend amounts** — Cash and stock dividend per share
3. **Yield at current price** — Current dividend yield for each stock
4. **Calendar view** — Sorted by date for planning, labeled by exchange

## Troubleshooting

### Empty schedule
- Ex-dividend announcements are published progressively. Early in the year, few stocks have announced.
- The bulk of announcements come in May-June for the main dividend season.

### Historical data
- The `twt48u-all` endpoint shows the current year's TWSE schedule.
- Historical dividend data is available via `company.t187ap45-l` (TWSE) or `otc_company.t187ap39-o` (TPEX).

### OTC ex-dividend data
- TPEX ex-dividend endpoints (`otc.exright-prepost`, `otc.exright-daily`) use different field names than TWSE.
- Use `twstock schema otc.exright-prepost --json` to verify exact fields.

## See Also

- [twstock-dividend-screener](../twstock-dividend-screener/SKILL.md) — Find high-yield stocks (both exchanges)
- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Full stock details for ex-dividend candidates
- [persona-dividend-investor](../persona-dividend-investor/SKILL.md) — Dividend investing mindset

## Notes

- Buy before the ex-dividend date to receive the dividend. The stock trades ex-dividend (adjusted price) on the ex-date.
- 填權息 (gap fill) performance is a critical metric — a stock that fills the gap quickly indicates strong fundamentals.
- Consider tax implications: cash dividends > NT$20,000 per payment trigger 2.11% supplementary health insurance premium.
- Some investors avoid buying just before ex-dividend dates if the stock historically fails to fill the gap.
- TPEX stocks often have different ex-dividend timing than TWSE — check both calendars.
