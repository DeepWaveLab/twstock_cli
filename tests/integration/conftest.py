"""Integration test fixtures — rate limiting, health check, cache control."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import httpx
import pytest

TWSE_HEALTH_URL = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: hits real TWSE API")
    config.addinivalue_line("markers", "smoke: minimal smoke test subset")


@pytest.fixture(scope="session", autouse=True)
def twse_health_check(request: pytest.FixtureRequest) -> None:
    """Skip live-API tests if TWSE is unreachable."""
    # Collect whether any test in this session actually needs the API.
    # If all tests are deterministic (requires_api=false), skip the check.
    items = request.session.items
    needs_api = any(
        getattr(m, "get_closest_marker", lambda _: None)("integration")
        for m in items
    )
    if not needs_api:
        return

    try:
        r = httpx.get(TWSE_HEALTH_URL, timeout=10, verify=False)
        r.raise_for_status()
    except Exception:
        pytest.skip("TWSE API unreachable — skipping integration tests")


@pytest.fixture(scope="session", autouse=True)
def clear_cache_before_run() -> None:
    """Clear the TWSE CLI disk cache for a clean baseline."""
    cache_dir = Path.home() / ".cache" / "twstock-cli"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


@pytest.fixture(autouse=True)
def rate_limit_between_tests() -> None:
    """Enforce 0.6 s delay between test cases to respect TWSE rate limits."""
    yield
    time.sleep(0.6)
