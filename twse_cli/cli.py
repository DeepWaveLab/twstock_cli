"""CLI entry point for twse-cli.

Usage:
    twse fetch <endpoint> [--json] [--fields F] [--code C] [--limit N]
    twse endpoints [--json] [--search K] [--category C] [--with-fields]
    twse version
"""

from __future__ import annotations

import json
import logging
import sys

import click

from . import __version__
from .client import TWSEApiError, TWSEClient, TWSENetworkError
from .endpoints import list_endpoints, resolve_endpoint
from .output import (
    console,
    emit_error,
    emit_json,
    filter_by_code,
    filter_fields,
    is_agent_mode,
    render_table,
)

# Exit codes
EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_VALIDATION_ERROR = 2
EXIT_NETWORK_ERROR = 3


@click.group()
@click.version_option(version=__version__, prog_name="twse")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """twse-cli — Agent-friendly Taiwan Stock Exchange data tool."""
    ctx.ensure_object(dict)
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")


@cli.command()
@click.argument("endpoint_ref")
@click.option("--json", "as_json", is_flag=True, help="Output JSON envelope to stdout")
@click.option("--fields", "field_list", default=None, help="Comma-separated fields to include")
@click.option("--code", "stock_code", default=None, help="Filter by stock code")
@click.option("--limit", "max_records", type=int, default=None, help="Limit number of records")
def fetch(endpoint_ref: str, as_json: bool, field_list: str | None, stock_code: str | None, max_records: int | None) -> None:
    """Fetch data from any TWSE endpoint.

    ENDPOINT_REF can be a dotted name (stock.stock-day-all), raw API path
    (/exchangeReport/STOCK_DAY_ALL), or API code (STOCK_DAY_ALL).

    \b
    Examples:
        twse fetch stock.stock-day-all --json
        twse fetch /exchangeReport/STOCK_DAY_ALL --json --fields "Code,Name,ClosingPrice"
        twse fetch stock.bwibbu-all --json --code 2330
    """
    ep = resolve_endpoint(endpoint_ref)
    if not ep:
        if as_json or is_agent_mode():
            emit_error("unknown_endpoint", f"Unknown endpoint: {endpoint_ref}", EXIT_VALIDATION_ERROR)
        console.print(f"[red]Unknown endpoint: {endpoint_ref}[/red]")
        console.print("Use [bold]twse endpoints --search <keyword>[/bold] to discover endpoints.")
        raise SystemExit(EXIT_VALIDATION_ERROR)

    try:
        with TWSEClient() as client:
            data = client.fetch(ep.path)
    except TWSEApiError as exc:
        if as_json or is_agent_mode():
            emit_error("api_error", str(exc), EXIT_API_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_API_ERROR) from None
    except TWSENetworkError as exc:
        if as_json or is_agent_mode():
            emit_error("network_error", str(exc), EXIT_NETWORK_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_NETWORK_ERROR) from None

    # Apply filters
    if stock_code:
        data = filter_by_code(data, stock_code, ep.code_field)
    if field_list:
        data = filter_fields(data, field_list)
    if max_records:
        data = data[:max_records]

    # Output
    if as_json or is_agent_mode():
        emit_json(data)
    else:
        render_table(data, title=f"{ep.description} ({endpoint_ref})")


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output JSON to stdout")
@click.option("--search", "keyword", default=None, help="Search by keyword (en/zh)")
@click.option("--category", default=None, type=click.Choice(["stock", "company", "broker", "other"]), help="Filter by category")
@click.option("--with-fields", is_flag=True, help="Include field definitions")
def endpoints(as_json: bool, keyword: str | None, category: str | None, with_fields: bool) -> None:
    """Discover TWSE OpenAPI endpoints.

    \b
    Examples:
        twse endpoints --json
        twse endpoints --search "股利" --json
        twse endpoints --search "daily" --json
        twse endpoints --category stock --json
        twse endpoints --search "stock.bwibbu" --with-fields --json
    """
    results = list_endpoints(category=category, search=keyword, with_fields=with_fields)

    if as_json or is_agent_mode():
        click.echo(json.dumps(results, ensure_ascii=False))
    else:
        if not results:
            console.print("[dim]No endpoints found.[/dim]")
            return
        from rich.table import Table

        table = Table(title=f"TWSE Endpoints ({len(results)} found)")
        table.add_column("Name", style="bold")
        table.add_column("Group")
        table.add_column("Description")
        table.add_column("Path", style="dim")
        for r in results:
            table.add_row(r["name"], r["group"], r["description"], r["path"])
        console.print(table)


@cli.command()
def version() -> None:
    """Show version information."""
    info = {"name": "twse-cli", "version": __version__, "python": sys.version.split()[0]}
    if is_agent_mode():
        click.echo(json.dumps(info))
    else:
        console.print(f"twse-cli {__version__} (Python {info['python']})")


if __name__ == "__main__":
    cli()
