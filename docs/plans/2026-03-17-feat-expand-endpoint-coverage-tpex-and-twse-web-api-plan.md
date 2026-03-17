---
title: "feat: Expand endpoint coverage — TPEX OpenAPI + TWSE web API"
type: feat
date: 2026-03-17
---

# Expand endpoint coverage — TPEX OpenAPI + TWSE web API

## Overview

The CLI currently covers **all 143 TWSE OpenAPI endpoints** plus 1 TWSE web API endpoint (T86). There are two major expansion opportunities:

1. **TPEX OpenAPI** (tpex.org.tw) — 225 endpoints for OTC market (上櫃/興櫃) data, completely uncovered
2. **TWSE Web API** (www.twse.com.tw) — date-parameterized endpoints enabling **historical queries** not possible with OpenAPI snapshots

## Problem Statement / Motivation

- Users asking about OTC stocks (e.g., "What's the price of 6547?") get no data — the CLI only covers TWSE-listed (上市) stocks
- OpenAPI endpoints only return today's snapshot — no way to query historical data by date
- Taiwan's stock market has ~1,000 TWSE-listed stocks but also ~800 TPEX-listed OTC stocks — missing half the market
- The T86 web API pattern already works; extending it to more endpoints is low-risk

## Research Findings

### Current State

| Source | Total Endpoints | In CLI | Gap |
|--------|----------------|--------|-----|
| TWSE OpenAPI (openapi.twse.com.tw) | 143 | 143 | 0 |
| TWSE Web API (www.twse.com.tw/rwd/zh) | ~15 key ones | 1 (T86) | ~14 |
| TPEX OpenAPI (www.tpex.org.tw/openapi/v1) | 225 | 0 | 225 |

### TPEX OpenAPI Breakdown (225 endpoints)

| Category | Count | Examples |
|----------|-------|---------|
| Stock Trading (tpex_*) | 108 | Daily quotes, institutional trading, margin, warrants, indices |
| Company Financials (mopsfin_*) | 70 | Revenue, balance sheets, income statements, directors |
| ESG/Governance (t187ap46_O_*) | 18 | ESG disclosures (mirrors TWSE ESG endpoints) |
| Bonds (bond_*) | 12 | Government/corporate bond issuance data |
| Other (indices, gold, etc.) | 17 | TPEX 50 index, gold spot, salary index |

TPEX OpenAPI uses the **same JSON format** as TWSE OpenAPI (list of dicts with English field names for stock endpoints, Chinese for company endpoints). Base URL: `https://www.tpex.org.tw/openapi/v1`

### TWSE Web API Key Endpoints (not in OpenAPI)

These use `www.twse.com.tw/rwd/zh` base and return `{stat, fields, data}` format (like T86):

| Path | Description | Params |
|------|-------------|--------|
| `/afterTrading/STOCK_DAY` | Individual stock daily OHLCV | `stockNo`, `date` |
| `/fund/BFI82U` | 三大法人買賣金額統計表 | `date` |
| `/afterTrading/BWIBBU` | Individual stock P/E, yield, PBR by month | `stockNo`, `date` |
| `/afterTrading/FMSRFK` | Individual stock monthly trading info | `stockNo`, `date` |
| `/afterTrading/MI_INDEX` | Daily market closing (tables format) | `date` |
| `/fund/TWT38U` | Foreign investor buy/sell by industry | `date` |
| `/fund/TWT43U` | Investment trust buy/sell by industry | `date` |
| `/fund/TWT44U` | Dealer buy/sell by industry | `date` |

These are the **only way to get historical data** — the OpenAPI always returns today's snapshot.

## Proposed Solution

### Architecture Changes

1. **Multi-source endpoint registry** — Add a `source` field to `EndpointDef` to distinguish `twse_openapi`, `twse_web`, and `tpex_openapi`
2. **TPEX client support** — Add `TPEX_BASE_URL = "https://www.tpex.org.tw/openapi/v1"` to `client.py`; TPEX uses the same `fetch()` method (returns list of dicts)
3. **Date parameters for web API** — Extend `EndpointDef` with optional `date_param` and `stock_param` fields for web API endpoints that accept query parameters

### Implementation Phases

#### Phase 1: TPEX OpenAPI Core (highest value, lowest effort)

Add the ~40 most useful TPEX endpoints that mirror popular TWSE endpoints:

**Stock trading (must-have):**
- `tpex_mainboard_daily_close_quotes` — OTC daily quotes (mirrors `STOCK_DAY_ALL`)
- `tpex_mainboard_quotes` — OTC closing quotes
- `tpex_3insti_daily_trading` — OTC institutional buy/sell (mirrors T86)
- `tpex_3insti_summary` — OTC institutional summary
- `tpex_3insti_qfii_trading` — OTC foreign investor trading
- `tpex_3insti_qfii` — OTC foreign investor holdings ranking
- `tpex_3insti_qfii_industry` — OTC foreign investor holdings by industry
- `tpex_mainboard_margin_balance` — OTC margin balance (mirrors `MI_MARGN`)
- `tpex_mainboard_peratio_analysis` — OTC P/E, yield, PBR (mirrors `BWIBBU_ALL`)
- `tpex_exright_prepost` — OTC ex-dividend schedule (mirrors `TWT48U_ALL`)
- `tpex_exright_daily` — OTC ex-dividend results
- `tpex_index` — TPEX index history
- `tpex_intraday_trading_statistics` — OTC day trading stats
- `tpex_odd_stock` — OTC odd-lot trading
- `tpex_off_market` — OTC after-hours pricing
- `tpex_mainborad_highlight` — OTC market summary
- `tpex_daily_trading_index` — OTC daily trading volume/value
- `tpex_esb_latest_statistics` — Emerging stock board quotes

**Company financials (must-have):**
- `mopsfin_t187ap03_O` — OTC company basic data (mirrors `t187ap03_L`)
- `mopsfin_t187ap05_O` — OTC monthly revenue (mirrors `t187ap05_L`)
- `mopsfin_t187ap06_O_ci` — OTC income statement, general (mirrors `t187ap06_L_ci`)
- `mopsfin_t187ap07_O_ci` — OTC balance sheet, general (mirrors `t187ap07_L_ci`)
- `mopsfin_t187ap11_O` — OTC director holdings (mirrors `t187ap11_L`)
- `mopsfin_t187ap14_O` — OTC industry EPS stats (mirrors `t187ap14_L`)
- `mopsfin_t187ap39_O` — OTC dividend info

**Changes:**
- `twse_cli/endpoints.py` — Add ~40 new `EndpointDef` entries with `base_url="https://www.tpex.org.tw/openapi/v1"` and `group` prefixed with `tpex_`
- `twse_cli/client.py` — No changes needed; `fetch()` already supports custom base_url via the `fetch_web()` pattern, but for TPEX we can just create a second client or add a base_url override to `fetch()`
- `twse_cli/commands/_factory.py` — May need to handle TPEX base URL routing

**Acceptance criteria:**
- [x] `twse endpoints --search 上櫃 --json` returns TPEX endpoints
- [x] `twse fetch otc.mainboard-daily-close-quotes --json` returns OTC stock data
- [x] `twse fetch otc_company.t187ap05-o --code 6547 --json` returns OTC company revenue
- [x] `twse endpoints --category otc` lists all TPEX endpoints

#### Phase 2: Remaining TPEX Endpoints (bulk add)

Add the remaining ~185 TPEX endpoints:
- All 108 `tpex_*` stock trading endpoints
- All 70 `mopsfin_*` company financial endpoints
- All 18 ESG endpoints
- All 12 bond endpoints
- All 17 index/other endpoints

This can potentially be **auto-generated** from the TPEX swagger.json spec.

**Changes:**
- `twse_cli/endpoints.py` — Add remaining entries (could be script-generated)
- Script: `scripts/generate_tpex_endpoints.py` — Parse swagger.json and generate `EndpointDef` entries

**Acceptance criteria:**
- [x] All 207 TPEX endpoints registered (swagger.json has 207, not 225 as initially estimated)
- [x] `twstock endpoints --json | python3 -c "import json,sys; print(len(json.load(sys.stdin)['data']))"` returns 351 (144 + 207)

#### Phase 3: TWSE Web API Historical Endpoints

Add date-parameterized TWSE web API endpoints (~10-15).

**Changes:**
- `twse_cli/endpoints.py` — Add web API endpoints with `base_url`, `default_params`, `field_aliases` (like T86)
- `twse_cli/endpoints.py` — Add new optional fields: `date_param: str | None` and `stock_param: str | None` to `EndpointDef`
- `twse_cli/commands/_factory.py` — Generate `--date` and `--stock-no` Click options for endpoints that have `date_param`/`stock_param`
- Handle the `tables` response format (MI_INDEX returns `{tables: [{title, fields, data}, ...]}`) as a variant of `fetch_web`

**Key endpoints:**
- `twse_web.stock-day` — `/afterTrading/STOCK_DAY` (per-stock daily OHLCV by month)
- `twse_web.bfi82u` — `/fund/BFI82U` (institutional summary by type)
- `twse_web.bwibbu` — `/afterTrading/BWIBBU` (per-stock P/E history)
- `twse_web.fmsrfk` — `/afterTrading/FMSRFK` (per-stock monthly history)

**Acceptance criteria:**
- [x] `twse fetch stock-day --stock-no 2330 --date 20260301 --json` returns TSMC's March 2026 daily data
- [x] `twse fetch bfi82u --date 20260316 --json` returns institutional buy/sell summary
- [x] `--date` option auto-generated only for web API endpoints that support it

## Technical Considerations

### Client Architecture

The current `TWSEClient` has two methods:
- `fetch(path)` — For OpenAPI endpoints (base URL: `openapi.twse.com.tw/v1`)
- `fetch_web(base_url, path, params)` — For web API endpoints (custom base URL, `fields+data` format)

For TPEX, we need a third pattern: same format as `fetch()` (list of dicts) but different base URL. Options:

1. **Add `base_url` param to `fetch()`** — Simplest. If `EndpointDef.base_url` is set, use it instead of default.
2. **Create `TPEXClient`** — More separation but unnecessary duplication.

**Recommended: Option 1** — minimal change, consistent with existing T86 pattern.

### Endpoint Naming Convention

Current: `{group}.{cli_name}` (e.g., `stock.stock-day-all`)

For TPEX: Use `tpex_stock.{cli_name}` or `otc.{cli_name}` prefix:
- `otc.mainboard-daily-close-quotes`
- `otc.3insti-daily-trading`
- `otc_company.t187ap05-o`

For TWSE web: Use `web.{cli_name}` prefix:
- `web.stock-day`
- `web.bfi82u`

### Rate Limiting

TPEX may have different rate limits than TWSE. The existing 0.5s interval should be safe but may need per-source tuning.

### Endpoint Count in Docs

Update `endpoints.py` module docstring, `CLAUDE.md`, `AGENTS.md` to reflect new totals.

## Success Metrics

- Endpoint count: 144 → 369+ (after TPEX) → 380+ (after web API)
- OTC stock queries work end-to-end
- Historical date-range queries work for key TWSE endpoints
- Existing 144 endpoints remain fully functional (no regressions)

## Dependencies & Risks

| Risk | Mitigation |
|------|-----------|
| TPEX API rate limiting / blocking | Use same 0.5s interval, add retry logic |
| TPEX field names inconsistent | Map during Phase 1, standardize aliases |
| TWSE web API format varies (tables vs fields+data) | Handle both in `fetch_web()` |
| Massive endpoint count slows CLI startup | Already using LazyGroup; endpoint registry is just dicts |
| TPEX SSL issues (like TWSE) | Already using `verify=False` |

## References & Research

### Data Sources Confirmed Working
- TWSE OpenAPI Swagger: https://openapi.twse.com.tw/v1/swagger.json (143 endpoints)
- TPEX OpenAPI Swagger: https://www.tpex.org.tw/openapi/swagger.json (225 endpoints)
- TWSE Web API: `https://www.twse.com.tw/rwd/zh/{path}?response=json`

### Internal References
- `twse_cli/endpoints.py` — Endpoint registry (144 entries currently)
- `twse_cli/client.py:147-224` — `fetch_web()` method (T86 pattern to reuse)
- `twse_cli/commands/_factory.py` — Dynamic command generation
