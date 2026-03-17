"""Tests for response sanitization — strip control chars from API data."""

from twstock_cli.sanitize import sanitize_data, sanitize_record


class TestSanitizeRecord:
    def test_clean_data_unchanged(self):
        record = {"Code": "2330", "Name": "台積電", "Price": "595.00"}
        assert sanitize_record(record) == record

    def test_null_byte_stripped(self):
        assert sanitize_record({"Name": "Test\x00Corp"}) == {"Name": "TestCorp"}

    def test_escape_stripped(self):
        assert sanitize_record({"Name": "Ignore\x1bprevious"}) == {"Name": "Ignoreprevious"}

    def test_bell_stripped(self):
        assert sanitize_record({"Name": "Alert\x07!"}) == {"Name": "Alert!"}

    def test_tab_preserved(self):
        assert sanitize_record({"Name": "Col\tVal"}) == {"Name": "Col\tVal"}

    def test_newline_preserved(self):
        assert sanitize_record({"Name": "Line1\nLine2"}) == {"Name": "Line1\nLine2"}

    def test_carriage_return_stripped(self):
        """CR is stripped (TWSE values shouldn't contain it)."""
        assert sanitize_record({"Name": "Line1\r\nLine2"}) == {"Name": "Line1\nLine2"}

    def test_non_string_values_unchanged(self):
        record = {"Code": "2330", "Price": 595.0, "Volume": 36317450}
        assert sanitize_record(record) == record

    def test_empty_string_unchanged(self):
        assert sanitize_record({"Name": ""}) == {"Name": ""}

    def test_multiple_control_chars(self):
        assert sanitize_record({"Name": "\x00\x01\x02Test\x7f"}) == {"Name": "Test"}


class TestSanitizeData:
    def test_sanitizes_all_records(self):
        data = [
            {"Code": "2330", "Name": "台積電\x00"},
            {"Code": "2317", "Name": "鴻海\x1b"},
        ]
        result = sanitize_data(data)
        assert result == [
            {"Code": "2330", "Name": "台積電"},
            {"Code": "2317", "Name": "鴻海"},
        ]

    def test_empty_list(self):
        assert sanitize_data([]) == []
