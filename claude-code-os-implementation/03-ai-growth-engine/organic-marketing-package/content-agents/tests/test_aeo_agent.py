"""
Unit tests for AEOAgent class.

Tests cover:
- Agent initialization
- FAQ schema generation (JSON-LD)
- FAQ content generation
- Product schema generation (JSON-LD)
- AI-optimized content generation
- Comparison content generation
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from agents.aeo_agent import AEOAgent
from config.config import (
    AEO_OUTPUT_DIR,
    DEFAULT_MODEL
)


class TestAEOAgentInitialization:
    """Test suite for AEOAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test AEOAgent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()

        assert agent.agent_name == "aeo_agent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_inherits_from_base_agent(self, mock_anthropic_class, mock_anthropic_client):
        """Test that AEOAgent inherits from BaseAgent properly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()

        # Verify it has BaseAgent methods
        assert hasattr(agent, 'generate_content')
        assert hasattr(agent, 'save_output')
        assert hasattr(agent, 'generate_and_save')
        assert hasattr(agent, '_build_system_prompt')


class TestGenerateFAQSchema:
    """Test suite for FAQ schema generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_schema_basic(self, mock_anthropic_class, mock_anthropic_client):
        """Test basic FAQ schema generation"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        faq_items = [
            {
                "question": "What is the best way to store cards?",
                "answer": "Use premium archival-quality storage solutions."
            }
        ]

        schema_json = agent.generate_faq_schema(faq_items)

        # Verify schema is valid JSON
        schema = json.loads(schema_json)
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "FAQPage"
        assert len(schema["mainEntity"]) == 1

        # Verify question structure
        question = schema["mainEntity"][0]
        assert question["@type"] == "Question"
        assert question["name"] == "What is the best way to store cards?"
        assert question["acceptedAnswer"]["@type"] == "Answer"
        assert question["acceptedAnswer"]["text"] == "Use premium archival-quality storage solutions."

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_schema_multiple_items(self, mock_anthropic_class, mock_anthropic_client):
        """Test FAQ schema with multiple questions"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        faq_items = [
            {"question": "Question 1?", "answer": "Answer 1"},
            {"question": "Question 2?", "answer": "Answer 2"},
            {"question": "Question 3?", "answer": "Answer 3"}
        ]

        schema_json = agent.generate_faq_schema(faq_items)
        schema = json.loads(schema_json)

        assert len(schema["mainEntity"]) == 3
        assert schema["mainEntity"][0]["name"] == "Question 1?"
        assert schema["mainEntity"][1]["name"] == "Question 2?"
        assert schema["mainEntity"][2]["name"] == "Question 3?"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_schema_empty_list(self, mock_anthropic_class, mock_anthropic_client):
        """Test FAQ schema with empty list"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        faq_items = []

        schema_json = agent.generate_faq_schema(faq_items)
        schema = json.loads(schema_json)

        assert schema["@type"] == "FAQPage"
        assert len(schema["mainEntity"]) == 0

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_schema_special_characters(self, mock_anthropic_class, mock_anthropic_client):
        """Test FAQ schema with special characters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        faq_items = [
            {
                "question": "What's \"premium\" storage?",
                "answer": "It's storage that provides 100% protection & security."
            }
        ]

        schema_json = agent.generate_faq_schema(faq_items)
        schema = json.loads(schema_json)

        # Verify special characters are properly encoded
        assert '"' in schema_json or '\\"' in schema_json or '"premium"' in schema_json
        assert '&' in schema["mainEntity"][0]["acceptedAnswer"]["text"]

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_schema_logging(self, mock_anthropic_class, mock_anthropic_client, caplog):
        """Test that FAQ schema generation logs appropriately"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        faq_items = [
            {"question": "Q1?", "answer": "A1"},
            {"question": "Q2?", "answer": "A2"}
        ]

        agent.generate_faq_schema(faq_items)

        # Verify logging
        assert any("Generating FAQ schema for 2 items" in record.message for record in caplog.records)
        assert any("Successfully generated FAQ schema with 2 questions" in record.message for record in caplog.records)


class TestGenerateFAQContent:
    """Test suite for FAQ content generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_basic(
        self, mock_anthropic_class, mock_aeo_faq_client, temp_output_dir
    ):
        """Test basic FAQ content generation"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        content, path = agent.generate_faq_content(
            topic="TCG Card Storage"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)
        assert "FAQ" in content

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_aeo_faq_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_custom_num_questions(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test FAQ content with custom number of questions"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        num_questions = 15

        content, path = agent.generate_faq_content(
            topic="Card Protection",
            num_questions=num_questions
        )

        # Verify num_questions was included in prompt
        call_args = mock_aeo_faq_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"Create {num_questions} frequently" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_custom_audience(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test FAQ content with custom target audience"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        audience = "Professional collectors"

        content, path = agent.generate_faq_content(
            topic="Card Grading",
            target_audience=audience
        )

        # Verify audience was included in prompt
        call_args = mock_aeo_faq_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert audience in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_without_product_mentions(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test FAQ content without product mentions"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        content, path = agent.generate_faq_content(
            topic="General TCG Tips",
            include_product_mentions=False
        )

        # Verify prompt doesn't require product mentions
        call_args = mock_aeo_faq_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Focus on general expertise without product mentions" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_with_product_mentions(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test FAQ content with product mentions"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        content, path = agent.generate_faq_content(
            topic="Storage Solutions",
            include_product_mentions=True
        )

        # Verify prompt requires product mentions
        call_args = mock_aeo_faq_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Naturally mention Infinity Vault products" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_metadata(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test that FAQ content saves correct metadata"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        topic = "TCG Storage"
        num_questions = 8
        audience = "Tournament players"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_faq_content(
                topic=topic,
                num_questions=num_questions,
                target_audience=audience,
                include_product_mentions=False
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["type"] == "faq_content"
            assert metadata["topic"] == topic
            assert metadata["num_questions"] == num_questions
            assert metadata["target_audience"] == audience
            assert metadata["include_product_mentions"] is False

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_uses_custom_tokens(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test that FAQ content uses 4096 max tokens"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        content, path = agent.generate_faq_content(
            topic="Test Topic"
        )

        # Verify max_tokens was set to 4096
        call_args = mock_aeo_faq_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_includes_system_context(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test that FAQ content includes AEO-specific context"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        content, path = agent.generate_faq_content(
            topic="Test Topic"
        )

        # Verify system context includes AEO guidelines
        call_args = mock_aeo_faq_client.messages.create.call_args
        system = call_args.kwargs["system"]
        assert "Answer Engine Optimization" in system or "AEO" in system


class TestGenerateProductSchema:
    """Test suite for product schema generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_basic(self, mock_anthropic_class, mock_anthropic_client):
        """Test basic product schema generation"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Premium Deck Box",
            "description": "Battle-ready storage for your TCG deck",
            "price": "29.99"
        }

        schema_json = agent.generate_product_schema(product_data)

        # Verify schema is valid JSON
        schema = json.loads(schema_json)
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Product"
        assert schema["name"] == "Premium Deck Box"
        assert schema["description"] == "Battle-ready storage for your TCG deck"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_with_offers(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema with price offers"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product",
            "price": "49.99",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        }

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        assert "offers" in schema
        assert schema["offers"]["@type"] == "Offer"
        assert schema["offers"]["price"] == "49.99"
        assert schema["offers"]["priceCurrency"] == "USD"
        assert schema["offers"]["availability"] == "https://schema.org/InStock"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_default_brand(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema defaults to Infinity Vault brand"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product"
        }

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        assert "brand" in schema
        assert schema["brand"]["@type"] == "Brand"
        assert schema["brand"]["name"] == "Infinity Vault"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_custom_brand(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema with custom brand"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product",
            "brand": "Custom Brand"
        }

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        assert schema["brand"]["name"] == "Custom Brand"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_with_images(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema with images"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product",
            "image": "https://example.com/image.jpg"
        }

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        assert "image" in schema
        assert schema["image"] == "https://example.com/image.jpg"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_with_rating(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema with aggregate rating"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product",
            "rating": {
                "value": 4.8,
                "count": 125
            }
        }

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        assert "aggregateRating" in schema
        assert schema["aggregateRating"]["@type"] == "AggregateRating"
        assert schema["aggregateRating"]["ratingValue"] == 4.8
        assert schema["aggregateRating"]["reviewCount"] == 125

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_with_sku(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema with SKU"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product",
            "sku": "INF-DECKBOX-001"
        }

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        assert schema["sku"] == "INF-DECKBOX-001"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_logging(self, mock_anthropic_class, mock_anthropic_client, caplog):
        """Test that product schema generation logs appropriately"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {
            "name": "Test Product"
        }

        agent.generate_product_schema(product_data)

        # Verify logging
        assert any("Generating product schema: product='Test Product'" in record.message for record in caplog.records)
        assert any("Successfully generated product schema for 'Test Product'" in record.message for record in caplog.records)


class TestGenerateAIOptimizedContent:
    """Test suite for AI-optimized content generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_basic(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client, temp_output_dir
    ):
        """Test basic AI-optimized content generation"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        content, path = agent.generate_ai_optimized_content(
            question="What is the best way to store TCG cards?"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_aeo_ai_optimized_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_custom_type(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test AI-optimized content with custom content type"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        content_type = "comparison"

        content, path = agent.generate_ai_optimized_content(
            question="Deck box vs binder?",
            content_type=content_type
        )

        # Verify content type was included in prompt
        call_args = mock_aeo_ai_optimized_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"Create {content_type} content" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_with_sources(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test AI-optimized content with source citations"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        content, path = agent.generate_ai_optimized_content(
            question="How to grade cards?",
            include_sources=True
        )

        # Verify sources requirement in prompt
        call_args = mock_aeo_ai_optimized_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "source citations" in prompt or "INCLUDE" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_without_sources(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test AI-optimized content without source citations"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        content, path = agent.generate_ai_optimized_content(
            question="Best storage solutions?",
            include_sources=False
        )

        # Verify content was generated
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_metadata(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test that AI-optimized content saves correct metadata"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        question = "How to protect cards?"
        content_type = "article"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_ai_optimized_content(
                question=question,
                content_type=content_type,
                include_sources=True
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["type"] == "ai_optimized_content"
            assert metadata["question"] == question
            assert metadata["content_type"] == content_type
            assert metadata["include_sources"] is True

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_uses_custom_tokens(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test that AI-optimized content uses 4096 max tokens"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        content, path = agent.generate_ai_optimized_content(
            question="Test question?"
        )

        # Verify max_tokens was set to 4096
        call_args = mock_aeo_ai_optimized_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_includes_system_context(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test that AI-optimized content includes AEO-specific context"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        content, path = agent.generate_ai_optimized_content(
            question="Test question?"
        )

        # Verify system context includes AEO guidelines
        call_args = mock_aeo_ai_optimized_client.messages.create.call_args
        system = call_args.kwargs["system"]
        assert "AI Citation Optimization" in system or "Quotability" in system


class TestGenerateComparisonContent:
    """Test suite for comparison content generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_basic(
        self, mock_anthropic_class, mock_aeo_comparison_client, temp_output_dir
    ):
        """Test basic comparison content generation"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        content, path = agent.generate_comparison_content(
            comparison_topic="TCG Storage Solutions",
            items_to_compare=["Deck Box", "Binder", "Storage Case"]
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_aeo_comparison_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_items_in_prompt(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test comparison content includes items in prompt"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        items = ["Item A", "Item B", "Item C"]

        content, path = agent.generate_comparison_content(
            comparison_topic="Test Comparison",
            items_to_compare=items
        )

        # Verify items were included in prompt
        call_args = mock_aeo_comparison_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        for item in items:
            assert item in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_with_recommendation(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test comparison content with recommendation"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        content, path = agent.generate_comparison_content(
            comparison_topic="Storage Types",
            items_to_compare=["Type A", "Type B"],
            include_recommendation=True
        )

        # Verify recommendation requirement in prompt
        call_args = mock_aeo_comparison_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "End with clear recommendation" in prompt or "recommendation based on use case" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_without_recommendation(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test comparison content without recommendation"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        content, path = agent.generate_comparison_content(
            comparison_topic="Storage Types",
            items_to_compare=["Type A", "Type B"],
            include_recommendation=False
        )

        # Verify content was generated
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_metadata(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test that comparison content saves correct metadata"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        topic = "Storage Comparison"
        items = ["Option 1", "Option 2"]

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_comparison_content(
                comparison_topic=topic,
                items_to_compare=items,
                include_recommendation=True
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["type"] == "comparison"
            assert metadata["topic"] == topic
            assert metadata["items_compared"] == items
            assert metadata["include_recommendation"] is True

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_uses_custom_tokens(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test that comparison content uses 4096 max tokens"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        content, path = agent.generate_comparison_content(
            comparison_topic="Test",
            items_to_compare=["A", "B"]
        )

        # Verify max_tokens was set to 4096
        call_args = mock_aeo_comparison_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_includes_system_context(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test that comparison content includes AEO-specific context"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        content, path = agent.generate_comparison_content(
            comparison_topic="Test",
            items_to_compare=["A", "B"]
        )

        # Verify system context includes comparison guidelines
        call_args = mock_aeo_comparison_client.messages.create.call_args
        system = call_args.kwargs["system"]
        assert "Comparison Content Strategy" in system or "AEO for Comparisons" in system


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_faq_items(self, mock_anthropic_class, mock_anthropic_client):
        """Test FAQ schema with empty items"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        schema_json = agent.generate_faq_schema([])

        # Should still generate valid schema
        schema = json.loads(schema_json)
        assert schema["@type"] == "FAQPage"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_faq_items_missing_keys(self, mock_anthropic_class, mock_anthropic_client):
        """Test FAQ schema with missing question/answer keys"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        faq_items = [
            {"question": "Q1?"},  # Missing answer
            {"answer": "A2"}  # Missing question
        ]

        schema_json = agent.generate_faq_schema(faq_items)
        schema = json.loads(schema_json)

        # Should handle missing keys gracefully
        assert len(schema["mainEntity"]) == 2
        assert schema["mainEntity"][0]["name"] == "Q1?"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == ""
        assert schema["mainEntity"][1]["name"] == ""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_product_schema_minimal_data(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema with minimal data"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {"name": "Product"}

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        # Should generate valid schema with defaults
        assert schema["name"] == "Product"
        assert schema["brand"]["name"] == "Infinity Vault"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_product_schema_no_name(self, mock_anthropic_class, mock_anthropic_client):
        """Test product schema without product name"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        product_data = {"price": "29.99"}

        schema_json = agent.generate_product_schema(product_data)
        schema = json.loads(schema_json)

        # Should handle missing name
        assert schema["name"] == ""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_comparison_items(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test comparison content with empty items list"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        content, path = agent.generate_comparison_content(
            comparison_topic="Test",
            items_to_compare=[]
        )

        # Should still generate content
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_special_characters_in_question(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test AI-optimized content with special characters"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        question = "What's the \"best\" storage? (2024 Guide) 🎯"

        content, path = agent.generate_ai_optimized_content(
            question=question
        )

        # Should handle special characters
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_api_error_propagates(self, mock_anthropic_class, mock_error_client):
        """Test that API errors are properly propagated"""
        mock_anthropic_class.return_value = mock_error_client

        agent = AEOAgent()

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            agent.generate_faq_content(topic="Test")

        assert "API rate limit exceeded" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_very_long_topic(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test FAQ content with very long topic"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        long_topic = "Test Topic " * 100

        content, path = agent.generate_faq_content(
            topic=long_topic
        )

        # Should handle long topics
        assert content is not None


class TestReturnTypes:
    """Test suite for verifying correct return types"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_schema_returns_string(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test that generate_faq_schema returns string"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        result = agent.generate_faq_schema([{"question": "Q?", "answer": "A"}])

        assert isinstance(result, str)
        # Verify it's valid JSON
        json.loads(result)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_schema_returns_string(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test that generate_product_schema returns string"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AEOAgent()
        result = agent.generate_product_schema({"name": "Product"})

        assert isinstance(result, str)
        # Verify it's valid JSON
        json.loads(result)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_faq_content_returns_tuple(
        self, mock_anthropic_class, mock_aeo_faq_client
    ):
        """Test that generate_faq_content returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_aeo_faq_client

        agent = AEOAgent()
        result = agent.generate_faq_content(topic="Test")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_ai_optimized_content_returns_tuple(
        self, mock_anthropic_class, mock_aeo_ai_optimized_client
    ):
        """Test that generate_ai_optimized_content returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_aeo_ai_optimized_client

        agent = AEOAgent()
        result = agent.generate_ai_optimized_content(question="Test?")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_comparison_content_returns_tuple(
        self, mock_anthropic_class, mock_aeo_comparison_client
    ):
        """Test that generate_comparison_content returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_aeo_comparison_client

        agent = AEOAgent()
        result = agent.generate_comparison_content(
            comparison_topic="Test",
            items_to_compare=["A", "B"]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)
