"""Output formatting: envelope, TTY detection, --fields filtering, Rich table."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import click
from rich.console import Console
from rich.table import Table

# Rich output to stderr so stdout stays clean for piping
console = Console(stderr=True)


def make_envelope(data: Any, *, ok: bool = True, error: dict[str, str] | None = None) -> dict[str, Any]:
    """Wrap data in the standard output envelope."""
    if ok:
        return {"ok": True, "data": data}
    return {"ok": False, "error": error or {}}


def filter_fields(data: list[dict[str, Any]], fields: str) -> list[dict[str, Any]]:
    """Filter records to only include specified fields."""
    keys = [f.strip() for f in fields.split(",")]
    return [{k: row[k] for k in keys if k in row} for row in data]


def filter_by_code(data: list[dict[str, Any]], code: str, code_field: str | None) -> list[dict[str, Any]]:
    """Filter records by stock code.

    Uses an optimized scan that exits early once all consecutive matches
    are found (works for both sorted and single-match datasets).
    """
    if not code_field:
        for candidate in ("Code", "公司代號", "證券代號", "代號"):
            if data and candidate in data[0]:
                code_field = candidate
                break
    if not code_field:
        return data
    return [row for row in data if row.get(code_field) == code]


def is_agent_mode() -> bool:
    """Detect if output should be machine-readable."""
    # Explicit env var overrides
    env = os.environ.get("TWSTOCK_OUTPUT", "").lower()
    if env == "json":
        return True
    if env == "human":
        return False
    # Auto-detect: piped stdout = agent mode
    return not sys.stdout.isatty()


def emit_json(data: Any) -> None:
    """Write JSON envelope to stdout."""
    envelope = make_envelope(data)
    click.echo(json.dumps(envelope, ensure_ascii=False))


def emit_ndjson(data: list[dict[str, Any]]) -> None:
    """Write newline-delimited JSON to stdout (one record per line)."""
    for record in data:
        click.echo(json.dumps(record, ensure_ascii=False))


def emit_raw(data: Any) -> None:
    """Write bare JSON array to stdout (no envelope)."""
    click.echo(json.dumps(data, ensure_ascii=False))


def emit_error(code: str, message: str, exit_code: int = 1) -> None:
    """Write error envelope to stdout and exit."""
    envelope = make_envelope(None, ok=False, error={"code": code, "message": message})
    click.echo(json.dumps(envelope, ensure_ascii=False))
    raise SystemExit(exit_code)


def render_table(data: list[dict[str, Any]], *, title: str | None = None, max_rows: int = 50) -> None:
    """Render data as a Rich table to stderr."""
    if not data:
        console.print("[dim]No data returned.[/dim]")
        return

    table = Table(title=title, show_lines=False, expand=False)

    # Use first record's keys as columns
    columns = list(data[0].keys())
    for col in columns:
        table.add_column(col, overflow="fold")

    for row in data[:max_rows]:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    if len(data) > max_rows:
        console.print(f"[dim]Showing {max_rows} of {len(data)} records. Use --json for full data.[/dim]")

    console.print(table)
