import app.services.hotel_service as hotel_service
from app.agents.requirement_schemas import RequirementAgentResult
from app.models.trip import TripPlanRequest
from app.services.hotel_service import build_hotel_keywords, search_trip_hotel_candidates


def test_build_hotel_keywords_uses_budget_and_requirement_preferences() -> None:
    request = _request(budget=2400, days=2)
    requirement_result = _requirement_result(
        hotel_preferences=["靠近地铁", "亲子友好"],
        companions=["亲子出行"],
    )

    keywords = build_hotel_keywords(request, requirement_result)

    assert keywords[:3] == ["舒适型酒店", "精品酒店", "高评分酒店"]
    assert "地铁站 酒店" in keywords
    assert "亲子酒店" in keywords


def test_search_trip_hotel_candidates_filters_non_hotels_and_bad_locations(
    monkeypatch,
) -> None:
    request = _request(city="杭州-hotel-test", budget=2400, days=2)
    raw_pois = [
        {
            "name": "西湖舒适酒店",
            "address": "杭州市西湖区",
            "location": "120.1,30.2",
            "type": "酒店",
        },
        {
            "name": "西湖舒适酒店",
            "address": "杭州市西湖区",
            "location": "120.1,30.2",
            "type": "酒店",
        },
        {
            "name": "西湖商场",
            "address": "杭州市",
            "location": "120.2,30.3",
            "type": "购物服务",
        },
        {
            "name": "坐标错误酒店",
            "address": "杭州市",
            "location": "bad",
            "type": "酒店",
        },
    ]
    monkeypatch.setattr(hotel_service, "resolve_city_center", lambda city: "120.0,30.0")
    monkeypatch.setattr(hotel_service, "search_around_pois", lambda *args, **kwargs: raw_pois)

    candidates = search_trip_hotel_candidates(request)

    assert [candidate.name for candidate in candidates] == ["西湖舒适酒店"]
    assert candidates[0].price_hint == "建议选择舒适型或精品酒店"


def _request(city: str = "杭州", budget: int = 1000, days: int = 1) -> TripPlanRequest:
    return TripPlanRequest(
        city=city,
        start_date="2026-06-20",
        days=days,
        budget=budget,
        people=2,
        preference="自然风光",
    )


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
