import os
from functools import lru_cache
from time import sleep

import httpx


AMAP_TEXT_SEARCH_URL = "https://restapi.amap.com/v3/place/text"
AMAP_AROUND_SEARCH_URL = "https://restapi.amap.com/v3/place/around"
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"


def search_text_pois(
    keywords: str,
    city: str,
    *,
    limit: int = 10,
) -> list[dict]:
    api_key = _get_api_key()

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

    data = _request_json(AMAP_TEXT_SEARCH_URL, params=params)
    _raise_for_amap_error(data, "AMap text search failed")

    pois = data.get("pois", [])
    if not isinstance(pois, list):
        return []

    return pois


def search_around_pois(
    location: str,
    *,
    keywords: str,
    radius: int = 5000,
    limit: int = 10,
) -> list[dict]:
    api_key = _get_api_key()

    params = {
        "key": api_key,
        "location": location,
        "keywords": keywords,
        "radius": max(1000, min(radius, 50000)),
        "offset": max(1, min(limit, 20)),
        "page": 1,
        "extensions": "base",
        "sortrule": "distance",
        "output": "JSON",
    }

    data = _request_json(AMAP_AROUND_SEARCH_URL, params=params)
    _raise_for_amap_error(data, "AMap around search failed")

    pois = data.get("pois", [])
    if not isinstance(pois, list):
        return []

    return pois


def get_weather_info(
    city_code: str,
    *,
    extensions: str = "all",
) -> dict:
    api_key = _get_api_key()

    params = {
        "key": api_key,
        "city": city_code,
        "extensions": extensions,
        "output": "JSON",
    }

    data = _request_json(AMAP_WEATHER_URL, params=params)
    _raise_for_amap_error(data, "AMap weather query failed")
    return data


@lru_cache(maxsize=64)
def geocode_city(city: str) -> dict:
    """根据城市名动态查询高德地理编码，返回城市中心坐标和 adcode。"""
    api_key = _get_api_key()
    normalized_city = city.strip()
    if not normalized_city:
        raise ValueError("City name is required for geocoding")

    params = {
        "key": api_key,
        "address": normalized_city,
        "output": "JSON",
    }

    data = _request_json(AMAP_GEOCODE_URL, params=params)
    _raise_for_amap_error(data, "AMap geocode query failed")

    geocodes = data.get("geocodes", [])
    if not isinstance(geocodes, list) or not geocodes:
        raise RuntimeError(f"AMap geocode returned no results for city: {city}")

    first = geocodes[0]
    location = str(first.get("location", "")).strip()
    adcode = str(first.get("adcode", "")).strip()
    name = str(first.get("formatted_address", "")).strip() or normalized_city

    if not location:
        raise RuntimeError(f"AMap geocode did not provide location for city: {city}")
    if not adcode:
        raise RuntimeError(f"AMap geocode did not provide adcode for city: {city}")

    return {
        "name": name,
        "location": location,
        "adcode": adcode,
    }


def _get_api_key() -> str:
    api_key = os.getenv("AMAP_WEB_API_KEY")
    if not api_key:
        raise RuntimeError("AMAP_WEB_API_KEY is not configured")
    return api_key


def _request_json(
    url: str,
    *,
    params: dict,
    timeout: float = 8.0,
    max_retries: int = 2,
) -> dict:
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 2):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
            return response.json()
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_error = exc
            print(f"[AMAP_RETRY] attempt={attempt} url={url} error={exc}")

            if attempt > max_retries:
                break

            sleep(0.8 * attempt)

    raise RuntimeError(f"AMap request failed after retries: {last_error}")


def _raise_for_amap_error(data: dict, prefix: str) -> None:
    if data.get("status") == "1":
        return

    info = data.get("info", "Unknown AMap error")
    raise RuntimeError(f"{prefix}: {info}")
