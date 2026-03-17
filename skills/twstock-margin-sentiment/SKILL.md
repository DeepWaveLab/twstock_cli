---
name: twstock-margin-sentiment
description: "Analyze margin trading balances as a retail investor sentiment indicator."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Margin Sentiment (融資融券)

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format and token-saving conventions.

Analyze margin trading (融資融券) balances as a sentiment indicator for retail investor positioning and risk.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available (updates after market close)

## Background

Margin trading data is a key sentiment indicator in Taiwan's retail-dominated market:

- **融資 (Margin Financing):** Investors borrow money to buy stocks. High balance = bullish retail sentiment.
- **融券 (Short Selling):** Investors borrow shares to sell short. High balance = bearish bets.
- **融資維持率 (Margin Maintenance Ratio):** When this drops below 130%, brokers issue margin calls and force liquidation (斷頭). This often marks market bottoms — a contrarian buy signal.

## Workflow

### Step 1: Fetch Overall Margin Balance

```bash
twstock fetch stock.mi-margn --json --limit 20 --normalize
```

Returns margin financing and short-selling balances across the market.

### Step 2: Check Suspended Margin Trading Stocks

```bash
twstock fetch stock.bfi84u --json
```

Lists stocks where margin trading has been suspended (停資停券). This often signals regulatory concern about volatility.

### Step 3: Interpret Signals

Analyze the margin data for sentiment signals:

| Signal | Interpretation |
|--------|---------------|
| Rising margin financing balance | Retail investors are leveraging up (bullish sentiment) |
| Falling margin financing balance | Retail deleveraging (bearish sentiment or forced selling) |
| High short-selling balance | Bearish bets accumulating |
| Maintenance ratio < 130% | Margin call territory — forced liquidation risk |
| Maintenance ratio < 120% | Extreme stress — often marks market bottoms |

## Expected Output

1. **Overall margin balance** — Total financing and short-selling amounts
2. **Suspended stocks** — Stocks with margin restrictions
3. **Sentiment reading** — Bullish/bearish/neutral based on margin trends

## Troubleshooting

### Margin data appears stale
- Margin data updates after 18:00 Taiwan time (later than price data).
- Check trading calendar: `twstock fetch stock.holidayschedule --json`

## See Also

- [twstock-market-overview](../twstock-market-overview/SKILL.md) — Includes margin data in daily snapshot
- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Individual stock data

## Notes

- Taiwan's margin maintenance ratio (融資維持率) is one of the most effective contrarian indicators in the market.
- Historically, market-wide margin call events (大量斷頭) have preceded significant rebounds.
- Individual stock margin data can reveal crowded retail positions that may unwind during corrections.
- Combine margin sentiment with institutional flow for a complete positioning picture.
