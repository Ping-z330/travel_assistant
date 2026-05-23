import re
from dataclasses import dataclass

from app.models.trip import TripPlanRequest
from app.services.cache_utils import TTLCache
from app.services.amap_client import search_text_pois


NOISE_NAME_KEYWORDS = {
    "入口",
    "出口",
    "停车场",
    "服务区",
    "售票处",
    "游客中心",
    "检票口",
    "观光车",
    "缆车",
    "索道",
    "码头",
    "东门",
    "西门",
    "南门",
    "北门",
}

ALLOWED_CATEGORY_KEYWORDS = {
    "风景名胜",
    "博物馆",
    "公园",
    "国家级景点",
    "世界遗产",
    "旅游景点",
    "教堂",
    "古镇",
    "寺庙",
    "遗址",
}

POI_CACHE = TTLCache(ttl_seconds=1800)


@dataclass
class PoiCandidate:
    name: str
    address: str
    longitude: float
    latitude: float
    category: str


# search_trip_poi_candidates 函数负责根据用户的旅行需求搜索景点候选列表，
# 并进行去重和过滤，最终返回一个符合条件的景点候选列表。
def search_trip_poi_candidates(
    request: TripPlanRequest,
    *,
    per_keyword_limit: int = 5,
    total_limit: int = 8,
) -> list[PoiCandidate]:
    cache_key = (
        f"poi:{request.city.strip()}:{request.days}:"
        f"{request.preference.strip()}:{per_keyword_limit}:{total_limit}"
    )
    cached = POI_CACHE.get(cache_key)
    if cached is not None:
        print(f"[POI_CACHE] hit city={request.city}")
        return cached

    candidates: list[PoiCandidate] = []
    seen_keys: set[tuple[str, str]] = set()
    seen_names: set[str] = set()

    for keyword in build_search_keywords(request.preference):
        raw_pois = search_text_pois(
            keyword,
            request.city,
            limit=per_keyword_limit,
        )

        for raw_poi in raw_pois:
            candidate = _convert_poi(raw_poi)
            if candidate is None:
                continue

            if _is_noise_poi(candidate.name):
                continue

            if not _is_valid_category(candidate.category):
                continue

            normalized_name = _normalize_poi_name(candidate.name)
            if normalized_name in seen_names:
                continue

            dedupe_key = (normalized_name, candidate.address)
            if dedupe_key in seen_keys:
                continue

            seen_names.add(normalized_name)
            seen_keys.add(dedupe_key)
            candidates.append(candidate)

            if len(candidates) >= total_limit:
                POI_CACHE.set(cache_key, candidates)
                return candidates

    POI_CACHE.set(cache_key, candidates)
    return candidates

# format_poi_candidates_for_prompt 函数负责将景点候选列表格式化为一个适合提示词使用的字符串，
def format_poi_candidates_for_prompt(candidates: list[PoiCandidate]) -> str:
    if not candidates:
        return "暂无真实景点候选，可根据城市常识生成合理行程。"

    lines = []
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            (
                f"{index}. {candidate.name}｜地址：{candidate.address}｜"
                f"坐标：{candidate.longitude},{candidate.latitude}｜"
                f"类型：{candidate.category}"
            )
        )

    return "\n".join(lines)


def build_search_keywords(preference: str) -> list[str]:
    parts = [
        item.strip()
        for item in re.split(r"[，,、/；;|]+", preference)
        if item.strip()
    ]

    keywords: list[str] = []
    for part in parts[:3]:
        if "景点" in part or "公园" in part or "博物馆" in part:
            keywords.append(part)
        else:
            keywords.append(f"{part} 景点")

    keywords.append("热门景点")
    keywords.append("旅游景点")

    deduped_keywords: list[str] = []
    seen: set[str] = set()
    for keyword in keywords:
        if keyword in seen:
            continue
        seen.add(keyword)
        deduped_keywords.append(keyword)

    return deduped_keywords


def _normalize_poi_name(name: str) -> str:
    normalized = name.strip()
    normalized = normalized.split("-")[0]
    normalized = normalized.split("（")[0]
    normalized = normalized.split("(")[0]
    return normalized.strip()


def _is_noise_poi(name: str) -> bool:
    if "-" in name or "（" in name or "(" in name:
        return True

    return any(keyword in name for keyword in NOISE_NAME_KEYWORDS)


def _is_valid_category(category: str) -> bool:
    return any(keyword in category for keyword in ALLOWED_CATEGORY_KEYWORDS)


def _convert_poi(raw_poi: dict) -> PoiCandidate | None:
    name = str(raw_poi.get("name", "")).strip()
    location = str(raw_poi.get("location", "")).strip()
    if not name or not location or "," not in location:
        return None

    longitude_text, latitude_text = location.split(",", 1)

    try:
        longitude = float(longitude_text)
        latitude = float(latitude_text)
    except ValueError:
        return None

    address = str(raw_poi.get("address", "")).strip() or "地址待补充"
    category = str(raw_poi.get("type", "")).strip() or "景点"

    return PoiCandidate(
        name=name,
        address=address,
        longitude=longitude,
        latitude=latitude,
        category=category,
    )
