from app.agents.requirement_agent import RequirementAgent
from app.models.trip import TripPlanRequest


def test_requirement_agent_extracts_structured_travel_constraints() -> None:
    request = TripPlanRequest(
        city="杭州",
        start_date="2026-06-20",
        days=2,
        budget=4000,
        people=3,
        preference="自然风光和本地小吃",
        requirements="带父母，少走路，不要爬山，酒店靠近地铁，想去西湖，吃本地特色菜",
    )

    result = RequirementAgent().run(request)

    assert result.pace == "慢节奏"
    assert result.mobility_level == "低步行"
    assert result.route_intensity == "低强度"
    assert result.meal_focus == "地方特色餐饮优先"
    assert result.hotel_area_preference == "地铁/公共交通便利区域"
    assert "父母同行" in result.companions
    assert "自然风光" in result.route_preferences
    assert "爬山或大量台阶" in result.avoid
    assert "西湖" in result.must_have
    assert "爬山或大量台阶" in result.must_avoid
    assert "- 步行承受度：低步行" in result.prompt_context
    assert "- 必须包含：西湖" in result.prompt_context


def test_requirement_agent_summary_includes_new_constraints() -> None:
    request = TripPlanRequest(
        city="成都",
        start_date="2026-06-20",
        days=3,
        budget=3500,
        people=2,
        preference="深度游",
        requirements="行程紧凑一点，市中心住宿，多逛博物馆",
    )

    result = RequirementAgent().run(request)
    summary = RequirementAgent.to_summary(result)

    assert summary.mobility_level == result.mobility_level
    assert summary.route_intensity == "高强度"
    assert summary.hotel_area_preference == "市中心区域"
    assert summary.meal_focus == result.meal_focus
    assert summary.must_have == result.must_have
    assert summary.must_avoid == result.must_avoid

