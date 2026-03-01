/**
 * Test suite for async state management patterns.
 *
 * Since the useAsyncState hook is being built by the component-specialist (task #10),
 * this file provides the test scaffolding and tests for the expected interface.
 * Tests will validate the hook once it is implemented.
 */

// Placeholder: import { useAsyncState } from '@/hooks/useAsyncState'
import { renderHook, act, waitFor } from '@testing-library/react'

/**
 * Minimal implementation to validate test infrastructure works.
 * This will be replaced by the actual useAsyncState hook from task #10.
 */
type AsyncState<T> = {
  data: T | null
  error: Error | null
  isLoading: boolean
  isError: boolean
  isSuccess: boolean
  execute: () => Promise<void>
  reset: () => void
}

function useAsyncState<T>(
  asyncFn: () => Promise<T>,
  options: { immediate?: boolean } = {}
): AsyncState<T> {
  const [state, setState] = React.useState<{
    data: T | null
    error: Error | null
    isLoading: boolean
  }>({
    data: null,
    error: null,
    isLoading: options.immediate ?? false,
  })

  const execute = React.useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))
    try {
      const data = await asyncFn()
      setState({ data, error: null, isLoading: false })
    } catch (err) {
      setState({
        data: null,
        error: err instanceof Error ? err : new Error('Unknown error'),
        isLoading: false,
      })
    }
  }, [asyncFn])

  const reset = React.useCallback(() => {
    setState({ data: null, error: null, isLoading: false })
  }, [])

  React.useEffect(() => {
    if (options.immediate) {
      execute()
    }
  }, [])

  return {
    ...state,
    isError: state.error !== null,
    isSuccess: state.data !== null && state.error === null,
    execute,
    reset,
  }
}

import React from 'react'

describe('useAsyncState', () => {
  it('starts in idle state', () => {
    const asyncFn = jest.fn().mockResolvedValue('data')

    const { result } = renderHook(() => useAsyncState(asyncFn))

    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.isLoading).toBe(false)
    expect(result.current.isError).toBe(false)
    expect(result.current.isSuccess).toBe(false)
  })

  it('transitions to loading on execute', async () => {
    let resolvePromise: (value: string) => void
    const asyncFn = jest.fn(
      () =>
        new Promise<string>((resolve) => {
          resolvePromise = resolve
        })
    )

    const { result } = renderHook(() => useAsyncState(asyncFn))

    act(() => {
      result.current.execute()
    })

    expect(result.current.isLoading).toBe(true)

    await act(async () => {
      resolvePromise!('data')
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBe('data')
    expect(result.current.isSuccess).toBe(true)
  })

  it('handles errors correctly', async () => {
    const error = new Error('fetch failed')
    const asyncFn = jest.fn().mockRejectedValue(error)

    const { result } = renderHook(() => useAsyncState(asyncFn))

    await act(async () => {
      await result.current.execute()
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.isError).toBe(true)
    expect(result.current.error?.message).toBe('fetch failed')
    expect(result.current.data).toBeNull()
  })

  it('executes immediately when immediate option is true', async () => {
    const asyncFn = jest.fn().mockResolvedValue('immediate data')

    const { result } = renderHook(() =>
      useAsyncState(asyncFn, { immediate: true })
    )

    await waitFor(() => {
      expect(result.current.data).toBe('immediate data')
    })

    expect(asyncFn).toHaveBeenCalledTimes(1)
  })

  it('resets state correctly', async () => {
    const asyncFn = jest.fn().mockResolvedValue('data')

    const { result } = renderHook(() => useAsyncState(asyncFn))

    await act(async () => {
      await result.current.execute()
    })

    expect(result.current.data).toBe('data')

    act(() => {
      result.current.reset()
    })

    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.isLoading).toBe(false)
  })

  it('clears previous error on re-execute', async () => {
    const asyncFn = jest
      .fn()
      .mockRejectedValueOnce(new Error('first error'))
      .mockResolvedValueOnce('success')

    const { result } = renderHook(() => useAsyncState(asyncFn))

    // First call - error
    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.isError).toBe(true)

    // Second call - success
    await act(async () => {
      await result.current.execute()
    })
    expect(result.current.isError).toBe(false)
    expect(result.current.data).toBe('success')
  })

  it('handles non-Error rejections', async () => {
    const asyncFn = jest.fn().mockRejectedValue('string error')

    const { result } = renderHook(() => useAsyncState(asyncFn))

    await act(async () => {
      await result.current.execute()
    })

    expect(result.current.isError).toBe(true)
    expect(result.current.error?.message).toBe('Unknown error')
  })
})
