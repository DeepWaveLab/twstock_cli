"""MCP server mode — expose twstock-cli as a Model Context Protocol server.

Usage:
    twstock serve              # Start MCP server on stdio
    python -m twstock_cli.serve  # Direct execution

Exposes tools:
    - twstock_fetch: Fetch data from any TWSE/TPEX endpoint
    - twstock_endpoints: Discover and search endpoints
    - twstock_schema: Inspect endpoint schema
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

import click

from .client import TWStockApiError, TWStockClient, TWStockNetworkError
from .endpoints import list_endpoints, resolve_endpoint
from .normalize import normalize_data
from .sanitize import sanitize_data
from .schema import analyze_schema
from .validate import validate_input

mcp = FastMCP(
    "twstock-cli",
    json_response=True,
)


@mcp.tool()
def twstock_fetch(
    endpoint: str,
    fields: str = "",
    code: str = "",
    limit: int = 0,
    normalize: bool = False,
    date: str = "",
) -> dict[str, Any]:
    """Fetch data from any TWSE endpoint (OpenAPI or web API).

    Args:
        endpoint: Endpoint reference — dotted name (stock.stock-day-all),
                  raw path (/exchangeReport/STOCK_DAY_ALL), or API code (STOCK_DAY_ALL).
        fields: Comma-separated field names to include (e.g. "Code,Name,ClosingPrice").
                Empty string returns all fields.
        code: Filter by stock code (e.g. "2330"). Empty string means no filter.
        limit: Maximum number of records to return. 0 means no limit.
        normalize: If true, convert string→number and ROC→ISO dates.
        date: Date in YYYYMMDD format (for web API endpoints like T86). Empty = today.

    Returns:
        Standard envelope: {"ok": true, "data": [...]} or {"ok": false, "error": {...}}
    """
    # Validate user-supplied inputs
    try:
        endpoint = validate_input(endpoint, "endpoint")
        if fields:
            fields = validate_input(fields, "fields")
        if code:
            code = validate_input(code, "code")
    except click.BadParameter as exc:
        return {"ok": False, "error": {"code": "validation_error", "message": str(exc)}}

    ep = resolve_endpoint(endpoint)
    if not ep:
        return {"ok": False, "error": {"code": "unknown_endpoint", "message": f"Unknown endpoint: {endpoint}"}}

    try:
        with TWStockClient() as client:
            if ep.base_url:
                params = dict(ep.default_params)
                if date:
                    params["date"] = date
                data = client.fetch_web(ep.base_url, ep.path, params)
            else:
                data = client.fetch(ep.path)
    except TWStockApiError as exc:
        return {"ok": False, "error": {"code": "api_error", "message": str(exc)}}
    except TWStockNetworkError as exc:
        return {"ok": False, "error": {"code": "network_error", "message": str(exc)}}

    # Sanitize response strings
    data = sanitize_data(data)

    # Apply field aliases (web API endpoints have verbose Chinese field names)
    if ep.field_aliases:
        from .commands._factory import _apply_field_aliases

        data = _apply_field_aliases(data, ep.field_aliases)

    # Apply filters
    if code:
        from .output import filter_by_code

        data = filter_by_code(data, code, ep.code_field)
    if normalize:
        data = normalize_data(data)
    if fields:
        from .output import filter_fields

        data = filter_fields(data, fields)
    if limit > 0:
        data = data[:limit]

    return {"ok": True, "data": data}


@mcp.tool()
def twstock_endpoints(
    search: str = "",
    category: str = "",
    with_fields: bool = False,
) -> list[dict[str, Any]]:
    """Discover TWSE OpenAPI endpoints.

    Args:
        search: Search keyword (Chinese or English). Empty string returns all.
        category: Filter by category: stock, company, broker, other. Empty string returns all.
        with_fields: Include field definitions in output.

    Returns:
        List of endpoint descriptors with name, path, group, description.
    """
    # Validate user-supplied inputs
    try:
        if search:
            search = validate_input(search, "search")
    except click.BadParameter as exc:
        return {"ok": False, "error": {"code": "validation_error", "message": str(exc)}}

    return list_endpoints(
        category=category or None,
        search=search or None,
        with_fields=with_fields,
    )


@mcp.tool()
def twstock_schema(endpoint: str) -> dict[str, Any]:
    """Inspect schema of a TWSE endpoint (field names, types, examples).

    Fetches sample data and analyzes field characteristics.

    Args:
        endpoint: Endpoint reference (dotted name, raw path, or API code).

    Returns:
        Schema info with field names, inferred types, examples, and non-empty percentages.
    """
    # Validate user-supplied input
    try:
        endpoint = validate_input(endpoint, "endpoint")
    except click.BadParameter as exc:
        return {"ok": False, "error": {"code": "validation_error", "message": str(exc)}}

    ep = resolve_endpoint(endpoint)
    if not ep:
        return {"ok": False, "error": {"code": "unknown_endpoint", "message": f"Unknown endpoint: {endpoint}"}}

    try:
        with TWStockClient() as client:
            data = client.fetch(ep.path)
    except TWStockApiError as exc:
        return {"ok": False, "error": {"code": "api_error", "message": str(exc)}}
    except TWStockNetworkError as exc:
        return {"ok": False, "error": {"code": "network_error", "message": str(exc)}}

    data = sanitize_data(data)

    return analyze_schema(
        data,
        endpoint_name=f"{ep.group}.{ep.cli_name}",
        description=ep.description,
        path=ep.path,
    )


def run_server() -> None:
    """Start the MCP server on stdio transport."""
    mcp.run()


if __name__ == "__main__":
    run_server()
