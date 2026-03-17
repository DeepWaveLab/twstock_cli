---
name: twstock-margin-sentiment
description: "Analyze margin trading balances as a retail investor sentiment indicator for both TWSE and TPEX markets."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Margin Sentiment (融資融券)

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Analyze margin trading (融資融券) balances as a sentiment indicator for retail investor positioning and risk, covering both TWSE and TPEX markets. TPEX has 10 margin-related endpoints providing richer data than TWSE.

## Preconditions

- `twstock` CLI installed and accessible
- Market data available (updates after market close)

## Background

Margin trading data is a key sentiment indicator in Taiwan's retail-dominated market:

- **融資 (Margin Financing):** Investors borrow money to buy stocks. High balance = bullish retail sentiment.
- **融券 (Short Selling):** Investors borrow shares to sell short. High balance = bearish bets.
- **融資維持率 (Margin Maintenance Ratio):** When this drops below 130%, brokers issue margin calls and force liquidation (斷頭). This often marks market bottoms — a contrarian buy signal.

TPEX provides richer margin data than TWSE, including short-sell rankings and margin usage rates.

## Workflow

### TWSE Margin Data

#### Step 1: Fetch Overall Margin Balance (TWSE)

```bash
twstock fetch stock.mi-margn --json --limit 20 --normalize
```

Returns TWSE margin financing and short-selling balances across the market.

#### Step 2: Check Suspended Margin Trading Stocks (TWSE)

```bash
twstock fetch stock.bfi84u --json
```

Lists TWSE stocks where margin trading has been suspended (停資停券).

### TPEX Margin Data

#### Step 3: Fetch OTC Margin Balance

```bash
twstock fetch otc.mainboard-margin-balance --json --limit 20 --normalize
```

Returns TPEX margin financing and short-selling balances.

#### Step 4: Fetch OTC Margin + Short-Sell Balance

```bash
twstock fetch otc.margin-sbl --json --normalize
```

Combined margin and SBL (securities borrowing and lending) balance for OTC market.

#### Step 5: Fetch OTC Short-Sell Rankings

```bash
twstock fetch otc.margin-trading-short-sell --json --normalize
```

Lists OTC stocks ranked by short-selling volume — identifies the most shorted TPEX stocks.

#### Step 6: Fetch OTC Margin Usage Rate

```bash
twstock fetch otc.margin-trading-margin-used --json --normalize
```

Shows margin usage rates for OTC stocks — high usage rate means retail is heavily leveraged.

### Analysis

#### Step 7: Interpret Signals

Analyze the margin data from both exchanges for sentiment signals:

| Signal | Interpretation |
|--------|---------------|
| Rising margin financing balance | Retail investors are leveraging up (bullish sentiment) |
| Falling margin financing balance | Retail deleveraging (bearish sentiment or forced selling) |
| High short-selling balance | Bearish bets accumulating |
| Maintenance ratio < 130% | Margin call territory — forced liquidation risk |
| Maintenance ratio < 120% | Extreme stress — often marks market bottoms |
| High OTC margin usage rate | OTC retail heavily leveraged — higher volatility risk |
| Top shorted OTC stocks rising | Short squeeze potential |

## Expected Output

1. **TWSE margin overview** — Total financing and short-selling amounts, suspended stocks
2. **TPEX margin overview** — OTC margin balance, SBL data, short-sell rankings
3. **Top shorted stocks** — Most-shorted OTC stocks (potential squeeze candidates)
4. **Sentiment reading** — Bullish/bearish/neutral based on combined margin trends
5. **Divergence signals** — When TWSE and TPEX margin trends diverge

## Troubleshooting

### Margin data appears stale
- Margin data updates after 18:00 Taiwan time (later than price data).
- Check trading calendar: `twstock fetch stock.holidayschedule --json`

### OTC margin endpoint field names
- Use `twstock schema otc.mainboard-margin-balance --json` to verify exact field names.

## See Also

- [twstock-market-overview](../twstock-market-overview/SKILL.md) — Includes margin data in daily snapshot
- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Individual stock data

## Notes

- Taiwan's margin maintenance ratio (融資維持率) is one of the most effective contrarian indicators in the market.
- Historically, market-wide margin call events (大量斷頭) have preceded significant rebounds.
- Individual stock margin data can reveal crowded retail positions that may unwind during corrections.
- Combine margin sentiment with institutional flow for a complete positioning picture.
- TPEX margin data (Steps 3-6) is richer than TWSE's single `mi-margn` endpoint — use it for deeper analysis.
