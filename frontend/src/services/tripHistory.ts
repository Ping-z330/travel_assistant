import type { SavedTripPlan, TripPlan } from '../types/trip'

const HISTORY_STORAGE_KEY = 'savedTripPlans'

type TripHistoryStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>

export const listSavedTripPlans = (
  storage: TripHistoryStorage = localStorage,
): SavedTripPlan[] => {
  const raw = storage.getItem(HISTORY_STORAGE_KEY)
  if (!raw) {
    return []
  }

  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) {
      return []
    }

    return parsed as SavedTripPlan[]
  } catch {
    storage.removeItem(HISTORY_STORAGE_KEY)
    return []
  }
}

export const saveTripPlanToHistory = (
  tripPlan: TripPlan,
  options: {
    existingId?: string | null
  } = {},
  storage: TripHistoryStorage = localStorage,
): SavedTripPlan => {
  const savedTrips = listSavedTripPlans(storage)
  const now = new Date().toISOString()
  const existingTrip = options.existingId
    ? savedTrips.find((savedTrip) => savedTrip.id === options.existingId)
    : null
  const id = existingTrip?.id ?? createSavedTripId(tripPlan)
  const record: SavedTripPlan = {
    id,
    title: `${tripPlan.city} ${tripPlan.days.length} 日旅行计划`,
    city: tripPlan.city,
    start_date: tripPlan.start_date,
    days_count: tripPlan.days.length,
    budget_total: tripPlan.budget.total,
    saved_at: existingTrip?.saved_at ?? now,
    updated_at: now,
    trip_plan: tripPlan,
  }

  const nextTrips = [
    record,
    ...savedTrips.filter((savedTrip) => savedTrip.id !== id),
  ]

  storage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(nextTrips))
  return record
}

export const deleteSavedTripPlan = (
  id: string,
  storage: TripHistoryStorage = localStorage,
): SavedTripPlan[] => {
  const nextTrips = listSavedTripPlans(storage).filter((savedTrip) => savedTrip.id !== id)
  storage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(nextTrips))
  return nextTrips
}

export const findSavedTripPlan = (
  id: string,
  storage: TripHistoryStorage = localStorage,
): SavedTripPlan | null =>
  listSavedTripPlans(storage).find((savedTrip) => savedTrip.id === id) ?? null

const createSavedTripId = (tripPlan: TripPlan): string =>
  `${tripPlan.city.trim()}-${tripPlan.start_date}-${tripPlan.days.length}-${createUniqueId()}`

const createUniqueId = (): string => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }

  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}
