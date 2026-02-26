"""
Unit tests for AmazonAgent class.

Tests cover:
- Agent initialization
- Product title generation
- Bullet point generation
- Product description generation
- A+ Content generation
- Listing optimization
- Backend keyword generation
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from agents.amazon_agent import AmazonAgent
from config.config import (
    AMAZON_OUTPUT_DIR,
    DEFAULT_MODEL
)


class TestAmazonAgentInitialization:
    """Test suite for AmazonAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test AmazonAgent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AmazonAgent()

        assert agent.agent_name == "amazon_agent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_inherits_from_base_agent(self, mock_anthropic_class, mock_anthropic_client):
        """Test that AmazonAgent inherits from BaseAgent properly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = AmazonAgent()

        # Verify it has BaseAgent methods
        assert hasattr(agent, 'generate_content')
        assert hasattr(agent, 'save_output')
        assert hasattr(agent, 'generate_and_save')
        assert hasattr(agent, '_build_system_prompt')


class TestGenerateProductTitle:
    """Test suite for product title generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_title_basic(
        self, mock_anthropic_class, mock_amazon_client, temp_output_dir
    ):
        """Test basic product title generation"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_product_title(
            product_name="Card Binder",
            key_features=["9-pocket pages", "scratch-resistant"],
            target_keywords=["trading card binder", "pokemon"]
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_amazon_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_title_includes_keywords(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test product title generation includes target keywords"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        keywords = ["tournament grade", "premium", "battle ready"]

        content, path = agent.generate_product_title(
            product_name="Deck Box",
            key_features=["durable", "portable"],
            target_keywords=keywords
        )

        # Verify keywords were included in prompt
        call_args = mock_amazon_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        for keyword in keywords:
            assert keyword in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_title_metadata(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that product title saves correct metadata"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        product_name = "Card Binder"
        features = ["feature1", "feature2"]
        keywords = ["keyword1", "keyword2"]

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_product_title(
                product_name=product_name,
                key_features=features,
                target_keywords=keywords
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["product_name"] == product_name
            assert metadata["key_features"] == features
            assert metadata["target_keywords"] == keywords


class TestGenerateBulletPoints:
    """Test suite for bullet point generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_bullet_points_basic(
        self, mock_anthropic_class, mock_amazon_client, temp_output_dir
    ):
        """Test basic bullet point generation"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_bullet_points(
            product_name="Card Binder",
            features=[
                {"feature": "Scratch-resistant pages", "benefit": "Keep cards pristine"},
                {"feature": "9-pocket layout", "benefit": "Optimal organization"}
            ]
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_bullet_points_with_custom_audience(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test bullet point generation with custom target audience"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        audience = "Casual collectors"

        content, path = agent.generate_bullet_points(
            product_name="Card Binder",
            features=[{"feature": "Test", "benefit": "Test benefit"}],
            target_audience=audience
        )

        # Verify audience was included in prompt
        call_args = mock_amazon_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert audience in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_bullet_points_includes_system_context(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that bullet points include strategic system context"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_bullet_points(
            product_name="Test Product",
            features=[{"feature": "Test", "benefit": "Benefit"}]
        )

        # Verify system context was provided
        call_args = mock_amazon_client.messages.create.call_args
        system = call_args.kwargs["system"]
        assert "AMAZON BULLET POINT STRATEGY" in system

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_bullet_points_metadata(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that bullet points save correct metadata"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        product_name = "Card Binder"
        features = [{"feature": "F1", "benefit": "B1"}]
        audience = "Tournament players"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_bullet_points(
                product_name=product_name,
                features=features,
                target_audience=audience
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["product_name"] == product_name
            assert metadata["features"] == features
            assert metadata["target_audience"] == audience


class TestGenerateProductDescription:
    """Test suite for product description generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_description_basic(
        self, mock_anthropic_class, mock_amazon_client, temp_output_dir
    ):
        """Test basic product description generation"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_product_description(
            product_name="Card Binder",
            long_description="Premium 9-pocket pages with scratch-resistant material",
            usp="Battle-ready storage for tournament players"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_description_with_warranty(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test product description generation with warranty info"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        warranty = "Lifetime warranty included"

        content, path = agent.generate_product_description(
            product_name="Deck Box",
            long_description="Test description",
            usp="Premium quality",
            warranty_info=warranty
        )

        # Verify warranty was included in prompt
        call_args = mock_amazon_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert warranty in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_description_metadata(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that product description saves correct metadata"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        product_name = "Test Product"
        usp = "Unique value"
        warranty = "Lifetime"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_product_description(
                product_name=product_name,
                long_description="Description",
                usp=usp,
                warranty_info=warranty
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["product_name"] == product_name
            assert metadata["usp"] == usp
            assert metadata["warranty"] == warranty


class TestGenerateAPlusContent:
    """Test suite for A+ Content generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_a_plus_content_basic(
        self, mock_anthropic_class, mock_amazon_client, temp_output_dir
    ):
        """Test basic A+ Content generation"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_a_plus_content(
            product_name="Card Binder",
            modules=["Hero image", "Feature comparison", "Brand story"]
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_a_plus_content_with_modules(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test A+ Content generation with specific modules"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        modules = ["Hero image", "Product benefits grid", "Technical specs"]

        content, path = agent.generate_a_plus_content(
            product_name="Deck Box",
            modules=modules
        )

        # Verify modules were included in prompt
        call_args = mock_amazon_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        for module in modules:
            assert module in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_a_plus_content_metadata(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that A+ Content saves correct metadata"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        product_name = "Test Product"
        modules = ["Module1", "Module2"]

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_a_plus_content(
                product_name=product_name,
                modules=modules
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["product_name"] == product_name
            assert metadata["modules"] == modules


class TestOptimizeExistingListing:
    """Test suite for listing optimization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_optimize_existing_listing_basic(
        self, mock_anthropic_class, mock_amazon_client, temp_output_dir
    ):
        """Test basic listing optimization"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.optimize_existing_listing(
            current_title="Card Binder Storage",
            current_bullets=["Holds cards", "Durable material", "Good quality"],
            current_description="A card binder for storage"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_optimize_existing_listing_with_performance_data(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test listing optimization with performance data"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        perf_data = {"ctr": 0.05, "conversion_rate": 0.02}

        content, path = agent.optimize_existing_listing(
            current_title="Test Title",
            current_bullets=["Bullet 1"],
            current_description="Description",
            performance_data=perf_data
        )

        # Verify performance data was included
        call_args = mock_amazon_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "PERFORMANCE DATA" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_optimize_existing_listing_uses_extended_tokens(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that listing optimization uses 4096 tokens"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.optimize_existing_listing(
            current_title="Test",
            current_bullets=["Test"],
            current_description="Test"
        )

        # Verify max_tokens was set to 4096
        call_args = mock_amazon_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096


class TestGenerateBackendKeywords:
    """Test suite for backend keyword generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_backend_keywords_basic(
        self, mock_anthropic_class, mock_amazon_client, temp_output_dir
    ):
        """Test basic backend keyword generation"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_backend_keywords(
            product_name="Card Binder",
            category="Trading Card Storage",
            target_use_cases=["tournament play", "collection organization"]
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_backend_keywords_includes_use_cases(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test backend keywords include use cases in prompt"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        use_cases = ["tournament", "collection display", "protection"]

        content, path = agent.generate_backend_keywords(
            product_name="Deck Box",
            category="Card Storage",
            target_use_cases=use_cases
        )

        # Verify use cases were included in prompt
        call_args = mock_amazon_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        for use_case in use_cases:
            assert use_case in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_backend_keywords_metadata(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that backend keywords save correct metadata"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        product_name = "Test Product"
        category = "Test Category"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_backend_keywords(
                product_name=product_name,
                category=category,
                target_use_cases=["use1"]
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["product_name"] == product_name
            assert metadata["category"] == category


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_product_name(self, mock_anthropic_class, mock_amazon_client):
        """Test title generation with empty product name"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_product_title(
            product_name="",
            key_features=["feature"],
            target_keywords=["keyword"]
        )

        # Should still generate content
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_features_list(self, mock_anthropic_class, mock_amazon_client):
        """Test bullet generation with empty features"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        content, path = agent.generate_bullet_points(
            product_name="Test",
            features=[]
        )

        # Should handle empty list
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_special_characters_in_product_name(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test generation with special characters in product name"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        special_name = "Card Binder™ - Professional Edition (9-Pocket)"
        content, path = agent.generate_product_title(
            product_name=special_name,
            key_features=["test"],
            target_keywords=["test"]
        )

        # Should handle special characters
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_api_error_propagates(self, mock_anthropic_class, mock_error_client):
        """Test that API errors are properly propagated"""
        mock_anthropic_class.return_value = mock_error_client

        agent = AmazonAgent()

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            agent.generate_product_title(
                product_name="Test",
                key_features=["test"],
                target_keywords=["test"]
            )

        assert "API rate limit exceeded" in str(exc_info.value)


class TestReturnTypes:
    """Test suite for verifying correct return types"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_product_title_returns_tuple(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that generate_product_title returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        result = agent.generate_product_title(
            product_name="Test",
            key_features=["test"],
            target_keywords=["test"]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_bullet_points_returns_tuple(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that generate_bullet_points returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        result = agent.generate_bullet_points(
            product_name="Test",
            features=[{"feature": "F", "benefit": "B"}]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_optimize_existing_listing_returns_tuple(
        self, mock_anthropic_class, mock_amazon_client
    ):
        """Test that optimize_existing_listing returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_amazon_client

        agent = AmazonAgent()
        result = agent.optimize_existing_listing(
            current_title="Test",
            current_bullets=["Test"],
            current_description="Test"
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)
