"""
Unit tests for BaseAgent class.

Tests cover:
- Agent initialization
- Brand context loading
- System prompt building
- Content generation (success and error cases)
- File output operations
- Combined generate-and-save workflow
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from datetime import datetime

from agents.base_agent import BaseAgent
from config.config import (
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    BRAND_NAME,
    BRAND_TAGLINE,
    BRAND_PROMISE
)


class TestBaseAgentInitialization:
    """Test suite for BaseAgent initialization"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_defaults(self, mock_anthropic_class, mock_anthropic_client):
        """Test agent initialization with default parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")

        assert agent.agent_name == "TestAgent"
        assert agent.model == DEFAULT_MODEL
        assert agent.client is not None
        assert agent.brand_context is not None
        mock_anthropic_class.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_with_custom_model(self, mock_anthropic_class, mock_anthropic_client):
        """Test agent initialization with custom model"""
        mock_anthropic_class.return_value = mock_anthropic_client

        custom_model = "claude-opus-4-20250514"
        agent = BaseAgent(agent_name="CustomAgent", model=custom_model)

        assert agent.agent_name == "CustomAgent"
        assert agent.model == custom_model

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_init_loads_brand_context(self, mock_anthropic_class, mock_anthropic_client):
        """Test that initialization loads brand context"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")

        # Verify brand context includes core identity
        assert "brand_name" in agent.brand_context
        assert "tagline" in agent.brand_context
        assert "promise" in agent.brand_context
        assert agent.brand_context["brand_name"] == BRAND_NAME
        assert agent.brand_context["tagline"] == BRAND_TAGLINE
        assert agent.brand_context["promise"] == BRAND_PROMISE


class TestBrandContextLoading:
    """Test suite for brand context loading"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_load_brand_context_includes_core_values(self, mock_anthropic_class, mock_anthropic_client):
        """Test that core brand values are loaded"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        context = agent.brand_context

        assert context["brand_name"] == BRAND_NAME
        assert context["tagline"] == BRAND_TAGLINE
        assert context["promise"] == BRAND_PROMISE

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.base_agent.BRAND_VOICE_PATH')
    def test_load_brand_context_with_existing_files(
        self, mock_voice_path, mock_anthropic_class, mock_anthropic_client
    ):
        """Test loading brand context when files exist"""
        mock_anthropic_class.return_value = mock_anthropic_client
        mock_voice_path.exists.return_value = True
        mock_voice_path.read_text.return_value = "Test brand voice content"

        agent = BaseAgent(agent_name="TestAgent")

        # Verify brand voice was loaded
        assert "brand_voice" in agent.brand_context
        assert agent.brand_context["brand_voice"] == "Test brand voice content"

    @patch('agents.base_agent.anthropic.Anthropic')
    @patch('agents.base_agent.BRAND_VOICE_PATH')
    def test_load_brand_context_with_missing_files(
        self, mock_voice_path, mock_anthropic_class, mock_anthropic_client
    ):
        """Test loading brand context when files don't exist"""
        mock_anthropic_class.return_value = mock_anthropic_client
        mock_voice_path.exists.return_value = False

        agent = BaseAgent(agent_name="TestAgent")

        # Verify brand voice is not in context when file doesn't exist
        assert "brand_voice" not in agent.brand_context or agent.brand_context.get("brand_voice") is None


class TestSystemPromptBuilding:
    """Test suite for system prompt building"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_build_system_prompt_basic(self, mock_anthropic_class, mock_anthropic_client):
        """Test building basic system prompt"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        prompt = agent._build_system_prompt()

        # Verify prompt contains brand identity
        assert BRAND_NAME in prompt
        assert BRAND_TAGLINE in prompt
        assert BRAND_PROMISE in prompt
        assert "BRAND IDENTITY:" in prompt
        assert "TCG storage brand" in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_build_system_prompt_with_additional_context(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test building system prompt with additional context"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        additional = "You are creating blog content focused on tactical gear."
        prompt = agent._build_system_prompt(additional_context=additional)

        # Verify additional context is included
        assert additional in prompt
        assert BRAND_NAME in prompt

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_build_system_prompt_includes_content_guidelines(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test that system prompt includes content creation guidelines"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        prompt = agent._build_system_prompt()

        # Verify key content guidelines are present
        assert "battle-ready equipment" in prompt.lower()
        assert "serious players" in prompt.lower()
        assert "Show Up Battle Ready" in prompt


class TestContentGeneration:
    """Test suite for content generation"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_success(self, mock_anthropic_class, mock_anthropic_client):
        """Test successful content generation"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        result = agent.generate_content("Test prompt")

        # Verify content was generated
        assert result is not None
        assert isinstance(result, str)
        mock_anthropic_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_with_custom_parameters(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test content generation with custom parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        result = agent.generate_content(
            prompt="Test prompt",
            system_context="Additional context",
            max_tokens=2000,
            temperature=0.7
        )

        # Verify API was called with correct parameters
        call_args = mock_anthropic_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 2000
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["model"] == agent.model

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_api_error(self, mock_anthropic_class, mock_error_client):
        """Test handling of API errors during content generation"""
        mock_anthropic_class.return_value = mock_error_client

        agent = BaseAgent(agent_name="TestAgent")

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            agent.generate_content("Test prompt")

        assert "API rate limit exceeded" in str(exc_info.value)

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_content_builds_system_prompt(
        self, mock_anthropic_class, mock_anthropic_client
    ):
        """Test that generate_content builds system prompt correctly"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        agent.generate_content("Test prompt", system_context="Extra context")

        # Verify system prompt was built and passed to API
        call_args = mock_anthropic_client.messages.create.call_args
        system_prompt = call_args.kwargs["system"]
        assert BRAND_NAME in system_prompt
        assert "Extra context" in system_prompt


class TestSaveOutput:
    """Test suite for saving output to files"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_save_output_with_custom_filename(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test saving output with custom filename"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        content = "Test content"
        filename = "test_output.md"

        output_path = agent.save_output(content, temp_output_dir, filename=filename)

        # Verify file was created
        assert output_path.exists()
        assert output_path.name == filename
        assert output_path.read_text() == content

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_save_output_with_generated_filename(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test saving output with auto-generated filename"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="BlogAgent")
        content = "Auto-generated filename test"

        output_path = agent.save_output(content, temp_output_dir)

        # Verify file was created with agent name
        assert output_path.exists()
        assert output_path.name.startswith("BlogAgent_")
        assert output_path.suffix == ".md"
        assert output_path.read_text() == content

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_save_output_with_metadata(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test saving output with metadata"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        content = "Content with metadata"
        metadata = {
            "topic": "Test Topic",
            "keywords": ["test", "metadata"],
            "pillar": "Test Pillar"
        }

        output_path = agent.save_output(
            content, temp_output_dir, filename="test.md", metadata=metadata
        )

        # Verify content file exists
        assert output_path.exists()

        # Verify metadata file exists
        metadata_path = temp_output_dir / "test_metadata.json"
        assert metadata_path.exists()

        # Verify metadata content
        saved_metadata = json.loads(metadata_path.read_text())
        assert saved_metadata == metadata

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_save_output_returns_path(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test that save_output returns the correct path"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        content = "Path test"

        output_path = agent.save_output(content, temp_output_dir, filename="path_test.md")

        # Verify returned path is correct
        assert isinstance(output_path, Path)
        assert output_path == temp_output_dir / "path_test.md"


class TestGenerateAndSave:
    """Test suite for combined generate and save workflow"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_and_save_basic(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test basic generate and save workflow"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        content, path = agent.generate_and_save(
            prompt="Test prompt",
            output_dir=temp_output_dir,
            filename="combined_test.md"
        )

        # Verify content was generated
        assert content is not None
        assert isinstance(content, str)

        # Verify file was saved
        assert path.exists()
        assert path.read_text() == content

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_and_save_with_metadata(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test generate and save with metadata"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        metadata = {"test": "metadata"}

        content, path = agent.generate_and_save(
            prompt="Test prompt",
            output_dir=temp_output_dir,
            filename="meta_test.md",
            metadata=metadata
        )

        # Verify metadata file was created
        metadata_path = temp_output_dir / "meta_test_metadata.json"
        assert metadata_path.exists()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_and_save_with_custom_params(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test generate and save with custom generation parameters"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        content, path = agent.generate_and_save(
            prompt="Test prompt",
            output_dir=temp_output_dir,
            system_context="Custom context",
            max_tokens=3000,
            temperature=0.5
        )

        # Verify API was called with custom parameters
        call_args = mock_anthropic_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 3000
        assert call_args.kwargs["temperature"] == 0.5

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_generate_and_save_returns_tuple(
        self, mock_anthropic_class, mock_anthropic_client, temp_output_dir
    ):
        """Test that generate_and_save returns (content, path) tuple"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        result = agent.generate_and_save(
            prompt="Test prompt",
            output_dir=temp_output_dir
        )

        # Verify return type is tuple
        assert isinstance(result, tuple)
        assert len(result) == 2

        content, path = result
        assert isinstance(content, str)
        assert isinstance(path, Path)


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_empty_prompt(self, mock_anthropic_class, mock_anthropic_client):
        """Test handling of empty prompt"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        result = agent.generate_content("")

        # Should still call API even with empty prompt
        assert result is not None
        mock_anthropic_client.messages.create.assert_called_once()

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_very_long_prompt(self, mock_anthropic_class, mock_anthropic_client):
        """Test handling of very long prompts"""
        mock_anthropic_class.return_value = mock_anthropic_client

        agent = BaseAgent(agent_name="TestAgent")
        long_prompt = "Test prompt " * 1000
        result = agent.generate_content(long_prompt)

        # Should handle long prompts
        assert result is not None

    @patch('agents.base_agent.anthropic.Anthropic')
    def test_special_characters_in_content(
        self, mock_anthropic_class, temp_output_dir
    ):
        """Test saving content with special characters"""
        mock_client = Mock()
        mock_client.messages.create.return_value = Mock(
            content=[Mock(text="Content with special chars: émojis 🎯, quotes \"test\", newlines\n")]
        )
        mock_anthropic_class.return_value = mock_client

        agent = BaseAgent(agent_name="TestAgent")
        content = "Content with émojis 🎯 and special chars"

        output_path = agent.save_output(content, temp_output_dir, filename="special.md")

        # Verify file was saved correctly
        assert output_path.exists()
        assert output_path.read_text() == content
