"""
Dependency Injection

Dependency injection container and setup.
"""

from .container import DIContainer, DIModule
from .setup import (
    VideoGenerationModule,
    setup_di_container,
    create_video_generation_service,
)

__all__ = [
    'DIContainer',
    'DIModule',
    'VideoGenerationModule',
    'setup_di_container',
    'create_video_generation_service',
]