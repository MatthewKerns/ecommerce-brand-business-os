"""
Integration tests for FastAPI application core endpoints.

Tests cover:
- Application initialization and startup
- Root endpoint
- Health check endpoint
- CORS middleware configuration
- Global exception handler
- OpenAPI documentation endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from datetime import datetime

from api.main import app


class TestApplicationSetup:
    """Test suite for application initialization and configuration"""

    def test_app_initialization(self):
        """Test that the FastAPI app initializes correctly"""
        assert app is not None
        assert app.title == "AI Content Agents API"
        assert app.version == "1.0.0"
        assert app.docs_url == "/api/docs"
        assert app.redoc_url == "/api/redoc"
        assert app.openapi_url == "/api/openapi.json"

    def test_app_has_routes(self):
        """Test that the app has expected routes registered"""
        routes = [route.path for route in app.routes]

        assert "/" in routes
        assert "/health" in routes

        # Check that route prefixes exist
        blog_routes = [r for r in routes if r.startswith("/api/blog")]
        social_routes = [r for r in routes if r.startswith("/api/social")]

        assert len(blog_routes) > 0
        assert len(social_routes) > 0

    def test_app_has_exception_handler(self):
        """Test that global exception handler is configured"""
        # The exception handler should be registered
        assert Exception in app.exception_handlers


class TestRootEndpoint:
    """Test suite for root endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_root_endpoint_success(self, client):
        """Test root endpoint returns correct information"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "AI Content Agents API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        assert data["docs"] == "/api/docs"

    def test_root_endpoint_response_structure(self, client):
        """Test that root endpoint returns expected keys"""
        response = client.get("/")
        data = response.json()

        expected_keys = {"service", "version", "status", "docs"}
        assert set(data.keys()) == expected_keys

    def test_root_endpoint_content_type(self, client):
        """Test that root endpoint returns JSON"""
        response = client.get("/")

        assert "application/json" in response.headers["content-type"]


class TestHealthCheckEndpoint:
    """Test suite for health check endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_health_check_success(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "ai-content-agents"
        assert "timestamp" in data

    def test_health_check_timestamp_format(self, client):
        """Test health check timestamp is in ISO format"""
        response = client.get("/health")
        data = response.json()

        # Verify timestamp is valid ISO format
        timestamp = data["timestamp"]
        assert timestamp.endswith("Z")

        # Should be able to parse the timestamp
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)

    def test_health_check_response_structure(self, client):
        """Test health check returns expected keys"""
        response = client.get("/health")
        data = response.json()

        expected_keys = {"status", "timestamp", "service"}
        assert set(data.keys()) == expected_keys

    def test_health_check_multiple_calls(self, client):
        """Test health check can be called multiple times"""
        # Make multiple requests to ensure consistency
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


class TestCORSMiddleware:
    """Test suite for CORS middleware configuration"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_cors_headers_on_root(self, client):
        """Test CORS headers are present on root endpoint"""
        response = client.get("/")

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight_request(self, client):
        """Test CORS preflight (OPTIONS) request"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Should allow CORS
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestGlobalExceptionHandler:
    """Test suite for global exception handler"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_exception_handler_structure(self, client):
        """Test that unhandled exceptions return proper error structure"""
        # Create a temporary route that raises an exception
        @app.get("/test-error")
        async def test_error():
            raise Exception("Test error")

        response = client.get("/test-error")

        # Should return 500 error
        assert response.status_code == 500
        data = response.json()

        # Should have expected error structure
        assert "error" in data
        assert "message" in data
        assert "timestamp" in data
        assert data["error"] == "InternalServerError"

    def test_404_on_unknown_route(self, client):
        """Test that unknown routes return 404"""
        response = client.get("/this-route-does-not-exist")

        assert response.status_code == 404


class TestOpenAPIDocumentation:
    """Test suite for OpenAPI documentation endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_openapi_json_endpoint(self, client):
        """Test that OpenAPI JSON is accessible"""
        response = client.get("/api/openapi.json")

        assert response.status_code == 200
        data = response.json()

        # Should have OpenAPI structure
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_swagger_ui_docs(self, client):
        """Test that Swagger UI docs are accessible"""
        response = client.get("/api/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_docs(self, client):
        """Test that ReDoc documentation is accessible"""
        response = client.get("/api/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_schema_has_routes(self, client):
        """Test that OpenAPI schema includes API routes"""
        response = client.get("/api/openapi.json")
        data = response.json()

        paths = data["paths"]

        # Should have blog routes
        assert any("/api/blog" in path for path in paths)

        # Should have social routes
        assert any("/api/social" in path for path in paths)


class TestStartupAndShutdown:
    """Test suite for application lifecycle events"""

    @patch('api.main.logger')
    def test_startup_event_logging(self, mock_logger):
        """Test that startup event logs appropriately"""
        # Create a new test client to trigger startup
        with TestClient(app) as client:
            # Verify health check works after startup
            response = client.get("/health")
            assert response.status_code == 200

        # Startup logging should have occurred
        mock_logger.info.assert_any_call("AI Content Agents API starting up...")

    @patch('api.main.logger')
    def test_shutdown_event_logging(self, mock_logger):
        """Test that shutdown event logs appropriately"""
        # Create and close client to trigger shutdown
        with TestClient(app):
            pass

        # Shutdown logging should have occurred
        mock_logger.info.assert_any_call("AI Content Agents API shutting down...")
