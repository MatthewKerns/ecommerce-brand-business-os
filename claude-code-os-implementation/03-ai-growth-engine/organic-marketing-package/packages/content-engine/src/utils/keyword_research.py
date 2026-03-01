"""
Keyword Research Utility
Provides keyword research, relevance scoring, and related keyword suggestions for SEO optimization
"""
import anthropic
from typing import List, Dict, Optional
from dataclasses import dataclass

from config.config import ANTHROPIC_API_KEY, DEFAULT_MODEL
from logging_config import get_logger
from exceptions import (
    AgentInitializationError,
    ContentGenerationError,
    AuthenticationError,
    AnthropicAPIError,
    RateLimitError
)


@dataclass
class KeywordSuggestion:
    """Data class for keyword suggestions"""
    keyword: str
    relevance_score: float  # 0-100 scale
    estimated_volume: str  # 'low', 'medium', 'high'
    difficulty: str  # 'easy', 'medium', 'hard'
    intent: str  # 'informational', 'commercial', 'transactional'


class KeywordResearcher:
    """
    Utility for AI-powered keyword research and analysis

    Provides keyword suggestions, relevance scoring, and search intent analysis
    for SEO-optimized content creation.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the keyword researcher

        Args:
            model: Claude model to use for keyword analysis

        Raises:
            AgentInitializationError: If initialization fails
            AuthenticationError: If API key is missing
        """
        self.model = model
        self.logger = get_logger("keyword_researcher")

        try:
            self.logger.info(f"Initializing KeywordResearcher with model {model}")

            if not ANTHROPIC_API_KEY:
                raise AuthenticationError("Anthropic")

            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            self.logger.info("Successfully initialized KeywordResearcher")
        except AuthenticationError:
            self.logger.error("Authentication failed for KeywordResearcher", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize KeywordResearcher: {e}", exc_info=True)
            raise AgentInitializationError("keyword_researcher", str(e))

    def research_keywords(
        self,
        topic: str,
        target_audience: str = "TCG players and collectors",
        brand_context: Optional[str] = None,
        num_suggestions: int = 10
    ) -> List[KeywordSuggestion]:
        """
        Generate keyword suggestions for a given topic

        Args:
            topic: The main topic or theme for keyword research
            target_audience: Description of the target audience
            brand_context: Optional brand-specific context
            num_suggestions: Number of keyword suggestions to generate

        Returns:
            List of KeywordSuggestion objects with scoring and metadata

        Raises:
            ContentGenerationError: If keyword generation fails
        """
        self.logger.info(f"Researching keywords for topic: '{topic}'")
        self.logger.debug(f"Target audience: {target_audience}, Suggestions: {num_suggestions}")

        prompt = self._build_keyword_research_prompt(
            topic=topic,
            target_audience=target_audience,
            brand_context=brand_context,
            num_suggestions=num_suggestions
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=1.0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text
            keywords = self._parse_keyword_response(content)

            self.logger.info(f"Successfully generated {len(keywords)} keyword suggestions")
            return keywords

        except anthropic.RateLimitError as e:
            self.logger.error("Rate limit exceeded", exc_info=True)
            raise RateLimitError(retry_after=getattr(e, 'retry_after', None))
        except anthropic.AuthenticationError as e:
            self.logger.error("Authentication failed", exc_info=True)
            raise AuthenticationError("Anthropic")
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {e}", exc_info=True)
            raise AnthropicAPIError(
                status_code=getattr(e, 'status_code', None),
                response_body=str(e)
            )
        except Exception as e:
            self.logger.error(f"Keyword research failed: {e}", exc_info=True)
            raise ContentGenerationError("keyword_researcher", prompt, str(e))

    def analyze_keyword_relevance(
        self,
        keyword: str,
        content: str,
        target_audience: str = "TCG players and collectors"
    ) -> float:
        """
        Analyze how relevant a keyword is to given content

        Args:
            keyword: The keyword to analyze
            content: The content to check relevance against
            target_audience: Target audience description

        Returns:
            Relevance score from 0-100
        """
        self.logger.debug(f"Analyzing relevance of keyword '{keyword}' to content")

        prompt = f"""Analyze the relevance of the keyword "{keyword}" to the following content for {target_audience}.

CONTENT:
{content[:1000]}...

Rate the relevance on a scale of 0-100, where:
- 0-25: Not relevant or forced
- 26-50: Somewhat relevant but not natural
- 51-75: Relevant and could be naturally incorporated
- 76-100: Highly relevant and already naturally present

Respond with ONLY a number between 0-100."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            score_text = message.content[0].text.strip()
            # Extract number from response
            score = float(''.join(filter(str.isdigit, score_text)))
            score = min(100, max(0, score))  # Clamp to 0-100

            self.logger.debug(f"Relevance score for '{keyword}': {score}")
            return score

        except Exception as e:
            self.logger.warning(f"Failed to analyze keyword relevance: {e}")
            # Return neutral score on error
            return 50.0

    def suggest_related_keywords(
        self,
        primary_keyword: str,
        num_suggestions: int = 5
    ) -> List[str]:
        """
        Suggest related keywords and variations

        Args:
            primary_keyword: The main keyword to find variations for
            num_suggestions: Number of related keywords to suggest

        Returns:
            List of related keyword strings
        """
        self.logger.debug(f"Finding related keywords for '{primary_keyword}'")

        prompt = f"""Generate {num_suggestions} related keyword variations for: "{primary_keyword}"

Focus on:
1. Long-tail variations
2. Question-based keywords
3. Related topics
4. Semantic variations

Respond with ONLY the keywords, one per line, without numbering or explanations."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text.strip()
            keywords = [k.strip() for k in content.split('\n') if k.strip()]

            self.logger.debug(f"Found {len(keywords)} related keywords")
            return keywords[:num_suggestions]

        except Exception as e:
            self.logger.warning(f"Failed to suggest related keywords: {e}")
            return []

    def _build_keyword_research_prompt(
        self,
        topic: str,
        target_audience: str,
        brand_context: Optional[str],
        num_suggestions: int
    ) -> str:
        """Build the prompt for keyword research"""

        brand_section = ""
        if brand_context:
            brand_section = f"\nBRAND CONTEXT:\n{brand_context}\n"

        return f"""You are an expert SEO keyword researcher. Generate {num_suggestions} keyword suggestions for content about: "{topic}"

TARGET AUDIENCE: {target_audience}
{brand_section}

KEYWORD RESEARCH FRAMEWORK:

1. PRIMARY KEYWORDS (High-intent, direct match)
   - Main topic keywords
   - Commercial intent
   - Medium-high search volume

2. LONG-TAIL KEYWORDS (Specific, lower competition)
   - Question-based ("how to", "what is", "best")
   - Specific use cases
   - Lower volume but higher conversion

3. SEMANTIC KEYWORDS (Related topics)
   - Related concepts
   - Supporting topics
   - Context-building terms

For each keyword provide:
- KEYWORD: The actual keyword phrase
- RELEVANCE: Score 0-100 (how relevant to the topic)
- VOLUME: Estimated search volume (low/medium/high)
- DIFFICULTY: Ranking difficulty (easy/medium/hard)
- INTENT: Search intent (informational/commercial/transactional)

FORMAT (one keyword per line):
KEYWORD: [keyword phrase] | RELEVANCE: [0-100] | VOLUME: [low/medium/high] | DIFFICULTY: [easy/medium/hard] | INTENT: [informational/commercial/transactional]

Example:
KEYWORD: best deck boxes for magic the gathering | RELEVANCE: 95 | VOLUME: medium | DIFFICULTY: medium | INTENT: commercial

Generate the {num_suggestions} most valuable keyword suggestions now:"""

    def _parse_keyword_response(self, response: str) -> List[KeywordSuggestion]:
        """
        Parse Claude's keyword response into KeywordSuggestion objects

        Args:
            response: Raw response text from Claude

        Returns:
            List of KeywordSuggestion objects
        """
        keywords = []

        for line in response.split('\n'):
            line = line.strip()
            if not line or not line.startswith('KEYWORD:'):
                continue

            try:
                # Parse the structured format
                parts = line.split('|')

                keyword_part = parts[0].replace('KEYWORD:', '').strip()
                relevance_part = parts[1].replace('RELEVANCE:', '').strip()
                volume_part = parts[2].replace('VOLUME:', '').strip().lower()
                difficulty_part = parts[3].replace('DIFFICULTY:', '').strip().lower()
                intent_part = parts[4].replace('INTENT:', '').strip().lower()

                suggestion = KeywordSuggestion(
                    keyword=keyword_part,
                    relevance_score=float(relevance_part),
                    estimated_volume=volume_part,
                    difficulty=difficulty_part,
                    intent=intent_part
                )

                keywords.append(suggestion)
                self.logger.debug(f"Parsed keyword: {suggestion.keyword} (relevance: {suggestion.relevance_score})")

            except (IndexError, ValueError) as e:
                self.logger.warning(f"Failed to parse keyword line: {line} - {e}")
                continue

        return keywords

    def get_keyword_metrics_summary(self, keywords: List[KeywordSuggestion]) -> Dict[str, any]:
        """
        Get summary metrics for a list of keyword suggestions

        Args:
            keywords: List of KeywordSuggestion objects

        Returns:
            Dictionary with summary metrics
        """
        if not keywords:
            return {
                "total_keywords": 0,
                "avg_relevance": 0,
                "volume_distribution": {},
                "intent_distribution": {},
                "difficulty_distribution": {}
            }

        total = len(keywords)
        avg_relevance = sum(k.relevance_score for k in keywords) / total

        volume_dist = {}
        intent_dist = {}
        difficulty_dist = {}

        for kw in keywords:
            volume_dist[kw.estimated_volume] = volume_dist.get(kw.estimated_volume, 0) + 1
            intent_dist[kw.intent] = intent_dist.get(kw.intent, 0) + 1
            difficulty_dist[kw.difficulty] = difficulty_dist.get(kw.difficulty, 0) + 1

        return {
            "total_keywords": total,
            "avg_relevance": round(avg_relevance, 2),
            "volume_distribution": volume_dist,
            "intent_distribution": intent_dist,
            "difficulty_distribution": difficulty_dist
        }
