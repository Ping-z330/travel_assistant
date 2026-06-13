import { beforeEach, describe, expect, it, vi } from 'vitest'

const axiosMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('axios', () => ({
  default: axiosMock,
}))

type MemoryStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>

const createMemoryStorage = (): MemoryStorage => {
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

describe('auth', () => {
  beforeEach(() => {
    vi.resetModules()
    axiosMock.get.mockReset()
    axiosMock.post.mockReset()
    delete (globalThis as { window?: unknown }).window
    delete (globalThis as { localStorage?: unknown }).localStorage
  })

  it('logs in and persists access token and user', async () => {
    const storage = createMemoryStorage()
    Object.defineProperty(globalThis, 'localStorage', {
      value: storage,
      configurable: true,
    })

    axiosMock.post.mockResolvedValue({
      data: {
        access_token: 'token-1',
        token_type: 'bearer',
        user: {
          username: 'demo',
          display_name: '旅行助手用户',
        },
      },
    })

    const auth = await import('./auth')
    const user = await auth.login({
      username: 'demo',
      password: 'travel123',
    })

    expect(user).toEqual({
      username: 'demo',
      display_name: '旅行助手用户',
    })
    expect(storage.getItem('travelAssistantAccessToken')).toBe('token-1')
    expect(storage.getItem('travelAssistantAuthUser')).toContain('旅行助手用户')
    expect(auth.isAuthenticated()).toBe(true)
  })

  it('refreshes the current user from /me when a token exists', async () => {
    const storage = createMemoryStorage()
    storage.setItem('travelAssistantAccessToken', 'token-2')
    storage.setItem(
      'travelAssistantAuthUser',
      JSON.stringify({
        username: 'demo',
        display_name: '旧用户',
      }),
    )

    Object.defineProperty(globalThis, 'window', {
      value: {},
      configurable: true,
    })
    Object.defineProperty(globalThis, 'localStorage', {
      value: storage,
      configurable: true,
    })

    axiosMock.get.mockResolvedValue({
      data: {
        username: 'demo',
        display_name: '新用户',
      },
    })

    const auth = await import('./auth')
    await auth.ensureAuthReady()

    expect(axiosMock.get).toHaveBeenCalledTimes(1)
    expect(auth.getCurrentUser()).toEqual({
      username: 'demo',
      display_name: '新用户',
    })
  })

  it('clears stored auth state on logout', async () => {
    const storage = createMemoryStorage()
    Object.defineProperty(globalThis, 'localStorage', {
      value: storage,
      configurable: true,
    })

    axiosMock.post.mockResolvedValue({
      data: {
        access_token: 'token-3',
        token_type: 'bearer',
        user: {
          username: 'demo',
          display_name: '旅行助手用户',
        },
      },
    })

    const auth = await import('./auth')
    await auth.login({
      username: 'demo',
      password: 'travel123',
    })
    auth.logout()

    expect(storage.getItem('travelAssistantAccessToken')).toBeNull()
    expect(storage.getItem('travelAssistantAuthUser')).toBeNull()
    expect(auth.isAuthenticated()).toBe(false)
  })
})
