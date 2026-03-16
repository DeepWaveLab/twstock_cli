# twse-cli

Agent-friendly CLI for Taiwan Stock Exchange (TWSE) OpenAPI.

## Install

```
uv tool install twse-cli
```

## Quick Start

```bash
# Fetch daily stock data
twse fetch stock.daily --json

# Filter fields for token efficiency
twse fetch stock.daily --json --fields "Code,Name,ClosingPrice"

# Filter by stock code
twse fetch stock.daily --json --code 2330

# Discover endpoints
twse endpoints --search "dividend" --json

# List all endpoints
twse endpoints --json
```
