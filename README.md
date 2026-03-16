# twse-cli

Agent-friendly CLI for Taiwan Stock Exchange (TWSE) OpenAPI — 143 endpoints, one tool.

## Install

```
uv tool install twse-cli
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

# List all 143 endpoints
twse endpoints --json
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
| `--json` | JSON output (auto-detected when piped) |
| `--fields "Code,Name"` | Select specific fields |
| `--code 2330` | Filter by stock code |
| `--limit 10` | Limit records returned |

### `twse endpoints`

Discover available endpoints.

```bash
twse endpoints --json                           # list all 143
twse endpoints --search "daily" --json          # search by keyword
twse endpoints --category stock --json          # filter by category
twse endpoints --search "bwibbu" --with-fields --json  # show fields
```

Categories: `stock` (44), `company` (86), `broker` (9), `other` (4).

## Output Format

```json
{"ok": true, "data": [{"Code": "2330", "Name": "台積電", "ClosingPrice": "1865.00"}]}
```

Exit codes: `0` success, `1` API error, `2` validation error, `3` network error.

## For AI Agents

See [AGENTS.md](AGENTS.md) for agent-specific instructions, workflows, and token-saving tips.

## License

MIT
