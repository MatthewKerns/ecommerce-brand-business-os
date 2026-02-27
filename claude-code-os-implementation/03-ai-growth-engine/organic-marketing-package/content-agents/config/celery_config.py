"""
Celery Configuration for Background Task Processing
"""
import os

# Broker and Backend Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Timezone Configuration
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Task Configuration
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Result Configuration
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_RESULT_PERSISTENT = True

# Task Routing
CELERY_TASK_ROUTES = {
    "tasks.cart_recovery.*": {"queue": "cart_recovery"},
}

# Worker Configuration
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Beat Schedule (Periodic Tasks)
CELERY_BEAT_SCHEDULE = {
    "process-abandoned-carts": {
        "task": "tasks.cart_recovery.process_abandoned_carts",
        "schedule": 300.0,  # Run every 5 minutes (300 seconds)
        "options": {
            "queue": "cart_recovery",
            "expires": 240.0,  # Task expires after 4 minutes if not picked up
        }
    },
}

# Logging Configuration
CELERY_WORKER_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
CELERY_WORKER_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s"
