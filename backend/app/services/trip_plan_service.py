import os

from app.models.trip import TripPlan, TripPlanRequest
from app.services.llm_trip_service import build_llm_trip_plan
from app.services.mock_trip_service import build_mock_trip_plan


def generate_trip_plan(request: TripPlanRequest) -> TripPlan:
    mode = os.getenv("TRIP_PLAN_MODE", "mock")

    if mode == "mock":
        return build_mock_trip_plan(request)

    if mode == "llm":
        return build_llm_trip_plan(request)

    raise ValueError(f"Unsupported trip plan mode: {mode}")