import os

import httpx


AMAP_TEXT_SEARCH_URL = "https://restapi.amap.com/v3/place/text"
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"


def search_text_pois(
    keywords: str,
    city: str,
    *,
    limit: int = 10,
) -> list[dict]:
    api_key = os.getenv("AMAP_WEB_API_KEY")
    if not api_key:
        raise RuntimeError("AMAP_WEB_API_KEY is not configured")

    params = {
        "key": api_key,
        "keywords": keywords,
        "city": city,
        "citylimit": "true",
        "offset": max(1, min(limit, 20)),
        "page": 1,
        "extensions": "base",
        "output": "JSON",
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.get(AMAP_TEXT_SEARCH_URL, params=params)
        response.raise_for_status()

    data = response.json()
    if data.get("status") != "1":
        info = data.get("info", "Unknown AMap error")
        raise RuntimeError(f"AMap text search failed: {info}")

    pois = data.get("pois", [])
    if not isinstance(pois, list):
        return []

    return pois


def get_weather_info(
    city_code: str,
    *,
    extensions: str = "all",
) -> dict:
    api_key = os.getenv("AMAP_WEB_API_KEY")
    if not api_key:
        raise RuntimeError("AMAP_WEB_API_KEY is not configured")

    params = {
        "key": api_key,
        "city": city_code,
        "extensions": extensions,
        "output": "JSON",
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.get(AMAP_WEATHER_URL, params=params)
        response.raise_for_status()

    data = response.json()
    if data.get("status") != "1":
        info = data.get("info", "Unknown AMap weather error")
        raise RuntimeError(f"AMap weather query failed: {info}")

    return data
