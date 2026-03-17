"""Disk-based response cache with TTL tiers.

Cache directory: ~/.cache/twstock-cli/ (XDG-compatible)
Key: SHA-256 of API path (first 16 chars)
Format: JSON files with data payload

TTL tiers:
  - Daily endpoints (stock prices, trading data): 4 hours
  - Static endpoints (company info, broker list): 24 hours
  - Default: 4 hours
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default TTL in seconds
TTL_DAILY = 4 * 3600      # 4 hours — stock prices, trading data
TTL_STATIC = 24 * 3600    # 24 hours — company info, broker data

# Paths that change infrequently get longer TTL
_STATIC_PREFIXES = (
    "/company/",
    "/brokerService/",
    "/opendata/t187ap03",    # Company basic info
    "/opendata/t187ap18",    # Broker basic info
    "/holidaySchedule/",
)


def _cache_dir() -> Path:
    """Get cache directory, respecting XDG_CACHE_HOME."""
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        base = Path(xdg)
    else:
        base = Path.home() / ".cache"
    return base / "twstock-cli"


def _cache_path(api_path: str) -> Path:
    """Generate cache file path from API path."""
    key = hashlib.sha256(api_path.encode()).hexdigest()[:16]
    return _cache_dir() / f"{key}.json"


def _ttl_for_path(api_path: str) -> float:
    """Determine TTL based on endpoint path."""
    for prefix in _STATIC_PREFIXES:
        if api_path.startswith(prefix):
            return TTL_STATIC
    return TTL_DAILY


def get_cached(api_path: str) -> list[dict[str, Any]] | None:
    """Read cached response if fresh, else return None."""
    cache_file = _cache_path(api_path)
    if not cache_file.exists():
        return None

    age = time.time() - cache_file.stat().st_mtime
    ttl = _ttl_for_path(api_path)

    if age > ttl:
        logger.info("Cache expired for %s (%.0fs old, TTL=%.0fs)", api_path, age, ttl)
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        logger.info("Cache hit for %s (%.0fs old)", api_path, age)
        return data
    except (json.JSONDecodeError, OSError):
        return None


def set_cached(api_path: str, data: list[dict[str, Any]]) -> None:
    """Write response to cache."""
    cache_dir = _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_path(api_path)
    try:
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        logger.info("Cached %d records for %s", len(data), api_path)
    except OSError as exc:
        logger.warning("Failed to write cache for %s: %s", api_path, exc)


def clear_cache() -> int:
    """Remove all cached files. Returns number of files removed."""
    cache_dir = _cache_dir()
    if not cache_dir.exists():
        return 0
    count = 0
    for f in cache_dir.glob("*.json"):
        f.unlink()
        count += 1
    return count
