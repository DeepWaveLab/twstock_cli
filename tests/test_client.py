"""Tests for TWStockClient — retry, error handling, rate limiting."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from twstock_cli.client import TWStockApiError, TWStockClient, TWStockNetworkError


class TestTWStockClientContextManager:
    def test_creates_http_client_on_enter(self):
        client = TWStockClient()
        assert client._http is None
        with client:
            assert client._http is not None
        assert client._http is None

    def test_raises_if_fetch_without_context(self):
        client = TWStockClient()
        with pytest.raises(RuntimeError, match="not initialized"):
            client.fetch("/test")


class TestTWStockClientFetch:
    def test_fetch_returns_list(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Code": "2330"}]

        with TWStockClient(use_cache=False) as client:
            client._http = MagicMock()
            client._http.get.return_value = mock_response
            result = client.fetch("/exchangeReport/STOCK_DAY_ALL")

        assert result == [{"Code": "2330"}]

    def test_fetch_unwraps_dict_with_data_key(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"Code": "2330"}]}

        with TWStockClient(use_cache=False) as client:
            client._http = MagicMock()
            client._http.get.return_value = mock_response
            result = client.fetch("/test")

        assert result == [{"Code": "2330"}]

    def test_fetch_raises_api_error_on_4xx(self):
        mock_response = MagicMock()
        mock_response.status_code = 404

        with TWStockClient(use_cache=False) as client:
            client._http = MagicMock()
            client._http.get.return_value = mock_response
            with pytest.raises(TWStockApiError, match="404"):
                client.fetch("/test")

    def test_fetch_retries_on_5xx(self):
        fail_response = MagicMock()
        fail_response.status_code = 503

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = [{"ok": True}]

        mock_http = MagicMock()
        mock_http.get.side_effect = [fail_response, success_response]

        with TWStockClient(request_interval=0, use_cache=False) as client:
            client._http = mock_http
            with patch("twstock_cli.client.time.sleep"):
                result = client.fetch("/test")

        assert result == [{"ok": True}]
        assert mock_http.get.call_count == 2

    def test_fetch_raises_network_error(self):
        with TWStockClient(request_interval=0, use_cache=False) as client:
            client._http = MagicMock()
            client._http.get.side_effect = httpx.NetworkError("connection refused")
            with patch("twstock_cli.client.time.sleep"):
                with pytest.raises(TWStockNetworkError, match="3 attempts"):
                    client.fetch("/test")


class TestTWStockClientRateLimit:
    def test_rate_limit_sleeps_when_too_fast(self):
        """Verify that the client sleeps when requests are too close together."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("twstock_cli.client.time.sleep") as mock_sleep:
            with TWStockClient(request_interval=0.5, use_cache=False) as client:
                client._http = MagicMock()
                client._http.get.return_value = mock_response
                # Set last request time to "just now" to trigger rate limit
                client._last_request_time = __import__("time").monotonic()
                client.fetch("/test")

            assert mock_sleep.called
