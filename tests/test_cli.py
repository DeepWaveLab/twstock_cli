"""Tests for CLI commands — CliRunner tests for fetch, endpoints, version."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from twse_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def _mock_fetch(data):
    """Create a mock that patches TWSEClient to return given data."""
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.fetch.return_value = data
    return patch("twse_cli.client.TWSEClient", return_value=mock_client)


class TestFetchCommand:
    def test_fetch_json_output(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True
        assert envelope["data"] == data

    def test_fetch_with_fields(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00", "Volume": "100"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json", "--fields", "Code,Name"])
        envelope = json.loads(result.output)
        assert envelope["data"] == [{"Code": "2330", "Name": "台積電"}]

    def test_fetch_with_code_filter(self, runner):
        data = [
            {"Code": "2330", "Name": "台積電"},
            {"Code": "2317", "Name": "鴻海"},
        ]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json", "--code", "2330"])
        envelope = json.loads(result.output)
        assert len(envelope["data"]) == 1
        assert envelope["data"][0]["Code"] == "2330"

    def test_fetch_with_limit(self, runner):
        data = [{"Code": str(i)} for i in range(100)]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json", "--limit", "5"])
        envelope = json.loads(result.output)
        assert len(envelope["data"]) == 5

    def test_fetch_unknown_endpoint_exit_code(self, runner):
        result = runner.invoke(cli, ["fetch", "NONEXISTENT", "--json"])
        assert result.exit_code == 2
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert envelope["error"]["code"] == "unknown_endpoint"

    def test_fetch_api_error_exit_code(self, runner):
        from twse_cli.client import TWSEApiError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.fetch.side_effect = TWSEApiError("TWSE API returned 503")

        with patch("twse_cli.client.TWSEClient", return_value=mock_client):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json"])
        assert result.exit_code == 1
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert envelope["error"]["code"] == "api_error"

    def test_fetch_network_error_exit_code(self, runner):
        from twse_cli.client import TWSENetworkError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.fetch.side_effect = TWSENetworkError("Cannot reach TWSE")

        with patch("twse_cli.client.TWSEClient", return_value=mock_client):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json"])
        assert result.exit_code == 3
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert envelope["error"]["code"] == "network_error"

    def test_fetch_by_raw_path(self, runner):
        data = [{"Code": "2330"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "/exchangeReport/STOCK_DAY_ALL", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True

    def test_fetch_by_api_code(self, runner):
        data = [{"Code": "2330"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "STOCK_DAY_ALL", "--json"])
        assert result.exit_code == 0


class TestEndpointsCommand:
    def test_endpoints_json_lists_all(self, runner):
        result = runner.invoke(cli, ["endpoints", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 143

    def test_endpoints_search(self, runner):
        result = runner.invoke(cli, ["endpoints", "--search", "股利", "--json"])
        data = json.loads(result.output)
        assert len(data) >= 1
        assert any("股利" in ep["description"] for ep in data)

    def test_endpoints_category_filter(self, runner):
        result = runner.invoke(cli, ["endpoints", "--category", "broker", "--json"])
        data = json.loads(result.output)
        assert all(ep["group"] == "broker" for ep in data)
        assert len(data) == 9

    def test_endpoints_with_fields(self, runner):
        result = runner.invoke(cli, ["endpoints", "--search", "stock.stock-day-all", "--with-fields", "--json"])
        data = json.loads(result.output)
        assert len(data) >= 1
        # The stock.stock-day-all endpoint has fields defined
        ep = data[0]
        assert "fields" in ep
        assert "Code" in ep["fields"]


class TestVersionCommand:
    def test_version_flag(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "twse" in result.output

    def test_version_command(self, runner):
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
