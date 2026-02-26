/**
 * Configuration Manager Library
 *
 * Manages configuration for all organic marketing services.
 * Provides centralized configuration storage and retrieval.
 *
 * @example
 * ```ts
 * import { getServiceConfig, updateServiceConfig } from '@/lib/config-manager'
 *
 * const config = await getServiceConfig('tiktok')
 * await updateServiceConfig('tiktok', { apiKey: 'new-key' })
 * ```
 */

export interface ServiceConfig {
  service: string
  settings: {
    [key: string]: string | number | boolean | object
  }
  lastUpdated: string
  status: 'active' | 'inactive' | 'error'
}

export interface AllConfigs {
  timestamp: string
  configs: ServiceConfig[]
}

// In-memory configuration storage
// TODO: Replace with database or persistent storage when available
const configStore = new Map<string, ServiceConfig>()

// Initialize default configurations
const DEFAULT_CONFIGS: ServiceConfig[] = [
  {
    service: 'tiktok',
    status: 'active',
    lastUpdated: new Date().toISOString(),
    settings: {
      apiKey: '',
      webhookUrl: '',
      refreshInterval: 3600,
      autoPost: false,
      contentPillars: ['Battle-Ready Lifestyle', 'Gear & Equipment', 'Community Champion'],
    },
  },
  {
    service: 'blog',
    status: 'active',
    lastUpdated: new Date().toISOString(),
    settings: {
      baseUrl: 'https://blog.infinityvault.com',
      postsPerPage: 10,
      autoPublish: false,
      seoEnabled: true,
      contentCategories: ['product-reviews', 'tutorials', 'community-stories'],
    },
  },
  {
    service: 'email',
    status: 'active',
    lastUpdated: new Date().toISOString(),
    settings: {
      provider: 'sendgrid',
      apiKey: '',
      fromEmail: 'noreply@infinityvault.com',
      fromName: 'Infinity Vault',
      autoSendEnabled: false,
      campaignTemplates: ['welcome', 'product-launch', 'engagement'],
    },
  },
]

// Initialize store with defaults
DEFAULT_CONFIGS.forEach((config) => {
  configStore.set(config.service, config)
})

/**
 * Get configuration for a specific service
 *
 * @param {string} serviceName - Name of the service (tiktok, blog, email)
 * @returns {Promise<ServiceConfig>} Configuration for the specified service
 */
export async function getServiceConfig(serviceName: string): Promise<ServiceConfig> {
  const config = configStore.get(serviceName.toLowerCase())

  if (!config) {
    return {
      service: serviceName,
      status: 'error',
      lastUpdated: new Date().toISOString(),
      settings: {},
    }
  }

  return {
    ...config,
    lastUpdated: new Date().toISOString(),
  }
}

/**
 * Get all service configurations
 *
 * @returns {Promise<AllConfigs>} All service configurations
 */
export async function getAllConfigs(): Promise<AllConfigs> {
  const configs = Array.from(configStore.values())

  return {
    timestamp: new Date().toISOString(),
    configs,
  }
}

/**
 * Update configuration for a specific service
 *
 * @param {string} serviceName - Name of the service (tiktok, blog, email)
 * @param {object} settings - Configuration settings to update
 * @returns {Promise<ServiceConfig>} Updated configuration
 */
export async function updateServiceConfig(
  serviceName: string,
  settings: { [key: string]: string | number | boolean | object }
): Promise<ServiceConfig> {
  const existingConfig = configStore.get(serviceName.toLowerCase())

  if (!existingConfig) {
    throw new Error(`Unknown service: ${serviceName}`)
  }

  const updatedConfig: ServiceConfig = {
    service: serviceName.toLowerCase(),
    status: 'active',
    lastUpdated: new Date().toISOString(),
    settings: {
      ...existingConfig.settings,
      ...settings,
    },
  }

  configStore.set(serviceName.toLowerCase(), updatedConfig)

  return updatedConfig
}

/**
 * Reset configuration for a specific service to defaults
 *
 * @param {string} serviceName - Name of the service (tiktok, blog, email)
 * @returns {Promise<ServiceConfig>} Reset configuration
 */
export async function resetServiceConfig(serviceName: string): Promise<ServiceConfig> {
  const defaultConfig = DEFAULT_CONFIGS.find(
    (c) => c.service === serviceName.toLowerCase()
  )

  if (!defaultConfig) {
    throw new Error(`Unknown service: ${serviceName}`)
  }

  const resetConfig: ServiceConfig = {
    ...defaultConfig,
    lastUpdated: new Date().toISOString(),
  }

  configStore.set(serviceName.toLowerCase(), resetConfig)

  return resetConfig
}

/**
 * Validate service configuration settings
 *
 * @param {string} serviceName - Name of the service
 * @param {object} settings - Configuration settings to validate
 * @returns {boolean} True if valid, throws error if invalid
 */
export function validateServiceConfig(
  serviceName: string,
  settings: { [key: string]: unknown }
): boolean {
  // Basic validation rules per service
  const validationRules: { [key: string]: string[] } = {
    tiktok: ['apiKey', 'webhookUrl', 'refreshInterval', 'autoPost', 'contentPillars'],
    blog: ['baseUrl', 'postsPerPage', 'autoPublish', 'seoEnabled', 'contentCategories'],
    email: [
      'provider',
      'apiKey',
      'fromEmail',
      'fromName',
      'autoSendEnabled',
      'campaignTemplates',
    ],
  }

  const allowedKeys = validationRules[serviceName.toLowerCase()]
  if (!allowedKeys) {
    throw new Error(`Unknown service: ${serviceName}`)
  }

  // Check for invalid keys
  const providedKeys = Object.keys(settings)
  const invalidKeys = providedKeys.filter((key) => !allowedKeys.includes(key))

  if (invalidKeys.length > 0) {
    throw new Error(
      `Invalid configuration keys for ${serviceName}: ${invalidKeys.join(', ')}`
    )
  }

  return true
}
