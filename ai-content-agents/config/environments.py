"""
Environment-aware configuration management for AI Content Agents

Loads configuration from environment-specific .env files based on the
ENVIRONMENT variable (development, staging, or production).
"""
import os
from pathlib import Path
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "python-dotenv library is required. Install with: pip install python-dotenv"
    )


# Valid environment names
VALID_ENVIRONMENTS = ["development", "staging", "production"]
DEFAULT_ENVIRONMENT = "development"


def get_environment() -> str:
    """
    Get the current environment from the ENVIRONMENT variable.

    Returns:
        Environment name (development, staging, or production)
    """
    env = os.getenv("ENVIRONMENT", DEFAULT_ENVIRONMENT).lower()

    if env not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"Invalid environment '{env}'. Must be one of: {', '.join(VALID_ENVIRONMENTS)}"
        )

    return env


def get_env_file_path(environment: Optional[str] = None) -> Path:
    """
    Get the path to the environment-specific .env file.

    Args:
        environment: Environment name. If not provided, will be detected from
                    ENVIRONMENT variable.

    Returns:
        Path to the .env file for the specified environment
    """
    if environment is None:
        environment = get_environment()

    # Get the config directory (where this file is located)
    config_dir = Path(__file__).parent
    # Go up one level to ai-content-agents directory
    base_dir = config_dir.parent

    env_file = base_dir / f".env.{environment}"

    return env_file


def load_environment_config(environment: Optional[str] = None, override: bool = False) -> Dict[str, str]:
    """
    Load configuration from the appropriate environment-specific .env file.

    This function:
    1. Detects the current environment (or uses the provided one)
    2. Loads the corresponding .env file (.env.development, .env.staging, or .env.production)
    3. Returns a dictionary of the loaded configuration

    Args:
        environment: Environment name to load. If not provided, will be detected
                    from ENVIRONMENT variable (defaults to 'development').
        override: If True, override existing environment variables. If False,
                 existing environment variables take precedence.

    Returns:
        Dictionary containing the loaded configuration values

    Raises:
        ValueError: If an invalid environment is specified
        FileNotFoundError: If the environment-specific .env file doesn't exist

    Example:
        >>> # Load development config (default)
        >>> config = load_environment_config()
        >>>
        >>> # Load production config
        >>> config = load_environment_config("production")
    """
    if environment is None:
        environment = get_environment()

    env_file_path = get_env_file_path(environment)

    # Check if the file exists
    if not env_file_path.exists():
        raise FileNotFoundError(
            f"Environment configuration file not found: {env_file_path}\n"
            f"Please create it based on .env.example"
        )

    # Load the environment file
    load_dotenv(env_file_path, override=override)

    # Return a dictionary of loaded values
    # Note: We only return values that are actually in the .env file
    config = {}

    # Read the file to get the keys (not values, as those are now in os.environ)
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Parse key=value lines
            if '=' in line:
                key = line.split('=')[0].strip()
                # Get the value from environment (it's been loaded by load_dotenv)
                config[key] = os.getenv(key, "")

    return config


def is_development() -> bool:
    """Check if running in development environment."""
    return get_environment() == "development"


def is_staging() -> bool:
    """Check if running in staging environment."""
    return get_environment() == "staging"


def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment() == "production"


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a configuration value from the current environment.

    Ensures the environment config is loaded, then retrieves the value.

    Args:
        key: Configuration key to retrieve
        default: Default value if key is not found

    Returns:
        Configuration value or default
    """
    # Ensure environment config is loaded (idempotent operation)
    try:
        load_environment_config(override=False)
    except FileNotFoundError:
        # If no env file exists, just use what's in environment
        pass

    return os.getenv(key, default)
