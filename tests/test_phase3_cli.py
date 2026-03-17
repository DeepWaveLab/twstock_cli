"""Tests for Phase 3 CLI features: --normalize, --ndjson, --raw, schema command."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from twstock_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def _mock_fetch(data):
    """Create a mock that patches TWStockClient to return given data."""
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.fetch.return_value = data
    return patch("twstock_cli.client.TWStockClient", return_value=mock_client)


class TestNormalizeFlag:
    def test_normalize_converts_numbers(self, runner):
        data = [{"Code": "2330", "ClosingPrice": "595.00", "TradeVolume": "36317450"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json", "--normalize"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        record = envelope["data"][0]
        assert record["Code"] == "2330"  # Preserved as string
        assert record["ClosingPrice"] == 595.0
        assert record["TradeVolume"] == 36317450

    def test_normalize_on_domain_shortcut(self, runner):
        data = [{"Code": "2330", "ClosingPrice": "595.00"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["stock", "stock-day-all", "--json", "--normalize"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["data"][0]["ClosingPrice"] == 595.0


class TestNdjsonFlag:
    def test_ndjson_output(self, runner):
        data = [
            {"Code": "2330", "Name": "台積電"},
            {"Code": "2317", "Name": "鴻海"},
        ]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--ndjson"])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["Code"] == "2330"
        assert json.loads(lines[1])["Code"] == "2317"

    def test_ndjson_with_fields(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "Volume": "100"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--ndjson", "--fields", "Code,Name"])
        lines = result.output.strip().split("\n")
        record = json.loads(lines[0])
        assert "Volume" not in record
        assert record["Code"] == "2330"

    def test_ndjson_on_domain_shortcut(self, runner):
        data = [{"Code": "2330"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["stock", "stock-day-all", "--ndjson"])
        assert result.exit_code == 0
        assert json.loads(result.output.strip())["Code"] == "2330"


class TestRawFlag:
    def test_raw_output_no_envelope(self, runner):
        data = [{"Code": "2330"}, {"Code": "2317"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--raw"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        # Raw output is a bare list, no "ok" or "data" wrapper
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["Code"] == "2330"

    def test_raw_with_fields(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "Volume": "100"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--raw", "--fields", "Code"])
        parsed = json.loads(result.output)
        assert parsed == [{"Code": "2330"}]

    def test_raw_on_domain_shortcut(self, runner):
        data = [{"Code": "2330"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["stock", "stock-day-all", "--raw"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert isinstance(parsed, list)


class TestSchemaCommand:
    def test_schema_json_output(self, runner):
        data = [
            {"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"},
            {"Code": "2317", "Name": "鴻海", "ClosingPrice": "100.50"},
        ]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["schema", "stock.stock-day-all", "--json"])
        assert result.exit_code == 0
        schema = json.loads(result.output)
        assert schema["endpoint"] == "stock.stock-day-all"
        assert schema["record_count"] == 2
        assert len(schema["fields"]) == 3

    def test_schema_unknown_endpoint(self, runner):
        result = runner.invoke(cli, ["schema", "NONEXISTENT", "--json"])
        assert result.exit_code == 2

    def test_schema_field_types(self, runner):
        data = [
            {"Code": "2330", "ClosingPrice": "595.00", "Volume": "36317450"},
        ]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["schema", "stock.stock-day-all", "--json"])
        schema = json.loads(result.output)
        fields_by_name = {f["name"]: f for f in schema["fields"]}
        assert fields_by_name["ClosingPrice"]["type"] == "decimal"
        assert fields_by_name["Volume"]["type"] == "integer"


class TestServeCommand:
    def test_serve_help_exists(self, runner):
        result = runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0
        assert "MCP" in result.output

    def test_serve_in_help_list(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "serve" in result.output
