"""Structured JSON metadata for Click commands.

Enables agents to discover flags, types, and defaults without parsing
help text. Used by the --help-json eager option.
"""

from __future__ import annotations

import json
from typing import Any

import click


def command_to_json(cmd: click.BaseCommand) -> dict[str, Any]:
    """Convert a Click command/group to JSON metadata."""
    result: dict[str, Any] = {
        "name": cmd.name,
        "description": (cmd.help or "").strip().split("\n")[0],
    }

    if isinstance(cmd, click.Group):
        result["commands"] = sorted(cmd.list_commands(click.Context(cmd)))
        return result

    params = []
    for param in cmd.params:
        if param.name in ("help", "help_json"):
            continue
        info: dict[str, Any] = {"name": param.human_readable_name}
        if isinstance(param, click.Option):
            info["flag"] = param.opts[0]  # e.g., "--limit"
            info["type"] = _click_type_name(param.type)
            if isinstance(param.type, click.Choice):
                info["choices"] = list(param.type.choices)
            info["default"] = param.default
            info["required"] = param.required
        elif isinstance(param, click.Argument):
            info["type"] = "argument"
            info["required"] = param.required
        # Only Options have a .help attribute
        if isinstance(param, click.Option):
            info["help"] = param.help or ""
        params.append(info)

    result["params"] = params
    return result


_TYPE_MAP = {
    "string": "string",
    "integer": "int",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "boolean": "bool",
    "text": "string",
}


def _click_type_name(t: click.ParamType) -> str:
    """Map Click type to JSON-friendly name."""
    if isinstance(t, click.Choice):
        return "choice"
    return _TYPE_MAP.get(t.name.lower(), t.name.lower())


def help_json_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Eager callback for --help-json option."""
    if not value or ctx.resilient_parsing:
        return

    cmd = ctx.command
    # For lazy groups, trigger loading of all subcommands
    if isinstance(cmd, click.Group):
        cmd.list_commands(ctx)

    click.echo(json.dumps(command_to_json(cmd), ensure_ascii=False, indent=2))
    ctx.exit()


# Shared option to attach to commands
help_json_option = click.option(
    "--help-json",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=help_json_callback,
    help="Output command metadata as JSON",
)
