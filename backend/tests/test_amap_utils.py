from app.services.amap_utils import parse_amap_location


def test_parse_amap_location_returns_coordinates() -> None:
    assert parse_amap_location("120.123,30.456") == (120.123, 30.456)


def test_parse_amap_location_rejects_invalid_values() -> None:
    assert parse_amap_location("") is None
    assert parse_amap_location("120.123") is None
    assert parse_amap_location("lng,lat") is None
