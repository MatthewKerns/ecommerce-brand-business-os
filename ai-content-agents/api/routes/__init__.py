"""
API routes package.

This package contains all API route modules for the AI Content Agents service.
"""

from api.routes.blog import router as blog_router
from api.routes.social import router as social_router
from api.routes.amazon import router as amazon_router
from api.routes.competitor import router as competitor_router

__all__ = [
    "blog_router",
    "social_router",
    "amazon_router",
    "competitor_router"
]
