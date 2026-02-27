"""
Celery Application for Background Task Processing

This module initializes the Celery application for handling background tasks
such as abandoned cart recovery email sequences.
"""
import os
from celery import Celery
from pathlib import Path

# Determine the base directory
BASE_DIR = Path(__file__).parent

# Load environment variables
try:
    from config.environments import load_environment_config
    load_environment_config()
except (ImportError, FileNotFoundError):
    # Fall back to system environment if environments module doesn't exist
    from dotenv import load_dotenv
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)

# Create Celery application
app = Celery("content_agents")

# Load configuration from celery_config module
app.config_from_object("config.celery_config", namespace="CELERY")

# Auto-discover tasks in all apps
# This will automatically find tasks in tasks/ directory
app.autodiscover_tasks(["tasks"])


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery configuration"""
    print(f"Request: {self.request!r}")


if __name__ == "__main__":
    app.start()
