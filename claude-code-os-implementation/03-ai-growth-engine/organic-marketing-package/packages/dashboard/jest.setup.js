require('@testing-library/jest-dom')

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    prefetch: jest.fn(),
    refresh: jest.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock IntersectionObserver
class MockIntersectionObserver {
  constructor(callback) {
    this.callback = callback
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
})

// Suppress console.error in tests unless DEBUG_TESTS is set
if (!process.env.DEBUG_TESTS) {
  const originalError = console.error
  beforeAll(() => {
    console.error = (...args) => {
      // Allow React error boundary messages through
      if (
        typeof args[0] === 'string' &&
        args[0].includes('ErrorBoundary')
      ) {
        return
      }
      // Suppress "act" warnings and other test noise
      if (
        typeof args[0] === 'string' &&
        (args[0].includes('act(') ||
          args[0].includes('Not implemented') ||
          args[0].includes('Warning:'))
      ) {
        return
      }
      originalError.call(console, ...args)
    }
  })
  afterAll(() => {
    console.error = originalError
  })
}
