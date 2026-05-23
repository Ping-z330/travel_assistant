from dataclasses import dataclass

from app.services.amap_client import geocode_city, get_weather_info
from app.services.cache_utils import TTLCache


WEATHER_CACHE = TTLCache(ttl_seconds=1800)


@dataclass
class WeatherSnapshot:
    city: str
    report_time: str
    summary: str
    temperature_hint: str
    suggestion: str


# get_trip_weather_snapshot 函数负责获取指定城市的天气快照信息，包括天气概况、温度提示和出行建议等内容，并使用缓存机制优化性能。
def get_trip_weather_snapshot(city: str, *, max_days: int = 3) -> WeatherSnapshot:
    cache_key = f"weather:{city.strip()}:{max_days}"
    cached = WEATHER_CACHE.get(cache_key)
    if cached is not None:
        print(f"[WEATHER_CACHE] hit city={city} max_days={max_days}")
        return cached

    adcode = resolve_city_adcode(city)
    raw = get_weather_info(adcode, extensions="all")

    forecasts = raw.get("forecasts", [])
    if not forecasts:
        raise RuntimeError("AMap weather response does not contain forecasts")

    first_forecast = forecasts[0]
    casts = first_forecast.get("casts", [])
    if not casts:
        raise RuntimeError("AMap weather response does not contain cast details")

    selected_casts = casts[:max_days]
    summary_lines: list[str] = []

    for index, cast in enumerate(selected_casts, start=1):
        dayweather = str(cast.get("dayweather", "")).strip() or "天气待确认"
        nightweather = str(cast.get("nightweather", "")).strip()
        daytemp = str(cast.get("daytemp", "")).strip()
        nighttemp = str(cast.get("nighttemp", "")).strip()

        if nightweather and nightweather != dayweather:
            weather_text = f"{dayweather}转{nightweather}"
        else:
            weather_text = dayweather

        temp_text = f"{nighttemp}-{daytemp}°C" if daytemp and nighttemp else "温度待确认"
        summary_lines.append(f"- 第{index}天：{weather_text}，{temp_text}")

    city_name = str(first_forecast.get("city", "")).strip() or city
    report_time = str(first_forecast.get("reporttime", "")).strip() or "时间待确认"
    temperature_hint = "；".join(line.replace("- ", "") for line in summary_lines)
    suggestion = _build_weather_suggestion(selected_casts)

    snapshot = WeatherSnapshot(
        city=city_name,
        report_time=report_time,
        summary="\n".join(summary_lines),
        temperature_hint=temperature_hint,
        suggestion=suggestion,
    )
    WEATHER_CACHE.set(cache_key, snapshot)
    return snapshot


# format_weather_for_prompt 函数负责将天气快照信息格式化为一个适合提示词使用的字符串，
# 包括天气概况、温度提示和出行建议等内容，这些信息将被传
def format_weather_for_prompt(weather: WeatherSnapshot) -> str:
    return (
        f"{weather.city}天气参考：\n"
        f"发布时间：{weather.report_time}\n"
        f"{weather.summary}\n"
        f"出行建议：{weather.suggestion}"
    )


def resolve_city_adcode(city: str) -> str:
    result = geocode_city(city)
    adcode = result.get("adcode", "").strip()
    if not adcode:
        raise ValueError(f"Unable to resolve city adcode: {city}")
    return adcode


def _build_weather_suggestion(casts: list[dict]) -> str:
    weather_text = " ".join(
        f"{cast.get('dayweather', '')} {cast.get('nightweather', '')}" for cast in casts
    )

    if "雨" in weather_text:
        return "行程中建议准备雨具，优先把重要户外景点安排在降雨较弱的时段。"
    if "雪" in weather_text:
        return "建议注意保暖和防滑，优先安排交通便利或室内景点。"
    if "晴" in weather_text:
        return "整体适合户外活动，建议注意防晒和补水。"

    return "建议根据天气变化灵活调整室内外行程搭配。"
