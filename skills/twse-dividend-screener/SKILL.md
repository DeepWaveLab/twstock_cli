---
name: twse-dividend-screener
description: "Screen for high dividend yield stocks using Taiwan 存股 (stock accumulation) criteria."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twse"]
    skills: ["twse-shared"]
---

# Dividend Screener

> **PREREQUISITE:** Read `../twse-shared/SKILL.md` for output format and token-saving conventions.

Screen for high dividend yield stocks following Taiwan's 存股 (stock accumulation) investment culture. Identify stocks with stable, high-yield dividends suitable for long-term income investing.

## Preconditions

- `twse` CLI installed and accessible
- Market data available

## Background

存股 (stock accumulation) is a dominant investment strategy in Taiwan, especially among retail investors. Key principles:
- Focus on dividend yield stability over 3+ consecutive years
- Target yield > 4-5% with reasonable P/E ratios
- Prefer companies with consistent payout history
- Popular targets include high-dividend ETFs (0056, 00919, 00929) and blue-chip stocks

## Workflow

### Step 1: Fetch All Valuation Data

```bash
twse fetch stock.bwibbu-all --json --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

Returns P/E ratio, dividend yield, and P/B ratio for all listed stocks.

### Step 2: Filter High-Yield Candidates

From the data returned in Step 1, filter stocks matching these criteria:

| Criteria | Threshold | Rationale |
|----------|-----------|-----------|
| DividendYield | > 4% (conservative) or > 5% (aggressive) | Core income target |
| PEratio | < 20 (below market average) | Avoid overvalued stocks |
| PBratio | < 3.0 | Reasonable price-to-book |

### Step 3: Verify Dividend History

For each candidate from Step 2, check dividend stability:

```bash
twse fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

Look for:
- 3+ consecutive years of cash dividend payments
- Stable or growing dividend amounts
- No years with zero payout

### Step 4 (Optional): Check Revenue Trend

Verify the company's revenue supports continued dividends:

```bash
twse fetch company.t187ap05-l --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)"
```

Declining revenue may signal future dividend cuts.

## Expected Output

A ranked list of dividend candidates:

1. **Top candidates** — Stocks ranked by dividend yield, filtered by P/E and P/B
2. **Dividend history** — Payout consistency for top candidates
3. **Risk flags** — Any candidates with declining revenue or irregular payout history

## Troubleshooting

### DividendYield is 0 for many stocks
- Some stocks haven't announced dividends yet for the current year.
- DividendYield is calculated from the most recent declared dividend.

### Very high DividendYield (>15%)
- Likely a one-time special dividend or stock price crash. Check price and dividend history before recommending.

## See Also

- [twse-ex-dividend-calendar](../twse-ex-dividend-calendar/SKILL.md) — Check upcoming ex-dividend dates
- [twse-stock-lookup](../twse-stock-lookup/SKILL.md) — Deep-dive into individual candidates
- [persona-dividend-investor](../persona-dividend-investor/SKILL.md) — 存股 investor mindset

## Notes

- Taiwan's ex-dividend season concentrates in June-September. Screen in Q1-Q2 for best entry timing.
- High-dividend ETFs (0056, 00919, 00929, 00878) are popular alternatives to individual stock picking.
- Monthly-distribution ETFs (月配息) like 00929 are increasingly popular among younger investors.
- Always cross-reference dividend yield with payout history — a high yield from a one-time special dividend is not sustainable.
