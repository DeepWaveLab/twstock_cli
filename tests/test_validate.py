"""Tests for input validation — control chars, path traversal, injection."""

import pytest
import click

from twse_cli.validate import validate_input, MAX_INPUT_LENGTH


class TestValidateInputClean:
    """Clean inputs should pass through."""

    def test_simple_field_list(self):
        assert validate_input("Code,Name", "--fields") == "Code,Name"

    def test_stock_code(self):
        assert validate_input("2330", "--code") == "2330"

    def test_dotted_endpoint(self):
        assert validate_input("stock.stock-day-all", "ENDPOINT_REF") == "stock.stock-day-all"

    def test_search_keyword_english(self):
        assert validate_input("daily", "--search") == "daily"

    def test_unicode_cjk(self):
        assert validate_input("公司代號,公司名稱", "--fields") == "公司代號,公司名稱"

    def test_empty_string(self):
        assert validate_input("", "--fields") == ""

    def test_strips_whitespace(self):
        assert validate_input("  Code,Name  ", "--fields") == "Code,Name"

    def test_raw_api_path(self):
        assert validate_input("/exchangeReport/STOCK_DAY_ALL", "ENDPOINT_REF") == "/exchangeReport/STOCK_DAY_ALL"


class TestValidateInputControlChars:
    """Control characters should be rejected."""

    def test_null_byte(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("Code\x00Name", "--fields")

    def test_bell(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("23\x07thirty", "--code")

    def test_escape(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("test\x1binput", "--fields")

    def test_del(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("test\x7finput", "--fields")

    def test_backspace(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("test\x08input", "--fields")


class TestValidateInputPathTraversal:
    """Path traversal patterns should be rejected."""

    def test_unix_traversal(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("../etc/passwd", "ENDPOINT_REF")

    def test_windows_traversal(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("..\\windows", "ENDPOINT_REF")

    def test_percent_encoded_lower(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("%2e%2e/foo", "ENDPOINT_REF")

    def test_percent_encoded_upper(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("%2E./bar", "ENDPOINT_REF")


class TestValidateInputInjection:
    """Query/fragment injection should be rejected."""

    def test_query_injection(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("Code?extra=1", "--fields")

    def test_fragment_injection(self):
        with pytest.raises(click.BadParameter, match="forbidden characters"):
            validate_input("Code#fragment", "--fields")


class TestValidateInputMaxLength:
    """Strings exceeding max length should be rejected."""

    def test_at_max_length_passes(self):
        value = "a" * MAX_INPUT_LENGTH
        assert validate_input(value, "--fields") == value

    def test_over_max_length_rejected(self):
        value = "a" * (MAX_INPUT_LENGTH + 1)
        with pytest.raises(click.BadParameter, match="exceeds maximum length"):
            validate_input(value, "--fields")
