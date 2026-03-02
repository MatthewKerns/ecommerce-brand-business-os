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
from api.routes.tiktok_affiliates import router as tiktok_affiliates_router
from api.routes.aeo import router as aeo_router
from api.routes.citation_monitoring import router as citation_monitoring_router
# from api.routes.seo import router as seo_router  # Temporarily disabled - missing KeywordResearchRequest
from api.routes.klaviyo import router as klaviyo_router
from api.routes.cart import router as cart_router
from api.routes.review import router as review_router
from api.routes.versions import router as versions_router
from api.routes.tasks import router as tasks_router

__all__ = [
    "blog_router",
    "social_router",
    "amazon_router",
    "competitor_router",
    "tiktok_channels_router",
    "tiktok_scheduling_router",
    "tiktok_affiliates_router",
    "aeo_router",
    "citation_monitoring_router",
    # "seo_router",  # Temporarily disabled
    "klaviyo_router",
    "cart_router",
    "review_router",
    "versions_router",
    "tasks_router"
]
