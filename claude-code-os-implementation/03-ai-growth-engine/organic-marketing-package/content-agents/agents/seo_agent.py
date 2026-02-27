"""
SEO Agent
Orchestrates keyword research, content analysis, and optimization recommendations
"""
from typing import Optional, List, Dict
from .base_agent import BaseAgent
from utils.keyword_research import KeywordResearcher, KeywordSuggestion
from utils.seo_analyzer import SEOAnalyzer
from utils.internal_linking import InternalLinkingSuggester, LinkSuggestion


class SEOAgent(BaseAgent):
    """Agent specialized in SEO optimization and analysis"""

    def __init__(self):
        super().__init__(agent_name="seo_agent")

        # Initialize SEO utilities
        self.keyword_researcher = KeywordResearcher(model=self.model)
        self.seo_analyzer = SEOAnalyzer()
        self.link_suggester = InternalLinkingSuggester(model=self.model)

        self.logger.info("SEOAgent initialized with keyword research, analysis, and linking utilities")

    def research_keywords(
        self,
        topic: str,
        target_audience: str = "TCG players and collectors",
        num_suggestions: int = 10
    ) -> List[KeywordSuggestion]:
        """
        Research keywords for a given topic using AI-powered analysis

        Args:
            topic: The main topic or theme for keyword research
            target_audience: Description of the target audience
            num_suggestions: Number of keyword suggestions to generate

        Returns:
            List of KeywordSuggestion objects with relevance scores and metadata
        """
        self.logger.info(f"Researching keywords for topic: '{topic}'")

        # Build brand context for keyword research
        brand_context = f"""
BRAND: {self.brand_context.get('brand_name', 'Infinity Vault')}
POSITIONING: Battle-ready TCG storage equipment (not commodity storage)
TARGET AUDIENCE: Serious TCG players and collectors who identify as battle-ready
VOICE: Confident, passionate, empowering (using fantasy/gaming language)
"""

        keywords = self.keyword_researcher.research_keywords(
            topic=topic,
            target_audience=target_audience,
            brand_context=brand_context,
            num_suggestions=num_suggestions
        )

        self.logger.info(f"Generated {len(keywords)} keyword suggestions")

        # Log summary metrics
        metrics = self.keyword_researcher.get_keyword_metrics_summary(keywords)
        self.logger.debug(f"Keyword metrics: {metrics}")

        return keywords

    def analyze_content_seo(
        self,
        content: str,
        target_keyword: Optional[str] = None,
        title: Optional[str] = None,
        meta_description: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Perform comprehensive SEO analysis on content

        Args:
            content: The content to analyze (markdown or plain text)
            target_keyword: Primary keyword to optimize for
            title: Optional page/article title
            meta_description: Optional meta description

        Returns:
            Dictionary containing SEO scores, grade, issues, and recommendations
        """
        self.logger.info(f"Analyzing content SEO (keyword: '{target_keyword}')")

        analysis = self.seo_analyzer.analyze_content(
            content=content,
            target_keyword=target_keyword,
            title=title,
            meta_description=meta_description
        )

        self.logger.info(
            f"SEO analysis complete: Score={analysis['total_score']}, "
            f"Grade={analysis['grade']}, Issues={len(analysis['issues'])}"
        )

        return analysis

    def generate_meta_description(
        self,
        content: str,
        target_keyword: Optional[str] = None,
        max_length: int = 160
    ) -> str:
        """
        Generate an SEO-optimized meta description for content

        Args:
            content: The content to generate meta description for
            target_keyword: Optional target keyword to include
            max_length: Maximum character length (default: 160)

        Returns:
            SEO-optimized meta description string
        """
        self.logger.info("Generating meta description")

        # Extract title and first paragraph from content
        import re
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else ""

        # Get first paragraph (skip title)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        first_para = paragraphs[0] if paragraphs else ""

        prompt = f"""Create an SEO-optimized meta description for this content.

TITLE: {title}

FIRST PARAGRAPH:
{first_para[:300]}

TARGET KEYWORD: {target_keyword or 'Use naturally from content'}

REQUIREMENTS:
1. Maximum {max_length} characters (STRICT LIMIT)
2. Include target keyword naturally if provided
3. Compelling and click-worthy
4. Accurately summarizes content value
5. Uses active voice
6. Includes call-to-action or value proposition
7. Aligns with Infinity Vault brand voice (confident, battle-ready mindset)

Return ONLY the meta description, no quotes or explanations."""

        meta_description = self.generate_content(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        ).strip().strip('"\'')

        # Ensure it's within length limit
        if len(meta_description) > max_length:
            self.logger.warning(f"Meta description too long ({len(meta_description)} chars), truncating")
            # Truncate at word boundary
            meta_description = meta_description[:max_length].rsplit(' ', 1)[0] + '...'

        self.logger.info(f"Generated meta description ({len(meta_description)} chars): {meta_description[:50]}...")
        return meta_description

    def suggest_optimizations(
        self,
        content: str,
        target_keyword: Optional[str] = None,
        current_seo_score: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Generate actionable SEO optimization suggestions for content

        Args:
            content: The content to analyze for optimizations
            target_keyword: Target keyword for optimization
            current_seo_score: Optional pre-computed SEO analysis to use

        Returns:
            Dictionary with prioritized optimization suggestions
        """
        self.logger.info("Generating SEO optimization suggestions")

        # Get current SEO analysis if not provided
        if not current_seo_score:
            current_seo_score = self.analyze_content_seo(
                content=content,
                target_keyword=target_keyword
            )

        # Organize suggestions by priority
        high_priority = []
        medium_priority = []
        low_priority = []

        # Analyze each SEO factor and prioritize fixes
        scores = current_seo_score['scores']

        # Keyword optimization (highest weight: 30%)
        if scores['keyword_optimization']['score'] < 70:
            high_priority.append({
                'category': 'Keyword Optimization',
                'issue': scores['keyword_optimization']['feedback'],
                'impact': 'High',
                'action': self._get_keyword_optimization_action(
                    scores['keyword_optimization']['score'],
                    target_keyword
                )
            })

        # Content structure (weight: 25%)
        if scores['content_structure']['score'] < 70:
            high_priority.append({
                'category': 'Content Structure',
                'issue': scores['content_structure']['feedback'],
                'impact': 'High',
                'action': self._get_structure_optimization_action(
                    scores['content_structure']['score']
                )
            })

        # Content quality (weight: 20%)
        if scores['content_quality']['score'] < 70:
            medium_priority.append({
                'category': 'Content Quality',
                'issue': scores['content_quality']['feedback'],
                'impact': 'Medium',
                'action': self._get_quality_optimization_action(
                    current_seo_score['word_count']
                )
            })

        # Readability (weight: 15%)
        if scores['readability']['score'] < 70:
            medium_priority.append({
                'category': 'Readability',
                'issue': scores['readability']['feedback'],
                'impact': 'Medium',
                'action': 'Break long sentences into shorter ones. Use simpler language. Add paragraph breaks for better scanning.'
            })

        # Keyword placement (weight: 10%)
        if scores['keyword_placement']['score'] < 70:
            low_priority.append({
                'category': 'Keyword Placement',
                'issue': scores['keyword_placement']['feedback'],
                'impact': 'Low',
                'action': 'Place target keyword in: title/H1, opening paragraph, at least one subheading, and closing section.'
            })

        # Compile all suggestions
        suggestions = {
            'total_score': current_seo_score['total_score'],
            'grade': current_seo_score['grade'],
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'quick_wins': self._identify_quick_wins(current_seo_score),
            'estimated_improvement': self._estimate_improvement_potential(current_seo_score)
        }

        self.logger.info(
            f"Generated {len(high_priority)} high, {len(medium_priority)} medium, "
            f"{len(low_priority)} low priority suggestions"
        )

        return suggestions

    def suggest_internal_links(
        self,
        content: str,
        max_suggestions: int = 5,
        content_type: str = "blog"
    ) -> List[LinkSuggestion]:
        """
        Suggest internal links for given content based on existing articles

        Args:
            content: The content to analyze for internal linking opportunities
            max_suggestions: Maximum number of link suggestions to return
            content_type: Type of content to search for links

        Returns:
            List of LinkSuggestion objects with relevance scores
        """
        self.logger.info(f"Suggesting internal links (max: {max_suggestions})")

        suggestions = self.link_suggester.suggest_links(
            content=content,
            max_suggestions=max_suggestions,
            content_type=content_type
        )

        # Log summary
        summary = self.link_suggester.get_link_summary(suggestions)
        self.logger.info(f"Internal link summary: {summary}")

        return suggestions

    def calculate_seo_score(self, content_data: Dict[str, any]) -> Dict[str, any]:
        """
        Calculate comprehensive SEO score for content

        Args:
            content_data: Dictionary with 'content', 'title', 'target_keyword', etc.

        Returns:
            Dictionary with total score, grade, and detailed metrics
        """
        self.logger.info("Calculating comprehensive SEO score")

        content = content_data.get('content', '')
        title = content_data.get('title')
        target_keyword = content_data.get('target_keyword')
        meta_description = content_data.get('meta_description')

        # Perform SEO analysis
        analysis = self.analyze_content_seo(
            content=content,
            target_keyword=target_keyword,
            title=title,
            meta_description=meta_description
        )

        # Calculate additional bonus points for meta description
        if meta_description:
            meta_score = self._score_meta_description(meta_description, target_keyword)
            analysis['meta_description_score'] = meta_score
            # Add small bonus to total score (5% weight)
            analysis['total_score'] = min(100, analysis['total_score'] + (meta_score * 0.05))
            analysis['grade'] = self.seo_analyzer._get_grade(analysis['total_score'])

        self.logger.info(f"Final SEO score: {analysis['total_score']} ({analysis['grade']})")
        return analysis

    # Helper methods for optimization suggestions

    def _get_keyword_optimization_action(self, score: float, keyword: Optional[str]) -> str:
        """Generate specific action for keyword optimization"""
        if not keyword:
            return "Define a target keyword and incorporate it naturally throughout content."

        if score < 30:
            return f"Increase usage of '{keyword}' to achieve 1-2% keyword density. Use it naturally in headings and body text."
        elif score < 50:
            return f"Add '{keyword}' to more strategic locations while maintaining natural flow."
        else:
            return f"Fine-tune '{keyword}' usage to reach optimal 1.5% density."

    def _get_structure_optimization_action(self, score: float) -> str:
        """Generate specific action for structure optimization"""
        if score < 50:
            return "Add proper heading hierarchy (H1, H2, H3). Ensure single H1 and logical subheading structure."
        else:
            return "Improve heading distribution. Add more subheadings to break up long sections."

    def _get_quality_optimization_action(self, word_count: int) -> str:
        """Generate specific action for quality optimization"""
        if word_count < 300:
            return f"Expand content significantly. Current: {word_count} words. Target: 1000+ words for better ranking potential."
        elif word_count < 1000:
            return f"Add more depth and detail. Current: {word_count} words. Target: 1000+ words for optimal SEO."
        else:
            return "Content length is good. Focus on depth, examples, and value-add information."

    def _identify_quick_wins(self, seo_analysis: Dict) -> List[str]:
        """Identify quick, high-impact fixes"""
        quick_wins = []

        issues = seo_analysis.get('issues', [])

        # Quick wins are issues that can be fixed in < 5 minutes
        quick_win_keywords = ['H1', 'title', 'keyword in', 'meta description']

        for issue in issues:
            if any(keyword in issue for keyword in quick_win_keywords):
                quick_wins.append(issue)

        return quick_wins[:3]  # Return top 3 quick wins

    def _estimate_improvement_potential(self, seo_analysis: Dict) -> Dict[str, any]:
        """Estimate how much score could improve with fixes"""
        current_score = seo_analysis['total_score']

        # Calculate potential score if all issues were fixed
        scores = seo_analysis['scores']
        potential_score = 0

        for metric, data in scores.items():
            weight = data['weight']
            current = data['score']

            # Assume we can improve each metric to at least 85
            improved = max(current, 85)
            potential_score += improved * weight

        improvement = potential_score - current_score

        return {
            'current_score': round(current_score, 2),
            'potential_score': round(potential_score, 2),
            'improvement_points': round(improvement, 2),
            'improvement_percentage': round((improvement / current_score) * 100, 2) if current_score > 0 else 0
        }

    def _score_meta_description(self, meta_description: str, target_keyword: Optional[str]) -> float:
        """Score the quality of a meta description"""
        score = 100.0

        # Check length (optimal: 150-160 chars)
        length = len(meta_description)
        if length < 120:
            score -= 20
        elif length > 160:
            score -= 30  # Over limit is worse

        # Check keyword presence
        if target_keyword and target_keyword.lower() not in meta_description.lower():
            score -= 25

        # Check for call-to-action words
        cta_words = ['discover', 'learn', 'find', 'get', 'explore', 'see', 'shop', 'read']
        has_cta = any(word in meta_description.lower() for word in cta_words)
        if not has_cta:
            score -= 15

        return max(0, min(100, score))
