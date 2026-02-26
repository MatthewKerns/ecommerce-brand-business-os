"""
Test that all API routes can be imported successfully.

This test ensures the route modules are properly structured and have no import errors.
"""

import pytest


def test_import_blog_router():
    """Test that blog router can be imported."""
    from api.routes.blog import router
    assert router is not None
    assert router.prefix == "/blog"


def test_import_social_router():
    """Test that social router can be imported."""
    from api.routes.social import router
    assert router is not None
    assert router.prefix == "/social"


def test_import_amazon_router():
    """Test that amazon router can be imported."""
    from api.routes.amazon import router
    assert router is not None
    assert router.prefix == "/amazon"


def test_import_competitor_router():
    """Test that competitor router can be imported."""
    from api.routes.competitor import router
    assert router is not None
    assert router.prefix == "/competitor"


def test_all_routers_from_routes_package():
    """Test that all routers can be imported from routes package."""
    from api.routes import (
        blog_router,
        social_router,
        amazon_router,
        competitor_router
    )

    assert blog_router is not None
    assert social_router is not None
    assert amazon_router is not None
    assert competitor_router is not None
