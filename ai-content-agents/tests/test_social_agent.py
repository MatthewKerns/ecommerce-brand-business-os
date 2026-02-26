"""
Unit tests for SocialAgent class.

Tests cover:
- Agent initialization
- Instagram post generation
- Reddit post generation
- Content calendar generation
- Carousel script generation
- Batch post generation
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from datetime import datetime

from agents.social_agent import SocialAgent
from config.config import (
    SOCIAL_OUTPUT_DIR,
    DEFAULT_MODEL
)


class TestSocialAgentInitialization:
    """Test suite for SocialAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test SocialAgent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = SocialAgent()

        assert agent.agent_name == "social_agent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_inherits_from_base_agent(self, mock_anthropic_class, mock_anthropic_client):
        """Test that SocialAgent inherits from BaseAgent properly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = SocialAgent()

        # Verify it has BaseAgent methods
        assert hasattr(agent, 'generate_content')
        assert hasattr(agent, 'save_output')
        assert hasattr(agent, 'generate_and_save')
        assert hasattr(agent, '_build_system_prompt')

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_platform_specs_defined(self, mock_anthropic_class, mock_anthropic_client):
        """Test that platform specifications are properly defined"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = SocialAgent()

        assert hasattr(agent, 'platform_specs')
        assert 'instagram' in agent.platform_specs
        assert 'reddit' in agent.platform_specs
        assert 'discord' in agent.platform_specs
        assert 'twitter' in agent.platform_specs


class TestGenerateInstagramPost:
    """Test suite for Instagram post generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_instagram_post_basic(
        self, mock_anthropic_class, mock_social_client, temp_output_dir
    ):
        """Test basic Instagram post generation"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_instagram_post(
            topic="Daily EDC Essentials"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_social_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_instagram_post_with_pillar(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test Instagram post generation with content pillar"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        pillar = "Gear & Equipment"

        content, path = agent.generate_instagram_post(
            topic="Tournament Gear Essentials",
            content_pillar=pillar
        )

        # Verify pillar was included in prompt
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert pillar in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_instagram_post_with_image_description(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test Instagram post generation with image description"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        image_desc = "Premium deck box on tournament table"

        content, path = agent.generate_instagram_post(
            topic="Show Up Battle Ready",
            image_description=image_desc
        )

        # Verify image description was included in prompt
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert image_desc in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_instagram_post_without_hashtags(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test Instagram post generation without hashtags"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_instagram_post(
            topic="Collection Organization",
            include_hashtags=False
        )

        # Content should be generated
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_instagram_post_metadata(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test that Instagram post saves correct metadata"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        topic = "EDC Essentials"
        pillar = "Battle-Ready Lifestyle"
        image_desc = "Tactical gear layout"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_instagram_post(
                topic=topic,
                content_pillar=pillar,
                image_description=image_desc
            )

            # Verify generate_and_save was called with correct metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["platform"] == "instagram"
            assert metadata["topic"] == topic
            assert metadata["content_pillar"] == pillar
            assert metadata["image_description"] == image_desc


class TestGenerateRedditPost:
    """Test suite for Reddit post generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_reddit_post_basic(
        self, mock_anthropic_class, mock_social_client, temp_output_dir
    ):
        """Test basic Reddit post generation"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_reddit_post(
            subreddit="PokemonTCG",
            topic="Tournament preparation tips"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_social_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_reddit_post_with_subreddit(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test Reddit post generation includes subreddit in prompt"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        subreddit = "magicTCG"

        content, path = agent.generate_reddit_post(
            subreddit=subreddit,
            topic="Deck building advice"
        )

        # Verify subreddit was included in prompt
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"r/{subreddit}" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_reddit_post_types(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test different Reddit post types"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        post_types = ["discussion", "question", "guide", "showcase"]

        for post_type in post_types:
            content, path = agent.generate_reddit_post(
                subreddit="TCG",
                topic="Test topic",
                post_type=post_type
            )

            # Verify post type was included in prompt
            call_args = mock_social_client.messages.create.call_args
            prompt = call_args.kwargs["messages"][0]["content"]
            assert post_type in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_reddit_post_with_product_mention(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test Reddit post with product mention"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_reddit_post(
            subreddit="TCG",
            topic="Storage solutions",
            include_product_mention=True
        )

        # Verify product mention setting was included
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "mention" in prompt.lower()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_reddit_post_metadata(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test that Reddit post saves correct metadata"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        subreddit = "PokemonTCG"
        topic = "Collection organization"
        post_type = "guide"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_reddit_post(
                subreddit=subreddit,
                topic=topic,
                post_type=post_type
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["platform"] == "reddit"
            assert metadata["subreddit"] == subreddit
            assert metadata["topic"] == topic
            assert metadata["post_type"] == post_type


class TestGenerateContentCalendar:
    """Test suite for content calendar generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_calendar_basic(
        self, mock_anthropic_class, mock_social_client, temp_output_dir
    ):
        """Test basic content calendar generation"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_content_calendar(
            platform="instagram"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_calendar_custom_days(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test content calendar with custom number of days"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        num_days = 14

        content, path = agent.generate_content_calendar(
            platform="instagram",
            num_days=num_days
        )

        # Verify number of days was included in prompt
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"{num_days}-day" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_calendar_with_pillar(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test content calendar with content pillar focus"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        pillar = "Community Champion"

        content, path = agent.generate_content_calendar(
            platform="reddit",
            content_pillar=pillar
        )

        # Verify pillar was included in prompt
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert pillar in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_calendar_filename(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test content calendar saves with correct filename"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        num_days = 7

        content, path = agent.generate_content_calendar(
            platform="instagram",
            num_days=num_days
        )

        # Verify filename includes number of days
        assert f"content_calendar_{num_days}days.md" in str(path)


class TestGenerateCarouselScript:
    """Test suite for carousel script generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_carousel_script_basic(
        self, mock_anthropic_class, mock_social_client, temp_output_dir
    ):
        """Test basic carousel script generation"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_carousel_script(
            topic="Tournament Preparation Checklist"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_carousel_script_custom_slide_count(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test carousel script with custom number of slides"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        num_slides = 8

        content, path = agent.generate_carousel_script(
            topic="EDC Essentials",
            num_slides=num_slides
        )

        # Verify slide count was included in prompt
        call_args = mock_social_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"NUMBER OF SLIDES: {num_slides}" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_carousel_script_metadata(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test that carousel script saves correct metadata"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        topic = "Collection Care Tips"
        num_slides = 10

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_carousel_script(
                topic=topic,
                num_slides=num_slides
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["type"] == "carousel"
            assert metadata["topic"] == topic
            assert metadata["num_slides"] == num_slides


class TestBatchGeneratePosts:
    """Test suite for batch post generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_batch_generate_posts_instagram(
        self, mock_anthropic_class, mock_social_client, capsys
    ):
        """Test batch generation for Instagram"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        num_posts = 3

        results = agent.batch_generate_posts(
            platform="instagram",
            num_posts=num_posts
        )

        # Verify correct number of posts generated
        assert isinstance(results, list)
        assert len(results) == num_posts

        # Verify each result is a tuple
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 2
            content, path = result
            assert isinstance(content, str)
            assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_batch_generate_posts_reddit(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test batch generation for Reddit"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        num_posts = 2

        results = agent.batch_generate_posts(
            platform="reddit",
            num_posts=num_posts
        )

        # Verify posts were generated
        assert len(results) == num_posts

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_batch_generate_posts_with_content_mix(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test batch generation with custom content mix"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content_mix = ["Gear & Equipment", "Battle-Ready Lifestyle"]

        results = agent.batch_generate_posts(
            platform="instagram",
            num_posts=4,
            content_mix=content_mix
        )

        # Verify posts were generated
        assert len(results) == 4


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_topic(self, mock_anthropic_class, mock_social_client):
        """Test post generation with empty topic"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        content, path = agent.generate_instagram_post(topic="")

        # Should still generate content
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_special_characters_in_topic(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test post generation with special characters in topic"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        special_topic = "EDC Essentials: What's in Your Kit? 🎯"
        content, path = agent.generate_instagram_post(topic=special_topic)

        # Should handle special characters
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_api_error_propagates(self, mock_anthropic_class, mock_error_client):
        """Test that API errors are properly propagated"""
        mock_anthropic_class.return_value = mock_error_client

        agent = SocialAgent()

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            agent.generate_instagram_post(topic="Test Topic")

        assert "API rate limit exceeded" in str(exc_info.value)


class TestReturnTypes:
    """Test suite for verifying correct return types"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_instagram_post_returns_tuple(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test that generate_instagram_post returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        result = agent.generate_instagram_post(topic="Test")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_reddit_post_returns_tuple(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test that generate_reddit_post returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        result = agent.generate_reddit_post(subreddit="TCG", topic="Test")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_batch_generate_posts_returns_list_of_tuples(
        self, mock_anthropic_class, mock_social_client
    ):
        """Test that batch_generate_posts returns list of (content, path) tuples"""
        mock_anthropic_class.return_value = mock_social_client

        agent = SocialAgent()
        result = agent.batch_generate_posts(platform="instagram", num_posts=2)

        assert isinstance(result, list)
        assert len(result) > 0

        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            content, path = item
            assert isinstance(content, str)
            assert isinstance(path, Path)
