from app.models.trip import TripPlanRequest
from app.services.hotel_service import (
    HotelCandidate,
    format_hotel_candidates_for_prompt,
)
from app.services.poi_service import (
    PoiCandidate,
    format_poi_candidates_for_prompt,
)
from app.services.weather_service import (
    WeatherSnapshot,
    format_weather_for_prompt,
)


def build_trip_prompt(
    request: TripPlanRequest,
    poi_candidates: list[PoiCandidate],
    weather_snapshot: WeatherSnapshot | None,
    hotel_candidates: list[HotelCandidate],
) -> str:
    poi_context = format_poi_candidates_for_prompt(poi_candidates)
    weather_context = (
        format_weather_for_prompt(weather_snapshot)
        if weather_snapshot
        else "暂无实时天气参考，可根据常识生成天气建议。"
    )
    hotel_context = format_hotel_candidates_for_prompt(hotel_candidates)

    return f"""
你是一名智能旅行规划助手。请根据用户需求生成一份实用、可执行的旅行计划。

用户需求：
- 目的地城市：{request.city}
- 出发日期：{request.start_date}
- 游玩天数：{request.days}
- 总预算：{request.budget} 元
- 出行人数：{request.people}
- 旅行偏好：{request.preference}

已检索到的真实景点候选：
{poi_context}

已查询到的天气信息：
{weather_context}

已查询到的酒店候选：
{hotel_context}

生成规则：
- 只返回 JSON，不要返回 Markdown，不要返回解释说明。
- `days` 数组必须刚好包含 {request.days} 天。
- 每一天建议包含 2 个景点。
- 同一个主景点不要跨天重复使用。
- 如果上面提供了真实景点候选，请优先从候选中选择景点，并尽量使用候选中的名称、地址和坐标。
- 如果上面提供了真实酒店候选，请优先从候选中选择酒店，并尽量参考候选中的酒店名称、地址、预算建议和坐标。
- 每一天都必须包含完整的 `hotel` 对象，`hotel` 绝对不能为 null。
- 即使多天入住同一家酒店，也必须在每一天重复输出完整的 hotel 字段。
- 请根据天气信息安排室内外景点比例，遇到降雨时减少长时间户外活动。
- 景点名称、地址、餐饮建议、酒店名称、预算数字要尽量真实合理。
- 经度纬度可以使用近似值，但优先使用候选中给出的真实坐标。
- 如果不知道可靠图片地址，`image_url` 返回空字符串。
- 所有面向用户展示的文本都必须使用中文。

请严格遵守下面的 JSON 结构：
{{
  "city": "{request.city}",
  "start_date": "{request.start_date}",
  "days": [
    {{
      "day": 1,
      "title": "当天路线标题",
      "attractions": [
        {{
          "name": "景点名称",
          "address": "景点地址",
          "location": {{
            "longitude": 116.397128,
            "latitude": 39.916527
          }},
          "visit_duration": 120,
          "ticket_price": 60,
          "description": "推荐理由",
          "image_url": "",
          "category": "景点类型"
        }}
      ],
      "meals": ["午餐建议", "晚餐建议"],
      "hotel": {{
        "name": "酒店名称",
        "address": "酒店地址",
        "price": 500,
        "description": "推荐理由",
        "location": {{
          "longitude": 116.397128,
          "latitude": 39.916527
        }}
      }},
      "weather": {{
        "date": "日期或第几天",
        "weather": "天气",
        "temperature": "温度范围",
        "suggestion": "天气建议"
      }}
    }}
  ],
  "budget": {{
    "total_attractions": 100,
    "total_hotels": 1000,
    "total_meals": 600,
    "total_transportation": 300,
    "total": 2000
  }},
  "overall_suggestion": "整体旅行建议"
}}
""".strip()
