---
name: twstock-revenue-tracker
description: "Track monthly revenue with year-over-year comparison to identify growth leaders and decliners."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Revenue Tracker

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format and token-saving conventions.

Analyze monthly revenue (月營收) data with year-over-year comparisons. Monthly revenue is the most-watched fundamental indicator between quarterly earnings releases in Taiwan.

## Preconditions

- `twstock` CLI installed and accessible
- Revenue data available (published by the 10th of each month for the prior month)

## Background

Monthly revenue (月營收) reporting is mandatory for all listed companies in Taiwan. This data is:
- Released by the 10th of each month
- The most timely fundamental indicator available
- Widely used by both retail and institutional investors
- A leading indicator for quarterly earnings

## Workflow

### Step 1: Fetch All Company Revenue Data

```bash
twstock fetch company.t187ap05-l --json --fields "出表日期,資料年月,公司代號,公司名稱,產業別,營業收入-當月營收,營業收入-去年當月營收,營業收入-去年同月增減(%)" --normalize
```

Returns monthly revenue for all listed companies with YoY comparison.

### Step 2: Identify Growth Leaders

From Step 1 data, sort by `營業收入-去年同月增減(%)` descending to find stocks with highest YoY revenue growth.

Filter criteria for growth screening:
- YoY growth > 20% (strong growth)
- YoY growth > 50% (exceptional growth — verify it's not a low-base effect)

### Step 3: Check Specific Stock Revenue

For individual stock analysis:

```bash
twstock fetch company.t187ap05-l --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年當月營收,營業收入-去年同月增減(%)" --normalize
```

### Step 4 (Optional): Cross-Reference with Valuation

Check if growth stocks are reasonably valued:

```bash
twstock fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

## Expected Output

1. **Growth leaders** — Top companies by YoY revenue growth
2. **Growth decliners** — Companies with largest revenue declines
3. **Sector trends** — Revenue growth patterns by industry (產業別)
4. **Individual analysis** — Detailed revenue for specific stocks

## Troubleshooting

### Revenue data appears old
- Revenue data is published by the 10th of each month. Between the 1st-10th, the latest data is from two months prior.
- Example: On March 5th, the latest revenue is for January.

### YoY comparison shows extreme values
- Very high growth (>100%) may indicate a low base from the prior year (e.g., COVID recovery).
- Very low growth (<-50%) may indicate one-time events. Check company news.

## See Also

- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Includes revenue in stock overview
- [twstock-dividend-screener](../twstock-dividend-screener/SKILL.md) — Revenue supports dividend sustainability
- [twstock-company-profile](../twstock-company-profile/SKILL.md) — Full financial deep-dive

## Notes

- Revenue data uses Chinese field names. Use `twstock schema company.t187ap05-l --json` to verify exact names.
- The `營業收入-當月營收` field is in thousands of NT dollars (千元).
- Semiconductor stocks (especially TSMC) often set the tone for the broader market's revenue season.
- Consistent YoY growth for 3+ months is a stronger signal than a single month spike.
