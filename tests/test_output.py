"""Tests for output formatting: envelope, field filtering, code filtering."""

import json

from twstock_cli.output import filter_by_code, filter_fields, make_envelope


class TestEnvelope:
    def test_success_envelope(self):
        data = [{"Code": "2330", "Name": "TSMC"}]
        envelope = make_envelope(data)
        assert envelope["ok"] is True
        assert envelope["data"] == data
        assert "error" not in envelope

    def test_success_envelope_is_valid_json(self):
        data = [{"Code": "2330", "Name": "台積電"}]
        envelope = make_envelope(data)
        parsed = json.loads(json.dumps(envelope, ensure_ascii=False))
        assert parsed["ok"] is True
        assert parsed["data"][0]["Name"] == "台積電"

    def test_error_envelope(self):
        envelope = make_envelope(None, ok=False, error={"code": "api_error", "message": "TWSE API returned 503"})
        assert envelope["ok"] is False
        assert envelope["error"]["code"] == "api_error"
        assert "data" not in envelope

    def test_empty_data_envelope(self):
        envelope = make_envelope([])
        assert envelope["ok"] is True
        assert envelope["data"] == []


class TestFilterFields:
    def test_filters_specified_fields(self):
        data = [
            {"Code": "2330", "Name": "TSMC", "ClosingPrice": "595.00", "Volume": "1000"},
        ]
        result = filter_fields(data, "Code,Name,ClosingPrice")
        assert result == [{"Code": "2330", "Name": "TSMC", "ClosingPrice": "595.00"}]

    def test_silently_omits_missing_fields(self):
        data = [{"Code": "2330", "Name": "TSMC"}]
        result = filter_fields(data, "Code,Name,NonExistent")
        assert result == [{"Code": "2330", "Name": "TSMC"}]

    def test_strips_whitespace_in_field_names(self):
        data = [{"Code": "2330", "Name": "TSMC"}]
        result = filter_fields(data, "Code , Name")
        assert result == [{"Code": "2330", "Name": "TSMC"}]

    def test_empty_data(self):
        result = filter_fields([], "Code,Name")
        assert result == []


class TestFilterByCode:
    def test_filters_by_english_code_field(self):
        data = [
            {"Code": "2330", "Name": "TSMC"},
            {"Code": "2317", "Name": "Foxconn"},
        ]
        result = filter_by_code(data, "2330", "Code")
        assert len(result) == 1
        assert result[0]["Code"] == "2330"

    def test_filters_by_chinese_code_field(self):
        data = [
            {"公司代號": "2330", "公司名稱": "台積電"},
            {"公司代號": "2317", "公司名稱": "鴻海"},
        ]
        result = filter_by_code(data, "2330", "公司代號")
        assert len(result) == 1
        assert result[0]["公司代號"] == "2330"

    def test_auto_detects_code_field(self):
        data = [
            {"Code": "2330", "Name": "TSMC"},
            {"Code": "2317", "Name": "Foxconn"},
        ]
        result = filter_by_code(data, "2330", None)
        assert len(result) == 1

    def test_returns_all_if_no_code_field_found(self):
        data = [{"Title": "News 1"}, {"Title": "News 2"}]
        result = filter_by_code(data, "2330", None)
        assert len(result) == 2
