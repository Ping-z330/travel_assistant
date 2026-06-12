import type { TripPlan } from '../types/trip'

export const DAY_COLORS = ['#176b5d', '#d97706', '#2563eb', '#dc2626', '#7c3aed']
export const HOTEL_COLOR = '#c27c2c'

export type RoutePoint = {
  day: number
  order: number
  name: string
  address: string
  longitude: number
  latitude: number
  color: string
}

export type DayRoute = {
  day: number
  color: string
  points: RoutePoint[]
}

export type HotelPoint = {
  startDay: number
  endDay: number
  name: string
  address: string
  price: number
  longitude: number
  latitude: number
  color: string
}

export const countAttractions = (tripPlan: TripPlan): number =>
  tripPlan.days.reduce((total, day) => total + day.attractions.length, 0)

export const buildDayRoutes = (tripPlan: TripPlan): DayRoute[] =>
  tripPlan.days.map((day, index) => {
    const color = DAY_COLORS[index % DAY_COLORS.length]

    return {
      day: day.day,
      color,
      points: day.attractions.map((attraction, pointIndex) => ({
        day: day.day,
        order: pointIndex + 1,
        name: attraction.name,
        address: attraction.address,
        longitude: attraction.location.longitude,
        latitude: attraction.location.latitude,
        color,
      })),
    }
  })

export const buildHotelPoints = (tripPlan: TripPlan): HotelPoint[] => {
  const merged: HotelPoint[] = []

  tripPlan.days.forEach((day) => {
    if (!day.hotel.location) {
      return
    }

    const current: HotelPoint = {
      startDay: day.day,
      endDay: day.day,
      name: day.hotel.name,
      address: day.hotel.address,
      price: day.hotel.price,
      longitude: day.hotel.location.longitude,
      latitude: day.hotel.location.latitude,
      color: HOTEL_COLOR,
    }

    const previous = merged[merged.length - 1]
    const isSameHotel =
      previous &&
      previous.name === current.name &&
      previous.address === current.address &&
      previous.longitude === current.longitude &&
      previous.latitude === current.latitude &&
      previous.endDay + 1 === current.startDay

    if (isSameHotel) {
      previous.endDay = current.endDay
      return
    }

    merged.push(current)
  })

  return merged
}
