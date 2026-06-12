from app.agents.requirement_schemas import RequirementAgentResult
from app.agents.schemas import PlanningContext
from app.agents.trip_plan_generator import TripPlanGenerator
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


def test_trip_plan_generator_builds_prompt_and_normalizes_plan(monkeypatch) -> None:
    request = _request()
    requirement_result = _requirement_result()
    raw_plan = _trip_plan("原始计划")
    normalized_plan = _trip_plan("规范化计划")
    captured_prompt_context = {}
    captured_normalize_inputs = {}

    def fake_build_trip_prompt(context: PlanningContext):
        captured_prompt_context["value"] = context
        return "prompt text"

    def fake_call_deepseek(prompt: str) -> str:
        assert prompt == "prompt text"
        return '{"city": "杭州"}'

    def fake_normalize_trip_plan(trip_plan, request, hotel_candidates):
        captured_normalize_inputs["trip_plan"] = trip_plan
        captured_normalize_inputs["request"] = request
        captured_normalize_inputs["hotel_candidates"] = hotel_candidates
        return normalized_plan

    monkeypatch.setattr(
        "app.agents.trip_plan_generator.build_trip_prompt",
        fake_build_trip_prompt,
    )
    monkeypatch.setattr(
        "app.agents.trip_plan_generator.call_deepseek",
        fake_call_deepseek,
    )
    monkeypatch.setattr(
        "app.agents.trip_plan_generator.parse_llm_trip_plan",
        lambda content: raw_plan,
    )
    monkeypatch.setattr(
        "app.agents.trip_plan_generator.normalize_trip_plan",
        fake_normalize_trip_plan,
    )

    result = TripPlanGenerator().run(
        request=request,
        requirement_result=requirement_result,
        poi_candidates=[],
        weather_snapshot=None,
        hotel_candidates=[],
    )

    assert result is normalized_plan
    context = captured_prompt_context["value"]
    assert isinstance(context, PlanningContext)
    assert context.request is request
    assert context.requirement_result is requirement_result
    assert context.poi_candidates == []
    assert context.weather_snapshot is None
    assert context.hotel_candidates == []
    assert captured_normalize_inputs == {
        "trip_plan": raw_plan,
        "request": request,
        "hotel_candidates": [],
    }


def _request() -> TripPlanRequest:
    return TripPlanRequest(
        city="杭州",
        start_date="2026-06-20",
        days=1,
        budget=3000,
        people=2,
        preference="自然风光",
    )


def _requirement_result() -> RequirementAgentResult:
    return RequirementAgentResult(
        raw_text="",
        pace="正常",
        companions=[],
        food_preferences=[],
        hotel_preferences=[],
        avoid=[],
        route_preferences=["自然风光"],
        attractions_per_day=2,
        prompt_context="- 行程节奏：正常",
    )


def _trip_plan(title: str) -> TripPlan:
    return TripPlan(
        city="杭州",
        start_date="2026-06-20",
        days=[
            DayPlan(
                day=1,
                title=title,
                attractions=[
                    Attraction(
                        name="西湖",
                        address="杭州市西湖区",
                        location=Location(longitude=120.148, latitude=30.246),
                        visit_duration=120,
                        ticket_price=0,
                        description="湖区漫步。",
                        image_url="",
                        category="自然风光",
                    )
                ],
                meals=["早餐：酒店早餐", "午餐：杭帮菜", "晚餐：湖滨用餐"],
                hotel=Hotel(
                    name="西湖酒店",
                    address="杭州市西湖区",
                    price=500,
                    description="交通便利。",
                ),
                weather=WeatherInfo(
                    date="2026-06-20",
                    weather="多云",
                    temperature="20-28°C",
                    suggestion="适合步行。",
                ),
            )
        ],
        budget=Budget(
            total_attractions=0,
            total_hotels=500,
            total_meals=300,
            total_transportation=100,
            total=900,
        ),
        overall_suggestion="轻松游玩。",
    )
