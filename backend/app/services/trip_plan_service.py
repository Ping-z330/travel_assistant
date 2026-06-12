import os

from app.agents.planner_agent import PlannerAgent
from app.models.trip import TripPlan, TripPlanRequest
from app.services.mock_trip_service import build_mock_trip_plan


def generate_trip_plan(request: TripPlanRequest) -> TripPlan:
    mode = os.getenv("TRIP_PLAN_MODE", "mock")

    if mode == "mock":
        return build_mock_trip_plan(request)

    if mode == "llm":
        planner = PlannerAgent()
        return planner.run(request)

    raise ValueError(f"Unsupported trip plan mode: {mode}")
