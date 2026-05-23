from fastapi import APIRouter, Query

from app.models.trip import TripPlanRequest
from app.services.hotel_service import search_trip_hotel_candidates
from app.services.image_service import search_attraction_image
from app.services.poi_service import build_search_keywords, search_trip_poi_candidates
from app.services.weather_service import get_trip_weather_snapshot

router = APIRouter(prefix="/api/trip", tags=["trip-debug"])


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


@router.get("/debug/image")
def debug_image_search(
    name: str = Query(..., description="景点名称"),
    city: str = Query(..., description="城市名称"),
):
    try:
        result = search_attraction_image(name, city)
    except Exception as exc:
        return {
            "name": name,
            "city": city,
            "found": False,
            "error": str(exc),
            "image": None,
        }

    if result is None:
        return {
            "name": name,
            "city": city,
            "found": False,
            "error": None,
            "image": None,
        }

    return {
        "name": name,
        "city": city,
        "found": True,
        "error": None,
        "image": {
            "image_url": result.image_url,
            "thumb_url": result.thumb_url,
            "alt_description": result.alt_description,
            "photographer": result.photographer,
            "photographer_url": result.photographer_url,
            "download_location": result.download_location,
        },
    }


@router.get("/debug/hotel")
def debug_hotel_search(
    city: str = Query(..., description="目的地城市"),
    budget: int = Query(..., description="总预算"),
    days: int = Query(3, description="旅行天数"),
    preference: str = Query("舒适,交通便利", description="旅行偏好"),
):
    request = TripPlanRequest(
        city=city,
        start_date="2026-06-01",
        days=days,
        budget=budget,
        people=2,
        preference=preference,
    )

    candidates = search_trip_hotel_candidates(request)

    return {
        "city": city,
        "budget": budget,
        "days": days,
        "preference": preference,
        "count": len(candidates),
        "hotels": [
            {
                "name": hotel.name,
                "address": hotel.address,
                "longitude": hotel.longitude,
                "latitude": hotel.latitude,
                "category": hotel.category,
                "price_hint": hotel.price_hint,
            }
            for hotel in candidates
        ],
    }
