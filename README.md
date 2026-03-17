# twstock-cli

Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX) — stock market data, one tool.

## Install

```bash
pip install twstock-cli
```

With optional extras:

```bash
pip install 'twstock-cli[mcp]'            # MCP server support
pip install 'twstock-cli[analysis]'       # pandas, openpyxl, matplotlib, plotly
pip install 'twstock-cli[mcp,analysis]'   # everything
```

### From source

```bash
git clone https://github.com/weirenlan/twstock-cli.git
cd twstock-cli
uv sync                                   # core only
uv sync --extra mcp --extra analysis      # with all extras
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

Fetch data from any TWSE/TPEX endpoint.

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
twstock endpoints --json                           # list all 359
twstock endpoints --search "daily" --json          # search by keyword
twstock endpoints --category stock --json          # filter by category
twstock endpoints --search "bwibbu" --with-fields --json  # show fields
```

**Sources:** 143 TWSE OpenAPI + 9 TWSE Web API + 207 TPEX OpenAPI = 359 endpoints.

Categories: `stock` (45), `company` (86), `broker` (9), `other` (4), `otc` (64), `otc_company` (29), `otc_index` (18), `otc_esg` (16), `otc_financial` (32), `otc_warrant` (16), `otc_bond` (8), `otc_broker` (8), `otc_esb` (5), `otc_gisa` (5), `otc_fund` (3), `otc_gold` (3), `web` (8).

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

## Data Analysis & Export (`[analysis]` extra)

Install the `analysis` extra to unlock data analysis, visualization, and export capabilities.

### Export to XLSX

```python
import subprocess, json, pandas as pd

result = subprocess.run(
    ["twstock", "fetch", "stock.stock-day-all", "--json", "--fields", "Code,Name,ClosingPrice,TradeVolume", "--normalize"],
    capture_output=True, text=True,
)
data = json.loads(result.stdout)["data"]
df = pd.DataFrame(data)
df.to_excel("stock_daily.xlsx", index=False)
```

### Visualization with matplotlib

```python
import subprocess, json, pandas as pd, matplotlib.pyplot as plt

result = subprocess.run(
    ["twstock", "fetch", "stock.stock-day-all", "--json", "--fields", "Code,Name,ClosingPrice,TradeVolume", "--normalize", "--limit", "20"],
    capture_output=True, text=True,
)
df = pd.DataFrame(json.loads(result.stdout)["data"])
df.plot.bar(x="Name", y="TradeVolume", title="Top 20 Stocks by Volume")
plt.tight_layout()
plt.savefig("volume_chart.png")
```

### Interactive charts with plotly

```python
import subprocess, json, pandas as pd, plotly.express as px

result = subprocess.run(
    ["twstock", "fetch", "stock.stock-day-all", "--json", "--fields", "Code,Name,ClosingPrice,TradeVolume", "--normalize", "--limit", "30"],
    capture_output=True, text=True,
)
df = pd.DataFrame(json.loads(result.stdout)["data"])
fig = px.scatter(df, x="ClosingPrice", y="TradeVolume", hover_name="Name", title="Price vs Volume")
fig.write_html("price_vs_volume.html")
```

### Export to PPTX

```python
from pptx import Presentation
from pptx.util import Inches
import subprocess, json

result = subprocess.run(
    ["twstock", "fetch", "stock.stock-day-all", "--json", "--fields", "Code,Name,ClosingPrice", "--limit", "10", "--normalize"],
    capture_output=True, text=True,
)
data = json.loads(result.stdout)["data"]

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])  # blank layout
slide.shapes.title.text = "Top 10 Stocks"

rows, cols = len(data) + 1, 3
table = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(9), Inches(4)).table
for i, header in enumerate(["Code", "Name", "ClosingPrice"]):
    table.cell(0, i).text = header
for r, row in enumerate(data, 1):
    for c, key in enumerate(["Code", "Name", "ClosingPrice"]):
        table.cell(r, c).text = str(row.get(key, ""))

prs.save("stocks.pptx")
```

### Analysis extras included

| Package | Purpose |
|---------|---------|
| `pandas` | DataFrames, filtering, groupby, `.to_excel()`, `.to_csv()` |
| `openpyxl` | XLSX read/write (powers `pandas.to_excel()`) |
| `matplotlib` | Static charts and plots |
| `plotly` | Interactive HTML charts |
| `python-pptx` | PowerPoint slide generation (included in core) |

## For AI Agents

See [AGENTS.md](AGENTS.md) for agent-specific instructions, workflows, and token-saving tips.

## License

MIT
