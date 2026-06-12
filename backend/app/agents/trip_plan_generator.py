from app.agents.prompt_builder import build_trip_prompt
from app.agents.requirement_schemas import RequirementAgentResult
from app.agents.schemas import PlanningContext
from app.models.trip import TransportSummary, TripPlan, TripPlanRequest
from app.services.hotel_service import HotelCandidate
from app.services.llm_client import call_deepseek
from app.services.poi_service import PoiCandidate
from app.services.trip_plan_postprocessor import (
    normalize_trip_plan,
    parse_llm_trip_plan,
)
from app.services.weather_service import WeatherSnapshot


class TripPlanGenerator:
    """负责把规划上下文交给 LLM，并规范化最终 TripPlan。"""

    def run(
        self,
        *,
        request: TripPlanRequest,
        requirement_result: RequirementAgentResult,
        poi_candidates: list[PoiCandidate],
        weather_snapshot: WeatherSnapshot | None,
        hotel_candidates: list[HotelCandidate],
        transport_summary: TransportSummary | None,
    ) -> TripPlan:
        context = PlanningContext(
            request=request,
            requirement_result=requirement_result,
            poi_candidates=poi_candidates,
            weather_snapshot=weather_snapshot,
            hotel_candidates=hotel_candidates,
            transport_summary=transport_summary,
        )
        prompt = build_trip_prompt(context)
        content = call_deepseek(prompt)
        trip_plan = parse_llm_trip_plan(content)
        return normalize_trip_plan(
            trip_plan,
            request,
            hotel_candidates,
            transport_summary=transport_summary,
        )
