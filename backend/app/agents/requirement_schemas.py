from dataclasses import dataclass


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
