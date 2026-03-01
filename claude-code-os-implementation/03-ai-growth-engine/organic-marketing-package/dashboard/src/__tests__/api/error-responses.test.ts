import { ApiError, apiClient } from '@/lib/api-client'

// Mock resilience module to avoid retry/circuit-breaker logic in unit tests
jest.mock('@/lib/resilience', () => ({
  withRetry: jest.fn((fn: () => Promise<unknown>) => fn()),
  retryPolicies: {
    read: undefined,
    write: undefined,
    critical: undefined,
  },
  deduplicateRequest: jest.fn(
    (_key: string, fn: () => Promise<unknown>) => fn()
  ),
  generateIdempotencyKey: jest.fn(() => 'test-idempotency-key'),
}))

// Mock global fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('ApiError', () => {
  it('creates error with status and data', () => {
    const error = new ApiError('Not found', 404, { detail: 'Resource missing' })

    expect(error.message).toBe('Not found')
    expect(error.name).toBe('ApiError')
    expect(error.status).toBe(404)
    expect(error.data).toEqual({ detail: 'Resource missing' })
  })

  it('is an instance of Error', () => {
    const error = new ApiError('test', 500)
    expect(error).toBeInstanceOf(Error)
    expect(error).toBeInstanceOf(ApiError)
  })
})

describe('apiClient.get', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('returns parsed JSON on success', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'test' }),
    })

    const result = await apiClient.get('/api/test')

    expect(result).toEqual({ data: 'test' })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    )
  })

  it('throws ApiError on HTTP error with JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ message: 'Not found' }),
    })

    await expect(apiClient.get('/api/test')).rejects.toThrow(ApiError)

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ message: 'Not found' }),
    })

    await expect(apiClient.get('/api/test')).rejects.toMatchObject({
      status: 404,
    })
  })

  it('throws ApiError on HTTP error without JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error('not json')
      },
    })

    await expect(apiClient.get('/api/test')).rejects.toThrow('HTTP error 500')
  })

  it('passes custom headers', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    })

    await apiClient.get('/api/test', {
      headers: { Authorization: 'Bearer token123' },
    })

    expect(mockFetch).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token123',
        }),
      })
    )
  })

  it('aborts on timeout', async () => {
    mockFetch.mockImplementation(
      (_url: string, options: { signal: AbortSignal }) =>
        new Promise((_resolve, reject) => {
          options.signal.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'))
          })
        })
    )

    await expect(
      apiClient.get('/api/test', { timeout: 50 })
    ).rejects.toThrow()
  })
})

describe('apiClient.post', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('sends POST with JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '123' }),
    })

    const result = await apiClient.post('/api/test', { name: 'test' })

    expect(result).toEqual({ id: '123' })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/test',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ name: 'test' }),
      })
    )
  })

  it('throws ApiError on POST failure', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: async () => ({ message: 'Validation failed' }),
    })

    await expect(
      apiClient.post('/api/test', { invalid: true })
    ).rejects.toThrow('Validation failed')
  })

  it('wraps non-fetch errors', async () => {
    mockFetch.mockRejectedValueOnce(new TypeError('Network error'))

    await expect(apiClient.post('/api/test', {})).rejects.toThrow()
  })
})

describe('apiClient.put', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('sends PUT with JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ updated: true }),
    })

    const result = await apiClient.put('/api/test/1', { name: 'updated' })

    expect(result).toEqual({ updated: true })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/test/1',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({ name: 'updated' }),
      })
    )
  })
})

describe('apiClient.delete', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('sends DELETE request', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ deleted: true }),
    })

    const result = await apiClient.delete('/api/test/1')

    expect(result).toEqual({ deleted: true })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/test/1',
      expect.objectContaining({
        method: 'DELETE',
      })
    )
  })

  it('throws on delete failure', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: async () => ({ message: 'Forbidden' }),
    })

    await expect(apiClient.delete('/api/test/1')).rejects.toThrow('Forbidden')
  })
})
