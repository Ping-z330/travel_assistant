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

        # candidates得到搜索到的酒店候选列表，
        # prompt_context是将候选列表格式化为一个适合提示词使用的字符串，这些信息将被传递给 LLM 来生成旅行计划。
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
