import { describe, expect, it } from 'vitest'
import type { TripPlan } from '../types/trip'
import {
  deleteSavedTripPlan,
  findSavedTripPlan,
  listSavedTripPlans,
  saveTripPlanToHistory,
} from './tripHistory'

describe('tripHistory', () => {
  it('saves a trip plan as the newest history item', () => {
    const storage = createMemoryStorage()

    const saved = saveTripPlanToHistory(createTripPlan('杭州'), {}, storage)

    expect(saved.title).toBe('杭州 1 日旅行计划')
    expect(listSavedTripPlans(storage)).toHaveLength(1)
    expect(listSavedTripPlans(storage)[0].city).toBe('杭州')
  })

  it('creates separate records for separate manual saves', () => {
    const storage = createMemoryStorage()

    saveTripPlanToHistory(createTripPlan('杭州', { total: 1000 }), {}, storage)
    saveTripPlanToHistory(createTripPlan('杭州', { total: 2000 }), {}, storage)

    const savedTrips = listSavedTripPlans(storage)
    expect(savedTrips).toHaveLength(2)
    expect(savedTrips[0].budget_total).toBe(2000)
  })

  it('updates an existing history record by id', () => {
    const storage = createMemoryStorage()
    const saved = saveTripPlanToHistory(createTripPlan('杭州', { total: 1000 }), {}, storage)

    const updated = saveTripPlanToHistory(
      createTripPlan('杭州', { total: 2000 }),
      { existingId: saved.id },
      storage,
    )

    const savedTrips = listSavedTripPlans(storage)
    expect(savedTrips).toHaveLength(1)
    expect(updated.id).toBe(saved.id)
    expect(updated.saved_at).toBe(saved.saved_at)
    expect(savedTrips[0].budget_total).toBe(2000)
  })

  it('finds and deletes saved trip plans', () => {
    const storage = createMemoryStorage()
    const saved = saveTripPlanToHistory(createTripPlan('成都'), {}, storage)

    expect(findSavedTripPlan(saved.id, storage)?.city).toBe('成都')
    expect(deleteSavedTripPlan(saved.id, storage)).toEqual([])
    expect(findSavedTripPlan(saved.id, storage)).toBeNull()
  })
})

function createMemoryStorage(): Pick<Storage, 'getItem' | 'setItem' | 'removeItem'> {
  const values = new Map<string, string>()

  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => {
      values.set(key, value)
    },
    removeItem: (key: string) => {
      values.delete(key)
    },
  }
}

function createTripPlan(city: string, options: { total?: number } = {}): TripPlan {
  return {
    city,
    start_date: '2026-06-20',
    days: [
      {
        day: 1,
        title: '城市经典路线',
        attractions: [
          {
            name: '西湖',
            address: '杭州市西湖区',
            location: {
              longitude: 120.1,
              latitude: 30.2,
            },
            visit_duration: 120,
            ticket_price: 0,
            description: '湖区漫步。',
            image_url: '',
            category: '景点',
          },
        ],
        meals: ['早餐：酒店早餐', '午餐：本地餐厅', '晚餐：城市商圈'],
        hotel: {
          name: '舒适酒店',
          address: '城市核心区',
          price: 500,
          description: '交通便利。',
        },
        weather: {
          date: '2026-06-20',
          weather: '多云',
          temperature: '20-28°C',
          suggestion: '适合出行。',
        },
      },
    ],
    budget: {
      total_attractions: 0,
      total_hotels: 500,
      total_meals: 300,
      total_transportation: 200,
      total: options.total ?? 1000,
    },
    overall_suggestion: '轻松游玩。',
  }
}
