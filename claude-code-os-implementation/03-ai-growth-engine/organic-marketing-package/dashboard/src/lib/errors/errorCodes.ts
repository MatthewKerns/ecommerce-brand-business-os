/**
 * Standardized Error Codes Catalog
 *
 * Provides a centralized, consistent error code system for the entire application.
 * Error codes follow the format: CATEGORY_SPECIFIC_ERROR
 */

export enum ErrorCategory {
  NETWORK = 'network',
  VALIDATION = 'validation',
  AUTH = 'auth',
  SERVICE = 'service',
  COMPONENT = 'component',
  UNKNOWN = 'unknown',
}

export enum ErrorCode {
  // Network errors
  NETWORK_TIMEOUT = 'NETWORK_TIMEOUT',
  NETWORK_OFFLINE = 'NETWORK_OFFLINE',
  NETWORK_DNS_FAILURE = 'NETWORK_DNS_FAILURE',
  NETWORK_CONNECTION_REFUSED = 'NETWORK_CONNECTION_REFUSED',

  // API / HTTP errors
  API_BAD_REQUEST = 'API_BAD_REQUEST',
  API_UNAUTHORIZED = 'API_UNAUTHORIZED',
  API_FORBIDDEN = 'API_FORBIDDEN',
  API_NOT_FOUND = 'API_NOT_FOUND',
  API_RATE_LIMITED = 'API_RATE_LIMITED',
  API_CONFLICT = 'API_CONFLICT',
  API_UNPROCESSABLE = 'API_UNPROCESSABLE',
  API_SERVER_ERROR = 'API_SERVER_ERROR',
  API_BAD_GATEWAY = 'API_BAD_GATEWAY',
  API_SERVICE_UNAVAILABLE = 'API_SERVICE_UNAVAILABLE',
  API_GATEWAY_TIMEOUT = 'API_GATEWAY_TIMEOUT',
  API_UNKNOWN = 'API_UNKNOWN',

  // Validation errors
  VALIDATION_REQUIRED_FIELD = 'VALIDATION_REQUIRED_FIELD',
  VALIDATION_INVALID_FORMAT = 'VALIDATION_INVALID_FORMAT',
  VALIDATION_OUT_OF_RANGE = 'VALIDATION_OUT_OF_RANGE',
  VALIDATION_TYPE_MISMATCH = 'VALIDATION_TYPE_MISMATCH',
  VALIDATION_CONSTRAINT = 'VALIDATION_CONSTRAINT',

  // Auth errors
  AUTH_SESSION_EXPIRED = 'AUTH_SESSION_EXPIRED',
  AUTH_INVALID_TOKEN = 'AUTH_INVALID_TOKEN',
  AUTH_INSUFFICIENT_PERMISSIONS = 'AUTH_INSUFFICIENT_PERMISSIONS',
  AUTH_ACCOUNT_LOCKED = 'AUTH_ACCOUNT_LOCKED',
  AUTH_WORKSPACE_REQUIRED = 'AUTH_WORKSPACE_REQUIRED',

  // External service errors
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  SERVICE_TIMEOUT = 'SERVICE_TIMEOUT',
  SERVICE_RATE_LIMITED = 'SERVICE_RATE_LIMITED',
  SERVICE_CONFIGURATION_ERROR = 'SERVICE_CONFIGURATION_ERROR',
  SERVICE_RESPONSE_INVALID = 'SERVICE_RESPONSE_INVALID',

  // Component errors
  COMPONENT_LOAD_FAILURE = 'COMPONENT_LOAD_FAILURE',
  COMPONENT_RENDER_ERROR = 'COMPONENT_RENDER_ERROR',
  COMPONENT_STATE_ERROR = 'COMPONENT_STATE_ERROR',

  // Unknown
  UNKNOWN = 'UNKNOWN',
}

/**
 * Maps HTTP status codes to error codes.
 */
export function errorCodeFromStatus(status: number): ErrorCode {
  const statusMap: Record<number, ErrorCode> = {
    400: ErrorCode.API_BAD_REQUEST,
    401: ErrorCode.API_UNAUTHORIZED,
    403: ErrorCode.API_FORBIDDEN,
    404: ErrorCode.API_NOT_FOUND,
    409: ErrorCode.API_CONFLICT,
    422: ErrorCode.API_UNPROCESSABLE,
    429: ErrorCode.API_RATE_LIMITED,
    500: ErrorCode.API_SERVER_ERROR,
    502: ErrorCode.API_BAD_GATEWAY,
    503: ErrorCode.API_SERVICE_UNAVAILABLE,
    504: ErrorCode.API_GATEWAY_TIMEOUT,
  }

  return statusMap[status] ?? ErrorCode.API_UNKNOWN
}

/**
 * Maps an error code to its category.
 */
export function categoryFromCode(code: ErrorCode): ErrorCategory {
  if (code.startsWith('NETWORK_')) return ErrorCategory.NETWORK
  if (code.startsWith('API_')) return ErrorCategory.NETWORK
  if (code.startsWith('VALIDATION_')) return ErrorCategory.VALIDATION
  if (code.startsWith('AUTH_')) return ErrorCategory.AUTH
  if (code.startsWith('SERVICE_')) return ErrorCategory.SERVICE
  if (code.startsWith('COMPONENT_')) return ErrorCategory.COMPONENT
  return ErrorCategory.UNKNOWN
}
