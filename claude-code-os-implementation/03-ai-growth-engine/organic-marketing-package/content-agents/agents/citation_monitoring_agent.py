"""
Citation Monitoring Agent

Monitors and analyzes how AI assistants (ChatGPT, Claude, Perplexity) mention
and cite the brand. Provides optimization recommendations based on citation patterns.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from database.models import CitationRecord, CompetitorCitation, OptimizationRecommendation
from database.connection import get_db_session
from integrations.ai_assistants.chatgpt_client import ChatGPTClient
from integrations.ai_assistants.claude_client import ClaudeClient
from integrations.ai_assistants.perplexity_client import PerplexityClient
from integrations.ai_assistants.exceptions import AIAssistantAPIError
from config.config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    PERPLEXITY_API_KEY,
    BRAND_NAME
)
from exceptions import ContentGenerationError


class CitationMonitoringAgent(BaseAgent):
    """Agent specialized in monitoring AI assistant citations and brand mentions"""

    def __init__(self):
        """
        Initialize the Citation Monitoring Agent

        Sets up connections to AI assistant clients (ChatGPT, Claude, Perplexity)
        and prepares database session for tracking citations.

        Raises:
            AgentInitializationError: If agent initialization fails
        """
        super().__init__(agent_name="citation_monitoring_agent")

        self.logger.info("Initializing AI assistant clients for citation monitoring")

        # Initialize AI assistant clients
        self.chatgpt_client: Optional[ChatGPTClient] = None
        self.claude_client: Optional[ClaudeClient] = None
        self.perplexity_client: Optional[PerplexityClient] = None

        # Initialize ChatGPT client if API key is available
        if OPENAI_API_KEY:
            try:
                self.chatgpt_client = ChatGPTClient(api_key=OPENAI_API_KEY)
                self.logger.info("ChatGPT client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize ChatGPT client: {e}")

        # Initialize Claude client if API key is available
        if ANTHROPIC_API_KEY:
            try:
                self.claude_client = ClaudeClient(api_key=ANTHROPIC_API_KEY)
                self.logger.info("Claude client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Claude client: {e}")

        # Initialize Perplexity client if API key is available
        if PERPLEXITY_API_KEY:
            try:
                self.perplexity_client = PerplexityClient(api_key=PERPLEXITY_API_KEY)
                self.logger.info("Perplexity client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Perplexity client: {e}")

        # Check if at least one client was initialized
        if not any([self.chatgpt_client, self.claude_client, self.perplexity_client]):
            self.logger.error("No AI assistant clients could be initialized")
            raise ContentGenerationError(
                "Citation monitoring agent requires at least one AI assistant API key"
            )

        self.logger.info(f"Citation monitoring agent initialized with {self._count_active_clients()} active clients")

    def _count_active_clients(self) -> int:
        """
        Count the number of active AI assistant clients

        Returns:
            Number of active clients
        """
        return sum([
            self.chatgpt_client is not None,
            self.claude_client is not None,
            self.perplexity_client is not None
        ])

    def _get_client(self, platform: str):
        """
        Get the appropriate AI assistant client for the given platform

        Args:
            platform: AI platform name (chatgpt, claude, perplexity)

        Returns:
            AI assistant client instance

        Raises:
            ValueError: If platform is invalid or client is not initialized
        """
        platform_lower = platform.lower()

        if platform_lower == "chatgpt":
            if not self.chatgpt_client:
                raise ValueError("ChatGPT client is not initialized")
            return self.chatgpt_client
        elif platform_lower == "claude":
            if not self.claude_client:
                raise ValueError("Claude client is not initialized")
            return self.claude_client
        elif platform_lower == "perplexity":
            if not self.perplexity_client:
                raise ValueError("Perplexity client is not initialized")
            return self.perplexity_client
        else:
            raise ValueError(f"Invalid platform: {platform}. Must be one of: chatgpt, claude, perplexity")

    def get_available_platforms(self) -> List[str]:
        """
        Get list of available AI platforms based on initialized clients

        Returns:
            List of platform names that are available
        """
        platforms = []
        if self.chatgpt_client:
            platforms.append("chatgpt")
        if self.claude_client:
            platforms.append("claude")
        if self.perplexity_client:
            platforms.append("perplexity")
        return platforms

    def query_ai_assistant(
        self,
        query: str,
        platform: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query an AI assistant platform with a specific query

        This method queries the specified AI platform (ChatGPT, Claude, or Perplexity)
        and returns the complete response. It handles platform-specific client
        initialization and error handling.

        Args:
            query: The user query/prompt to send to the AI assistant
            platform: AI platform to query (chatgpt, claude, perplexity)
            model: Optional model override (uses client default if not provided)
            temperature: Optional temperature override for response randomness
            max_tokens: Optional maximum tokens in response
            system_prompt: Optional system prompt to set context
            timeout: Optional request timeout in seconds

        Returns:
            Dictionary containing the full API response from the AI platform.
            Response structure varies by platform:
            - ChatGPT/Perplexity: {id, model, choices, usage, created}
            - Claude: {id, type, role, content, model, stop_reason, usage}

        Raises:
            ValueError: If query is empty or platform is invalid/not initialized
            AIAssistantAPIError: If the API request fails
            ContentGenerationError: For other unexpected errors

        Example:
            >>> agent = CitationMonitoringAgent()
            >>> response = agent.query_ai_assistant(
            ...     query="What are the best TCG storage solutions?",
            ...     platform="chatgpt"
            ... )
            >>> # Process response based on platform
        """
        # Validate query parameter
        if not query or not query.strip():
            raise ValueError("Query parameter is required and cannot be empty")

        self.logger.info(f"Querying {platform} with query: {query[:100]}...")

        try:
            # Get the appropriate client for the platform
            client = self._get_client(platform)

            # Build kwargs for the query method
            query_kwargs = {}
            if model is not None:
                query_kwargs['model'] = model
            if temperature is not None:
                query_kwargs['temperature'] = temperature
            if max_tokens is not None:
                query_kwargs['max_tokens'] = max_tokens
            if system_prompt is not None:
                query_kwargs['system_prompt'] = system_prompt
            if timeout is not None:
                query_kwargs['timeout'] = timeout

            # Query the AI assistant
            response = client.query(query, **query_kwargs)

            self.logger.info(f"Successfully received response from {platform}")
            return response

        except ValueError as e:
            # Re-raise ValueError (platform validation errors)
            self.logger.error(f"Invalid platform or client error for {platform}: {e}")
            raise

        except AIAssistantAPIError as e:
            # Log and re-raise AI assistant API errors
            self.logger.error(f"API error querying {platform}: {e}")
            raise

        except Exception as e:
            # Catch any unexpected errors and wrap in ContentGenerationError
            error_msg = f"Unexpected error querying {platform}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg)
