/**
 * Alert Configuration and Dispatch
 *
 * Defines alert rules for error rate thresholds and service degradation.
 * Supports Slack, email, and custom webhook channels.
 */

import { ErrorCategory } from '@/lib/errors/errorCodes'

// ---------------------------------------------------------------------------
// Alert types
// ---------------------------------------------------------------------------

export type AlertSeverity = 'info' | 'warning' | 'critical'

export type AlertChannel = 'slack' | 'email' | 'webhook'

export interface AlertRule {
  id: string
  name: string
  description: string
  enabled: boolean
  severity: AlertSeverity
  channels: AlertChannel[]
  condition: AlertCondition
  cooldownMinutes: number
}

export type AlertCondition =
  | { type: 'error_rate_threshold'; errorsPerMinute: number; category?: ErrorCategory }
  | { type: 'service_down'; serviceName: string; durationMinutes: number }
  | { type: 'circuit_breaker_open'; serviceName: string }
  | { type: 'error_spike'; percentIncrease: number; windowMinutes: number }

export interface AlertEvent {
  ruleId: string
  ruleName: string
  severity: AlertSeverity
  message: string
  timestamp: string
  metadata: Record<string, unknown>
}

export interface ChannelConfig {
  slack?: { webhookUrl: string; channel: string }
  email?: { recipients: string[]; fromAddress: string }
  webhook?: { url: string; headers?: Record<string, string> }
}

// ---------------------------------------------------------------------------
// Default alert rules
// ---------------------------------------------------------------------------

export const DEFAULT_ALERT_RULES: AlertRule[] = [
  {
    id: 'high-error-rate',
    name: 'High Error Rate',
    description: 'Fires when overall error rate exceeds 10 errors per minute',
    enabled: true,
    severity: 'critical',
    channels: ['slack', 'email'],
    condition: { type: 'error_rate_threshold', errorsPerMinute: 10 },
    cooldownMinutes: 15,
  },
  {
    id: 'api-error-spike',
    name: 'API Error Spike',
    description: 'Fires when API errors increase by 200% over 5 minutes',
    enabled: true,
    severity: 'warning',
    channels: ['slack'],
    condition: { type: 'error_spike', percentIncrease: 200, windowMinutes: 5 },
    cooldownMinutes: 10,
  },
  {
    id: 'service-down',
    name: 'Service Down',
    description: 'Fires when any external service is unreachable for 2+ minutes',
    enabled: true,
    severity: 'critical',
    channels: ['slack', 'email', 'webhook'],
    condition: { type: 'service_down', serviceName: '*', durationMinutes: 2 },
    cooldownMinutes: 5,
  },
  {
    id: 'circuit-breaker-open',
    name: 'Circuit Breaker Opened',
    description: 'Fires when a circuit breaker transitions to open state',
    enabled: true,
    severity: 'warning',
    channels: ['slack'],
    condition: { type: 'circuit_breaker_open', serviceName: '*' },
    cooldownMinutes: 15,
  },
  {
    id: 'auth-error-surge',
    name: 'Authentication Error Surge',
    description: 'Fires when auth errors exceed 5 per minute (potential attack)',
    enabled: true,
    severity: 'critical',
    channels: ['slack', 'email'],
    condition: { type: 'error_rate_threshold', errorsPerMinute: 5, category: ErrorCategory.AUTH },
    cooldownMinutes: 30,
  },
]

// ---------------------------------------------------------------------------
// Alert dispatch
// ---------------------------------------------------------------------------

const lastFiredAt = new Map<string, number>()

/**
 * Evaluate alert rules against current metrics and dispatch if triggered.
 */
export async function evaluateAlerts(
  rules: AlertRule[],
  channelConfig: ChannelConfig,
  context: {
    errorsPerMinute: number
    errorsByCategory: Partial<Record<ErrorCategory, number>>
    openCircuitBreakers: string[]
    downServices: Array<{ name: string; downSinceMinutes: number }>
  }
) {
  const now = Date.now()
  const triggered: AlertEvent[] = []

  for (const rule of rules) {
    if (!rule.enabled) continue

    // Check cooldown
    const lastFired = lastFiredAt.get(rule.id) ?? 0
    if (now - lastFired < rule.cooldownMinutes * 60_000) continue

    const shouldFire = checkCondition(rule.condition, context)
    if (!shouldFire) continue

    const event: AlertEvent = {
      ruleId: rule.id,
      ruleName: rule.name,
      severity: rule.severity,
      message: buildAlertMessage(rule, context),
      timestamp: new Date().toISOString(),
      metadata: { ...context },
    }

    triggered.push(event)
    lastFiredAt.set(rule.id, now)

    // Dispatch to configured channels
    await dispatchAlert(event, rule.channels, channelConfig)
  }

  return triggered
}

function checkCondition(
  condition: AlertCondition,
  context: {
    errorsPerMinute: number
    errorsByCategory: Partial<Record<ErrorCategory, number>>
    openCircuitBreakers: string[]
    downServices: Array<{ name: string; downSinceMinutes: number }>
  }
): boolean {
  switch (condition.type) {
    case 'error_rate_threshold': {
      if (condition.category) {
        return (context.errorsByCategory[condition.category] ?? 0) >= condition.errorsPerMinute
      }
      return context.errorsPerMinute >= condition.errorsPerMinute
    }
    case 'service_down': {
      if (condition.serviceName === '*') {
        return context.downServices.some((s) => s.downSinceMinutes >= condition.durationMinutes)
      }
      const svc = context.downServices.find((s) => s.name === condition.serviceName)
      return svc ? svc.downSinceMinutes >= condition.durationMinutes : false
    }
    case 'circuit_breaker_open': {
      if (condition.serviceName === '*') {
        return context.openCircuitBreakers.length > 0
      }
      return context.openCircuitBreakers.includes(condition.serviceName)
    }
    case 'error_spike':
      // Spike detection requires historical comparison - simplified here
      return false
  }
}

function buildAlertMessage(
  rule: AlertRule,
  context: { errorsPerMinute: number; openCircuitBreakers: string[]; downServices: Array<{ name: string }> }
): string {
  switch (rule.condition.type) {
    case 'error_rate_threshold':
      return `Error rate is ${context.errorsPerMinute}/min (threshold: ${rule.condition.errorsPerMinute}/min)`
    case 'service_down':
      return `Services down: ${context.downServices.map((s) => s.name).join(', ')}`
    case 'circuit_breaker_open':
      return `Circuit breakers open: ${context.openCircuitBreakers.join(', ')}`
    case 'error_spike':
      return `Error spike detected`
  }
}

async function dispatchAlert(event: AlertEvent, channels: AlertChannel[], config: ChannelConfig) {
  const dispatchers: Promise<void>[] = []

  for (const channel of channels) {
    switch (channel) {
      case 'slack':
        if (config.slack) dispatchers.push(sendSlackAlert(event, config.slack))
        break
      case 'email':
        if (config.email) dispatchers.push(sendEmailAlert(event, config.email))
        break
      case 'webhook':
        if (config.webhook) dispatchers.push(sendWebhookAlert(event, config.webhook))
        break
    }
  }

  await Promise.allSettled(dispatchers)
}

async function sendSlackAlert(
  event: AlertEvent,
  config: { webhookUrl: string; channel: string }
) {
  const color = event.severity === 'critical' ? '#dc2626' : event.severity === 'warning' ? '#f59e0b' : '#3b82f6'

  try {
    await fetch(config.webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: config.channel,
        attachments: [
          {
            color,
            title: `[${event.severity.toUpperCase()}] ${event.ruleName}`,
            text: event.message,
            ts: Math.floor(new Date(event.timestamp).getTime() / 1000),
          },
        ],
      }),
    })
  } catch {
    console.error('[Alerts] Failed to send Slack alert:', event.ruleId)
  }
}

async function sendEmailAlert(
  event: AlertEvent,
  config: { recipients: string[]; fromAddress: string }
) {
  // Email sending would integrate with the existing email automation service
  // For now, log the intent
  console.info('[Alerts] Email alert:', {
    to: config.recipients,
    from: config.fromAddress,
    subject: `[${event.severity.toUpperCase()}] ${event.ruleName}`,
    body: event.message,
  })
}

async function sendWebhookAlert(
  event: AlertEvent,
  config: { url: string; headers?: Record<string, string> }
) {
  try {
    await fetch(config.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...config.headers },
      body: JSON.stringify(event),
    })
  } catch {
    console.error('[Alerts] Failed to send webhook alert:', event.ruleId)
  }
}
