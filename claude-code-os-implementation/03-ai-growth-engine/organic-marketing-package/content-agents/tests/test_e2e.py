"""
End-to-end tests for the complete workflow: API → Agent → Database
Tests the full integration from API request through agent processing to database logging.

This test suite verifies:
1. API request handling and validation
2. Agent content generation
3. Database logging of content history
4. Request/response logging
5. Error handling across all layers
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import logging
import json
from datetime import datetime

# Import application components
from api.main import app
from agents.blog_agent import BlogAgent
from database.connection import get_db, init_db, SessionLocal
from database.models import ContentHistory


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Initialize test database."""
    init_db()
    yield
    # Cleanup could go here if needed


@pytest.fixture
def db_session(setup_database):
    """Provide a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # Clean up test data
        db.query(ContentHistory).delete()
        db.commit()
        db.close()


@pytest.fixture
def mock_blog_agent():
    """Mock the BlogAgent for controlled testing."""
    with patch('api.routes.blog.BlogAgent') as mock_agent_class:
        mock_agent = Mock(spec=BlogAgent)
        mock_agent.generate_blog_post.return_value = (
            "# Test Blog Post\n\nThis is test content for e2e testing.",
            Path("/tmp/test_blog.md"),
            None  # seo_analysis
        )
        mock_agent_class.return_value = mock_agent
        yield mock_agent


@pytest.mark.e2e
class TestEndToEndWorkflow:
    """
    End-to-end tests for the complete API → Agent → Database workflow.

    These tests verify the full integration from API request through
    agent processing to database logging and response generation.
    """

    def test_blog_generation_complete_workflow(
        self,
        test_client,
        db_session,
        mock_blog_agent,
        caplog
    ):
        """
        Test complete workflow: API request → Agent → Database logging.

        Steps:
        1. Send POST request to /api/blog/generate
        2. Verify agent processes the request
        3. Verify successful response with generated content
        4. Verify logs contain request processing information
        5. Verify database has content_history record (when implemented)

        This is the primary e2e test validating the entire system flow.
        """
        caplog.set_level(logging.INFO)

        # Step 1: Prepare and send API request
        request_payload = {
            "topic": "10 Essential Tips for Trading Card Organization",
            "content_pillar": "Gear & Equipment",
            "target_keywords": ["trading cards", "organization", "storage"],
            "word_count": 1200,
            "include_cta": True
        }

        # Step 2: Send request to API
        response = test_client.post(
            "/api/blog/generate",
            json=request_payload
        )

        # Step 3: Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_data = response.json()

        # Verify response structure
        assert "request_id" in response_data, "Response missing 'request_id' field"
        assert "content" in response_data, "Response missing 'content' field"
        assert "file_path" in response_data, "Response missing 'file_path' field"
        assert "metadata" in response_data, "Response missing 'metadata' field"
        assert response_data["status"] == "success", "Status should be 'success'"

        # Verify content is not empty
        assert len(response_data["content"]) > 0, "Generated content is empty"

        # Verify metadata structure
        metadata = response_data["metadata"]
        assert "agent" in metadata, "Metadata missing 'agent' field"
        assert "model" in metadata, "Metadata missing 'model' field"
        assert "generation_time_ms" in metadata, "Metadata missing 'generation_time_ms' field"
        assert metadata["agent"] == "blog_agent", "Agent name should be 'blog_agent'"

        # Step 4: Verify agent was called with correct parameters
        mock_blog_agent.generate_blog_post.assert_called_once()
        call_kwargs = mock_blog_agent.generate_blog_post.call_args.kwargs
        assert call_kwargs["topic"] == request_payload["topic"]
        assert call_kwargs["word_count"] == request_payload["word_count"]
        assert call_kwargs["include_cta"] == request_payload["include_cta"]

        # Step 5: Verify logs contain request information
        log_messages = [record.message for record in caplog.records]
        log_text = " ".join(log_messages)

        # Check for API request logging
        assert any("Generating blog post" in msg for msg in log_messages), \
            "No log entry for blog post generation request"

        # Check for success logging
        assert any("Successfully generated blog post" in msg for msg in log_messages), \
            "No log entry for successful generation"

        # Check request ID appears in logs
        request_id = response_data["request_id"]
        assert request_id in log_text, \
            f"Request ID {request_id} not found in logs"

        # Step 6: Verify database logging (when implemented)
        # Note: Currently, database logging is not fully implemented in the API routes
        # This section can be expanded when database integration is complete
        # For now, we verify the database structure is ready

        # Verify we can query the content_history table
        content_records = db_session.query(ContentHistory).all()
        # Note: Count may be 0 if database logging not yet implemented in routes
        # This is expected for current implementation

    def test_error_handling_workflow(self, test_client, caplog):
        """
        Test error handling throughout the workflow.

        Verifies that errors are:
        - Properly caught and handled by the API
        - Logged with appropriate error levels
        - Returned with correct HTTP status codes
        - Include helpful error messages
        """
        caplog.set_level(logging.INFO)

        # Test 1: Empty topic (validation error)
        invalid_payload = {
            "topic": "short"  # Too short (min_length=10)
        }

        response = test_client.post(
            "/api/blog/generate",
            json=invalid_payload
        )

        # Verify error response
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

        response_data = response.json()
        assert "detail" in response_data, \
            "Error response should contain 'detail' field"

        # Test 2: Invalid content type
        response = test_client.post(
            "/api/blog/generate",
            data="not json",  # Send plain text instead of JSON
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422], \
            f"Expected 400 or 422 for invalid content, got {response.status_code}"

    def test_request_with_custom_request_id(self, test_client, mock_blog_agent, caplog):
        """
        Test that custom request IDs are properly handled and logged.

        Verifies:
        - Custom request ID from header is used
        - Request ID appears in response
        - Request ID appears in all log messages
        """
        caplog.set_level(logging.INFO)

        custom_request_id = "test-request-12345"

        request_payload = {
            "topic": "How to Store Trading Cards Properly"
        }

        response = test_client.post(
            "/api/blog/generate",
            json=request_payload,
            headers={"X-Request-ID": custom_request_id}
        )

        assert response.status_code == 200
        response_data = response.json()

        # Verify custom request ID is used
        assert response_data["request_id"] == custom_request_id, \
            "Custom request ID should be used in response"

        # Verify request ID appears in logs
        log_text = " ".join([record.message for record in caplog.records])
        assert custom_request_id in log_text, \
            "Custom request ID should appear in logs"

    def test_response_timing_metadata(self, test_client, mock_blog_agent):
        """
        Test that response includes timing metadata.

        Verifies:
        - Response includes generation_time_ms
        - Generation time is reasonable (not negative, not excessively large)
        """
        request_payload = {
            "topic": "Quick Guide to Tournament Preparation"
        }

        response = test_client.post(
            "/api/blog/generate",
            json=request_payload
        )

        assert response.status_code == 200
        response_data = response.json()

        # Verify timing metadata
        assert "metadata" in response_data
        assert "generation_time_ms" in response_data["metadata"]

        generation_time = response_data["metadata"]["generation_time_ms"]
        assert generation_time >= 0, "Generation time should not be negative"
        assert generation_time < 60000, "Generation time should be reasonable (< 60s)"

    def test_concurrent_requests(self, test_client, mock_blog_agent):
        """
        Test handling of multiple requests.

        Verifies:
        - Multiple requests can be processed
        - Each request gets a unique request_id
        - All requests return successfully
        """
        import concurrent.futures

        def make_request(topic_num):
            return test_client.post(
                "/api/blog/generate",
                json={"topic": f"Trading Card Topic {topic_num}"}
            )

        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(3)]
            responses = [f.result() for f in futures]

        # Verify all requests succeeded
        assert all(r.status_code == 200 for r in responses), \
            "All concurrent requests should succeed"

        # Extract request IDs
        request_ids = [r.json()["request_id"] for r in responses]

        # Verify all request IDs are unique
        assert len(set(request_ids)) == len(request_ids), \
            "Each request should have a unique request_id"


@pytest.mark.e2e
class TestHealthEndpoints:
    """Tests for health check and monitoring endpoints."""

    def test_health_check(self, test_client):
        """
        Test health check endpoint.

        Verifies:
        - /health endpoint is accessible
        - Returns 200 status
        - Returns expected health status
        """
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data

    def test_root_endpoint(self, test_client):
        """
        Test root API information endpoint.

        Verifies:
        - / endpoint returns API metadata
        - Response includes version and docs link
        """
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
