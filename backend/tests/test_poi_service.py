import app.services.poi_service as poi_service
from app.agents.requirement_schemas import RequirementAgentResult
from app.models.trip import TripPlanRequest
from app.services.poi_service import build_search_keywords, search_trip_poi_candidates


def test_build_search_keywords_uses_requirements_and_avoids_hot_spots() -> None:
    requirement_result = _requirement_result(
        pace="慢节奏",
        companions=["老人同行"],
        food_preferences=["本地小吃"],
        avoid=["拥挤景点"],
        route_preferences=["博物馆"],
    )

    keywords = build_search_keywords("自然风光,公园", requirement_result)

    assert "自然风光 景点" in keywords
    assert "公园" in keywords
    assert "博物馆" in keywords
    assert "热门景点" not in keywords
    assert keywords[-1] == "旅游景点"


def test_search_trip_poi_candidates_filters_noise_invalid_categories_and_duplicates(
    monkeypatch,
) -> None:
    request = TripPlanRequest(
        city="杭州-poi-test",
        start_date="2026-06-20",
        days=1,
        budget=1000,
        people=2,
        preference="自然风光",
    )
    raw_pois = [
        {
            "name": "西湖",
            "address": "杭州市西湖区",
            "location": "120.1,30.2",
            "type": "风景名胜",
        },
        {
            "name": "西湖",
            "address": "杭州市西湖区",
            "location": "120.1,30.2",
            "type": "风景名胜",
        },
        {
            "name": "西湖-入口",
            "address": "杭州市西湖区",
            "location": "120.1,30.2",
            "type": "风景名胜",
        },
        {
            "name": "测试商店",
            "address": "杭州市",
            "location": "120.2,30.3",
            "type": "购物服务",
        },
        {
            "name": "浙江省博物馆",
            "address": "杭州市",
            "location": "120.3,30.4",
            "type": "博物馆",
        },
        {
            "name": "坐标错误点",
            "address": "杭州市",
            "location": "bad",
            "type": "博物馆",
        },
    ]
    monkeypatch.setattr(poi_service, "search_text_pois", lambda *args, **kwargs: raw_pois)

    candidates = search_trip_poi_candidates(request, total_limit=3)

    assert [candidate.name for candidate in candidates] == ["西湖", "浙江省博物馆"]


def _requirement_result(
    *,
    pace: str = "正常",
    companions: list[str] | None = None,
    food_preferences: list[str] | None = None,
    hotel_preferences: list[str] | None = None,
    avoid: list[str] | None = None,
    route_preferences: list[str] | None = None,
) -> RequirementAgentResult:
    return RequirementAgentResult(
        raw_text="",
        pace=pace,
        companions=companions or [],
        food_preferences=food_preferences or [],
        hotel_preferences=hotel_preferences or [],
        avoid=avoid or [],
        route_preferences=route_preferences or [],
        attractions_per_day=2,
        prompt_context="",
    )
