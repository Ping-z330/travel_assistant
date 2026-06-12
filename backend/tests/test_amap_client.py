import pytest

import app.services.amap_client as amap_client
from app.services.amap_client import (
    AmapConfigurationError,
    AmapResponseError,
    search_text_pois,
)


def test_search_text_pois_reports_missing_api_key(monkeypatch) -> None:
    monkeypatch.delenv("AMAP_WEB_API_KEY", raising=False)

    with pytest.raises(AmapConfigurationError):
        search_text_pois("景点", "杭州")


def test_search_text_pois_reports_amap_business_error(monkeypatch) -> None:
    monkeypatch.setenv("AMAP_WEB_API_KEY", "test-key")
    monkeypatch.setattr(
        amap_client,
        "_request_json",
        lambda *args, **kwargs: {"status": "0", "info": "INVALID_USER_KEY"},
    )

    with pytest.raises(AmapResponseError, match="INVALID_USER_KEY"):
        search_text_pois("景点", "杭州")


def test_search_text_pois_returns_empty_list_for_non_list_pois(monkeypatch) -> None:
    monkeypatch.setenv("AMAP_WEB_API_KEY", "test-key")
    monkeypatch.setattr(
        amap_client,
        "_request_json",
        lambda *args, **kwargs: {"status": "1", "pois": {}},
    )

    assert search_text_pois("景点", "杭州") == []
