/**
 * Sentry Client-Side Configuration
 *
 * This file configures Sentry for the browser/client runtime.
 * It is automatically loaded by @sentry/nextjs.
 */

import { initSentry } from '@/lib/monitoring/sentry'

initSentry({
  // Client-specific overrides can go here
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
})
