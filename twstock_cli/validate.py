"""Input validation for user-supplied strings.

Rejects control characters, path traversal patterns, and URL
fragment/query injection to harden the CLI against malformed input.
"""

from __future__ import annotations

import re

import click

# Reject: C0 control chars (except HT=0x09, LF=0x0A, CR=0x0D), DEL,
# path traversal, percent-encoded dots, query/fragment injection
_DANGEROUS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]|\.\.[\\/]|%2[eE]|[?#]")

# Maximum allowed length for any user-supplied string
MAX_INPUT_LENGTH = 1000


def validate_input(value: str, name: str) -> str:
    """Validate user-supplied string input.

    Raises click.BadParameter on dangerous patterns or excessive length.
    Returns the stripped value on success.
    """
    if len(value) > MAX_INPUT_LENGTH:
        raise click.BadParameter(
            f"exceeds maximum length of {MAX_INPUT_LENGTH} characters",
            param_hint=name,
        )
    if _DANGEROUS.search(value):
        raise click.BadParameter(
            "contains forbidden characters (control chars, path traversal, or query/fragment injection)",
            param_hint=name,
        )
    return value.strip()
