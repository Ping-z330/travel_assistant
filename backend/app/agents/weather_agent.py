from time import perf_counter

from app.agents.schemas import WeatherAgentResult
from app.models.trip import TripPlanRequest
from app.services.weather_service import (
    format_weather_for_prompt,
    get_trip_weather_snapshot,
)


class WeatherAgent:
    """负责天气查询与天气上下文整理。"""

    def run(self, request: TripPlanRequest) -> WeatherAgentResult:
        start = perf_counter()
        print(f"[WEATHER_AGENT] start city={request.city}")

        snapshot = get_trip_weather_snapshot(request.city)
        prompt_context = format_weather_for_prompt(snapshot)
        elapsed_ms = round((perf_counter() - start) * 1000, 1)

        print(
            f"[WEATHER_AGENT] success city={request.city} "
            f"report_city={snapshot.city} prompt_chars={len(prompt_context)} elapsed_ms={elapsed_ms}"
        )

        return WeatherAgentResult(
            snapshot=snapshot,
            prompt_context=prompt_context,
        )
