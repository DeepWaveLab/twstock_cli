"""Integration test fixtures — rate limiting, health checks, cache control."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import httpx
import pytest

from .test_runner import _EXCHANGE_HEALTH_KEY

TWSE_HEALTH_URL = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
TPEX_HEALTH_URL = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
TWSE_WEB_HEALTH_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: hits real TWSE/TPEX API")
    config.addinivalue_line("markers", "smoke: minimal smoke test subset")
    config.addinivalue_line("markers", "twse: TWSE OpenAPI endpoints only")
    config.addinivalue_line("markers", "tpex: TPEX OpenAPI endpoints only")
    config.addinivalue_line("markers", "web: TWSE web API endpoints only")


def _check_url(url: str) -> bool:
    """Return True if *url* responds with 2xx within 10 s."""
    try:
        r = httpx.get(url, timeout=10, verify=False)
        r.raise_for_status()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def exchange_health_checks(request: pytest.FixtureRequest) -> None:
    """Probe each exchange and store reachability in config stash."""
    items = request.session.items
    needs_api = any(
        getattr(m, "get_closest_marker", lambda _: None)("integration")
        for m in items
    )
    if not needs_api:
        return

    health: dict[str, bool] = {
        "twse": _check_url(TWSE_HEALTH_URL),
        "tpex": _check_url(TPEX_HEALTH_URL),
        "web": _check_url(TWSE_WEB_HEALTH_URL),
    }
    request.config.stash[_EXCHANGE_HEALTH_KEY] = health

    # If ALL exchanges are down, skip the entire session.
    if not any(health.values()):
        pytest.skip("All exchanges unreachable — skipping integration tests")


@pytest.fixture(scope="session", autouse=True)
def clear_cache_before_run() -> None:
    """Clear the twstock-cli disk cache for a clean baseline."""
    cache_dir = Path.home() / ".cache" / "twstock-cli"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


@pytest.fixture(autouse=True)
def rate_limit_between_tests() -> None:
    """Enforce 0.6 s delay between test cases to respect rate limits."""
    yield
    time.sleep(0.6)
