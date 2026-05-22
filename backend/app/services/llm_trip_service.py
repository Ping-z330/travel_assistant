import json

from app.models.trip import TripPlan, TripPlanRequest
from app.services.hotel_service import (
    HotelCandidate,
    format_hotel_candidates_for_prompt,
    search_trip_hotel_candidates,
)
from app.services.image_service import search_attraction_image
from app.services.llm_client import call_deepseek
from app.services.mock_trip_service import build_mock_trip_plan
from app.services.poi_service import (
    PoiCandidate,
    format_poi_candidates_for_prompt,
    search_trip_poi_candidates,
)
from app.services.weather_service import (
    WeatherSnapshot,
    format_weather_for_prompt,
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


def build_trip_prompt(
    request: TripPlanRequest,
    poi_candidates: list[PoiCandidate],
    weather_snapshot: WeatherSnapshot | None,
    hotel_candidates: list[HotelCandidate],
) -> str:
    poi_context = format_poi_candidates_for_prompt(poi_candidates)
    weather_context = (
        format_weather_for_prompt(weather_snapshot)
        if weather_snapshot
        else "暂无实时天气参考，可根据常识生成天气建议。"
    )
    hotel_context = format_hotel_candidates_for_prompt(hotel_candidates)

    return f"""
你是一名智能旅行规划助手。请根据用户需求生成一份实用、可执行的旅行计划。

用户需求：
- 目的地城市：{request.city}
- 出发日期：{request.start_date}
- 游玩天数：{request.days}
- 总预算：{request.budget} 元
- 出行人数：{request.people}
- 旅行偏好：{request.preference}

已检索到的真实景点候选：
{poi_context}

已查询到的天气信息：
{weather_context}

已查询到的酒店候选：
{hotel_context}

生成规则：
- 只返回 JSON，不要返回 Markdown，不要返回解释说明。
- `days` 数组必须刚好包含 {request.days} 天。
- 每一天建议包含 2 个景点。
- 同一个主景点不要跨天重复使用。
- 如果上面提供了真实景点候选，请优先从候选中选择景点，并尽量使用候选中的名称、地址和坐标。
- 如果上面提供了真实酒店候选，请优先从候选中选择酒店，并尽量参考候选中的酒店名称、地址、预算建议和坐标。
- 请根据天气信息安排室内外景点比例，遇到降雨时减少长时间户外活动。
- 景点名称、地址、餐饮建议、酒店名称、预算数字要尽量真实合理。
- 经纬度可以使用近似值，但优先使用候选中给出的真实坐标。
- 如果不知道可靠图片地址，`image_url` 返回空字符串。
- 所有面向用户展示的文本都必须使用中文。

请严格遵守下面的 JSON 结构：
{{
  "city": "{request.city}",
  "start_date": "{request.start_date}",
  "days": [
    {{
      "day": 1,
      "title": "当天路线标题",
      "attractions": [
        {{
          "name": "景点名称",
          "address": "景点地址",
          "location": {{
            "longitude": 116.397128,
            "latitude": 39.916527
          }},
          "visit_duration": 120,
          "ticket_price": 60,
          "description": "推荐理由",
          "image_url": "",
          "category": "景点类型"
        }}
      ],
      "meals": ["午餐建议", "晚餐建议"],
      "hotel": {{
        "name": "酒店名称",
        "address": "酒店地址",
        "price": 500,
        "description": "推荐理由",
        "location": {{
          "longitude": 116.397128,
          "latitude": 39.916527
        }}
      }},
      "weather": {{
        "date": "日期或第几天",
        "weather": "天气",
        "temperature": "温度范围",
        "suggestion": "天气建议"
      }}
    }}
  ],
  "budget": {{
    "total_attractions": 100,
    "total_hotels": 1000,
    "total_meals": 600,
    "total_transportation": 300,
    "total": 2000
  }},
  "overall_suggestion": "整体旅行建议"
}}
""".strip()


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
