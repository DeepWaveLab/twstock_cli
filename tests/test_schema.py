"""Tests for runtime schema introspection."""

from twse_cli.schema import analyze_schema


class TestAnalyzeSchema:
    def test_basic_schema(self):
        data = [
            {"Code": "2330", "Name": "台積電", "ClosingPrice": "595.00"},
            {"Code": "2317", "Name": "鴻海", "ClosingPrice": "100.50"},
        ]
        result = analyze_schema(data, endpoint_name="stock.test", description="Test", path="/test")
        assert result["endpoint"] == "stock.test"
        assert result["record_count"] == 2
        assert len(result["fields"]) == 3
        assert result["fields"][0]["name"] == "Code"

    def test_empty_data(self):
        result = analyze_schema([], endpoint_name="test", description="Test", path="/test")
        assert result["record_count"] == 0
        assert result["fields"] == []

    def test_type_inference_decimal(self):
        data = [{"Price": "595.00"}, {"Price": "100.50"}]
        result = analyze_schema(data)
        assert result["fields"][0]["type"] == "decimal"

    def test_type_inference_integer(self):
        data = [{"Volume": "36317450"}, {"Volume": "12345678"}]
        result = analyze_schema(data)
        assert result["fields"][0]["type"] == "integer"

    def test_type_inference_string(self):
        data = [{"Name": "台積電"}, {"Name": "鴻海"}]
        result = analyze_schema(data)
        assert result["fields"][0]["type"] == "string"

    def test_non_empty_percentage(self):
        data = [{"Code": "2330"}, {"Code": ""}, {"Code": "2317"}]
        result = analyze_schema(data)
        assert result["fields"][0]["non_empty_pct"] == 67

    def test_example_from_first_non_empty(self):
        data = [{"Code": "2330"}, {"Code": "2317"}]
        result = analyze_schema(data)
        assert result["fields"][0]["example"] == "2330"
