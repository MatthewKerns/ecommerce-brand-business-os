"""
Blog Post Generation Agent
Creates SEO-optimized blog posts aligned with brand voice and content pillars.
Enhanced with AEO (Answer Engine Optimization) for AI citation potential.
"""
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent
from config.config import BLOG_OUTPUT_DIR, CONTENT_PILLARS, BRAND_NAME


class BlogAgent(BaseAgent):
    """Agent specialized in creating blog content with AEO optimization"""

    def __init__(self):
        super().__init__(agent_name="blog_agent")

        # Initialize SEO agent for analysis (lazy import to avoid circular dependency)
        self._seo_agent = None
        self._aeo_agent = None

        self.logger.info("BlogAgent initialized with AEO support")

    @property
    def seo_agent(self):
        """Lazy load SEO agent to avoid circular imports"""
        if self._seo_agent is None:
            from .seo_agent import SEOAgent
            self._seo_agent = SEOAgent()
            self.logger.debug("SEOAgent initialized for blog analysis")
        return self._seo_agent

    @property
    def aeo_agent(self):
        """Lazy load AEO agent to avoid circular imports"""
        if self._aeo_agent is None:
            from .aeo_optimization_agent import AEOOptimizationAgent
            self._aeo_agent = AEOOptimizationAgent()
            self.logger.debug("AEOOptimizationAgent initialized for blog AEO optimization")
        return self._aeo_agent

    def generate_blog_post(
        self,
        topic: str,
        content_pillar: Optional[str] = None,
        target_keywords: Optional[List[str]] = None,
        word_count: int = 1000,
        include_cta: bool = True,
        include_seo_analysis: bool = False,
        aeo_optimized: bool = False,
        include_faq: bool = False,
        num_faq_items: int = 5,
        include_schema_markup: bool = False,
        authority_signals: Optional[List[str]] = None
    ) -> tuple[str, Path, Optional[Dict]]:
        """
        Generate a complete blog post with optional AEO optimization

        Args:
            topic: The blog post topic
            content_pillar: Which content pillar (Battle-Ready Lifestyle, Gear & Equipment, etc.)
            target_keywords: SEO keywords to target
            word_count: Target word count
            include_cta: Whether to include a call-to-action
            include_seo_analysis: Whether to perform SEO analysis on generated content
            aeo_optimized: Enable AEO optimization (direct answer, entity clarity, authority)
            include_faq: Auto-generate FAQ section at end of post
            num_faq_items: Number of FAQ items to generate (default 5)
            include_schema_markup: Generate JSON-LD structured data alongside the post
            authority_signals: List of authority signals to include (e.g., ["expert_quotes", "statistics", "citations"])

        Returns:
            Tuple of (blog_content, file_path, seo_analysis)
            seo_analysis is None if include_seo_analysis is False
        """
        self.logger.info(
            f"Generating blog post: topic='{topic}', pillar={content_pillar}, "
            f"word_count={word_count}, seo_analysis={include_seo_analysis}, "
            f"aeo_optimized={aeo_optimized}, include_faq={include_faq}"
        )

        # Validate content pillar
        if content_pillar and content_pillar not in CONTENT_PILLARS:
            self.logger.warning(f"Content pillar '{content_pillar}' not in defined pillars. Using anyway.")

        # Build AEO-specific prompt additions
        aeo_requirements = ""
        aeo_format = ""
        if aeo_optimized:
            aeo_requirements = self._build_aeo_requirements(authority_signals)
            aeo_format = self._build_aeo_format_instructions(include_faq, num_faq_items)

        # Build the prompt
        prompt = f"""Create a blog post on the following topic:

TOPIC: {topic}

CONTENT PILLAR: {content_pillar or 'Choose the most relevant pillar'}

TARGET WORD COUNT: {word_count} words

TARGET KEYWORDS: {', '.join(target_keywords) if target_keywords else 'Use natural language, optimize for topic'}

REQUIREMENTS:
1. Write in the {BRAND_NAME} brand voice (confident, passionate, empowering)
2. Use fantasy/gaming language naturally throughout
3. Focus on the "battle-ready" mindset - this is about preparation, confidence, respect
4. Make readers feel like serious players, not casual hobbyists
5. Include practical value (tips, insights, how-tos)
6. Optimize for SEO naturally (don't keyword stuff)
7. Use headers (H2, H3) to structure content
8. Include an engaging introduction that hooks readers
{"9. End with a strong call-to-action that ties to " + BRAND_NAME + " products" if include_cta else ""}
{aeo_requirements}

FORMAT:
Return the blog post in markdown format with:
- Title (# H1)
- Meta description (as a comment at top)
- Structured sections with H2/H3 headers
- Natural keyword integration
- Engaging conclusion
{"- Call-to-action" if include_cta else ""}
{aeo_format}

Write the complete blog post now."""

        system_context = self._build_blog_system_context(aeo_optimized)

        # Generate and save
        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=BLOG_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "topic": topic,
                "content_pillar": content_pillar,
                "target_keywords": target_keywords,
                "word_count_target": word_count,
                "aeo_optimized": aeo_optimized,
                "include_faq": include_faq,
                "include_schema_markup": include_schema_markup
            },
            max_tokens=4096
        )

        # Generate and append FAQ section if requested but not already in content
        if include_faq and "## FAQ" not in content and "## Frequently Asked" not in content:
            faq_content = self.generate_faq_section(
                topic=topic,
                num_questions=num_faq_items,
                target_keywords=target_keywords
            )
            content = content.rstrip() + "\n\n---\n\n" + faq_content
            path.write_text(content)
            self.logger.info(f"Appended FAQ section with {num_faq_items} items")

        # Generate schema markup alongside the post
        if include_schema_markup:
            schema = self.generate_article_schema(content=content, topic=topic)
            schema_path = path.parent / f"{path.stem}_schema.json"
            schema_path.write_text(schema)
            self.logger.info(f"Schema markup saved to: {schema_path}")

            # If FAQ exists in content, also generate FAQ schema
            faq_items = self._extract_faq_items(content)
            if faq_items:
                faq_schema = self.aeo_agent.generate_faq_schema(faq_items)
                faq_schema_path = path.parent / f"{path.stem}_faq_schema.json"
                faq_schema_path.write_text(faq_schema)
                self.logger.info(f"FAQ schema saved to: {faq_schema_path}")

        # Perform SEO analysis if requested
        seo_analysis = None
        if include_seo_analysis:
            seo_analysis = self._analyze_and_log_seo(
                content=content,
                target_keywords=target_keywords,
                path=path
            )
            # Add AEO score if AEO optimization was enabled
            if aeo_optimized:
                aeo_score = self.score_aeo_readiness(content)
                seo_analysis['aeo_score'] = aeo_score
                self.logger.info(f"AEO Readiness Score: {aeo_score['total_score']}/100")

        self.logger.info(f"Successfully generated blog post: {path}")
        return content, path, seo_analysis

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

    def generate_meta_description(
        self,
        content: str,
        max_length: int = 160
    ) -> str:
        """
        Generate an SEO-optimized meta description for blog content

        Args:
            content: The article content or topic to generate meta description for
            max_length: Maximum character length (default 160 for SEO best practice)

        Returns:
            Meta description string (≤ max_length characters)
        """
        self.logger.info(f"Generating meta description (max_length={max_length})")

        prompt = f"""Generate a compelling meta description for the following content:

CONTENT:
{content[:1000]}

REQUIREMENTS:
1. Maximum {max_length} characters (strict limit)
2. Include primary keywords naturally
3. Write in active voice
4. Make it compelling and clickable
5. Align with Infinity Vault brand voice (confident, battle-ready)
6. Include a clear value proposition or hook
7. No special characters that break HTML

Return ONLY the meta description text, nothing else."""

        system_context = """You are an SEO expert specializing in meta descriptions.

Meta descriptions should:
- Be concise and compelling
- Include target keywords naturally
- Encourage clicks from search results
- Accurately represent the content
- End with a complete thought (no cut-off sentences)

For Infinity Vault content, emphasize:
- Battle-ready mindset
- Premium quality and expertise
- Value for serious TCG players"""

        meta_description = self.generate_content(
            prompt=prompt,
            system_context=system_context,
            max_tokens=100,
            temperature=0.7
        ).strip()

        # Ensure it meets length requirement
        if len(meta_description) > max_length:
            self.logger.warning(
                f"Generated meta description ({len(meta_description)} chars) exceeds "
                f"max_length ({max_length}). Truncating..."
            )
            # Truncate at last complete word before max_length
            meta_description = meta_description[:max_length].rsplit(' ', 1)[0].rstrip('.,;:') + '...'
            if len(meta_description) > max_length:
                meta_description = meta_description[:max_length-3] + '...'

        self.logger.info(f"Generated meta description ({len(meta_description)} chars): {meta_description}")
        return meta_description

    # -------------------------------------------------------------------------
    # AEO (Answer Engine Optimization) Methods
    # -------------------------------------------------------------------------

    def generate_aeo_blog_post(
        self,
        topic: str,
        content_pillar: Optional[str] = None,
        target_keywords: Optional[List[str]] = None,
        word_count: int = 1200,
        include_cta: bool = True,
        include_seo_analysis: bool = True,
        num_faq_items: int = 5,
        authority_signals: Optional[List[str]] = None
    ) -> tuple[str, Path, Optional[Dict]]:
        """
        Generate a blog post fully optimized for AI engine citation.

        Convenience method that enables all AEO features: direct answer optimization,
        FAQ generation, schema markup, entity clarity, and authority signals.

        Args:
            topic: The blog post topic
            content_pillar: Which content pillar
            target_keywords: SEO keywords to target
            word_count: Target word count (default 1200 for AEO depth)
            include_cta: Whether to include a call-to-action
            include_seo_analysis: Whether to perform SEO+AEO analysis
            num_faq_items: Number of FAQ items to auto-generate
            authority_signals: Authority types to include (defaults to all)

        Returns:
            Tuple of (blog_content, file_path, analysis_results)
        """
        if authority_signals is None:
            authority_signals = ["expert_quotes", "statistics", "citations"]

        return self.generate_blog_post(
            topic=topic,
            content_pillar=content_pillar,
            target_keywords=target_keywords,
            word_count=word_count,
            include_cta=include_cta,
            include_seo_analysis=include_seo_analysis,
            aeo_optimized=True,
            include_faq=True,
            num_faq_items=num_faq_items,
            include_schema_markup=True,
            authority_signals=authority_signals
        )

    def generate_faq_section(
        self,
        topic: str,
        num_questions: int = 5,
        target_keywords: Optional[List[str]] = None
    ) -> str:
        """
        Generate a FAQ section for appending to blog posts.

        Each answer uses the direct-answer pattern: core answer in the first
        sentence, followed by supporting details.

        Args:
            topic: The blog topic to generate FAQs for
            num_questions: Number of FAQ items
            target_keywords: Keywords to incorporate naturally

        Returns:
            Markdown-formatted FAQ section
        """
        self.logger.info(f"Generating FAQ section: topic='{topic}', num_questions={num_questions}")

        keywords_str = ', '.join(target_keywords) if target_keywords else topic

        prompt = f"""Generate exactly {num_questions} FAQ items for a blog post about:

TOPIC: {topic}
KEYWORDS: {keywords_str}

REQUIREMENTS FOR EACH FAQ:
1. Question must be a natural query someone would ask an AI assistant
2. Answer MUST start with a direct, definitive answer in the first sentence (40-60 words)
3. Follow with 1-2 supporting sentences with specific details
4. Use "{BRAND_NAME}" by name where naturally relevant
5. Use definitive language ("is", "provides", "means") not hedging language
6. Each answer should be independently quotable by an AI assistant

FORMAT:
## Frequently Asked Questions

### [Question 1]?

[Direct answer first sentence. Supporting detail sentences.]

### [Question 2]?

[Direct answer first sentence. Supporting detail sentences.]

(continue for all {num_questions} questions)

Write the FAQ section now."""

        faq_content = self.generate_content(
            prompt=prompt,
            system_context="You are an AEO expert creating FAQ content optimized for AI assistant citation. Every answer must front-load the direct answer.",
            max_tokens=2048,
            temperature=0.7
        )

        self.logger.info(f"Generated FAQ section with {num_questions} items")
        return faq_content.strip()

    def generate_article_schema(
        self,
        content: str,
        topic: str,
        author_name: str = "Infinity Vault Team",
        publisher_name: Optional[str] = None
    ) -> str:
        """
        Generate JSON-LD Article schema markup for a blog post.

        Args:
            content: The blog post content
            topic: The article topic
            author_name: Author name for schema
            publisher_name: Publisher org name (defaults to BRAND_NAME)

        Returns:
            JSON-LD Article schema as a string
        """
        self.logger.info(f"Generating Article schema for topic: '{topic}'")

        if publisher_name is None:
            publisher_name = BRAND_NAME

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else topic

        # Extract meta description if present
        meta_match = re.search(r'<!--\s*meta[:\s]+(.+?)\s*-->', content, re.IGNORECASE)
        description = meta_match.group(1) if meta_match else ""
        if not description:
            # Fall back to first paragraph
            paragraphs = [p.strip() for p in content.split('\n\n')
                          if p.strip() and not p.strip().startswith('#') and not p.strip().startswith('<!--')]
            description = paragraphs[0][:300] if paragraphs else topic

        # Count words for wordCount property
        word_count = len(content.split())

        # Extract headings for article sections
        headings = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)

        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "author": {
                "@type": "Organization",
                "name": author_name
            },
            "publisher": {
                "@type": "Organization",
                "name": publisher_name
            },
            "wordCount": word_count,
            "articleSection": headings[:10] if headings else [topic],
            "inLanguage": "en-US",
            "isAccessibleForFree": True
        }

        schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
        self.logger.info(f"Generated Article schema: headline='{title}', wordCount={word_count}")
        return schema_json

    def score_aeo_readiness(self, content: str) -> Dict[str, Any]:
        """
        Score how well blog content is optimized for AI engine citation.

        Checks:
        - Direct answer presence (first 40-60 words contain a clear answer)
        - Entity clarity (consistent brand name usage)
        - FAQ section presence
        - Authority signals (statistics, expert references, citations)
        - Structured headings for AI parsing
        - Definitive language usage

        Args:
            content: The blog post content to score

        Returns:
            Dictionary with total_score (0-100), component scores, and recommendations
        """
        self.logger.info("Scoring AEO readiness")

        scores = {}
        recommendations = []

        # 1. Direct Answer Score (25 points)
        scores['direct_answer'] = self._score_direct_answer(content)
        if scores['direct_answer']['score'] < 15:
            recommendations.append(
                "Front-load a clear, definitive answer in the first 40-60 words of the post"
            )

        # 2. Entity Clarity Score (20 points)
        scores['entity_clarity'] = self._score_entity_clarity(content)
        if scores['entity_clarity']['score'] < 12:
            recommendations.append(
                f"Use '{BRAND_NAME}' consistently by full name (found {scores['entity_clarity']['brand_mentions']} mentions)"
            )

        # 3. FAQ Section Score (20 points)
        scores['faq_section'] = self._score_faq_section(content)
        if scores['faq_section']['score'] < 10:
            recommendations.append(
                "Add a FAQ section with 3-5 questions that match natural AI assistant queries"
            )

        # 4. Authority Signals Score (20 points)
        scores['authority_signals'] = self._score_authority_signals(content)
        if scores['authority_signals']['score'] < 12:
            recommendations.append(
                "Add authority signals: statistics, expert quotes, or source citations"
            )

        # 5. Structure Score (15 points)
        scores['structure'] = self._score_aeo_structure(content)
        if scores['structure']['score'] < 10:
            recommendations.append(
                "Improve heading structure with clear H2/H3 hierarchy for better AI parsing"
            )

        total_score = sum(s['score'] for s in scores.values())

        result = {
            'total_score': round(total_score, 1),
            'max_score': 100,
            'grade': self._aeo_grade(total_score),
            'scores': scores,
            'recommendations': recommendations
        }

        self.logger.info(f"AEO readiness score: {total_score}/100 ({result['grade']})")
        return result

    # -------------------------------------------------------------------------
    # Private helper methods for AEO
    # -------------------------------------------------------------------------

    def _build_aeo_requirements(self, authority_signals: Optional[List[str]] = None) -> str:
        """Build AEO-specific requirements for the blog post prompt"""
        if authority_signals is None:
            authority_signals = []

        requirements = f"""
AEO (ANSWER ENGINE OPTIMIZATION) REQUIREMENTS:
10. DIRECT ANSWER: The first paragraph MUST contain a clear, definitive answer to the topic's
    core question in 40-60 words. Start with a direct statement using "is", "means", or "provides".
    This paragraph should be independently quotable by AI assistants.
11. ENTITY CLARITY: Use "{BRAND_NAME}" by its full name consistently (not pronouns or abbreviations).
    First mention should include the full brand name and what it is.
12. DEFINITIVE LANGUAGE: Use authoritative language throughout. Prefer "is", "provides", "ensures"
    over "might", "could", "may". Position as THE expert, not "an" expert.
13. SECTION INDEPENDENCE: Each H2 section should make sense on its own when quoted by an AI assistant.
    Front-load the key point in the first sentence of each section."""

        if "expert_quotes" in authority_signals:
            requirements += """
14. EXPERT QUOTES: Include 1-2 expert-style quotes or industry insights that add credibility."""

        if "statistics" in authority_signals:
            requirements += """
15. STATISTICS: Include 2-3 specific statistics, numbers, or data points that support key claims."""

        if "citations" in authority_signals:
            requirements += """
16. CITATIONS: Reference credible sources or industry standards to support claims."""

        return requirements

    def _build_aeo_format_instructions(self, include_faq: bool, num_faq_items: int) -> str:
        """Build AEO-specific format instructions"""
        fmt = """
AEO FORMAT:
- First paragraph: Direct answer (40-60 words, quotable summary)
- Each section: Key point in first sentence, then supporting details
- Use question-based H2/H3 headers where natural (matches AI queries)"""

        if include_faq:
            fmt += f"""
- FAQ Section: Include {num_faq_items} FAQ items at the end, each with a direct answer first sentence"""

        return fmt

    def _build_blog_system_context(self, aeo_optimized: bool) -> str:
        """Build the system context for blog post generation"""
        context = """
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

        if aeo_optimized:
            context += f"""

AEO (Answer Engine Optimization) Strategy:
- AI assistants (ChatGPT, Claude, Perplexity) prioritize clear, authoritative, structured answers
- The first paragraph is critical: AI assistants often quote the opening summary
- Each section should be independently meaningful when extracted
- Definitive language builds citation confidence for AI models
- Consistent entity naming ("{BRAND_NAME}") helps AI attribute correctly
- FAQ sections match natural language queries users ask AI assistants
- Authority signals (stats, expert references) increase citation likelihood

Citation Optimization:
- Make key statements quotable and self-contained
- Use "{BRAND_NAME}" (not "we" or "our") so AI can attribute properly
- Support claims with specifics (numbers, specifications, examples)
- Structure content so each section answers a specific question"""

        return context

    def _extract_faq_items(self, content: str) -> List[Dict[str, str]]:
        """Extract FAQ question/answer pairs from blog content"""
        faq_items = []

        # Find FAQ section
        faq_match = re.search(
            r'(?:## (?:FAQ|Frequently Asked Questions).*?\n)(.*)',
            content, re.DOTALL | re.IGNORECASE
        )
        if not faq_match:
            return faq_items

        faq_text = faq_match.group(1)

        # Extract individual Q&A pairs (### Question format)
        qa_pattern = re.compile(
            r'###\s+(.+?\?)\s*\n\n?(.*?)(?=\n###|\n##|\Z)',
            re.DOTALL
        )
        for match in qa_pattern.finditer(faq_text):
            question = match.group(1).strip()
            answer = match.group(2).strip()
            if question and answer:
                faq_items.append({
                    'question': question,
                    'answer': answer
                })

        self.logger.debug(f"Extracted {len(faq_items)} FAQ items from content")
        return faq_items

    def _score_direct_answer(self, content: str) -> Dict[str, Any]:
        """Score direct answer optimization (max 25 points)"""
        score = 0
        feedback = []

        # Get first paragraph (skip title and meta comment)
        paragraphs = []
        for p in content.split('\n\n'):
            p = p.strip()
            if p and not p.startswith('#') and not p.startswith('<!--'):
                paragraphs.append(p)
                break

        if not paragraphs:
            return {'score': 0, 'max': 25, 'feedback': ['No introductory paragraph found']}

        first_para = paragraphs[0]
        first_para_words = first_para.split()
        word_count = len(first_para_words)

        # Check word count of first paragraph (40-60 words ideal)
        if 35 <= word_count <= 70:
            score += 8
            feedback.append(f"First paragraph length is good ({word_count} words)")
        elif 20 <= word_count <= 100:
            score += 4
            feedback.append(f"First paragraph is acceptable ({word_count} words, ideal: 40-60)")
        else:
            feedback.append(f"First paragraph is {'too short' if word_count < 20 else 'too long'} ({word_count} words)")

        # Check for definitive language in first paragraph
        definitive_patterns = [
            r'\bis\b', r'\bare\b', r'\bprovides?\b', r'\bensures?\b',
            r'\bmeans?\b', r'\boffers?\b', r'\bdelivers?\b', r'\brepresents?\b'
        ]
        definitive_count = sum(
            1 for pattern in definitive_patterns
            if re.search(pattern, first_para, re.IGNORECASE)
        )
        if definitive_count >= 3:
            score += 7
            feedback.append("Strong definitive language in opening")
        elif definitive_count >= 1:
            score += 4
            feedback.append("Some definitive language in opening")
        else:
            feedback.append("Opening lacks definitive language (use 'is', 'provides', 'means')")

        # Check for hedging language (negative signal)
        hedge_patterns = [r'\bmight\b', r'\bcould\b', r'\bperhaps\b', r'\bmaybe\b', r'\bpossibly\b']
        hedge_count = sum(
            1 for pattern in hedge_patterns
            if re.search(pattern, first_para, re.IGNORECASE)
        )
        if hedge_count == 0:
            score += 5
            feedback.append("No hedging language in opening")
        else:
            score += max(0, 5 - hedge_count * 2)
            feedback.append(f"Found {hedge_count} hedging words in opening (avoid 'might', 'could', 'perhaps')")

        # Check that first sentence is self-contained (ends with period)
        first_sentence_match = re.match(r'[^.!?]+[.!?]', first_para)
        if first_sentence_match:
            score += 5
            feedback.append("First sentence is self-contained and quotable")
        else:
            feedback.append("First sentence should end with clear punctuation")

        return {'score': min(score, 25), 'max': 25, 'feedback': feedback}

    def _score_entity_clarity(self, content: str) -> Dict[str, Any]:
        """Score entity clarity and consistent brand naming (max 20 points)"""
        score = 0
        feedback = []

        # Count brand name mentions
        brand_mentions = len(re.findall(re.escape(BRAND_NAME), content, re.IGNORECASE))

        # Check first mention includes full brand name
        first_mention_idx = content.lower().find(BRAND_NAME.lower())
        has_first_mention = first_mention_idx >= 0

        if brand_mentions >= 5:
            score += 8
            feedback.append(f"Good brand frequency ({brand_mentions} mentions)")
        elif brand_mentions >= 3:
            score += 5
            feedback.append(f"Adequate brand frequency ({brand_mentions} mentions)")
        elif brand_mentions >= 1:
            score += 2
            feedback.append(f"Low brand frequency ({brand_mentions} mentions, aim for 5+)")
        else:
            feedback.append("Brand name not found in content")

        if has_first_mention:
            score += 4
            feedback.append("Brand name present in content")
        else:
            feedback.append(f"Include '{BRAND_NAME}' by full name in content")

        # Check for pronoun overuse instead of brand name (rough heuristic)
        we_count = len(re.findall(r'\b(?:we|our|us)\b', content, re.IGNORECASE))
        brand_to_pronoun_ratio = brand_mentions / max(we_count, 1)
        if brand_to_pronoun_ratio >= 0.5 or we_count < 5:
            score += 4
            feedback.append("Good brand name to pronoun ratio")
        else:
            score += 1
            feedback.append(
                f"Consider replacing some 'we/our' ({we_count}) with '{BRAND_NAME}' for AI attribution"
            )

        # Check for consistent naming (no abbreviations/variations)
        # Look for potential abbreviations like "IV" that might confuse AI
        variations = re.findall(r'\bIV\b', content)
        if len(variations) == 0:
            score += 4
            feedback.append("No ambiguous abbreviations found")
        else:
            score += 1
            feedback.append(f"Found {len(variations)} potential abbreviations - use full brand name")

        return {
            'score': min(score, 20), 'max': 20,
            'brand_mentions': brand_mentions, 'feedback': feedback
        }

    def _score_faq_section(self, content: str) -> Dict[str, Any]:
        """Score FAQ section presence and quality (max 20 points)"""
        score = 0
        feedback = []

        faq_items = self._extract_faq_items(content)
        num_items = len(faq_items)

        if num_items == 0:
            # Check for any FAQ-like section even without standard format
            has_faq_header = bool(re.search(r'##.*(?:FAQ|Frequently Asked)', content, re.IGNORECASE))
            if has_faq_header:
                score += 4
                feedback.append("FAQ section header found but no extractable Q&A items")
            else:
                feedback.append("No FAQ section found - add FAQ for AEO optimization")
            return {'score': score, 'max': 20, 'num_items': 0, 'feedback': feedback}

        # Score based on number of items
        if num_items >= 5:
            score += 8
            feedback.append(f"Excellent FAQ coverage ({num_items} items)")
        elif num_items >= 3:
            score += 5
            feedback.append(f"Good FAQ coverage ({num_items} items, aim for 5+)")
        else:
            score += 3
            feedback.append(f"FAQ section present ({num_items} items, aim for 5+)")

        # Score FAQ answer quality (check first item as representative)
        if faq_items:
            first_answer = faq_items[0]['answer']
            first_answer_words = len(first_answer.split())

            # Check answer length
            if 30 <= first_answer_words <= 100:
                score += 4
                feedback.append("FAQ answer length is appropriate")
            elif first_answer_words > 100:
                score += 2
                feedback.append("FAQ answers may be too long for AI citation (aim for 30-100 words)")
            else:
                score += 1
                feedback.append("FAQ answers are too brief (aim for 30-100 words)")

            # Check for definitive language in FAQ answers
            definitive = bool(re.search(
                r'\b(?:is|are|means|provides|ensures)\b', first_answer, re.IGNORECASE
            ))
            if definitive:
                score += 4
                feedback.append("FAQ answers use definitive language")
            else:
                score += 1
                feedback.append("FAQ answers should use more definitive language")

            # Check questions end with question mark
            questions_valid = all(q['question'].strip().endswith('?') for q in faq_items)
            if questions_valid:
                score += 4
                feedback.append("All FAQ questions are properly formatted")
            else:
                score += 2
                feedback.append("Some FAQ questions missing question marks")

        return {'score': min(score, 20), 'max': 20, 'num_items': num_items, 'feedback': feedback}

    def _score_authority_signals(self, content: str) -> Dict[str, Any]:
        """Score presence of authority signals (max 20 points)"""
        score = 0
        feedback = []
        signals_found = []

        # Check for statistics/numbers
        stat_patterns = [
            r'\d+%', r'\d+\s*(?:percent|million|billion|thousand)',
            r'(?:studies?\s+show|research\s+(?:shows?|indicates?|suggests?))',
            r'(?:according\s+to|data\s+(?:shows?|from))'
        ]
        stats_found = sum(
            1 for pattern in stat_patterns
            if re.search(pattern, content, re.IGNORECASE)
        )
        if stats_found >= 2:
            score += 7
            signals_found.append("statistics/data points")
            feedback.append(f"Good use of statistics ({stats_found} instances)")
        elif stats_found >= 1:
            score += 4
            signals_found.append("statistics")
            feedback.append("Some statistics present (aim for 2+ data points)")
        else:
            feedback.append("Add statistics or data points for authority")

        # Check for expert references/quotes
        expert_patterns = [
            r'"[^"]{20,}"',  # Quoted text (potential expert quotes)
            r'(?:experts?\s+(?:say|recommend|suggest|note))',
            r'(?:industry|professional|specialist|veteran)',
            r'(?:according\s+to\s+\w+)',
        ]
        experts_found = sum(
            1 for pattern in expert_patterns
            if re.search(pattern, content, re.IGNORECASE)
        )
        if experts_found >= 2:
            score += 7
            signals_found.append("expert references")
            feedback.append("Strong expert/authority references")
        elif experts_found >= 1:
            score += 4
            signals_found.append("expert reference")
            feedback.append("Some expert references (add more for credibility)")
        else:
            feedback.append("Add expert quotes or industry references")

        # Check for specific claims (not vague)
        specificity_patterns = [
            r'\d+[\-\s](?:year|month|day|hour)',
            r'\d+(?:\.\d+)?\s*(?:inch|mm|cm|oz|lb|gram)',
            r'(?:specifically|precisely|exactly)',
        ]
        specific_count = sum(
            1 for pattern in specificity_patterns
            if re.search(pattern, content, re.IGNORECASE)
        )
        if specific_count >= 2:
            score += 6
            signals_found.append("specific claims")
            feedback.append("Content includes specific, verifiable details")
        elif specific_count >= 1:
            score += 3
            signals_found.append("specific claim")
            feedback.append("Some specificity present (add measurements, timeframes, specs)")
        else:
            feedback.append("Add specific details (measurements, timeframes, specifications)")

        return {
            'score': min(score, 20), 'max': 20,
            'signals_found': signals_found, 'feedback': feedback
        }

    def _score_aeo_structure(self, content: str) -> Dict[str, Any]:
        """Score content structure for AI parsing (max 15 points)"""
        score = 0
        feedback = []

        # Count heading levels
        h1_count = len(re.findall(r'^# [^#]', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## [^#]', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### [^#]', content, re.MULTILINE))

        # H1 should be exactly 1
        if h1_count == 1:
            score += 3
            feedback.append("Correct single H1 heading")
        elif h1_count > 1:
            score += 1
            feedback.append(f"Multiple H1 headings found ({h1_count}), use exactly 1")
        else:
            feedback.append("Missing H1 heading")

        # H2 structure
        if h2_count >= 4:
            score += 4
            feedback.append(f"Good section structure ({h2_count} H2 headings)")
        elif h2_count >= 2:
            score += 2
            feedback.append(f"Basic structure ({h2_count} H2 headings, aim for 4+)")
        else:
            feedback.append("Add more H2 sections for better AI parsing")

        # Check for question-based headings (great for AEO)
        question_headings = len(re.findall(r'^##+ .+\?$', content, re.MULTILINE))
        if question_headings >= 2:
            score += 4
            feedback.append(f"Question-based headings present ({question_headings})")
        elif question_headings >= 1:
            score += 2
            feedback.append("Some question-based headings (add more to match AI queries)")
        else:
            score += 0
            feedback.append("Add question-based headings (e.g., '## What Is...?') to match AI queries")

        # Check for logical hierarchy (H3 under H2)
        if h3_count > 0 and h2_count > 0:
            score += 4
            feedback.append("Good heading hierarchy (H2 + H3)")
        elif h2_count > 0:
            score += 2
            feedback.append("Consider adding H3 sub-sections for depth")
        else:
            feedback.append("Improve overall heading structure")

        return {
            'score': min(score, 15), 'max': 15,
            'h1': h1_count, 'h2': h2_count, 'h3': h3_count,
            'question_headings': question_headings,
            'feedback': feedback
        }

    @staticmethod
    def _aeo_grade(score: float) -> str:
        """Convert AEO score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
