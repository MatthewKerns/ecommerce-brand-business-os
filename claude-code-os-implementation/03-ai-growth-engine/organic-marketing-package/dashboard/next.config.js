const { withSentryConfig } = require('@sentry/nextjs')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

// Sentry wraps the Next.js config to enable source map uploads and
// automatic instrumentation. It's a no-op when NEXT_PUBLIC_SENTRY_DSN
// is not set, so this is safe to keep in all environments.
module.exports = withSentryConfig(nextConfig, {
  // Suppress source map upload logs during build
  silent: true,

  // Upload source maps only when a Sentry auth token is available
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,

  // Automatically tree-shake Sentry logger statements in production
  disableLogger: true,

  // Hide source maps from the client bundle in production
  hideSourceMaps: true,
})
