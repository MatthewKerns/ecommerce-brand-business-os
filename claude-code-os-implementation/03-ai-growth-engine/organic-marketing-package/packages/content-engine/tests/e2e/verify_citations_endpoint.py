#!/usr/bin/env python3
"""
Verify the GET /citations endpoint exists and can be imported.
"""

import sys
import os

# Add the content-agents directory to the path
content_agents_dir = os.path.join(
    os.path.dirname(__file__),
    'claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents'
)
sys.path.insert(0, content_agents_dir)

def verify_citations_endpoint():
    """Verify the citations endpoint exists."""
    try:
        # Import the router
        from api.routes.citation_monitoring import router

        # Check router exists
        assert router is not None, "Router is None"

        # Check prefix
        assert router.prefix == "/citation-monitoring", f"Expected prefix '/citation-monitoring', got '{router.prefix}'"

        # Check that the GET /citations endpoint exists
        route_paths = [route.path for route in router.routes]

        # The path should be /citations (prefix is added by main.py)
        assert "/citations" in route_paths, f"GET /citations endpoint not found. Available paths: {route_paths}"

        # Find the citations route and check it's a GET endpoint
        citations_route = None
        for route in router.routes:
            if route.path == "/citations":
                citations_route = route
                break

        assert citations_route is not None, "Citations route not found"
        assert "GET" in citations_route.methods, f"Expected GET method, got {citations_route.methods}"

        print("✓ Citations endpoint verified successfully!")
        print(f"  - Router prefix: {router.prefix}")
        print(f"  - Endpoint path: /citations")
        print(f"  - HTTP method: GET")
        print(f"  - Full URL: /api/citation-monitoring/citations")
        print(f"  - Response model: CitationListResponse")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Assertion error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_citations_endpoint()
    sys.exit(0 if success else 1)
