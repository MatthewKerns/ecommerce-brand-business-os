"""
Integration tests for AEO API endpoints.

Tests cover:
- FAQ content generation endpoint
- FAQ schema generation endpoint
- Product schema generation endpoint
- AI-optimized content generation endpoint
- Comparison content generation endpoint
- Health check endpoint
- Request validation
- Error handling
- Response structure
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from pathlib import Path
from datetime import datetime

from api.main import app
from agents.aeo_agent import AEOAgent


class TestFAQGeneration:
    """Test suite for /api/aeo/generate-faq endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_aeo_agent(self):
        """Mock AEOAgent for testing"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock(spec=AEOAgent)
            mock_agent.generate_faq_content.return_value = (
                "# Frequently Asked Questions\n\nQ: Test question?\nA: Test answer.",
                Path("/tmp/test_faq.md")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_faq_success(self, client, mock_aeo_agent):
        """Test successful FAQ content generation"""
        request_data = {
            "topic": "Trading Card Storage and Protection",
            "num_questions": 10,
            "target_audience": "Competitive TCG players",
            "include_product_mentions": True
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_faq_minimal_request(self, client, mock_aeo_agent):
        """Test FAQ generation with minimal required fields"""
        request_data = {
            "topic": "Card Protection Basics"
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["status"] == "success"

        # Verify agent was called with defaults
        mock_aeo_agent.generate_faq_content.assert_called_once()
        call_kwargs = mock_aeo_agent.generate_faq_content.call_args.kwargs

        assert call_kwargs["topic"] == "Card Protection Basics"
        assert call_kwargs["num_questions"] == 10  # Default value
        assert call_kwargs["target_audience"] == "TCG players and collectors"  # Default value
        assert call_kwargs["include_product_mentions"] is True  # Default value

    def test_generate_faq_with_custom_request_id(self, client, mock_aeo_agent):
        """Test FAQ generation with custom request ID in header"""
        request_data = {
            "topic": "Tournament Preparation FAQs"
        }

        response = client.post(
            "/api/aeo/generate-faq",
            json=request_data,
            headers={"X-Request-ID": "custom-faq-123"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "custom-faq-123"

    def test_generate_faq_metadata_structure(self, client, mock_aeo_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "topic": "Card Organization Tips"
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "aeo_agent"
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_faq_invalid_topic_too_short(self, client):
        """Test validation error for topic that's too short"""
        request_data = {
            "topic": "Short"  # Less than 10 characters
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_faq_invalid_num_questions_too_few(self, client):
        """Test validation error for too few questions"""
        request_data = {
            "topic": "Card Storage Questions",
            "num_questions": 2  # Less than minimum (3)
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_faq_invalid_num_questions_too_many(self, client):
        """Test validation error for too many questions"""
        request_data = {
            "topic": "Comprehensive FAQ Collection",
            "num_questions": 30  # More than maximum (25)
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_faq_missing_required_field(self, client):
        """Test validation error when required field is missing"""
        request_data = {
            "num_questions": 10
            # Missing required 'topic' field
        }

        response = client.post("/api/aeo/generate-faq", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_faq_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_faq_content.side_effect = Exception("Agent error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test Topic for Error Handling"
            }

            response = client.post("/api/aeo/generate-faq", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "FAQGenerationError" in str(data["detail"])


class TestFAQSchemaGeneration:
    """Test suite for /api/aeo/generate-faq-schema endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_aeo_agent(self):
        """Mock AEOAgent for testing"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock(spec=AEOAgent)
            mock_agent.generate_faq_schema.return_value = '{"@context": "https://schema.org", "@type": "FAQPage"}'
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_faq_schema_success(self, client, mock_aeo_agent):
        """Test successful FAQ schema generation"""
        request_data = {
            "faq_items": [
                {
                    "question": "What is the best way to store trading cards?",
                    "answer": "The best way to store trading cards is using archival-quality sleeves and binders."
                },
                {
                    "question": "How do I protect expensive cards?",
                    "answer": "Expensive cards should be double-sleeved and stored in rigid holders."
                }
            ]
        }

        response = client.post("/api/aeo/generate-faq-schema", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "schema" in data
        assert "schema_type" in data
        assert "metadata" in data
        assert data["status"] == "success"
        assert data["schema_type"] == "FAQPage"

    def test_generate_faq_schema_metadata_structure(self, client, mock_aeo_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "faq_items": [
                {
                    "question": "Test question?",
                    "answer": "Test answer."
                }
            ]
        }

        response = client.post("/api/aeo/generate-faq-schema", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "aeo_agent"
        assert metadata["tokens_used"] == 0  # No tokens for schema generation
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_faq_schema_with_custom_request_id(self, client, mock_aeo_agent):
        """Test FAQ schema generation with custom request ID in header"""
        request_data = {
            "faq_items": [
                {
                    "question": "What is AEO?",
                    "answer": "AEO stands for Answer Engine Optimization."
                }
            ]
        }

        response = client.post(
            "/api/aeo/generate-faq-schema",
            json=request_data,
            headers={"X-Request-ID": "custom-schema-456"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "custom-schema-456"

    def test_generate_faq_schema_empty_list(self, client):
        """Test validation error for empty FAQ items list"""
        request_data = {
            "faq_items": []
        }

        response = client.post("/api/aeo/generate-faq-schema", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_faq_schema_missing_required_field(self, client):
        """Test validation error when required field is missing"""
        request_data = {}  # Missing required 'faq_items' field

        response = client.post("/api/aeo/generate-faq-schema", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_faq_schema_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_faq_schema.side_effect = Exception("Schema generation error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "faq_items": [
                    {
                        "question": "Test question?",
                        "answer": "Test answer."
                    }
                ]
            }

            response = client.post("/api/aeo/generate-faq-schema", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "FAQSchemaGenerationError" in str(data["detail"])


class TestProductSchemaGeneration:
    """Test suite for /api/aeo/generate-product-schema endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_aeo_agent(self):
        """Mock AEOAgent for testing"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock(spec=AEOAgent)
            mock_agent.generate_product_schema.return_value = '{"@context": "https://schema.org", "@type": "Product"}'
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_product_schema_success(self, client, mock_aeo_agent):
        """Test successful Product schema generation"""
        request_data = {
            "product_data": {
                "name": "Infinity Vault Premium Card Binder",
                "description": "Professional-grade trading card binder with 400-card capacity",
                "price": "49.99",
                "priceCurrency": "USD",
                "brand": "Infinity Vault",
                "image": "https://example.com/images/premium-binder.jpg",
                "sku": "IV-BINDER-400",
                "availability": "https://schema.org/InStock"
            }
        }

        response = client.post("/api/aeo/generate-product-schema", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "schema" in data
        assert "schema_type" in data
        assert "metadata" in data
        assert data["status"] == "success"
        assert data["schema_type"] == "Product"

    def test_generate_product_schema_minimal_data(self, client, mock_aeo_agent):
        """Test Product schema generation with minimal product data"""
        request_data = {
            "product_data": {
                "name": "Basic Card Sleeve",
                "price": "9.99"
            }
        }

        response = client.post("/api/aeo/generate-product-schema", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["schema_type"] == "Product"

    def test_generate_product_schema_with_ratings(self, client, mock_aeo_agent):
        """Test Product schema generation with aggregate ratings"""
        request_data = {
            "product_data": {
                "name": "Premium Deck Box",
                "description": "Ultra-durable deck box",
                "price": "24.99",
                "priceCurrency": "USD",
                "brand": "Infinity Vault",
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": 4.8,
                    "reviewCount": 127
                }
            }
        }

        response = client.post("/api/aeo/generate-product-schema", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

        # Verify agent was called with ratings data
        mock_aeo_agent.generate_product_schema.assert_called_once()
        call_kwargs = mock_aeo_agent.generate_product_schema.call_args.kwargs
        assert "aggregateRating" in call_kwargs["product_data"]

    def test_generate_product_schema_metadata_structure(self, client, mock_aeo_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "product_data": {
                "name": "Test Product",
                "price": "19.99"
            }
        }

        response = client.post("/api/aeo/generate-product-schema", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "aeo_agent"
        assert metadata["tokens_used"] == 0  # No tokens for schema generation
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_product_schema_missing_required_field(self, client):
        """Test validation error when required field is missing"""
        request_data = {}  # Missing required 'product_data' field

        response = client.post("/api/aeo/generate-product-schema", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_product_schema_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_product_schema.side_effect = Exception("Product schema error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "product_data": {
                    "name": "Error Test Product",
                    "price": "9.99"
                }
            }

            response = client.post("/api/aeo/generate-product-schema", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "ProductSchemaGenerationError" in str(data["detail"])


class TestAIOptimizedContentGeneration:
    """Test suite for /api/aeo/generate-ai-content endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_aeo_agent(self):
        """Mock AEOAgent for testing"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock(spec=AEOAgent)
            mock_agent.generate_ai_optimized_content.return_value = (
                "# AI-Optimized Content\n\nThis is content optimized for AI assistants.",
                Path("/tmp/test_ai_content.md")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_ai_optimized_content_success(self, client, mock_aeo_agent):
        """Test successful AI-optimized content generation"""
        request_data = {
            "question": "How do I organize a large trading card collection?",
            "content_type": "guide",
            "include_sources": True
        }

        response = client.post("/api/aeo/generate-ai-content", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_ai_optimized_content_minimal_request(self, client, mock_aeo_agent):
        """Test AI content generation with minimal required fields"""
        request_data = {
            "question": "What are the best card sleeves for tournament play?"
        }

        response = client.post("/api/aeo/generate-ai-content", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["status"] == "success"

        # Verify agent was called with defaults
        mock_aeo_agent.generate_ai_optimized_content.assert_called_once()
        call_kwargs = mock_aeo_agent.generate_ai_optimized_content.call_args.kwargs

        assert call_kwargs["question"] == "What are the best card sleeves for tournament play?"
        assert call_kwargs["content_type"] == "guide"  # Default value
        assert call_kwargs["include_sources"] is True  # Default value

    def test_generate_ai_optimized_content_all_content_types(self, client, mock_aeo_agent):
        """Test that all valid content types are accepted"""
        valid_types = ["guide", "article", "comparison", "tutorial"]

        for content_type in valid_types:
            request_data = {
                "question": f"Test question for {content_type}",
                "content_type": content_type
            }

            response = client.post("/api/aeo/generate-ai-content", json=request_data)
            assert response.status_code == 200

    def test_generate_ai_optimized_content_invalid_content_type(self, client):
        """Test validation error for invalid content type"""
        request_data = {
            "question": "Test question with invalid type",
            "content_type": "invalid"  # Not in allowed values
        }

        response = client.post("/api/aeo/generate-ai-content", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_ai_optimized_content_invalid_question_too_short(self, client):
        """Test validation error for question that's too short"""
        request_data = {
            "question": "Short"  # Less than 10 characters
        }

        response = client.post("/api/aeo/generate-ai-content", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_ai_optimized_content_metadata_structure(self, client, mock_aeo_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "question": "How do I protect my card collection from damage?"
        }

        response = client.post("/api/aeo/generate-ai-content", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "aeo_agent"
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_ai_optimized_content_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_ai_optimized_content.side_effect = Exception("Content generation error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "question": "Test question for error handling"
            }

            response = client.post("/api/aeo/generate-ai-content", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "AIContentGenerationError" in str(data["detail"])


class TestComparisonContentGeneration:
    """Test suite for /api/aeo/generate-comparison endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_aeo_agent(self):
        """Mock AEOAgent for testing"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock(spec=AEOAgent)
            mock_agent.generate_comparison_content.return_value = (
                "# Comparison: Test Topic\n\nComparing items...",
                Path("/tmp/test_comparison.md")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_comparison_content_success(self, client, mock_aeo_agent):
        """Test successful comparison content generation"""
        request_data = {
            "comparison_topic": "TCG Storage Solutions",
            "items_to_compare": [
                "Card binders",
                "Storage boxes",
                "Deck boxes",
                "Card sleeves"
            ],
            "include_recommendation": True
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_comparison_content_minimal_request(self, client, mock_aeo_agent):
        """Test comparison content generation with minimal required fields"""
        request_data = {
            "comparison_topic": "Best Card Sleeves",
            "items_to_compare": [
                "Standard sleeves",
                "Premium sleeves"
            ]
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["status"] == "success"

        # Verify agent was called with defaults
        mock_aeo_agent.generate_comparison_content.assert_called_once()
        call_kwargs = mock_aeo_agent.generate_comparison_content.call_args.kwargs

        assert call_kwargs["comparison_topic"] == "Best Card Sleeves"
        assert call_kwargs["items_to_compare"] == ["Standard sleeves", "Premium sleeves"]
        assert call_kwargs["include_recommendation"] is True  # Default value

    def test_generate_comparison_content_invalid_topic_too_short(self, client):
        """Test validation error for topic that's too short"""
        request_data = {
            "comparison_topic": "Short",  # Less than 10 characters
            "items_to_compare": ["Item 1", "Item 2"]
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_comparison_content_invalid_too_few_items(self, client):
        """Test validation error for too few items to compare"""
        request_data = {
            "comparison_topic": "Card Storage Comparison",
            "items_to_compare": ["Only one item"]  # Less than minimum (2)
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_comparison_content_invalid_too_many_items(self, client):
        """Test validation error for too many items to compare"""
        request_data = {
            "comparison_topic": "Extensive Storage Comparison",
            "items_to_compare": [f"Item {i}" for i in range(15)]  # More than maximum (10)
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_comparison_content_missing_required_fields(self, client):
        """Test validation error when required fields are missing"""
        request_data = {
            "comparison_topic": "Test Comparison"
            # Missing required 'items_to_compare' field
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_comparison_content_metadata_structure(self, client, mock_aeo_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "comparison_topic": "Binder vs Storage Box",
            "items_to_compare": ["Binders", "Storage boxes"]
        }

        response = client.post("/api/aeo/generate-comparison", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "aeo_agent"
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_comparison_content_with_custom_request_id(self, client, mock_aeo_agent):
        """Test comparison generation with custom request ID in header"""
        request_data = {
            "comparison_topic": "Card Protection Methods",
            "items_to_compare": ["Sleeves", "Top loaders", "Binders"]
        }

        response = client.post(
            "/api/aeo/generate-comparison",
            json=request_data,
            headers={"X-Request-ID": "custom-comparison-789"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "custom-comparison-789"

    def test_generate_comparison_content_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_comparison_content.side_effect = Exception("Comparison generation error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "comparison_topic": "Test Error Handling",
                "items_to_compare": ["Item 1", "Item 2"]
            }

            response = client.post("/api/aeo/generate-comparison", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "ComparisonGenerationError" in str(data["detail"])


class TestAEOHealthCheck:
    """Test suite for /api/aeo/health endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_health_check_success(self, client):
        """Test that health check endpoint returns success"""
        response = client.get("/api/aeo/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "timestamp" in data

        assert data["status"] == "healthy"
        assert data["service"] == "aeo"

    def test_health_check_response_content_type(self, client):
        """Test that health check response has correct content type"""
        response = client.get("/api/aeo/health")

        assert "application/json" in response.headers["content-type"]

    def test_health_check_timestamp_format(self, client):
        """Test that health check timestamp is properly formatted"""
        response = client.get("/api/aeo/health")
        data = response.json()

        timestamp = data["timestamp"]

        # Verify timestamp ends with Z (UTC indicator)
        assert timestamp.endswith("Z")

        # Verify timestamp can be parsed as ISO format
        # Remove the Z and parse
        datetime.fromisoformat(timestamp.rstrip("Z"))


class TestAEOAPIRequestValidation:
    """Test suite for AEO API request validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_json_body(self, client):
        """Test that invalid JSON returns proper error"""
        response = client.post(
            "/api/aeo/generate-faq",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_empty_request_body_faq(self, client):
        """Test that empty request body returns validation error"""
        response = client.post("/api/aeo/generate-faq", json={})

        assert response.status_code == 422

    def test_empty_request_body_schema(self, client):
        """Test that empty request body returns validation error for schema endpoint"""
        response = client.post("/api/aeo/generate-faq-schema", json={})

        assert response.status_code == 422

    def test_response_content_type(self, client):
        """Test that responses have correct content type"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_faq_content.return_value = (
                "Test content",
                Path("/tmp/test.md")
            )
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test Content Type Response"
            }

            response = client.post("/api/aeo/generate-faq", json=request_data)

            assert "application/json" in response.headers["content-type"]

    def test_custom_request_id_propagates_across_endpoints(self, client):
        """Test that custom request ID is respected across different endpoints"""
        with patch('api.routes.aeo.AEOAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_faq_content.return_value = (
                "FAQ content",
                Path("/tmp/faq.md")
            )
            mock_agent.generate_ai_optimized_content.return_value = (
                "AI content",
                Path("/tmp/ai.md")
            )
            mock_agent_class.return_value = mock_agent

            custom_id = "test-request-id-999"

            # Test FAQ endpoint
            response1 = client.post(
                "/api/aeo/generate-faq",
                json={"topic": "Test Topic 1"},
                headers={"X-Request-ID": custom_id}
            )
            assert response1.json()["request_id"] == custom_id

            # Test AI content endpoint with different custom ID
            custom_id2 = "test-request-id-888"
            response2 = client.post(
                "/api/aeo/generate-ai-content",
                json={"question": "Test question?"},
                headers={"X-Request-ID": custom_id2}
            )
            assert response2.json()["request_id"] == custom_id2
