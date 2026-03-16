"""Tests for --help-json flag — structured command metadata."""

import json

import pytest
from click.testing import CliRunner

from twse_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestHelpJsonTopLevel:
    def test_top_level_lists_commands(self, runner):
        result = runner.invoke(cli, ["--help-json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "cli"
        assert "commands" in data
        assert "fetch" in data["commands"]
        assert "endpoints" in data["commands"]
        assert "schema" in data["commands"]
        assert "version" in data["commands"]
        assert "serve" in data["commands"]
        assert "stock" in data["commands"]
        assert "company" in data["commands"]
        assert "broker" in data["commands"]


class TestHelpJsonFetch:
    def test_fetch_lists_params(self, runner):
        result = runner.invoke(cli, ["fetch", "--help-json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "fetch"
        assert "params" in data
        param_names = {p["name"] for p in data["params"]}
        assert "ENDPOINT_REF" in param_names or "endpoint_ref" in param_names
        flag_names = {p.get("flag") for p in data["params"] if "flag" in p}
        assert "--json" in flag_names
        assert "--fields" in flag_names
        assert "--code" in flag_names
        assert "--limit" in flag_names
        assert "--dry-run" in flag_names
        assert "--stdin" in flag_names

    def test_fetch_param_types(self, runner):
        result = runner.invoke(cli, ["fetch", "--help-json"])
        data = json.loads(result.output)
        params_by_flag = {p.get("flag"): p for p in data["params"] if "flag" in p}
        assert params_by_flag["--limit"]["type"] == "int"
        assert params_by_flag["--json"]["type"] == "bool"
        assert params_by_flag["--fields"]["type"] == "string"


class TestHelpJsonEndpoints:
    def test_endpoints_includes_choice(self, runner):
        result = runner.invoke(cli, ["endpoints", "--help-json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        params_by_flag = {p.get("flag"): p for p in data["params"] if "flag" in p}
        cat = params_by_flag["--category"]
        assert cat["type"] == "choice"
        assert "stock" in cat["choices"]
        assert "company" in cat["choices"]


class TestHelpJsonDomainShortcuts:
    def test_stock_group_lists_commands(self, runner):
        result = runner.invoke(cli, ["stock", "--help-json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "stock"
        assert "commands" in data
        assert "stock-day-all" in data["commands"]

    def test_stock_subcommand_lists_params(self, runner):
        result = runner.invoke(cli, ["stock", "stock-day-all", "--help-json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "stock-day-all"
        flag_names = {p.get("flag") for p in data["params"] if "flag" in p}
        assert "--json" in flag_names
        assert "--fields" in flag_names
        assert "--dry-run" in flag_names


class TestHelpJsonSchema:
    def test_schema_lists_params(self, runner):
        result = runner.invoke(cli, ["schema", "--help-json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "schema"
        flag_names = {p.get("flag") for p in data["params"] if "flag" in p}
        assert "--json" in flag_names
        assert "--dry-run" in flag_names


class TestHelpJsonPrecedence:
    def test_help_json_wins_over_json_flag(self, runner):
        """--help-json should exit early even if --json is passed."""
        result = runner.invoke(cli, ["fetch", "--help-json", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "params" in data  # It's metadata, not fetch output
