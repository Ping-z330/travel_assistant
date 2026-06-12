from dataclasses import dataclass

from app.agents.requirement_schemas import RequirementAgentResult
from app.models.trip import TripPlanRequest
from app.services.hotel_service import HotelCandidate
from app.services.poi_service import PoiCandidate
from app.services.weather_service import WeatherSnapshot


@dataclass
class AgentRunResult:
    source: str
    ok: bool
    data: object | None
    error: str | None
    elapsed_ms: float


@dataclass
class PlanningContext:
    request: TripPlanRequest
    requirement_result: RequirementAgentResult
    poi_candidates: list[PoiCandidate]
    weather_snapshot: WeatherSnapshot | None
    hotel_candidates: list[HotelCandidate]


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
