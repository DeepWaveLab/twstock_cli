"""Factory for generating Click commands from the endpoint registry.

Each endpoint becomes a thin CLI command that delegates to the shared
fetch-filter-output pipeline. Groups (stock, company, broker) are built
by filtering the registry.
"""

from __future__ import annotations

import json

import click

from ..endpoints import ENDPOINTS, EndpointDef
from ..help_json import help_json_option

# Group metadata: name → (description, help text)
GROUPS: dict[str, str] = {
    "stock": "Stock trading, indices, warrants, and market data (證券交易)",
    "company": "Company governance, financials, and disclosures (公司治理)",
    "broker": "Broker information and statistics (券商資料)",
    "otc": "OTC stock trading, indices, and market data (上櫃證券交易)",
    "otc_company": "OTC company governance, financials, and disclosures (上櫃公司治理)",
    "web": "TWSE historical web API — date-parameterized endpoints (歷史資料)",
}


def _apply_field_aliases(data: list[dict], aliases: dict[str, str]) -> list[dict]:
    """Rename keys in each record using the alias mapping."""
    return [{aliases.get(k, k): v for k, v in row.items()} for row in data]


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
    date: str | None = None,
    stock_no: str | None = None,
) -> None:
    """Shared fetch-filter-output pipeline used by both `twstock fetch` and domain shortcuts."""
    from ..cli import EXIT_API_ERROR, EXIT_NETWORK_ERROR, EXIT_VALIDATION_ERROR
    from ..client import TWStockApiError, TWStockClient, TWStockNetworkError
    from ..output import console, emit_error, emit_json, emit_ndjson, emit_raw, filter_by_code, filter_fields, is_agent_mode, render_table
    from ..validate import validate_input

    # Web API endpoints use date_param (fields+data format, e.g. T86, STOCK_DAY).
    # TPEX OpenAPI endpoints have base_url but no date_param (list-of-dicts format).
    is_web = ep.date_param is not None

    # Validate user-supplied inputs (for domain shortcuts that bypass cli.py validation)
    try:
        if field_list:
            field_list = validate_input(field_list, "--fields")
        if stock_code:
            stock_code = validate_input(stock_code, "--code")
        if stock_no:
            stock_no = validate_input(stock_no, "--stock-no")
    except click.BadParameter as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("validation_error", str(exc), EXIT_VALIDATION_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_VALIDATION_ERROR) from None

    # Dry-run: emit preview JSON without making an HTTP call
    if dry_run:
        from ..client import BASE_URL

        if is_web:
            url = f"{ep.base_url}{ep.path}"
            params = dict(ep.default_params)
            if date and ep.date_param:
                params[ep.date_param] = date
            if stock_no and ep.stock_param:
                params[ep.stock_param] = stock_no
            preview = {
                "dry_run": True,
                "method": "GET",
                "url": url,
                "params": params,
                "endpoint": f"{ep.group}.{ep.cli_name}",
            }
        else:
            effective_base = ep.base_url or BASE_URL
            preview = {
                "dry_run": True,
                "method": "GET",
                "url": f"{effective_base}{ep.path}",
                "endpoint": f"{ep.group}.{ep.cli_name}",
            }

        filters = {
            "fields": [f.strip() for f in field_list.split(",")] if field_list else None,
            "code": stock_code,
            "limit": max_records,
            "normalize": normalize,
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        if filters:
            preview["filters"] = filters
        click.echo(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    try:
        with TWStockClient(use_cache=not no_cache) as client:
            if is_web:
                params = dict(ep.default_params)
                if date and ep.date_param:
                    params[ep.date_param] = date
                if stock_no and ep.stock_param:
                    params[ep.stock_param] = stock_no
                data = client.fetch_web(ep.base_url, ep.path, params)
            else:
                data = client.fetch(ep.path, base_url=ep.base_url)
    except TWStockApiError as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("api_error", str(exc), EXIT_API_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_API_ERROR) from None
    except TWStockNetworkError as exc:
        if as_json or ndjson or raw or is_agent_mode():
            emit_error("network_error", str(exc), EXIT_NETWORK_ERROR)
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(EXIT_NETWORK_ERROR) from None

    # Sanitize response strings (strip control chars)
    from ..sanitize import sanitize_data

    data = sanitize_data(data)

    # Apply field aliases (web API endpoints have verbose Chinese field names)
    if ep.field_aliases:
        data = _apply_field_aliases(data, ep.field_aliases)

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
    if ep.date_param is not None:
        return _make_web_endpoint_command(ep)

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
    @help_json_option
    def cmd(
        as_json: bool,
        field_list: str | None,
        stock_code: str | None,
        max_records: int | None,
        no_cache: bool,
        normalize: bool,
        ndjson: bool,
        raw: bool,
        dry_run: bool,
    ) -> None:
        _run_fetch(
            ep,
            as_json,
            field_list,
            stock_code,
            max_records,
            no_cache=no_cache,
            normalize=normalize,
            ndjson=ndjson,
            raw=raw,
            dry_run=dry_run,
        )

    return cmd


def _make_web_endpoint_command(ep: EndpointDef) -> click.Command:
    """Create a Click command for a web API endpoint (with --date and optional --stock-no)."""

    has_stock = ep.stock_param is not None

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
    @click.option("--date", default=None, help="Date in YYYYMMDD format (default: today)")
    @click.option("--stock-no", default=None, help="Stock number (e.g. 2330)", hidden=not has_stock)
    @help_json_option
    def cmd(
        as_json: bool,
        field_list: str | None,
        stock_code: str | None,
        max_records: int | None,
        no_cache: bool,
        normalize: bool,
        ndjson: bool,
        raw: bool,
        dry_run: bool,
        date: str | None,
        stock_no: str | None,
    ) -> None:
        _run_fetch(
            ep,
            as_json,
            field_list,
            stock_code,
            max_records,
            no_cache=no_cache,
            normalize=normalize,
            ndjson=ndjson,
            raw=raw,
            dry_run=dry_run,
            date=date,
            stock_no=stock_no,
        )

    return cmd


def make_group(group_name: str) -> click.Group:
    """Create a Click group with all commands for the given group name."""
    description = GROUPS.get(group_name, group_name)

    @click.group(name=group_name, help=description)
    @help_json_option
    def grp() -> None:
        pass

    for key, ep in sorted(ENDPOINTS.items()):
        if ep.group == group_name:
            grp.add_command(make_endpoint_command(ep))

    return grp
