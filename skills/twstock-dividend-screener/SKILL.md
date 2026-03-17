---
name: twstock-dividend-screener
description: "Screen for high dividend yield stocks across both TWSE and TPEX using Taiwan 存股 (stock accumulation) criteria."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Dividend Screener

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Screen for high dividend yield stocks following Taiwan's 存股 (stock accumulation) investment culture. Covers both TWSE (上市) and TPEX (上櫃) stocks for complete market coverage.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available

## Background

存股 (stock accumulation) is a dominant investment strategy in Taiwan, especially among retail investors. Key principles:
- Focus on dividend yield stability over 3+ consecutive years
- Target yield > 4-5% with reasonable P/E ratios
- Prefer companies with consistent payout history
- Popular targets include high-dividend ETFs (0056, 00919, 00929) and blue-chip stocks
- Some of the best 存股 candidates are OTC-listed (上櫃), especially financial and tech names

## Workflow

### Step 1: Fetch TWSE Valuation Data

```bash
twstock fetch stock.bwibbu-all --json --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

Returns P/E ratio, dividend yield, and P/B ratio for all TWSE-listed stocks.

### Step 2: Fetch TPEX Valuation Data

```bash
twstock fetch otc.mainboard-peratio-analysis --json --normalize
```

Returns P/E ratio, dividend yield, and P/B ratio for all TPEX-listed stocks.

### Step 3: Filter High-Yield Candidates (Both Exchanges)

From the data returned in Steps 1-2, filter stocks matching these criteria:

| Criteria | Threshold | Rationale |
|----------|-----------|-----------|
| DividendYield | > 4% (conservative) or > 5% (aggressive) | Core income target |
| PEratio | < 20 (below market average) | Avoid overvalued stocks |
| PBratio | < 3.0 | Reasonable price-to-book |

### Step 4: Verify Dividend History

For each TWSE candidate:

```bash
twstock fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

For each TPEX candidate:

```bash
twstock fetch otc_company.t187ap39-o --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

Look for:
- 3+ consecutive years of cash dividend payments
- Stable or growing dividend amounts
- No years with zero payout

### Step 5 (Optional): Check Revenue Trend

Verify the company's revenue supports continued dividends.

For TWSE:

```bash
twstock fetch company.t187ap05-l --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)"
```

For TPEX:

```bash
twstock fetch otc_company.t187ap05-o --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年同月增減(%)"
```

Declining revenue may signal future dividend cuts.

## Expected Output

A ranked list of dividend candidates from both exchanges:

1. **Top candidates** — Stocks ranked by dividend yield, filtered by P/E and P/B, labeled by exchange
2. **Dividend history** — Payout consistency for top candidates
3. **Risk flags** — Any candidates with declining revenue or irregular payout history

## Troubleshooting

### DividendYield is 0 for many stocks
- Some stocks haven't announced dividends yet for the current year.
- DividendYield is calculated from the most recent declared dividend.

### Very high DividendYield (>15%)
- Likely a one-time special dividend or stock price crash. Check price and dividend history before recommending.

### OTC field names differ from TWSE
- Use `twstock schema otc.mainboard-peratio-analysis --json` to discover exact TPEX field names for `--fields` filtering.

## See Also

- [twstock-ex-dividend-calendar](../twstock-ex-dividend-calendar/SKILL.md) — Check upcoming ex-dividend dates (both exchanges)
- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Deep-dive into individual candidates
- [persona-dividend-investor](../persona-dividend-investor/SKILL.md) — 存股 investor mindset

## Notes

- Taiwan's ex-dividend season concentrates in June-September. Screen in Q1-Q2 for best entry timing.
- High-dividend ETFs (0056, 00919, 00929, 00878) are popular alternatives to individual stock picking.
- Monthly-distribution ETFs (月配息) like 00929 are increasingly popular among younger investors.
- Always cross-reference dividend yield with payout history — a high yield from a one-time special dividend is not sustainable.
- TPEX stocks are sometimes overlooked in dividend screening — don't miss OTC-listed financial and tech stocks with strong yields.
