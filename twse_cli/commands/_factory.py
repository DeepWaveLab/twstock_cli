"""Factory for generating Click commands from the endpoint registry.

Each endpoint becomes a thin CLI command that delegates to the shared
fetch-filter-output pipeline. Groups (stock, company, broker) are built
by filtering the registry.
"""

from __future__ import annotations

import json

import click

from ..endpoints import ENDPOINTS, EndpointDef

# Group metadata: name → (description, help text)
GROUPS: dict[str, str] = {
    "stock": "Stock trading, indices, warrants, and market data (證券交易)",
    "company": "Company governance, financials, and disclosures (公司治理)",
    "broker": "Broker information and statistics (券商資料)",
}


def _run_fetch(
    ep: EndpointDef,
    as_json: bool,
    field_list: str | None,
    stock_code: str | None,
    max_records: int | None,
    *,
    no_cache: bool = False,
    normalize: bool = False,
    ndjson: bool = False,
    raw: bool = False,
    dry_run: bool = False,
) -> None:
    """Shared fetch-filter-output pipeline used by both `twse fetch` and domain shortcuts."""
    from ..cli import EXIT_API_ERROR, EXIT_NETWORK_ERROR, EXIT_VALIDATION_ERROR
    from ..client import TWSEApiError, TWSEClient, TWSENetworkError
    from ..output import console, emit_error, emit_json, emit_ndjson, emit_raw, filter_by_code, filter_fields, is_agent_mode, render_table
    from ..validate import validate_input

    # Validate user-supplied inputs (for domain shortcuts that bypass cli.py validation)
    try:
        if field_list:
            field_list = validate_input(field_list, "--fields")
        if stock_code:
            stock_code = validate_input(stock_code, "--code")
    except click.BadParameter as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("validation_error", str(exc), EXIT_VALIDATION_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_VALIDATION_ERROR) from None

    # Dry-run: emit preview JSON without making an HTTP call
    if dry_run:
        from ..client import BASE_URL

        preview = {
            "dry_run": True,
            "method": "GET",
            "url": f"{BASE_URL}{ep.path}",
            "endpoint": f"{ep.group}.{ep.cli_name}",
            "filters": {
                "fields": [f.strip() for f in field_list.split(",")] if field_list else None,
                "code": stock_code,
                "limit": max_records,
                "normalize": normalize,
            },
        }
        # Remove None values from filters
        preview["filters"] = {k: v for k, v in preview["filters"].items() if v is not None}
        if not preview["filters"]:
            del preview["filters"]
        click.echo(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    try:
        with TWSEClient(use_cache=not no_cache) as client:
            data = client.fetch(ep.path)
    except TWSEApiError as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("api_error", str(exc), EXIT_API_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_API_ERROR) from None
    except TWSENetworkError as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("network_error", str(exc), EXIT_NETWORK_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_NETWORK_ERROR) from None

    if stock_code:
        data = filter_by_code(data, stock_code, ep.code_field)
    if normalize:
        from ..normalize import normalize_data

        data = normalize_data(data)
    if field_list:
        data = filter_fields(data, field_list)
    if max_records:
        data = data[:max_records]

    if ndjson:
        emit_ndjson(data)
    elif raw:
        emit_raw(data)
    elif as_json or is_agent_mode():
        emit_json(data)
    else:
        dotted = f"{ep.group}.{ep.cli_name}"
        render_table(data, title=f"{ep.description} ({dotted})")


def make_endpoint_command(ep: EndpointDef) -> click.Command:
    """Create a Click command from an EndpointDef."""

    @click.command(name=ep.cli_name, help=ep.description)
    @click.option("--json", "as_json", is_flag=True, help="Output JSON envelope to stdout")
    @click.option("--fields", "field_list", default=None, help="Comma-separated fields to include")
    @click.option("--code", "stock_code", default=None, help="Filter by stock code")
    @click.option("--limit", "max_records", type=int, default=None, help="Limit number of records")
    @click.option("--no-cache", is_flag=True, help="Bypass disk cache")
    @click.option("--normalize", is_flag=True, help="Normalize data: string→number, ROC→ISO dates")
    @click.option("--ndjson", is_flag=True, help="Output as newline-delimited JSON")
    @click.option("--raw", is_flag=True, help="Output bare JSON array (no envelope)")
    @click.option("--dry-run", is_flag=True, help="Preview request as JSON without making an HTTP call")
    def cmd(as_json: bool, field_list: str | None, stock_code: str | None, max_records: int | None, no_cache: bool, normalize: bool, ndjson: bool, raw: bool, dry_run: bool) -> None:
        _run_fetch(ep, as_json, field_list, stock_code, max_records, no_cache=no_cache, normalize=normalize, ndjson=ndjson, raw=raw, dry_run=dry_run)

    return cmd


def make_group(group_name: str) -> click.Group:
    """Create a Click group with all commands for the given group name."""
    description = GROUPS.get(group_name, group_name)

    @click.group(name=group_name, help=description)
    def grp() -> None:
        pass

    for key, ep in sorted(ENDPOINTS.items()):
        if ep.group == group_name:
            grp.add_command(make_endpoint_command(ep))

    return grp
