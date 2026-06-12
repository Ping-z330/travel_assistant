import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.trip import TransportSummary, TripPlan, TripPlanRequest
from app.services.hotel_service import HotelCandidate
from app.services.image_service import search_attraction_image


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
    *,
    enrich_images: bool = True,
    transport_summary: TransportSummary | None = None,
) -> TripPlan:
    trip_plan.city = request.city
    trip_plan.start_date = request.start_date
    if transport_summary is not None:
        trip_plan.transport_summary = transport_summary

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

        if (
            not day.hotel.name.strip()
            or not day.hotel.address.strip()
            or day.hotel.price <= 0
            or day.hotel.location is None
        ):
            day.hotel = _build_fallback_hotel(request.city, hotel_candidates)

        _ensure_daily_meals(day.meals, request.city)

    if enrich_images:
        _enrich_missing_attraction_images(trip_plan, request.city)

    trip_plan.budget.total = (
        trip_plan.budget.total_attractions
        + trip_plan.budget.total_hotels
        + trip_plan.budget.total_meals
        + trip_plan.budget.total_transportation
    )

    return trip_plan


def _enrich_missing_attraction_images(trip_plan: TripPlan, city: str) -> None:
    attractions = [
        attraction
        for day in trip_plan.days
        for attraction in day.attractions
    ]

    missing_image_attractions = []
    seen_names: set[str] = set()
    for attraction in attractions:
        if attraction.image_url is None:
            attraction.image_url = ""

        normalized_name = _normalize_attraction_name(attraction.name)
        if attraction.image_url or normalized_name in seen_names:
            continue

        seen_names.add(normalized_name)
        missing_image_attractions.append(attraction)

    if not missing_image_attractions:
        return

    max_workers = min(4, len(missing_image_attractions))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_attraction = {
            executor.submit(_safe_search_attraction_image, attraction.name, city): attraction
            for attraction in missing_image_attractions
        }

        for future in as_completed(future_to_attraction):
            attraction = future_to_attraction[future]
            image_result = future.result()
            if image_result:
                attraction.image_url = image_result.image_url


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
        meals=["早餐：酒店或附近早餐店", "午餐：本地特色餐厅", "晚餐：城市商圈用餐"],
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


def _ensure_daily_meals(meals: list[str], city: str) -> None:
    if not any(meal.strip().startswith("早餐") for meal in meals):
        meals.insert(0, f"早餐：{city}本地早餐或酒店早餐")

    if not any(meal.strip().startswith("午餐") for meal in meals):
        meals.append("午餐：本地特色餐厅")

    if not any(meal.strip().startswith("晚餐") for meal in meals):
        meals.append("晚餐：城市商圈用餐")


def _safe_search_attraction_image(name: str, city: str):
    try:
        return search_attraction_image(name, city)
    except Exception as exc:
        print(f"[IMAGE_WARN] Failed to search image for {name}: {exc}")
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
