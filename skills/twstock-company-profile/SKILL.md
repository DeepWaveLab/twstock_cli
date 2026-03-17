---
name: twstock-company-profile
description: "Company fundamentals deep-dive — profile, income statement, balance sheet, shareholders, dividends, and governance for both TWSE and TPEX."
version: 2.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twstock"]
    skills: ["twstock-shared"]
---

# Company Profile

> **PREREQUISITE:** Read `../twstock-shared/SKILL.md` for output format, token-saving conventions, and exchange detection.

Perform a comprehensive company fundamentals deep-dive combining basic info, financial statements, shareholder structure, dividend history, and governance data. Supports both TWSE (上市) and TPEX (上櫃) companies.

## Preconditions

- `twstock` CLI installed and accessible
- Know the stock code (e.g., `2330` for TSMC, `6510` for 精測)
- Financial statements are updated quarterly

## Workflow

Replace `<CODE>` with the target stock code.

### Step 0: Determine Exchange

```bash
twstock fetch stock.stock-day-all --json --code <CODE> --limit 1
```

If data is non-empty → TWSE listed. Use **TWSE endpoints** below.

If data is empty:

```bash
twstock fetch otc.mainboard-daily-close-quotes --json --code <CODE> --limit 1
```

If data is non-empty → TPEX listed. Use **TPEX endpoints** below.

---

### Step 1: Company Basic Info

**TWSE:**
```bash
twstock fetch company.t187ap03-l --json --code <CODE> --fields "公司代號,公司名稱,公司簡稱,產業別,住址,董事長,總經理,成立日期,上市日期,實收資本額"
```

**TPEX:**
```bash
twstock fetch otc_company.t187ap03-o --json --code <CODE> --fields "公司代號,公司名稱,公司簡稱,產業別,住址,董事長,總經理,成立日期,上櫃日期,實收資本額"
```

### Step 2: Income Statement (一般業)

**TWSE:**
```bash
twstock fetch company.t187ap06-l-ci --json --code <CODE>
```

**TPEX:**
```bash
twstock fetch otc_financial.t187ap06-o-ci --json --code <CODE>
```

For other industries, use the appropriate variant:
- Financial industry: `company.t187ap06-l-basi` / `otc_financial.t187ap06-o-basi`
- Securities/futures: `company.t187ap06-l-bd` / `otc_financial.t187ap06-o-bd`
- Financial holding: `company.t187ap06-l-fh` / `otc_financial.t187ap06-o-fh`
- Insurance: `company.t187ap06-l-ins` / `otc_financial.t187ap06-o-ins`

### Step 3: Balance Sheet (一般業)

**TWSE:**
```bash
twstock fetch company.t187ap07-l-ci --json --code <CODE>
```

**TPEX:**
```bash
twstock fetch otc_financial.t187ap07-o-ci --json --code <CODE>
```

For other industries, use the matching `t187ap07-*` variant.

### Step 4: Major Shareholders (>10%)

**TWSE:**
```bash
twstock fetch company.t187ap02-l --json --code <CODE>
```

**TPEX:**
```bash
twstock fetch otc_company.t187ap02-o --json --code <CODE>
```

### Step 5: Dividend History

**TWSE:**
```bash
twstock fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

**TPEX:**
```bash
twstock fetch otc_company.t187ap39-o --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

### Step 6: Board Composition

**TWSE:**
```bash
twstock fetch company.t187ap11-l --json --code <CODE>
```

**TPEX:**
```bash
twstock fetch otc_company.t187ap11-o --json --code <CODE>
```

### Step 7 (Optional): ESG Data

**TWSE:**
```bash
twstock fetch company.t187ap46-l-1 --json --code <CODE>   # Greenhouse gas
twstock fetch company.t187ap46-l-6 --json --code <CODE>   # Board governance
twstock fetch company.t187ap46-l-13 --json --code <CODE>  # Supply chain
```

**TPEX:**
```bash
twstock fetch otc_esg.t187ap46-o-1 --json --code <CODE>   # Greenhouse gas
twstock fetch otc_esg.t187ap46-o-6 --json --code <CODE>   # Board governance
twstock fetch otc_esg.t187ap46-o-13 --json --code <CODE>  # Supply chain
```

TPEX has 16 ESG topic categories available via `otc_esg.t187ap46-o-*`.

## Expected Output

1. **Exchange** — TWSE (上市) or TPEX (上櫃)
2. **Company overview** — Name, industry, leadership, listing date, capital
3. **Financial performance** — Key income statement metrics (revenue, operating income, net income, EPS)
4. **Financial health** — Balance sheet highlights (total assets, liabilities, equity, debt ratio)
5. **Ownership** — Major shareholders and their stakes
6. **Dividend track record** — Historical payouts and consistency
7. **Governance** — Board composition and director holdings
8. **ESG** (optional) — Key sustainability metrics

## Troubleshooting

### Wrong income statement variant
- Most companies are "一般業" (general industry) — use `t187ap06-*-ci`.
- Check the company's `產業別` from Step 1 to pick the correct variant.
- Financial industry includes banks, securities firms, insurance, and financial holding companies.

### Empty financial data
- Financial statements update quarterly with a ~45 day lag after quarter end.
- Q1 data: available by mid-May, Q2: mid-August, Q3: mid-November, Q4/Annual: mid-March.

### TPEX financial endpoint variants
- Use `twstock endpoints --group otc_financial --json` to discover available TPEX financial statement variants.

## See Also

- [twstock-stock-lookup](../twstock-stock-lookup/SKILL.md) — Quick overview with price and valuation
- [twstock-revenue-tracker](../twstock-revenue-tracker/SKILL.md) — Monthly revenue trends
- [twstock-dividend-screener](../twstock-dividend-screener/SKILL.md) — Screen across all companies

## Notes

- This is the most comprehensive skill — use it for due diligence or research reports.
- For a quick check, use `twstock-stock-lookup` instead (Steps 1-4 only).
- Always run Step 0 first to determine the exchange — do not assume TWSE.
- Company endpoints all use Chinese field names. Use `twstock schema <endpoint> --json` to discover fields.
- The income statement endpoint varies by industry — always check `產業別` first.
- ESG data covers 16-21 categories depending on exchange. Only fetch the ones relevant to your analysis.
