import json

from app.agents.prompt_builder import build_trip_prompt
from app.models.trip import TripPlan, TripPlanRequest
from app.services.hotel_service import (
    HotelCandidate,
    search_trip_hotel_candidates,
)
from app.services.image_service import search_attraction_image
from app.services.llm_client import call_deepseek
from app.services.mock_trip_service import build_mock_trip_plan
from app.services.poi_service import (
    PoiCandidate,
    search_trip_poi_candidates,
)
from app.services.weather_service import (
    WeatherSnapshot,
    get_trip_weather_snapshot,
)


def build_llm_trip_plan(request: TripPlanRequest) -> TripPlan:
    poi_candidates: list[PoiCandidate] = []
    weather_snapshot: WeatherSnapshot | None = None
    hotel_candidates: list[HotelCandidate] = []

    try:
        poi_candidates = search_trip_poi_candidates(request)
    except Exception as exc:
        print(f"[AMAP_POI_WARN] Failed to search POIs: {exc}")

    try:
        weather_snapshot = get_trip_weather_snapshot(request.city)
    except Exception as exc:
        print(f"[AMAP_WEATHER_WARN] Failed to query weather: {exc}")

    try:
        hotel_candidates = search_trip_hotel_candidates(request)
    except Exception as exc:
        print(f"[AMAP_HOTEL_WARN] Failed to search hotels: {exc}")

    prompt = build_trip_prompt(
        request=request,
        poi_candidates=poi_candidates,
        weather_snapshot=weather_snapshot,
        hotel_candidates=hotel_candidates,
    )

    try:
        content = call_deepseek(prompt)
        trip_plan = parse_llm_trip_plan(content)
        return normalize_trip_plan(trip_plan, request, hotel_candidates)
    except Exception as exc:
        print(f"[LLM_FALLBACK] DeepSeek generation failed: {exc}")
        return build_mock_trip_plan(request)
def parse_llm_trip_plan(content: str) -> TripPlan:
    data = json.loads(content)
    _fill_missing_hotels(data)
    return TripPlan(**data)


def _fill_missing_hotels(data: dict) -> None:
    raw_days = data.get("days")
    if not isinstance(raw_days, list):
        return

    for index, day in enumerate(raw_days, start=1):
        if not isinstance(day, dict):
            continue

        if day.get("hotel") is None:
            day["hotel"] = {
                "name": "待补充酒店",
                "address": "待补充地址",
                "price": 0,
                "description": f"第 {index} 天酒店信息暂缺，后续将使用兜底逻辑补全。",
                "location": None,
            }


def normalize_trip_plan(
    trip_plan: TripPlan,
    request: TripPlanRequest,
    hotel_candidates: list[HotelCandidate],
) -> TripPlan:
    trip_plan.city = request.city
    trip_plan.start_date = request.start_date

    if len(trip_plan.days) > request.days:
        trip_plan.days = trip_plan.days[: request.days]

    while len(trip_plan.days) < request.days:
        day_index = len(trip_plan.days) + 1
        trip_plan.days.append(_build_fallback_day(day_index, request.city))

    seen_attraction_names: set[str] = set()

    for index, day in enumerate(trip_plan.days, start=1):
        day.day = index
        day.attractions = _dedupe_day_attractions(day.attractions, seen_attraction_names)

        while len(day.attractions) < 2:
            day.attractions.append(
                _build_fallback_attraction(
                    request.city,
                    suffix=f"第{index}天补充点位{len(day.attractions) + 1}",
                )
            )

        for attraction in day.attractions:
            if attraction.image_url is None:
                attraction.image_url = ""
            if not attraction.image_url:
                image_result = _safe_search_attraction_image(attraction.name, request.city)
                if image_result:
                    attraction.image_url = image_result.image_url

        if (
            not day.hotel.name.strip()
            or not day.hotel.address.strip()
            or day.hotel.price <= 0
            or day.hotel.location is None
        ):
            day.hotel = _build_fallback_hotel(request.city, hotel_candidates)

    trip_plan.budget.total = (
        trip_plan.budget.total_attractions
        + trip_plan.budget.total_hotels
        + trip_plan.budget.total_meals
        + trip_plan.budget.total_transportation
    )

    return trip_plan


def _dedupe_day_attractions(attractions: list, seen_attraction_names: set[str]) -> list:
    unique_attractions = []

    for attraction in attractions:
        normalized_name = _normalize_attraction_name(attraction.name)
        if normalized_name in seen_attraction_names:
            continue

        seen_attraction_names.add(normalized_name)
        unique_attractions.append(attraction)

    return unique_attractions


def _normalize_attraction_name(name: str) -> str:
    normalized = name.strip()
    normalized = normalized.split("-")[0]
    normalized = normalized.split("（")[0]
    normalized = normalized.split("(")[0]
    return normalized.strip()


def _build_fallback_day(day: int, city: str):
    from app.models.trip import DayPlan, Hotel, Location, WeatherInfo

    return DayPlan(
        day=day,
        title=f"{city}自由探索路线",
        attractions=[
            _build_fallback_attraction(city, suffix=f"第{day}天补充点位1"),
            _build_fallback_attraction(city, suffix=f"第{day}天补充点位2"),
        ],
        meals=["午餐：本地特色餐厅", "晚餐：城市商圈用餐"],
        hotel=Hotel(
            name=f"{city}舒适酒店",
            address=f"{city}交通便利区域",
            price=450,
            description="作为兜底住宿推荐，方便继续后续行程。",
            location=Location(longitude=116.397128, latitude=39.916527),
        ),
        weather=WeatherInfo(
            date=f"第 {day} 天",
            weather="多云",
            temperature="18-26°C",
            suggestion="根据当天实际天气灵活调整安排。",
        ),
    )


def _build_fallback_attraction(city: str, suffix: str = "城市漫游"):
    from app.models.trip import Attraction, Location

    return Attraction(
        name=f"{city}{suffix}",
        address=f"{city}核心城区",
        location=Location(longitude=116.397128, latitude=39.916527),
        visit_duration=120,
        ticket_price=0,
        description="当模型返回内容不足或出现重复景点时，补充一个自由探索点位以保证结构完整。",
        image_url="",
        category="自由探索",
    )


def _safe_search_attraction_image(name: str, city: str):
    try:
        return search_attraction_image(name, city)
    except Exception as exc:
        print(f"[UNSPLASH_WARN] Failed to search image for {name}: {exc}")
        return None


def _build_fallback_hotel(city: str, hotel_candidates: list[HotelCandidate]):
    from app.models.trip import Hotel, Location

    if hotel_candidates:
        hotel = hotel_candidates[0]
        return Hotel(
            name=hotel.name,
            address=hotel.address or f"{city}核心区域",
            price=450,
            description=hotel.price_hint,
            location=Location(longitude=hotel.longitude, latitude=hotel.latitude),
        )

    return Hotel(
        name=f"{city}舒适酒店",
        address=f"{city}交通便利区域",
        price=450,
        description="作为兜底住宿推荐，方便继续后续行程。",
        location=Location(longitude=116.397128, latitude=39.916527),
    )
