"""Tests for endpoint registry — resolve, list, search."""

import json
from pathlib import Path

from twstock_cli.endpoints import ENDPOINTS, EndpointDef, list_endpoints, resolve_endpoint

INTEGRATION_DIR = Path(__file__).parent / "integration"


class TestEndpointRegistry:
    def test_endpoint_count(self):
        assert len(ENDPOINTS) == 359  # 144 TWSE + 8 web + 207 TPEX

    def test_endpoint_is_frozen_dataclass(self):
        ep = next(iter(ENDPOINTS.values()))
        assert isinstance(ep, EndpointDef)

    def test_all_endpoints_have_required_fields(self):
        valid_groups = (
            "stock",
            "company",
            "broker",
            "other",
            "otc",
            "otc_company",
            "otc_index",
            "otc_esg",
            "otc_financial",
            "otc_esb",
            "otc_gisa",
            "otc_warrant",
            "otc_fund",
            "otc_gold",
            "otc_bond",
            "otc_broker",
            "web",
        )
        for key, ep in ENDPOINTS.items():
            assert ep.path.startswith("/"), f"{key}: path should start with /"
            assert ep.cli_name, f"{key}: cli_name is empty"
            assert ep.group in valid_groups, f"{key}: invalid group {ep.group}"
            assert ep.description, f"{key}: description is empty"


class TestResolveEndpoint:
    def test_resolve_by_dotted_name(self):
        ep = resolve_endpoint("stock.stock-day-all")
        assert ep is not None
        assert ep.path == "/exchangeReport/STOCK_DAY_ALL"

    def test_resolve_by_raw_path(self):
        ep = resolve_endpoint("/exchangeReport/STOCK_DAY_ALL")
        assert ep is not None
        assert ep.cli_name == "stock-day-all"

    def test_resolve_by_api_code(self):
        ep = resolve_endpoint("STOCK_DAY_ALL")
        assert ep is not None

    def test_resolve_returns_none_for_unknown(self):
        assert resolve_endpoint("nonexistent.endpoint") is None
        assert resolve_endpoint("/nonexistent/path") is None


class TestListEndpoints:
    def test_list_all(self):
        results = list_endpoints()
        assert len(results) == 359

    def test_list_by_category(self):
        results = list_endpoints(category="stock")
        assert all(r["group"] == "stock" for r in results)
        assert len(results) == 45

    def test_search_chinese(self):
        results = list_endpoints(search="股利")
        assert len(results) >= 1

    def test_search_english_path(self):
        results = list_endpoints(search="STOCK_DAY")
        assert len(results) >= 1

    def test_search_no_results(self):
        results = list_endpoints(search="xyznonexistent")
        assert results == []

    def test_with_fields(self):
        results = list_endpoints(search="stock.stock-day-all", with_fields=True)
        assert len(results) == 1
        assert "fields" in results[0]


class TestWebApiEndpoint:
    def test_t86_has_base_url(self):
        ep = ENDPOINTS["stock.t86"]
        assert ep.base_url == "https://www.twse.com.tw/rwd/zh"

    def test_t86_has_default_params(self):
        ep = ENDPOINTS["stock.t86"]
        assert ep.default_params["selectType"] == "ALLBUT0999"
        assert ep.default_params["response"] == "json"

    def test_t86_has_field_aliases(self):
        ep = ENDPOINTS["stock.t86"]
        assert ep.field_aliases["證券代號"] == "Code"
        assert ep.field_aliases["三大法人買賣超股數"] == "InstitutionalNet"

    def test_t86_resolve_by_dotted_name(self):
        ep = resolve_endpoint("stock.t86")
        assert ep is not None
        assert ep.path == "/fund/T86"

    def test_t86_resolve_by_cli_name(self):
        ep = resolve_endpoint("t86")
        assert ep is not None
        assert ep.group == "stock"

    def test_twse_openapi_endpoints_unaffected(self):
        """All 143 original TWSE OpenAPI endpoints should have no base_url set."""
        for key, ep in ENDPOINTS.items():
            if key == "stock.t86" or ep.group.startswith("otc") or ep.group == "web":
                continue
            assert ep.base_url is None, f"{key} should not have base_url"
            assert ep.default_params == {}, f"{key} should have empty default_params"
            assert ep.field_aliases == {}, f"{key} should have empty field_aliases"


class TestTpexEndpoints:
    def test_otc_endpoint_count(self):
        otc = [k for k in ENDPOINTS if k.startswith("otc.")]
        assert len(otc) == 64  # 18 Phase 1 + 46 Phase 2

    def test_otc_company_endpoint_count(self):
        otc_company = [k for k in ENDPOINTS if k.startswith("otc_company.")]
        assert len(otc_company) == 29  # 7 Phase 1 + 22 Phase 2

    def test_all_tpex_endpoint_count(self):
        tpex = [k for k in ENDPOINTS if k.startswith("otc")]
        assert len(tpex) == 207  # All TPEX OpenAPI endpoints

    def test_tpex_endpoints_have_base_url(self):
        from twstock_cli.endpoints import TPEX_BASE_URL

        for key, ep in ENDPOINTS.items():
            if ep.group.startswith("otc"):
                assert ep.base_url == TPEX_BASE_URL, f"{key}: missing TPEX base_url"

    def test_tpex_endpoints_no_field_aliases(self):
        """TPEX OpenAPI endpoints return list-of-dicts, not fields+data."""
        for key, ep in ENDPOINTS.items():
            if ep.group.startswith("otc"):
                assert ep.field_aliases == {}, f"{key}: should not have field_aliases"
                assert ep.default_params == {}, f"{key}: should not have default_params"

    def test_resolve_otc_by_dotted_name(self):
        ep = resolve_endpoint("otc.mainboard-daily-close-quotes")
        assert ep is not None
        assert ep.path == "/tpex_mainboard_daily_close_quotes"

    def test_resolve_otc_company_by_dotted_name(self):
        ep = resolve_endpoint("otc_company.t187ap05-o")
        assert ep is not None
        assert ep.group == "otc_company"

    def test_search_otc_by_chinese(self):
        results = list_endpoints(search="上櫃")
        assert len(results) >= 18

    def test_list_by_otc_category(self):
        results = list_endpoints(category="otc")
        assert all(r["group"] == "otc" for r in results)
        assert len(results) == 64

    def test_list_by_otc_company_category(self):
        results = list_endpoints(category="otc_company")
        assert all(r["group"] == "otc_company" for r in results)
        assert len(results) == 29


class TestIntegrationTestSync:
    """Verify every endpoint has at least one integration test case."""

    def _load_all_tested_endpoints(self) -> set[str]:
        """Parse all test_cases*.json and extract endpoint dotted names from commands."""
        tested = set()
        for f in INTEGRATION_DIR.glob("test_cases*.json"):
            for case in json.loads(f.read_text()):
                if "id" not in case:
                    continue
                cmd = case.get("command", [])
                if len(cmd) >= 2 and cmd[0] == "fetch" and not cmd[1].startswith("-"):
                    tested.add(cmd[1])
        return tested

    def test_all_endpoints_have_integration_tests(self):
        """Every endpoint in the registry must have at least one test case."""
        tested = self._load_all_tested_endpoints()
        endpoint_keys = set(ENDPOINTS.keys())
        untested = endpoint_keys - tested
        assert not untested, (
            f"{len(untested)} endpoints lack integration tests: {sorted(untested)[:10]}{'...' if len(untested) > 10 else ''}"
        )
