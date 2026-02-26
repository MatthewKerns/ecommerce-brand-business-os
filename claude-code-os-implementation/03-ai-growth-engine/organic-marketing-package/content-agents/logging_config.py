"""
Centralized logging configuration for AI Content Agents

This module provides a standardized logging setup with both file and console handlers,
following the error handling and logging standards defined in docs/ERROR_HANDLING.md.
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Base paths
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Track initialized loggers to avoid duplicate handlers
_initialized_loggers = set()


def get_logger(
    name: str,
    log_level: str = "INFO",
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """
    Get or create a configured logger instance with file and console handlers

    Args:
        name: Logger name (will be prefixed with 'business_os.')
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Optional custom log directory (defaults to logs/)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger('blog_agent')
        >>> logger.info('Content generation started')
        >>> logger.error('API request failed', exc_info=True)
    """
    # Create logger with business_os prefix
    logger_name = f"business_os.{name}" if name else "business_os"
    logger = logging.getLogger(logger_name)

    # Avoid adding duplicate handlers
    if logger_name in _initialized_loggers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper()))

    # Determine log directory
    target_log_dir = log_dir or LOGS_DIR
    target_log_dir.mkdir(parents=True, exist_ok=True)

    # File handler with date-stamped filename (DEBUG level for detailed logs)
    log_file = target_log_dir / f"{name or 'app'}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler (INFO level for less verbose output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Structured format with timestamp, logger name, level, message, function, and line number
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(funcName)s:%(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Mark as initialized
    _initialized_loggers.add(logger_name)

    return logger


def setup_logging(
    log_dir: Path,
    log_level: str = "INFO",
    agent_name: Optional[str] = None
) -> logging.Logger:
    """
    Configure structured logging for agents (legacy function for compatibility)

    This function is provided for backwards compatibility with the pattern
    shown in docs/ERROR_HANDLING.md. New code should use get_logger().

    Args:
        log_dir: Directory to store log files
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        agent_name: Optional agent name for logger identification

    Returns:
        Configured logger instance
    """
    return get_logger(
        name=agent_name or "app",
        log_level=log_level,
        log_dir=log_dir
    )
