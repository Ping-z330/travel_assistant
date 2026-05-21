// 放置与行程规划相关的 TypeScript 类型定义
export interface TripPlanRequest {
  city: string
  start_date: string
  days: number
  budget: number
  people: number
  preference: string
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

export interface TripPlan {
  city: string
  start_date: string
  days: DayPlan[]
  budget: Budget
  overall_suggestion: string
}