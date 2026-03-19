"""Runtime schema introspection for TWSE endpoints.

Analyzes endpoint data to determine field names, types, examples,
and completeness. Used by `twstock schema <endpoint>`.
"""

from __future__ import annotations

import re
from typing import Any

_ROC_DATE_RE = re.compile(r"^\d{2,3}[/]?\d{2}[/]?\d{2}$")
_NUMERIC_RE = re.compile(r"^-?[\d,]+\.?\d*$")


def _infer_type(values: list[str]) -> str:
    """Infer the logical type from a sample of string values."""
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return "empty"

    sample = non_empty[:50]  # Check up to 50 values
    date_count = sum(1 for v in sample if _ROC_DATE_RE.match(v.replace("/", "")))
    numeric_count = sum(1 for v in sample if _NUMERIC_RE.match(v.replace(",", "")))

    if date_count > len(sample) * 0.8:
        return "roc_date"
    if numeric_count > len(sample) * 0.8:
        # Distinguish integer vs decimal
        has_decimal = any("." in v for v in sample if _NUMERIC_RE.match(v.replace(",", "")))
        return "decimal" if has_decimal else "integer"
    return "string"


def analyze_schema(
    data: list[dict[str, Any]],
    *,
    endpoint_name: str = "",
    description: str = "",
    path: str = "",
) -> dict[str, Any]:
    """Analyze a dataset and return schema information.

    Returns:
        Dict with endpoint info and per-field analysis:
        {
            "endpoint": "stock.stock-day-all",
            "description": "...",
            "path": "/exchangeReport/...",
            "record_count": 1000,
            "fields": [
                {"name": "Code", "type": "string", "example": "2330", "non_empty_pct": 100}
            ]
        }
    """
    if not data:
        return {
            "endpoint": endpoint_name,
            "description": description,
            "path": path,
            "record_count": 0,
            "fields": [],
        }

    columns = list(data[0].keys())
    total = len(data)
    field_info = []

    for col in columns:
        values = [str(row.get(col, "")) for row in data]
        non_empty = [v for v in values if v.strip()]
        non_empty_pct = round(len(non_empty) / total * 100) if total > 0 else 0
        example = non_empty[0] if non_empty else ""
        inferred_type = _infer_type(values)

        field_info.append(
            {
                "name": col,
                "type": inferred_type,
                "example": example,
                "non_empty_pct": non_empty_pct,
            }
        )

    return {
        "endpoint": endpoint_name,
        "description": description,
        "path": path,
        "record_count": total,
        "fields": field_info,
    }
