# twstock-cli

Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX) — stock market data, one tool.

## Install

```
uv tool install twstock-cli
```

With MCP server support:

```
uv tool install 'twstock-cli[mcp]'
```

## Quick Start

```bash
# Fetch daily stock data (all stocks)
twstock fetch stock.stock-day-all --json

# Filter to specific fields (saves tokens)
twstock fetch stock.stock-day-all --json --fields "Code,Name,ClosingPrice"

# Filter by stock code
twstock fetch stock.stock-day-all --json --code 2330

# Get PE ratio and dividend yield
twstock fetch stock.bwibbu-all --json --code 2330

# Discover endpoints
twstock endpoints --search "股利" --json

# Inspect endpoint schema
twstock schema stock.stock-day-all --json
```

## Commands

### `twstock fetch <endpoint>`

Fetch data from any TWSE endpoint.

```bash
twstock fetch stock.stock-day-all --json              # by dotted name
twstock fetch /exchangeReport/STOCK_DAY_ALL --json     # by raw API path
twstock fetch STOCK_DAY_ALL --json                     # by API code
```

| Flag | Description |
|------|-------------|
| `--json` | JSON envelope output (auto-detected when piped) |
| `--fields "Code,Name"` | Select specific fields |
| `--code 2330` | Filter by stock code |
| `--limit 10` | Limit records returned |
| `--normalize` | Convert strings to numbers, ROC dates to ISO 8601 |
| `--ndjson` | Newline-delimited JSON (one record per line) |
| `--raw` | Bare JSON array without envelope |
| `--dry-run` | Preview request as JSON without making an HTTP call |
| `--stdin` | Read parameters from JSON on stdin |
| `--no-cache` | Bypass disk cache |

### `twstock endpoints`

Discover available endpoints.

```bash
twstock endpoints --json                           # list all 143
twstock endpoints --search "daily" --json          # search by keyword
twstock endpoints --category stock --json          # filter by category
twstock endpoints --search "bwibbu" --with-fields --json  # show fields
```

Categories: `stock` (44), `company` (86), `broker` (9), `other` (4).

### `twstock schema <endpoint>`

Inspect endpoint fields, inferred types, and example values.

```bash
twstock schema stock.stock-day-all --json
```

### `twstock serve`

Start as an MCP (Model Context Protocol) server on stdio.

```bash
twstock serve
```

Exposes tools: `twstock_fetch`, `twstock_endpoints`, `twstock_schema`. Requires `mcp` extra.

### `twstock <command> --help-json`

Output structured command metadata as JSON (flags, types, defaults).

```bash
twstock --help-json                  # list all commands
twstock fetch --help-json            # list fetch params with types
twstock stock --help-json            # list stock subcommands
```

### `--dry-run`

Preview the planned request without making an HTTP call.

```bash
twstock fetch stock.stock-day-all --dry-run --fields "Code,Name" --code 2330
```

### `--stdin`

Accept structured JSON input from stdin (CLI flags override stdin values).

```bash
echo '{"endpoint":"stock.stock-day-all","fields":["Code","Name"],"limit":5}' | twstock fetch --stdin --json
```

## Output Formats

### JSON envelope (default)

```json
{"ok": true, "data": [{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}]}
```

### NDJSON (`--ndjson`)

```
{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}
{"Code": "2317", "Name": "鴻海", "ClosingPrice": "100.50"}
```

### Raw (`--raw`)

```json
[{"Code": "2330", "Name": "台積電"}, {"Code": "2317", "Name": "鴻海"}]
```

### Normalized (`--normalize`)

```json
{"ok": true, "data": [{"Code": "2330", "ClosingPrice": 595.0, "TradeVolume": 36317450}]}
```

## Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `TWSTOCK_OUTPUT` | `json`, `human` | Override auto-detection of output format |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | API error (TWSE returned 4xx/5xx) |
| `2` | Validation error (unknown endpoint, bad args) |
| `3` | Network error (cannot reach TWSE API) |

## For AI Agents

See [AGENTS.md](AGENTS.md) for agent-specific instructions, workflows, and token-saving tips.

## License

MIT
