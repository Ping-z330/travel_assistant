def parse_amap_location(location: object) -> tuple[float, float] | None:
    location_text = str(location or "").strip()
    if not location_text or "," not in location_text:
        return None

    longitude_text, latitude_text = location_text.split(",", 1)

    try:
        return float(longitude_text), float(latitude_text)
    except ValueError:
        return None
