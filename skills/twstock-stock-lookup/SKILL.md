---
name: twstock-stock-lookup
description: "Comprehensive single-stock lookup — price, valuation, company info, revenue, and dividends for both TWSE and TPEX stocks."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Stock Lookup

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Get a comprehensive view of a single stock by combining price, valuation, company fundamentals, revenue, and dividend data. Supports both TWSE (上市) and TPEX (上櫃) stocks.

## Preconditions

- `twstock` CLI installed and accessible
- Know the stock code (e.g., `2330` for TSMC, `6510` for 精測)
- If unsure of the code, search: `twstock endpoints --search "台積電" --json`

## Workflow

Replace `<CODE>` with the target stock code (e.g., `2330`).

### Step 0: Determine Exchange

```bash
twstock fetch stock.stock-day-all --json --code <CODE> --limit 1
```

If data is non-empty → TWSE listed. Use the **TWSE path** below.

If data is empty:

```bash
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --limit 1
```

If data is non-empty → TPEX listed. Use the **TPEX path** below.

---

### TWSE Path (上市)

#### Step 1: Fetch Daily Price and Volume

```bash
twstock fetch stock.stock-day-all --json --code <CODE> --fields "Code,Name,TradeVolume,TradeValue,OpeningPrice,HighestPrice,LowestPrice,ClosingPrice,Change,Transaction" --normalize
```

#### Step 2: Fetch Valuation Metrics

```bash
twstock fetch stock.bwibbu-all --json --code <CODE> --fields "Code,Name,PEratio,DividendYield,PBratio" --normalize
```

#### Step 3: Fetch Company Profile

```bash
twstock fetch company.t187ap03-l --json --code <CODE> --fields "公司代號,公司名稱,公司簡稱,產業別,董事長,總經理,成立日期,上市日期,實收資本額"
```

#### Step 4: Fetch Latest Revenue

```bash
twstock fetch company.t187ap05-l --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年當月營收,營業收入-去年同月增減(%)"
```

#### Step 5 (Optional): Fetch Dividend History

```bash
twstock fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

---

### TPEX Path (上櫃)

#### Step 1: Fetch Daily Price and Volume

```bash
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --normalize
```

#### Step 2: Fetch Valuation Metrics

```bash
twstock fetch otc.mainboard-peratio-analysis --json --code <CODE> --normalize
```

#### Step 3: Fetch Company Profile

```bash
twstock fetch otc_company.t187ap03-o --json --code <CODE> --fields "公司代號,公司名稱,公司簡稱,產業別,董事長,總經理,成立日期,上櫃日期,實收資本額"
```

#### Step 4: Fetch Latest Revenue

```bash
twstock fetch otc_company.t187ap05-o --json --code <CODE> --fields "資料年月,公司代號,公司名稱,營業收入-當月營收,營業收入-去年當月營收,營業收入-去年同月增減(%)"
```

#### Step 5 (Optional): Fetch Dividend History

```bash
twstock fetch otc_company.t187ap39-o --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

---

### Step 6 (Optional): Fetch Historical Data via Web API

For multi-month price history on a specific stock (works for both TWSE and TPEX):

```bash
twstock fetch web.stock-day --date 20260301 --stock-no <CODE> --json
twstock fetch web.bwibbu --date 20260301 --stock-no <CODE> --json
```

## Expected Output

Combine the data into a stock summary:

1. **Exchange** — TWSE (上市) or TPEX (上櫃)
2. **Price** — Current closing price, daily change, volume, and value
3. **Valuation** — P/E ratio, dividend yield, P/B ratio
4. **Company** — Industry, chairman, CEO, listing date, capital
5. **Revenue** — Latest monthly revenue and YoY growth rate
6. **Dividends** (optional) — Recent dividend history and payout amounts

## Troubleshooting

### Stock code not found on either exchange
- Verify the code exists: try both `stock.stock-day-all` and `otc.mainboard-daily-close-quotes`
- The stock may be on the emerging board (興櫃): check `otc_esb.*` endpoints
- Some codes are ETFs or special instruments — try: `twstock endpoints --search "<CODE>" --json`

### Company data returns empty
- Company endpoints may have delayed updates compared to stock price endpoints.
- Some fields may be empty for recently listed companies.

## See Also

- [twstock-stock-compare](../twstock-stock-compare/SKILL.md) — Compare multiple stocks side-by-side (supports cross-exchange)
- [twstock-company-profile](../twstock-company-profile/SKILL.md) — Full company deep-dive with financials

## Notes

- This is the most common skill — use it whenever a user asks about a specific stock.
- Always run Step 0 first to determine the exchange. Do not assume a stock is TWSE-listed.
- Major TPEX stocks include: 精測(6510), 信驊(5274), 力旺(3529), 富邦媒(8454).
- All company endpoint fields use Chinese names. Use `twstock schema <endpoint> --json` to discover exact field names.
- Web API (Step 6) provides historical data not available from the daily snapshot endpoints.
