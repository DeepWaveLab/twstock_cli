"""Tests for data normalization — string→number, ROC→ISO dates."""

from twstock_cli.normalize import normalize_data, normalize_record


class TestNormalizeRecord:
    def test_numeric_integer(self):
        result = normalize_record({"TradeVolume": "36317450"})
        assert result["TradeVolume"] == 36317450

    def test_numeric_float(self):
        result = normalize_record({"ClosingPrice": "595.00"})
        assert result["ClosingPrice"] == 595.0

    def test_numeric_with_commas(self):
        result = normalize_record({"TradeValue": "1,234,567,890"})
        assert result["TradeValue"] == 1234567890

    def test_roc_date_conversion(self):
        result = normalize_record({"日期": "1150313"})
        assert result["日期"] == "2026-03-13"

    def test_roc_date_with_slashes(self):
        result = normalize_record({"出表日期": "115/03/13"})
        assert result["出表日期"] == "2026-03-13"

    def test_preserves_code_field(self):
        result = normalize_record({"Code": "2330", "Name": "台積電"})
        assert result["Code"] == "2330"
        assert result["Name"] == "台積電"

    def test_preserves_chinese_code_field(self):
        result = normalize_record({"公司代號": "2330", "公司名稱": "台積電"})
        assert result["公司代號"] == "2330"
        assert result["公司名稱"] == "台積電"

    def test_empty_string_preserved(self):
        result = normalize_record({"Field": ""})
        assert result["Field"] == ""

    def test_non_numeric_string_preserved(self):
        result = normalize_record({"Industry": "半導體業"})
        assert result["Industry"] == "半導體業"

    def test_mixed_record(self):
        result = normalize_record(
            {
                "Code": "2330",
                "ClosingPrice": "595.00",
                "TradeVolume": "36317450",
                "Change": "+5.00",
                "日期": "1150313",
            }
        )
        assert result["Code"] == "2330"
        assert result["ClosingPrice"] == 595.0
        assert result["TradeVolume"] == 36317450
        assert result["日期"] == "2026-03-13"


class TestNormalizeData:
    def test_normalizes_multiple_records(self):
        data = [
            {"Code": "2330", "ClosingPrice": "595.00"},
            {"Code": "2317", "ClosingPrice": "100.50"},
        ]
        result = normalize_data(data)
        assert result[0]["ClosingPrice"] == 595.0
        assert result[1]["ClosingPrice"] == 100.5
        assert result[0]["Code"] == "2330"

    def test_empty_data(self):
        assert normalize_data([]) == []
