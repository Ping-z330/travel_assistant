from typing import List, Optional

from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):
    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="出发日期")
    days: int = Field(..., ge=1, le=15, description="游玩天数")
    budget: int = Field(..., ge=0, description="总预算")
    people: int = Field(..., ge=1, le=20, description="出行人数")
    preference: str = Field(..., description="旅行偏好")
    requirements: Optional[str] = Field(None, description="补充需求")


class Location(BaseModel):
    longitude: float
    latitude: float


class Attraction(BaseModel):
    name: str
    address: str
    location: Location
    visit_duration: int
    ticket_price: int
    description: str
    image_url: Optional[str] = None
    category: str = "景点"


class Hotel(BaseModel):
    name: str
    address: str
    price: int
    description: str
    location: Optional[Location] = None


class WeatherInfo(BaseModel):
    date: str
    weather: str
    temperature: str
    suggestion: str


class DayPlan(BaseModel):
    day: int
    title: str
    attractions: List[Attraction]
    meals: List[str]
    hotel: Hotel
    weather: WeatherInfo


class Budget(BaseModel):
    total_attractions: int
    total_hotels: int
    total_meals: int
    total_transportation: int
    total: int


class RequirementSummary(BaseModel):
    raw_text: str = ""
    pace: str = "正常"
    companions: List[str] = []
    food_preferences: List[str] = []
    hotel_preferences: List[str] = []
    avoid: List[str] = []
    route_preferences: List[str] = []
    attractions_per_day: int = 2


class TripPlan(BaseModel):
    city: str
    start_date: str
    days: List[DayPlan]
    budget: Budget
    overall_suggestion: str
    requirement_summary: Optional[RequirementSummary] = None
