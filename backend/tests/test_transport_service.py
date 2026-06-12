from app.models.trip import TripPlanRequest
from app.services.transport_service import build_transport_summary


def test_build_transport_summary_recommends_high_speed_rail_for_short_city_pair() -> None:
    summary = build_transport_summary(
        TripPlanRequest(
            departure_city="上海",
            city="杭州",
            start_date="2026-06-20",
            days=3,
            budget=3000,
            people=2,
            preference="自然风光",
        )
    )

    assert summary is not None
    assert summary.recommended_mode == "高铁"
    assert summary.departure_city == "上海"
    assert summary.destination_city == "杭州"
    assert summary.options[0].mode == "高铁"


def test_build_transport_summary_recommends_flight_for_long_city_pair() -> None:
    summary = build_transport_summary(
        TripPlanRequest(
            departure_city="北京",
            city="三亚",
            start_date="2026-06-20",
            days=5,
            budget=8000,
            people=2,
            preference="亲子轻松",
        )
    )

    assert summary is not None
    assert summary.recommended_mode == "飞机"
    assert any(option.mode == "飞机" for option in summary.options)


def test_build_transport_summary_returns_local_advice_without_departure_city() -> None:
    summary = build_transport_summary(
        TripPlanRequest(
            city="成都",
            start_date="2026-06-20",
            days=2,
            budget=3000,
            people=2,
            preference="美食探索",
        )
    )

    assert summary is not None
    assert summary.recommended_mode == "市内交通"
    assert summary.departure_city is None
    assert summary.options[0].mode == "地铁/打车"
