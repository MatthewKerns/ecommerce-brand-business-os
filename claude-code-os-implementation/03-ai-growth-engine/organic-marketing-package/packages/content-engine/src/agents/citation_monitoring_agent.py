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

    def compare_competitors(
        self,
        competitor_names: List[str],
        days: int = 30,
        platform: Optional[str] = None,
        brand_name: Optional[str] = None,
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Compare brand citation rates against competitor citation rates

        This method analyzes citation patterns over a specified time period and
        provides comparative metrics between the brand and competitors. It calculates
        citation rates, mention frequencies, and position analytics for both the brand
        and specified competitors.

        Args:
            competitor_names: List of competitor names to compare against
            days: Number of days to look back for citation data (default: 30)
            platform: Optional AI platform filter (chatgpt, claude, perplexity, or None for all)
            brand_name: Brand name to compare (defaults to BRAND_NAME from config)
            db_session: Optional database session (creates new if not provided)

        Returns:
            Dictionary containing competitor comparison analysis:
                - brand_name: The brand being analyzed
                - time_period_days: Number of days analyzed
                - platforms_analyzed: List of platforms included in analysis
                - brand_stats: Dict with brand citation statistics
                    - total_queries: Total queries executed
                    - citations: Number of times brand was cited
                    - citation_rate: Percentage of queries where brand was cited
                    - avg_position: Average position when mentioned
                    - platforms: Per-platform breakdown
                - competitor_stats: List of dicts with competitor statistics
                    - competitor_name: Name of competitor
                    - total_queries: Total queries executed
                    - citations: Number of times competitor was cited
                    - citation_rate: Percentage of queries where competitor was cited
                    - avg_position: Average position when mentioned
                    - platforms: Per-platform breakdown
                - comparison_summary: Summary insights
                    - brand_rank: Brand's rank among all entities (1 = best)
                    - leading_competitors: Competitors with higher citation rates
                    - citation_rate_difference: Percentage point difference vs top competitor
                    - recommended_actions: List of recommended actions based on comparison

        Raises:
            ValueError: If competitor_names is empty or days is invalid
            ContentGenerationError: For unexpected errors during comparison

        Example:
            >>> agent = CitationMonitoringAgent()
            >>> comparison = agent.compare_competitors(
            ...     competitor_names=["UltraGuard", "DeckMaster", "CardSafe"],
            ...     days=30,
            ...     platform="chatgpt"
            ... )
            >>> print(f"Brand citation rate: {comparison['brand_stats']['citation_rate']}%")
            >>> print(f"Brand rank: {comparison['comparison_summary']['brand_rank']}")
        """
        # Validate parameters
        if not competitor_names or len(competitor_names) == 0:
            raise ValueError("competitor_names parameter is required and cannot be empty")
        if days <= 0:
            raise ValueError("days parameter must be greater than 0")
        if platform and platform.lower() not in ["chatgpt", "claude", "perplexity"]:
            raise ValueError("platform must be one of: chatgpt, claude, perplexity, or None for all")

        # Use configured brand name if not provided
        if brand_name is None:
            brand_name = BRAND_NAME

        self.logger.info(
            f"Comparing brand '{brand_name}' against {len(competitor_names)} competitors "
            f"over {days} days (platform: {platform or 'all'})"
        )

        # Create database session if not provided
        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Build base query for citation records
            brand_query = db_session.query(CitationRecord).filter(
                CitationRecord.query_timestamp >= start_date,
                CitationRecord.query_timestamp <= end_date,
                CitationRecord.brand_name == brand_name
            )

            # Apply platform filter if specified
            if platform:
                brand_query = brand_query.filter(CitationRecord.ai_platform == platform.lower())

            # Get brand citation records
            brand_records = brand_query.all()

            # Calculate brand statistics
            brand_stats = self._calculate_citation_stats(
                brand_records,
                brand_name,
                "CitationRecord"
            )

            # Build base query for competitor citations
            competitor_query = db_session.query(CompetitorCitation).filter(
                CompetitorCitation.query_timestamp >= start_date,
                CompetitorCitation.query_timestamp <= end_date,
                CompetitorCitation.competitor_name.in_(competitor_names)
            )

            # Apply platform filter if specified
            if platform:
                competitor_query = competitor_query.filter(
                    CompetitorCitation.ai_platform == platform.lower()
                )

            # Get competitor citation records
            competitor_records = competitor_query.all()

            # Calculate competitor statistics (grouped by competitor name)
            competitor_stats = []
            for competitor_name in competitor_names:
                competitor_records_filtered = [
                    r for r in competitor_records if r.competitor_name == competitor_name
                ]
                stats = self._calculate_citation_stats(
                    competitor_records_filtered,
                    competitor_name,
                    "CompetitorCitation"
                )
                competitor_stats.append(stats)

            # Determine platforms analyzed
            platforms_analyzed = []
            if platform:
                platforms_analyzed = [platform.lower()]
            else:
                platforms_analyzed = ["chatgpt", "claude", "perplexity"]

            # Generate comparison summary
            comparison_summary = self._generate_comparison_summary(
                brand_stats,
                competitor_stats,
                brand_name
            )

            # Build result
            result = {
                'brand_name': brand_name,
                'time_period_days': days,
                'platforms_analyzed': platforms_analyzed,
                'brand_stats': brand_stats,
                'competitor_stats': competitor_stats,
                'comparison_summary': comparison_summary
            }

            self.logger.info(
                f"Competitor comparison complete: brand_rank={comparison_summary['brand_rank']}, "
                f"citation_rate={brand_stats['citation_rate']:.2f}%"
            )

            return result

        except ValueError as e:
            # Re-raise validation errors
            self.logger.error(f"Validation error in competitor comparison: {e}")
            raise

        except Exception as e:
            # Catch any unexpected errors
            error_msg = f"Unexpected error comparing competitors: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg)

        finally:
            # Close session if we created it
            if not session_provided and db_session:
                db_session.close()

    def _calculate_citation_stats(
        self,
        records: List[Any],
        entity_name: str,
        record_type: str
    ) -> Dict[str, Any]:
        """
        Calculate citation statistics for a brand or competitor

        Args:
            records: List of CitationRecord or CompetitorCitation objects
            entity_name: Name of the brand or competitor
            record_type: Type of record ("CitationRecord" or "CompetitorCitation")

        Returns:
            Dictionary containing citation statistics
        """
        total_queries = len(records)

        # Determine the mentioned field based on record type
        if record_type == "CitationRecord":
            citations = sum(1 for r in records if r.brand_mentioned)
            mentioned_records = [r for r in records if r.brand_mentioned]
        else:  # CompetitorCitation
            citations = sum(1 for r in records if r.competitor_mentioned)
            mentioned_records = [r for r in records if r.competitor_mentioned]

        # Calculate citation rate
        citation_rate = (citations / total_queries * 100) if total_queries > 0 else 0.0

        # Calculate average position
        positions = [r.position_in_response for r in mentioned_records if r.position_in_response is not None]
        avg_position = (sum(positions) / len(positions)) if positions else None

        # Calculate per-platform breakdown
        platforms = {}
        for platform_name in ["chatgpt", "claude", "perplexity"]:
            platform_records = [r for r in records if r.ai_platform == platform_name]
            platform_total = len(platform_records)

            if record_type == "CitationRecord":
                platform_citations = sum(1 for r in platform_records if r.brand_mentioned)
            else:
                platform_citations = sum(1 for r in platform_records if r.competitor_mentioned)

            platform_rate = (platform_citations / platform_total * 100) if platform_total > 0 else 0.0

            platforms[platform_name] = {
                'total_queries': platform_total,
                'citations': platform_citations,
                'citation_rate': platform_rate
            }

        return {
            'entity_name': entity_name,
            'total_queries': total_queries,
            'citations': citations,
            'citation_rate': citation_rate,
            'avg_position': avg_position,
            'platforms': platforms
        }

    def _generate_comparison_summary(
        self,
        brand_stats: Dict[str, Any],
        competitor_stats: List[Dict[str, Any]],
        brand_name: str
    ) -> Dict[str, Any]:
        """
        Generate comparison summary with insights and recommendations

        Args:
            brand_stats: Brand citation statistics
            competitor_stats: List of competitor citation statistics
            brand_name: Name of the brand

        Returns:
            Dictionary containing comparison summary
        """
        # Create sorted list of all entities by citation rate
        all_entities = [brand_stats] + competitor_stats
        sorted_entities = sorted(all_entities, key=lambda x: x['citation_rate'], reverse=True)

        # Find brand rank
        brand_rank = None
        for idx, entity in enumerate(sorted_entities):
            if entity['entity_name'] == brand_name:
                brand_rank = idx + 1  # 1-based rank
                break

        # Find leading competitors (those with higher citation rates)
        leading_competitors = [
            {
                'name': entity['entity_name'],
                'citation_rate': entity['citation_rate'],
                'difference': entity['citation_rate'] - brand_stats['citation_rate']
            }
            for entity in sorted_entities
            if entity['entity_name'] != brand_name and entity['citation_rate'] > brand_stats['citation_rate']
        ]

        # Calculate citation rate difference vs top competitor
        citation_rate_difference = None
        if leading_competitors:
            top_competitor = leading_competitors[0]
            citation_rate_difference = top_competitor['difference']

        # Generate recommended actions based on comparison
        recommended_actions = []
        if brand_rank and brand_rank > 1:
            recommended_actions.append(
                f"Brand is ranked #{brand_rank} in citation rate - consider optimizing content to improve visibility"
            )
        if leading_competitors:
            recommended_actions.append(
                f"Top competitor '{leading_competitors[0]['name']}' has {citation_rate_difference:.2f}% higher citation rate - analyze their content strategy"
            )
        if brand_stats['citation_rate'] < 50:
            recommended_actions.append(
                "Citation rate is below 50% - focus on improving content relevance and authority"
            )
        if brand_stats['avg_position'] and brand_stats['avg_position'] > 2:
            recommended_actions.append(
                f"Average citation position is {brand_stats['avg_position']:.1f} - work on being mentioned earlier in responses"
            )

        # Add platform-specific recommendations
        for platform_name, platform_stats in brand_stats['platforms'].items():
            if platform_stats['total_queries'] > 0 and platform_stats['citation_rate'] < 30:
                recommended_actions.append(
                    f"Low citation rate on {platform_name} ({platform_stats['citation_rate']:.1f}%) - optimize content for this platform"
                )

        if not recommended_actions:
            recommended_actions.append("Brand is performing well - maintain current content strategy")

        return {
            'brand_rank': brand_rank,
            'leading_competitors': leading_competitors,
            'citation_rate_difference': citation_rate_difference,
            'recommended_actions': recommended_actions
        }

    def generate_recommendations(
        self,
        days: int = 30,
        platform: Optional[str] = None,
        brand_name: Optional[str] = None,
        competitor_names: Optional[List[str]] = None,
        save_to_db: bool = True,
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Generate optimization recommendations based on citation analysis

        This method analyzes citation patterns over a specified time period and generates
        actionable recommendations to improve citation rates and positioning. It examines
        brand performance, competitor performance, platform-specific metrics, and content
        patterns to identify opportunities for improvement.

        Args:
            days: Number of days to analyze (default: 30)
            platform: Optional AI platform filter (chatgpt, claude, perplexity, or None for all)
            brand_name: Optional brand name override (uses BRAND_NAME from config if not provided)
            competitor_names: Optional list of competitor names to include in analysis
            save_to_db: Whether to save recommendations to database (default: True)
            db_session: Optional database session (creates new session if not provided)

        Returns:
            Dictionary containing:
            - recommendations: List of recommendation objects
                - id: Recommendation ID (if saved to DB)
                - type: Recommendation type (content/keyword/structure/technical/other)
                - title: Short title
                - description: Detailed description
                - priority: Priority level (high/medium/low)
                - expected_impact: Expected impact score (0-100)
                - implementation_effort: Estimated effort (low/medium/high)
                - ai_platform: Target platform or "all"
                - status: Status (pending)
            - summary: Overall summary
                - total_recommendations: Total number of recommendations generated
                - high_priority: Number of high priority recommendations
                - medium_priority: Number of medium priority recommendations
                - low_priority: Number of low priority recommendations
                - by_type: Breakdown by recommendation type
                - by_platform: Breakdown by platform
            - analysis_period: Analysis period details
                - start_date: Start of analysis period
                - end_date: End of analysis period
                - days: Number of days analyzed
                - platform: Platform filter (or "all")

        Raises:
            ValueError: If days is invalid or platform is invalid
            ContentGenerationError: For unexpected errors during recommendation generation

        Example:
            >>> agent = CitationMonitoringAgent()
            >>> result = agent.generate_recommendations(
            ...     days=30,
            ...     competitor_names=["UltraGuard", "DeckMaster"],
            ...     save_to_db=True
            ... )
            >>> print(f"Generated {result['summary']['total_recommendations']} recommendations")
            >>> for rec in result['recommendations']:
            ...     if rec['priority'] == 'high':
            ...         print(f"High Priority: {rec['title']}")
        """
        # Validate parameters
        if days <= 0:
            raise ValueError("days parameter must be greater than 0")
        if platform and platform.lower() not in ["chatgpt", "claude", "perplexity"]:
            raise ValueError("platform must be one of: chatgpt, claude, perplexity, or None for all")

        # Use configured brand name if not provided
        if brand_name is None:
            brand_name = BRAND_NAME

        self.logger.info(
            f"Generating optimization recommendations for '{brand_name}' "
            f"over {days} days (platform: {platform or 'all'})"
        )

        # Create database session if not provided
        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Build query for citation records
            citation_query = db_session.query(CitationRecord).filter(
                CitationRecord.query_timestamp >= start_date,
                CitationRecord.query_timestamp <= end_date,
                CitationRecord.brand_name == brand_name
            )

            # Apply platform filter if specified
            if platform:
                citation_query = citation_query.filter(CitationRecord.ai_platform == platform.lower())

            # Get citation records
            citation_records = citation_query.all()

            # Calculate basic statistics
            total_queries = len(citation_records)
            cited_queries = len([r for r in citation_records if r.brand_mentioned])
            citation_rate = (cited_queries / total_queries * 100) if total_queries > 0 else 0

            self.logger.info(
                f"Analyzed {total_queries} queries with {cited_queries} citations "
                f"(citation rate: {citation_rate:.1f}%)"
            )

            # Initialize recommendations list
            recommendations = []

            # 1. Analyze overall citation rate
            if total_queries > 0:
                if citation_rate < 30:
                    recommendations.append({
                        'type': 'content',
                        'title': 'Low overall citation rate - improve content authority',
                        'description': (
                            f"Brand citation rate is only {citation_rate:.1f}% over the past {days} days. "
                            f"Focus on creating more authoritative, comprehensive content that AI assistants "
                            f"are likely to reference. Consider: publishing detailed guides, original research, "
                            f"case studies, and expert analysis in your domain."
                        ),
                        'priority': 'high',
                        'expected_impact': 75,
                        'implementation_effort': 'high',
                        'ai_platform': platform or 'all'
                    })
                elif citation_rate < 50:
                    recommendations.append({
                        'type': 'content',
                        'title': 'Moderate citation rate - expand content coverage',
                        'description': (
                            f"Brand citation rate is {citation_rate:.1f}%. There's room for improvement. "
                            f"Expand content coverage to address more user queries in your domain. "
                            f"Analyze which queries result in citations vs. no citations to identify gaps."
                        ),
                        'priority': 'medium',
                        'expected_impact': 60,
                        'implementation_effort': 'medium',
                        'ai_platform': platform or 'all'
                    })

            # 2. Analyze citation positioning
            cited_records = [r for r in citation_records if r.brand_mentioned and r.citation_position]
            if cited_records:
                avg_position = sum(r.citation_position for r in cited_records) / len(cited_records)
                if avg_position > 3:
                    recommendations.append({
                        'type': 'content',
                        'title': 'Improve citation positioning - be mentioned earlier',
                        'description': (
                            f"Average citation position is {avg_position:.1f}. The brand is often mentioned "
                            f"later in AI responses rather than first. To improve positioning: become the "
                            f"primary authority in your niche, create highly-cited cornerstone content, "
                            f"and ensure content directly answers common user queries."
                        ),
                        'priority': 'high' if avg_position > 5 else 'medium',
                        'expected_impact': 70,
                        'implementation_effort': 'high',
                        'ai_platform': platform or 'all'
                    })

            # 3. Platform-specific analysis
            platform_stats = {}
            for platform_name in ['chatgpt', 'claude', 'perplexity']:
                platform_records = [r for r in citation_records if r.ai_platform == platform_name]
                if platform_records:
                    platform_cited = len([r for r in platform_records if r.brand_mentioned])
                    platform_rate = (platform_cited / len(platform_records) * 100)
                    platform_stats[platform_name] = {
                        'total': len(platform_records),
                        'cited': platform_cited,
                        'rate': platform_rate
                    }

                    if platform_rate < 25 and len(platform_records) >= 5:
                        recommendations.append({
                            'type': 'technical',
                            'title': f'Low citation rate on {platform_name.title()} - platform optimization',
                            'description': (
                                f"Citation rate on {platform_name.title()} is only {platform_rate:.1f}%. "
                                f"Different AI platforms have different citation preferences. Research how "
                                f"{platform_name.title()} selects sources and optimize content accordingly. "
                                f"Consider: structured data, clear factual statements, and authoritative sources."
                            ),
                            'priority': 'medium',
                            'expected_impact': 55,
                            'implementation_effort': 'medium',
                            'ai_platform': platform_name
                        })

            # 4. Competitor analysis (if competitor names provided)
            if competitor_names and len(competitor_names) > 0:
                try:
                    comparison = self.compare_competitors(
                        competitor_names=competitor_names,
                        days=days,
                        platform=platform,
                        brand_name=brand_name,
                        db_session=db_session
                    )

                    brand_rank = comparison['comparison_summary'].get('brand_rank')
                    if brand_rank and brand_rank > 1:
                        leading_competitors = comparison['comparison_summary'].get('leading_competitors', [])
                        if leading_competitors:
                            top_competitor = leading_competitors[0]
                            recommendations.append({
                                'type': 'content',
                                'title': 'Competitor analysis - learn from top performers',
                                'description': (
                                    f"Brand ranks #{brand_rank} in citation rate. "
                                    f"Top competitor '{top_competitor['name']}' has "
                                    f"{top_competitor['difference']:.1f}% higher citation rate. "
                                    f"Analyze their content strategy, topics covered, and content depth. "
                                    f"Identify content gaps where they are being cited but your brand is not."
                                ),
                                'priority': 'high',
                                'expected_impact': 80,
                                'implementation_effort': 'high',
                                'ai_platform': platform or 'all'
                            })
                except Exception as e:
                    self.logger.warning(f"Could not perform competitor analysis: {e}")

            # 5. Analyze query patterns for content gaps
            uncited_records = [r for r in citation_records if not r.brand_mentioned]
            if len(uncited_records) > len(citation_records) * 0.5:  # More than 50% uncited
                recommendations.append({
                    'type': 'keyword',
                    'title': 'Content gaps detected - analyze uncited queries',
                    'description': (
                        f"Over {len(uncited_records)} queries ({len(uncited_records)/len(citation_records)*100:.1f}%) "
                        f"did not result in brand citations. Analyze these queries to identify content gaps. "
                        f"Create targeted content addressing these specific user questions and needs."
                    ),
                    'priority': 'medium',
                    'expected_impact': 65,
                    'implementation_effort': 'medium',
                    'ai_platform': platform or 'all'
                })

            # 6. Freshness recommendation
            if total_queries > 0:
                recommendations.append({
                    'type': 'content',
                    'title': 'Maintain content freshness and relevance',
                    'description': (
                        "AI assistants favor recent, up-to-date content. Regularly update existing "
                        "content with new information, statistics, and examples. Publish new content "
                        "consistently to maintain visibility in AI assistant responses."
                    ),
                    'priority': 'low',
                    'expected_impact': 45,
                    'implementation_effort': 'low',
                    'ai_platform': platform or 'all'
                })

            # 7. Structured data recommendation
            if citation_rate < 60:
                recommendations.append({
                    'type': 'technical',
                    'title': 'Implement structured data markup',
                    'description': (
                        "Add schema.org structured data to your content to help AI assistants better "
                        "understand and extract information. Use appropriate schema types like Article, "
                        "Product, HowTo, FAQPage, etc. This can improve citation rates by making content "
                        "more machine-readable."
                    ),
                    'priority': 'medium',
                    'expected_impact': 50,
                    'implementation_effort': 'medium',
                    'ai_platform': platform or 'all'
                })

            self.logger.info(f"Generated {len(recommendations)} recommendations")

            # Save recommendations to database if requested
            saved_recommendations = []
            if save_to_db:
                for rec in recommendations:
                    try:
                        db_rec = OptimizationRecommendation(
                            recommendation_type=rec['type'],
                            title=rec['title'],
                            description=rec['description'],
                            priority=rec['priority'],
                            status='pending',
                            expected_impact=rec['expected_impact'],
                            implementation_effort=rec['implementation_effort'],
                            ai_platform=rec['ai_platform'],
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db_session.add(db_rec)
                        db_session.flush()  # Flush to get the ID

                        # Add ID to recommendation
                        rec['id'] = db_rec.id
                        rec['status'] = 'pending'
                        saved_recommendations.append(rec)

                        self.logger.debug(f"Saved recommendation {db_rec.id}: {rec['title']}")
                    except Exception as e:
                        self.logger.error(f"Error saving recommendation to database: {e}")
                        # Continue with next recommendation

                # Commit all recommendations
                db_session.commit()
                self.logger.info(f"Saved {len(saved_recommendations)} recommendations to database")
            else:
                # Just add status to each recommendation
                for rec in recommendations:
                    rec['status'] = 'pending'
                saved_recommendations = recommendations

            # Generate summary
            summary = {
                'total_recommendations': len(saved_recommendations),
                'high_priority': len([r for r in saved_recommendations if r['priority'] == 'high']),
                'medium_priority': len([r for r in saved_recommendations if r['priority'] == 'medium']),
                'low_priority': len([r for r in saved_recommendations if r['priority'] == 'low']),
                'by_type': {},
                'by_platform': {}
            }

            # Count by type
            for rec in saved_recommendations:
                rec_type = rec['type']
                summary['by_type'][rec_type] = summary['by_type'].get(rec_type, 0) + 1

            # Count by platform
            for rec in saved_recommendations:
                rec_platform = rec['ai_platform']
                summary['by_platform'][rec_platform] = summary['by_platform'].get(rec_platform, 0) + 1

            return {
                'recommendations': saved_recommendations,
                'summary': summary,
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days,
                    'platform': platform or 'all'
                }
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Log and wrap unexpected errors
            self.logger.error(f"Error generating recommendations: {e}", exc_info=True)
            raise ContentGenerationError(f"Failed to generate recommendations: {str(e)}")
        finally:
            # Close session if we created it
            if not session_provided and db_session:
                db_session.close()

    def detect_alerts(
        self,
        current_period_days: int = 7,
        comparison_period_days: int = 7,
        platform: Optional[str] = None,
        brand_name: Optional[str] = None,
        competitor_names: Optional[List[str]] = None,
        citation_drop_threshold: float = 20.0,
        competitor_advantage_threshold: float = 15.0,
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Detect alerts for citation rate drops and competitor citation gains

        This method analyzes citation patterns to identify potential issues requiring
        attention. It compares current citation rates against historical baselines and
        competitor performance to detect:
        1. Citation rate drops - when current citation rate drops significantly vs previous period
        2. Competitor gains - when competitors have significantly higher citation rates

        Args:
            current_period_days: Number of days for current analysis period (default: 7)
            comparison_period_days: Number of days for comparison period (default: 7)
            platform: Optional AI platform filter (chatgpt, claude, perplexity, or None for all)
            brand_name: Optional brand name override (uses BRAND_NAME from config if not provided)
            competitor_names: Optional list of competitor names to monitor
            citation_drop_threshold: Minimum percentage point drop to trigger alert (default: 20.0)
            competitor_advantage_threshold: Minimum percentage point advantage to trigger alert (default: 15.0)
            db_session: Optional database session (creates new session if not provided)

        Returns:
            Dictionary containing alert analysis:
            - alerts: List of alert objects
                - alert_type: Type of alert ("citation_rate_drop" or "competitor_gain")
                - severity: Severity level ("critical", "high", "medium", "low")
                - title: Short alert title
                - description: Detailed description
                - metrics: Relevant metrics for the alert
                - detected_at: When alert was detected
                - platform: Platform where alert was detected (or "all")
            - summary: Overall summary
                - total_alerts: Total number of alerts
                - critical_alerts: Number of critical severity alerts
                - high_alerts: Number of high severity alerts
                - medium_alerts: Number of medium severity alerts
                - low_alerts: Number of low severity alerts
                - by_type: Breakdown by alert type
                - by_platform: Breakdown by platform
            - analysis_periods: Analysis period details
                - current_period: Start and end dates for current period
                - comparison_period: Start and end dates for comparison period
                - platform: Platform filter (or "all")

        Raises:
            ValueError: If days parameters are invalid or thresholds are out of range
            ContentGenerationError: For unexpected errors during alert detection

        Example:
            >>> agent = CitationMonitoringAgent()
            >>> alerts = agent.detect_alerts(
            ...     current_period_days=7,
            ...     comparison_period_days=7,
            ...     competitor_names=["Competitor A", "Competitor B"],
            ...     citation_drop_threshold=20.0
            ... )
            >>> print(f"Found {alerts['summary']['total_alerts']} alerts")
        """
        # Validate parameters
        if current_period_days <= 0:
            raise ValueError("current_period_days must be greater than 0")
        if comparison_period_days <= 0:
            raise ValueError("comparison_period_days must be greater than 0")
        if citation_drop_threshold < 0 or citation_drop_threshold > 100:
            raise ValueError("citation_drop_threshold must be between 0 and 100")
        if competitor_advantage_threshold < 0 or competitor_advantage_threshold > 100:
            raise ValueError("competitor_advantage_threshold must be between 0 and 100")
        if platform and platform.lower() not in ['chatgpt', 'claude', 'perplexity']:
            raise ValueError("platform must be one of: chatgpt, claude, perplexity")

        # Use brand name from config if not provided
        if not brand_name:
            brand_name = BRAND_NAME

        self.logger.info(
            f"Detecting alerts for {brand_name}: current={current_period_days}d, "
            f"comparison={comparison_period_days}d, platform={platform or 'all'}"
        )

        # Track whether we created the session
        session_provided = db_session is not None
        if not db_session:
            db_session = get_db_session()

        try:
            alerts = []
            now = datetime.utcnow()

            # Calculate time periods
            current_start = now - timedelta(days=current_period_days)
            current_end = now
            comparison_start = current_start - timedelta(days=comparison_period_days)
            comparison_end = current_start

            # Build base query for current period
            current_query = db_session.query(CitationRecord).filter(
                CitationRecord.brand_name == brand_name,
                CitationRecord.query_timestamp >= current_start,
                CitationRecord.query_timestamp <= current_end
            )
            if platform:
                current_query = current_query.filter(CitationRecord.ai_platform == platform.lower())

            current_records = current_query.all()

            # Build base query for comparison period
            comparison_query = db_session.query(CitationRecord).filter(
                CitationRecord.brand_name == brand_name,
                CitationRecord.query_timestamp >= comparison_start,
                CitationRecord.query_timestamp < comparison_end
            )
            if platform:
                comparison_query = comparison_query.filter(CitationRecord.ai_platform == platform.lower())

            comparison_records = comparison_query.all()

            self.logger.debug(
                f"Found {len(current_records)} current records, {len(comparison_records)} comparison records"
            )

            # 1. Detect citation rate drops (overall and per-platform)
            if len(current_records) >= 5 and len(comparison_records) >= 5:
                # Calculate overall citation rates
                current_stats = self._calculate_citation_stats(
                    current_records, brand_name, "CitationRecord"
                )
                comparison_stats = self._calculate_citation_stats(
                    comparison_records, brand_name, "CitationRecord"
                )

                current_rate = current_stats['citation_rate']
                comparison_rate = comparison_stats['citation_rate']
                rate_drop = comparison_rate - current_rate

                # Alert if citation rate dropped significantly
                if rate_drop >= citation_drop_threshold:
                    severity = self._determine_alert_severity(rate_drop, citation_drop_threshold)
                    alerts.append({
                        'alert_type': 'citation_rate_drop',
                        'severity': severity,
                        'title': f'Citation rate dropped {rate_drop:.1f}% in last {current_period_days} days',
                        'description': (
                            f"Brand citation rate decreased from {comparison_rate:.1f}% "
                            f"({comparison_stats['citations']}/{comparison_stats['total_queries']} queries) "
                            f"to {current_rate:.1f}% ({current_stats['citations']}/{current_stats['total_queries']} queries). "
                            f"This represents a {rate_drop:.1f} percentage point drop. "
                            f"Review recent content changes, algorithm updates, or competitor activity."
                        ),
                        'metrics': {
                            'current_rate': current_rate,
                            'previous_rate': comparison_rate,
                            'rate_drop': rate_drop,
                            'current_citations': current_stats['citations'],
                            'current_queries': current_stats['total_queries'],
                            'previous_citations': comparison_stats['citations'],
                            'previous_queries': comparison_stats['total_queries']
                        },
                        'detected_at': now.isoformat(),
                        'platform': platform or 'all'
                    })
                    self.logger.warning(
                        f"Citation rate drop alert: {rate_drop:.1f}% drop from {comparison_rate:.1f}% to {current_rate:.1f}%"
                    )

                # Check per-platform citation rate drops (if not already filtered by platform)
                if not platform:
                    for platform_name in ['chatgpt', 'claude', 'perplexity']:
                        platform_current = [r for r in current_records if r.ai_platform == platform_name]
                        platform_comparison = [r for r in comparison_records if r.ai_platform == platform_name]

                        if len(platform_current) >= 3 and len(platform_comparison) >= 3:
                            platform_current_stats = self._calculate_citation_stats(
                                platform_current, brand_name, "CitationRecord"
                            )
                            platform_comparison_stats = self._calculate_citation_stats(
                                platform_comparison, brand_name, "CitationRecord"
                            )

                            platform_current_rate = platform_current_stats['citation_rate']
                            platform_comparison_rate = platform_comparison_stats['citation_rate']
                            platform_drop = platform_comparison_rate - platform_current_rate

                            if platform_drop >= citation_drop_threshold:
                                severity = self._determine_alert_severity(platform_drop, citation_drop_threshold)
                                alerts.append({
                                    'alert_type': 'citation_rate_drop',
                                    'severity': severity,
                                    'title': f'{platform_name.title()} citation rate dropped {platform_drop:.1f}%',
                                    'description': (
                                        f"Citation rate on {platform_name.title()} decreased from "
                                        f"{platform_comparison_rate:.1f}% to {platform_current_rate:.1f}%. "
                                        f"This platform-specific drop may indicate algorithm changes or "
                                        f"content optimization issues specific to {platform_name.title()}."
                                    ),
                                    'metrics': {
                                        'current_rate': platform_current_rate,
                                        'previous_rate': platform_comparison_rate,
                                        'rate_drop': platform_drop,
                                        'current_citations': platform_current_stats['citations'],
                                        'current_queries': platform_current_stats['total_queries'],
                                        'previous_citations': platform_comparison_stats['citations'],
                                        'previous_queries': platform_comparison_stats['total_queries']
                                    },
                                    'detected_at': now.isoformat(),
                                    'platform': platform_name
                                })
                                self.logger.warning(
                                    f"{platform_name.title()} citation rate drop: {platform_drop:.1f}% drop"
                                )

            # 2. Detect competitor citation gains
            if competitor_names and len(competitor_names) > 0 and len(current_records) >= 5:
                # Get current period competitor citations
                competitor_query = db_session.query(CompetitorCitation).filter(
                    CompetitorCitation.competitor_name.in_(competitor_names),
                    CompetitorCitation.query_timestamp >= current_start,
                    CompetitorCitation.query_timestamp <= current_end
                )
                if platform:
                    competitor_query = competitor_query.filter(
                        CompetitorCitation.ai_platform == platform.lower()
                    )

                competitor_citations = competitor_query.all()

                # Calculate brand citation rate
                brand_stats = self._calculate_citation_stats(
                    current_records, brand_name, "CitationRecord"
                )
                brand_rate = brand_stats['citation_rate']

                # Calculate citation rate for each competitor
                for comp_name in competitor_names:
                    comp_records = [c for c in competitor_citations if c.competitor_name == comp_name]

                    if len(comp_records) >= 5:
                        comp_stats = self._calculate_citation_stats(
                            comp_records, comp_name, "CompetitorCitation"
                        )
                        comp_rate = comp_stats['citation_rate']
                        advantage = comp_rate - brand_rate

                        # Alert if competitor has significant advantage
                        if advantage >= competitor_advantage_threshold:
                            severity = self._determine_alert_severity(advantage, competitor_advantage_threshold)
                            alerts.append({
                                'alert_type': 'competitor_gain',
                                'severity': severity,
                                'title': f'{comp_name} has {advantage:.1f}% higher citation rate',
                                'description': (
                                    f"Competitor '{comp_name}' is being cited at {comp_rate:.1f}% "
                                    f"({comp_stats['citations']}/{comp_stats['total_queries']} queries) "
                                    f"compared to brand's {brand_rate:.1f}% "
                                    f"({brand_stats['citations']}/{brand_stats['total_queries']} queries). "
                                    f"This {advantage:.1f} percentage point advantage suggests they have "
                                    f"stronger content or better positioning for these queries. "
                                    f"Analyze their content strategy and identify opportunities to improve."
                                ),
                                'metrics': {
                                    'brand_rate': brand_rate,
                                    'competitor_rate': comp_rate,
                                    'advantage': advantage,
                                    'competitor_name': comp_name,
                                    'brand_citations': brand_stats['citations'],
                                    'brand_queries': brand_stats['total_queries'],
                                    'competitor_citations': comp_stats['citations'],
                                    'competitor_queries': comp_stats['total_queries']
                                },
                                'detected_at': now.isoformat(),
                                'platform': platform or 'all'
                            })
                            self.logger.warning(
                                f"Competitor gain alert: {comp_name} has {advantage:.1f}% advantage "
                                f"({comp_rate:.1f}% vs {brand_rate:.1f}%)"
                            )

            # Generate summary
            summary = {
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['severity'] == 'critical']),
                'high_alerts': len([a for a in alerts if a['severity'] == 'high']),
                'medium_alerts': len([a for a in alerts if a['severity'] == 'medium']),
                'low_alerts': len([a for a in alerts if a['severity'] == 'low']),
                'by_type': {},
                'by_platform': {}
            }

            # Count by type
            for alert in alerts:
                alert_type = alert['alert_type']
                summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1

            # Count by platform
            for alert in alerts:
                alert_platform = alert['platform']
                summary['by_platform'][alert_platform] = summary['by_platform'].get(alert_platform, 0) + 1

            self.logger.info(
                f"Detected {len(alerts)} alerts: "
                f"{summary['critical_alerts']} critical, {summary['high_alerts']} high, "
                f"{summary['medium_alerts']} medium, {summary['low_alerts']} low"
            )

            return {
                'alerts': alerts,
                'summary': summary,
                'analysis_periods': {
                    'current_period': {
                        'start': current_start.isoformat(),
                        'end': current_end.isoformat(),
                        'days': current_period_days
                    },
                    'comparison_period': {
                        'start': comparison_start.isoformat(),
                        'end': comparison_end.isoformat(),
                        'days': comparison_period_days
                    },
                    'platform': platform or 'all'
                }
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Log and wrap unexpected errors
            self.logger.error(f"Error detecting alerts: {e}", exc_info=True)
            raise ContentGenerationError(f"Failed to detect alerts: {str(e)}")
        finally:
            # Close session if we created it
            if not session_provided and db_session:
                db_session.close()

    def _determine_alert_severity(self, value: float, threshold: float) -> str:
        """
        Determine alert severity based on how much the value exceeds the threshold

        Args:
            value: The measured value (e.g., citation rate drop percentage)
            threshold: The minimum threshold for triggering an alert

        Returns:
            Severity level: "critical", "high", "medium", or "low"
        """
        if value >= threshold * 2.5:
            return "critical"
        elif value >= threshold * 1.75:
            return "high"
        elif value >= threshold * 1.25:
            return "medium"
        else:
            return "low"
