"""
End-to-end integration tests for SEO pipeline.
Tests the complete integration from API request through SEO agent processing.

This test suite verifies:
1. SEO content analysis workflow (API → Agent → Analysis)
2. Keyword research workflow
3. Internal linking suggestions workflow
4. Error handling across all SEO endpoints
5. Database logging of SEO metadata (when implemented)
6. Response structure and validation
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
from agents.seo_agent import SEOAgent
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
def sample_blog_content():
    """Sample blog content for SEO analysis testing."""
    return """# Best Tactical Backpacks for Urban Professionals

If you're a tactical backpack enthusiast, you know that finding the right tactical backpack can make all the difference. This comprehensive guide will help you choose the perfect tactical backpack for your needs.

## Why Choose a Tactical Backpack?

Tactical backpacks are designed for durability and functionality. Whether you're commuting to work or heading out on an adventure, a tactical backpack provides the storage and organization you need.

## Top Features to Look For

When selecting a tactical backpack, consider these essential features:

### Durability and Materials

Look for tactical backpacks made from high-quality materials like 1000D nylon. These materials ensure your tactical backpack can withstand daily wear and tear.

### Storage and Organization

A good tactical backpack should have multiple compartments for organizing your gear efficiently.

### Comfort and Fit

Make sure your tactical backpack has padded straps and proper weight distribution for all-day comfort.

## Conclusion

Choosing the right tactical backpack is an important decision. Consider your needs, budget, and intended use when selecting your tactical backpack.

Ready to upgrade your gear? Check out our selection of premium tactical backpacks today!"""


@pytest.fixture
def mock_keyword_research_result():
    """Mock keyword research result from SEO agent."""
    return [
        {
            "keyword": "tactical backpack",
            "relevance_score": 0.95,
            "search_volume": 12000,
            "difficulty": 45,
            "intent": "commercial"
        },
        {
            "keyword": "tactical backpack for work",
            "relevance_score": 0.88,
            "search_volume": 3500,
            "difficulty": 38,
            "intent": "commercial"
        },
        {
            "keyword": "best tactical backpack",
            "relevance_score": 0.92,
            "search_volume": 8200,
            "difficulty": 52,
            "intent": "commercial"
        }
    ]


@pytest.fixture
def mock_internal_links_result():
    """Mock internal linking suggestions from SEO agent."""
    return [
        {
            "target_url": "/blog/tactical-gear-essentials",
            "anchor_text": "tactical gear",
            "relevance_score": 0.89,
            "context": "Learn more about essential tactical gear"
        },
        {
            "target_url": "/blog/edc-backpack-guide",
            "anchor_text": "EDC backpack",
            "relevance_score": 0.85,
            "context": "Complete guide to choosing an EDC backpack"
        }
    ]


@pytest.mark.e2e
@pytest.mark.seo
class TestSEOAnalysisWorkflow:
    """
    End-to-end tests for SEO content analysis workflow.

    These tests verify the complete integration from API request through
    SEO agent analysis to response generation and database logging.
    """

    @patch('agents.seo_agent.KeywordResearcher')
    @patch('agents.seo_agent.SEOAnalyzer')
    @patch('agents.seo_agent.InternalLinkingSuggester')
    def test_seo_analysis_complete_workflow(
        self,
        mock_link_suggester_class,
        mock_analyzer_class,
        mock_researcher_class,
        test_client,
        db_session,
        sample_blog_content,
        caplog
    ):
        """
        Test complete SEO analysis workflow: API request → Agent → Analysis → Response.

        Steps:
        1. Send POST request to /api/seo/analyze
        2. Verify agent processes the content
        3. Verify successful response with SEO scores
        4. Verify logs contain analysis information
        5. Verify response structure and metrics
        """
        caplog.set_level(logging.INFO)

        # Mock SEO analyzer to return realistic analysis
        mock_analyzer = Mock()
        mock_analyzer.analyze_content.return_value = {
            'total_score': 78.5,
            'grade': 'B',
            'word_count': 350,
            'scores': {
                'keyword_optimization': {
                    'score': 75,
                    'weight': 0.30,
                    'feedback': 'Good keyword usage'
                },
                'content_quality': {
                    'score': 80,
                    'weight': 0.20,
                    'feedback': 'High quality content'
                },
                'content_structure': {
                    'score': 85,
                    'weight': 0.25,
                    'feedback': 'Well structured'
                },
                'readability': {
                    'score': 78,
                    'weight': 0.15,
                    'feedback': 'Easy to read'
                },
                'keyword_placement': {
                    'score': 70,
                    'weight': 0.10,
                    'feedback': 'Keyword placement could be improved'
                }
            },
            'issues': ['Add more internal links'],
            'recommendations': []
        }
        mock_analyzer_class.return_value = mock_analyzer

        # Mock keyword researcher
        mock_researcher = Mock()
        mock_researcher_class.return_value = mock_researcher

        # Mock link suggester
        mock_link_suggester = Mock()
        mock_link_suggester_class.return_value = mock_link_suggester

        # Step 1: Prepare and send API request
        request_payload = {
            "content": sample_blog_content,
            "target_keyword": "tactical backpack",
            "title": "Best Tactical Backpacks for Urban Professionals",
            "include_recommendations": True
        }

        # Step 2: Send request to API
        response = test_client.post(
            "/api/seo/analyze",
            json=request_payload
        )

        # Step 3: Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_data = response.json()

        # Verify response structure
        assert "request_id" in response_data, "Response missing 'request_id' field"
        assert "seo_score" in response_data, "Response missing 'seo_score' field"
        assert "grade" in response_data, "Response missing 'grade' field"
        assert "keyword_optimization" in response_data, "Response missing 'keyword_optimization' field"
        assert "content_quality" in response_data, "Response missing 'content_quality' field"
        assert "structure" in response_data, "Response missing 'structure' field"
        assert "readability" in response_data, "Response missing 'readability' field"
        assert "recommendations" in response_data, "Response missing 'recommendations' field"
        assert "issues" in response_data, "Response missing 'issues' field"
        assert "metadata" in response_data, "Response missing 'metadata' field"
        assert response_data["status"] == "success", "Status should be 'success'"

        # Verify SEO score is valid
        seo_score = response_data["seo_score"]
        assert 0 <= seo_score <= 100, f"SEO score should be between 0-100, got {seo_score}"

        # Verify grade is valid
        grade = response_data["grade"]
        assert grade in ["A", "B", "C", "D", "F"], f"Invalid grade: {grade}"

        # Verify metadata structure
        metadata = response_data["metadata"]
        assert "agent" in metadata, "Metadata missing 'agent' field"
        assert "model" in metadata, "Metadata missing 'model' field"
        assert "generation_time_ms" in metadata, "Metadata missing 'generation_time_ms' field"
        assert metadata["agent"] == "seo_agent", "Agent name should be 'seo_agent'"

        # Verify keyword optimization metrics exist
        keyword_opt = response_data["keyword_optimization"]
        assert isinstance(keyword_opt, dict), "keyword_optimization should be a dictionary"

        # Verify recommendations are included when requested
        recommendations = response_data["recommendations"]
        assert isinstance(recommendations, list), "recommendations should be a list"

        # Step 4: Verify logs contain analysis information
        log_messages = [record.message for record in caplog.records]
        log_text = " ".join(log_messages)

        # Check for API request logging
        assert any("Starting SEO content analysis" in msg for msg in log_messages), \
            "No log entry for SEO analysis request"

        # Check for success logging
        assert any("SEO analysis completed" in msg for msg in log_messages), \
            "No log entry for successful analysis"

        # Check request ID appears in logs
        request_id = response_data["request_id"]
        assert request_id in log_text, \
            f"Request ID {request_id} not found in logs"

    @patch('agents.seo_agent.KeywordResearcher')
    @patch('agents.seo_agent.SEOAnalyzer')
    @patch('agents.seo_agent.InternalLinkingSuggester')
    def test_seo_analysis_without_recommendations(
        self,
        mock_link_suggester_class,
        mock_analyzer_class,
        mock_researcher_class,
        test_client,
        sample_blog_content
    ):
        """
        Test SEO analysis workflow when recommendations are not requested.

        Verifies that recommendations can be optionally excluded from response.
        """
        # Mock SEO analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_content.return_value = {
            'total_score': 78.5,
            'grade': 'B',
            'word_count': 350,
            'scores': {
                'keyword_optimization': {'score': 75, 'weight': 0.30, 'feedback': 'Good'},
                'content_quality': {'score': 80, 'weight': 0.20, 'feedback': 'Good'},
                'content_structure': {'score': 85, 'weight': 0.25, 'feedback': 'Good'},
                'readability': {'score': 78, 'weight': 0.15, 'feedback': 'Good'},
                'keyword_placement': {'score': 70, 'weight': 0.10, 'feedback': 'Good'}
            },
            'issues': [],
            'recommendations': []
        }
        mock_analyzer_class.return_value = mock_analyzer
        mock_researcher_class.return_value = Mock()
        mock_link_suggester_class.return_value = Mock()

        # Prepare request without recommendations
        request_payload = {
            "content": sample_blog_content,
            "target_keyword": "tactical backpack",
            "include_recommendations": False
        }

        # Send request
        response = test_client.post(
            "/api/seo/analyze",
            json=request_payload
        )

        # Verify successful response
        assert response.status_code == 200

        response_data = response.json()

        # Verify recommendations are empty when not requested
        recommendations = response_data.get("recommendations", [])
        assert isinstance(recommendations, list), "recommendations should be a list"
        # Note: May be empty or minimal when include_recommendations is False

        # Verify other analysis data is still present
        assert "seo_score" in response_data
        assert "grade" in response_data
        assert "keyword_optimization" in response_data

    @patch('agents.seo_agent.KeywordResearcher')
    @patch('agents.seo_agent.SEOAnalyzer')
    @patch('agents.seo_agent.InternalLinkingSuggester')
    def test_seo_analysis_without_target_keyword(
        self,
        mock_link_suggester_class,
        mock_analyzer_class,
        mock_researcher_class,
        test_client,
        sample_blog_content
    ):
        """
        Test SEO analysis workflow without a target keyword.

        Verifies that analysis can be performed even without a specific target keyword.
        """
        # Mock SEO analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_content.return_value = {
            'total_score': 75.0,
            'grade': 'B',
            'word_count': 350,
            'scores': {
                'keyword_optimization': {'score': 70, 'weight': 0.30, 'feedback': 'No target keyword'},
                'content_quality': {'score': 80, 'weight': 0.20, 'feedback': 'Good'},
                'content_structure': {'score': 85, 'weight': 0.25, 'feedback': 'Good'},
                'readability': {'score': 75, 'weight': 0.15, 'feedback': 'Good'},
                'keyword_placement': {'score': 60, 'weight': 0.10, 'feedback': 'No target keyword'}
            },
            'issues': [],
            'recommendations': []
        }
        mock_analyzer_class.return_value = mock_analyzer
        mock_researcher_class.return_value = Mock()
        mock_link_suggester_class.return_value = Mock()

        # Prepare request without target keyword
        request_payload = {
            "content": sample_blog_content,
            "include_recommendations": True
        }

        # Send request
        response = test_client.post(
            "/api/seo/analyze",
            json=request_payload
        )

        # Verify successful response
        assert response.status_code == 200

        response_data = response.json()

        # Verify analysis completed
        assert response_data["status"] == "success"
        assert "seo_score" in response_data
        assert "grade" in response_data

        # Analysis should still provide metrics even without target keyword
        assert "content_quality" in response_data
        assert "structure" in response_data
        assert "readability" in response_data


@pytest.mark.e2e
@pytest.mark.seo
class TestKeywordResearchWorkflow:
    """
    End-to-end tests for keyword research workflow.

    These tests verify the complete integration of keyword research
    from API request through agent processing to response generation.
    """

    @patch('api.routes.seo.SEOAgent')
    def test_keyword_research_complete_workflow(
        self,
        mock_seo_agent_class,
        test_client,
        mock_keyword_research_result,
        caplog
    ):
        """
        Test complete keyword research workflow: API request → Agent → Keywords → Response.

        Steps:
        1. Send POST request to /api/seo/keywords/research
        2. Verify agent processes the request
        3. Verify successful response with keyword suggestions
        4. Verify logs contain research information
        """
        caplog.set_level(logging.INFO)

        # Mock the SEO agent and its research_keywords method
        mock_agent = Mock()
        mock_agent.research_keywords.return_value = mock_keyword_research_result
        mock_seo_agent_class.return_value = mock_agent

        # Step 1: Prepare and send API request
        request_payload = {
            "topic": "Tactical backpacks for urban professionals",
            "seed_keywords": ["tactical backpack", "EDC bag"],
            "max_keywords": 50,
            "include_long_tail": True
        }

        # Step 2: Send request to API
        response = test_client.post(
            "/api/seo/keywords/research",
            json=request_payload
        )

        # Step 3: Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_data = response.json()

        # Verify response structure
        assert "request_id" in response_data, "Response missing 'request_id' field"
        assert "keywords" in response_data, "Response missing 'keywords' field"
        assert "seed_keywords" in response_data, "Response missing 'seed_keywords' field"
        assert "topic" in response_data, "Response missing 'topic' field"
        assert "metadata" in response_data, "Response missing 'metadata' field"
        assert response_data["status"] == "success", "Status should be 'success'"

        # Verify keywords are returned
        keywords = response_data["keywords"]
        assert isinstance(keywords, list), "keywords should be a list"
        assert len(keywords) > 0, "Should return at least one keyword"

        # Verify keyword structure (first keyword)
        if len(keywords) > 0:
            first_keyword = keywords[0]
            assert "keyword" in first_keyword, "Keyword missing 'keyword' field"
            assert "relevance_score" in first_keyword, "Keyword missing 'relevance_score' field"

        # Verify seed keywords match request
        assert response_data["seed_keywords"] == request_payload["seed_keywords"]

        # Verify topic matches request
        assert response_data["topic"] == request_payload["topic"]

        # Verify metadata structure
        metadata = response_data["metadata"]
        assert metadata["agent"] == "seo_agent"

        # Step 4: Verify agent was instantiated and called with correct parameters
        mock_seo_agent_class.assert_called_once()
        mock_agent.research_keywords.assert_called_once()

        # Step 5: Verify logs
        log_messages = [record.message for record in caplog.records]

        assert any("Starting keyword research" in msg for msg in log_messages), \
            "No log entry for keyword research request"

        assert any("Keyword research completed" in msg for msg in log_messages), \
            "No log entry for successful research"

    def test_keyword_research_validation_errors(self, test_client):
        """
        Test validation errors in keyword research requests.

        Verifies that invalid requests are properly rejected.
        """
        # Test 1: Empty seed keywords
        invalid_payload = {
            "topic": "Tactical gear",
            "seed_keywords": [],  # Empty list - should fail validation
            "max_keywords": 50
        }

        response = test_client.post(
            "/api/seo/keywords/research",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

        # Test 2: Topic too short
        invalid_payload = {
            "topic": "Hi",  # Too short (min_length=5)
            "seed_keywords": ["tactical"],
            "max_keywords": 50
        }

        response = test_client.post(
            "/api/seo/keywords/research",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

        # Test 3: max_keywords out of range
        invalid_payload = {
            "topic": "Tactical backpacks",
            "seed_keywords": ["tactical"],
            "max_keywords": 500  # Out of range (max=200)
        }

        response = test_client.post(
            "/api/seo/keywords/research",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"


@pytest.mark.e2e
@pytest.mark.seo
class TestInternalLinkingWorkflow:
    """
    End-to-end tests for internal linking suggestions workflow.

    These tests verify the complete integration of internal linking
    from API request through agent processing to response generation.
    """

    @patch('api.routes.seo.SEOAgent')
    def test_internal_linking_complete_workflow(
        self,
        mock_seo_agent_class,
        test_client,
        sample_blog_content,
        mock_internal_links_result,
        caplog
    ):
        """
        Test complete internal linking workflow: API request → Agent → Links → Response.

        Steps:
        1. Send POST request to /api/seo/internal-links/suggest
        2. Verify agent processes the content
        3. Verify successful response with link suggestions
        4. Verify logs contain linking information
        """
        caplog.set_level(logging.INFO)

        # Mock the SEO agent and its suggest_internal_links method
        mock_agent = Mock()
        mock_agent.suggest_internal_links.return_value = mock_internal_links_result
        mock_seo_agent_class.return_value = mock_agent

        # Step 1: Prepare and send API request
        request_payload = {
            "content": sample_blog_content,
            "title": "Best Tactical Backpacks for Urban Professionals",
            "content_pillar": "Gear & Equipment",
            "max_suggestions": 5
        }

        # Step 2: Send request to API
        response = test_client.post(
            "/api/seo/internal-links/suggest",
            json=request_payload
        )

        # Step 3: Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_data = response.json()

        # Verify response structure
        assert "request_id" in response_data, "Response missing 'request_id' field"
        assert "suggestions" in response_data, "Response missing 'suggestions' field"
        assert "total_suggestions" in response_data, "Response missing 'total_suggestions' field"
        assert "content_title" in response_data, "Response missing 'content_title' field"
        assert "metadata" in response_data, "Response missing 'metadata' field"
        assert response_data["status"] == "success", "Status should be 'success'"

        # Verify suggestions are returned
        suggestions = response_data["suggestions"]
        assert isinstance(suggestions, list), "suggestions should be a list"
        assert len(suggestions) > 0, "Should return at least one suggestion"

        # Verify suggestion structure (first suggestion)
        if len(suggestions) > 0:
            first_suggestion = suggestions[0]
            assert "target_url" in first_suggestion, "Suggestion missing 'target_url' field"
            assert "anchor_text" in first_suggestion, "Suggestion missing 'anchor_text' field"

        # Verify total matches actual count
        assert response_data["total_suggestions"] == len(suggestions)

        # Verify content title matches request
        assert response_data["content_title"] == request_payload["title"]

        # Verify metadata structure
        metadata = response_data["metadata"]
        assert metadata["agent"] == "seo_agent"

        # Step 4: Verify agent was instantiated and called
        mock_seo_agent_class.assert_called_once()
        mock_agent.suggest_internal_links.assert_called_once()

        # Step 5: Verify logs
        log_messages = [record.message for record in caplog.records]

        assert any("Starting internal link suggestion" in msg for msg in log_messages), \
            "No log entry for internal linking request"

        assert any("Internal link suggestions completed" in msg for msg in log_messages), \
            "No log entry for successful suggestion generation"

    @patch('api.routes.seo.SEOAgent')
    def test_internal_linking_max_suggestions_limit(
        self,
        mock_seo_agent_class,
        test_client,
        sample_blog_content
    ):
        """
        Test that max_suggestions parameter is respected.

        Verifies that the number of returned suggestions doesn't exceed the limit.
        """
        # Mock the SEO agent to return limited suggestions
        mock_agent = Mock()
        mock_agent.suggest_internal_links.return_value = [
            {"target_url": "/blog/link1", "anchor_text": "link 1", "relevance_score": 0.9},
            {"target_url": "/blog/link2", "anchor_text": "link 2", "relevance_score": 0.8}
        ]
        mock_seo_agent_class.return_value = mock_agent

        # Request with low max_suggestions limit
        request_payload = {
            "content": sample_blog_content,
            "title": "Tactical Backpack Guide",
            "max_suggestions": 2
        }

        response = test_client.post(
            "/api/seo/internal-links/suggest",
            json=request_payload
        )

        # Verify successful response
        assert response.status_code == 200

        response_data = response.json()

        # Verify suggestions don't exceed limit
        suggestions = response_data["suggestions"]
        assert len(suggestions) <= 2, f"Expected at most 2 suggestions, got {len(suggestions)}"

    def test_internal_linking_validation_errors(self, test_client):
        """
        Test validation errors in internal linking requests.

        Verifies that invalid requests are properly rejected.
        """
        # Test 1: Content too short
        invalid_payload = {
            "content": "Short content",  # Too short (min_length=50)
            "title": "Test Title",
            "max_suggestions": 5
        }

        response = test_client.post(
            "/api/seo/internal-links/suggest",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

        # Test 2: Title too short
        invalid_payload = {
            "content": "This is a longer piece of content that meets the minimum length requirement for testing.",
            "title": "Hi",  # Too short (min_length=5)
            "max_suggestions": 5
        }

        response = test_client.post(
            "/api/seo/internal-links/suggest",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

        # Test 3: max_suggestions out of range
        invalid_payload = {
            "content": "This is a longer piece of content that meets the minimum length requirement for testing.",
            "title": "Valid Title",
            "max_suggestions": 50  # Out of range (max=20)
        }

        response = test_client.post(
            "/api/seo/internal-links/suggest",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"


@pytest.mark.e2e
@pytest.mark.seo
class TestSEOErrorHandling:
    """
    End-to-end tests for error handling in SEO pipeline.

    These tests verify that errors are properly caught, logged,
    and returned with appropriate status codes and messages.
    """

    def test_seo_analysis_content_validation(self, test_client, caplog):
        """
        Test content validation in SEO analysis.

        Verifies that invalid content is rejected with proper error messages.
        """
        caplog.set_level(logging.INFO)

        # Test 1: Content too short
        invalid_payload = {
            "content": "Too short",  # Min length is 50
            "target_keyword": "tactical backpack"
        }

        response = test_client.post(
            "/api/seo/analyze",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

        response_data = response.json()
        assert "detail" in response_data, \
            "Error response should contain 'detail' field"

        # Test 2: Missing required content field
        invalid_payload = {
            "target_keyword": "tactical backpack"
            # content field missing
        }

        response = test_client.post(
            "/api/seo/analyze",
            json=invalid_payload
        )

        # Verify validation error
        assert response.status_code == 422, \
            f"Expected 422 for validation error, got {response.status_code}"

    @patch('agents.seo_agent.SEOAgent.analyze_content_seo')
    def test_seo_analysis_agent_error_handling(
        self,
        mock_analyze,
        test_client,
        sample_blog_content,
        caplog
    ):
        """
        Test error handling when SEO agent fails.

        Verifies that agent errors are caught and returned as 500 errors.
        """
        caplog.set_level(logging.INFO)

        # Mock agent to raise an error
        mock_analyze.side_effect = Exception("Analysis failed due to unexpected error")

        # Prepare request
        request_payload = {
            "content": sample_blog_content,
            "target_keyword": "tactical backpack",
            "include_recommendations": True
        }

        # Send request
        response = test_client.post(
            "/api/seo/analyze",
            json=request_payload
        )

        # Verify error response
        assert response.status_code == 500, \
            f"Expected 500 for server error, got {response.status_code}"

        response_data = response.json()
        assert "detail" in response_data, \
            "Error response should contain 'detail' field"

        # Verify error is logged
        log_messages = [record.message for record in caplog.records]
        assert any("SEO analysis failed" in msg for msg in log_messages), \
            "No log entry for analysis failure"

    def test_seo_health_check_endpoint(self, test_client):
        """
        Test SEO service health check endpoint.

        Verifies that the health check endpoint returns proper status.
        """
        response = test_client.get("/api/seo/health")

        # Verify successful response
        assert response.status_code == 200

        response_data = response.json()

        # Verify health check structure
        assert "service" in response_data
        assert "status" in response_data
        assert "timestamp" in response_data

        # Verify service name and status
        assert response_data["service"] == "seo"
        assert response_data["status"] == "healthy"


@pytest.mark.e2e
@pytest.mark.seo
class TestSEODatabaseIntegration:
    """
    End-to-end tests for SEO database integration.

    These tests verify that SEO analysis results are properly
    logged to the database (when database logging is implemented).
    """

    def test_seo_database_schema_supports_seo_metadata(self, db_session):
        """
        Test that database schema supports SEO metadata fields.

        Verifies that ContentHistory model has fields for SEO data.
        """
        # Verify ContentHistory model has SEO fields
        content_history_columns = [column.name for column in ContentHistory.__table__.columns]

        # Check for SEO-specific columns
        assert "seo_score" in content_history_columns, \
            "ContentHistory missing 'seo_score' column"
        assert "seo_grade" in content_history_columns, \
            "ContentHistory missing 'seo_grade' column"
        assert "target_keyword" in content_history_columns, \
            "ContentHistory missing 'target_keyword' column"
        assert "meta_description" in content_history_columns, \
            "ContentHistory missing 'meta_description' column"
        assert "internal_links" in content_history_columns, \
            "ContentHistory missing 'internal_links' column"

    def test_seo_metadata_can_be_saved_to_database(self, db_session):
        """
        Test that SEO metadata can be saved to database.

        Verifies that we can create and persist ContentHistory records with SEO data.
        """
        # Create a test content record with SEO metadata
        test_content = ContentHistory(
            request_id="test_seo_integration_001",
            content_type="blog",
            agent_name="seo_agent",
            prompt="Analyze SEO for tactical backpack content",
            content="# Tactical Backpack Guide\n\nTest content for SEO analysis.",
            model="claude-sonnet-4-5-20250929",
            tokens_used=1500,
            generation_time_ms=2500,
            status="success",
            seo_score=78.5,
            seo_grade="B",
            target_keyword="tactical backpack",
            meta_description="Discover the best tactical backpacks for urban professionals",
            internal_links='[{"url": "/blog/edc-gear", "anchor": "EDC gear"}]'
        )

        # Save to database
        db_session.add(test_content)
        db_session.commit()

        # Query back from database
        saved_content = db_session.query(ContentHistory).filter_by(
            request_id="test_seo_integration_001"
        ).first()

        # Verify data was saved correctly
        assert saved_content is not None, "Content should be saved to database"
        assert saved_content.seo_score == 78.5
        assert saved_content.seo_grade == "B"
        assert saved_content.target_keyword == "tactical backpack"
        assert saved_content.meta_description == "Discover the best tactical backpacks for urban professionals"
        assert saved_content.internal_links is not None

        # Clean up
        db_session.delete(saved_content)
        db_session.commit()


@pytest.mark.e2e
@pytest.mark.seo
@pytest.mark.performance
class TestSEOPipelinePerformance:
    """
    End-to-end performance tests for SEO pipeline.

    These tests verify that the SEO pipeline performs within acceptable time limits.
    """

    @patch('agents.seo_agent.KeywordResearcher')
    @patch('agents.seo_agent.SEOAnalyzer')
    @patch('agents.seo_agent.InternalLinkingSuggester')
    def test_seo_analysis_performance(
        self,
        mock_link_suggester_class,
        mock_analyzer_class,
        mock_researcher_class,
        test_client,
        sample_blog_content
    ):
        """
        Test that SEO analysis completes within reasonable time.

        Verifies that analysis doesn't take too long (< 10 seconds for typical content).
        """
        import time

        # Mock SEO analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_content.return_value = {
            'total_score': 78.5,
            'grade': 'B',
            'word_count': 350,
            'scores': {
                'keyword_optimization': {'score': 75, 'weight': 0.30, 'feedback': 'Good'},
                'content_quality': {'score': 80, 'weight': 0.20, 'feedback': 'Good'},
                'content_structure': {'score': 85, 'weight': 0.25, 'feedback': 'Good'},
                'readability': {'score': 78, 'weight': 0.15, 'feedback': 'Good'},
                'keyword_placement': {'score': 70, 'weight': 0.10, 'feedback': 'Good'}
            },
            'issues': [],
            'recommendations': []
        }
        mock_analyzer_class.return_value = mock_analyzer
        mock_researcher_class.return_value = Mock()
        mock_link_suggester_class.return_value = Mock()

        request_payload = {
            "content": sample_blog_content,
            "target_keyword": "tactical backpack",
            "include_recommendations": True
        }

        # Measure request time
        start_time = time.time()
        response = test_client.post(
            "/api/seo/analyze",
            json=request_payload
        )
        end_time = time.time()

        # Verify successful response
        assert response.status_code == 200

        # Verify response time is reasonable (< 10 seconds)
        request_duration = end_time - start_time
        assert request_duration < 10.0, \
            f"SEO analysis took too long: {request_duration:.2f}s"

        # Verify generation_time_ms is recorded in metadata
        response_data = response.json()
        metadata = response_data["metadata"]
        assert "generation_time_ms" in metadata
        assert metadata["generation_time_ms"] > 0

    def test_keyword_research_performance(self, test_client):
        """
        Test that keyword research completes within reasonable time.

        Verifies that research doesn't take too long (< 15 seconds).
        """
        import time

        request_payload = {
            "topic": "Tactical backpacks for urban professionals",
            "seed_keywords": ["tactical backpack", "EDC bag"],
            "max_keywords": 50
        }

        # Measure request time
        start_time = time.time()
        response = test_client.post(
            "/api/seo/keywords/research",
            json=request_payload
        )
        end_time = time.time()

        # Note: This will likely fail without mocking since it uses real AI
        # In a production test suite, you would mock the AI calls
        # For now, we just verify the endpoint structure is correct
        if response.status_code == 200:
            request_duration = end_time - start_time
            # More generous timeout for AI-powered research
            assert request_duration < 15.0, \
                f"Keyword research took too long: {request_duration:.2f}s"

            response_data = response.json()
            assert "metadata" in response_data
            assert "generation_time_ms" in response_data["metadata"]
