import { describe, expect, it } from 'vitest'
import type { TripPlan } from '../types/trip'
import {
  buildDayRoutes,
  buildHotelPoints,
  countAttractions,
  DAY_COLORS,
  HOTEL_COLOR,
} from './travelMapData'

describe('travelMapData', () => {
  it('counts attractions across all days', () => {
    const tripPlan = createTripPlan([
      createDay(1, { attractions: ['西湖', '灵隐寺'] }),
      createDay(2, { attractions: ['浙江省博物馆'] }),
    ])

    expect(countAttractions(tripPlan)).toBe(3)
  })

  it('builds day routes with point order and rotating colors', () => {
    const tripPlan = createTripPlan([
      createDay(1, { attractions: ['西湖', '灵隐寺'] }),
      createDay(2, { attractions: ['浙江省博物馆'] }),
    ])

    const routes = buildDayRoutes(tripPlan)

    expect(routes).toHaveLength(2)
    expect(routes[0].color).toBe(DAY_COLORS[0])
    expect(routes[1].color).toBe(DAY_COLORS[1])
    expect(routes[0].points.map((point) => point.order)).toEqual([1, 2])
    expect(routes[0].points[0]).toMatchObject({
      day: 1,
      name: '西湖',
      longitude: 120.1,
      latitude: 30.2,
      color: DAY_COLORS[0],
    })
  })

  it('merges consecutive stays at the same hotel', () => {
    const hotel = createHotel('西湖舒适酒店', 120.1, 30.2)
    const tripPlan = createTripPlan([
      createDay(1, { hotel }),
      createDay(2, { hotel }),
      createDay(3, { hotel: createHotel('河坊街酒店', 120.2, 30.3) }),
    ])

    const hotels = buildHotelPoints(tripPlan)

    expect(hotels).toEqual([
      {
        startDay: 1,
        endDay: 2,
        name: '西湖舒适酒店',
        address: '西湖舒适酒店地址',
        price: 500,
        longitude: 120.1,
        latitude: 30.2,
        color: HOTEL_COLOR,
      },
      {
        startDay: 3,
        endDay: 3,
        name: '河坊街酒店',
        address: '河坊街酒店地址',
        price: 500,
        longitude: 120.2,
        latitude: 30.3,
        color: HOTEL_COLOR,
      },
    ])
  })

  it('does not merge nonconsecutive stays at the same hotel', () => {
    const hotel = createHotel('西湖舒适酒店', 120.1, 30.2)
    const tripPlan = createTripPlan([
      createDay(1, { hotel }),
      createDay(2, { hotel: createHotel('河坊街酒店', 120.2, 30.3) }),
      createDay(3, { hotel }),
    ])

    const hotels = buildHotelPoints(tripPlan)

    expect(hotels.map((point) => `${point.startDay}-${point.endDay}:${point.name}`)).toEqual([
      '1-1:西湖舒适酒店',
      '2-2:河坊街酒店',
      '3-3:西湖舒适酒店',
    ])
  })

  it('skips hotel points without locations', () => {
    const tripPlan = createTripPlan([
      createDay(1, { hotel: createHotel('待定酒店', undefined, undefined) }),
      createDay(2, { hotel: createHotel('西湖舒适酒店', 120.1, 30.2) }),
    ])

    const hotels = buildHotelPoints(tripPlan)

    expect(hotels).toHaveLength(1)
    expect(hotels[0].startDay).toBe(2)
    expect(hotels[0].name).toBe('西湖舒适酒店')
  })
})

function createTripPlan(days: TripPlan['days']): TripPlan {
  return {
    city: '杭州',
    start_date: '2026-06-20',
    days,
    budget: {
      total_attractions: 100,
      total_hotels: 1000,
      total_meals: 500,
      total_transportation: 200,
      total: 1800,
    },
    overall_suggestion: '测试行程',
  }
}

function createDay(
  day: number,
  options: {
    attractions?: string[]
    hotel?: TripPlan['days'][number]['hotel']
  } = {},
): TripPlan['days'][number] {
  return {
    day,
    title: `第 ${day} 天`,
    attractions: (options.attractions ?? [`景点${day}`]).map((name, index) => ({
      name,
      address: `${name}地址`,
      location: {
        longitude: 120.1 + index,
        latitude: 30.2 + index,
      },
      visit_duration: 120,
      ticket_price: 0,
      description: `${name}介绍`,
      image_url: '',
      category: '景点',
    })),
    meals: ['早餐：酒店早餐', '午餐：本地餐厅', '晚餐：城市商圈'],
    hotel: options.hotel ?? createHotel(`酒店${day}`, 120.5 + day, 30.5 + day),
    weather: {
      date: `第 ${day} 天`,
      weather: '多云',
      temperature: '18-26°C',
      suggestion: '适合出行。',
    },
  }
}

function createHotel(name: string, longitude?: number, latitude?: number): TripPlan['days'][number]['hotel'] {
  return {
    name,
    address: `${name}地址`,
    price: 500,
    description: `${name}说明`,
    location:
      longitude === undefined || latitude === undefined
        ? undefined
        : {
            longitude,
            latitude,
          },
  }
}
