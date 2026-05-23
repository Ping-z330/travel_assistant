from time import perf_counter

from app.agents.schemas import AttractionAgentResult
from app.models.trip import TripPlanRequest
from app.services.poi_service import (
    format_poi_candidates_for_prompt,
    search_trip_poi_candidates,
)


class AttractionAgent:
    """负责景点候选搜索与景点上下文整理。"""

    def run(self, request: TripPlanRequest) -> AttractionAgentResult:
        start = perf_counter()
        print(f"[ATTRACTION_AGENT] start city={request.city} preference={request.preference}")

        candidates = search_trip_poi_candidates(request)
        prompt_context = format_poi_candidates_for_prompt(candidates)
        elapsed_ms = round((perf_counter() - start) * 1000, 1)

        print(
            f"[ATTRACTION_AGENT] success city={request.city} "
            f"count={len(candidates)} prompt_chars={len(prompt_context)} elapsed_ms={elapsed_ms}"
        )

        return AttractionAgentResult(
            candidates=candidates,
            prompt_context=prompt_context,
        )
