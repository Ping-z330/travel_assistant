import app.services.weather_service as weather_service
import pytest
from app.services.amap_client import AmapResponseError
from app.services.weather_service import get_trip_weather_snapshot


def test_get_trip_weather_snapshot_builds_summary_and_rain_suggestion(monkeypatch) -> None:
    monkeypatch.setattr(weather_service, "resolve_city_adcode", lambda city: "330100")
    monkeypatch.setattr(
        weather_service,
        "get_weather_info",
        lambda *args, **kwargs: {
            "forecasts": [
                {
                    "city": "杭州",
                    "reporttime": "2026-06-12 10:00:00",
                    "casts": [
                        {
                            "dayweather": "小雨",
                            "nightweather": "多云",
                            "daytemp": "26",
                            "nighttemp": "20",
                        },
                        {
                            "dayweather": "晴",
                            "nightweather": "晴",
                            "daytemp": "28",
                            "nighttemp": "21",
                        },
                    ],
                }
            ]
        },
    )

    snapshot = get_trip_weather_snapshot("杭州-weather-test", max_days=2)

    assert snapshot.city == "杭州"
    assert "- 第1天：小雨转多云，20-26°C" in snapshot.summary
    assert "- 第2天：晴，21-28°C" in snapshot.summary
    assert "准备雨具" in snapshot.suggestion


def test_get_trip_weather_snapshot_reports_invalid_amap_response(monkeypatch) -> None:
    monkeypatch.setattr(weather_service, "resolve_city_adcode", lambda city: "330100")
    monkeypatch.setattr(
        weather_service,
        "get_weather_info",
        lambda *args, **kwargs: {"forecasts": []},
    )

    with pytest.raises(AmapResponseError, match="does not contain forecasts"):
        get_trip_weather_snapshot("杭州-weather-invalid-test")
