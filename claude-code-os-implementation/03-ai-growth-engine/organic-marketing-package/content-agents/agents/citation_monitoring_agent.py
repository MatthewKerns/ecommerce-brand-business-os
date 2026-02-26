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
