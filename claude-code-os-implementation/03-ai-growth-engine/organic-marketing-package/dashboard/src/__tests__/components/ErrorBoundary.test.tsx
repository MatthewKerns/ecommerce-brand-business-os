import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from '@/components/ErrorBoundary'

// Component that throws an error on demand
function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test component error')
  }
  return <div>Healthy content</div>
}

// Component that throws on a specific render
function DelayedThrow({ throwOnRender }: { throwOnRender: number }) {
  const renderCount = React.useRef(0)
  renderCount.current += 1

  if (renderCount.current >= throwOnRender) {
    throw new Error('Delayed component error')
  }
  return <div>Render {renderCount.current}</div>
}

describe('ErrorBoundary', () => {
  // Suppress React error boundary console noise
  const originalError = console.error
  beforeAll(() => {
    console.error = jest.fn()
  })
  afterAll(() => {
    console.error = originalError
  })

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Healthy content')).toBeInTheDocument()
  })

  it('renders default error UI when a child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Try Again')).toBeInTheDocument()
    expect(screen.getByText('Go to Dashboard')).toBeInTheDocument()
  })

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom error view</div>}>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Custom error view')).toBeInTheDocument()
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('calls onError callback when error is caught', () => {
    const onError = jest.fn()

    render(
      <ErrorBoundary onError={onError}>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(onError).toHaveBeenCalledTimes(1)
    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({ message: 'Test component error' }),
      expect.objectContaining({ componentStack: expect.any(String) })
    )
  })

  it('resets error state when Try Again is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Rerender with non-throwing child before clicking reset
    rerender(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>
    )

    fireEvent.click(screen.getByText('Try Again'))

    expect(screen.getByText('Healthy content')).toBeInTheDocument()
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV
    Object.defineProperty(process.env, 'NODE_ENV', { value: 'development', configurable: true })

    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Error Details:')).toBeInTheDocument()
    expect(screen.getByText('Test component error')).toBeInTheDocument()

    Object.defineProperty(process.env, 'NODE_ENV', { value: originalEnv, configurable: true })
  })

  it('handles multiple sequential errors after reset', () => {
    let shouldThrow = true

    function ConditionalThrow() {
      if (shouldThrow) {
        throw new Error('Sequential error')
      }
      return <div>Recovered</div>
    }

    const { rerender } = render(
      <ErrorBoundary>
        <ConditionalThrow />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Reset without fixing the throw
    shouldThrow = false
    rerender(
      <ErrorBoundary>
        <ConditionalThrow />
      </ErrorBoundary>
    )
    fireEvent.click(screen.getByText('Try Again'))

    expect(screen.getByText('Recovered')).toBeInTheDocument()
  })

  it('does not catch errors outside its boundary', () => {
    // Verify that each ErrorBoundary is independent
    render(
      <div>
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={false} />
        </ErrorBoundary>
      </div>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Healthy content')).toBeInTheDocument()
  })
})
