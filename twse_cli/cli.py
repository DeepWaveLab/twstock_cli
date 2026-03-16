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
from .help_json import help_json_option
from .validate import validate_input

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
@help_json_option
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """twse-cli — Agent-friendly Taiwan Stock Exchange data tool."""
    ctx.ensure_object(dict)
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")


@cli.command()
@click.argument("endpoint_ref", required=False, default=None)
@click.option("--json", "as_json", is_flag=True, help="Output JSON envelope to stdout")
@click.option("--fields", "field_list", default=None, help="Comma-separated fields to include")
@click.option("--code", "stock_code", default=None, help="Filter by stock code")
@click.option("--limit", "max_records", type=int, default=None, help="Limit number of records")
@click.option("--no-cache", is_flag=True, help="Bypass disk cache")
@click.option("--normalize", is_flag=True, help="Normalize data: string→number, ROC→ISO dates")
@click.option("--ndjson", is_flag=True, help="Output as newline-delimited JSON")
@click.option("--raw", is_flag=True, help="Output bare JSON array (no envelope)")
@click.option("--dry-run", is_flag=True, help="Preview request as JSON without making an HTTP call")
@click.option("--stdin", "use_stdin", is_flag=True, help="Read parameters from JSON on stdin")
@click.option("--date", default=None, help="Date in YYYYMMDD format (for web API endpoints like T86)")
@help_json_option
def fetch(endpoint_ref: str | None, as_json: bool, field_list: str | None, stock_code: str | None, max_records: int | None, no_cache: bool, normalize: bool, ndjson: bool, raw: bool, dry_run: bool, use_stdin: bool, date: str | None) -> None:
    """Fetch data from any TWSE endpoint.

    ENDPOINT_REF can be a dotted name (stock.stock-day-all), raw API path
    (/exchangeReport/STOCK_DAY_ALL), or API code (STOCK_DAY_ALL).

    \b
    Examples:
        twse fetch stock.stock-day-all --json
        twse fetch /exchangeReport/STOCK_DAY_ALL --json --fields "Code,Name,ClosingPrice"
        twse fetch stock.bwibbu-all --json --code 2330
        twse fetch stock.stock-day-all --json --normalize
        twse fetch stock.stock-day-all --ndjson
        twse fetch stock.stock-day-all --raw
        echo '{"endpoint":"stock.stock-day-all"}' | twse fetch --stdin --json
    """
    # Parse stdin JSON if --stdin is set
    stdin_data: dict = {}
    if use_stdin:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            emit_error("validation_error", "No input received on stdin", EXIT_VALIDATION_ERROR)
        try:
            stdin_data = json.loads(raw_input)
        except json.JSONDecodeError as e:
            emit_error("validation_error", f"Invalid JSON on stdin: {e}", EXIT_VALIDATION_ERROR)
        if not isinstance(stdin_data, dict):
            emit_error("validation_error", "Stdin JSON must be an object", EXIT_VALIDATION_ERROR)

    # Merge: CLI flags override stdin values
    endpoint_ref = endpoint_ref or stdin_data.get("endpoint")
    if not endpoint_ref:
        emit_error("validation_error", "Missing endpoint: provide ENDPOINT_REF argument or 'endpoint' in stdin JSON", EXIT_VALIDATION_ERROR)

    fields_from_stdin = stdin_data.get("fields")
    if fields_from_stdin and not field_list:
        field_list = ",".join(fields_from_stdin) if isinstance(fields_from_stdin, list) else fields_from_stdin
    stock_code = stock_code or stdin_data.get("code")
    if max_records is None and stdin_data.get("limit") is not None:
        max_records = int(stdin_data["limit"])
    if not normalize and stdin_data.get("normalize"):
        normalize = True
    if not ndjson and stdin_data.get("ndjson"):
        ndjson = True
    if not raw and stdin_data.get("raw"):
        raw = True
    if not no_cache and stdin_data.get("no_cache"):
        no_cache = True
    if not dry_run and stdin_data.get("dry_run"):
        dry_run = True
    if not date and stdin_data.get("date"):
        date = stdin_data["date"]

    # Validate user-supplied inputs
    try:
        endpoint_ref = validate_input(endpoint_ref, "ENDPOINT_REF")
        if field_list:
            field_list = validate_input(field_list, "--fields")
        if stock_code:
            stock_code = validate_input(stock_code, "--code")
    except click.BadParameter as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("validation_error", str(exc), EXIT_VALIDATION_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_VALIDATION_ERROR) from None

    ep = resolve_endpoint(endpoint_ref)
    if not ep:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("unknown_endpoint", f"Unknown endpoint: {endpoint_ref}", EXIT_VALIDATION_ERROR)
        console.print(f"[red]Unknown endpoint: {endpoint_ref}[/red]")
        console.print("Use [bold]twse endpoints --search <keyword>[/bold] to discover endpoints.")
        raise SystemExit(EXIT_VALIDATION_ERROR)

    from .commands._factory import _run_fetch

    _run_fetch(ep, as_json, field_list, stock_code, max_records, no_cache=no_cache, normalize=normalize, ndjson=ndjson, raw=raw, dry_run=dry_run, date=date)


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output JSON to stdout")
@click.option("--search", "keyword", default=None, help="Search by keyword (en/zh)")
@click.option("--category", default=None, type=click.Choice(["stock", "company", "broker", "other"]), help="Filter by category")
@click.option("--with-fields", is_flag=True, help="Include field definitions")
@help_json_option
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
    # Validate search keyword
    if keyword:
        try:
            keyword = validate_input(keyword, "--search")
        except click.BadParameter as exc:
            if as_json or is_agent_mode():
                emit_error("validation_error", str(exc), EXIT_VALIDATION_ERROR)
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(EXIT_VALIDATION_ERROR) from None

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
@click.argument("endpoint_ref")
@click.option("--json", "as_json", is_flag=True, help="Output JSON to stdout")
@click.option("--no-cache", is_flag=True, help="Bypass disk cache")
@click.option("--dry-run", is_flag=True, help="Preview request as JSON without making an HTTP call")
@help_json_option
def schema(endpoint_ref: str, as_json: bool, no_cache: bool, dry_run: bool) -> None:
    """Inspect schema of a TWSE endpoint (fields, types, examples).

    Fetches a sample from the endpoint and analyzes field characteristics.

    \b
    Examples:
        twse schema stock.stock-day-all --json
        twse schema company.t187ap03-l
    """
    # Validate user-supplied input
    try:
        endpoint_ref = validate_input(endpoint_ref, "ENDPOINT_REF")
    except click.BadParameter as exc:
        if as_json or is_agent_mode():
            emit_error("validation_error", str(exc), EXIT_VALIDATION_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_VALIDATION_ERROR) from None

    ep = resolve_endpoint(endpoint_ref)
    if not ep:
        if as_json or is_agent_mode():
            emit_error("unknown_endpoint", f"Unknown endpoint: {endpoint_ref}", EXIT_VALIDATION_ERROR)
        console.print(f"[red]Unknown endpoint: {endpoint_ref}[/red]")
        raise SystemExit(EXIT_VALIDATION_ERROR)

    # Dry-run: show what schema fetch would do
    if dry_run:
        from .client import BASE_URL

        preview = {
            "dry_run": True,
            "command": "schema",
            "method": "GET",
            "url": f"{BASE_URL}{ep.path}",
            "endpoint": f"{ep.group}.{ep.cli_name}",
        }
        click.echo(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    from .client import TWSEApiError, TWSEClient, TWSENetworkError

    try:
        with TWSEClient(use_cache=not no_cache) as client:
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

    from .sanitize import sanitize_data
    from .schema import analyze_schema

    data = sanitize_data(data)

    schema_info = analyze_schema(
        data, endpoint_name=f"{ep.group}.{ep.cli_name}", description=ep.description, path=ep.path
    )

    if as_json or is_agent_mode():
        click.echo(json.dumps(schema_info, ensure_ascii=False))
    else:
        from rich.table import Table

        console.print(f"\n[bold]{ep.group}.{ep.cli_name}[/bold] — {ep.description}")
        console.print(f"[dim]Path: {ep.path} | Records: {schema_info['record_count']}[/dim]\n")

        table = Table(title="Fields")
        table.add_column("Field", style="bold")
        table.add_column("Type")
        table.add_column("Example", style="dim")
        table.add_column("Non-empty %")
        for f in schema_info["fields"]:
            table.add_row(f["name"], f["type"], str(f["example"]), f"{f['non_empty_pct']}%")
        console.print(table)


@cli.command()
@help_json_option
def version() -> None:
    """Show version information."""
    info = {"name": "twse-cli", "version": __version__, "python": sys.version.split()[0]}
    if is_agent_mode():
        click.echo(json.dumps(info))
    else:
        console.print(f"twse-cli {__version__} (Python {info['python']})")


@cli.command()
@help_json_option
def serve() -> None:
    """Start MCP (Model Context Protocol) server on stdio.

    Exposes twse-cli as an MCP server for AI agents.
    Tools: twse_fetch, twse_endpoints, twse_schema.

    \b
    Usage:
        twse serve
    """
    try:
        from .serve import run_server
    except ImportError:
        console.print("[red]MCP server requires 'mcp' package.[/red]")
        console.print("Install with: [bold]uv pip install 'twse-cli[mcp]'[/bold]")
        raise SystemExit(EXIT_VALIDATION_ERROR) from None

    run_server()


if __name__ == "__main__":
    cli()
