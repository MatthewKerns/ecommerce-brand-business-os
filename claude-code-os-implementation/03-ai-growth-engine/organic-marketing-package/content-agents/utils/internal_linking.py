"""
Internal Linking Utility
Provides internal linking suggestions based on content relevance and existing articles
"""
import re
import anthropic
from typing import List, Dict, Optional
from dataclasses import dataclass
from sqlalchemy import desc

from config.config import ANTHROPIC_API_KEY, DEFAULT_MODEL
from logging_config import get_logger
from database.connection import get_db_session
from database.models import ContentHistory
from exceptions import (
    AgentInitializationError,
    ContentGenerationError,
    AuthenticationError,
    AnthropicAPIError,
    RateLimitError,
    DatabaseError
)


@dataclass
class LinkSuggestion:
    """Data class for internal link suggestions"""
    target_article_id: int
    target_title: str
    suggested_anchor_text: str
    relevance_score: float  # 0-100 scale
    context_snippet: str  # Where to place the link in current content
    target_url: Optional[str] = None


class InternalLinkingSuggester:
    """
    Utility for suggesting internal links based on content relevance

    Analyzes current content and existing published articles to suggest
    relevant internal linking opportunities for SEO optimization.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the internal linking suggester

        Args:
            model: Claude model to use for relevance analysis

        Raises:
            AgentInitializationError: If initialization fails
            AuthenticationError: If API key is missing
        """
        self.model = model
        self.logger = get_logger("internal_linking_suggester")

        try:
            self.logger.info(f"Initializing InternalLinkingSuggester with model {model}")

            if not ANTHROPIC_API_KEY:
                raise AuthenticationError("Anthropic")

            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            self.logger.info("Successfully initialized InternalLinkingSuggester")
        except AuthenticationError:
            self.logger.error("Authentication failed for InternalLinkingSuggester", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize InternalLinkingSuggester: {e}", exc_info=True)
            raise AgentInitializationError("internal_linking_suggester", str(e))

    def suggest_links(
        self,
        content: str,
        max_suggestions: int = 5,
        content_type: str = "blog",
        exclude_ids: Optional[List[int]] = None
    ) -> List[LinkSuggestion]:
        """
        Suggest internal links for given content based on existing articles

        Args:
            content: The content to analyze for internal linking opportunities
            max_suggestions: Maximum number of link suggestions to return
            content_type: Type of content to search for links (default: 'blog')
            exclude_ids: List of content IDs to exclude from suggestions

        Returns:
            List of LinkSuggestion objects with relevance scores

        Raises:
            DatabaseError: If database query fails
            ContentGenerationError: If link analysis fails
        """
        self.logger.info(f"Generating internal link suggestions (max: {max_suggestions})")
        self.logger.debug(f"Content length: {len(content)} chars, Type: {content_type}")

        try:
            # Get existing published content from database
            existing_articles = self._get_existing_articles(
                content_type=content_type,
                exclude_ids=exclude_ids or []
            )

            if not existing_articles:
                self.logger.info("No existing articles found for internal linking")
                return []

            self.logger.info(f"Found {len(existing_articles)} potential articles for linking")

            # Analyze content and suggest relevant links
            suggestions = self._analyze_and_suggest(
                current_content=content,
                existing_articles=existing_articles,
                max_suggestions=max_suggestions
            )

            self.logger.info(f"Generated {len(suggestions)} internal link suggestions")
            return suggestions

        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to suggest internal links: {e}", exc_info=True)
            raise ContentGenerationError("internal_linking_suggester", content[:100], str(e))

    def analyze_link_relevance(
        self,
        current_content: str,
        target_content: str,
        target_title: str
    ) -> float:
        """
        Analyze relevance between current content and a potential link target

        Args:
            current_content: The content being analyzed
            target_content: Content of the potential link target
            target_title: Title of the potential link target

        Returns:
            Relevance score from 0-100
        """
        self.logger.debug(f"Analyzing link relevance to '{target_title}'")

        # Extract key topics from both contents
        current_preview = current_content[:500]
        target_preview = target_content[:500]

        prompt = f"""Analyze the relevance between these two articles for internal linking purposes.

CURRENT ARTICLE PREVIEW:
{current_preview}

TARGET ARTICLE: "{target_title}"
{target_preview}

Rate the relevance for internal linking on a scale of 0-100, where:
- 0-25: Not relevant, would be forced or off-topic
- 26-50: Somewhat relevant, could be mentioned but weak connection
- 51-75: Relevant, natural linking opportunity exists
- 76-100: Highly relevant, strong topical connection, valuable for readers

Consider:
1. Topic overlap and semantic similarity
2. Value to the reader (would they benefit from this link?)
3. Natural linking opportunities (can it be mentioned organically?)
4. SEO value (topical authority building)

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

            self.logger.debug(f"Relevance score for '{target_title}': {score}")
            return score

        except Exception as e:
            self.logger.warning(f"Failed to analyze link relevance: {e}")
            # Return neutral score on error
            return 50.0

    def suggest_anchor_text(
        self,
        current_content: str,
        target_title: str,
        target_content: str
    ) -> str:
        """
        Suggest optimal anchor text for an internal link

        Args:
            current_content: Content where the link will be placed
            target_title: Title of the link target
            target_content: Preview of target content

        Returns:
            Suggested anchor text string
        """
        self.logger.debug(f"Suggesting anchor text for '{target_title}'")

        prompt = f"""Suggest optimal anchor text for an internal link.

CURRENT ARTICLE CONTEXT:
{current_content[:300]}

LINK TARGET: "{target_title}"
{target_content[:200]}

Provide 1-4 word anchor text that:
1. Is natural and contextually relevant
2. Includes keywords from the target article
3. Entices clicks without being clickbait
4. Follows SEO best practices

Respond with ONLY the anchor text, no quotes or explanations."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            anchor_text = message.content[0].text.strip().strip('"\'')
            self.logger.debug(f"Suggested anchor text: '{anchor_text}'")
            return anchor_text

        except Exception as e:
            self.logger.warning(f"Failed to suggest anchor text: {e}")
            # Fallback to title
            return target_title

    def find_link_placement(
        self,
        content: str,
        anchor_text: str,
        max_snippets: int = 3
    ) -> List[str]:
        """
        Find suitable locations in content to place a link

        Args:
            content: Content to search for placement opportunities
            anchor_text: The anchor text to place
            max_snippets: Maximum number of placement suggestions

        Returns:
            List of context snippets showing where link could be placed
        """
        self.logger.debug(f"Finding placement for anchor text: '{anchor_text}'")

        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        # Look for paragraphs containing related keywords
        anchor_keywords = set(anchor_text.lower().split())
        placements = []

        for para in paragraphs:
            para_lower = para.lower()
            # Check if paragraph contains any keywords from anchor text
            if any(keyword in para_lower for keyword in anchor_keywords):
                # Extract a snippet around potential placement
                snippet = para[:200] + "..." if len(para) > 200 else para
                placements.append(snippet)

                if len(placements) >= max_snippets:
                    break

        if not placements:
            # If no keyword matches, suggest first few paragraphs
            placements = [
                p[:200] + "..." if len(p) > 200 else p
                for p in paragraphs[:max_snippets]
            ]

        self.logger.debug(f"Found {len(placements)} potential placements")
        return placements

    def _get_existing_articles(
        self,
        content_type: str,
        exclude_ids: List[int],
        limit: int = 50
    ) -> List[Dict]:
        """
        Query database for existing published articles

        Args:
            content_type: Type of content to retrieve
            exclude_ids: IDs to exclude from results
            limit: Maximum number of articles to retrieve

        Returns:
            List of article dictionaries with id, content, and metadata

        Raises:
            DatabaseError: If database query fails
        """
        self.logger.debug(f"Querying database for {content_type} articles")

        try:
            db = get_db_session()
            try:
                query = db.query(ContentHistory).filter(
                    ContentHistory.content_type == content_type,
                    ContentHistory.status == 'success'
                )

                if exclude_ids:
                    query = query.filter(ContentHistory.id.notin_(exclude_ids))

                # Get most recent articles first
                articles = query.order_by(desc(ContentHistory.created_at)).limit(limit).all()

                results = []
                for article in articles:
                    # Extract title from content (first H1 heading)
                    title_match = re.search(r'^#\s+(.+)$', article.content, re.MULTILINE)
                    title = title_match.group(1) if title_match else f"Article {article.id}"

                    results.append({
                        'id': article.id,
                        'title': title,
                        'content': article.content,
                        'request_id': article.request_id,
                        'created_at': article.created_at
                    })

                self.logger.debug(f"Retrieved {len(results)} articles from database")
                return results

            finally:
                db.close()

        except Exception as e:
            self.logger.error(f"Database query failed: {e}", exc_info=True)
            raise DatabaseError("content_history", f"Failed to retrieve articles: {e}")

    def _analyze_and_suggest(
        self,
        current_content: str,
        existing_articles: List[Dict],
        max_suggestions: int
    ) -> List[LinkSuggestion]:
        """
        Analyze existing articles and generate link suggestions

        Args:
            current_content: Content to add links to
            existing_articles: List of potential link targets
            max_suggestions: Maximum suggestions to return

        Returns:
            List of LinkSuggestion objects sorted by relevance
        """
        self.logger.debug(f"Analyzing {len(existing_articles)} articles for link suggestions")

        suggestions = []

        for article in existing_articles:
            try:
                # Calculate relevance score
                relevance_score = self.analyze_link_relevance(
                    current_content=current_content,
                    target_content=article['content'],
                    target_title=article['title']
                )

                # Only suggest if relevance is above threshold
                if relevance_score < 30:
                    self.logger.debug(f"Skipping '{article['title']}' (low relevance: {relevance_score})")
                    continue

                # Generate anchor text suggestion
                anchor_text = self.suggest_anchor_text(
                    current_content=current_content,
                    target_title=article['title'],
                    target_content=article['content']
                )

                # Find placement location
                placements = self.find_link_placement(
                    content=current_content,
                    anchor_text=anchor_text,
                    max_snippets=1
                )

                context_snippet = placements[0] if placements else "No specific placement found"

                suggestion = LinkSuggestion(
                    target_article_id=article['id'],
                    target_title=article['title'],
                    suggested_anchor_text=anchor_text,
                    relevance_score=relevance_score,
                    context_snippet=context_snippet,
                    target_url=f"/blog/{article['request_id']}"
                )

                suggestions.append(suggestion)
                self.logger.debug(
                    f"Added suggestion: '{article['title']}' "
                    f"(relevance: {relevance_score:.1f})"
                )

            except Exception as e:
                self.logger.warning(f"Failed to analyze article {article['id']}: {e}")
                continue

        # Sort by relevance score (highest first)
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)

        # Return top N suggestions
        top_suggestions = suggestions[:max_suggestions]

        self.logger.info(
            f"Returning {len(top_suggestions)} suggestions "
            f"(from {len(suggestions)} candidates)"
        )

        return top_suggestions

    def get_link_summary(self, suggestions: List[LinkSuggestion]) -> Dict[str, any]:
        """
        Get summary statistics for link suggestions

        Args:
            suggestions: List of LinkSuggestion objects

        Returns:
            Dictionary with summary metrics
        """
        if not suggestions:
            return {
                "total_suggestions": 0,
                "avg_relevance": 0,
                "high_relevance_count": 0,
                "medium_relevance_count": 0,
                "low_relevance_count": 0
            }

        total = len(suggestions)
        avg_relevance = sum(s.relevance_score for s in suggestions) / total

        high_relevance = sum(1 for s in suggestions if s.relevance_score >= 75)
        medium_relevance = sum(1 for s in suggestions if 50 <= s.relevance_score < 75)
        low_relevance = sum(1 for s in suggestions if s.relevance_score < 50)

        return {
            "total_suggestions": total,
            "avg_relevance": round(avg_relevance, 2),
            "high_relevance_count": high_relevance,
            "medium_relevance_count": medium_relevance,
            "low_relevance_count": low_relevance
        }
