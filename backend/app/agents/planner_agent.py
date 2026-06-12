from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from app.agents.attraction_agent import AttractionAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.prompt_builder import build_trip_prompt
from app.agents.requirement_agent import RequirementAgent
from app.agents.weather_agent import WeatherAgent
from app.models.trip import TripPlan, TripPlanRequest
from app.services.llm_client import call_deepseek
from app.services.trip_plan_postprocessor import (
    normalize_trip_plan,
    parse_llm_trip_plan,
)
from app.services.mock_trip_service import build_mock_trip_plan


class PlannerAgent:
    """负责统一调度多个子 Agent，并生成最终旅行计划。"""

    def __init__(self) -> None:
        self.requirement_agent = RequirementAgent()
        self.attraction_agent = AttractionAgent()
        self.weather_agent = WeatherAgent()
        self.hotel_agent = HotelAgent()

    def run(self, request: TripPlanRequest) -> TripPlan:
        total_start = perf_counter()
        print(
            f"[PLANNER_AGENT] start city={request.city} days={request.days} "
            f"budget={request.budget} people={request.people}"
        )
        requirement_result = self.requirement_agent.run(request)

        with ThreadPoolExecutor(max_workers=3) as executor:
            attraction_future = executor.submit(
                self._run_agent_safely,
                "ATTRACTION_AGENT",
                self.attraction_agent.run,
                request,
                requirement_result,
            )
            weather_future = executor.submit(
                self._run_agent_safely,
                "WEATHER_AGENT",
                self.weather_agent.run,
                request,
            )
            hotel_future = executor.submit(
                self._run_agent_safely,
                "HOTEL_AGENT",
                self.hotel_agent.run,
                request,
                requirement_result,
            )

            attraction_result = attraction_future.result()
            weather_result = weather_future.result()
            hotel_result = hotel_future.result()

        poi_candidates = attraction_result.candidates if attraction_result else []
        weather_snapshot = weather_result.snapshot if weather_result else None
        hotel_candidates = hotel_result.candidates if hotel_result else []

        prompt = build_trip_prompt(
            request=request,
            requirement_result=requirement_result,
            poi_candidates=poi_candidates,
            weather_snapshot=weather_snapshot,
            hotel_candidates=hotel_candidates,
        )

        try:
            llm_start = perf_counter()
            content = call_deepseek(prompt)
            trip_plan = parse_llm_trip_plan(content)
            result = normalize_trip_plan(trip_plan, request, hotel_candidates)
            result.requirement_summary = self.requirement_agent.to_summary(requirement_result)
            llm_elapsed_ms = round((perf_counter() - llm_start) * 1000, 1)
            total_elapsed_ms = round((perf_counter() - total_start) * 1000, 1)

            print(
                f"[PLANNER_AGENT] success city={request.city} "
                f"poi_count={len(poi_candidates)} hotel_count={len(hotel_candidates)} "
                f"weather={'yes' if weather_snapshot else 'no'} "
                f"llm_elapsed_ms={llm_elapsed_ms} total_elapsed_ms={total_elapsed_ms}"
            )

            return result
        except Exception as exc:
            total_elapsed_ms = round((perf_counter() - total_start) * 1000, 1)
            print(f"[PLANNER_AGENT_FALLBACK] {exc} total_elapsed_ms={total_elapsed_ms}")
            result = build_mock_trip_plan(request)
            result.requirement_summary = self.requirement_agent.to_summary(requirement_result)
            return result

    @staticmethod
    def _run_agent_safely(agent_name: str, agent_runner, request: TripPlanRequest, *args):
        try:
            return agent_runner(request, *args)
        except Exception as exc:
            print(f"[{agent_name}_WARN] {exc}")
            return None
