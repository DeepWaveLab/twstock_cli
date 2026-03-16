---
title: "feat: TWSE CLI — Agent-Friendly Taiwan Stock Exchange Data Tool"
type: feat
date: 2026-03-16
deepened: 2026-03-16
---

# TWSE CLI — Agent-Friendly Taiwan Stock Exchange Data Tool

## Enhancement Summary

**Deepened on:** 2026-03-16
**Research agents used:** best-practices-researcher, framework-docs-researcher, performance-oracle, code-simplicity-reviewer, agent-native-architecture, TWSE-API-researcher, architecture-strategist, security-sentinel, kieran-python-reviewer, agent-native-reviewer, skill-creator

### Key Improvements from Research

1. **`twse fetch <endpoint>` primitive** — Dynamic Capability Discovery pattern replaces Static Tool Mapping. Agents get full API access via 2 commands (fetch + endpoints) on day one; named shortcuts (`twse stock daily`) graduate later from observed usage.
2. **Radical simplification** — MVP is ~300 LOC, 3 core commands, 8 files. Ship in 1 week, not 4.
3. **Drop `--yaml` and pyyaml** — YAML serialization is 20-50x slower than JSON, zero agents use it.
4. **Simplified envelope** — `{"ok": true, "data": [...]}` is sufficient. Remove `schema_version`, `command`, `metadata` (agents already know what they ran; `data.length` exists).
5. **Exit codes in Phase 1** — Agents branch on exit codes, not error text. Must be present from day one.
6. **TWSE API findings** — All values are strings, two naming conventions (English for `/exchangeReport/`, Chinese for `/opendata/`), ROC dates (not ISO 8601), static files on nginx (ETag/Last-Modified present), no pagination.

### New Considerations Discovered

- TWSE API returns `Content-Disposition: attachment` headers — these are **pre-generated static files**, not dynamic endpoints. Rate limiting is unlikely aggressive.
- `普通股每股面額` field contains formatted strings like `"新台幣 10.0000元"` — not clean numeric values.
- `MI_INDEX` uses Chinese field names despite being under `/exchangeReport/` (exception to the English naming pattern).
- SSL verification must be disabled (`verify=False`) due to known TWSE certificate issues (confirmed by MCP server reference).

---

## Overview

Build `twse_cli`, an open-source CLI tool that wraps Taiwan Stock Exchange (TWSE) OpenAPI (143 endpoints, 8 categories) with agent-first design. The tool enables AI agents (Claude Code, Copilot, Cursor, Gemini CLI, etc.) to efficiently query stock market data with minimal token consumption.

**Key differentiator vs existing TWSE MCP Server:** CLI-first distribution — installable via `uv tool install` / `brew install`, works in any terminal or agent environment without MCP server setup.

**Goal:** 使用者的 AI agent 更方便、更省 token 找到資料。

## Problem Statement / Motivation

1. **TWSE OpenAPI is free and auth-free**, but raw API responses are verbose JSON blobs (all values are strings, Chinese field names, ROC dates) that waste agent context windows
2. **No CLI tool exists** for TWSE data — developers must write custom HTTP calls or use MCP servers
3. **MCP servers require setup** (config files, server processes) — a CLI is instantly usable by any agent
4. **143 endpoints are hard to navigate** — agents need discovery (`twse endpoints --search`), field masks (`--fields`), and a generic access primitive (`twse fetch`)

## Technical Approach

### Architecture: Primitives + Graduated Shortcuts

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Agent Documentation                                    │
│  AGENTS.md (includes SKILL.md frontmatter)                      │
│  → Vocabulary, workflows, examples, token-saving tips            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Agent-Safe Execution                                   │
│  TTY-aware | JSON envelope | exit codes | --fields              │
│  → Reliable parsing, token efficiency                            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Agent-Native Interface                                 │
│                                                                  │
│  PRIMITIVES (agent-first, ship Phase 1):                         │
│  ┌──────────────────┐  ┌────────────────────────────────┐       │
│  │ twse endpoints   │  │ twse fetch <endpoint>          │       │
│  │ (discover)       │  │ (access any of 143 endpoints)  │       │
│  └──────────────────┘  └────────────────────────────────┘       │
│                                                                  │
│  DOMAIN SHORTCUTS (human-friendly, ship Phase 2):                │
│  ┌──────┐ ┌─────────┐ ┌─────────┐ ┌────────┐                   │
│  │stock │ │company  │ │broker   │ │...     │                    │
│  │daily │ │info     │ │list     │ │        │                    │
│  │pe    │ │dividend │ │etf-rank │ │        │                    │
│  └──────┘ └─────────┘ └─────────┘ └────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │  Endpoint Registry  │
                    │  (143 endpoints)    │
                    │  endpoints.py       │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴──────────┐
                    │  TWSEClient        │
                    │  httpx + retry     │
                    │  ONE fetch() method│
                    └─────────┬──────────┘
                              │
                    ┌─────────┴──────────┐
                    │  TWSE OpenAPI      │
                    │  openapi.twse.com  │
                    └────────────────────┘
```

**Why `fetch` + `endpoints` as primitives:**
- Agent discovers endpoints: `twse endpoints --search "dividend" --json` (one call)
- Agent fetches any endpoint: `twse fetch stock.daily --json --fields "Code,Name,ClosingPrice"`
- New TWSE endpoint #144 → update `endpoints.py` registry only, no code change
- Named shortcuts (`twse stock daily`) are thin wrappers → Phase 2 sugar

### Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | Python 3.12+ | Same as job104_cli, wide AI agent compatibility |
| CLI Framework | Click | Proven pattern from job104_cli, LazyGroup for 143 commands |
| HTTP Client | httpx | Connection pooling (37% faster), transport-level retry |
| Rich Output | Rich | TTY-aware tables → stderr, `Console(stderr=True)` |
| Package Manager | uv + Hatchling | Modern Python packaging, fast installs |
| Distribution | PyPI + Homebrew tap | `uv tool install twse-cli` / `brew install` |

**Dropped:** pyyaml — YAML serialization is 20-50x slower than JSON, zero agents consume YAML.

### Command Structure

#### Phase 1 MVP (3 commands, all 143 endpoints accessible)

```
twse
├── fetch <endpoint_ref>          # Fetch any endpoint by name or path
│   --json                        # JSON envelope to stdout
│   --fields "Code,Name,..."      # Context window protection
│   --code <stock_code>           # Filter by stock code (client-side)
│   --limit N                     # Limit records returned
├── endpoints                     # Discover all 143 endpoints
│   --json                        # Machine-readable catalog
│   --search <keyword>            # Search by keyword (en/zh)
│   --category <cat>              # Filter by category
│   --with-fields                 # Include field definitions
└── version                       # Version info
```

**Endpoint reference formats accepted by `twse fetch`:**
```bash
twse fetch stock.daily                              # dotted name
twse fetch /exchangeReport/STOCK_DAY_ALL            # raw API path
twse fetch STOCK_DAY_ALL                            # API code
```

#### Phase 2 Domain Shortcuts (human-friendly, delegates to fetch)

```
twse
├── stock                    # 證券交易 (36 APIs)
│   ├── daily                # → twse fetch stock.daily
│   ├── daily-avg            # → twse fetch stock.daily-avg
│   ├── pe-ratio             # → twse fetch stock.pe-ratio
│   └── ...
├── company                  # 公司治理 + 財務報表 (86 APIs)
│   ├── info                 # → twse fetch company.info
│   ├── dividend             # → twse fetch company.dividend
│   └── ...
├── broker                   # 券商資料 (9 APIs)
│   └── ...
└── (index, warrant, news merged into stock/root)
```

**Research Insight:** Merge 7 groups → 3 groups. `finance` → `company` (company financials are company data), `index`+`warrant` → `stock` (too few endpoints to justify own groups), `news` → top-level.

### Agent-Friendly Output Design

#### 1. Simplified Envelope Format

```json
{
  "ok": true,
  "data": [
    {"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00", "Change": "+5.00"}
  ]
}
```

Error envelope:
```json
{
  "ok": false,
  "error": {
    "code": "api_error",
    "message": "TWSE API returned 503"
  }
}
```

**Research Insight (Simplicity):** Removed `schema_version` (version the CLI, not the envelope), `command` (agent knows what it ran), `metadata` (`data.length` exists, `fetched_at` is YAGNI). Add metadata back later if users request it.

#### 2. TTY-Aware Output

| Context | stdout | stderr |
|---------|--------|--------|
| Terminal (TTY) | (empty) | Rich table |
| Pipe / Agent | JSON envelope | (empty) |
| `--json` flag | JSON envelope | (empty) |

**Three-tier cascade:** Explicit `--json` flag > `TWSE_OUTPUT` env var > TTY auto-detection.

#### 3. `--fields` for Context Window Protection

```bash
# Full response — 30+ fields, wastes tokens
twse fetch company.info --json

# Selective — only what agent needs
twse fetch company.info --json --fields "公司代號,公司名稱,董事長"
```

**Implementation:** Simple dict comprehension, no registry validation. Accept any field string, silently omit missing fields:

```python
if fields:
    keys = [f.strip() for f in fields.split(",")]
    data = [{k: row[k] for k in keys if k in row} for row in data]
```

#### 4. Exit Codes (Phase 1, not Phase 4)

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | API error (TWSE returned 4xx/5xx) |
| `2` | Validation error (bad args, unknown endpoint) |
| `3` | Network error (cannot reach TWSE API) |

**Research Insight (Agent-Native):** Agents branch on exit codes, not error text. These must be present from day one.

#### 5. Self-Documenting Discovery

```bash
# Agent discovers dividend-related endpoints
twse endpoints --search "dividend" --json
# Returns: [{"name": "company.dividend", "path": "...", "description": "..."}, ...]

# Agent inspects fields for an endpoint
twse endpoints --search "stock.daily" --with-fields --json
# Returns fields list for that endpoint
```

### Project Structure (MVP)

```
twse_cli/
├── pyproject.toml              # Hatchling build, click+httpx+rich deps
├── LICENSE                     # MIT
├── README.md                   # Quick start, install, usage
├── AGENTS.md                   # Agent doc (includes SKILL.md frontmatter)
├── twse_cli/
│   ├── __init__.py             # __version__
│   ├── cli.py                  # Click root group (LazyGroup in Phase 2)
│   ├── client.py               # TWSEClient — ONE fetch(path) method
│   ├── output.py               # Envelope, TTY detection, --fields, table render
│   ├── endpoints.py            # 143 EndpointDef dataclasses (single source of truth)
│   └── commands/               # (Phase 2: factory-generated domain shortcuts)
│       ├── __init__.py
│       └── _factory.py         # make_endpoint_command, make_group_from_registry
├── tests/
│   ├── test_cli.py             # CliRunner tests
│   ├── test_client.py          # httpx client tests
│   └── test_output.py          # Envelope format, field filtering
└── docs/
    ├── drafts/
    └── plans/
```

**Research Insight (Simplicity):** 8 core files vs original 25+. Eliminated: `constants.py` (one constant belongs in `client.py`), `exceptions.py` (use `click.ClickException`), `renderers/` directory (10-line generic table in `output.py`), `SCHEMA.md` (envelope is self-documenting), `CLAUDE.md` (agent reads `AGENTS.md` directly).

### Client Design (`client.py`)

```python
class TWSEClient:
    """TWSE OpenAPI client with connection pooling, retry, and rate limiting.

    Usage:
        with TWSEClient() as client:
            data = client.fetch("/exchangeReport/STOCK_DAY_ALL")
    """
    BASE_URL = "https://openapi.twse.com.tw/v1"

    def __init__(self, timeout: float = 30.0, request_interval: float = 0.5):
        ...

    def __enter__(self) -> TWSEClient:
        transport = httpx.HTTPTransport(retries=2)
        self._http = httpx.Client(
            base_url=self.BASE_URL,
            transport=transport,
            timeout=httpx.Timeout(connect=10.0, read=timeout, write=10.0, pool=5.0),
            headers={"User-Agent": "twse-cli/0.1.0", "Accept": "application/json"},
            verify=False,  # TWSE API has known SSL certificate issues
        )
        return self

    def fetch(self, path: str) -> list[dict]:
        """Fetch data from any TWSE endpoint. THE ONLY public method."""
        # Rate limit → GET → retry on 5xx → return parsed JSON
        ...
```

**Research Insights:**
- **One `fetch(path)` method**, not 143 individual methods (Simplicity + Kieran)
- **httpx.Client context manager** reuses TCP connections — 37% faster for sequential calls (Performance)
- **Application-level retry** for 429/5xx with exponential backoff — `HTTPTransport(retries=N)` only handles connection errors (Framework Docs)
- **0.5s client-side rate limit** between requests — reference MCP server uses this interval
- **`verify=False`** required due to known TWSE SSL issues (Security: document the reason)

### Endpoint Registry Design

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class EndpointDef:
    path: str                       # "/exchangeReport/STOCK_DAY_ALL"
    cli_name: str                   # "daily"
    group: str                      # "stock"
    description: str                # "每日收盤行情（全部）"
    description_en: str             # "Daily stock closing prices (all)"
    fields: list[str] = field(default_factory=list)
    code_field: str | None = None   # "Code" or "公司代號" — for --code filter

ENDPOINTS: dict[str, EndpointDef] = {
    "stock.daily": EndpointDef(
        path="/exchangeReport/STOCK_DAY_ALL",
        cli_name="daily", group="stock",
        description="每日收盤行情（全部）",
        description_en="Daily stock closing prices (all)",
        fields=["Code", "Name", "TradeVolume", "TradeValue",
                "OpeningPrice", "HighestPrice", "LowestPrice",
                "ClosingPrice", "Change", "Transaction"],
        code_field="Code",
    ),
    # ... all 143 endpoints
}

def resolve_endpoint(ref: str) -> EndpointDef | None:
    """Resolve dotted name, raw path, or API code to EndpointDef."""
    ...

def list_endpoints(category=None, search=None) -> list[dict]:
    """Discovery primitive — agents call this first."""
    ...
```

**Research Insights (Kieran Python):** Use `dataclass(frozen=True, slots=True)` not dicts. Frozen = immutable (safety). Slots = less memory for 143 instances.

### TWSE API Data Characteristics

> **Critical finding from live API research:**

| Characteristic | Detail |
|---------------|--------|
| All values are strings | Prices: `"75.15"`, volumes: `"115111624"`, dates: `"1150313"` |
| Missing values = `""` | Empty string, not `null` |
| Dates use ROC calendar | `"1150313"` = 2026-03-13 (ROC year + 1911 = Gregorian) |
| Two naming conventions | `/exchangeReport/*` uses English fields (`Code`, `ClosingPrice`); `/opendata/*` uses Chinese (`公司代號`, `收盤指數`) |
| Exception: `MI_INDEX` | Under `/exchangeReport/` but uses Chinese field names |
| No pagination | Every endpoint returns complete dataset in one response |
| Static files on nginx | `ETag`/`Last-Modified` headers present; pre-generated, not computed on demand |
| Response sizes | 46 KB (MI_INDEX) to 2.87 MB (STOCK_DAY_AVG_ALL) |
| Formatted text in numeric fields | `普通股每股面額` = `"新台幣 10.0000元"` — not a clean number |

**Decision:** Pass through raw TWSE data as-is for MVP. Field normalization (string→number, ROC→ISO dates) is Phase 3.

---

## Implementation Phases

### Phase 1: MVP — Primitives (Week 1)

**Goal:** All 143 endpoints accessible via `twse fetch`. Ship to PyPI.

**Tasks:**
- [x] Initialize project: `pyproject.toml` (click, httpx, rich), uv setup
- [x] `twse_cli/client.py` — TWSEClient with httpx, single `fetch(path)` method, retry, rate limiting
- [x] `twse_cli/endpoints.py` — All 143 EndpointDef entries (dataclass registry)
- [x] `twse_cli/output.py` — Envelope, TTY detection, `--fields` filtering, generic Rich table
- [x] `twse_cli/cli.py` — `twse fetch`, `twse endpoints`, `twse version`
- [x] Exit codes: 0=success, 1=API error, 2=validation, 3=network
- [x] Tests: envelope format, client retry, `CliRunner` for fetch/endpoints
- [x] `AGENTS.md` with SKILL.md frontmatter (install, quick start, vocabulary, workflows)
- [x] `README.md` with Quick Start
- [ ] Publish to PyPI: `uv build && uv publish`

**Files (8 core):**
```
pyproject.toml, README.md, AGENTS.md,
twse_cli/__init__.py, twse_cli/cli.py, twse_cli/client.py,
twse_cli/output.py, twse_cli/endpoints.py,
tests/test_cli.py, tests/test_client.py, tests/test_output.py
```

**Success Criteria:**
- [x] `twse fetch stock.stock-day-all --json` returns valid `{"ok": true, "data": [...]}`
- [x] `twse fetch stock.stock-day-all --json --fields "Code,Name,ClosingPrice"` filters fields
- [x] `twse fetch stock.stock-day-all` shows Rich table in terminal
- [x] `twse fetch stock.stock-day-all --json | jq '.data[0]'` works (pipe mode)
- [x] `twse endpoints --json` lists all 143 endpoints
- [x] `twse endpoints --search "股利" --json` finds dividend endpoints
- [x] `twse fetch NONEXISTENT` exits with code 2 and structured error JSON
- [ ] `uv tool install twse-cli && twse fetch stock.stock-day-all --json` works end-to-end
- [x] `twse fetch stock.stock-day-all --json --code 2330` returns only TSMC record

### Phase 2: Domain Shortcuts + Distribution (Week 2)

**Goal:** Named commands for human convenience. Homebrew tap.

**Tasks:**
- [x] `twse_cli/commands/_factory.py` — `make_endpoint_command()`, `make_group_from_registry()`
- [x] `twse_cli/cli.py` — LazyGroup loading for `stock`, `company`, `broker` subgroups
- [x] `twse stock daily` → thin wrapper over `twse fetch stock.daily`
- [x] `twse company info` → thin wrapper over `twse fetch company.info`
- [x] `twse broker list` → thin wrapper over `twse fetch broker.list`
- [x] Merge groups: `finance` → `company`, `index`+`warrant` → `stock`, `news` → root
- [x] `TWSE_OUTPUT` env var for session-wide default format
- [x] Setup GitHub Actions for PyPI publish
- [x] Setup Homebrew tap formula
- [x] Disk-based response cache with TTL tiers (daily=4h, static=24h)

**Files added:**
```
twse_cli/commands/__init__.py, twse_cli/commands/_factory.py,
twse_cli/commands/stock.py, twse_cli/commands/company.py,
twse_cli/commands/broker.py,
.github/workflows/publish.yml
```

**Success Criteria:**
- [x] `twse stock daily --json` works as alias for `twse fetch stock.daily --json`
- [x] All 143 endpoints have named commands under 3 groups
- [x] `twse --help` fast (LazyGroup defers imports)
- [ ] `brew install <user>/tap/twse-cli` works (formula created, needs PyPI publish first)
- [x] Second fetch of same endpoint hits cache (< 5ms vs 2-4s)

### Phase 3: Polish & Advanced (Optional, based on user feedback)

- [x] Data normalization: string→number, ROC→ISO dates (opt-in `--normalize`)
- [x] `twse schema <endpoint>` — runtime schema introspection (fields, types, examples)
- [x] NDJSON streaming (`--ndjson`) for large datasets
- [x] `--raw` flag for pipe composability (bare JSON array, no envelope)
- [x] `--code` client-side filter with early-exit optimization
- [x] `CONTEXT.md` / `gemini-extension.json` / `.github/copilot-instructions.md` for other agents
- [x] `twse serve` — MCP server mode (reuse same client/endpoints)

---

## Acceptance Criteria

### Functional Requirements

- [x] All 143 TWSE OpenAPI endpoints accessible via `twse fetch <endpoint>`
- [x] `twse endpoints` self-documenting command with `--search`, `--category`, `--with-fields`
- [x] `--json` flag on every command (auto-detect when piped)
- [x] `--fields` flag for context window protection
- [x] TTY-aware output: Rich tables for humans (stderr), JSON for agents (stdout)
- [x] Structured exit codes: 0=success, 1=API error, 2=validation, 3=network
- [x] Structured error JSON envelope on failures

### Non-Functional Requirements

- [ ] Installable via `uv tool install twse-cli` (needs PyPI publish)
- [x] Python 3.12+ compatible
- [x] No authentication required (TWSE API is public)
- [x] Response time < 5s for any single command
- [x] Minimal dependencies: click, rich, httpx (3 deps, no pyyaml)

### Quality Gates

- [x] Envelope format tested with JSON parse (not string matching)
- [x] CLI invocation tests for fetch/endpoints commands
- [x] `ruff` linting passes
- [x] `pytest` passes (69 tests)

## Dependencies & Prerequisites

- TWSE OpenAPI available at https://openapi.twse.com.tw (public, no auth)
- Python 3.12+
- GitHub account for repo + Homebrew tap
- PyPI account for package publishing

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| TWSE API rate limiting | Medium | High | 0.5s client-side interval, retry with backoff |
| TWSE SSL certificate issues | High | Low | `verify=False` with documented reason |
| Response sizes up to 2.87MB | Medium | Medium | `--fields` filter before serialization (2.2x faster, 5x smaller) |
| All values are strings | High | Low | Pass through as-is for MVP; normalize in Phase 3 |
| Dual field naming (EN/ZH) | High | Medium | `code_field` in registry handles both `Code` and `公司代號` |
| ROC dates confuse agents | Medium | Medium | Document in AGENTS.md; normalize in Phase 3 |

## Success Metrics

1. **Agent token efficiency**: `twse fetch stock.daily --fields "Code,ClosingPrice" --json` returns < 50% tokens vs raw API
2. **Installation time**: < 30s from `uv tool install twse-cli` to first query
3. **Discovery**: Agent finds any endpoint via `twse endpoints --search <keyword> --json`
4. **Composability test**: Agent can answer "Find stocks with PE < 15 and dividend yield > 4%" using only `twse fetch` + `twse endpoints` — no new code needed

## Alternative Approaches Considered

### 1. 143 Named Commands from Day One (Original Plan, Revised)
- Original plan proposed all named commands in Phase 1-2
- Research showed `fetch` + `endpoints` primitives cover 100% of use cases
- Named commands graduated to Phase 2 as syntactic sugar
- **Decision:** Primitives first, shortcuts later

### 2. MCP Server Only (Rejected)
- Requires server setup and config per agent platform
- CLI is universally accessible from any terminal/agent
- **Decision:** CLI-first, MCP can layer on later via `twse serve`

### 3. Rust/Go CLI (Rejected)
- Better binary distribution but slower iteration
- Python matches job104_cli ecosystem and agent tooling
- **Decision:** Python + uv provides fast enough distribution

## Future Considerations

- **MCP Server Mode**: `twse serve` to run as MCP server (reuse same client/endpoints)
- **TPEX Support**: Taipei Exchange (櫃買中心) has similar OpenAPI at tpex.org.tw
- **Data Pipeline**: `twse export --from 2025-01 --to 2026-03 --format csv`
- **Disk Caching**: TTL-tiered disk cache (daily=4h, static=24h) for repeated queries

## References

### Internal References

- job104_cli patterns: `/Users/weirenlan/Desktop/self_project/labs/job104_cli/`
  - `cli.py` — Click group + command registration pattern
  - `client.py` — httpx client with retry, rate limiting
  - `commands/_common.py` — envelope, TTY-aware output
  - `pyproject.toml` — uv + hatchling packaging
- Agent-friendly CLI research: `job104_cli/docs/plans/2026-03-15-feat-agent-friendly-cli-mechanisms-plan.md`
- TWSE MCP Server reference: https://github.com/twjackysu/TWSEMCPServer

### External References

- TWSE OpenAPI: https://openapi.twse.com.tw/
- AGENTS.md spec: https://agents.md/ (60,000+ repos adopted)
- GitHub Blog: How to write a great agents.md: https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
- OpenClaw Skills: https://docs.openclaw.ai/tools/skills
- better-cli: CLI best practices for humans and AI: https://github.com/yogin16/better-cli
- Click LazyGroup: https://click.palletsprojects.com/en/stable/complex/#defining-multi-commands
- httpx connection pooling: https://www.python-httpx.org/advanced/clients/

### API Coverage

| Category | Endpoints | Phase 1 (fetch) | Phase 2 (named) |
|----------|-----------|-----------------|-----------------|
| 公司治理 + 財務報表 | 86 | `twse fetch company.*` | `twse company <cmd>` |
| 證券交易 + 指數 + 權證 | 44 | `twse fetch stock.*` | `twse stock <cmd>` |
| 券商資料 | 9 | `twse fetch broker.*` | `twse broker <cmd>` |
| 其他 | 4 | `twse fetch news.*` | top-level commands |
| **Total** | **143** | **All via `twse fetch`** | **3 groups** |
