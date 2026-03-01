"""
Unit tests for TikTokChannelAgent class.

Tests cover:
- Agent initialization
- Channel specifications
- Content validation
- Video script generation
- Content calendar generation
- Multi-channel strategy
- Channel management (CRUD operations)
- Cross-posting prevention
- Batch content generation
- Performance metrics
- Helper methods
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from datetime import datetime

from agents.tiktok_channel_agent import TikTokChannelAgent
from config.config import (
    TIKTOK_CHANNELS_OUTPUT_DIR,
    DEFAULT_MODEL,
    TIKTOK_CHANNELS,
    CHANNEL_THEMES
)


class TestTikTokChannelAgentInitialization:
    """Test suite for TikTokChannelAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test TikTokChannelAgent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        assert agent.agent_name == "tiktok_channel_agent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_inherits_from_base_agent(self, mock_anthropic_class, mock_anthropic_client):
        """Test that TikTokChannelAgent inherits from BaseAgent properly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        # Verify it has BaseAgent methods
        assert hasattr(agent, 'generate_content')
        assert hasattr(agent, 'save_output')
        assert hasattr(agent, 'generate_and_save')
        assert hasattr(agent, '_build_system_prompt')

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_channels_loaded(self, mock_anthropic_class, mock_anthropic_client):
        """Test that channel configurations are properly loaded"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        assert hasattr(agent, 'channels')
        assert hasattr(agent, 'channel_themes')
        assert len(agent.channels) >= 4  # At least 4 channels

        # Verify all 4 elemental channels exist
        required_elements = ["air", "water", "fire", "earth"]
        for element in required_elements:
            assert element in agent.channels


class TestGetChannelSpecs:
    """Test suite for get_channel_specs method"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_get_channel_specs_air(self, mock_anthropic_class, mock_anthropic_client):
        """Test getting specifications for Air channel"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        specs = agent.get_channel_specs('air')

        assert specs['element'] == 'air'
        assert 'channel_name' in specs
        assert 'description' in specs
        assert 'target_audience' in specs
        assert 'content_focus' in specs
        assert 'posting_schedule' in specs
        assert 'tone' in specs
        assert 'content_types' in specs
        assert 'key_messages' in specs
        assert 'content_pillars' in specs
        assert 'video_length' in specs
        assert 'hook_style' in specs
        assert 'hashtags' in specs
        assert 'visual_style' in specs

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_get_channel_specs_all_elements(self, mock_anthropic_class, mock_anthropic_client):
        """Test getting specifications for all elemental channels"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        elements = ["air", "water", "fire", "earth"]

        for element in elements:
            specs = agent.get_channel_specs(element)
            assert specs['element'] == element
            assert isinstance(specs, dict)
            assert len(specs) > 0

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_get_channel_specs_invalid_element(self, mock_anthropic_class, mock_anthropic_client):
        """Test that invalid channel element raises ValueError"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.get_channel_specs('invalid_element')

        assert "Invalid channel element" in str(exc_info.value)
        assert "invalid_element" in str(exc_info.value)


class TestValidateContentForChannel:
    """Test suite for content validation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_validate_content_basic(
        self, mock_anthropic_class, mock_tiktok_validation_client
    ):
        """Test basic content validation"""
        mock_anthropic_class.return_value = mock_tiktok_validation_client

        agent = TikTokChannelAgent()
        result = agent.validate_content_for_channel(
            content="Quick deck building tips for tournaments",
            channel_element="air"
        )

        assert 'is_valid' in result
        assert 'alignment_score' in result
        assert 'feedback' in result
        assert 'suggestions' in result
        assert 'channel_element' in result
        assert result['channel_element'] == 'air'

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_validate_content_returns_valid(
        self, mock_anthropic_class, mock_tiktok_validation_client
    ):
        """Test that validation returns valid content"""
        mock_anthropic_class.return_value = mock_tiktok_validation_client

        agent = TikTokChannelAgent()
        result = agent.validate_content_for_channel(
            content="Fast tournament prep tips",
            channel_element="air"
        )

        assert result['is_valid'] == True
        assert result['alignment_score'] >= 0.0
        assert result['alignment_score'] <= 1.0

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_validate_content_invalid_channel(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test validation with invalid channel raises ValueError"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.validate_content_for_channel(
                content="Test content",
                channel_element="invalid"
            )

        assert "Invalid channel element" in str(exc_info.value)


class TestGenerateChannelVideoScript:
    """Test suite for channel video script generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_video_script_basic(
        self, mock_anthropic_class, mock_tiktok_script_client, temp_output_dir
    ):
        """Test basic video script generation"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()
        content, path = agent.generate_channel_video_script(
            channel_element="air",
            topic="Quick deck building tips"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_tiktok_script_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_video_script_with_product(
        self, mock_anthropic_class, mock_tiktok_script_client
    ):
        """Test video script generation with product feature"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()
        product = "Tournament Deck Box"

        content, path = agent.generate_channel_video_script(
            channel_element="air",
            topic="Tournament prep essentials",
            product=product
        )

        # Verify product was included in prompt
        call_args = mock_tiktok_script_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert product in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_video_script_with_product_link(
        self, mock_anthropic_class, mock_tiktok_script_client
    ):
        """Test video script generation with product link CTA"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()

        content, path = agent.generate_channel_video_script(
            channel_element="fire",
            topic="Unboxing rare cards",
            product="Premium Card Binder",
            include_product_link=True
        )

        # Verify include_product_link flag was used in prompt
        call_args = mock_tiktok_script_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "INCLUDE PRODUCT LINK" in prompt or "Shop Now" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_video_script_all_channels(
        self, mock_anthropic_class, mock_tiktok_script_client
    ):
        """Test video script generation for all channel elements"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()
        elements = ["air", "water", "fire", "earth"]

        for element in elements:
            content, path = agent.generate_channel_video_script(
                channel_element=element,
                topic=f"{element.capitalize()} channel test content"
            )

            assert content is not None
            assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_video_script_metadata(
        self, mock_anthropic_class, mock_tiktok_script_client
    ):
        """Test that video script saves correct metadata"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()
        topic = "Tournament prep"
        element = "air"
        product = "Deck Box"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_channel_video_script(
                channel_element=element,
                topic=topic,
                product=product
            )

            # Verify generate_and_save was called with correct metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["platform"] == "tiktok"
            assert metadata["channel_element"] == element
            assert metadata["topic"] == topic
            assert metadata["product"] == product


class TestGenerateChannelContentCalendar:
    """Test suite for content calendar generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_calendar_basic(
        self, mock_anthropic_class, mock_tiktok_calendar_client, temp_output_dir
    ):
        """Test basic content calendar generation"""
        mock_anthropic_class.return_value = mock_tiktok_calendar_client

        agent = TikTokChannelAgent()
        content, path = agent.generate_channel_content_calendar(
            channel_element="air",
            num_days=7
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_tiktok_calendar_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_calendar_custom_days(
        self, mock_anthropic_class, mock_tiktok_calendar_client
    ):
        """Test calendar generation with custom number of days"""
        mock_anthropic_class.return_value = mock_tiktok_calendar_client

        agent = TikTokChannelAgent()
        num_days = 14

        content, path = agent.generate_channel_content_calendar(
            channel_element="water",
            num_days=num_days
        )

        # Verify num_days was included in prompt
        call_args = mock_tiktok_calendar_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert str(num_days) in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_calendar_without_topics(
        self, mock_anthropic_class, mock_tiktok_calendar_client
    ):
        """Test calendar generation without topic suggestions"""
        mock_anthropic_class.return_value = mock_tiktok_calendar_client

        agent = TikTokChannelAgent()

        content, path = agent.generate_channel_content_calendar(
            channel_element="earth",
            include_topics=False
        )

        assert content is not None


class TestGenerateMultiChannelStrategy:
    """Test suite for multi-channel strategy generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_multi_channel_strategy_weekly(
        self, mock_anthropic_class, mock_tiktok_script_client, temp_output_dir
    ):
        """Test weekly multi-channel strategy generation"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()
        content, path = agent.generate_multi_channel_strategy(
            time_period="weekly"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_multi_channel_strategy_monthly(
        self, mock_anthropic_class, mock_tiktok_script_client
    ):
        """Test monthly multi-channel strategy generation"""
        mock_anthropic_class.return_value = mock_tiktok_script_client

        agent = TikTokChannelAgent()

        content, path = agent.generate_multi_channel_strategy(
            time_period="monthly"
        )

        # Verify time period was included in prompt
        call_args = mock_tiktok_script_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "monthly" in prompt.lower()


class TestChannelManagement:
    """Test suite for channel CRUD operations"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_list_channels(self, mock_anthropic_class, mock_anthropic_client):
        """Test listing all channels"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        channels = agent.list_channels()

        assert isinstance(channels, list)
        assert len(channels) >= 4

        # Verify each channel has required fields
        for channel in channels:
            assert 'element' in channel
            assert 'channel_name' in channel
            assert 'description' in channel
            assert 'target_audience' in channel
            assert 'content_focus' in channel
            assert 'posting_frequency' in channel
            assert 'tone' in channel
            assert 'content_types' in channel

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_get_channel_valid(self, mock_anthropic_class, mock_anthropic_client):
        """Test getting a valid channel"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        channel = agent.get_channel('air')

        assert channel['element'] == 'air'
        assert 'channel_name' in channel
        assert 'posting_schedule' in channel

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_get_channel_invalid(self, mock_anthropic_class, mock_anthropic_client):
        """Test getting invalid channel raises ValueError"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.get_channel('invalid_channel')

        assert "Invalid channel element" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_create_channel_basic(self, mock_anthropic_class, mock_anthropic_client):
        """Test creating a new channel"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        result = agent.create_channel(
            element="metal",
            channel_name="Infinity Vault - Metal",
            description="Premium collecting and rare cards",
            target_audience="High-value collectors",
            content_focus="Rare cards, premium products",
            posting_schedule={
                'frequency': '3x per week',
                'days': ['monday', 'wednesday', 'friday'],
                'best_times': ['6:00 PM']
            },
            branding_guidelines={
                'visual_style': 'Premium, elegant',
                'hashtags': ['#PremiumTCG', '#RareCards']
            }
        )

        assert result['element'] == 'metal'
        assert result['status'] == 'created'
        assert 'channel_config' in result

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_create_channel_duplicate(self, mock_anthropic_class, mock_anthropic_client):
        """Test creating duplicate channel raises ValueError"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.create_channel(
                element="air",  # Already exists
                channel_name="Test",
                description="Test",
                target_audience="Test",
                content_focus="Test",
                posting_schedule={
                    'frequency': 'daily',
                    'days': ['monday'],
                    'best_times': ['8:00 AM']
                },
                branding_guidelines={
                    'visual_style': 'Test',
                    'hashtags': ['#test']
                }
            )

        assert "already exists" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_create_channel_invalid_params(self, mock_anthropic_class, mock_anthropic_client):
        """Test creating channel with invalid parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        # Test with missing required schedule keys
        with pytest.raises(ValueError):
            agent.create_channel(
                element="test",
                channel_name="Test",
                description="Test",
                target_audience="Test",
                content_focus="Test",
                posting_schedule={},  # Missing required keys
                branding_guidelines={
                    'visual_style': 'Test',
                    'hashtags': ['#test']
                }
            )

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_update_channel_basic(self, mock_anthropic_class, mock_anthropic_client):
        """Test updating a channel"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        result = agent.update_channel(
            'air',
            description='Updated description'
        )

        assert result['element'] == 'air'
        assert result['status'] == 'updated'
        assert 'description' in result['updated_fields']

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_update_channel_invalid(self, mock_anthropic_class, mock_anthropic_client):
        """Test updating invalid channel raises ValueError"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.update_channel('invalid_channel', description='Test')

        assert "does not exist" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_update_channel_no_updates(self, mock_anthropic_class, mock_anthropic_client):
        """Test updating channel with no changes"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        result = agent.update_channel('air')

        assert result['status'] == 'no_changes'


class TestCrossPostingPrevention:
    """Test suite for cross-posting prevention"""

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.tiktok_channel_agent.get_db_session')
    def test_check_content_uniqueness_no_existing(
        self, mock_db_session, mock_anthropic_class, mock_anthropic_client
    ):
        """Test content uniqueness when no existing content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        # Mock database to return no existing content
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []
        mock_db_session.return_value = mock_db

        agent = TikTokChannelAgent()
        is_unique = agent.check_content_uniqueness(
            content_text="Test content",
            channel_element="air"
        )

        assert is_unique == True

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.tiktok_channel_agent.get_db_session')
    def test_check_content_uniqueness_exact_duplicate(
        self, mock_db_session, mock_anthropic_class, mock_anthropic_client
    ):
        """Test detection of exact duplicate content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        # Mock database to return existing identical content
        mock_db = Mock()
        mock_channel = Mock()
        mock_channel.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_channel

        mock_content = Mock()
        mock_history = Mock()
        mock_history.content = "test content"  # Same as input (after normalization)
        mock_content.channel_id = 2  # Different channel

        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_content, mock_history)
        ]
        mock_db_session.return_value = mock_db

        agent = TikTokChannelAgent()
        is_unique = agent.check_content_uniqueness(
            content_text="Test content",  # Will be normalized to "test content"
            channel_element="air"
        )

        assert is_unique == False

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_check_content_uniqueness_invalid_channel(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test that invalid channel raises ValueError"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.check_content_uniqueness(
                content_text="Test",
                channel_element="invalid"
            )

        assert "Invalid channel element" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.tiktok_channel_agent.get_db_session')
    def test_check_content_uniqueness_db_error(
        self, mock_db_session, mock_anthropic_class, mock_anthropic_client
    ):
        """Test that database errors default to allowing content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        # Mock database to raise error
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database error")
        mock_db_session.return_value = mock_db

        agent = TikTokChannelAgent()
        is_unique = agent.check_content_uniqueness(
            content_text="Test content",
            channel_element="air"
        )

        # Should default to True on error (fail open)
        assert is_unique == True


class TestBatchGeneration:
    """Test suite for batch content generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_batch_generate_weekly_content(
        self, mock_anthropic_class, mock_tiktok_calendar_client
    ):
        """Test batch generation for all channels"""
        mock_anthropic_class.return_value = mock_tiktok_calendar_client

        agent = TikTokChannelAgent()
        results = agent.batch_generate_weekly_content()

        assert isinstance(results, dict)
        assert len(results) == 4  # All 4 channels

        # Verify each channel result
        for element in ["air", "water", "fire", "earth"]:
            assert element in results
            assert results[element]['element'] == element
            assert 'calendar_content' in results[element]
            assert 'calendar_path' in results[element]

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_batch_generate_custom_days(
        self, mock_anthropic_class, mock_tiktok_calendar_client
    ):
        """Test batch generation with custom number of days"""
        mock_anthropic_class.return_value = mock_tiktok_calendar_client

        agent = TikTokChannelAgent()
        num_days = 14
        results = agent.batch_generate_weekly_content(num_days=num_days)

        # Verify all results have correct num_days
        for result in results.values():
            assert result['num_days'] == num_days


class TestPerformanceMetrics:
    """Test suite for channel performance metrics"""

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.tiktok_channel_agent.get_db_session')
    def test_get_channel_performance_no_data(
        self, mock_db_session, mock_anthropic_class, mock_anthropic_client
    ):
        """Test performance metrics when no data exists"""
        mock_anthropic_class.return_value = mock_anthropic_client

        # Mock database to return no channel
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.return_value = mock_db

        agent = TikTokChannelAgent()
        metrics = agent.get_channel_performance('air')

        assert metrics['channel_element'] == 'air'
        assert metrics['total_posts'] == 0
        assert metrics['total_saves'] == 0
        assert metrics['total_views'] == 0
        assert metrics['save_rate'] == 0.0

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.tiktok_channel_agent.get_db_session')
    def test_get_channel_performance_with_data(
        self, mock_db_session, mock_anthropic_class, mock_anthropic_client
    ):
        """Test performance metrics with actual data"""
        mock_anthropic_class.return_value = mock_anthropic_client

        # Mock database with channel and content
        mock_db = Mock()
        mock_channel = Mock()
        mock_channel.id = 1
        mock_channel.channel_name = "Infinity Vault - Air"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_channel

        # Create mock content records
        mock_content_1 = Mock()
        mock_content_1.save_count = 100
        mock_content_1.view_count = 10000
        mock_content_1.engagement_rate = 5.0
        mock_content_1.post_date = datetime.utcnow()
        mock_content_1.content_id = 1

        mock_content_2 = Mock()
        mock_content_2.save_count = 50
        mock_content_2.view_count = 5000
        mock_content_2.engagement_rate = 4.0
        mock_content_2.post_date = datetime.utcnow()
        mock_content_2.content_id = 2

        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_content_1, mock_content_2
        ]
        mock_db_session.return_value = mock_db

        agent = TikTokChannelAgent()
        metrics = agent.get_channel_performance('air')

        assert metrics['total_posts'] == 2
        assert metrics['total_saves'] == 150
        assert metrics['total_views'] == 15000
        assert metrics['save_rate'] == 1.0  # 150/15000 * 100
        assert 'top_performing_content' in metrics

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_get_channel_performance_invalid_channel(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test performance metrics with invalid channel"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.get_channel_performance('invalid_channel')

        assert "Invalid channel element" in str(exc_info.value)


class TestHelperMethods:
    """Test suite for helper methods"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_normalize_content(self, mock_anthropic_class, mock_anthropic_client):
        """Test content normalization"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        # Test with various whitespace and case
        normalized = agent._normalize_content("  Test   Content  WITH  caps  ")
        assert normalized == "test content with caps"

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_normalize_content_empty(self, mock_anthropic_class, mock_anthropic_client):
        """Test normalization of empty content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        normalized = agent._normalize_content("")
        assert normalized == ""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_hash(self, mock_anthropic_class, mock_anthropic_client):
        """Test content hash generation"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        hash1 = agent._generate_content_hash("test content")
        hash2 = agent._generate_content_hash("test content")
        hash3 = agent._generate_content_hash("different content")

        # Same content should produce same hash
        assert hash1 == hash2
        # Different content should produce different hash
        assert hash1 != hash3
        # Hash should be hex string
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_calculate_similarity_identical(self, mock_anthropic_class, mock_anthropic_client):
        """Test similarity calculation for identical content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        similarity = agent._calculate_similarity(
            "test content",
            "test content"
        )

        assert similarity == 1.0

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_calculate_similarity_different(self, mock_anthropic_class, mock_anthropic_client):
        """Test similarity calculation for different content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        similarity = agent._calculate_similarity(
            "test content",
            "completely different words"
        )

        assert similarity < 1.0

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_calculate_similarity_empty(self, mock_anthropic_class, mock_anthropic_client):
        """Test similarity calculation for empty content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()

        # Both empty should be identical
        similarity = agent._calculate_similarity("", "")
        assert similarity == 1.0

        # One empty should be completely different
        similarity = agent._calculate_similarity("test", "")
        assert similarity == 0.0

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_calculate_similarity_partial(self, mock_anthropic_class, mock_anthropic_client):
        """Test similarity calculation for partially similar content"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = TikTokChannelAgent()
        similarity = agent._calculate_similarity(
            "quick deck building tips",
            "quick tips for deck building"
        )

        # Should have high similarity (4 out of 5 words match)
        assert similarity > 0.5
        assert similarity < 1.0
