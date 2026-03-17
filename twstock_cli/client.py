"""TWSE/TPEX API client with connection pooling, retry, and rate limiting."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from . import __version__

logger = logging.getLogger(__name__)

BASE_URL = "https://openapi.twse.com.tw/v1"


class TWStockApiError(Exception):
    """TWSE API returned an error response."""


class TWStockNetworkError(Exception):
    """Cannot reach TWSE API."""


class TWStockClient:
    """TWSE/TPEX API client with connection pooling, retry, and rate limiting.

    Usage:
        with TWStockClient() as client:
            data = client.fetch("/exchangeReport/STOCK_DAY_ALL")
    """

    def __init__(self, timeout: float = 30.0, request_interval: float = 0.5, use_cache: bool = True):
        self._timeout = timeout
        self._request_interval = request_interval
        self._use_cache = use_cache
        self._last_request_time = 0.0
        self._http: httpx.Client | None = None

    def __enter__(self) -> TWStockClient:
        transport = httpx.HTTPTransport(retries=2)
        self._http = httpx.Client(
            base_url=BASE_URL,
            transport=transport,
            timeout=httpx.Timeout(connect=10.0, read=self._timeout, write=10.0, pool=5.0),
            headers={
                "User-Agent": f"twstock-cli/{__version__}",
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

    def fetch(self, path: str, *, base_url: str | None = None) -> list[dict[str, Any]]:
        """Fetch data from a TWSE/TPEX OpenAPI endpoint.

        Args:
            path: API path (e.g., "/exchangeReport/STOCK_DAY_ALL").
            base_url: Override base URL (e.g., TPEX "https://www.tpex.org.tw/openapi/v1").

        Returns:
            List of record dicts from the API.

        Raises:
            TWStockApiError: On 4xx/5xx responses.
            TWStockNetworkError: On connection failures.
        """
        if not self._http:
            raise RuntimeError("Client not initialized. Use 'with TWStockClient() as client:'")

        # For non-default base URLs, build full URL; otherwise use relative path
        url = f"{base_url}{path}" if base_url else path
        cache_key = url if base_url else path

        # Check cache first
        if self._use_cache:
            from .cache import get_cached

            cached = get_cached(cache_key)
            if cached is not None:
                return cached

        self._rate_limit()
        last_exc: Exception | None = None

        for attempt in range(3):
            try:
                t0 = time.monotonic()
                resp = self._http.get(url)
                elapsed = time.monotonic() - t0
                self._last_request_time = time.monotonic()

                logger.info("GET %s -> %d (%.2fs)", url, resp.status_code, elapsed)

                if resp.status_code in (429, 500, 502, 503, 504):
                    wait = 2**attempt + 0.5
                    logger.warning("HTTP %d, retrying in %.1fs (attempt %d/3)", resp.status_code, wait, attempt + 1)
                    time.sleep(wait)
                    continue

                if resp.status_code >= 400:
                    raise TWStockApiError(f"API returned {resp.status_code}")

                data = resp.json()
                result: list[dict[str, Any]]
                if isinstance(data, list):
                    result = data
                elif isinstance(data, dict):
                    # Try common wrapper keys
                    result = []
                    for key in ("data", "Data", "tables"):
                        if key in data and isinstance(data[key], list):
                            result = data[key]
                            break
                    else:
                        result = [data]
                else:
                    result = []

                # Write to cache
                if self._use_cache:
                    from .cache import set_cached

                    set_cached(cache_key, result)

                return result

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                wait = 2**attempt + 0.5
                logger.warning("Network error: %s, retrying in %.1fs (attempt %d/3)", exc, wait, attempt + 1)
                time.sleep(wait)

        if last_exc:
            raise TWStockNetworkError(f"Cannot reach TWSE API after 3 attempts: {last_exc}") from last_exc
        raise TWStockApiError("TWSE API request failed after 3 attempts")

    def fetch_web(self, base_url: str, path: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
        """Fetch data from a TWSE web API endpoint (fields+data format).

        Unlike the OpenAPI, the web API returns {"stat":"OK","fields":[...],"data":[[...],...]}.
        This method zips fields+data into list[dict].

        Args:
            base_url: Base URL (e.g. "https://www.twse.com.tw/rwd/zh").
            path: API path (e.g. "/fund/T86").
            params: Query parameters (date, selectType, etc.).

        Returns:
            List of record dicts.
        """
        if not self._http:
            raise RuntimeError("Client not initialized. Use 'with TWStockClient() as client:'")

        # Build cache key from base_url + path + sorted params
        cache_key = f"{base_url}{path}"
        if params:
            sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            cache_key = f"{cache_key}?{sorted_params}"

        if self._use_cache:
            from .cache import get_cached

            cached = get_cached(cache_key)
            if cached is not None:
                return cached

        self._rate_limit()
        url = f"{base_url}{path}"
        last_exc: Exception | None = None

        for attempt in range(3):
            try:
                t0 = time.monotonic()
                resp = self._http.get(url, params=params)
                elapsed = time.monotonic() - t0
                self._last_request_time = time.monotonic()

                logger.info("GET %s -> %d (%.2fs)", url, resp.status_code, elapsed)

                if resp.status_code in (429, 500, 502, 503, 504):
                    wait = 2**attempt + 0.5
                    logger.warning("HTTP %d, retrying in %.1fs (attempt %d/3)", resp.status_code, wait, attempt + 1)
                    time.sleep(wait)
                    continue

                if resp.status_code >= 400:
                    raise TWStockApiError(f"TWSE web API returned {resp.status_code}")

                body = resp.json()

                if body.get("stat") != "OK":
                    msg = body.get("stat", "unknown error")
                    raise TWStockApiError(f"TWSE web API error: {msg}")

                fields = body.get("fields", [])
                raw_data = body.get("data", [])
                result = [dict(zip(fields, row)) for row in raw_data]

                if self._use_cache:
                    from .cache import set_cached

                    set_cached(cache_key, result)

                return result

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                wait = 2**attempt + 0.5
                logger.warning("Network error: %s, retrying in %.1fs (attempt %d/3)", exc, wait, attempt + 1)
                time.sleep(wait)

        if last_exc:
            raise TWStockNetworkError(f"Cannot reach TWSE web API after 3 attempts: {last_exc}") from last_exc
        raise TWStockApiError("TWSE web API request failed after 3 attempts")
