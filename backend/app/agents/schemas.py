from dataclasses import dataclass

from app.services.hotel_service import HotelCandidate
from app.services.poi_service import PoiCandidate
from app.services.weather_service import WeatherSnapshot


@dataclass
class RequirementAgentResult:
    raw_text: str
    pace: str
    companions: list[str]
    food_preferences: list[str]
    hotel_preferences: list[str]
    avoid: list[str]
    route_preferences: list[str]
    attractions_per_day: int
    prompt_context: str


# 景点Agent输出
@dataclass
class AttractionAgentResult:
    candidates: list[PoiCandidate]
    prompt_context: str


# 天气Agent输出
@dataclass
class WeatherAgentResult:
    snapshot: WeatherSnapshot | None
    prompt_context: str


# 酒店Agent输出
@dataclass
class HotelAgentResult:
    candidates: list[HotelCandidate]
    prompt_context: str
