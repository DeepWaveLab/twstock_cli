"""Data normalization: string→number, ROC→ISO dates.

TWSE API returns all values as strings, dates in ROC calendar format.
This module provides opt-in normalization for agent convenience.

ROC date format: "1150313" → "2026-03-13" (ROC year 115 + 1911 = 2026)
Numeric strings: "595.00" → 595.0, "36317450" → 36317450
"""

from __future__ import annotations

import re
from typing import Any

# ROC date patterns (common lengths: 7 digits YYYMMDD, or formatted YYY/MM/DD)
_ROC_DATE_RE = re.compile(r"^(\d{2,3})(\d{2})(\d{2})$")
_ROC_DATE_SLASH_RE = re.compile(r"^(\d{2,3})/(\d{2})/(\d{2})$")

# Fields that are known dates (avoid false positives on stock codes like "2330")
_DATE_FIELD_HINTS = frozenset({
    "日期", "出表日期", "成立日期", "上市日期", "資料日期", "年月日",
    "Date", "TradeDate", "date", "EstablishmentDate",
    "股利年度", "資料年月",
})

# Fields that should never be converted (stock codes, IDs)
_SKIP_FIELDS = frozenset({
    "Code", "公司代號", "證券代號", "代號", "券商代號",
    "Name", "公司名稱", "公司簡稱", "證券名稱",
})


def _try_roc_to_iso(value: str) -> str | None:
    """Convert ROC date string to ISO 8601 date, or return None."""
    m = _ROC_DATE_RE.match(value)
    if m:
        roc_year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31 and roc_year >= 70:
            return f"{roc_year + 1911:04d}-{month:02d}-{day:02d}"
    m = _ROC_DATE_SLASH_RE.match(value)
    if m:
        roc_year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31 and roc_year >= 70:
            return f"{roc_year + 1911:04d}-{month:02d}-{day:02d}"
    return None


def _try_numeric(value: str) -> int | float | None:
    """Convert numeric string to int or float, or return None."""
    # Strip commas from formatted numbers like "1,234,567"
    cleaned = value.replace(",", "")
    if not cleaned or cleaned in ("", "-", "--", "N/A", "X"):
        return None
    try:
        if "." in cleaned:
            return float(cleaned)
        return int(cleaned)
    except ValueError:
        return None


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single record: string→number, ROC→ISO dates."""
    result = {}
    for key, value in record.items():
        if not isinstance(value, str) or not value.strip():
            result[key] = value
            continue

        value = value.strip()

        # Skip fields that should remain strings
        if key in _SKIP_FIELDS:
            result[key] = value
            continue

        # Try ROC date conversion for date-hinted fields
        if key in _DATE_FIELD_HINTS:
            iso = _try_roc_to_iso(value)
            if iso:
                result[key] = iso
                continue

        # Try numeric conversion
        num = _try_numeric(value)
        if num is not None:
            result[key] = num
            continue

        # Keep as string
        result[key] = value
    return result


def normalize_data(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize all records in a dataset."""
    return [normalize_record(row) for row in data]
