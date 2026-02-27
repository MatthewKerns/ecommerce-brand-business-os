"""
Integration tests for citation monitoring API endpoints.

Tests cover:
- Test query endpoint (testing AI assistant citations)
- Citations retrieval endpoint
- Recommendations retrieval endpoint
- Alerts retrieval endpoint
- Request validation
- Error handling
- Response structure
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

from api.main import app


class TestCitationMonitoringTestQuery:
    """Test suite for /api/citation-monitoring/test-query endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_agent(self):
        """Mock CitationMonitoringAgent for testing"""
        with patch('api.routes.citation_monitoring.CitationMonitoringAgent') as mock_agent_class:
            mock_agent = Mock()

            # Mock get_available_platforms
            mock_agent.get_available_platforms.return_value = ["chatgpt", "claude", "perplexity"]

            # Mock query_ai_assistant response
            mock_agent.query_ai_assistant.return_value = {
                "choices": [{"message": {"content": "BattlBox is a great tactical gear subscription box."}}]
            }

            # Mock analyze_citation response
            mock_agent.analyze_citation.return_value = {
                "brand_mentioned": True,
                "citation_context": "...BattlBox is a great tactical gear subscription box...",
                "position_in_response": 1,
                "competitor_mentioned": False,
                "competitor_details": []
            }

            mock_agent_class.return_value = mock_agent
            yield mock_agent

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()
            mock_session.add = Mock()
            mock_session.flush = Mock()
            mock_session.commit = Mock()
            mock_session.close = Mock()
            mock_db.return_value = mock_session
            yield mock_session

    def test_test_query_success(self, client, mock_agent, mock_db_session):
        """Test successful query test with brand citation"""
        request_data = {
            "query": "What are the best tactical gear subscription boxes?",
            "platforms": ["chatgpt"],
            "brand_name": "BattlBox",
            "save_to_db": True
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "query" in data
        assert "results" in data
        assert "brand_name" in data
        assert "total_platforms" in data
        assert "citations_found" in data
        assert "citation_rate" in data
        assert "timestamp" in data
        assert "saved_to_db" in data

        assert data["query"] == request_data["query"]
        assert data["brand_name"] == "BattlBox"
        assert data["total_platforms"] == 1
        assert data["saved_to_db"] is True

    def test_test_query_minimal_request(self, client, mock_agent, mock_db_session):
        """Test query with minimal required fields using defaults"""
        request_data = {
            "query": "Best subscription boxes for outdoor enthusiasts"
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["brand_name"] == "BattlBox"
        assert data["total_platforms"] == 3  # Default platforms
        assert data["saved_to_db"] is True

    def test_test_query_multiple_platforms(self, client, mock_agent, mock_db_session):
        """Test query against multiple AI platforms"""
        request_data = {
            "query": "Top tactical subscription services",
            "platforms": ["chatgpt", "claude", "perplexity"],
            "brand_name": "BattlBox"
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["total_platforms"] == 3
        assert len(data["results"]) == 3

        # Verify all platforms were queried
        platforms_in_results = [r["platform"] for r in data["results"]]
        assert "chatgpt" in platforms_in_results
        assert "claude" in platforms_in_results
        assert "perplexity" in platforms_in_results

    def test_test_query_with_competitors(self, client, mock_agent, mock_db_session):
        """Test query with competitor tracking"""
        mock_agent.analyze_citation.return_value = {
            "brand_mentioned": True,
            "citation_context": "...BattlBox offers tactical gear...",
            "position_in_response": 2,
            "competitor_mentioned": True,
            "competitor_details": [
                {
                    "competitor_name": "Carnivore Club",
                    "mentioned": True,
                    "citation_context": "...Carnivore Club is another option...",
                    "position_in_response": 1
                }
            ]
        }

        request_data = {
            "query": "Compare tactical gear subscription boxes",
            "platforms": ["chatgpt"],
            "brand_name": "BattlBox",
            "competitor_names": ["Carnivore Club", "Tactical Gear Box"]
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify competitors were tracked
        result = data["results"][0]
        assert "competitors_mentioned" in result
        assert "Carnivore Club" in result["competitors_mentioned"]

    def test_test_query_with_custom_request_id(self, client, mock_agent, mock_db_session):
        """Test query with custom request ID in header"""
        request_data = {
            "query": "Best tactical subscription boxes"
        }

        response = client.post(
            "/api/citation-monitoring/test-query",
            json=request_data,
            headers={"X-Request-ID": "custom-test-123"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "custom-test-123"

    def test_test_query_citation_rate_calculation(self, client, mock_agent, mock_db_session):
        """Test that citation rate is calculated correctly"""
        # Mock different results for different platforms
        citation_count = 0

        def mock_analyze(query, response_text, platform, brand_name, **kwargs):
            nonlocal citation_count
            citation_count += 1
            # First two platforms mention brand, third doesn't
            return {
                "brand_mentioned": citation_count <= 2,
                "citation_context": "...BattlBox..." if citation_count <= 2 else None,
                "position_in_response": 1 if citation_count <= 2 else None,
                "competitor_mentioned": False,
                "competitor_details": []
            }

        mock_agent.analyze_citation.side_effect = mock_analyze

        request_data = {
            "query": "Tactical gear subscriptions",
            "platforms": ["chatgpt", "claude", "perplexity"]
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["total_platforms"] == 3
        assert data["citations_found"] == 2
        assert abs(data["citation_rate"] - 0.67) < 0.01  # 2/3 ≈ 0.67

    def test_test_query_without_saving_to_db(self, client, mock_agent):
        """Test query without saving results to database"""
        request_data = {
            "query": "Best tactical subscription boxes",
            "platforms": ["chatgpt"],
            "save_to_db": False
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["saved_to_db"] is False

    def test_test_query_invalid_platform(self, client, mock_agent):
        """Test validation error for invalid platform"""
        request_data = {
            "query": "Test query for invalid platform",
            "platforms": ["invalid_platform"]
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "InvalidPlatformsError"
        assert "available_platforms" in data["detail"]

    def test_test_query_invalid_query_too_short(self, client):
        """Test validation error for query that's too short"""
        request_data = {
            "query": "Hi"  # Less than 5 characters
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_test_query_invalid_temperature(self, client):
        """Test validation error for invalid temperature"""
        request_data = {
            "query": "Test query for temperature validation",
            "temperature": 3.0  # Greater than max (2.0)
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_test_query_invalid_timeout(self, client):
        """Test validation error for invalid timeout"""
        request_data = {
            "query": "Test query for timeout validation",
            "timeout": 3  # Less than min (5)
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_test_query_missing_required_field(self, client):
        """Test validation error when required field is missing"""
        request_data = {
            "platforms": ["chatgpt"]
            # Missing required 'query' field
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_test_query_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.citation_monitoring.CitationMonitoringAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.get_available_platforms.return_value = ["chatgpt", "claude", "perplexity"]
            mock_agent.query_ai_assistant.side_effect = Exception("AI platform error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "query": "Test query for error handling",
                "platforms": ["chatgpt"]
            }

            response = client.post("/api/citation-monitoring/test-query", json=request_data)

            # Should handle gracefully and return result with error
            assert response.status_code == 200
            data = response.json()

            # Result should indicate error
            result = data["results"][0]
            assert result["brand_mentioned"] is False
            assert "Error" in result["response_text"]

    def test_test_query_response_structure(self, client, mock_agent, mock_db_session):
        """Test that response has correct structure"""
        request_data = {
            "query": "Best tactical subscription boxes",
            "platforms": ["chatgpt"]
        }

        response = client.post("/api/citation-monitoring/test-query", json=request_data)
        data = response.json()

        # Verify top-level structure
        assert isinstance(data["request_id"], str)
        assert isinstance(data["query"], str)
        assert isinstance(data["results"], list)
        assert isinstance(data["brand_name"], str)
        assert isinstance(data["total_platforms"], int)
        assert isinstance(data["citations_found"], int)
        assert isinstance(data["citation_rate"], float)
        assert isinstance(data["saved_to_db"], bool)

        # Verify result structure
        result = data["results"][0]
        assert "platform" in result
        assert "brand_mentioned" in result
        assert "citation_context" in result
        assert "position_in_response" in result
        assert "competitors_mentioned" in result
        assert "response_time_ms" in result
        assert "response_text" in result


class TestCitationMonitoringGetCitations:
    """Test suite for /api/citation-monitoring/citations endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with citation records"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()

            # Create mock citation records
            mock_record = Mock()
            mock_record.id = 1
            mock_record.query = "Test query"
            mock_record.ai_platform = "chatgpt"
            mock_record.brand_mentioned = True
            mock_record.citation_context = "...BattlBox offers..."
            mock_record.position_in_response = 1
            mock_record.competitor_mentioned = False
            mock_record.query_timestamp = datetime.utcnow()
            mock_record.response_time_ms = 2341

            # Mock query builder
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_record]

            mock_session.query.return_value = mock_query
            mock_session.close = Mock()
            mock_db.return_value = mock_session
            yield mock_session

    def test_get_citations_success(self, client, mock_db_session):
        """Test successful retrieval of citation records"""
        response = client.get("/api/citation-monitoring/citations")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "citations" in data
        assert "total_count" in data
        assert "filter_days" in data
        assert "filter_platform" in data
        assert "citation_rate" in data

    def test_get_citations_with_filters(self, client, mock_db_session):
        """Test citations retrieval with filters"""
        response = client.get(
            "/api/citation-monitoring/citations",
            params={
                "days": 7,
                "platform": "chatgpt",
                "brand_name": "BattlBox",
                "limit": 50
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["filter_days"] == 7
        assert data["filter_platform"] == "chatgpt"

    def test_get_citations_default_values(self, client, mock_db_session):
        """Test that default values are applied correctly"""
        response = client.get("/api/citation-monitoring/citations")

        assert response.status_code == 200
        data = response.json()

        # Default values
        assert data["filter_days"] == 30
        assert data["total_count"] >= 0

    def test_get_citations_citation_rate_calculation(self, client, mock_db_session):
        """Test that citation rate is calculated correctly"""
        response = client.get("/api/citation-monitoring/citations")

        assert response.status_code == 200
        data = response.json()

        # Verify citation rate calculation
        if data["total_count"] > 0:
            assert 0.0 <= data["citation_rate"] <= 1.0

    def test_get_citations_invalid_platform(self, client):
        """Test validation error for invalid platform"""
        response = client.get(
            "/api/citation-monitoring/citations",
            params={"platform": "invalid_platform"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_citations_invalid_days(self, client):
        """Test validation error for invalid days value"""
        response = client.get(
            "/api/citation-monitoring/citations",
            params={"days": 500}  # Greater than max (365)
        )

        assert response.status_code == 422  # Validation error

    def test_get_citations_invalid_limit(self, client):
        """Test validation error for invalid limit value"""
        response = client.get(
            "/api/citation-monitoring/citations",
            params={"limit": 5000}  # Greater than max (1000)
        )

        assert response.status_code == 422  # Validation error

    def test_get_citations_response_structure(self, client, mock_db_session):
        """Test that response has correct structure"""
        response = client.get("/api/citation-monitoring/citations")
        data = response.json()

        # Verify structure
        assert isinstance(data["request_id"], str)
        assert isinstance(data["citations"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["citation_rate"], float)

        # If citations exist, verify their structure
        if len(data["citations"]) > 0:
            citation = data["citations"][0]
            assert "id" in citation
            assert "query" in citation
            assert "ai_platform" in citation
            assert "brand_mentioned" in citation
            assert "query_timestamp" in citation

    def test_get_citations_database_error(self, client):
        """Test error handling when database query fails"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()
            mock_session.query.side_effect = Exception("Database error")
            mock_db.return_value = mock_session

            response = client.get("/api/citation-monitoring/citations")

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "CitationRetrievalError" in str(data["detail"])


class TestCitationMonitoringGetRecommendations:
    """Test suite for /api/citation-monitoring/recommendations endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with recommendation records"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()

            # Create mock recommendation records
            mock_record = Mock()
            mock_record.id = 1
            mock_record.recommendation_type = "content"
            mock_record.title = "Improve comparison content"
            mock_record.description = "Add detailed comparison tables"
            mock_record.priority = "high"
            mock_record.status = "pending"
            mock_record.ai_platform = "chatgpt"
            mock_record.expected_impact = 75
            mock_record.actual_impact = None
            mock_record.implementation_effort = "medium"
            mock_record.created_at = datetime.utcnow()

            # Mock query builder
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_record]

            mock_session.query.return_value = mock_query
            mock_session.close = Mock()
            mock_db.return_value = mock_session
            yield mock_session

    def test_get_recommendations_success(self, client, mock_db_session):
        """Test successful retrieval of recommendations"""
        response = client.get("/api/citation-monitoring/recommendations")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "recommendations" in data
        assert "total_count" in data
        assert "by_priority" in data
        assert "by_type" in data
        assert "by_status" in data

    def test_get_recommendations_with_filters(self, client, mock_db_session):
        """Test recommendations retrieval with filters"""
        response = client.get(
            "/api/citation-monitoring/recommendations",
            params={
                "days": 7,
                "platform": "chatgpt",
                "status": "pending",
                "priority": "high",
                "recommendation_type": "content",
                "limit": 50
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_count"] >= 0

    def test_get_recommendations_default_values(self, client, mock_db_session):
        """Test that default values are applied correctly"""
        response = client.get("/api/citation-monitoring/recommendations")

        assert response.status_code == 200
        data = response.json()

        # Verify statistics are present
        assert isinstance(data["by_priority"], dict)
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["by_status"], dict)

    def test_get_recommendations_statistics(self, client, mock_db_session):
        """Test that statistics are calculated correctly"""
        response = client.get("/api/citation-monitoring/recommendations")

        assert response.status_code == 200
        data = response.json()

        # Verify statistics structure
        by_priority = data["by_priority"]
        by_type = data["by_type"]
        by_status = data["by_status"]

        # All should be dictionaries
        assert isinstance(by_priority, dict)
        assert isinstance(by_type, dict)
        assert isinstance(by_status, dict)

    def test_get_recommendations_invalid_platform(self, client):
        """Test validation error for invalid platform"""
        response = client.get(
            "/api/citation-monitoring/recommendations",
            params={"platform": "invalid_platform"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_recommendations_invalid_status(self, client):
        """Test validation error for invalid status"""
        response = client.get(
            "/api/citation-monitoring/recommendations",
            params={"status": "invalid_status"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_recommendations_invalid_priority(self, client):
        """Test validation error for invalid priority"""
        response = client.get(
            "/api/citation-monitoring/recommendations",
            params={"priority": "urgent"}  # Not in allowed values
        )

        assert response.status_code == 422  # Validation error

    def test_get_recommendations_invalid_type(self, client):
        """Test validation error for invalid recommendation type"""
        response = client.get(
            "/api/citation-monitoring/recommendations",
            params={"recommendation_type": "invalid_type"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_recommendations_response_structure(self, client, mock_db_session):
        """Test that response has correct structure"""
        response = client.get("/api/citation-monitoring/recommendations")
        data = response.json()

        # Verify structure
        assert isinstance(data["request_id"], str)
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["by_priority"], dict)
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["by_status"], dict)

        # If recommendations exist, verify their structure
        if len(data["recommendations"]) > 0:
            rec = data["recommendations"][0]
            assert "id" in rec
            assert "recommendation_type" in rec
            assert "title" in rec
            assert "description" in rec
            assert "priority" in rec
            assert "status" in rec
            assert "created_at" in rec

    def test_get_recommendations_database_error(self, client):
        """Test error handling when database query fails"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()
            mock_session.query.side_effect = Exception("Database error")
            mock_db.return_value = mock_session

            response = client.get("/api/citation-monitoring/recommendations")

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "RecommendationRetrievalError" in str(data["detail"])


class TestCitationMonitoringGetAlerts:
    """Test suite for /api/citation-monitoring/alerts endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with alert records"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            from decimal import Decimal

            mock_session = Mock()

            # Create mock alert records
            mock_record = Mock()
            mock_record.id = 1
            mock_record.alert_type = "citation_drop"
            mock_record.alert_severity = "high"
            mock_record.status = "active"
            mock_record.title = "Citation rate dropped"
            mock_record.message = "Citation rate dropped from 75% to 45%"
            mock_record.brand_name = "BattlBox"
            mock_record.competitor_name = None
            mock_record.ai_platform = "chatgpt"
            mock_record.metric_name = "citation_rate"
            mock_record.previous_value = Decimal("0.75")
            mock_record.current_value = Decimal("0.45")
            mock_record.threshold_value = Decimal("0.20")
            mock_record.change_percentage = Decimal("-30.0")
            mock_record.triggered_at = datetime.utcnow()
            mock_record.acknowledged_at = None
            mock_record.resolved_at = None
            mock_record.dismissed_at = None

            # Mock query builder
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_record]

            mock_session.query.return_value = mock_query
            mock_session.close = Mock()
            mock_db.return_value = mock_session
            yield mock_session

    def test_get_alerts_success(self, client, mock_db_session):
        """Test successful retrieval of alert records"""
        response = client.get("/api/citation-monitoring/alerts")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "alerts" in data
        assert "total_count" in data
        assert "by_severity" in data
        assert "by_type" in data
        assert "by_status" in data
        assert "by_platform" in data
        assert "active_count" in data

    def test_get_alerts_with_filters(self, client, mock_db_session):
        """Test alerts retrieval with filters"""
        response = client.get(
            "/api/citation-monitoring/alerts",
            params={
                "days": 7,
                "severity": "high",
                "status": "active",
                "alert_type": "citation_drop",
                "platform": "chatgpt",
                "brand_name": "BattlBox",
                "limit": 50
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_count"] >= 0

    def test_get_alerts_default_values(self, client, mock_db_session):
        """Test that default values are applied correctly"""
        response = client.get("/api/citation-monitoring/alerts")

        assert response.status_code == 200
        data = response.json()

        # Verify statistics are present
        assert isinstance(data["by_severity"], dict)
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["by_status"], dict)
        assert isinstance(data["by_platform"], dict)
        assert isinstance(data["active_count"], int)

    def test_get_alerts_statistics(self, client, mock_db_session):
        """Test that statistics are calculated correctly"""
        response = client.get("/api/citation-monitoring/alerts")

        assert response.status_code == 200
        data = response.json()

        # Verify statistics structure
        assert isinstance(data["by_severity"], dict)
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["by_status"], dict)
        assert isinstance(data["by_platform"], dict)

        # Active count should match status count
        active_from_status = data["by_status"].get("active", 0)
        assert data["active_count"] == active_from_status

    def test_get_alerts_invalid_severity(self, client):
        """Test validation error for invalid severity"""
        response = client.get(
            "/api/citation-monitoring/alerts",
            params={"severity": "urgent"}  # Not in allowed values
        )

        assert response.status_code == 422  # Validation error

    def test_get_alerts_invalid_status(self, client):
        """Test validation error for invalid status"""
        response = client.get(
            "/api/citation-monitoring/alerts",
            params={"status": "invalid_status"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_alerts_invalid_alert_type(self, client):
        """Test validation error for invalid alert type"""
        response = client.get(
            "/api/citation-monitoring/alerts",
            params={"alert_type": "invalid_type"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_alerts_invalid_platform(self, client):
        """Test validation error for invalid platform"""
        response = client.get(
            "/api/citation-monitoring/alerts",
            params={"platform": "invalid_platform"}
        )

        assert response.status_code == 422  # Validation error

    def test_get_alerts_response_structure(self, client, mock_db_session):
        """Test that response has correct structure"""
        response = client.get("/api/citation-monitoring/alerts")
        data = response.json()

        # Verify structure
        assert isinstance(data["request_id"], str)
        assert isinstance(data["alerts"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["by_severity"], dict)
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["by_status"], dict)
        assert isinstance(data["by_platform"], dict)
        assert isinstance(data["active_count"], int)

        # If alerts exist, verify their structure
        if len(data["alerts"]) > 0:
            alert = data["alerts"][0]
            assert "id" in alert
            assert "alert_type" in alert
            assert "alert_severity" in alert
            assert "status" in alert
            assert "title" in alert
            assert "message" in alert
            assert "triggered_at" in alert

    def test_get_alerts_decimal_conversion(self, client, mock_db_session):
        """Test that Decimal values are properly converted to float"""
        response = client.get("/api/citation-monitoring/alerts")
        data = response.json()

        # If alerts exist with numeric fields, verify they're floats not strings
        if len(data["alerts"]) > 0:
            alert = data["alerts"][0]
            if alert.get("previous_value") is not None:
                assert isinstance(alert["previous_value"], float)
            if alert.get("current_value") is not None:
                assert isinstance(alert["current_value"], float)
            if alert.get("threshold_value") is not None:
                assert isinstance(alert["threshold_value"], float)
            if alert.get("change_percentage") is not None:
                assert isinstance(alert["change_percentage"], float)

    def test_get_alerts_database_error(self, client):
        """Test error handling when database query fails"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()
            mock_session.query.side_effect = Exception("Database error")
            mock_db.return_value = mock_session

            response = client.get("/api/citation-monitoring/alerts")

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "AlertRetrievalError" in str(data["detail"])


class TestCitationMonitoringAPIValidation:
    """Test suite for citation monitoring API request validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_json_body(self, client):
        """Test that invalid JSON returns proper error"""
        response = client.post(
            "/api/citation-monitoring/test-query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_empty_request_body(self, client):
        """Test that empty request body returns validation error"""
        response = client.post("/api/citation-monitoring/test-query", json={})

        assert response.status_code == 422

    def test_response_content_type(self, client):
        """Test that responses have correct content type"""
        with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
            mock_session = Mock()
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = []
            mock_session.query.return_value = mock_query
            mock_session.close = Mock()
            mock_db.return_value = mock_session

            response = client.get("/api/citation-monitoring/citations")

            assert "application/json" in response.headers["content-type"]

    def test_all_platforms_are_valid(self, client):
        """Test that all documented platforms are accepted"""
        with patch('api.routes.citation_monitoring.CitationMonitoringAgent') as mock_agent_class:
            with patch('api.routes.citation_monitoring.get_db_session') as mock_db:
                mock_agent = Mock()
                mock_agent.get_available_platforms.return_value = ["chatgpt", "claude", "perplexity"]
                mock_agent.query_ai_assistant.return_value = {"choices": [{"message": {"content": "test"}}]}
                mock_agent.analyze_citation.return_value = {
                    "brand_mentioned": False,
                    "citation_context": None,
                    "position_in_response": None,
                    "competitor_mentioned": False,
                    "competitor_details": []
                }
                mock_agent_class.return_value = mock_agent

                mock_session = Mock()
                mock_session.add = Mock()
                mock_session.flush = Mock()
                mock_session.commit = Mock()
                mock_session.close = Mock()
                mock_db.return_value = mock_session

                valid_platforms = ["chatgpt", "claude", "perplexity"]

                for platform in valid_platforms:
                    request_data = {
                        "query": f"Test query for {platform}",
                        "platforms": [platform]
                    }

                    response = client.post("/api/citation-monitoring/test-query", json=request_data)
                    assert response.status_code == 200
