"""Tests for CLI commands — CliRunner tests for fetch, endpoints, version."""

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


def _mock_fetch_web(data):
    """Create a mock that patches TWStockClient.fetch_web to return given data."""
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.fetch_web.return_value = data
    return patch("twstock_cli.client.TWStockClient", return_value=mock_client)


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
        from twstock_cli.client import TWStockApiError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.fetch.side_effect = TWStockApiError("TWSE API returned 503")

        with patch("twstock_cli.client.TWStockClient", return_value=mock_client):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--json"])
        assert result.exit_code == 1
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert envelope["error"]["code"] == "api_error"

    def test_fetch_network_error_exit_code(self, runner):
        from twstock_cli.client import TWStockNetworkError

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.fetch.side_effect = TWStockNetworkError("Cannot reach TWSE")

        with patch("twstock_cli.client.TWStockClient", return_value=mock_client):
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
        assert len(data) == 359

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


class TestDomainShortcuts:
    """Test domain shortcut commands (twstock stock <cmd>, twstock company <cmd>, etc.)."""

    def test_stock_subgroup_exists(self, runner):
        result = runner.invoke(cli, ["stock", "--help"])
        assert result.exit_code == 0
        assert "stock-day-all" in result.output

    def test_company_subgroup_exists(self, runner):
        result = runner.invoke(cli, ["company", "--help"])
        assert result.exit_code == 0
        assert "t187ap03-l" in result.output

    def test_broker_subgroup_exists(self, runner):
        result = runner.invoke(cli, ["broker", "--help"])
        assert result.exit_code == 0
        assert "brokerlist" in result.output

    def test_stock_command_json_output(self, runner):
        data = [{"Code": "2330", "Name": "台積電"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["stock", "stock-day-all", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True
        assert envelope["data"] == data

    def test_stock_command_with_fields(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["stock", "stock-day-all", "--json", "--fields", "Code,Name"])
        envelope = json.loads(result.output)
        assert envelope["data"] == [{"Code": "2330", "Name": "台積電"}]

    def test_stock_command_with_code_filter(self, runner):
        data = [
            {"Code": "2330", "Name": "台積電"},
            {"Code": "2317", "Name": "鴻海"},
        ]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["stock", "stock-day-all", "--json", "--code", "2330"])
        envelope = json.loads(result.output)
        assert len(envelope["data"]) == 1
        assert envelope["data"][0]["Code"] == "2330"

    def test_company_command_json_output(self, runner):
        data = [{"公司代號": "2330", "公司名稱": "台積電"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["company", "t187ap03-l", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True

    def test_broker_command_json_output(self, runner):
        data = [{"Code": "1234", "Name": "Test Broker"}]
        with _mock_fetch(data):
            result = runner.invoke(cli, ["broker", "brokerlist", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True

    def test_stock_group_has_44_commands(self, runner):
        """Stock group should have 44 commands (matching endpoint count)."""
        result = runner.invoke(cli, ["stock", "--help"])
        # Filter to just command lines (those under Commands:)
        in_commands = False
        command_count = 0
        for line in result.output.split("\n"):
            if "Commands:" in line:
                in_commands = True
                continue
            if in_commands and line.strip():
                command_count += 1
        assert command_count == 45


class TestDryRun:
    """Test --dry-run flag on fetch, domain shortcuts, and schema."""

    def test_fetch_dry_run_emits_preview(self, runner):
        result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--dry-run"])
        assert result.exit_code == 0
        preview = json.loads(result.output)
        assert preview["dry_run"] is True
        assert preview["method"] == "GET"
        assert "openapi.twse.com.tw" in preview["url"]
        assert preview["endpoint"] == "stock.stock-day-all"

    def test_fetch_dry_run_with_filters(self, runner):
        result = runner.invoke(
            cli, ["fetch", "stock.stock-day-all", "--dry-run", "--fields", "Code,Name", "--code", "2330", "--limit", "5"]
        )
        assert result.exit_code == 0
        preview = json.loads(result.output)
        assert preview["filters"]["fields"] == ["Code", "Name"]
        assert preview["filters"]["code"] == "2330"
        assert preview["filters"]["limit"] == 5

    def test_fetch_dry_run_no_http_call(self, runner):
        """--dry-run should NOT make any HTTP call."""
        with patch("twstock_cli.client.TWStockClient") as mock_cls:
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--dry-run"])
        assert result.exit_code == 0
        mock_cls.assert_not_called()

    def test_fetch_dry_run_unknown_endpoint(self, runner):
        result = runner.invoke(cli, ["fetch", "NONEXISTENT", "--dry-run", "--json"])
        assert result.exit_code == 2

    def test_domain_shortcut_dry_run(self, runner):
        result = runner.invoke(cli, ["stock", "stock-day-all", "--dry-run"])
        assert result.exit_code == 0
        preview = json.loads(result.output)
        assert preview["dry_run"] is True
        assert preview["endpoint"] == "stock.stock-day-all"

    def test_schema_dry_run(self, runner):
        result = runner.invoke(cli, ["schema", "stock.stock-day-all", "--dry-run"])
        assert result.exit_code == 0
        preview = json.loads(result.output)
        assert preview["dry_run"] is True
        assert preview["command"] == "schema"
        assert "openapi.twse.com.tw" in preview["url"]


class TestStdinInput:
    """Test --stdin JSON input on fetch command."""

    def test_stdin_with_endpoint(self, runner):
        data = [{"Code": "2330", "Name": "台積電"}]
        stdin_json = '{"endpoint": "stock.stock-day-all"}'
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True

    def test_stdin_fields_as_array(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "Volume": "100"}]
        stdin_json = '{"endpoint": "stock.stock-day-all", "fields": ["Code", "Name"]}'
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["data"] == [{"Code": "2330", "Name": "台積電"}]

    def test_stdin_fields_as_string(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "Volume": "100"}]
        stdin_json = '{"endpoint": "stock.stock-day-all", "fields": "Code,Name"}'
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["data"] == [{"Code": "2330", "Name": "台積電"}]

    def test_stdin_cli_flag_overrides(self, runner):
        data = [{"Code": "2330", "Name": "台積電", "Volume": "100"}]
        stdin_json = '{"endpoint": "stock.stock-day-all", "fields": "Volume"}'
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "--stdin", "--json", "--fields", "Code,Name"], input=stdin_json)
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        # CLI --fields "Code,Name" should override stdin "Volume"
        assert envelope["data"] == [{"Code": "2330", "Name": "台積電"}]

    def test_stdin_positional_overrides(self, runner):
        data = [{"Code": "2330"}]
        stdin_json = '{"endpoint": "stock.bwibbu-all"}'
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "stock.stock-day-all", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 0
        # Positional endpoint_ref should override stdin

    def test_stdin_missing_endpoint(self, runner):
        stdin_json = '{"fields": "Code"}'
        result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 2
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert "Missing endpoint" in envelope["error"]["message"]

    def test_stdin_invalid_json(self, runner):
        result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input="not valid json")
        assert result.exit_code == 2
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert "Invalid JSON" in envelope["error"]["message"]

    def test_stdin_empty(self, runner):
        result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input="")
        assert result.exit_code == 2
        envelope = json.loads(result.output)
        assert envelope["ok"] is False
        assert "No input" in envelope["error"]["message"]

    def test_stdin_unknown_keys_ignored(self, runner):
        data = [{"Code": "2330"}]
        stdin_json = '{"endpoint": "stock.stock-day-all", "unknown_key": "value"}'
        with _mock_fetch(data):
            result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 0

    def test_stdin_with_control_chars_rejected(self, runner):
        stdin_json = '{"endpoint": "stock.stock-day-all", "code": "23\\u000030"}'
        result = runner.invoke(cli, ["fetch", "--stdin", "--json"], input=stdin_json)
        assert result.exit_code == 2


class TestLazyGroup:
    def test_help_lists_all_groups(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "stock" in result.output
        assert "company" in result.output
        assert "broker" in result.output

    def test_help_lists_core_commands(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "fetch" in result.output
        assert "endpoints" in result.output
        assert "version" in result.output


class TestT86WebEndpoint:
    """Test T86 三大法人買賣超日報 web API endpoint."""

    _T86_RAW = [
        {
            "證券代號": "2330",
            "證券名稱": "台積電",
            "外陸資買賣超股數(不含外資自營商)": "5,000",
            "投信買賣超股數": "1,000",
            "自營商買賣超股數": "500",
            "三大法人買賣超股數": "6,500",
        },
        {
            "證券代號": "2317",
            "證券名稱": "鴻海",
            "外陸資買賣超股數(不含外資自營商)": "-3,000",
            "投信買賣超股數": "200",
            "自營商買賣超股數": "-100",
            "三大法人買賣超股數": "-2,900",
        },
    ]

    def test_fetch_t86_json_with_aliases(self, runner):
        with _mock_fetch_web(self._T86_RAW):
            result = runner.invoke(cli, ["fetch", "stock.t86", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True
        # Field aliases should have been applied
        assert envelope["data"][0]["Code"] == "2330"
        assert envelope["data"][0]["Name"] == "台積電"
        assert envelope["data"][0]["ForeignNet"] == "5,000"
        assert envelope["data"][0]["InstitutionalNet"] == "6,500"

    def test_fetch_t86_with_code_filter(self, runner):
        with _mock_fetch_web(self._T86_RAW):
            result = runner.invoke(cli, ["fetch", "stock.t86", "--json", "--code", "2330"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert len(envelope["data"]) == 1
        assert envelope["data"][0]["Code"] == "2330"

    def test_fetch_t86_with_limit(self, runner):
        with _mock_fetch_web(self._T86_RAW):
            result = runner.invoke(cli, ["fetch", "stock.t86", "--json", "--limit", "1"])
        envelope = json.loads(result.output)
        assert len(envelope["data"]) == 1

    def test_fetch_t86_with_fields(self, runner):
        with _mock_fetch_web(self._T86_RAW):
            result = runner.invoke(cli, ["fetch", "stock.t86", "--json", "--fields", "Code,Name,InstitutionalNet"])
        envelope = json.loads(result.output)
        assert list(envelope["data"][0].keys()) == ["Code", "Name", "InstitutionalNet"]

    def test_fetch_t86_dry_run(self, runner):
        result = runner.invoke(cli, ["fetch", "stock.t86", "--dry-run"])
        assert result.exit_code == 0
        preview = json.loads(result.output)
        assert preview["dry_run"] is True
        assert "twse.com.tw" in preview["url"]
        assert preview["params"]["selectType"] == "ALLBUT0999"

    def test_fetch_t86_dry_run_with_date(self, runner):
        result = runner.invoke(cli, ["fetch", "stock.t86", "--dry-run", "--date", "20260316"])
        assert result.exit_code == 0
        preview = json.loads(result.output)
        assert preview["params"]["date"] == "20260316"

    def test_stock_t86_domain_shortcut(self, runner):
        with _mock_fetch_web(self._T86_RAW):
            result = runner.invoke(cli, ["stock", "t86", "--json"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True
        assert envelope["data"][0]["Code"] == "2330"

    def test_stock_t86_domain_shortcut_with_date(self, runner):
        with _mock_fetch_web(self._T86_RAW):
            result = runner.invoke(cli, ["stock", "t86", "--json", "--date", "20260316"])
        assert result.exit_code == 0
        envelope = json.loads(result.output)
        assert envelope["ok"] is True

    def test_resolve_t86_by_dotted_name(self):
        from twstock_cli.endpoints import resolve_endpoint

        ep = resolve_endpoint("stock.t86")
        assert ep is not None
        assert ep.base_url == "https://www.twse.com.tw/rwd/zh"
        assert ep.field_aliases["證券代號"] == "Code"

    def test_search_t86(self):
        from twstock_cli.endpoints import list_endpoints

        results = list_endpoints(search="t86")
        assert len(results) >= 1
        assert any(r["name"] == "stock.t86" for r in results)

    def test_search_institutional(self):
        from twstock_cli.endpoints import list_endpoints

        results = list_endpoints(search="法人")
        assert any(r["name"] == "stock.t86" for r in results)


class TestVersionCommand:
    def test_version_flag(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "twstock" in result.output

    def test_version_command(self, runner):
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
