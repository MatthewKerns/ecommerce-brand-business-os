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

    def analyze_citation(
        self,
        query: str,
        response_text: str,
        platform: str,
        brand_name: Optional[str] = None,
        competitor_names: Optional[List[str]] = None,
        response_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze an AI assistant response for brand and competitor citations

        This method performs comprehensive citation analysis including:
        - Brand mention detection (case-insensitive)
        - Citation context extraction (text snippet around the mention)
        - Position tracking (where in the response the brand appears)
        - Competitor mention detection

        Args:
            query: The original query sent to the AI assistant
            response_text: The full response text from the AI assistant
            platform: AI platform that generated the response (chatgpt, claude, perplexity)
            brand_name: Brand name to search for (defaults to BRAND_NAME from config)
            competitor_names: Optional list of competitor names to check for
            response_metadata: Optional metadata about the response (model, tokens, etc.)

        Returns:
            Dictionary containing citation analysis:
                - query: The original query
                - ai_platform: The AI platform
                - response_text: Full response text
                - brand_name: Brand name that was analyzed
                - brand_mentioned: Boolean indicating if brand was mentioned
                - citation_context: Text snippet showing how brand was mentioned (or None)
                - position_in_response: Position of first brand mention (1-based index, or None)
                - competitor_mentioned: Boolean indicating if any competitor was mentioned
                - competitor_details: List of dicts with competitor citation details
                - response_metadata: Optional metadata about the response

        Raises:
            ValueError: If required parameters are invalid
            ContentGenerationError: For unexpected errors during analysis

        Example:
            >>> agent = CitationMonitoringAgent()
            >>> analysis = agent.analyze_citation(
            ...     query="What are the best TCG storage solutions?",
            ...     response_text="For TCG storage, Infinity Vault offers...",
            ...     platform="chatgpt"
            ... )
            >>> if analysis['brand_mentioned']:
            ...     print(f"Brand mentioned at position {analysis['position_in_response']}")
        """
        # Validate required parameters
        if not query or not query.strip():
            raise ValueError("Query parameter is required and cannot be empty")
        if not response_text or not response_text.strip():
            raise ValueError("Response text parameter is required and cannot be empty")
        if not platform or not platform.strip():
            raise ValueError("Platform parameter is required and cannot be empty")

        # Use configured brand name if not provided
        if brand_name is None:
            brand_name = BRAND_NAME

        self.logger.info(f"Analyzing citation for brand '{brand_name}' in {platform} response")

        try:
            # Initialize result dictionary
            analysis_result = {
                'query': query,
                'ai_platform': platform.lower(),
                'response_text': response_text,
                'brand_name': brand_name,
                'brand_mentioned': False,
                'citation_context': None,
                'position_in_response': None,
                'competitor_mentioned': False,
                'competitor_details': [],
                'response_metadata': response_metadata or {}
            }

            # Analyze brand mention
            brand_mentioned, citation_context, position = self._extract_brand_citation(
                response_text,
                brand_name
            )

            analysis_result['brand_mentioned'] = brand_mentioned
            analysis_result['citation_context'] = citation_context
            analysis_result['position_in_response'] = position

            # Analyze competitor mentions if competitor names provided
            if competitor_names:
                competitor_details = self._extract_competitor_citations(
                    response_text,
                    competitor_names
                )
                analysis_result['competitor_mentioned'] = len(competitor_details) > 0
                analysis_result['competitor_details'] = competitor_details

            self.logger.info(
                f"Citation analysis complete: brand_mentioned={brand_mentioned}, "
                f"competitors_found={len(analysis_result['competitor_details'])}"
            )

            return analysis_result

        except ValueError as e:
            # Re-raise validation errors
            self.logger.error(f"Validation error in citation analysis: {e}")
            raise

        except Exception as e:
            # Catch any unexpected errors
            error_msg = f"Unexpected error analyzing citation: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg)

    def _extract_brand_citation(
        self,
        response_text: str,
        brand_name: str,
        context_chars: int = 150
    ) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Extract brand citation details from response text

        Args:
            response_text: Full response text to analyze
            brand_name: Brand name to search for
            context_chars: Number of characters to extract around the mention

        Returns:
            Tuple of (brand_mentioned, citation_context, position_in_response)
            - brand_mentioned: Boolean indicating if brand was found
            - citation_context: Text snippet around the mention (or None)
            - position_in_response: 1-based position of first mention (or None)
        """
        # Perform case-insensitive search
        response_lower = response_text.lower()
        brand_lower = brand_name.lower()

        # Check if brand is mentioned
        if brand_lower not in response_lower:
            return False, None, None

        # Find first occurrence position
        first_occurrence = response_lower.find(brand_lower)

        # Calculate position (1-based index of which mention this is in the text)
        # Count newlines or sentences before this point to get a position metric
        text_before = response_text[:first_occurrence]

        # Count approximate position: split by sentences/paragraphs
        sentences_before = text_before.count('.') + text_before.count('?') + text_before.count('!')
        position_in_response = sentences_before + 1  # 1-based position

        # Extract context around the mention
        start_pos = max(0, first_occurrence - context_chars)
        end_pos = min(len(response_text), first_occurrence + len(brand_name) + context_chars)

        citation_context = response_text[start_pos:end_pos].strip()

        # Add ellipsis if we truncated
        if start_pos > 0:
            citation_context = "..." + citation_context
        if end_pos < len(response_text):
            citation_context = citation_context + "..."

        return True, citation_context, position_in_response

    def _extract_competitor_citations(
        self,
        response_text: str,
        competitor_names: List[str],
        context_chars: int = 150
    ) -> List[Dict[str, Any]]:
        """
        Extract competitor citation details from response text

        Args:
            response_text: Full response text to analyze
            competitor_names: List of competitor names to search for
            context_chars: Number of characters to extract around each mention

        Returns:
            List of dictionaries containing competitor citation details:
                - competitor_name: Name of the competitor
                - mentioned: Boolean indicating if competitor was found
                - citation_context: Text snippet around the mention
                - position_in_response: 1-based position of first mention
        """
        competitor_details = []
        response_lower = response_text.lower()

        for competitor_name in competitor_names:
            competitor_lower = competitor_name.lower()

            # Check if competitor is mentioned
            if competitor_lower not in response_lower:
                continue

            # Find first occurrence position
            first_occurrence = response_lower.find(competitor_lower)

            # Calculate position
            text_before = response_text[:first_occurrence]
            sentences_before = text_before.count('.') + text_before.count('?') + text_before.count('!')
            position_in_response = sentences_before + 1

            # Extract context around the mention
            start_pos = max(0, first_occurrence - context_chars)
            end_pos = min(len(response_text), first_occurrence + len(competitor_name) + context_chars)

            citation_context = response_text[start_pos:end_pos].strip()

            # Add ellipsis if we truncated
            if start_pos > 0:
                citation_context = "..." + citation_context
            if end_pos < len(response_text):
                citation_context = citation_context + "..."

            competitor_details.append({
                'competitor_name': competitor_name,
                'mentioned': True,
                'citation_context': citation_context,
                'position_in_response': position_in_response
            })

        return competitor_details
