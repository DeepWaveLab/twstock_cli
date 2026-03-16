"""CLI entry point for twse-cli.

Usage:
    twse fetch <endpoint> [--json] [--fields F] [--code C] [--limit N]
    twse endpoints [--json] [--search K] [--category C] [--with-fields]
    twse stock <command> [options]    # Domain shortcuts
    twse company <command> [options]  # Domain shortcuts
    twse broker <command> [options]   # Domain shortcuts
    twse version
"""

from __future__ import annotations

import json
import logging
import sys

import click

from . import __version__
from .endpoints import list_endpoints, resolve_endpoint
from .output import (
    console,
    emit_error,
    is_agent_mode,
)

# Exit codes
EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_VALIDATION_ERROR = 2
EXIT_NETWORK_ERROR = 3


class LazyGroup(click.Group):
    """Click group that defers loading domain subgroups until needed.

    This keeps `twse --help` fast by not importing 143 command definitions
    until a subgroup is actually invoked.
    """

    def __init__(self, *args, lazy_subgroups: dict[str, str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._lazy_subgroups: dict[str, str] = lazy_subgroups or {}

    def list_commands(self, ctx: click.Context) -> list[str]:
        base = super().list_commands(ctx)
        lazy = sorted(self._lazy_subgroups.keys())
        return base + [name for name in lazy if name not in base]

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.BaseCommand | None:
        # Check eagerly registered commands first
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv

        # Lazy-load domain subgroup
        if cmd_name in self._lazy_subgroups:
            return self._load_group(cmd_name)

        return None

    def _load_group(self, name: str) -> click.BaseCommand:
        from .commands._factory import make_group

        grp = make_group(name)
        # Cache it so we don't rebuild on next access
        self.add_command(grp, name)
        return grp


@click.group(cls=LazyGroup, lazy_subgroups={
    "stock": "twse_cli.commands._factory",
    "company": "twse_cli.commands._factory",
    "broker": "twse_cli.commands._factory",
})
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
@click.option("--no-cache", is_flag=True, help="Bypass disk cache")
def fetch(endpoint_ref: str, as_json: bool, field_list: str | None, stock_code: str | None, max_records: int | None, no_cache: bool) -> None:
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

    from .commands._factory import _run_fetch

    _run_fetch(ep, as_json, field_list, stock_code, max_records, no_cache=no_cache)


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
