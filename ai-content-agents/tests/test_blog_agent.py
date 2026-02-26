"""
Unit tests for BlogAgent class.

Tests cover:
- Agent initialization
- Blog post generation with various parameters
- Blog series generation
- Listicle generation
- How-to guide generation
- Content pillar validation
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from agents.blog_agent import BlogAgent
from config.config import (
    BLOG_OUTPUT_DIR,
    CONTENT_PILLARS,
    DEFAULT_MODEL
)


class TestBlogAgentInitialization:
    """Test suite for BlogAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test BlogAgent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BlogAgent()

        assert agent.agent_name == "blog_agent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_inherits_from_base_agent(self, mock_anthropic_class, mock_anthropic_client):
        """Test that BlogAgent inherits from BaseAgent properly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BlogAgent()

        # Verify it has BaseAgent methods
        assert hasattr(agent, 'generate_content')
        assert hasattr(agent, 'save_output')
        assert hasattr(agent, 'generate_and_save')
        assert hasattr(agent, '_build_system_prompt')


class TestGenerateBlogPost:
    """Test suite for blog post generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_basic(
        self, mock_anthropic_class, mock_blog_client, temp_output_dir
    ):
        """Test basic blog post generation"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Essential Gear for Tournament Play",
            content_pillar="Gear & Equipment"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert isinstance(path, Path)
        assert path.exists()

        # Verify API was called
        mock_blog_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_with_keywords(
        self, mock_anthropic_class, mock_blog_client, temp_output_dir
    ):
        """Test blog post generation with target keywords"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        keywords = ["tactical gear", "EDC", "battle ready"]

        content, path = agent.generate_blog_post(
            topic="Daily Carry Essentials",
            target_keywords=keywords
        )

        # Verify API was called with keywords in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "tactical gear" in prompt
        assert "EDC" in prompt
        assert "battle ready" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_with_custom_word_count(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test blog post generation with custom word count"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Tournament Preparation",
            word_count=2000
        )

        # Verify word count was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "2000 words" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_without_cta(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test blog post generation without call-to-action"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Collection Care Tips",
            include_cta=False
        )

        # Verify CTA was not included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        # The prompt should not include CTA requirements when include_cta=False
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_with_valid_pillar(
        self, mock_anthropic_class, mock_blog_client, capsys
    ):
        """Test blog post generation with valid content pillar"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        pillar = "Battle-Ready Lifestyle"

        content, path = agent.generate_blog_post(
            topic="Mental Preparation for Competition",
            content_pillar=pillar
        )

        # Verify no warning was printed
        captured = capsys.readouterr()
        assert "Warning" not in captured.out

        # Verify pillar was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert pillar in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_with_invalid_pillar(
        self, mock_anthropic_class, mock_blog_client, capsys
    ):
        """Test blog post generation with invalid content pillar"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        invalid_pillar = "Invalid Pillar"

        content, path = agent.generate_blog_post(
            topic="Test Topic",
            content_pillar=invalid_pillar
        )

        # Verify warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert invalid_pillar in captured.out

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_metadata(
        self, mock_anthropic_class, mock_blog_client, temp_output_dir
    ):
        """Test that blog post generation saves correct metadata"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        topic = "Test Topic"
        pillar = "Gear & Equipment"
        keywords = ["test", "keywords"]
        word_count = 1500

        # Mock the save_output to capture metadata
        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_blog_post(
                topic=topic,
                content_pillar=pillar,
                target_keywords=keywords,
                word_count=word_count
            )

            # Verify generate_and_save was called with correct metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["topic"] == topic
            assert metadata["content_pillar"] == pillar
            assert metadata["target_keywords"] == keywords
            assert metadata["word_count_target"] == word_count

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_uses_custom_tokens(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that blog post generation uses 4096 tokens"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic"
        )

        # Verify max_tokens was set to 4096
        call_args = mock_blog_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_includes_system_context(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that blog post generation includes SEO and blog-specific context"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic"
        )

        # Verify system context includes blog-specific guidelines
        call_args = mock_blog_client.messages.create.call_args
        system = call_args.kwargs["system"]
        assert "Blog Content Strategy" in system or "SEO Best Practices" in system


class TestGenerateBlogSeries:
    """Test suite for blog series generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_series_basic(
        self, mock_anthropic_class, mock_blog_client, capsys
    ):
        """Test basic blog series outline generation"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        result = agent.generate_blog_series(
            series_topic="Complete Tournament Preparation Guide"
        )

        # Verify result is a list of tuples
        assert isinstance(result, list)
        assert len(result) == 1

        outline, path = result[0]
        assert isinstance(outline, str)
        assert isinstance(path, Path)
        assert path.exists()

        # Verify outline message was printed
        captured = capsys.readouterr()
        assert "Blog Series Outline" in captured.out

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_series_custom_post_count(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test blog series with custom number of posts"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        num_posts = 5

        result = agent.generate_blog_series(
            series_topic="Equipment Mastery",
            num_posts=num_posts
        )

        # Verify prompt includes correct number of posts
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert f"{num_posts}-part" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_series_with_pillar(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test blog series with content pillar"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        pillar = "Community Champion"

        result = agent.generate_blog_series(
            series_topic="Building Your Gaming Community",
            content_pillar=pillar
        )

        # Verify pillar was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert pillar in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_series_saves_outline(
        self, mock_anthropic_class, mock_blog_client, temp_output_dir
    ):
        """Test that blog series saves outline file"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        result = agent.generate_blog_series(
            series_topic="Test Series"
        )

        outline, path = result[0]

        # Verify outline file was created
        assert path.name == "series_outline.md"
        assert path.exists()
        assert path.read_text() == outline


class TestGenerateListicle:
    """Test suite for listicle generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_listicle_basic(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test basic listicle generation"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_listicle(
            topic="Essential Tournament Supplies"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_listicle_custom_item_count(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test listicle with custom number of items"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        num_items = 15

        content, path = agent.generate_listicle(
            topic="Deck Building Tips",
            num_items=num_items
        )

        # Verify number of items was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert str(num_items) in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_listicle_with_pillar(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test listicle with content pillar"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        pillar = "Collector's Journey"

        content, path = agent.generate_listicle(
            topic="Card Collection Milestones",
            content_pillar=pillar
        )

        # Verify pillar was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert pillar in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_listicle_metadata(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that listicle saves correct metadata"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        topic = "Top Storage Solutions"
        num_items = 7
        pillar = "Gear & Equipment"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_listicle(
                topic=topic,
                num_items=num_items,
                content_pillar=pillar
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["type"] == "listicle"
            assert metadata["topic"] == topic
            assert metadata["num_items"] == num_items
            assert metadata["content_pillar"] == pillar

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_listicle_includes_cta(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that listicle prompt includes CTA requirement"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_listicle(
            topic="Tournament Preparation Checklist"
        )

        # Verify CTA mentioned in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Call-to-action" in prompt or "Infinity Vault" in prompt


class TestGenerateHowToGuide:
    """Test suite for how-to guide generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_basic(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test basic how-to guide generation"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_how_to_guide(
            topic="Organize Your Card Collection"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)
        assert isinstance(path, Path)
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_with_target_audience(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test how-to guide with custom target audience"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        audience = "Casual players"

        content, path = agent.generate_how_to_guide(
            topic="Build Your First Competitive Deck",
            target_audience=audience
        )

        # Verify audience was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert audience in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_with_difficulty_level(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test how-to guide with difficulty level"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        difficulty = "advanced"

        content, path = agent.generate_how_to_guide(
            topic="Master Tournament Meta Strategy",
            difficulty_level=difficulty
        )

        # Verify difficulty was included in prompt
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert difficulty in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_metadata(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that how-to guide saves correct metadata"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        topic = "Protect Your Valuable Cards"
        audience = "Collectors"
        difficulty = "intermediate"

        with patch.object(agent, 'generate_and_save', wraps=agent.generate_and_save) as mock_gen_save:
            content, path = agent.generate_how_to_guide(
                topic=topic,
                target_audience=audience,
                difficulty_level=difficulty
            )

            # Verify metadata
            call_args = mock_gen_save.call_args
            metadata = call_args.kwargs["metadata"]
            assert metadata["type"] == "how-to"
            assert metadata["topic"] == topic
            assert metadata["target_audience"] == audience
            assert metadata["difficulty"] == difficulty

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_includes_structure(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that how-to guide prompt includes required structure"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_how_to_guide(
            topic="Test Guide"
        )

        # Verify prompt includes structural requirements
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "step-by-step" in prompt
        assert "pro tips" in prompt or "common mistakes" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_default_parameters(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test how-to guide uses correct default parameters"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_how_to_guide(
            topic="Test Topic"
        )

        # Verify defaults were used
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "Tournament players" in prompt
        assert "beginner" in prompt


class TestContentPillarValidation:
    """Test suite for content pillar validation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_all_valid_pillars_accepted(
        self, mock_anthropic_class, mock_blog_client, capsys
    ):
        """Test that all valid content pillars are accepted without warnings"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()

        for pillar in CONTENT_PILLARS:
            content, path = agent.generate_blog_post(
                topic="Test Topic",
                content_pillar=pillar
            )

            # Verify no warning was printed for valid pillar
            captured = capsys.readouterr()
            assert "Warning" not in captured.out

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_none_pillar_accepted(
        self, mock_anthropic_class, mock_blog_client, capsys
    ):
        """Test that None pillar is accepted (agent chooses)"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic",
            content_pillar=None
        )

        # Verify no warning for None
        captured = capsys.readouterr()
        assert "Warning" not in captured.out


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_topic(self, mock_anthropic_class, mock_blog_client):
        """Test blog generation with empty topic"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(topic="")

        # Should still generate content
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_very_long_topic(self, mock_anthropic_class, mock_blog_client):
        """Test blog generation with very long topic"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        long_topic = "Test Topic " * 100
        content, path = agent.generate_blog_post(topic=long_topic)

        # Should handle long topics
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_keywords_list(self, mock_anthropic_class, mock_blog_client):
        """Test blog generation with empty keywords list"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic",
            target_keywords=[]
        )

        # Should handle empty list
        assert content is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_special_characters_in_topic(self, mock_anthropic_class, mock_blog_client):
        """Test blog generation with special characters in topic"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        special_topic = "How to Organize Cards: A Guide for \"Battle-Ready\" Players! 🎯"
        content, path = agent.generate_blog_post(topic=special_topic)

        # Should handle special characters
        assert content is not None
        assert path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_api_error_propagates(self, mock_anthropic_class, mock_error_client):
        """Test that API errors are properly propagated"""
        mock_anthropic_class.return_value = mock_error_client

        agent = BlogAgent()

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            agent.generate_blog_post(topic="Test Topic")

        assert "API rate limit exceeded" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_very_small_word_count(self, mock_anthropic_class, mock_blog_client):
        """Test blog generation with very small word count"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic",
            word_count=100
        )

        # Verify word count was included
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "100 words" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_very_large_word_count(self, mock_anthropic_class, mock_blog_client):
        """Test blog generation with very large word count"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic",
            word_count=5000
        )

        # Verify word count was included
        call_args = mock_blog_client.messages.create.call_args
        prompt = call_args.kwargs["messages"][0]["content"]
        assert "5000 words" in prompt


class TestReturnTypes:
    """Test suite for verifying correct return types"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_post_returns_tuple(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that generate_blog_post returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        result = agent.generate_blog_post(topic="Test")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_listicle_returns_tuple(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that generate_listicle returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        result = agent.generate_listicle(topic="Test")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_how_to_guide_returns_tuple(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that generate_how_to_guide returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        result = agent.generate_how_to_guide(topic="Test")

        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_blog_series_returns_list_of_tuples(
        self, mock_anthropic_class, mock_blog_client
    ):
        """Test that generate_blog_series returns list of (content, path) tuples"""
        mock_anthropic_class.return_value = mock_blog_client

        agent = BlogAgent()
        result = agent.generate_blog_series(series_topic="Test Series")

        assert isinstance(result, list)
        assert len(result) > 0

        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            content, path = item
            assert isinstance(content, str)
            assert isinstance(path, Path)
