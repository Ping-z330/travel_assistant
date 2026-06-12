from dataclasses import dataclass

from app.agents.requirement_schemas import RequirementAgentResult
from app.models.trip import TripPlanRequest
from app.services.amap_client import geocode_city, search_around_pois
from app.services.amap_utils import parse_amap_location
from app.services.cache_utils import TTLCache


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

HOTEL_CACHE = TTLCache(ttl_seconds=1800)


# search_trip_hotel_candidates 函数负责根据预算生成关键词，并在目标城市中心点周边搜索酒店候选。
def search_trip_hotel_candidates(
    request: TripPlanRequest,
    *,
    requirement_result: RequirementAgentResult | None = None,
) -> list[HotelCandidate]:
    """根据预算生成关键词，并在目标城市中心点周边搜索酒店候选。"""
    cache_key = (
        f"hotel:{request.city.strip()}:{request.days}:"
        f"{request.budget}:{request.preference.strip()}:"
        f"{_requirement_cache_fragment(requirement_result)}"
    )
    cached = HOTEL_CACHE.get(cache_key)
    if cached is not None:
        print(f"[HOTEL_CACHE] hit city={request.city}")
        return cached

    keywords = build_hotel_keywords(request, requirement_result)
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
                HOTEL_CACHE.set(cache_key, candidates)
                return candidates

    HOTEL_CACHE.set(cache_key, candidates)
    return candidates


# build_hotel_keywords 函数根据用户的预算生成不同档位的酒店搜索关键词，帮助提高搜索结果的相关性和质量。
def build_hotel_keywords(
    request: TripPlanRequest,
    requirement_result: RequirementAgentResult | None = None,
) -> list[str]:
    """按人均日预算生成不同档位的酒店搜索关键词。"""
    requirement_keywords = _build_requirement_hotel_keywords(requirement_result)
    if _has_budget_friendly_requirement(requirement_result):
        return _dedupe_keywords(
            ["经济型酒店", "快捷酒店", "高评分酒店", *requirement_keywords]
        )

    budget_per_day = request.budget / max(request.days, 1)

    if budget_per_day <= 600:
        keywords = ["经济型酒店", "快捷酒店", "高评分酒店"]
    elif budget_per_day <= 1200:
        keywords = ["舒适型酒店", "精品酒店", "高评分酒店"]
    else:
        keywords = ["高档酒店", "豪华酒店", "高评分酒店"]

    keywords.extend(requirement_keywords)
    return _dedupe_keywords(keywords)


# format_hotel_candidates_for_prompt 函数把酒店候选整理成适合注入 LLM Prompt 的文本，
# 包括酒店名称、地址、坐标、类型和预算提示等信息，这些信息将被传递给 LLM 来生成旅行计划。
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
    coordinates = parse_amap_location(poi.get("location"))

    if not name or coordinates is None:
        return None

    if not any(keyword in name or keyword in category for keyword in HOTEL_CATEGORY_KEYWORDS):
        return None

    longitude, latitude = coordinates

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


def _build_requirement_hotel_keywords(
    requirement_result: RequirementAgentResult | None,
) -> list[str]:
    if requirement_result is None:
        return []

    preferences = set(requirement_result.hotel_preferences)
    companions = set(requirement_result.companions)

    keywords: list[str] = []
    if {"交通便利", "靠近地铁"} & preferences:
        keywords.extend(["地铁站 酒店", "交通便利酒店"])
    if {"舒适住宿", "安静住宿"} & preferences:
        keywords.extend(["舒适型酒店", "精品酒店"])
    if "市中心" in preferences:
        keywords.append("市中心酒店")
    if "亲子友好" in preferences or "亲子出行" in companions:
        keywords.append("亲子酒店")
    if "高档酒店" in preferences:
        keywords.append("高档酒店")
    if "预算友好" in preferences:
        keywords.extend(["经济型酒店", "快捷酒店"])

    return keywords


def _has_budget_friendly_requirement(
    requirement_result: RequirementAgentResult | None,
) -> bool:
    if requirement_result is None:
        return False

    preferences = set(requirement_result.hotel_preferences)
    return "预算友好" in preferences


def _dedupe_keywords(keywords: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for keyword in keywords:
        if keyword in seen:
            continue
        seen.add(keyword)
        deduped.append(keyword)
    return deduped


def _requirement_cache_fragment(requirement_result: RequirementAgentResult | None) -> str:
    if requirement_result is None:
        return "no_requirements"

    return "|".join(
        [
            requirement_result.pace,
            ",".join(requirement_result.companions),
            ",".join(requirement_result.hotel_preferences),
            ",".join(requirement_result.avoid),
        ]
    )
