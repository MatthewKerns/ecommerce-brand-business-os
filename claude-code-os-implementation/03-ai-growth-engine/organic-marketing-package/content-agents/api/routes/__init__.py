"""
API routes package.

This package contains all API route modules for the AI Content Agents service.
"""

from api.routes.blog import router as blog_router
from api.routes.social import router as social_router
from api.routes.amazon import router as amazon_router
from api.routes.competitor import router as competitor_router
from api.routes.tiktok_channels import router as tiktok_channels_router
from api.routes.tiktok_scheduling import router as tiktok_scheduling_router
from api.routes.aeo import router as aeo_router
from api.routes.citation_monitoring import router as citation_monitoring_router
from api.routes.seo import router as seo_router

__all__ = [
    "blog_router",
    "social_router",
    "amazon_router",
    "competitor_router",
    "tiktok_channels_router",
    "tiktok_scheduling_router",
    "aeo_router",
    "citation_monitoring_router",
    "seo_router"
]
