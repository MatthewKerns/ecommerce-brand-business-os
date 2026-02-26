"""
API routes package.

This package contains all API route modules for the AI Content Agents service.
"""

from api.routes.blog import router as blog_router

__all__ = ["blog_router"]
