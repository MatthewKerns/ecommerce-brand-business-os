"""
Blog Post Generation Agent
Creates SEO-optimized blog posts aligned with brand voice and content pillars
"""
from pathlib import Path
from typing import Optional, List, Dict
from .base_agent import BaseAgent
from config.config import BLOG_OUTPUT_DIR, CONTENT_PILLARS


class BlogAgent(BaseAgent):
    """Agent specialized in creating blog content"""

    def __init__(self):
        super().__init__(agent_name="blog_agent")

        # Initialize SEO agent for analysis (lazy import to avoid circular dependency)
        self._seo_agent = None

        self.logger.info("BlogAgent initialized")

    @property
    def seo_agent(self):
        """Lazy load SEO agent to avoid circular imports"""
        if self._seo_agent is None:
            from .seo_agent import SEOAgent
            self._seo_agent = SEOAgent()
            self.logger.debug("SEOAgent initialized for blog analysis")
        return self._seo_agent

    def generate_blog_post(
        self,
        topic: str,
        content_pillar: Optional[str] = None,
        target_keywords: Optional[List[str]] = None,
        word_count: int = 1000,
        include_cta: bool = True,
        include_seo_analysis: bool = False
    ) -> tuple[str, Path]:
        """
        Generate a complete blog post

        Args:
            topic: The blog post topic
            content_pillar: Which content pillar (Battle-Ready Lifestyle, Gear & Equipment, etc.)
            target_keywords: SEO keywords to target
            word_count: Target word count
            include_cta: Whether to include a call-to-action
            include_seo_analysis: Whether to perform SEO analysis on generated content

        Returns:
            Tuple of (blog_content, file_path)
        """
        self.logger.info(
            f"Generating blog post: topic='{topic}', pillar={content_pillar}, "
            f"word_count={word_count}, seo_analysis={include_seo_analysis}"
        )

        # Validate content pillar
        if content_pillar and content_pillar not in CONTENT_PILLARS:
            self.logger.warning(f"Content pillar '{content_pillar}' not in defined pillars. Using anyway.")

        # Build the prompt
        prompt = f"""Create a blog post on the following topic:

TOPIC: {topic}

CONTENT PILLAR: {content_pillar or 'Choose the most relevant pillar'}

TARGET WORD COUNT: {word_count} words

TARGET KEYWORDS: {', '.join(target_keywords) if target_keywords else 'Use natural language, optimize for topic'}

REQUIREMENTS:
1. Write in the Infinity Vault brand voice (confident, passionate, empowering)
2. Use fantasy/gaming language naturally throughout
3. Focus on the "battle-ready" mindset - this is about preparation, confidence, respect
4. Make readers feel like serious players, not casual hobbyists
5. Include practical value (tips, insights, how-tos)
6. Optimize for SEO naturally (don't keyword stuff)
7. Use headers (H2, H3) to structure content
8. Include an engaging introduction that hooks readers
{"9. End with a strong call-to-action that ties to Infinity Vault products" if include_cta else ""}

FORMAT:
Return the blog post in markdown format with:
- Title (# H1)
- Meta description (as a comment at top)
- Structured sections with H2/H3 headers
- Natural keyword integration
- Engaging conclusion
{"- Call-to-action" if include_cta else ""}

Write the complete blog post now."""

        system_context = """
ADDITIONAL CONTEXT FOR BLOG WRITING:

Blog Content Strategy:
- Educate and inspire, don't just sell
- Tell stories that connect with player identity
- Use gaming/fantasy metaphors naturally
- Build authority in TCG storage and collection care
- Drive organic traffic through valuable content

SEO Best Practices:
- Front-load important keywords in title and intro
- Use semantic keywords (related terms, synonyms)
- Write for humans first, search engines second
- Include internal linking opportunities (mention products naturally)
- Aim for featured snippet potential (answer questions directly)

Tone for Blog:
- More educational and storytelling than product pages
- Still passionate and confident
- Can be longer-form and more detailed
- Build trust through expertise"""

        # Generate and save
        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=BLOG_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "topic": topic,
                "content_pillar": content_pillar,
                "target_keywords": target_keywords,
                "word_count_target": word_count
            },
            max_tokens=4096
        )

        # Perform SEO analysis if requested
        if include_seo_analysis:
            self._analyze_and_log_seo(
                content=content,
                target_keywords=target_keywords,
                path=path
            )

        self.logger.info(f"Successfully generated blog post: {path}")
        return content, path

    def generate_blog_series(
        self,
        series_topic: str,
        num_posts: int = 3,
        content_pillar: Optional[str] = None
    ) -> List[tuple[str, Path]]:
        """
        Generate a series of related blog posts

        Args:
            series_topic: The overarching series topic
            num_posts: Number of posts in the series
            content_pillar: Content pillar for the series

        Returns:
            List of (content, path) tuples
        """
        self.logger.info(f"Generating blog series: topic='{series_topic}', num_posts={num_posts}, pillar={content_pillar}")

        # First, get post topics from Claude
        outline_prompt = f"""Create an outline for a {num_posts}-part blog series on:

SERIES TOPIC: {series_topic}
CONTENT PILLAR: {content_pillar or 'Choose most relevant'}

For each post in the series, provide:
1. Post title
2. Main topic/focus
3. Key points to cover
4. Target keywords (2-3 per post)

Format as a numbered list with clear separation between posts."""

        outline = self.generate_content(outline_prompt)
        self.logger.info("Blog series outline generated successfully")
        self.logger.debug(f"Outline:\n{outline}")

        # Parse outline and generate each post
        # (In real implementation, you'd parse the outline programmatically)
        # For now, return the outline and let user generate posts individually
        self.logger.info("Outline generated. Use generate_blog_post() for each post individually.")

        path = self.save_output(outline, BLOG_OUTPUT_DIR, "series_outline.md")
        self.logger.info(f"Saved series outline to {path}")
        return [(outline, path)]

    def generate_listicle(
        self,
        topic: str,
        num_items: int = 10,
        content_pillar: Optional[str] = None
    ) -> tuple[str, Path]:
        """
        Generate a listicle-style blog post

        Args:
            topic: The listicle topic
            num_items: Number of items in the list
            content_pillar: Content pillar

        Returns:
            Tuple of (content, path)
        """
        self.logger.info(f"Generating listicle: topic='{topic}', num_items={num_items}, pillar={content_pillar}")

        prompt = f"""Create a listicle blog post:

TOPIC: {topic}
NUMBER OF ITEMS: {num_items}
CONTENT PILLAR: {content_pillar or 'Choose most relevant'}

Create a "{num_items} [Topic]" style post that:
1. Has an engaging, clickable title
2. Brief intro explaining why this list matters
3. Each item has:
   - Clear header
   - 2-3 paragraphs of valuable content
   - Connects to battle-ready mindset
4. Conclusion that ties items together
5. Call-to-action related to Infinity Vault

Use the brand voice - make it exciting and empowering, not generic."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=BLOG_OUTPUT_DIR,
            metadata={
                "type": "listicle",
                "topic": topic,
                "num_items": num_items,
                "content_pillar": content_pillar
            }
        )

        self.logger.info(f"Successfully generated listicle: {path}")
        return content, path

    def generate_how_to_guide(
        self,
        topic: str,
        target_audience: str = "Tournament players",
        difficulty_level: str = "beginner"
    ) -> tuple[str, Path]:
        """
        Generate a how-to guide

        Args:
            topic: The how-to topic
            target_audience: Target reader
            difficulty_level: beginner, intermediate, or advanced

        Returns:
            Tuple of (content, path)
        """
        self.logger.info(f"Generating how-to guide: topic='{topic}', audience='{target_audience}', level={difficulty_level}")

        prompt = f"""Create a comprehensive how-to guide:

TOPIC: {topic}
TARGET AUDIENCE: {target_audience}
DIFFICULTY LEVEL: {difficulty_level}

Create a practical guide that:
1. Starts with why this matters (connect to battle-ready mindset)
2. Lists what readers need (tools, materials, time)
3. Provides step-by-step instructions
4. Includes pro tips and common mistakes to avoid
5. Ends with next steps or advanced techniques
6. Call-to-action to Infinity Vault products where relevant

Make it actionable and empowering. Readers should finish feeling capable and ready."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=BLOG_OUTPUT_DIR,
            metadata={
                "type": "how-to",
                "topic": topic,
                "target_audience": target_audience,
                "difficulty": difficulty_level
            }
        )

        self.logger.info(f"Successfully generated how-to guide: {path}")
        return content, path

    def _analyze_and_log_seo(
        self,
        content: str,
        target_keywords: Optional[List[str]],
        path: Path
    ) -> Dict[str, any]:
        """
        Analyze generated content for SEO quality and log results

        Args:
            content: The generated blog content
            target_keywords: List of target keywords
            path: Path where content was saved

        Returns:
            Dictionary with SEO analysis results
        """
        self.logger.info("Performing SEO analysis on generated blog post")

        # Extract title from content for analysis
        import re
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else None

        # Use primary keyword if available
        target_keyword = target_keywords[0] if target_keywords else None

        # Perform SEO analysis
        analysis = self.seo_agent.analyze_content_seo(
            content=content,
            target_keyword=target_keyword,
            title=title
        )

        # Log SEO checklist results
        self.logger.info("=" * 60)
        self.logger.info("SEO ANALYSIS RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Overall Score: {analysis['total_score']:.1f}/100")
        self.logger.info(f"Grade: {analysis['grade']}")
        self.logger.info(f"Word Count: {analysis['word_count']}")
        self.logger.info("")

        # Log individual scores
        self.logger.info("Component Scores:")
        for component, data in analysis['scores'].items():
            score = data['score']
            weight = data['weight']
            status = "✓" if score >= 70 else "✗"
            self.logger.info(
                f"  {status} {component.replace('_', ' ').title()}: "
                f"{score:.1f}/100 (weight: {weight:.0%})"
            )

        # Log issues if any
        if analysis['issues']:
            self.logger.info("")
            self.logger.info(f"Issues Found ({len(analysis['issues'])}):")
            for issue in analysis['issues']:
                self.logger.warning(f"  - {issue}")

        # Log recommendations
        if analysis['recommendations']:
            self.logger.info("")
            self.logger.info("Recommendations:")
            for rec in analysis['recommendations'][:5]:  # Top 5
                self.logger.info(f"  • {rec}")

        self.logger.info("=" * 60)

        # Save SEO analysis to separate file
        analysis_path = path.parent / f"{path.stem}_seo_analysis.json"
        import json
        analysis_path.write_text(json.dumps(analysis, indent=2))
        self.logger.info(f"SEO analysis saved to: {analysis_path}")

        # Enforce minimum quality threshold
        if analysis['total_score'] < 60:
            self.logger.warning(
                f"SEO score ({analysis['total_score']:.1f}) is below recommended threshold (60). "
                "Consider regenerating with improved keywords or structure."
            )
        elif analysis['total_score'] >= 80:
            self.logger.info(f"Excellent SEO score! Content is well-optimized.")

        return analysis
