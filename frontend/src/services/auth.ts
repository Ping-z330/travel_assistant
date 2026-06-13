import axios from 'axios'
import { computed, reactive } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8003'
const ACCESS_TOKEN_KEY = 'travelAssistantAccessToken'
const AUTH_USER_KEY = 'travelAssistantAuthUser'

export interface AuthUser {
  username: string
  display_name: string
}

interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  user: AuthUser
}

interface AuthState {
  accessToken: string | null
  user: AuthUser | null
  ready: boolean
}

const authState = reactive<AuthState>({
  accessToken: null,
  user: null,
  ready: false,
})

let bootstrapPromise: Promise<void> | null = null

const readStorage = () => {
  if (typeof window === 'undefined') {
    return
  }

  authState.accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  const rawUser = localStorage.getItem(AUTH_USER_KEY)

  if (!rawUser) {
    authState.user = null
    return
  }

  try {
    authState.user = JSON.parse(rawUser) as AuthUser
  } catch {
    authState.user = null
    localStorage.removeItem(AUTH_USER_KEY)
  }
}

const persistAuth = (response: LoginResponse) => {
  authState.accessToken = response.access_token
  authState.user = response.user
  localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token)
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.user))
}

const clearPersistedAuth = () => {
  authState.accessToken = null
  authState.user = null
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(AUTH_USER_KEY)
}

const refreshCurrentUser = async () => {
  if (!authState.accessToken) {
    clearPersistedAuth()
    authState.ready = true
    return
  }

  try {
    const response = await axios.get<AuthUser>(`${API_BASE_URL}/api/auth/me`, {
      headers: getAuthHeaders(),
    })
    authState.user = response.data
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.data))
  } catch {
    clearPersistedAuth()
  } finally {
    authState.ready = true
  }
}

export const ensureAuthReady = async () => {
  if (authState.ready) {
    return
  }

  if (!bootstrapPromise) {
    readStorage()
    bootstrapPromise = refreshCurrentUser().finally(() => {
      bootstrapPromise = null
    })
  }

  await bootstrapPromise
}

export const login = async (credentials: {
  username: string
  password: string
}): Promise<AuthUser> => {
  const response = await axios.post<LoginResponse>(`${API_BASE_URL}/api/auth/login`, credentials)
  persistAuth(response.data)
  authState.ready = true
  return response.data.user
}

export const logout = () => {
  clearPersistedAuth()
  authState.ready = true
}

export const isAuthenticated = () => Boolean(authState.accessToken && authState.user)

export const getCurrentUser = () => authState.user

export const getAccessToken = () => authState.accessToken

export const getAuthHeaders = () => {
  if (!authState.accessToken) {
    return {}
  }

  return {
    Authorization: `Bearer ${authState.accessToken}`,
  }
}

export const useCurrentUser = () => computed(() => authState.user)

export const useAuthReady = () => computed(() => authState.ready)
