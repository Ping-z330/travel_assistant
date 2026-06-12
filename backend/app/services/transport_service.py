from app.models.trip import TransportOption, TransportSummary, TripPlanRequest


LONG_DISTANCE_PAIRS = {
    frozenset(("北京", "三亚")),
    frozenset(("上海", "三亚")),
    frozenset(("广州", "北京")),
    frozenset(("深圳", "北京")),
    frozenset(("成都", "上海")),
    frozenset(("成都", "北京")),
}

SHORT_RAIL_PAIRS = {
    frozenset(("上海", "杭州")),
    frozenset(("上海", "苏州")),
    frozenset(("南京", "杭州")),
    frozenset(("广州", "深圳")),
    frozenset(("北京", "天津")),
    frozenset(("成都", "重庆")),
}


def build_transport_summary(request: TripPlanRequest) -> TransportSummary:
    departure_city = _clean_city(request.departure_city)
    destination_city = _clean_city(request.city) or request.city

    if not departure_city or departure_city == destination_city:
        return TransportSummary(
            departure_city=departure_city,
            destination_city=destination_city,
            recommended_mode="市内交通",
            summary="未提供明确出发城市，建议重点关注目的地市内交通衔接。",
            options=[
                TransportOption(
                    mode="地铁/打车",
                    title="目的地市内交通",
                    description="优先选择地铁、网约车或步行组合，按当天景点分布灵活调整。",
                    estimated_duration="按当日路线调整",
                    estimated_cost="约 50-150 元/人/天",
                    booking_advice="不需要提前订票，出行当天根据天气和体力选择即可。",
                )
            ],
        )

    pair = frozenset((departure_city, destination_city))

    if pair in SHORT_RAIL_PAIRS:
        return _rail_summary(departure_city, destination_city)

    if pair in LONG_DISTANCE_PAIRS:
        return _flight_summary(departure_city, destination_city)

    return _balanced_summary(departure_city, destination_city)


def format_transport_for_prompt(summary: TransportSummary | None) -> str:
    if summary is None:
        return "暂无交通建议，可根据目的地常规交通方式安排。"

    option_lines = [
        (
            f"- {option.mode}：{option.title}；"
            f"耗时 {option.estimated_duration}；费用 {option.estimated_cost}；"
            f"{option.booking_advice}"
        )
        for option in summary.options
    ]

    return "\n".join(
        [
            f"- 出发城市：{summary.departure_city or '未提供'}",
            f"- 目的地城市：{summary.destination_city}",
            f"- 推荐方式：{summary.recommended_mode}",
            f"- 建议摘要：{summary.summary}",
            *option_lines,
        ]
    )


def _rail_summary(departure_city: str, destination_city: str) -> TransportSummary:
    return TransportSummary(
        departure_city=departure_city,
        destination_city=destination_city,
        recommended_mode="高铁",
        summary=f"{departure_city} 到 {destination_city} 属于短途城市间出行，优先选择高铁，时间稳定且进出站成本低。",
        options=[
            TransportOption(
                mode="高铁",
                title="短途高铁优先",
                description="适合上午出发、抵达后直接衔接酒店或首日景点。",
                estimated_duration="约 1-2 小时",
                estimated_cost="约 50-200 元/人",
                booking_advice="建议提前 1-3 天购买车票，优先选择到达市中心车站的班次。",
            ),
            TransportOption(
                mode="自驾/打车",
                title="多人同行备选",
                description="如果携带较多行李或同行人较多，可考虑自驾或城际包车。",
                estimated_duration="约 2-3 小时",
                estimated_cost="按车辆和路况浮动",
                booking_advice="高峰期需预留进出城拥堵时间。",
            ),
        ],
    )


def _flight_summary(departure_city: str, destination_city: str) -> TransportSummary:
    return TransportSummary(
        departure_city=departure_city,
        destination_city=destination_city,
        recommended_mode="飞机",
        summary=f"{departure_city} 到 {destination_city} 距离较远，优先选择飞机，减少路上时间。",
        options=[
            TransportOption(
                mode="飞机",
                title="长距离飞行优先",
                description="适合把更多时间留给目的地游玩，抵达后再安排轻量行程。",
                estimated_duration="约 2-4 小时飞行",
                estimated_cost="约 500-1500 元/人",
                booking_advice="建议提前比价，优先选择白天抵达的航班。",
            ),
            TransportOption(
                mode="高铁",
                title="时间充裕备选",
                description="如果预算敏感且能接受更长路程，可对比高铁或动车。",
                estimated_duration="通常 6 小时以上",
                estimated_cost="按线路浮动",
                booking_advice="长途高铁建议选择直达或少换乘班次。",
            ),
        ],
    )


def _balanced_summary(departure_city: str, destination_city: str) -> TransportSummary:
    return TransportSummary(
        departure_city=departure_city,
        destination_city=destination_city,
        recommended_mode="高铁/飞机对比",
        summary=f"{departure_city} 到 {destination_city} 建议同时比较高铁和飞机，按预算、出发时间和同行人状态选择。",
        options=[
            TransportOption(
                mode="高铁",
                title="稳定出行方案",
                description="适合中短途或希望减少机场安检、候机时间的行程。",
                estimated_duration="约 3-6 小时",
                estimated_cost="约 200-600 元/人",
                booking_advice="优先选择到达市中心车站的班次。",
            ),
            TransportOption(
                mode="飞机",
                title="省时方案",
                description="适合跨省较远距离，尤其是游玩天数较短时。",
                estimated_duration="约 2-3 小时飞行",
                estimated_cost="约 500-1200 元/人",
                booking_advice="需额外预留往返机场和安检时间。",
            ),
        ],
    )


def _clean_city(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None
