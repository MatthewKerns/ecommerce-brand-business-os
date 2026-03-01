/**
 * Sentry Edge Runtime Configuration
 *
 * This file configures Sentry for the Edge runtime (middleware, edge API routes).
 * It is automatically loaded by @sentry/nextjs.
 */

import { initSentry } from '@/lib/monitoring/sentry'

initSentry({
  // Edge runtime overrides
  // Lower sample rate for edge since it handles high traffic
  tracesSampleRate: 0.05,
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,
})
