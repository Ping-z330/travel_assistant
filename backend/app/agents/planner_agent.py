from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from app.agents.attraction_agent import AttractionAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.requirement_agent import RequirementAgent
from app.agents.schemas import (
    AgentRunResult,
    AttractionAgentResult,
    HotelAgentResult,
    WeatherAgentResult,
)
from app.agents.trip_plan_generator import TripPlanGenerator
from app.agents.weather_agent import WeatherAgent
from app.models.trip import TripPlan, TripPlanRequest
from app.services.mock_trip_service import build_mock_trip_plan


class PlannerAgent:
    """负责统一调度多个子 Agent，并生成最终旅行计划。"""

    def __init__(self) -> None:
        self.requirement_agent = RequirementAgent()
        self.attraction_agent = AttractionAgent()
        self.weather_agent = WeatherAgent()
        self.hotel_agent = HotelAgent()
        self.trip_plan_generator = TripPlanGenerator()

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

            attraction_run = attraction_future.result()
            weather_run = weather_future.result()
            hotel_run = hotel_future.result()

        attraction_result = self._agent_data(attraction_run, AttractionAgentResult)
        weather_result = self._agent_data(weather_run, WeatherAgentResult)
        hotel_result = self._agent_data(hotel_run, HotelAgentResult)

        poi_candidates = attraction_result.candidates if attraction_result else []
        weather_snapshot = weather_result.snapshot if weather_result else None
        hotel_candidates = hotel_result.candidates if hotel_result else []

        try:
            generation_start = perf_counter()
            result = self.trip_plan_generator.run(
                request=request,
                requirement_result=requirement_result,
                poi_candidates=poi_candidates,
                weather_snapshot=weather_snapshot,
                hotel_candidates=hotel_candidates,
            )
            result.requirement_summary = self.requirement_agent.to_summary(requirement_result)
            generation_elapsed_ms = round((perf_counter() - generation_start) * 1000, 1)
            total_elapsed_ms = round((perf_counter() - total_start) * 1000, 1)

            print(
                f"[PLANNER_AGENT] success city={request.city} "
                f"poi_count={len(poi_candidates)} hotel_count={len(hotel_candidates)} "
                f"weather={'yes' if weather_snapshot else 'no'} "
                f"generation_elapsed_ms={generation_elapsed_ms} "
                f"total_elapsed_ms={total_elapsed_ms}"
            )

            return result
        except Exception as exc:
            total_elapsed_ms = round((perf_counter() - total_start) * 1000, 1)
            print(f"[PLANNER_AGENT_FALLBACK] {exc} total_elapsed_ms={total_elapsed_ms}")
            result = build_mock_trip_plan(request)
            result.requirement_summary = self.requirement_agent.to_summary(requirement_result)
            return result

    @staticmethod
    def _run_agent_safely(
        agent_name: str,
        agent_runner,
        request: TripPlanRequest,
        *args,
    ) -> AgentRunResult:
        start = perf_counter()
        try:
            data = agent_runner(request, *args)
            return AgentRunResult(
                source=agent_name,
                ok=True,
                data=data,
                error=None,
                elapsed_ms=round((perf_counter() - start) * 1000, 1),
            )
        except Exception as exc:
            print(f"[{agent_name}_WARN] {exc}")
            return AgentRunResult(
                source=agent_name,
                ok=False,
                data=None,
                error=str(exc),
                elapsed_ms=round((perf_counter() - start) * 1000, 1),
            )

    @staticmethod
    def _agent_data(
        result: AgentRunResult,
        expected_type: type,
    ):
        if not result.ok:
            return None

        if isinstance(result.data, expected_type):
            return result.data

        print(
            f"[{result.source}_WARN] unexpected result type="
            f"{type(result.data).__name__}"
        )
        return None
