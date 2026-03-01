"""
Content Generation Celery Tasks

This module contains Celery tasks for AI-powered content generation,
including blog posts and social media content with priority-based queueing.
"""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from celery import Task
from celery_app import app
from database.connection import get_db_session
from database.models import ContentHistory
from logging_config import get_logger

logger = get_logger("content_generation_tasks")


class ContentGenerationTask(Task):
    """
    Base task class for content generation tasks with agent lazy loading
    """
    _blog_agent = None
    _social_agent = None

    @property
    def blog_agent(self):
        """Lazy initialization of BlogAgent"""
        if self._blog_agent is None:
            from agents.blog_agent import BlogAgent
            self._blog_agent = BlogAgent()
            logger.debug("BlogAgent initialized for content generation")
        return self._blog_agent

    @property
    def social_agent(self):
        """Lazy initialization of SocialAgent"""
        if self._social_agent is None:
            from agents.social_agent import SocialAgent
            self._social_agent = SocialAgent()
            logger.debug("SocialAgent initialized for content generation")
        return self._social_agent


@app.task(
    bind=True,
    base=ContentGenerationTask,
    name="tasks.content_generation.generate_blog_post_task",
    max_retries=3,
    default_retry_delay=600  # 10 minutes
)
def generate_blog_post_task(
    self,
    topic: str,
    parameters: Optional[Dict[str, Any]] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Generate a blog post asynchronously and save as draft.

    This task runs in the background to generate blog content using the BlogAgent.
    Generated content is saved to ContentHistory with is_draft=True for human review.

    Args:
        topic: The blog post topic
        parameters: Optional parameters for blog generation:
            - content_pillar: Content pillar alignment
            - target_keywords: List of SEO keywords
            - word_count: Target word count (default: 1000)
            - include_cta: Include call-to-action (default: True)
            - include_seo_analysis: Perform SEO analysis (default: False)
            - aeo_optimized: Enable AEO optimization (default: False)
            - include_faq: Generate FAQ section (default: False)
            - num_faq_items: Number of FAQ items (default: 5)
        priority: Task priority (high, medium, low) for queue routing

    Returns:
        Dictionary with generation result:
        - success: Whether generation succeeded
        - content_id: ID of created ContentHistory record
        - topic: Blog post topic
        - priority: Task priority
        - request_id: Unique request identifier
        - error: Error message if failed

    Raises:
        Retry: Automatically retries on failure up to max_retries
    """
    logger.info(f"Starting blog post generation: topic='{topic}', priority={priority}")

    result = {
        "success": False,
        "content_id": None,
        "topic": topic,
        "priority": priority,
        "request_id": None,
        "error": None
    }

    # Generate unique request ID
    request_id = f"blog_{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}"
    result["request_id"] = request_id

    # Parse parameters with defaults
    if parameters is None:
        parameters = {}

    content_pillar = parameters.get("content_pillar")
    target_keywords = parameters.get("target_keywords")
    word_count = parameters.get("word_count", 1000)
    include_cta = parameters.get("include_cta", True)
    include_seo_analysis = parameters.get("include_seo_analysis", False)
    aeo_optimized = parameters.get("aeo_optimized", False)
    include_faq = parameters.get("include_faq", False)
    num_faq_items = parameters.get("num_faq_items", 5)

    db = get_db_session()

    try:
        # Generate blog post using BlogAgent
        logger.info(
            f"Calling BlogAgent: topic='{topic}', pillar={content_pillar}, "
            f"word_count={word_count}, aeo={aeo_optimized}"
        )

        generation_start = datetime.utcnow()

        content, file_path, seo_analysis = self.blog_agent.generate_blog_post(
            topic=topic,
            content_pillar=content_pillar,
            target_keywords=target_keywords,
            word_count=word_count,
            include_cta=include_cta,
            include_seo_analysis=include_seo_analysis,
            aeo_optimized=aeo_optimized,
            include_faq=include_faq,
            num_faq_items=num_faq_items
        )

        generation_end = datetime.utcnow()
        generation_time_ms = int((generation_end - generation_start).total_seconds() * 1000)

        logger.info(
            f"Blog post generated successfully: {len(content)} characters, "
            f"{generation_time_ms}ms"
        )

        # Save to ContentHistory as draft
        content_history = ContentHistory(
            request_id=request_id,
            content_type="blog",
            agent_name="blog_agent",
            prompt=f"Generate blog post on: {topic}",
            parameters=json.dumps(parameters),
            content_metadata=json.dumps({
                "topic": topic,
                "content_pillar": content_pillar,
                "file_path": str(file_path),
                "priority": priority
            }),
            content=content,
            content_format="markdown",
            model=self.blog_agent.model,
            tokens_used=0,  # BlogAgent doesn't expose token count directly
            generation_time_ms=generation_time_ms,
            status="success",
            is_draft=True,  # Mark as draft for human review
            version_number=1
        )

        # Add SEO metadata if analysis was performed
        if seo_analysis:
            content_history.seo_score = seo_analysis.get("total_score")
            content_history.seo_grade = seo_analysis.get("grade", "").replace("+", "")[:1]
            if target_keywords:
                content_history.target_keyword = target_keywords[0]

        db.add(content_history)
        db.commit()
        db.refresh(content_history)

        result["success"] = True
        result["content_id"] = content_history.id

        logger.info(
            f"Blog post saved to database: content_id={content_history.id}, "
            f"request_id={request_id}, is_draft=True"
        )

        return result

    except Exception as e:
        db.rollback()
        error_msg = f"Error generating blog post: {str(e)}"
        logger.error(error_msg, exc_info=True)
        result["error"] = error_msg

        # Save failed generation record
        try:
            content_history = ContentHistory(
                request_id=request_id,
                content_type="blog",
                agent_name="blog_agent",
                prompt=f"Generate blog post on: {topic}",
                parameters=json.dumps(parameters),
                content="",
                content_format="markdown",
                model=self.blog_agent.model,
                tokens_used=0,
                generation_time_ms=0,
                status="failed",
                error_message=str(e),
                is_draft=True
            )
            db.add(content_history)
            db.commit()
        except Exception as save_error:
            logger.error(f"Failed to save error record: {save_error}")

        # Retry the task
        raise self.retry(exc=e)

    finally:
        db.close()


@app.task(
    bind=True,
    base=ContentGenerationTask,
    name="tasks.content_generation.generate_social_post_task",
    max_retries=3,
    default_retry_delay=600  # 10 minutes
)
def generate_social_post_task(
    self,
    platform: str,
    topic: str,
    parameters: Optional[Dict[str, Any]] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Generate a social media post asynchronously and save as draft.

    This task runs in the background to generate social content using the SocialAgent.
    Generated content is saved to ContentHistory with is_draft=True for human review.

    Args:
        platform: Social media platform (instagram, reddit, twitter, discord)
        topic: The post topic/theme
        parameters: Optional parameters for social generation:
            - content_pillar: Content pillar alignment
            - image_description: For Instagram - description of accompanying image
            - include_hashtags: For Instagram - include hashtags (default: True)
            - subreddit: For Reddit - target subreddit
            - post_type: For Reddit - discussion, question, guide, showcase
            - include_product_mention: For Reddit - subtle product mention (default: False)
        priority: Task priority (high, medium, low) for queue routing

    Returns:
        Dictionary with generation result:
        - success: Whether generation succeeded
        - content_id: ID of created ContentHistory record
        - platform: Social media platform
        - topic: Post topic
        - priority: Task priority
        - request_id: Unique request identifier
        - error: Error message if failed

    Raises:
        Retry: Automatically retries on failure up to max_retries
    """
    logger.info(
        f"Starting social post generation: platform={platform}, topic='{topic}', "
        f"priority={priority}"
    )

    result = {
        "success": False,
        "content_id": None,
        "platform": platform,
        "topic": topic,
        "priority": priority,
        "request_id": None,
        "error": None
    }

    # Generate unique request ID
    request_id = f"social_{platform}_{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}"
    result["request_id"] = request_id

    # Parse parameters with defaults
    if parameters is None:
        parameters = {}

    db = get_db_session()

    try:
        # Generate social post based on platform
        logger.info(f"Calling SocialAgent: platform={platform}, topic='{topic}'")

        generation_start = datetime.utcnow()

        if platform.lower() == "instagram":
            content_pillar = parameters.get("content_pillar")
            image_description = parameters.get("image_description")
            include_hashtags = parameters.get("include_hashtags", True)

            content, file_path = self.social_agent.generate_instagram_post(
                topic=topic,
                content_pillar=content_pillar,
                image_description=image_description,
                include_hashtags=include_hashtags
            )

        elif platform.lower() == "reddit":
            subreddit = parameters.get("subreddit", "TCG")
            post_type = parameters.get("post_type", "discussion")
            include_product_mention = parameters.get("include_product_mention", False)

            content, file_path = self.social_agent.generate_reddit_post(
                subreddit=subreddit,
                topic=topic,
                post_type=post_type,
                include_product_mention=include_product_mention
            )

        else:
            raise ValueError(f"Unsupported platform: {platform}")

        generation_end = datetime.utcnow()
        generation_time_ms = int((generation_end - generation_start).total_seconds() * 1000)

        logger.info(
            f"Social post generated successfully: platform={platform}, "
            f"{len(content)} characters, {generation_time_ms}ms"
        )

        # Save to ContentHistory as draft
        content_history = ContentHistory(
            request_id=request_id,
            content_type="social",
            agent_name="social_agent",
            prompt=f"Generate {platform} post on: {topic}",
            parameters=json.dumps(parameters),
            content_metadata=json.dumps({
                "platform": platform,
                "topic": topic,
                "file_path": str(file_path),
                "priority": priority
            }),
            content=content,
            content_format="markdown",
            model=self.social_agent.model,
            tokens_used=0,  # SocialAgent doesn't expose token count directly
            generation_time_ms=generation_time_ms,
            status="success",
            is_draft=True,  # Mark as draft for human review
            version_number=1
        )

        db.add(content_history)
        db.commit()
        db.refresh(content_history)

        result["success"] = True
        result["content_id"] = content_history.id

        logger.info(
            f"Social post saved to database: content_id={content_history.id}, "
            f"request_id={request_id}, platform={platform}, is_draft=True"
        )

        return result

    except Exception as e:
        db.rollback()
        error_msg = f"Error generating social post: {str(e)}"
        logger.error(error_msg, exc_info=True)
        result["error"] = error_msg

        # Save failed generation record
        try:
            content_history = ContentHistory(
                request_id=request_id,
                content_type="social",
                agent_name="social_agent",
                prompt=f"Generate {platform} post on: {topic}",
                parameters=json.dumps(parameters),
                content="",
                content_format="markdown",
                model=self.social_agent.model,
                tokens_used=0,
                generation_time_ms=0,
                status="failed",
                error_message=str(e),
                is_draft=True
            )
            db.add(content_history)
            db.commit()
        except Exception as save_error:
            logger.error(f"Failed to save error record: {save_error}")

        # Retry the task
        raise self.retry(exc=e)

    finally:
        db.close()
