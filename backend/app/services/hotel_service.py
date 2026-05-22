from dataclasses import dataclass

from app.models.trip import TripPlanRequest
from app.services.amap_client import geocode_city, search_around_pois


@dataclass
class HotelCandidate:
    name: str
    address: str
    longitude: float
    latitude: float
    category: str
    price_hint: str


HOTEL_CATEGORY_KEYWORDS = [
    "酒店",
    "宾馆",
    "旅馆",
    "民宿",
]


def search_trip_hotel_candidates(request: TripPlanRequest) -> list[HotelCandidate]:
    """根据预算生成关键词，并在目标城市中心点周边搜索酒店候选。"""
    keywords = build_hotel_keywords(request)
    center = resolve_city_center(request.city)
    candidates: list[HotelCandidate] = []
    seen_names: set[str] = set()

    for keyword in keywords:
        pois = search_around_pois(
            location=center,
            keywords=keyword,
            radius=8000,
            limit=8,
        )

        for poi in pois:
            candidate = _convert_hotel_poi(poi, request)
            if candidate is None:
                continue

            if candidate.name in seen_names:
                continue

            seen_names.add(candidate.name)
            candidates.append(candidate)

            if len(candidates) >= 6:
                return candidates

    return candidates


def build_hotel_keywords(request: TripPlanRequest) -> list[str]:
    """按人均日预算生成不同档位的酒店搜索关键词。"""
    budget_per_day = request.budget / max(request.days, 1)

    if budget_per_day <= 600:
        return ["经济型酒店", "快捷酒店", "高评分酒店"]
    if budget_per_day <= 1200:
        return ["舒适型酒店", "精品酒店", "高评分酒店"]

    return ["高档酒店", "豪华酒店", "高评分酒店"]


def format_hotel_candidates_for_prompt(candidates: list[HotelCandidate]) -> str:
    """把酒店候选整理成适合注入 LLM Prompt 的文本。"""
    if not candidates:
        return "暂无可用酒店候选，请根据预算推荐合适住宿。"

    lines = []
    for index, hotel in enumerate(candidates, start=1):
        lines.append(
            f"{index}. {hotel.name} | 地址：{hotel.address or '地址待补充'} | "
            f"坐标：{hotel.longitude}, {hotel.latitude} | "
            f"类型：{hotel.category or '酒店'} | 建议：{hotel.price_hint}"
        )

    return "\n".join(lines)


def resolve_city_center(city: str) -> str:
    """动态查询城市中心坐标，供高德周边搜索使用。"""
    result = geocode_city(city)
    location = result.get("location", "").strip()
    if not location:
        raise ValueError(f"Unable to resolve city center: {city}")
    return location


def _convert_hotel_poi(
    poi: dict,
    request: TripPlanRequest,
) -> HotelCandidate | None:
    """将高德 POI 数据转换为酒店候选对象，并过滤非酒店结果。"""
    name = (poi.get("name") or "").strip()
    address = (poi.get("address") or "").strip()
    category = (poi.get("type") or "").strip()
    location = (poi.get("location") or "").strip()

    if not name or not location:
        return None

    if not any(keyword in name or keyword in category for keyword in HOTEL_CATEGORY_KEYWORDS):
        return None

    try:
        longitude_str, latitude_str = location.split(",")
        longitude = float(longitude_str)
        latitude = float(latitude_str)
    except (TypeError, ValueError):
        return None

    return HotelCandidate(
        name=name,
        address=address,
        longitude=longitude,
        latitude=latitude,
        category=category,
        price_hint=_build_price_hint(request),
    )


def _build_price_hint(request: TripPlanRequest) -> str:
    """生成给前端和 LLM 展示的预算提示文案。"""
    budget_per_day = request.budget / max(request.days, 1)

    if budget_per_day <= 600:
        return "预算友好，建议选择经济型或快捷酒店"
    if budget_per_day <= 1200:
        return "建议选择舒适型或精品酒店"

    return "预算充足，可优先考虑高档或豪华酒店"
