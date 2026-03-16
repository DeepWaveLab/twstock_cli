"""Tests for disk-based response cache."""

import time

import pytest

from twse_cli.cache import _cache_path, _ttl_for_path, clear_cache, get_cached, set_cached


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Use a temp directory for cache in all tests."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    yield tmp_path


class TestCacheReadWrite:
    def test_set_and_get_cached(self):
        data = [{"Code": "2330", "Name": "TSMC"}]
        set_cached("/exchangeReport/STOCK_DAY_ALL", data)
        result = get_cached("/exchangeReport/STOCK_DAY_ALL")
        assert result == data

    def test_get_cached_returns_none_when_empty(self):
        assert get_cached("/nonexistent") is None

    def test_cache_creates_directory(self, isolated_cache):
        set_cached("/test", [{"ok": True}])
        cache_dir = isolated_cache / "twse-cli"
        assert cache_dir.exists()
        assert len(list(cache_dir.glob("*.json"))) == 1

    def test_cache_preserves_chinese(self):
        data = [{"公司代號": "2330", "公司名稱": "台積電"}]
        set_cached("/test", data)
        result = get_cached("/test")
        assert result[0]["公司名稱"] == "台積電"


class TestCacheTTL:
    def test_ttl_daily_for_exchange_report(self):
        ttl = _ttl_for_path("/exchangeReport/STOCK_DAY_ALL")
        assert ttl == 4 * 3600  # 4 hours

    def test_ttl_static_for_company(self):
        ttl = _ttl_for_path("/company/newlisting")
        assert ttl == 24 * 3600  # 24 hours

    def test_ttl_static_for_broker(self):
        ttl = _ttl_for_path("/brokerService/brokerList")
        assert ttl == 24 * 3600

    def test_expired_cache_returns_none(self, isolated_cache):
        data = [{"Code": "2330"}]
        set_cached("/exchangeReport/STOCK_DAY_ALL", data)
        # Manually set mtime to 5 hours ago (past 4h TTL)
        cache_file = _cache_path("/exchangeReport/STOCK_DAY_ALL")
        import os

        old_time = time.time() - (5 * 3600)
        os.utime(cache_file, (old_time, old_time))
        assert get_cached("/exchangeReport/STOCK_DAY_ALL") is None


class TestCacheClear:
    def test_clear_cache(self):
        set_cached("/a", [{"a": 1}])
        set_cached("/b", [{"b": 2}])
        count = clear_cache()
        assert count == 2
        assert get_cached("/a") is None
        assert get_cached("/b") is None

    def test_clear_empty_cache(self):
        assert clear_cache() == 0
