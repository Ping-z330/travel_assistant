import json

from app.models.trip import (
    Attraction,
    Budget,
    DayPlan,
    Hotel,
    Location,
    TripPlan,
    TripPlanRequest,
    WeatherInfo,
)
from app.services.hotel_service import HotelCandidate
from app.services.trip_plan_postprocessor import (
    normalize_trip_plan,
    parse_llm_trip_plan,
)


def test_parse_llm_trip_plan_fills_null_hotels() -> None:
    content = json.dumps(
        {
            "city": "杭州",
            "start_date": "2026-06-20",
            "days": [
                {
                    "day": 1,
                    "title": "西湖漫游",
                    "attractions": [_attraction_dict("西湖")],
                    "meals": ["早餐：酒店早餐", "午餐：杭帮菜", "晚餐：湖滨用餐"],
                    "hotel": None,
                    "weather": _weather_dict(),
                }
            ],
            "budget": _budget_dict(total=999),
            "overall_suggestion": "轻松游玩。",
        },
        ensure_ascii=False,
    )

    trip_plan = parse_llm_trip_plan(content)

    assert trip_plan.days[0].hotel.name == "待补充酒店"
    assert trip_plan.days[0].hotel.location is None


def test_normalize_trip_plan_trims_extra_days() -> None:
    request = _request(days=2)
    trip_plan = _trip_plan(days=[_day(1), _day(2), _day(3)])

    result = normalize_trip_plan(
        trip_plan,
        request,
        hotel_candidates=[],
        enrich_images=False,
    )

    assert [day.day for day in result.days] == [1, 2]


def test_normalize_trip_plan_adds_missing_days() -> None:
    request = _request(days=3)
    trip_plan = _trip_plan(days=[_day(1)])

    result = normalize_trip_plan(
        trip_plan,
        request,
        hotel_candidates=[],
        enrich_images=False,
    )

    assert len(result.days) == 3
    assert [day.day for day in result.days] == [1, 2, 3]
    assert result.days[1].title == "杭州自由探索路线"


def test_normalize_trip_plan_dedupes_attractions_and_adds_fallbacks() -> None:
    request = _request(days=1)
    trip_plan = _trip_plan(
        days=[
            _day(
                1,
                attractions=[
                    _attraction("西湖"),
                    _attraction("西湖（断桥区域）"),
                    _attraction("西湖-苏堤"),
                ],
            )
        ]
    )

    result = normalize_trip_plan(
        trip_plan,
        request,
        hotel_candidates=[],
        enrich_images=False,
    )

    attraction_names = [attraction.name for attraction in result.days[0].attractions]
    assert attraction_names == ["西湖", "杭州第1天补充点位2"]


def test_normalize_trip_plan_uses_hotel_candidate_when_hotel_is_incomplete() -> None:
    request = _request(days=1)
    trip_plan = _trip_plan(
        days=[
            _day(
                1,
                hotel=Hotel(
                    name="",
                    address="",
                    price=0,
                    description="",
                    location=None,
                ),
            )
        ]
    )
    hotel_candidates = [
        HotelCandidate(
            name="西湖边舒适酒店",
            address="杭州市西湖区",
            longitude=120.12,
            latitude=30.25,
            category="酒店",
            price_hint="建议选择舒适型或精品酒店",
        )
    ]

    result = normalize_trip_plan(
        trip_plan,
        request,
        hotel_candidates=hotel_candidates,
        enrich_images=False,
    )

    hotel = result.days[0].hotel
    assert hotel.name == "西湖边舒适酒店"
    assert hotel.address == "杭州市西湖区"
    assert hotel.location == Location(longitude=120.12, latitude=30.25)


def test_normalize_trip_plan_adds_missing_meals() -> None:
    request = _request(days=1)
    trip_plan = _trip_plan(days=[_day(1, meals=["午餐：杭帮菜"])])

    result = normalize_trip_plan(
        trip_plan,
        request,
        hotel_candidates=[],
        enrich_images=False,
    )

    meals = result.days[0].meals
    assert any(meal.startswith("早餐") for meal in meals)
    assert any(meal.startswith("午餐") for meal in meals)
    assert any(meal.startswith("晚餐") for meal in meals)


def test_normalize_trip_plan_recalculates_budget_total() -> None:
    request = _request(days=1)
    trip_plan = _trip_plan(
        days=[_day(1)],
        budget=Budget(
            total_attractions=100,
            total_hotels=800,
            total_meals=300,
            total_transportation=200,
            total=1,
        ),
    )

    result = normalize_trip_plan(
        trip_plan,
        request,
        hotel_candidates=[],
        enrich_images=False,
    )

    assert result.budget.total == 1400


def _request(days: int) -> TripPlanRequest:
    return TripPlanRequest(
        city="杭州",
        start_date="2026-06-20",
        days=days,
        budget=3000,
        people=2,
        preference="自然风光",
    )


def _trip_plan(
    *,
    days: list[DayPlan],
    budget: Budget | None = None,
) -> TripPlan:
    return TripPlan(
        city="上海",
        start_date="2026-01-01",
        days=days,
        budget=budget or Budget(
            total_attractions=100,
            total_hotels=800,
            total_meals=300,
            total_transportation=200,
            total=999,
        ),
        overall_suggestion="测试计划。",
    )


def _day(
    day: int,
    *,
    attractions: list[Attraction] | None = None,
    hotel: Hotel | None = None,
    meals: list[str] | None = None,
) -> DayPlan:
    return DayPlan(
        day=day,
        title=f"第 {day} 天",
        attractions=attractions or [_attraction(f"景点{day}A"), _attraction(f"景点{day}B")],
        meals=meals or ["早餐：酒店早餐", "午餐：本地餐厅", "晚餐：城市商圈"],
        hotel=hotel
        or Hotel(
            name="测试酒店",
            address="测试地址",
            price=500,
            description="测试住宿。",
            location=Location(longitude=120.1, latitude=30.2),
        ),
        weather=WeatherInfo(
            date=f"第 {day} 天",
            weather="多云",
            temperature="18-26°C",
            suggestion="适合出行。",
        ),
    )


def _attraction(name: str) -> Attraction:
    return Attraction(
        name=name,
        address="测试地址",
        location=Location(longitude=120.1, latitude=30.2),
        visit_duration=120,
        ticket_price=0,
        description="测试景点。",
        image_url="",
        category="景点",
    )


def _attraction_dict(name: str) -> dict:
    return {
        "name": name,
        "address": "测试地址",
        "location": {"longitude": 120.1, "latitude": 30.2},
        "visit_duration": 120,
        "ticket_price": 0,
        "description": "测试景点。",
        "image_url": "",
        "category": "景点",
    }


def _weather_dict() -> dict:
    return {
        "date": "第 1 天",
        "weather": "多云",
        "temperature": "18-26°C",
        "suggestion": "适合出行。",
    }


def _budget_dict(total: int) -> dict:
    return {
        "total_attractions": 100,
        "total_hotels": 800,
        "total_meals": 300,
        "total_transportation": 200,
        "total": total,
    }
