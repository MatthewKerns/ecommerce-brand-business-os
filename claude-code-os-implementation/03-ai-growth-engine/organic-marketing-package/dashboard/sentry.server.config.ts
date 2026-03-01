/**
 * Sentry Server-Side Configuration
 *
 * This file configures Sentry for the Node.js server runtime.
 * It is automatically loaded by @sentry/nextjs.
 */

import { initSentry } from '@/lib/monitoring/sentry'

initSentry({
  // Server-specific overrides
  // No replay on server side
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,
})
