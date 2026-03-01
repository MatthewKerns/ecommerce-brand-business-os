"""
Social Media Content Generation Agent
Creates platform-optimized social content (Instagram, Reddit, Discord, etc.)
"""
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from config.config import SOCIAL_OUTPUT_DIR, CONTENT_PILLARS


class SocialAgent(BaseAgent):
    """Agent specialized in creating social media content"""

    def __init__(self):
        super().__init__(agent_name="social_agent")

        self.logger.debug("Initializing platform specifications")

        # Platform-specific parameters
        self.platform_specs = {
            "instagram": {
                "caption_length": 2200,
                "hashtag_count": 20,
                "tone": "Visual, aspirational, community-focused"
            },
            "reddit": {
                "post_length": "varies",
                "tone": "Authentic, helpful, non-salesy"
            },
            "discord": {
                "message_length": 2000,
                "tone": "Casual, direct, community-oriented"
            },
            "twitter": {
                "post_length": 280,
                "tone": "Punchy, quotable, engaging"
            }
        }

    def generate_instagram_post(
        self,
        topic: str,
        content_pillar: Optional[str] = None,
        image_description: Optional[str] = None,
        include_hashtags: bool = True
    ) -> tuple[str, Path]:
        """
        Generate Instagram caption and hashtags

        Args:
            topic: Post topic/theme
            content_pillar: Content pillar alignment
            image_description: Description of the image that will accompany this
            include_hashtags: Whether to include hashtags

        Returns:
            Tuple of (post_content, file_path)
        """
        self.logger.info(f"Generating Instagram post: topic='{topic}', pillar={content_pillar}, hashtags={include_hashtags}")

        prompt = f"""Create an Instagram post caption:

TOPIC: {topic}
CONTENT PILLAR: {content_pillar or 'Choose most relevant'}
IMAGE: {image_description or 'Battle-ready gaming setup with Infinity Vault products'}

REQUIREMENTS:
1. Hook in first line (before "...more")
2. Tell a micro-story or share valuable insight
3. Connect to battle-ready identity
4. Inspire action or reflection
5. Include call-to-action (follow, comment, save, shop)
{"6. Include relevant hashtags (mix of popular and niche)" if include_hashtags else ""}
7. Keep under 2200 characters
8. Use 2-3 emojis MAX (strategically, not excessive)
9. Write in Infinity Vault brand voice

TONE: Confident, passionate, empowering - make followers feel like serious players

Format:
[Hook opening line]

[Main caption body]

[Call-to-action]

{"[Hashtags - separated with spaces]" if include_hashtags else ""}

Write the complete Instagram caption now."""

        system_context = """
INSTAGRAM STRATEGY:

Content Types:
- Product showcases (battle-ready gear)
- Community spotlights (player features)
- Tournament prep tips
- Collection care advice
- Behind-the-scenes
- User-generated content reposts

Best Practices:
- First line must hook (shows before "...more")
- Use line breaks for readability
- Ask questions to drive comments
- Tag locations for local game stores
- Use Stories highlights for evergreen content

Hashtag Strategy:
- Mix sizes: 100K+ (reach), 10K-100K (engagement), <10K (niche)
- Include branded: #InfinityVault #ShowUpBattleReady
- TCG-specific: #TCG #PokemonTCG #MagicTheGathering
- Lifestyle: #TradingCards #CardCollector #GamingGear"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=SOCIAL_OUTPUT_DIR / "instagram",
            system_context=system_context,
            metadata={
                "platform": "instagram",
                "topic": topic,
                "content_pillar": content_pillar,
                "image_description": image_description
            }
        )

        self.logger.info(f"Successfully generated Instagram post: {path}")
        return content, path

    def generate_reddit_post(
        self,
        subreddit: str,
        topic: str,
        post_type: str = "discussion",
        include_product_mention: bool = False
    ) -> tuple[str, Path]:
        """
        Generate Reddit post (title + body)

        Args:
            subreddit: Target subreddit
            topic: Post topic
            post_type: discussion, question, guide, showcase
            include_product_mention: Whether to subtly mention products

        Returns:
            Tuple of (post_content, file_path)
        """
        self.logger.info(f"Generating Reddit post: subreddit=r/{subreddit}, topic='{topic}', type={post_type}")

        prompt = f"""Create a Reddit post for r/{subreddit}:

TOPIC: {topic}
POST TYPE: {post_type}
PRODUCT MENTION: {"Subtle mention OK (authentic, not salesy)" if include_product_mention else "Pure value, no selling"}

REQUIREMENTS:
1. Compelling title that fits subreddit culture
2. Valuable, authentic content
3. Never sound like an ad
4. Contribute to the community genuinely
5. If mentioning Infinity Vault, do so naturally (e.g., "I use X for Y")
6. Follow reddiquette
7. Encourage discussion

CRITICAL:
- Reddit hates obvious marketing
- Lead with value, not promotion
- Be a community member first, brand second
- If product mention feels forced, skip it

Format:
TITLE: [Post title]

BODY:
[Post body text]

Write the complete Reddit post now."""

        system_context = f"""
REDDIT STRATEGY:

Subreddit Context for r/{subreddit}:
- Understand the culture before posting
- Read rules and pinned posts
- Engage authentically, not transactionally

Content Approach:
- 90% value, 10% brand (if at all)
- Answer questions helpfully
- Share expertise and experiences
- Build karma through genuine contributions
- Mention products only when directly relevant

Common Subreddits for TCG:
- r/PokemonTCG (Pokemon collectors)
- r/magicTCG (MTG players)
- r/yugioh (Yu-Gi-Oh players)
- r/TradingCardCommunity (general TCG)

Best Practices:
- Never use salesy language
- Disclose any brand affiliation if asked
- Focus on helping, not selling
- Upvote and reply to comments"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=SOCIAL_OUTPUT_DIR / "reddit",
            system_context=system_context,
            metadata={
                "platform": "reddit",
                "subreddit": subreddit,
                "topic": topic,
                "post_type": post_type
            }
        )

        self.logger.info(f"Successfully generated Reddit post for r/{subreddit}: {path}")
        return content, path

    def generate_content_calendar(
        self,
        platform: str,
        num_days: int = 7,
        content_pillar: Optional[str] = None
    ) -> tuple[str, Path]:
        """
        Generate a content calendar for a platform

        Args:
            platform: Platform name (instagram, reddit, etc.)
            num_days: Number of days to plan
            content_pillar: Focus on specific pillar or mix

        Returns:
            Tuple of (calendar_content, file_path)
        """
        self.logger.info(f"Generating {num_days}-day content calendar for {platform}, pillar={content_pillar}")

        start_date = datetime.now()
        dates = [(start_date + timedelta(days=i)).strftime("%A, %B %d") for i in range(num_days)]

        prompt = f"""Create a {num_days}-day content calendar for {platform.upper()}:

DATES: {dates[0]} through {dates[-1]}
CONTENT PILLAR FOCUS: {content_pillar or 'Mix of all pillars'}

For each day, provide:
1. Date and day of week
2. Content pillar
3. Post topic/theme
4. Content type (carousel, video, static image, story, etc.)
5. Key message/angle
6. Call-to-action
7. Suggested hashtags (if Instagram)

REQUIREMENTS:
- Vary content types and pillars
- Balance educational, inspirational, and promotional (80/20 rule)
- Consider posting times (evenings for gaming community)
- Build a narrative arc across the week
- Include community engagement opportunities

Format as a clear calendar structure."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=SOCIAL_OUTPUT_DIR / platform,
            filename=f"content_calendar_{num_days}days.md",
            system_context="Focus on strategic planning and variety",
            metadata={
                "platform": platform,
                "num_days": num_days,
                "start_date": start_date.isoformat()
            }
        )

        self.logger.info(f"Successfully generated content calendar: {path}")
        return content, path

    def generate_carousel_script(
        self,
        topic: str,
        num_slides: int = 10
    ) -> tuple[str, Path]:
        """
        Generate Instagram carousel post script

        Args:
            topic: Carousel topic
            num_slides: Number of slides (usually 10)

        Returns:
            Tuple of (carousel_script, file_path)
        """
        self.logger.info(f"Generating carousel script: topic='{topic}', num_slides={num_slides}")

        prompt = f"""Create an Instagram carousel post script:

TOPIC: {topic}
NUMBER OF SLIDES: {num_slides}

For each slide, provide:
1. Slide number
2. Visual direction (what should be on the slide)
3. Text overlay (headline/key point)
4. Design notes (colors, layout, imagery)

SLIDE 1 (Cover):
- Hook headline
- Eye-catching visual
- Must make people want to swipe

SLIDES 2-{num_slides-1} (Content):
- One key point per slide
- Visual + text working together
- Progressive story or educational content

SLIDE {num_slides} (CTA):
- Clear call-to-action
- Link in bio direction
- Follow prompt

REQUIREMENTS:
- Each slide stands alone but builds a narrative
- Text overlays are punchy (5-10 words max)
- Visuals reinforce battle-ready positioning
- Educational or inspirational value
- Brand-consistent design direction

Write the complete carousel script now."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=SOCIAL_OUTPUT_DIR / "instagram",
            filename=f"carousel_{topic.replace(' ', '_')}.md",
            metadata={
                "type": "carousel",
                "topic": topic,
                "num_slides": num_slides
            }
        )

        self.logger.info(f"Successfully generated carousel script: {path}")
        return content, path

    def batch_generate_posts(
        self,
        platform: str,
        num_posts: int = 5,
        content_mix: Optional[List[str]] = None
    ) -> List[tuple[str, Path]]:
        """
        Batch generate multiple posts

        Args:
            platform: Platform to generate for
            num_posts: Number of posts to create
            content_mix: List of content pillars to use (will cycle through)

        Returns:
            List of (content, path) tuples
        """
        self.logger.info(f"Batch generating {num_posts} posts for {platform}")

        if content_mix is None:
            content_mix = CONTENT_PILLARS

        results = []
        for i in range(num_posts):
            pillar = content_mix[i % len(content_mix)]

            topic_prompt = f"Suggest a specific post topic for {platform} using the '{pillar}' content pillar. Just provide the topic in 1-2 sentences."
            topic = self.generate_content(topic_prompt, max_tokens=100)

            self.logger.info(f"Generating {platform} post {i+1}/{num_posts}: {topic[:50]}...")

            if platform.lower() == "instagram":
                result = self.generate_instagram_post(topic, pillar)
            elif platform.lower() == "reddit":
                result = self.generate_reddit_post("TCG", topic, include_product_mention=(i % 3 == 0))
            else:
                self.logger.warning(f"Platform {platform} not implemented for batch generation yet.")
                continue

            results.append(result)

        self.logger.info(f"Successfully generated {len(results)} {platform} posts")
        return results
