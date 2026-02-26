"""
Custom exception classes for AI Content Agents

This module defines the exception hierarchy for the AI Content Agents service,
following the error handling patterns defined in docs/ERROR_HANDLING.md.
"""

from typing import Any, Optional


class BusinessOSError(Exception):
    """Base exception for all Business OS errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Initialize a Business OS error

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., "AGENT_001")
            details: Additional context for debugging
        """
        self.message = message
        self.error_code = error_code or "UNKNOWN"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.error_code,
            "details": self.details
        }


# Agent-Related Exceptions
class AgentError(BusinessOSError):
    """Base exception for agent-related errors"""
    pass


class AgentInitializationError(AgentError):
    """Raised when an agent fails to initialize properly"""

    def __init__(self, agent_name: str, reason: str):
        super().__init__(
            message=f"Failed to initialize agent '{agent_name}': {reason}",
            error_code="AGENT_001",
            details={"agent_name": agent_name, "reason": reason}
        )


class ContentGenerationError(AgentError):
    """Raised when content generation fails"""

    def __init__(self, agent_name: str, prompt: str, api_error: str = None):
        super().__init__(
            message=f"Content generation failed for agent '{agent_name}'",
            error_code="AGENT_002",
            details={
                "agent_name": agent_name,
                "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "api_error": api_error
            }
        )


class ModelNotAvailableError(AgentError):
    """Raised when requested AI model is not available"""

    def __init__(self, model_name: str, available_models: list = None):
        super().__init__(
            message=f"Model '{model_name}' is not available",
            error_code="AGENT_003",
            details={
                "requested_model": model_name,
                "available_models": available_models or []
            }
        )


# Configuration Exceptions
class ConfigurationError(BusinessOSError):
    """Base exception for configuration-related errors"""
    pass


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing"""

    def __init__(self, config_key: str, config_file: str = None):
        super().__init__(
            message=f"Missing required configuration: {config_key}",
            error_code="CONFIG_001",
            details={
                "config_key": config_key,
                "config_file": config_file
            }
        )


class InvalidConfigError(ConfigurationError):
    """Raised when configuration value is invalid"""

    def __init__(self, config_key: str, value: Any, expected_type: str = None):
        super().__init__(
            message=f"Invalid configuration for '{config_key}': {value}",
            error_code="CONFIG_002",
            details={
                "config_key": config_key,
                "provided_value": str(value),
                "expected_type": expected_type
            }
        )


class BrandContextLoadError(ConfigurationError):
    """Raised when brand context files cannot be loaded"""

    def __init__(self, file_path: str, reason: str):
        super().__init__(
            message=f"Failed to load brand context from '{file_path}': {reason}",
            error_code="CONFIG_003",
            details={"file_path": file_path, "reason": reason}
        )


# API Exceptions
class APIError(BusinessOSError):
    """Base exception for API-related errors"""
    pass


class AnthropicAPIError(APIError):
    """Raised when Anthropic API call fails"""

    def __init__(self, status_code: int = None, response_body: str = None):
        super().__init__(
            message="Anthropic API request failed",
            error_code="API_001",
            details={
                "status_code": status_code,
                "response_body": response_body
            }
        )


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""

    def __init__(self, retry_after: int = None):
        super().__init__(
            message="API rate limit exceeded",
            error_code="API_002",
            details={"retry_after_seconds": retry_after}
        )


class AuthenticationError(APIError):
    """Raised when API authentication fails"""

    def __init__(self, api_name: str = "Anthropic"):
        super().__init__(
            message=f"{api_name} API authentication failed. Check API key.",
            error_code="API_003",
            details={"api_name": api_name}
        )


# Data Exceptions
class DataError(BusinessOSError):
    """Base exception for data-related errors"""
    pass


class ValidationError(DataError):
    """Raised when data validation fails"""

    def __init__(self, field_name: str, value: Any, validation_rule: str):
        super().__init__(
            message=f"Validation failed for field '{field_name}': {validation_rule}",
            error_code="DATA_001",
            details={
                "field_name": field_name,
                "value": str(value),
                "validation_rule": validation_rule
            }
        )


class DatabaseError(DataError):
    """Raised when database operations fail"""

    def __init__(self, operation: str, reason: str, table_name: str = None):
        super().__init__(
            message=f"Database {operation} failed: {reason}",
            error_code="DATA_002",
            details={
                "operation": operation,
                "reason": reason,
                "table_name": table_name
            }
        )


class SchemaError(DataError):
    """Raised when data schema validation fails"""

    def __init__(self, schema_name: str, validation_errors: list):
        super().__init__(
            message=f"Schema validation failed for '{schema_name}'",
            error_code="DATA_003",
            details={
                "schema_name": schema_name,
                "validation_errors": validation_errors
            }
        )
