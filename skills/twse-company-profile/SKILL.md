---
name: twse-company-profile
description: "Company fundamentals deep-dive — profile, income statement, balance sheet, shareholders, dividends, and governance."
version: 1.0.0
metadata:
  category: "recipe"
  requires:
    bins: ["twse"]
    skills: ["twse-shared"]
---

# Company Profile

> **PREREQUISITE:** Read `../twse-shared/SKILL.md` for output format and token-saving conventions.

Perform a comprehensive company fundamentals deep-dive combining basic info, financial statements, shareholder structure, dividend history, and governance data.

## Preconditions

- `twse` CLI installed and accessible
- Know the stock code (e.g., `2330` for TSMC)
- Financial statements are updated quarterly

## Workflow

Replace `<CODE>` with the target stock code.

### Step 1: Company Basic Info

```bash
twse fetch company.t187ap03-l --json --code <CODE> --fields "公司代號,公司名稱,公司簡稱,產業別,住址,董事長,總經理,成立日期,上市日期,實收資本額"
```

Returns company name, industry, chairman, CEO, founding date, listing date, and paid-in capital.

### Step 2: Income Statement (一般業)

```bash
twse fetch company.t187ap06-l-ci --json --code <CODE>
```

Returns the comprehensive income statement for general industry companies.

For other industries, use the appropriate endpoint:
- Financial industry: `company.t187ap06-l-basi`
- Securities/futures: `company.t187ap06-l-bd`
- Financial holding: `company.t187ap06-l-fh`
- Insurance: `company.t187ap06-l-ins`

### Step 3: Balance Sheet (一般業)

```bash
twse fetch company.t187ap07-l-ci --json --code <CODE>
```

Returns the balance sheet for general industry companies.

For other industries, use the matching `t187ap07-l-*` variant.

### Step 4: Major Shareholders (>10%)

```bash
twse fetch company.t187ap02-l --json --code <CODE>
```

Lists shareholders holding more than 10% of outstanding shares.

### Step 5: Dividend History

```bash
twse fetch company.t187ap45-l --json --code <CODE> --fields "公司代號,公司名稱,股利年度,股東配發-盈餘分配之現金股利(元/股),股東配發-盈餘轉增資配股(元/股)"
```

Returns historical dividend distributions by year.

### Step 6: Board Composition

```bash
twse fetch company.t187ap11-l --json --code <CODE>
```

Returns director and supervisor shareholding details.

### Step 7 (Optional): ESG Data

```bash
# Greenhouse gas emissions
twse fetch company.t187ap46-l-1 --json --code <CODE>

# Board governance
twse fetch company.t187ap46-l-6 --json --code <CODE>

# Supply chain management
twse fetch company.t187ap46-l-13 --json --code <CODE>
```

Returns ESG disclosure data across 21 categories.

## Expected Output

1. **Company overview** — Name, industry, leadership, listing date, capital
2. **Financial performance** — Key income statement metrics (revenue, operating income, net income, EPS)
3. **Financial health** — Balance sheet highlights (total assets, liabilities, equity, debt ratio)
4. **Ownership** — Major shareholders and their stakes
5. **Dividend track record** — Historical payouts and consistency
6. **Governance** — Board composition and director holdings
7. **ESG** (optional) — Key sustainability metrics

## Troubleshooting

### Wrong income statement variant
- Most companies are "一般業" (general industry) — use `t187ap06-l-ci`.
- Check the company's `產業別` from Step 1 to pick the correct variant.
- Financial industry includes banks, securities firms, insurance, and financial holding companies.

### Empty financial data
- Financial statements update quarterly with a ~45 day lag after quarter end.
- Q1 data: available by mid-May, Q2: mid-August, Q3: mid-November, Q4/Annual: mid-March.

## See Also

- [twse-stock-lookup](../twse-stock-lookup/SKILL.md) — Quick overview with price and valuation
- [twse-revenue-tracker](../twse-revenue-tracker/SKILL.md) — Monthly revenue trends
- [twse-dividend-screener](../twse-dividend-screener/SKILL.md) — Screen across all companies

## Notes

- This is the most comprehensive skill — use it for due diligence or research reports.
- For a quick check, use `twse-stock-lookup` instead (Steps 1-4 only).
- Company endpoints all use Chinese field names. Use `twse schema <endpoint> --json` to discover fields.
- The income statement endpoint varies by industry — always check `產業別` first.
- ESG data (Step 7) covers 21 categories. Only fetch the ones relevant to your analysis.
