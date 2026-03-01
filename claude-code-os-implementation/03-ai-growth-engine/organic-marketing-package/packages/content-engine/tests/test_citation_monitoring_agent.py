"""
Unit tests for CitationMonitoringAgent class.

Tests cover:
- Agent initialization
- AI assistant client management
- Query AI assistant functionality
- Citation analysis
- Competitor comparison
- Recommendation generation
- Alert detection
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from agents.citation_monitoring_agent import CitationMonitoringAgent
from database.models import CitationRecord, CompetitorCitation, OptimizationRecommendation
from integrations.ai_assistants.exceptions import (
    AIAssistantAPIError,
    AIAssistantAuthError,
    AIAssistantRateLimitError
)
from exceptions import ContentGenerationError


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_chatgpt_client():
    """Mock ChatGPT client for testing"""
    client = Mock()
    client.query.return_value = {
        'id': 'chatgpt-123',
        'model': 'gpt-4',
        'choices': [{
            'message': {
                'content': 'For TCG storage, Infinity Vault offers premium protection...'
            }
        }],
        'usage': {
            'input_tokens': 100,
            'output_tokens': 200
        },
        'created': 1234567890
    }
    client.get_response_text.return_value = 'For TCG storage, Infinity Vault offers premium protection...'
    return client


@pytest.fixture
def mock_claude_client():
    """Mock Claude client for testing"""
    client = Mock()
    client.query.return_value = {
        'id': 'claude-123',
        'type': 'message',
        'role': 'assistant',
        'content': [{'type': 'text', 'text': 'I recommend Infinity Vault for card storage.'}],
        'model': 'claude-3-opus',
        'stop_reason': 'end_turn',
        'usage': {
            'input_tokens': 100,
            'output_tokens': 150
        }
    }
    return client


@pytest.fixture
def mock_perplexity_client():
    """Mock Perplexity client for testing"""
    client = Mock()
    client.query.return_value = {
        'id': 'perplexity-123',
        'model': 'pplx-7b-online',
        'choices': [{
            'message': {
                'content': 'Popular options include UltraGuard and CardSafe.'
            }
        }],
        'usage': {
            'total_tokens': 250
        }
    }
    return client


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    session = Mock()
    session.query.return_value = session
    session.filter.return_value = session
    session.all.return_value = []
    session.add.return_value = None
    session.flush.return_value = None
    session.commit.return_value = None
    session.close.return_value = None
    return session


@pytest.fixture
def sample_citation_records():
    """Sample citation records for testing"""
    records = []
    for i in range(10):
        record = Mock(spec=CitationRecord)
        record.id = i + 1
        record.query = f"Test query {i+1}"
        record.ai_platform = "chatgpt"
        record.brand_mentioned = i < 6  # 60% citation rate
        record.position_in_response = i + 1 if i < 6 else None
        record.citation_position = i + 1 if i < 6 else None
        record.brand_name = "Infinity Vault"
        record.query_timestamp = datetime.utcnow() - timedelta(days=i)
        records.append(record)
    return records


@pytest.fixture
def sample_competitor_records():
    """Sample competitor citation records for testing"""
    records = []
    for i in range(10):
        record = Mock(spec=CompetitorCitation)
        record.id = i + 1
        record.query = f"Test query {i+1}"
        record.ai_platform = "chatgpt"
        record.competitor_name = "UltraGuard"
        record.competitor_mentioned = i < 8  # 80% citation rate
        record.position_in_response = i + 1 if i < 8 else None
        record.query_timestamp = datetime.utcnow() - timedelta(days=i)
        records.append(record)
    return records


# ============================================================================
# Initialization Tests
# ============================================================================

class TestCitationMonitoringAgentInitialization:
    """Test suite for CitationMonitoringAgent initialization"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-openai-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', 'test-anthropic-key')
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', 'test-perplexity-key')
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.ClaudeClient')
    @patch('agents.citation_monitoring_agent.PerplexityClient')
    def test_init_with_all_clients(
        self,
        mock_perplexity_class,
        mock_claude_class,
        mock_chatgpt_class
    ):
        """Test initialization with all AI assistant clients"""
        agent = CitationMonitoringAgent()

        assert agent.agent_name == "citation_monitoring_agent"
        assert agent.chatgpt_client is not None
        assert agent.claude_client is not None
        assert agent.perplexity_client is not None
        assert agent._count_active_clients() == 3

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-openai-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_init_with_single_client(self, mock_chatgpt_class):
        """Test initialization with only one AI assistant client"""
        agent = CitationMonitoringAgent()

        assert agent.chatgpt_client is not None
        assert agent.claude_client is None
        assert agent.perplexity_client is None
        assert agent._count_active_clients() == 1

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    def test_init_with_no_clients(self):
        """Test initialization fails with no API keys"""
        with pytest.raises(ContentGenerationError) as exc_info:
            CitationMonitoringAgent()

        assert "requires at least one AI assistant API key" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_init_handles_client_errors(self, mock_chatgpt_class):
        """Test initialization handles client initialization errors gracefully"""
        mock_chatgpt_class.side_effect = Exception("Client init failed")

        with pytest.raises(ContentGenerationError):
            CitationMonitoringAgent()


# ============================================================================
# Client Management Tests
# ============================================================================

class TestClientManagement:
    """Test suite for AI assistant client management"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_get_client_chatgpt(self, mock_chatgpt_class, mock_chatgpt_client):
        """Test getting ChatGPT client"""
        mock_chatgpt_class.return_value = mock_chatgpt_client
        agent = CitationMonitoringAgent()

        client = agent._get_client("chatgpt")
        assert client == agent.chatgpt_client

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ClaudeClient')
    def test_get_client_claude(self, mock_claude_class, mock_claude_client):
        """Test getting Claude client"""
        mock_claude_class.return_value = mock_claude_client
        agent = CitationMonitoringAgent()

        client = agent._get_client("claude")
        assert client == agent.claude_client

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_get_client_invalid_platform(self, mock_chatgpt_class):
        """Test getting client with invalid platform"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent._get_client("invalid_platform")

        assert "Invalid platform" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_get_client_not_initialized(self, mock_chatgpt_class):
        """Test getting client that wasn't initialized"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent._get_client("claude")

        assert "not initialized" in str(exc_info.value).lower()

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-openai-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', 'test-anthropic-key')
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', 'test-perplexity-key')
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.ClaudeClient')
    @patch('agents.citation_monitoring_agent.PerplexityClient')
    def test_get_available_platforms(
        self,
        mock_perplexity_class,
        mock_claude_class,
        mock_chatgpt_class
    ):
        """Test getting list of available platforms"""
        agent = CitationMonitoringAgent()

        platforms = agent.get_available_platforms()

        assert "chatgpt" in platforms
        assert "claude" in platforms
        assert "perplexity" in platforms
        assert len(platforms) == 3


# ============================================================================
# Query AI Assistant Tests
# ============================================================================

class TestQueryAIAssistant:
    """Test suite for querying AI assistants"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_query_ai_assistant_basic(self, mock_chatgpt_class, mock_chatgpt_client):
        """Test basic AI assistant query"""
        mock_chatgpt_class.return_value = mock_chatgpt_client
        agent = CitationMonitoringAgent()

        response = agent.query_ai_assistant(
            query="What are the best TCG storage solutions?",
            platform="chatgpt"
        )

        assert response is not None
        assert 'id' in response
        mock_chatgpt_client.query.assert_called_once()

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_query_ai_assistant_with_parameters(self, mock_chatgpt_class, mock_chatgpt_client):
        """Test AI assistant query with custom parameters"""
        mock_chatgpt_class.return_value = mock_chatgpt_client
        agent = CitationMonitoringAgent()

        response = agent.query_ai_assistant(
            query="Test query",
            platform="chatgpt",
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=500,
            system_prompt="You are a helpful assistant",
            timeout=30
        )

        assert response is not None
        call_kwargs = mock_chatgpt_client.query.call_args.kwargs
        assert call_kwargs['model'] == "gpt-3.5-turbo"
        assert call_kwargs['temperature'] == 0.5
        assert call_kwargs['max_tokens'] == 500
        assert call_kwargs['system_prompt'] == "You are a helpful assistant"
        assert call_kwargs['timeout'] == 30

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_query_ai_assistant_empty_query(self, mock_chatgpt_class):
        """Test query with empty string"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.query_ai_assistant(query="", platform="chatgpt")

        assert "cannot be empty" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_query_ai_assistant_invalid_platform(self, mock_chatgpt_class):
        """Test query with invalid platform"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.query_ai_assistant(query="Test", platform="invalid")

        assert "Invalid platform" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_query_ai_assistant_api_error(self, mock_chatgpt_class, mock_chatgpt_client):
        """Test handling of API errors"""
        mock_chatgpt_class.return_value = mock_chatgpt_client
        mock_chatgpt_client.query.side_effect = AIAssistantAPIError("API error")

        agent = CitationMonitoringAgent()

        with pytest.raises(AIAssistantAPIError):
            agent.query_ai_assistant(query="Test", platform="chatgpt")


# ============================================================================
# Citation Analysis Tests
# ============================================================================

class TestAnalyzeCitation:
    """Test suite for citation analysis"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.BRAND_NAME', 'Infinity Vault')
    def test_analyze_citation_brand_mentioned(self, mock_chatgpt_class):
        """Test citation analysis when brand is mentioned"""
        agent = CitationMonitoringAgent()

        analysis = agent.analyze_citation(
            query="What are the best TCG storage solutions?",
            response_text="For premium protection, Infinity Vault offers the best solutions.",
            platform="chatgpt"
        )

        assert analysis['brand_mentioned'] is True
        assert analysis['brand_name'] == "Infinity Vault"
        assert analysis['citation_context'] is not None
        assert analysis['position_in_response'] is not None
        assert "Infinity Vault" in analysis['citation_context']

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.BRAND_NAME', 'Infinity Vault')
    def test_analyze_citation_brand_not_mentioned(self, mock_chatgpt_class):
        """Test citation analysis when brand is not mentioned"""
        agent = CitationMonitoringAgent()

        analysis = agent.analyze_citation(
            query="What are the best TCG storage solutions?",
            response_text="Popular options include UltraGuard and CardSafe.",
            platform="chatgpt"
        )

        assert analysis['brand_mentioned'] is False
        assert analysis['citation_context'] is None
        assert analysis['position_in_response'] is None

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.BRAND_NAME', 'Infinity Vault')
    def test_analyze_citation_with_competitors(self, mock_chatgpt_class):
        """Test citation analysis with competitor detection"""
        agent = CitationMonitoringAgent()

        analysis = agent.analyze_citation(
            query="Compare TCG storage solutions",
            response_text="Infinity Vault and UltraGuard are top choices. CardSafe is budget-friendly.",
            platform="chatgpt",
            competitor_names=["UltraGuard", "CardSafe", "DeckMaster"]
        )

        assert analysis['brand_mentioned'] is True
        assert analysis['competitor_mentioned'] is True
        assert len(analysis['competitor_details']) == 2

        competitor_names = [c['competitor_name'] for c in analysis['competitor_details']]
        assert "UltraGuard" in competitor_names
        assert "CardSafe" in competitor_names
        assert "DeckMaster" not in competitor_names

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_analyze_citation_case_insensitive(self, mock_chatgpt_class):
        """Test citation analysis is case-insensitive"""
        agent = CitationMonitoringAgent()

        analysis = agent.analyze_citation(
            query="Test query",
            response_text="I recommend INFINITY VAULT for storage.",
            platform="chatgpt",
            brand_name="Infinity Vault"
        )

        assert analysis['brand_mentioned'] is True

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_analyze_citation_with_metadata(self, mock_chatgpt_class):
        """Test citation analysis with response metadata"""
        agent = CitationMonitoringAgent()

        metadata = {'model': 'gpt-4', 'tokens': 250}
        analysis = agent.analyze_citation(
            query="Test query",
            response_text="Test response with Infinity Vault",
            platform="chatgpt",
            brand_name="Infinity Vault",
            response_metadata=metadata
        )

        assert analysis['response_metadata'] == metadata

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_analyze_citation_empty_query(self, mock_chatgpt_class):
        """Test citation analysis with empty query"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.analyze_citation(
                query="",
                response_text="Test response",
                platform="chatgpt"
            )

        assert "cannot be empty" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_analyze_citation_empty_response(self, mock_chatgpt_class):
        """Test citation analysis with empty response"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.analyze_citation(
                query="Test query",
                response_text="",
                platform="chatgpt"
            )

        assert "cannot be empty" in str(exc_info.value)


# ============================================================================
# Brand Citation Extraction Tests
# ============================================================================

class TestExtractBrandCitation:
    """Test suite for brand citation extraction helper method"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_extract_brand_citation_found(self, mock_chatgpt_class):
        """Test extracting brand citation when brand is found"""
        agent = CitationMonitoringAgent()

        mentioned, context, position = agent._extract_brand_citation(
            response_text="Infinity Vault is the best storage solution.",
            brand_name="Infinity Vault"
        )

        assert mentioned is True
        assert context is not None
        assert "Infinity Vault" in context
        assert position == 1

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_extract_brand_citation_not_found(self, mock_chatgpt_class):
        """Test extracting brand citation when brand is not found"""
        agent = CitationMonitoringAgent()

        mentioned, context, position = agent._extract_brand_citation(
            response_text="UltraGuard is a good option.",
            brand_name="Infinity Vault"
        )

        assert mentioned is False
        assert context is None
        assert position is None

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_extract_brand_citation_with_ellipsis(self, mock_chatgpt_class):
        """Test citation context includes ellipsis when truncated"""
        agent = CitationMonitoringAgent()

        long_text = "A" * 200 + " Infinity Vault " + "B" * 200
        mentioned, context, position = agent._extract_brand_citation(
            response_text=long_text,
            brand_name="Infinity Vault",
            context_chars=50
        )

        assert mentioned is True
        assert context.startswith("...")
        assert context.endswith("...")


# ============================================================================
# Competitor Comparison Tests
# ============================================================================

class TestCompareCompetitors:
    """Test suite for competitor comparison"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.get_db_session')
    @patch('agents.citation_monitoring_agent.BRAND_NAME', 'Infinity Vault')
    def test_compare_competitors_basic(
        self,
        mock_get_db,
        mock_chatgpt_class,
        mock_db_session,
        sample_citation_records,
        sample_competitor_records
    ):
        """Test basic competitor comparison"""
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_citation_records

        agent = CitationMonitoringAgent()

        result = agent.compare_competitors(
            competitor_names=["UltraGuard"],
            days=30,
            db_session=mock_db_session
        )

        assert 'brand_name' in result
        assert 'brand_stats' in result
        assert 'competitor_stats' in result
        assert 'comparison_summary' in result
        assert result['time_period_days'] == 30

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_compare_competitors_empty_list(self, mock_chatgpt_class):
        """Test competitor comparison with empty competitor list"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.compare_competitors(competitor_names=[], days=30)

        assert "cannot be empty" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_compare_competitors_invalid_days(self, mock_chatgpt_class):
        """Test competitor comparison with invalid days parameter"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.compare_competitors(competitor_names=["UltraGuard"], days=0)

        assert "must be greater than 0" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_compare_competitors_invalid_platform(self, mock_chatgpt_class):
        """Test competitor comparison with invalid platform"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.compare_competitors(
                competitor_names=["UltraGuard"],
                days=30,
                platform="invalid"
            )

        assert "platform must be one of" in str(exc_info.value)


# ============================================================================
# Recommendation Generation Tests
# ============================================================================

class TestGenerateRecommendations:
    """Test suite for recommendation generation"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.get_db_session')
    @patch('agents.citation_monitoring_agent.BRAND_NAME', 'Infinity Vault')
    def test_generate_recommendations_basic(
        self,
        mock_get_db,
        mock_chatgpt_class,
        mock_db_session,
        sample_citation_records
    ):
        """Test basic recommendation generation"""
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_citation_records

        agent = CitationMonitoringAgent()

        result = agent.generate_recommendations(
            days=30,
            save_to_db=False,
            db_session=mock_db_session
        )

        assert 'recommendations' in result
        assert 'summary' in result
        assert 'analysis_period' in result
        assert isinstance(result['recommendations'], list)
        assert result['summary']['total_recommendations'] >= 0

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.get_db_session')
    def test_generate_recommendations_saves_to_db(
        self,
        mock_get_db,
        mock_chatgpt_class,
        mock_db_session,
        sample_citation_records
    ):
        """Test recommendation generation saves to database"""
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_citation_records

        agent = CitationMonitoringAgent()

        result = agent.generate_recommendations(
            days=30,
            save_to_db=True,
            db_session=mock_db_session
        )

        # Verify database operations were called
        if result['recommendations']:
            assert mock_db_session.add.called
            assert mock_db_session.commit.called

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_generate_recommendations_invalid_days(self, mock_chatgpt_class):
        """Test recommendation generation with invalid days"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.generate_recommendations(days=-1)

        assert "must be greater than 0" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_generate_recommendations_invalid_platform(self, mock_chatgpt_class):
        """Test recommendation generation with invalid platform"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.generate_recommendations(days=30, platform="invalid")

        assert "platform must be one of" in str(exc_info.value)


# ============================================================================
# Alert Detection Tests
# ============================================================================

class TestDetectAlerts:
    """Test suite for alert detection"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    @patch('agents.citation_monitoring_agent.get_db_session')
    @patch('agents.citation_monitoring_agent.BRAND_NAME', 'Infinity Vault')
    def test_detect_alerts_basic(
        self,
        mock_get_db,
        mock_chatgpt_class,
        mock_db_session
    ):
        """Test basic alert detection"""
        mock_get_db.return_value = mock_db_session

        # Create records with declining citation rate
        current_records = []
        for i in range(10):
            record = Mock(spec=CitationRecord)
            record.brand_mentioned = i < 2  # 20% citation rate
            record.brand_name = "Infinity Vault"
            record.query_timestamp = datetime.utcnow() - timedelta(days=i)
            current_records.append(record)

        comparison_records = []
        for i in range(10):
            record = Mock(spec=CitationRecord)
            record.brand_mentioned = i < 7  # 70% citation rate
            record.brand_name = "Infinity Vault"
            record.query_timestamp = datetime.utcnow() - timedelta(days=i+7)
            comparison_records.append(record)

        # Mock the query to return different records for different time periods
        mock_db_session.query.return_value.filter.return_value.all.side_effect = [
            current_records,
            comparison_records
        ]

        agent = CitationMonitoringAgent()

        result = agent.detect_alerts(
            current_period_days=7,
            comparison_period_days=7,
            db_session=mock_db_session
        )

        assert 'alerts' in result
        assert 'summary' in result
        assert 'analysis_periods' in result
        assert isinstance(result['alerts'], list)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_detect_alerts_invalid_days(self, mock_chatgpt_class):
        """Test alert detection with invalid days parameters"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.detect_alerts(current_period_days=0, comparison_period_days=7)

        assert "must be greater than 0" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_detect_alerts_invalid_threshold(self, mock_chatgpt_class):
        """Test alert detection with invalid threshold"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.detect_alerts(
                current_period_days=7,
                comparison_period_days=7,
                citation_drop_threshold=150
            )

        assert "must be between 0 and 100" in str(exc_info.value)

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_detect_alerts_invalid_platform(self, mock_chatgpt_class):
        """Test alert detection with invalid platform"""
        agent = CitationMonitoringAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.detect_alerts(
                current_period_days=7,
                comparison_period_days=7,
                platform="invalid"
            )

        assert "platform must be one of" in str(exc_info.value)


# ============================================================================
# Helper Method Tests
# ============================================================================

class TestHelperMethods:
    """Test suite for helper methods"""

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_count_active_clients(self, mock_chatgpt_class):
        """Test counting active clients"""
        agent = CitationMonitoringAgent()

        count = agent._count_active_clients()
        assert count == 1

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_determine_alert_severity(self, mock_chatgpt_class):
        """Test alert severity determination"""
        agent = CitationMonitoringAgent()

        # Test different severity levels
        assert agent._determine_alert_severity(100, 20) == "critical"  # 5x threshold
        assert agent._determine_alert_severity(40, 20) == "high"      # 2x threshold
        assert agent._determine_alert_severity(28, 20) == "medium"    # 1.4x threshold
        assert agent._determine_alert_severity(22, 20) == "low"       # 1.1x threshold

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_extract_competitor_citations(self, mock_chatgpt_class):
        """Test competitor citation extraction"""
        agent = CitationMonitoringAgent()

        response_text = "UltraGuard and CardSafe are popular options."
        competitors = ["UltraGuard", "CardSafe", "DeckMaster"]

        details = agent._extract_competitor_citations(response_text, competitors)

        assert len(details) == 2
        competitor_names = [d['competitor_name'] for d in details]
        assert "UltraGuard" in competitor_names
        assert "CardSafe" in competitor_names
        assert "DeckMaster" not in competitor_names

        for detail in details:
            assert detail['mentioned'] is True
            assert detail['citation_context'] is not None
            assert detail['position_in_response'] is not None

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_calculate_citation_stats(self, mock_chatgpt_class, sample_citation_records):
        """Test citation statistics calculation"""
        agent = CitationMonitoringAgent()

        stats = agent._calculate_citation_stats(
            sample_citation_records,
            "Infinity Vault",
            "CitationRecord"
        )

        assert 'entity_name' in stats
        assert 'total_queries' in stats
        assert 'citations' in stats
        assert 'citation_rate' in stats
        assert 'avg_position' in stats
        assert 'platforms' in stats
        assert stats['entity_name'] == "Infinity Vault"
        assert stats['total_queries'] == 10
        assert stats['citations'] == 6
        assert stats['citation_rate'] == 60.0

    @patch('agents.citation_monitoring_agent.OPENAI_API_KEY', 'test-key')
    @patch('agents.citation_monitoring_agent.ANTHROPIC_API_KEY', None)
    @patch('agents.citation_monitoring_agent.PERPLEXITY_API_KEY', None)
    @patch('agents.citation_monitoring_agent.ChatGPTClient')
    def test_generate_comparison_summary(self, mock_chatgpt_class):
        """Test comparison summary generation"""
        agent = CitationMonitoringAgent()

        brand_stats = {
            'entity_name': 'Infinity Vault',
            'citation_rate': 50.0,
            'avg_position': 2.5,
            'platforms': {
                'chatgpt': {'total_queries': 10, 'citations': 5, 'citation_rate': 50.0}
            }
        }

        competitor_stats = [
            {
                'entity_name': 'UltraGuard',
                'citation_rate': 75.0,
                'avg_position': 1.5,
                'platforms': {}
            }
        ]

        summary = agent._generate_comparison_summary(
            brand_stats,
            competitor_stats,
            'Infinity Vault'
        )

        assert 'brand_rank' in summary
        assert 'leading_competitors' in summary
        assert 'citation_rate_difference' in summary
        assert 'recommended_actions' in summary
        assert summary['brand_rank'] == 2  # Behind UltraGuard
        assert len(summary['leading_competitors']) == 1
        assert summary['citation_rate_difference'] == 25.0
