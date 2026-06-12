from app.agents.planner_agent import PlannerAgent
from app.agents.requirement_schemas import RequirementAgentResult
from app.agents.schemas import (
    AgentRunResult,
    AttractionAgentResult,
    HotelAgentResult,
    WeatherAgentResult,
)
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
from app.services.poi_service import PoiCandidate
from app.services.hotel_service import HotelCandidate
from app.services.weather_service import WeatherSnapshot


def test_run_agent_safely_wraps_successful_output() -> None:
    expected = object()

    result = PlannerAgent._run_agent_safely(
        "TEST_AGENT",
        lambda request: expected,
        _request(),
    )

    assert isinstance(result, AgentRunResult)
    assert result.ok is True
    assert result.data is expected
    assert result.error is None
    assert result.elapsed_ms >= 0
    assert result.source == "TEST_AGENT"


def test_run_agent_safely_wraps_failure_without_raising() -> None:
    def failing_agent(_request: TripPlanRequest) -> object:
        raise RuntimeError("boom")

    result = PlannerAgent._run_agent_safely("TEST_AGENT", failing_agent, _request())

    assert result.ok is False
    assert result.data is None
    assert result.error == "boom"
    assert result.elapsed_ms >= 0
    assert result.source == "TEST_AGENT"


def test_planner_continues_when_child_agent_fails(monkeypatch) -> None:
    planner = PlannerAgent()
    requirement_result = _requirement_result()
    attraction_result = AttractionAgentResult(
        candidates=[
            PoiCandidate(
                name="西湖",
                address="杭州市西湖区",
                longitude=120.148,
                latitude=30.246,
                category="景点",
            )
        ],
        prompt_context="- 西湖",
    )
    trip_plan = _trip_plan()
    captured_generation_inputs = {}

    monkeypatch.setattr(planner.requirement_agent, "run", lambda request: requirement_result)
    monkeypatch.setattr(
        planner.requirement_agent,
        "to_summary",
        lambda result: None,
    )
    monkeypatch.setattr(
        planner.attraction_agent,
        "run",
        lambda request, requirement: attraction_result,
    )
    monkeypatch.setattr(
        planner.weather_agent,
        "run",
        lambda request: (_ for _ in ()).throw(RuntimeError("weather down")),
    )
    monkeypatch.setattr(
        planner.hotel_agent,
        "run",
        lambda request, requirement: (_ for _ in ()).throw(RuntimeError("hotel down")),
    )

    def fake_generate_trip_plan(**kwargs):
        captured_generation_inputs.update(kwargs)
        return trip_plan

    monkeypatch.setattr(planner.trip_plan_generator, "run", fake_generate_trip_plan)

    result = planner.run(_request())

    assert result is trip_plan
    assert captured_generation_inputs["poi_candidates"] == attraction_result.candidates
    assert captured_generation_inputs["weather_snapshot"] is None
    assert captured_generation_inputs["hotel_candidates"] == []


def test_planner_passes_successful_agent_outputs_to_generator(monkeypatch) -> None:
    planner = PlannerAgent()
    request = _request()
    requirement_result = _requirement_result()
    attraction_result = AttractionAgentResult(
        candidates=[_poi_candidate()],
        prompt_context="- 西湖",
    )
    weather_result = WeatherAgentResult(
        snapshot=WeatherSnapshot(
            city="杭州",
            report_time="2026-06-20",
            summary="多云",
            temperature_hint="20-28°C",
            suggestion="适合步行。",
        ),
        prompt_context="- 多云",
    )
    hotel_result = HotelAgentResult(
        candidates=[_hotel_candidate()],
        prompt_context="- 西湖酒店",
    )
    trip_plan = _trip_plan()
    captured_generation_inputs = {}

    monkeypatch.setattr(planner.requirement_agent, "run", lambda request: requirement_result)
    monkeypatch.setattr(
        planner.attraction_agent,
        "run",
        lambda request, requirement: attraction_result,
    )
    monkeypatch.setattr(planner.weather_agent, "run", lambda request: weather_result)
    monkeypatch.setattr(
        planner.hotel_agent,
        "run",
        lambda request, requirement: hotel_result,
    )

    def fake_generate_trip_plan(**kwargs):
        captured_generation_inputs.update(kwargs)
        return trip_plan

    monkeypatch.setattr(planner.trip_plan_generator, "run", fake_generate_trip_plan)

    result = planner.run(request)

    assert result is trip_plan
    assert result.requirement_summary is not None
    assert result.requirement_summary.route_preferences == ["自然风光"]
    assert captured_generation_inputs == {
        "request": request,
        "requirement_result": requirement_result,
        "poi_candidates": attraction_result.candidates,
        "weather_snapshot": weather_result.snapshot,
        "hotel_candidates": hotel_result.candidates,
        "transport_summary": captured_generation_inputs["transport_summary"],
    }
    assert captured_generation_inputs["transport_summary"].recommended_mode == "市内交通"


def test_planner_falls_back_to_mock_plan_when_generation_fails(monkeypatch) -> None:
    planner = PlannerAgent()
    request = _request()
    requirement_result = _requirement_result()
    fallback_plan = _trip_plan()

    monkeypatch.setattr(planner.requirement_agent, "run", lambda request: requirement_result)
    monkeypatch.setattr(
        planner.attraction_agent,
        "run",
        lambda request, requirement: AttractionAgentResult(
            candidates=[],
            prompt_context="无景点候选",
        ),
    )
    monkeypatch.setattr(
        planner.weather_agent,
        "run",
        lambda request: WeatherAgentResult(snapshot=None, prompt_context="无天气"),
    )
    monkeypatch.setattr(
        planner.hotel_agent,
        "run",
        lambda request, requirement: HotelAgentResult(
            candidates=[],
            prompt_context="无酒店候选",
        ),
    )
    monkeypatch.setattr(
        planner.trip_plan_generator,
        "run",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("llm down")),
    )
    monkeypatch.setattr(
        "app.agents.planner_agent.build_mock_trip_plan",
        lambda request: fallback_plan,
    )

    result = planner.run(request)

    assert result is fallback_plan
    assert result.requirement_summary is not None
    assert result.requirement_summary.attractions_per_day == 2


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


def _poi_candidate() -> PoiCandidate:
    return PoiCandidate(
        name="西湖",
        address="杭州市西湖区",
        longitude=120.148,
        latitude=30.246,
        category="景点",
    )


def _hotel_candidate() -> HotelCandidate:
    return HotelCandidate(
        name="西湖酒店",
        address="杭州市西湖区",
        longitude=120.148,
        latitude=30.246,
        category="酒店",
        price_hint="舒适型酒店",
    )


def _trip_plan() -> TripPlan:
    return TripPlan(
        city="杭州",
        start_date="2026-06-20",
        days=[
            DayPlan(
                day=1,
                title="西湖漫游",
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
