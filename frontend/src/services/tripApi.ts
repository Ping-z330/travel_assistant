// 放置与行程规划相关的 API 调用逻辑
import axios from 'axios'
import { getAuthHeaders } from './auth'
import type { TripPlan, TripPlanRequest } from '../types/trip'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8003'

export const generateTripPlan = async (
  request: TripPlanRequest,
): Promise<TripPlan> => {
  const response = await axios.post<TripPlan>(
    `${API_BASE_URL}/api/trip/plan`,
    request,
    {
      headers: getAuthHeaders(),
    },
  )

  return response.data
}
