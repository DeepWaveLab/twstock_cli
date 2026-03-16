# twse-cli

Agent-friendly CLI for Taiwan Stock Exchange (TWSE) OpenAPI — 143 endpoints, one tool.

## Install

```
uv tool install twse-cli
```

With MCP server support:

```
uv tool install 'twse-cli[mcp]'
```

## Quick Start

```bash
# Fetch daily stock data (all stocks)
twse fetch stock.stock-day-all --json

# Filter to specific fields (saves tokens)
twse fetch stock.stock-day-all --json --fields "Code,Name,ClosingPrice"

# Filter by stock code
twse fetch stock.stock-day-all --json --code 2330

# Get PE ratio and dividend yield
twse fetch stock.bwibbu-all --json --code 2330

# Discover endpoints
twse endpoints --search "股利" --json

# Inspect endpoint schema
twse schema stock.stock-day-all --json
```

## Commands

### `twse fetch <endpoint>`

Fetch data from any TWSE endpoint.

```bash
twse fetch stock.stock-day-all --json              # by dotted name
twse fetch /exchangeReport/STOCK_DAY_ALL --json     # by raw API path
twse fetch STOCK_DAY_ALL --json                     # by API code
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

### `twse endpoints`

Discover available endpoints.

```bash
twse endpoints --json                           # list all 143
twse endpoints --search "daily" --json          # search by keyword
twse endpoints --category stock --json          # filter by category
twse endpoints --search "bwibbu" --with-fields --json  # show fields
```

Categories: `stock` (44), `company` (86), `broker` (9), `other` (4).

### `twse schema <endpoint>`

Inspect endpoint fields, inferred types, and example values.

```bash
twse schema stock.stock-day-all --json
```

### `twse serve`

Start as an MCP (Model Context Protocol) server on stdio.

```bash
twse serve
```

Exposes tools: `twse_fetch`, `twse_endpoints`, `twse_schema`. Requires `mcp` extra.

### `twse <command> --help-json`

Output structured command metadata as JSON (flags, types, defaults).

```bash
twse --help-json                  # list all commands
twse fetch --help-json            # list fetch params with types
twse stock --help-json            # list stock subcommands
```

### `--dry-run`

Preview the planned request without making an HTTP call.

```bash
twse fetch stock.stock-day-all --dry-run --fields "Code,Name" --code 2330
```

### `--stdin`

Accept structured JSON input from stdin (CLI flags override stdin values).

```bash
echo '{"endpoint":"stock.stock-day-all","fields":["Code","Name"],"limit":5}' | twse fetch --stdin --json
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
| `TWSE_OUTPUT` | `json`, `human` | Override auto-detection of output format |

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
