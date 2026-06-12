from dataclasses import dataclass, field


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
    mobility_level: str = "普通"
    route_intensity: str = "均衡"
    meal_focus: str = "常规餐饮"
    hotel_area_preference: str = "交通便利区域"
    must_have: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)
