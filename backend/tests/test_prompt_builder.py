from app.agents.prompt_builder import build_trip_prompt
from app.agents.requirement_schemas import RequirementAgentResult
from app.agents.schemas import PlanningContext
from app.models.trip import TripPlanRequest


def test_build_trip_prompt_reads_from_planning_context() -> None:
    context = PlanningContext(
        request=TripPlanRequest(
            city="杭州",
            start_date="2026-06-20",
            days=2,
            budget=3000,
            people=2,
            preference="自然风光",
            requirements="带父母，轻松一点",
        ),
        requirement_result=RequirementAgentResult(
            raw_text="带父母，轻松一点",
            pace="慢节奏",
            companions=["父母同行"],
            food_preferences=[],
            hotel_preferences=[],
            avoid=["高强度行程"],
            route_preferences=["自然风光"],
            attractions_per_day=2,
            prompt_context="- 行程节奏：慢节奏",
        ),
        poi_candidates=[],
        weather_snapshot=None,
        hotel_candidates=[],
    )

    prompt = build_trip_prompt(context)

    assert "- 目的地城市：杭州" in prompt
    assert "- 游玩天数：2" in prompt
    assert "- 补充需求：带父母，轻松一点" in prompt
    assert "- 行程节奏：慢节奏" in prompt
    assert "暂无实时天气参考" in prompt
    assert "每一天建议包含 2 个景点" in prompt
