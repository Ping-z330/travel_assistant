export interface TripPlanRequest {
  departure_city?: string
  city: string
  start_date: string
  days: number
  budget: number
  people: number
  preference: string
  requirements?: string
}

export interface Location {
  longitude: number
  latitude: number
}

export interface Attraction {
  name: string
  address: string
  location: Location
  visit_duration: number
  ticket_price: number
  description: string
  image_url?: string
  category?: string
}

export interface Hotel {
  name: string
  address: string
  price: number
  description: string
  location?: Location
}

export interface WeatherInfo {
  date: string
  weather: string
  temperature: string
  suggestion: string
}

export interface DayPlan {
  day: number
  title: string
  attractions: Attraction[]
  meals: string[]
  hotel: Hotel
  weather: WeatherInfo
}

export interface Budget {
  total_attractions: number
  total_hotels: number
  total_meals: number
  total_transportation: number
  total: number
}

export interface RequirementSummary {
  raw_text: string
  pace: string
  companions: string[]
  food_preferences: string[]
  hotel_preferences: string[]
  avoid: string[]
  route_preferences: string[]
  attractions_per_day: number
  mobility_level: string
  route_intensity: string
  meal_focus: string
  hotel_area_preference: string
  must_have: string[]
  must_avoid: string[]
}

export interface TripPlan {
  city: string
  start_date: string
  days: DayPlan[]
  budget: Budget
  overall_suggestion: string
  requirement_summary?: RequirementSummary
  transport_summary?: TransportSummary
}

export interface TransportOption {
  mode: string
  title: string
  description: string
  estimated_duration: string
  estimated_cost: string
  booking_advice: string
}

export interface TransportSummary {
  departure_city?: string | null
  destination_city: string
  recommended_mode: string
  summary: string
  options: TransportOption[]
}

export interface SavedTripPlan {
  id: string
  title: string
  city: string
  start_date: string
  days_count: number
  budget_total: number
  saved_at: string
  updated_at: string
  trip_plan: TripPlan
}
