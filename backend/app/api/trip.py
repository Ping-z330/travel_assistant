from fastapi import APIRouter, Query

from app.models.trip import TripPlan, TripPlanRequest
from app.services.poi_service import build_search_keywords, search_trip_poi_candidates
from app.services.trip_plan_service import generate_trip_plan
from app.services.weather_service import get_trip_weather_snapshot

router = APIRouter(prefix="/api/trip", tags=["trip"])


@router.post("/plan", response_model=TripPlan)
def create_trip_plan(request: TripPlanRequest) -> TripPlan:
    return generate_trip_plan(request)


@router.get("/debug/poi")
def debug_poi_search(
    city: str = Query(..., description="目的地城市"),
    preference: str = Query(..., description="旅行偏好"),
):
    request = TripPlanRequest(
        city=city,
        start_date="2026-01-01",
        days=1,
        budget=1000,
        people=1,
        preference=preference,
    )

    candidates = search_trip_poi_candidates(request)
    keywords = build_search_keywords(preference)

    return {
        "city": city,
        "preference": preference,
        "keywords": keywords,
        "count": len(candidates),
        "pois": [
            {
                "name": poi.name,
                "address": poi.address,
                "longitude": poi.longitude,
                "latitude": poi.latitude,
                "category": poi.category,
            }
            for poi in candidates
        ],
    }


@router.get("/debug/weather")
def debug_weather(
    city: str = Query(..., description="目的地城市"),
):
    weather = get_trip_weather_snapshot(city)

    return {
        "city": weather.city,
        "report_time": weather.report_time,
        "summary": weather.summary,
        "temperature_hint": weather.temperature_hint,
        "suggestion": weather.suggestion,
    }
