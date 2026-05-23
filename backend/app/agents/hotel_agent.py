from time import perf_counter

from app.agents.schemas import HotelAgentResult
from app.models.trip import TripPlanRequest
from app.services.hotel_service import (
    format_hotel_candidates_for_prompt,
    search_trip_hotel_candidates,
)


class HotelAgent:
    """负责酒店候选搜索与酒店上下文整理。"""

    def run(self, request: TripPlanRequest) -> HotelAgentResult:
        start = perf_counter()
        print(
            f"[HOTEL_AGENT] start city={request.city} days={request.days} budget={request.budget}"
        )

        candidates = search_trip_hotel_candidates(request)
        prompt_context = format_hotel_candidates_for_prompt(candidates)
        elapsed_ms = round((perf_counter() - start) * 1000, 1)

        print(
            f"[HOTEL_AGENT] success city={request.city} "
            f"count={len(candidates)} prompt_chars={len(prompt_context)} elapsed_ms={elapsed_ms}"
        )

        return HotelAgentResult(
            candidates=candidates,
            prompt_context=prompt_context,
        )
