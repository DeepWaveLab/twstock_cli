"""Response sanitization — strip control characters from API data.

Prevents prompt injection via TWSE data (e.g., a company name crafted
to manipulate an LLM). Always on, no opt-out.
"""

from __future__ import annotations

import re
from typing import Any

# Strip C0 control chars (except HT=0x09, LF=0x0A), CR=0x0D normalized away, DEL
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0d\x0e-\x1f\x7f]")


def sanitize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Strip control characters from all string values in a record."""
    return {k: _CONTROL_CHARS.sub("", v) if isinstance(v, str) else v for k, v in record.items()}


def sanitize_data(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitize all records."""
    return [sanitize_record(r) for r in data]
