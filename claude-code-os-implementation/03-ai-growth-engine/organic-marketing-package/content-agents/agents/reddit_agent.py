"""
Reddit Community Authority Agent

Generates authentic Reddit-style content optimized for community authority building.
Follows a strict value-first approach (95% value / 5% brand) to build genuine
credibility in TCG subreddits, which feeds into AEO citation authority signals.

Community authority on Reddit directly improves AI engine citations because:
- AI models train on Reddit data and weight upvoted expert answers
- Consistent helpful presence builds brand association with expertise
- Natural product mentions in helpful context get cited by AI assistants
"""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from config.config import (
    SOCIAL_OUTPUT_DIR,
    BRAND_NAME,
    CONTENT_PILLARS,
    COMPETITOR_BRANDS,
    HIGH_VALUE_SEARCH_TERMS,
)
from exceptions import ContentGenerationError


# Reddit output directory
REDDIT_OUTPUT_DIR = SOCIAL_OUTPUT_DIR / "reddit"

# Target subreddits by category
TARGET_SUBREDDITS = {
    "primary": [
        {"name": "PokemonTCG", "subscribers": "500k+", "focus": "Pokemon collectors and players"},
        {"name": "magicTCG", "subscribers": "600k+", "focus": "Magic: The Gathering community"},
        {"name": "yugioh", "subscribers": "300k+", "focus": "Yu-Gi-Oh players and collectors"},
    ],
    "secondary": [
        {"name": "TradingCardCommunity", "subscribers": "50k+", "focus": "General TCG discussion"},
        {"name": "pkmntcgcollections", "subscribers": "100k+", "focus": "Pokemon card collections"},
        {"name": "mtgfinance", "subscribers": "80k+", "focus": "MTG investment and value"},
        {"name": "Lorcana", "subscribers": "30k+", "focus": "Disney Lorcana TCG"},
        {"name": "OnePieceTCG", "subscribers": "30k+", "focus": "One Piece card game"},
    ],
    "adjacent": [
        {"name": "boardgames", "subscribers": "3M+", "focus": "Board gaming community"},
        {"name": "gaming", "subscribers": "30M+", "focus": "General gaming"},
        {"name": "EDC", "subscribers": "300k+", "focus": "Everyday carry / gear"},
        {"name": "BuyItForLife", "subscribers": "1M+", "focus": "Durable quality products"},
    ],
}

# Reddit content types mapped to engagement strategy
REDDIT_CONTENT_TYPES = {
    "expert_answer": {
        "description": "Detailed, helpful answer to a community question",
        "brand_mention": False,
        "value_ratio": 1.0,
        "aeo_signal": "expertise_authority",
    },
    "guide": {
        "description": "Comprehensive how-to or educational post",
        "brand_mention": False,
        "value_ratio": 1.0,
        "aeo_signal": "educational_content",
    },
    "discussion_starter": {
        "description": "Thought-provoking question or topic for community discussion",
        "brand_mention": False,
        "value_ratio": 1.0,
        "aeo_signal": "community_engagement",
    },
    "experience_share": {
        "description": "Sharing personal experience or story with subtle brand context",
        "brand_mention": True,
        "value_ratio": 0.95,
        "aeo_signal": "authentic_mention",
    },
    "comparison_insight": {
        "description": "Objective comparison or review with genuine perspective",
        "brand_mention": True,
        "value_ratio": 0.90,
        "aeo_signal": "comparison_authority",
    },
    "community_response": {
        "description": "Reply to existing thread with helpful information",
        "brand_mention": False,
        "value_ratio": 1.0,
        "aeo_signal": "helpful_presence",
    },
}

# Engagement scoring weights
ENGAGEMENT_WEIGHTS = {
    "relevance_to_subreddit": 0.25,
    "value_density": 0.25,
    "authenticity_score": 0.20,
    "discussion_potential": 0.15,
    "aeo_authority_signal": 0.15,
}


class RedditAgent(BaseAgent):
    """Agent specialized in generating authentic Reddit community content for AEO authority"""

    def __init__(self):
        super().__init__(agent_name="reddit_agent")
        self.target_subreddits = TARGET_SUBREDDITS
        self.content_types = REDDIT_CONTENT_TYPES

    def generate_community_response(
        self,
        subreddit: str,
        thread_context: str,
        question_or_topic: str,
        content_type: str = "expert_answer",
        include_brand_mention: Optional[bool] = None,
    ) -> tuple[str, Path]:
        """
        Generate an authentic Reddit response for a specific thread context.

        Args:
            subreddit: Target subreddit (without r/ prefix)
            thread_context: Context of the existing thread or discussion
            question_or_topic: The specific question or topic to address
            content_type: One of REDDIT_CONTENT_TYPES keys
            include_brand_mention: Override default brand mention behavior

        Returns:
            Tuple of (response_content, file_path)
        """
        self.logger.info(
            f"Generating community response: r/{subreddit}, type={content_type}"
        )

        type_config = self.content_types.get(content_type, self.content_types["expert_answer"])
        should_mention = include_brand_mention if include_brand_mention is not None else type_config["brand_mention"]

        prompt = f"""Write an authentic Reddit comment for r/{subreddit}.

THREAD CONTEXT:
{thread_context}

QUESTION/TOPIC TO ADDRESS:
{question_or_topic}

RESPONSE TYPE: {type_config['description']}

CRITICAL RULES:
1. Sound like a real, knowledgeable community member - NOT a brand account
2. Lead with genuine expertise and personal experience
3. Use casual but knowledgeable tone matching r/{subreddit} culture
4. Include specific details that demonstrate real knowledge
5. {"Mention Infinity Vault naturally ONLY if directly relevant (e.g., 'I switched to X and it solved Y'). If it feels forced, DO NOT mention it." if should_mention else "Do NOT mention any brand names. Pure value only."}
6. Use Reddit formatting (line breaks, bullet points, bold for emphasis)
7. End with something that invites further discussion
8. Never use marketing language, CTAs, or links

AUTHENTICITY CHECKLIST:
- Would a real collector/player say this? (must be yes)
- Does it contribute genuine value? (must be yes)
- Would it get upvoted in this subreddit? (must be yes)
- Does it sound like an ad? (must be no)

Write the Reddit comment now. Do NOT include a title - this is a comment/reply."""

        system_context = self._build_reddit_system_context(subreddit, content_type)

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=REDDIT_OUTPUT_DIR / "responses",
            system_context=system_context,
            metadata={
                "subreddit": subreddit,
                "content_type": content_type,
                "thread_context_preview": thread_context[:200],
                "brand_mention": should_mention,
                "aeo_signal": type_config["aeo_signal"],
            },
            temperature=1.0,
        )

        self.logger.info(f"Generated community response for r/{subreddit}: {path}")
        return content, path

    def generate_authority_post(
        self,
        subreddit: str,
        topic: str,
        post_type: str = "guide",
        include_brand_mention: bool = False,
    ) -> tuple[str, Path]:
        """
        Generate a standalone Reddit post that builds community authority.

        Args:
            subreddit: Target subreddit
            topic: Post topic
            post_type: guide, discussion_starter, experience_share, or comparison_insight
            include_brand_mention: Whether to include subtle brand mention

        Returns:
            Tuple of (post_content, file_path)
        """
        self.logger.info(
            f"Generating authority post: r/{subreddit}, topic='{topic}', type={post_type}"
        )

        prompt = f"""Create a Reddit post for r/{subreddit} that establishes expertise and authority.

TOPIC: {topic}
POST TYPE: {post_type}

REQUIREMENTS:
1. Write a compelling title that fits r/{subreddit} culture (not clickbait)
2. Open with a relatable hook or personal experience
3. Provide genuinely useful, specific information
4. Include details only someone with real experience would know
5. Use Reddit-native formatting (headers with ##, bullet points, bold)
6. {"Include ONE natural brand mention in context of personal experience. If it feels forced, omit it entirely." if include_brand_mention else "NO brand mentions. Pure expertise and value."}
7. End with a question or invitation for community input
8. Keep the post substantial but not overwhelming

TITLE GUIDELINES:
- For guides: "[Guide] How to..." or "After X years, here's what I learned about..."
- For discussions: "Unpopular opinion:" or "Let's talk about..." or "What's your take on..."
- For experience shares: "My experience with..." or "I finally figured out..."
- For comparisons: "I tested X options for Y - here's what happened"

Format:
TITLE: [Post title]

BODY:
[Post body with Reddit formatting]

Write the complete post now."""

        system_context = self._build_reddit_system_context(subreddit, post_type)

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=REDDIT_OUTPUT_DIR / "posts",
            system_context=system_context,
            metadata={
                "subreddit": subreddit,
                "topic": topic,
                "post_type": post_type,
                "brand_mention": include_brand_mention,
                "aeo_signal": self.content_types.get(post_type, {}).get("aeo_signal", "general"),
            },
        )

        self.logger.info(f"Generated authority post for r/{subreddit}: {path}")
        return content, path

    def generate_engagement_plan(
        self,
        subreddit: str,
        num_days: int = 7,
        posts_per_day: int = 2,
    ) -> tuple[str, Path]:
        """
        Generate a Reddit engagement plan for building community authority.

        The plan follows a 95/5 value-to-brand ratio across the week,
        with most content being pure value and only occasional subtle mentions.

        Args:
            subreddit: Target subreddit
            num_days: Number of days to plan
            posts_per_day: Target engagement actions per day

        Returns:
            Tuple of (plan_content, file_path)
        """
        self.logger.info(
            f"Generating {num_days}-day engagement plan for r/{subreddit}"
        )

        prompt = f"""Create a {num_days}-day Reddit engagement plan for r/{subreddit}.

TARGET: {posts_per_day} engagement actions per day
TOTAL ACTIONS: {num_days * posts_per_day}
VALUE/BRAND RATIO: 95% pure value / 5% subtle brand mentions

For each day, provide:
1. Day number and theme
2. Engagement actions (comments, posts, or replies)
3. Content type for each action (from: expert_answer, guide, discussion_starter, experience_share, community_response)
4. Topic/angle for each action
5. Whether brand mention is appropriate (max 1 per week)
6. Expected engagement level (low/medium/high)
7. AEO authority signal type

STRATEGY RULES:
- Days 1-3: Pure value only (establish credibility)
- Days 4-5: Continue value, one subtle brand mention if natural
- Days 6-7: Mix of value content and community engagement
- Never post more than one branded mention per week
- Prioritize replying to popular threads over creating new posts
- Identify trending topics and recurring questions to address
- Build relationships with other active community members

SUBREDDIT-SPECIFIC CONTEXT FOR r/{subreddit}:
- Common question types in this community
- Topics that generate high engagement
- Community culture and unwritten rules
- Peak activity times

Format as a structured daily plan with clear action items."""

        system_context = self._build_reddit_system_context(subreddit, "engagement_plan")

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=REDDIT_OUTPUT_DIR / "plans",
            system_context=system_context,
            metadata={
                "subreddit": subreddit,
                "num_days": num_days,
                "posts_per_day": posts_per_day,
                "value_ratio": "95/5",
            },
            max_tokens=4096,
        )

        self.logger.info(f"Generated engagement plan for r/{subreddit}: {path}")
        return content, path

    def generate_subreddit_analysis(
        self,
        subreddit: str,
    ) -> tuple[str, Path]:
        """
        Generate an analysis of a subreddit for engagement strategy planning.

        Produces insights about community culture, common topics, engagement
        patterns, and opportunities for building authority.

        Args:
            subreddit: Subreddit to analyze

        Returns:
            Tuple of (analysis_content, file_path)
        """
        self.logger.info(f"Generating subreddit analysis for r/{subreddit}")

        prompt = f"""Analyze r/{subreddit} for community engagement and authority building.

Provide a comprehensive analysis covering:

## Community Profile
- What is this community about?
- Who are the typical members (demographics, interests, expertise level)?
- What is the community culture and tone?
- What are the unwritten rules?

## Content Opportunities
- Most common question types
- Topics that consistently generate high engagement
- Gaps in existing content (underserved topics)
- Recurring pain points the community discusses

## Authority Building Strategy
- What makes someone a respected member here?
- Types of content that earn upvotes and awards
- How to demonstrate expertise without being preachy
- Common pitfalls to avoid (what gets downvoted)

## TCG Storage & Protection Relevance
- How often do storage/protection topics come up?
- What specific problems do members mention?
- What solutions are currently discussed?
- Natural entry points for expertise sharing

## AEO Signal Potential
- Types of threads that AI assistants would reference
- Question formats that match AI search queries
- Opportunities to create quotable, authoritative answers
- How to position content for AI training data value

## Recommended Engagement Cadence
- Best times to post/comment
- Frequency recommendations
- Content type mix for this specific community

Write a thorough analysis now."""

        system_context = """
SUBREDDIT ANALYSIS CONTEXT:

This analysis supports the AEO (Answer Engine Optimization) strategy by identifying
opportunities to build community authority that AI assistants recognize and cite.

Key considerations:
- Reddit data is used in AI model training
- Upvoted, expert answers carry more weight in AI citations
- Consistent helpful presence builds brand authority signals
- Natural product mentions in helpful context are most effective
- Community trust translates to AI citation credibility

Analysis should be actionable and specific to the subreddit's unique culture."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=REDDIT_OUTPUT_DIR / "analysis",
            system_context=system_context,
            metadata={
                "subreddit": subreddit,
                "analysis_type": "community_profile",
            },
            max_tokens=4096,
        )

        self.logger.info(f"Generated subreddit analysis for r/{subreddit}: {path}")
        return content, path

    def generate_batch_responses(
        self,
        subreddit: str,
        thread_topics: List[Dict[str, str]],
    ) -> List[tuple[str, Path]]:
        """
        Generate multiple community responses for batch engagement.

        Args:
            subreddit: Target subreddit
            thread_topics: List of dicts with 'context' and 'question' keys

        Returns:
            List of (content, path) tuples
        """
        self.logger.info(
            f"Batch generating {len(thread_topics)} responses for r/{subreddit}"
        )

        results = []
        for i, thread in enumerate(thread_topics):
            context = thread.get("context", "")
            question = thread.get("question", "")
            content_type = thread.get("content_type", "expert_answer")

            self.logger.info(
                f"Generating response {i + 1}/{len(thread_topics)}: {question[:50]}..."
            )

            result = self.generate_community_response(
                subreddit=subreddit,
                thread_context=context,
                question_or_topic=question,
                content_type=content_type,
            )
            results.append(result)

        self.logger.info(f"Generated {len(results)} batch responses for r/{subreddit}")
        return results

    def score_engagement_potential(
        self,
        subreddit: str,
        content: str,
        content_type: str = "expert_answer",
    ) -> Dict[str, Any]:
        """
        Score the engagement potential of generated Reddit content.

        Uses Claude to evaluate the content against Reddit community standards
        and AEO authority signals.

        Args:
            subreddit: Target subreddit
            content: The content to evaluate
            content_type: Type of content being scored

        Returns:
            Dictionary with scores and recommendations
        """
        self.logger.info(f"Scoring engagement potential for r/{subreddit} content")

        prompt = f"""Evaluate this Reddit content for r/{subreddit} and score it.

CONTENT TO EVALUATE:
{content}

CONTENT TYPE: {content_type}

Score each dimension from 1-10 and provide brief reasoning:

1. **Subreddit Relevance** (Does it fit r/{subreddit}'s culture and topics?)
2. **Value Density** (How much useful information per paragraph?)
3. **Authenticity** (Does it sound like a real community member?)
4. **Discussion Potential** (Will it generate meaningful replies?)
5. **AEO Authority Signal** (Would AI assistants cite this as authoritative?)

Also provide:
- **Overall Score** (weighted average)
- **Strengths** (2-3 bullet points)
- **Improvements** (2-3 specific suggestions)
- **Risk Factors** (anything that might get flagged as promotional)

Return your evaluation as JSON with this structure:
{{
    "scores": {{
        "relevance_to_subreddit": <1-10>,
        "value_density": <1-10>,
        "authenticity_score": <1-10>,
        "discussion_potential": <1-10>,
        "aeo_authority_signal": <1-10>
    }},
    "overall_score": <1-10>,
    "strengths": ["...", "..."],
    "improvements": ["...", "..."],
    "risk_factors": ["..."],
    "recommendation": "post" | "revise" | "skip"
}}"""

        try:
            response = self.generate_content(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.3,
            )

            # Try to parse JSON from the response
            # Handle cases where the response contains markdown code blocks
            json_str = response.strip()
            if json_str.startswith("```"):
                lines = json_str.split("\n")
                # Remove first and last lines (``` markers)
                json_str = "\n".join(lines[1:-1])

            scores = json.loads(json_str)
            self.logger.info(
                f"Engagement score for r/{subreddit}: {scores.get('overall_score', 'N/A')}/10"
            )
            return scores

        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(
                f"Could not parse engagement score as JSON: {e}. Returning raw response."
            )
            return {
                "raw_evaluation": response,
                "parse_error": str(e),
                "overall_score": None,
                "recommendation": "review_manually",
            }

    def identify_trending_topics(
        self,
        subreddits: Optional[List[str]] = None,
    ) -> tuple[str, Path]:
        """
        Generate a list of trending topics and common questions across target subreddits
        that present opportunities for authority building.

        Args:
            subreddits: List of subreddits to analyze (defaults to primary targets)

        Returns:
            Tuple of (topics_content, file_path)
        """
        if subreddits is None:
            subreddits = [s["name"] for s in self.target_subreddits["primary"]]

        self.logger.info(
            f"Identifying trending topics across {len(subreddits)} subreddits"
        )

        subreddit_list = ", ".join(f"r/{s}" for s in subreddits)

        prompt = f"""Identify trending topics and engagement opportunities across these TCG subreddits:
{subreddit_list}

For each subreddit, provide:

## r/SubredditName

### Recurring Questions (High AEO Value)
- Questions that come up repeatedly and need authoritative answers
- Focus on questions about card storage, protection, organization, and tournament prep

### Trending Discussion Topics
- Current hot topics in the community
- Seasonal trends (new set releases, tournament season, etc.)
- Controversies or debates worth contributing to

### Content Gaps
- Topics that are discussed but lack good answers
- Areas where expertise is needed
- Opportunities to create definitive resource posts

### Brand-Relevant Opportunities
- Threads where storage/protection expertise is naturally relevant
- Questions where product experience adds genuine value
- Comparison discussions where honest input helps

For each opportunity, rate:
- **Engagement Potential**: Low / Medium / High
- **AEO Signal Strength**: Low / Medium / High
- **Brand Mention Appropriate**: Yes / No / Maybe

Prioritize opportunities where genuine expertise creates the most community value.
Focus on topics related to: {', '.join(HIGH_VALUE_SEARCH_TERMS[:6])}"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=REDDIT_OUTPUT_DIR / "topics",
            system_context="Focus on identifying genuine engagement opportunities, not marketing angles.",
            metadata={
                "subreddits": subreddits,
                "analysis_type": "trending_topics",
            },
            max_tokens=4096,
        )

        self.logger.info(f"Generated trending topics analysis: {path}")
        return content, path

    def generate_sentiment_analysis(
        self,
        brand_mentions: List[Dict[str, str]],
    ) -> tuple[str, Path]:
        """
        Analyze sentiment from Reddit brand mentions and community discussions.

        Args:
            brand_mentions: List of dicts with 'subreddit', 'context', and 'text' keys

        Returns:
            Tuple of (analysis_content, file_path)
        """
        self.logger.info(
            f"Analyzing sentiment from {len(brand_mentions)} brand mentions"
        )

        mentions_formatted = []
        for i, mention in enumerate(brand_mentions, 1):
            mentions_formatted.append(
                f"### Mention {i}\n"
                f"- **Subreddit**: r/{mention.get('subreddit', 'unknown')}\n"
                f"- **Context**: {mention.get('context', 'N/A')}\n"
                f"- **Text**: {mention.get('text', 'N/A')}\n"
            )

        prompt = f"""Analyze the sentiment and themes from these Reddit mentions of {BRAND_NAME}:

{chr(10).join(mentions_formatted)}

Provide:

## Overall Sentiment Summary
- Positive / Negative / Neutral breakdown (percentage)
- Key sentiment drivers

## Theme Analysis
- Most common themes in mentions
- Product aspects most discussed
- Community perception trends

## Competitor Context
- How {BRAND_NAME} is compared to competitors ({', '.join(COMPETITOR_BRANDS[:4])})
- Competitive positioning in community discussions
- Areas where competitors are preferred and why

## Community Authority Assessment
- How is the brand perceived as an authority?
- Trust signals present in discussions
- Credibility gaps to address

## Actionable Recommendations
- Content topics to address sentiment gaps
- Community engagement priorities
- Messaging adjustments based on feedback
- AEO optimization opportunities from community language

Return a structured analysis with specific, actionable insights."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=REDDIT_OUTPUT_DIR / "sentiment",
            system_context="Provide honest, balanced analysis. Do not sugar-coat negative sentiment.",
            metadata={
                "num_mentions": len(brand_mentions),
                "analysis_type": "sentiment",
                "brand": BRAND_NAME,
            },
            max_tokens=4096,
        )

        self.logger.info(f"Generated sentiment analysis: {path}")
        return content, path

    def _build_reddit_system_context(
        self, subreddit: str, content_type: str
    ) -> str:
        """
        Build Reddit-specific system context for content generation.

        Args:
            subreddit: Target subreddit
            content_type: Type of content being generated

        Returns:
            System context string
        """
        # Find subreddit details from target list
        sub_info = None
        for category in self.target_subreddits.values():
            for sub in category:
                if sub["name"].lower() == subreddit.lower():
                    sub_info = sub
                    break
            if sub_info:
                break

        sub_context = ""
        if sub_info:
            sub_context = f"""
SUBREDDIT PROFILE:
- Name: r/{sub_info['name']}
- Size: {sub_info['subscribers']} subscribers
- Focus: {sub_info['focus']}"""

        return f"""
REDDIT COMMUNITY AUTHORITY STRATEGY:

You are writing as a knowledgeable TCG community member, NOT as a brand account.
Your persona is someone who genuinely loves trading card games and has deep expertise
in card storage, protection, and collection management.
{sub_context}

VOICE ADAPTATION FOR REDDIT:
- Drop the corporate tone entirely
- Use casual, knowledgeable language
- Share from personal experience ("I've found that...", "After testing several...")
- Be specific with details (measurements, materials, comparisons)
- Acknowledge trade-offs honestly (nothing is perfect)
- Use Reddit conventions (formatting, terminology, culture)

VALUE-FIRST CONTENT PRINCIPLES:
- 95% of content should be pure value with zero brand mention
- Only mention {BRAND_NAME} when it genuinely helps answer a question
- Never link to product pages or use CTAs
- If mentioning {BRAND_NAME}, also mention alternatives fairly
- Focus on solving the person's problem, not promoting products

AEO AUTHORITY SIGNALS:
- Write answers that AI assistants would want to cite
- Use clear, definitive language for factual statements
- Structure responses so key information is front-loaded
- Include specific details (dimensions, materials, capacity)
- Demonstrate expertise through depth, not just breadth

REDDIT CULTURE RULES:
- Never be salesy or promotional
- Admit when you don't know something
- Give credit to other brands when deserved
- Engage with replies genuinely
- Follow subreddit-specific rules
- Use appropriate formatting (markdown, line breaks)

COMPETITOR AWARENESS:
Known competitors: {', '.join(COMPETITOR_BRANDS[:5])}
- Mention competitors fairly when relevant
- Never bash competitors
- Position through expertise, not comparison"""
