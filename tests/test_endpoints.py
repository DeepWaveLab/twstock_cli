"""Tests for endpoint registry — resolve, list, search."""

from twse_cli.endpoints import ENDPOINTS, EndpointDef, list_endpoints, resolve_endpoint


class TestEndpointRegistry:
    def test_has_144_endpoints(self):
        assert len(ENDPOINTS) == 144

    def test_endpoint_is_frozen_dataclass(self):
        ep = next(iter(ENDPOINTS.values()))
        assert isinstance(ep, EndpointDef)

    def test_all_endpoints_have_required_fields(self):
        for key, ep in ENDPOINTS.items():
            assert ep.path.startswith("/"), f"{key}: path should start with /"
            assert ep.cli_name, f"{key}: cli_name is empty"
            assert ep.group in ("stock", "company", "broker", "other"), f"{key}: invalid group {ep.group}"
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
        assert len(results) == 144

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

    def test_existing_endpoints_unaffected(self):
        """All 143 original endpoints should have no base_url set."""
        for key, ep in ENDPOINTS.items():
            if key == "stock.t86":
                continue
            assert ep.base_url is None, f"{key} should not have base_url"
            assert ep.default_params == {}, f"{key} should have empty default_params"
            assert ep.field_aliases == {}, f"{key} should have empty field_aliases"
