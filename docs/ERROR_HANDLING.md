# Error Handling Guide

## Overview

This document defines the error handling standards, exception class hierarchy, logging patterns, and error response formats for the E-Commerce Brand Business OS. Proper error handling is critical to system reliability and competitive advantage over platforms like GoHighLevel that suffer from "constant glitches."

## Design Philosophy

Our error handling follows these core principles:

1. **Fail Fast, Fail Clearly**: Errors should be detected early and communicated with context
2. **Structured Exceptions**: Use typed exception classes rather than generic errors
3. **Consistent Logging**: All errors are logged with appropriate severity levels
4. **User-Friendly Messages**: External errors provide actionable feedback, not stack traces
5. **Graceful Degradation**: Systems should degrade gracefully when dependencies fail

## Exception Class Hierarchy

### Base Exception Classes

All custom exceptions inherit from a common base to enable consistent error handling across the system.

```python
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
```

### Agent-Related Exceptions

```python
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
```

### Configuration Exceptions

```python
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

    def __init__(self, config_key: str, value: any, expected_type: str = None):
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
```

### API Exceptions

```python
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
```

### Data Exceptions

```python
class DataError(BusinessOSError):
    """Base exception for data-related errors"""
    pass


class ValidationError(DataError):
    """Raised when data validation fails"""

    def __init__(self, field: str, value: any, constraint: str):
        super().__init__(
            message=f"Validation failed for '{field}': {constraint}",
            error_code="DATA_001",
            details={
                "field": field,
                "value": str(value),
                "constraint": constraint
            }
        )


class DatabaseError(DataError):
    """Raised when database operation fails"""

    def __init__(self, operation: str, table: str = None, reason: str = None):
        super().__init__(
            message=f"Database {operation} failed",
            error_code="DATA_002",
            details={
                "operation": operation,
                "table": table,
                "reason": reason
            }
        )


class FileOperationError(DataError):
    """Raised when file I/O operation fails"""

    def __init__(self, operation: str, file_path: str, reason: str):
        super().__init__(
            message=f"File {operation} failed for '{file_path}': {reason}",
            error_code="DATA_003",
            details={
                "operation": operation,
                "file_path": file_path,
                "reason": reason
            }
        )
```

## Logging Standards

### Logging Configuration

```python
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(
    log_dir: Path,
    log_level: str = "INFO",
    agent_name: str = None
) -> logging.Logger:
    """
    Configure structured logging for agents

    Args:
        log_dir: Directory to store log files
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        agent_name: Optional agent name for logger identification

    Returns:
        Configured logger instance
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger_name = f"business_os.{agent_name}" if agent_name else "business_os"
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # File handler with rotation
    log_file = log_dir / f"{agent_name or 'app'}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler (less verbose)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Structured format
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(funcName)s:%(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

### Logging Levels

Use logging levels consistently across the system:

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Detailed diagnostic information | Variable values, function entry/exit |
| **INFO** | General informational messages | "Agent initialized", "Content generated" |
| **WARNING** | Unexpected but recoverable issues | "Brand context file not found, using defaults" |
| **ERROR** | Error events that still allow operation | "Failed to generate content, retrying" |
| **CRITICAL** | Critical errors causing shutdown | "Database connection lost", "API key invalid" |

### Logging Patterns

#### Success Logging

```python
logger.info("Content generation started", extra={
    "agent": self.agent_name,
    "model": self.model,
    "prompt_length": len(prompt)
})

logger.info("Content generation completed", extra={
    "agent": self.agent_name,
    "output_length": len(content),
    "tokens_used": message.usage.total_tokens
})
```

#### Error Logging

```python
try:
    content = self.generate_content(prompt)
except AnthropicAPIError as e:
    logger.error(
        f"API request failed: {e.message}",
        extra={
            "error_code": e.error_code,
            "status_code": e.details.get("status_code"),
            "agent": self.agent_name
        },
        exc_info=True  # Include stack trace
    )
    raise
except Exception as e:
    logger.critical(
        f"Unexpected error: {str(e)}",
        extra={"agent": self.agent_name},
        exc_info=True
    )
    raise
```

#### Warning Logging

```python
if not BRAND_VOICE_PATH.exists():
    logger.warning(
        "Brand voice file not found, using default voice",
        extra={
            "expected_path": str(BRAND_VOICE_PATH),
            "agent": self.agent_name
        }
    )
```

## Error Handling Patterns

### Try-Except Best Practices

```python
def generate_content(self, prompt: str) -> str:
    """Generate content with proper error handling"""

    try:
        # Validate input
        if not prompt or not prompt.strip():
            raise ValidationError(
                field="prompt",
                value=prompt,
                constraint="Prompt cannot be empty"
            )

        # Make API call
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    except ValidationError:
        # Re-raise validation errors (already well-formed)
        raise

    except anthropic.AuthenticationError as e:
        # Convert library errors to our exception types
        raise AuthenticationError() from e

    except anthropic.RateLimitError as e:
        retry_after = getattr(e, 'retry_after', None)
        raise RateLimitError(retry_after=retry_after) from e

    except anthropic.APIError as e:
        # Generic API errors
        raise AnthropicAPIError(
            status_code=getattr(e, 'status_code', None),
            response_body=str(e)
        ) from e

    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception("Unexpected error in content generation")
        raise ContentGenerationError(
            agent_name=self.agent_name,
            prompt=prompt,
            api_error=str(e)
        ) from e
```

### Context Managers for Resource Cleanup

```python
from contextlib import contextmanager

@contextmanager
def agent_context(agent_name: str, logger: logging.Logger):
    """Context manager for agent operations with automatic cleanup"""
    logger.info(f"Starting {agent_name} operation")
    try:
        yield
        logger.info(f"{agent_name} operation completed successfully")
    except BusinessOSError as e:
        logger.error(f"{agent_name} operation failed: {e.message}", extra={
            "error_code": e.error_code,
            "details": e.details
        })
        raise
    except Exception as e:
        logger.critical(f"{agent_name} unexpected error: {str(e)}", exc_info=True)
        raise
    finally:
        # Cleanup logic here
        logger.debug(f"{agent_name} cleanup completed")
```

### Retry Logic with Exponential Backoff

```python
import time
from typing import Callable, Any

def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    logger: logging.Logger = None
) -> Any:
    """
    Retry a function with exponential backoff

    Args:
        func: Function to retry
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        logger: Optional logger for retry messages

    Returns:
        Result of successful function call

    Raises:
        Last exception encountered after all retries exhausted
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return func()
        except RateLimitError as e:
            last_exception = e
            # Use server-provided retry-after if available
            delay = e.details.get('retry_after_seconds') or \
                    min(base_delay * (exponential_base ** attempt), max_delay)

            if logger:
                logger.warning(
                    f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_attempts})"
                )

            if attempt < max_attempts - 1:
                time.sleep(delay)

        except (AnthropicAPIError, ContentGenerationError) as e:
            last_exception = e

            if attempt < max_attempts - 1:
                delay = min(base_delay * (exponential_base ** attempt), max_delay)
                if logger:
                    logger.warning(
                        f"API error, retrying in {delay}s (attempt {attempt + 1}/{max_attempts}): {e.message}"
                    )
                time.sleep(delay)
            else:
                # Don't retry on last attempt
                break

        except Exception as e:
            # Don't retry on unexpected errors
            if logger:
                logger.error(f"Unexpected error, not retrying: {str(e)}")
            raise

    # All retries exhausted
    raise last_exception
```

## Error Response Formats

### API Error Response Structure

When building REST APIs, use this standardized error response format:

```json
{
  "success": false,
  "error": {
    "type": "ContentGenerationError",
    "message": "Content generation failed for agent 'blog_agent'",
    "code": "AGENT_002",
    "details": {
      "agent_name": "blog_agent",
      "prompt_preview": "Write a blog post about...",
      "api_error": "Model overloaded"
    }
  },
  "timestamp": "2025-02-25T21:15:30Z",
  "request_id": "req_abc123"
}
```

### CLI Error Output

For command-line interfaces, provide user-friendly error messages:

```python
def format_error_for_cli(error: BusinessOSError) -> str:
    """Format error for command-line display"""
    output = f"❌ Error: {error.message}\n"
    output += f"Code: {error.error_code}\n"

    if error.details:
        output += "\nDetails:\n"
        for key, value in error.details.items():
            output += f"  • {key}: {value}\n"

    # Provide actionable suggestions
    if isinstance(error, AuthenticationError):
        output += "\n💡 Tip: Check that ANTHROPIC_API_KEY is set in your environment"
    elif isinstance(error, RateLimitError):
        retry_after = error.details.get('retry_after_seconds')
        if retry_after:
            output += f"\n💡 Tip: Please wait {retry_after} seconds before retrying"
    elif isinstance(error, BrandContextLoadError):
        output += "\n💡 Tip: Ensure brand context files exist in the config/brand-context/ directory"

    return output
```

## Testing Error Handling

### Unit Testing Exception Handling

```python
import pytest
from agents.base_agent import BaseAgent
from exceptions import ContentGenerationError, AuthenticationError

def test_agent_raises_auth_error_on_invalid_key(monkeypatch):
    """Test that agent raises AuthenticationError for invalid API key"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "invalid_key")

    agent = BaseAgent("test_agent")

    with pytest.raises(AuthenticationError) as exc_info:
        agent.generate_content("test prompt")

    assert exc_info.value.error_code == "API_003"
    assert "authentication failed" in exc_info.value.message.lower()


def test_agent_handles_empty_prompt():
    """Test that agent raises ValidationError for empty prompt"""
    agent = BaseAgent("test_agent")

    with pytest.raises(ValidationError) as exc_info:
        agent.generate_content("")

    assert exc_info.value.error_code == "DATA_001"
    assert exc_info.value.details["field"] == "prompt"
```

### Integration Testing Error Scenarios

```python
def test_retry_logic_succeeds_after_rate_limit():
    """Test that retry logic succeeds after temporary rate limit"""
    call_count = 0

    def mock_api_call():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RateLimitError(retry_after=1)
        return "success"

    result = retry_with_backoff(
        mock_api_call,
        max_attempts=3,
        base_delay=0.1  # Short delay for testing
    )

    assert result == "success"
    assert call_count == 3
```

## Error Monitoring and Alerting

### Error Metrics to Track

1. **Error Rate**: Percentage of requests that result in errors
2. **Error Distribution**: Count of each error type/code
3. **Mean Time to Recovery**: Average time from error to resolution
4. **Retry Success Rate**: Percentage of retries that eventually succeed

### Structured Error Logging for Monitoring

```python
def log_error_for_monitoring(error: BusinessOSError, context: dict = None):
    """Log error in structured format for monitoring systems"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error.__class__.__name__,
        "error_code": error.error_code,
        "error_message": error.message,
        "error_details": error.details,
        "context": context or {}
    }

    # Log as JSON for easy parsing by monitoring tools
    logger.error(json.dumps(log_entry))
```

## Best Practices Summary

1. ✅ **Always use typed exceptions** instead of generic `Exception`
2. ✅ **Include context** in exception details for debugging
3. ✅ **Log before raising** for critical errors
4. ✅ **Use appropriate log levels** consistently
5. ✅ **Implement retry logic** for transient failures (API rate limits, network issues)
6. ✅ **Validate input early** to fail fast
7. ✅ **Never expose stack traces** to end users in production
8. ✅ **Provide actionable error messages** with suggestions
9. ✅ **Test error paths** as thoroughly as success paths
10. ✅ **Monitor error rates** to detect issues proactively

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Anthropic API Error Handling](https://docs.anthropic.com/claude/reference/errors)
- Architecture Documentation: `docs/ARCHITECTURE.md`
- Testing Guide: `docs/TESTING_GUIDE.md`
