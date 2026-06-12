import app.services.cache_utils as cache_utils
from app.services.cache_utils import TTLCache


def test_ttl_cache_expires_entries(monkeypatch) -> None:
    now = 1000.0
    monkeypatch.setattr(cache_utils.time, "time", lambda: now)
    cache = TTLCache(ttl_seconds=10)

    cache.set("city", "杭州")
    assert cache.get("city") == "杭州"

    now = 1011.0
    assert cache.get("city") is None


def test_ttl_cache_respects_max_size() -> None:
    cache = TTLCache(ttl_seconds=60, max_size=2)

    cache.set("first", 1)
    cache.set("second", 2)
    cache.set("third", 3)

    assert cache.get("first") is None
    assert cache.get("second") == 2
    assert cache.get("third") == 3
