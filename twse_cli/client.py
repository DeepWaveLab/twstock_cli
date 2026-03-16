"""TWSE OpenAPI client with connection pooling, retry, and rate limiting."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from . import __version__

logger = logging.getLogger(__name__)

BASE_URL = "https://openapi.twse.com.tw/v1"


class TWSEApiError(Exception):
    """TWSE API returned an error response."""


class TWSENetworkError(Exception):
    """Cannot reach TWSE API."""


class TWSEClient:
    """TWSE OpenAPI client with connection pooling, retry, and rate limiting.

    Usage:
        with TWSEClient() as client:
            data = client.fetch("/exchangeReport/STOCK_DAY_ALL")
    """

    def __init__(self, timeout: float = 30.0, request_interval: float = 0.5):
        self._timeout = timeout
        self._request_interval = request_interval
        self._last_request_time = 0.0
        self._http: httpx.Client | None = None

    def __enter__(self) -> TWSEClient:
        transport = httpx.HTTPTransport(retries=2)
        self._http = httpx.Client(
            base_url=BASE_URL,
            transport=transport,
            timeout=httpx.Timeout(connect=10.0, read=self._timeout, write=10.0, pool=5.0),
            headers={
                "User-Agent": f"twse-cli/{__version__}",
                "Accept": "application/json",
            },
            verify=False,  # TWSE API has known SSL certificate issues
        )
        return self

    def __exit__(self, *args: Any) -> None:
        if self._http:
            self._http.close()
            self._http = None

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        if self._request_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self._request_interval:
            time.sleep(self._request_interval - elapsed)

    def fetch(self, path: str) -> list[dict[str, Any]]:
        """Fetch data from any TWSE endpoint.

        Args:
            path: API path (e.g., "/exchangeReport/STOCK_DAY_ALL").

        Returns:
            List of record dicts from the TWSE API.

        Raises:
            TWSEApiError: On 4xx/5xx responses.
            TWSENetworkError: On connection failures.
        """
        if not self._http:
            raise RuntimeError("Client not initialized. Use 'with TWSEClient() as client:'")

        self._rate_limit()
        last_exc: Exception | None = None

        for attempt in range(3):
            try:
                t0 = time.monotonic()
                resp = self._http.get(path)
                elapsed = time.monotonic() - t0
                self._last_request_time = time.monotonic()

                logger.info("GET %s -> %d (%.2fs)", path, resp.status_code, elapsed)

                if resp.status_code in (429, 500, 502, 503, 504):
                    wait = 2**attempt + 0.5
                    logger.warning("HTTP %d, retrying in %.1fs (attempt %d/3)", resp.status_code, wait, attempt + 1)
                    time.sleep(wait)
                    continue

                if resp.status_code >= 400:
                    raise TWSEApiError(f"TWSE API returned {resp.status_code}")

                data = resp.json()
                if isinstance(data, list):
                    return data
                # Some endpoints wrap in an object
                if isinstance(data, dict):
                    # Try common wrapper keys
                    for key in ("data", "Data", "tables"):
                        if key in data and isinstance(data[key], list):
                            return data[key]
                    return [data]
                return []

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                wait = 2**attempt + 0.5
                logger.warning("Network error: %s, retrying in %.1fs (attempt %d/3)", exc, wait, attempt + 1)
                time.sleep(wait)

        if last_exc:
            raise TWSENetworkError(f"Cannot reach TWSE API after 3 attempts: {last_exc}") from last_exc
        raise TWSEApiError("TWSE API request failed after 3 attempts")
