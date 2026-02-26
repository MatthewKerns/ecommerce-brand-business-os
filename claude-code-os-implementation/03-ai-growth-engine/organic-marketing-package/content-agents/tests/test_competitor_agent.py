"""
Unit tests for CompetitorAgent class.

Tests cover:
- Agent initialization
- Competitor listing analysis
- Competitor review analysis
- Multiple competitor comparison
- Content gap identification
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from agents.competitor_agent import CompetitorAgent
from config.config import (
    COMPETITOR_OUTPUT_DIR,
    DEFAULT_MODEL
)


class TestCompetitorAgentInitialization:
    """Test suite for CompetitorAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test CompetitorAgent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = CompetitorAgent()

        assert agent.agent_name == "competitor_agent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_inherits_from_base_agent(self, mock_anthropic_class, mock_anthropic_client):
        """Test that CompetitorAgent inherits from BaseAgent properly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = CompetitorAgent()

        # Verify it has BaseAgent methods
        assert hasattr(agent, 'generate_content')
        assert hasattr(agent, 'save_output')
        assert hasattr(agent, 'generate_and_save')
        assert hasattr(agent, '_build_system_prompt')


class TestAnalyzeCompetitorListing:
    """Test suite for competitor listing analysis"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_listing_basic(
        self, mock_anthropic_class, mock_competitor_client, temp_output_dir
    ):
        """Test basic competitor listing analysis"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_listing(
            competitor_name="CompetitorBrand",
            product_title="Card Storage Binder",
            bullet_points=["Holds cards", "Durable", "Affordable"],
            description="A basic card storage solution"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_competitor_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_listing_with_metrics(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test competitor listing analysis with price, rating, and reviews"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        price = 24.99
        rating = 4.5
        review_count = 1234

        content, path = agent.analyze_competitor_listing(
            competitor_name="TestBrand",
            product_title="Test Product",
            bullet_points=["Feature 1"],
            description="Description",
            price=price,
            rating=rating,
            review_count=review_count
        )

        # Verify metrics were included in prompt
        call_args = mock_competitor_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"${price}" in prompt
        assert f"{rating}/5 stars" in prompt
        assert str(review_count) in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_listing_metadata(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that competitor listing analysis saves correct metadata"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        competitor = "BrandX"
        price = 29.99
        rating = 4.2
        reviews = 500

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.analyze_competitor_listing(
                competitor_name=competitor,
                product_title="Test",
                bullet_points=["Test"],
                description="Test",
                price=price,
                rating=rating,
                review_count=reviews
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["competitor"] == competitor
            assert metadata["price"] == price
            assert metadata["rating"] == rating
            assert metadata["review_count"] == reviews

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_listing_uses_extended_tokens(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that competitor analysis uses 4096 tokens"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_listing(
            competitor_name="Test",
            product_title="Test",
            bullet_points=["Test"],
            description="Test"
        )

        # Verify max_tokens was set to 4096
        call_args = mock_competitor_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096


class TestAnalyzeCompetitorReviews:
    """Test suite for competitor review analysis"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_reviews_basic(
        self, mock_anthropic_class, mock_competitor_client, temp_output_dir
    ):
        """Test basic competitor review analysis"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_reviews(
            competitor_name="CompetitorBrand",
            positive_reviews=["Great quality", "Love it"],
            negative_reviews=["Too expensive", "Poor durability"]
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_reviews_includes_reviews(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that review analysis includes both positive and negative reviews"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        positive = ["Excellent product", "Highly recommended"]
        negative = ["Not durable", "Overpriced"]

        content, path = agent.analyze_competitor_reviews(
            competitor_name="TestBrand",
            positive_reviews=positive,
            negative_reviews=negative
        )

        # Verify reviews were included in prompt
        call_args = mock_competitor_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        for review in positive + negative:
            assert review in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_reviews_metadata(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that review analysis saves correct metadata"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        competitor = "BrandY"
        positive = ["Good", "Great"]
        negative = ["Bad"]

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.analyze_competitor_reviews(
                competitor_name=competitor,
                positive_reviews=positive,
                negative_reviews=negative
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["competitor"] == competitor
            assert metadata["positive_count"] == len(positive)
            assert metadata["negative_count"] == len(negative)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_reviews_uses_extended_tokens(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that review analysis uses 4096 tokens"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_reviews(
            competitor_name="Test",
            positive_reviews=["Test"],
            negative_reviews=["Test"]
        )

        # Verify max_tokens was set to 4096
        call_args = mock_competitor_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096


class TestCompareMultipleCompetitors:
    """Test suite for multiple competitor comparison"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_compare_multiple_competitors_basic(
        self, mock_anthropic_class, mock_competitor_client, temp_output_dir
    ):
        """Test basic multiple competitor comparison"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        competitors = [
            {
                "name": "Competitor A",
                "price": 19.99,
                "rating": 4.0,
                "positioning": "Budget",
                "key_features": "Basic storage",
                "weaknesses": "Low quality"
            },
            {
                "name": "Competitor B",
                "price": 39.99,
                "rating": 4.8,
                "positioning": "Premium",
                "key_features": "High-end materials",
                "weaknesses": "Expensive"
            }
        ]

        content, path = agent.compare_multiple_competitors(
            competitors=competitors
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_compare_multiple_competitors_includes_all_data(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that comparison includes all competitor data"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        competitors = [
            {
                "name": "Brand1",
                "price": 25.00,
                "rating": 4.5,
                "positioning": "Mid-tier",
                "key_features": "Features1",
                "weaknesses": "Weak1"
            }
        ]

        content, path = agent.compare_multiple_competitors(
            competitors=competitors
        )

        # Verify competitor data was included in prompt
        call_args = mock_competitor_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Brand1" in prompt
        assert "25.00" in prompt or "25.0" in prompt
        assert "4.5" in prompt
        assert "Mid-tier" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_compare_multiple_competitors_metadata(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that comparison saves correct metadata"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        competitors = [
            {"name": "A", "price": 20},
            {"name": "B", "price": 30}
        ]

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.compare_multiple_competitors(
                competitors=competitors
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["competitors_analyzed"] == ["A", "B"]
            assert metadata["num_competitors"] == 2

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_compare_multiple_competitors_uses_extended_tokens(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that comparison uses 4096 tokens"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.compare_multiple_competitors(
            competitors=[{"name": "Test"}]
        )

        # Verify max_tokens was set to 4096
        call_args = mock_competitor_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096


class TestIdentifyContentGaps:
    """Test suite for content gap identification"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_identify_content_gaps_basic(
        self, mock_anthropic_class, mock_competitor_client, temp_output_dir
    ):
        """Test basic content gap identification"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content_list = [
            {
                "competitor_name": "Competitor A",
                "content_type": "blog",
                "topic": "Card care tips"
            },
            {
                "competitor_name": "Competitor B",
                "content_type": "video",
                "topic": "Tournament prep"
            }
        ]

        content, path = agent.identify_content_gaps(
            competitor_content=content_list
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_identify_content_gaps_with_performance(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test content gap identification with performance data"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content_list = [
            {
                "competitor_name": "Brand A",
                "content_type": "blog",
                "topic": "Storage tips",
                "performance": "10K views"
            }
        ]

        content, path = agent.identify_content_gaps(
            competitor_content=content_list
        )

        # Verify performance data was included
        call_args = mock_competitor_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "10K views" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_identify_content_gaps_includes_all_content(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that content gap analysis includes all competitor content"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content_list = [
            {
                "competitor_name": "A",
                "content_type": "blog",
                "topic": "Topic 1"
            },
            {
                "competitor_name": "B",
                "content_type": "video",
                "topic": "Topic 2"
            }
        ]

        content, path = agent.identify_content_gaps(
            competitor_content=content_list
        )

        # Verify all content was included in prompt
        call_args = mock_competitor_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Topic 1" in prompt
        assert "Topic 2" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_identify_content_gaps_metadata(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that content gap analysis saves correct metadata"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content_list = [
            {"competitor_name": "A", "content_type": "blog", "topic": "T1"},
            {"competitor_name": "B", "content_type": "video", "topic": "T2"}
        ]

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.identify_content_gaps(
                competitor_content=content_list
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["content_pieces_analyzed"] == 2

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_identify_content_gaps_uses_extended_tokens(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that content gap analysis uses 4096 tokens"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.identify_content_gaps(
            competitor_content=[{"competitor_name": "Test", "content_type": "blog", "topic": "Test"}]
        )

        # Verify max_tokens was set to 4096
        call_args = mock_competitor_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_competitor_name(self, mock_anthropic_class, mock_competitor_client):
        """Test listing analysis with empty competitor name"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_listing(
            competitor_name="",
            product_title="Test",
            bullet_points=["Test"],
            description="Test"
        )

        # Should still generate content
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_bullet_points(self, mock_anthropic_class, mock_competitor_client):
        """Test listing analysis with empty bullet points"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_listing(
            competitor_name="Test",
            product_title="Test",
            bullet_points=[],
            description="Test"
        )

        # Should handle empty list
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_reviews(self, mock_anthropic_class, mock_competitor_client):
        """Test review analysis with empty review lists"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.analyze_competitor_reviews(
            competitor_name="Test",
            positive_reviews=[],
            negative_reviews=[]
        )

        # Should handle empty lists
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_single_competitor_comparison(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test comparison with only one competitor"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.compare_multiple_competitors(
            competitors=[{"name": "Single Competitor"}]
        )

        # Should handle single competitor
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_content_list(self, mock_anthropic_class, mock_competitor_client):
        """Test content gap analysis with empty content list"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        content, path = agent.identify_content_gaps(
            competitor_content=[]
        )

        # Should handle empty list
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_special_characters_in_competitor_name(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test analysis with special characters in competitor name"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        special_name = "Competitor™ Brand & Co. (Premium Edition)"
        content, path = agent.analyze_competitor_listing(
            competitor_name=special_name,
            product_title="Test",
            bullet_points=["Test"],
            description="Test"
        )

        # Should handle special characters
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_api_error_propagates(self, mock_anthropic_class, mock_error_client):
        """Test that API errors are properly propagated"""
        mock_anthropic_class.return_value = mock_error_client

        agent = CompetitorAgent()

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            agent.analyze_competitor_listing(
                competitor_name="Test",
                product_title="Test",
                bullet_points=["Test"],
                description="Test"
            )

        assert "API rate limit exceeded" in str(exc_info.value)


class TestReturnTypes:
    """Test suite for verifying correct return types"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_listing_returns_tuple(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that analyze_competitor_listing returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        result = agent.analyze_competitor_listing(
            competitor_name="Test",
            product_title="Test",
            bullet_points=["Test"],
            description="Test"
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_analyze_competitor_reviews_returns_tuple(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that analyze_competitor_reviews returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        result = agent.analyze_competitor_reviews(
            competitor_name="Test",
            positive_reviews=["Test"],
            negative_reviews=["Test"]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_compare_multiple_competitors_returns_tuple(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that compare_multiple_competitors returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        result = agent.compare_multiple_competitors(
            competitors=[{"name": "Test"}]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_identify_content_gaps_returns_tuple(
        self, mock_anthropic_class, mock_competitor_client
    ):
        """Test that identify_content_gaps returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_competitor_client

        agent = CompetitorAgent()
        result = agent.identify_content_gaps(
            competitor_content=[{"competitor_name": "Test", "content_type": "blog", "topic": "Test"}]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)
