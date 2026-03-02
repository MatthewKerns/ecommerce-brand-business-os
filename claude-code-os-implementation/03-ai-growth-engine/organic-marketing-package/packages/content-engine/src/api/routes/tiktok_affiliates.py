"""
TikTok Shop Affiliate API Routes

REST API endpoints for managing TikTok Shop affiliate outreach,
creator discovery, campaign management, and performance tracking.
"""
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tiktok/affiliates",
    tags=["TikTok Affiliates"],
)


# ========================================================================
# REQUEST/RESPONSE MODELS
# ========================================================================

class CreatorSearchRequest(BaseModel):
    """Request model for searching affiliate creators."""
    category: Optional[str] = Field(None, description="Product category filter")
    min_gmv_30d: Optional[float] = Field(None, description="Min GMV last 30 days")
    max_gmv_30d: Optional[float] = Field(None, description="Max GMV last 30 days")
    min_followers: Optional[int] = Field(None, description="Min follower count")
    max_followers: Optional[int] = Field(None, description="Max follower count")
    min_sales_30d: Optional[int] = Field(None, description="Min sales last 30 days")
    keyword: Optional[str] = Field(None, description="Search keyword")
    sort_by: str = Field("gmv_30d", description="Sort field")
    sort_order: str = Field("DESC", description="Sort order")
    page_size: int = Field(20, ge=1, le=50, description="Results per page")
    page_token: Optional[str] = Field(None, description="Pagination token")


class CreateCampaignRequest(BaseModel):
    """Request model for creating an outreach campaign."""
    campaign_name: str = Field(..., description="Campaign name")
    product_ids: List[str] = Field(..., min_length=1, description="Product IDs")
    commission_rate: float = Field(15.0, ge=1.0, le=80.0, description="Commission %")
    target_category: Optional[str] = Field(None, description="Category filter")
    min_gmv: float = Field(1000.0, description="Min creator GMV")
    min_followers: int = Field(1000, description="Min followers")
    max_followers: Optional[int] = Field(None, description="Max followers")
    daily_outreach_target: int = Field(50, ge=1, le=200, description="Daily target")
    invitation_message: Optional[str] = Field(
        None, max_length=500, description="Invitation message (500 char max)"
    )


class SendInvitationRequest(BaseModel):
    """Request model for sending invitations."""
    collaboration_id: str = Field(..., description="Collaboration ID")
    creator_ids: List[str] = Field(..., min_length=1, max_length=20)
    invitation_message: Optional[str] = Field(None, max_length=500)


class SendMessageRequest(BaseModel):
    """Request model for sending messages to creators."""
    creator_id: str = Field(..., description="Creator ID")
    message: str = Field(..., max_length=500, description="Message (500 char max)")


class GenerateScriptRequest(BaseModel):
    """Request model for generating affiliate video scripts."""
    product_name: str = Field(..., description="Product name")
    product_features: List[str] = Field(..., min_length=1, description="Key features")
    target_niche: str = Field("TCG collectors", description="Target niche")
    script_style: str = Field("review", description="review, unboxing, tutorial, comparison")


class ApproveSampleRequest(BaseModel):
    """Request model for approving sample requests."""
    request_id: str = Field(..., description="Sample request ID")
    shipping_note: Optional[str] = Field(None, description="Note for creator")


class GenerateDraftsRequest(BaseModel):
    """Request model for generating draft replies for pending conversations."""
    campaign_name: Optional[str] = Field(None, description="Filter by campaign")
    style_instructions: Optional[str] = Field(
        None, description="Custom tone/style instructions for drafts"
    )


class BatchSendRequest(BaseModel):
    """Request model for batch-sending approved draft messages."""
    draft_ids: List[str] = Field(..., min_length=1, description="IDs of drafts to send")


class UpdateDraftRequest(BaseModel):
    """Request model for editing a single draft before sending."""
    draft_id: str = Field(..., description="Draft ID to update")
    message: str = Field(..., max_length=500, description="Updated message text")


class StyleChatRequest(BaseModel):
    """Request model for chatting with the AI to refine message style."""
    instruction: str = Field(..., description="Style instruction or feedback")
    example_drafts: Optional[List[str]] = Field(
        None, description="Example draft IDs to reference"
    )


class ResearchVideosRequest(BaseModel):
    """Request model for researching competitor videos."""
    category: Optional[str] = Field(None, description="Product category")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags to search")
    min_views: int = Field(100000, description="Min view count")
    days: int = Field(7, ge=1, le=30, description="Lookback days")
    limit: int = Field(30, ge=1, le=100, description="Max results")


class AnalyzeVideosRequest(BaseModel):
    """Request model for manually analyzing video transcripts."""
    videos: List[Dict[str, str]] = Field(
        ..., description="List of {url, transcript} objects"
    )


class DataDrivenScriptRequest(BaseModel):
    """Request model for generating scripts from competitor research."""
    product_name: str = Field(..., description="Product name")
    product_features: List[str] = Field(..., min_length=1, description="Key features")
    target_niche: str = Field("TCG collectors", description="Target niche")
    script_style: str = Field("review", description="review, unboxing, tutorial, comparison")
    hashtags: Optional[List[str]] = Field(
        None, description="Hashtags to research first (auto-research)"
    )
    category: Optional[str] = Field(None, description="Category to research")


# ========================================================================
# CREATOR SEARCH & DISCOVERY
# ========================================================================

@router.post("/creators/search", summary="Search affiliate creators")
async def search_creators(request: CreatorSearchRequest):
    """
    Search for TikTok Shop affiliate creators with filters.

    Filters by GMV, follower count, category, and other criteria.
    Essential for building targeted outreach lists.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        from integrations.tiktok_shop.affiliate_client import (
            CreatorSortField,
            SortOrder,
        )

        result = client.search_creators(
            category=request.category,
            min_gmv_30d=request.min_gmv_30d,
            max_gmv_30d=request.max_gmv_30d,
            min_followers=request.min_followers,
            max_followers=request.max_followers,
            min_sales_30d=request.min_sales_30d,
            keyword=request.keyword,
            sort_by=CreatorSortField(request.sort_by),
            sort_order=SortOrder(request.sort_order),
            page_size=request.page_size,
            page_token=request.page_token,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Creator search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Creator search failed: {str(e)}")


@router.get("/creators/{creator_id}", summary="Get creator profile")
async def get_creator_profile(creator_id: str):
    """Get detailed profile for a specific affiliate creator."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        return client.get_creator_profile(creator_id)

    except Exception as e:
        logger.error(f"Get creator profile failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# CAMPAIGN MANAGEMENT
# ========================================================================

@router.post("/campaigns", summary="Create outreach campaign")
async def create_campaign(request: CreateCampaignRequest):
    """
    Create a new affiliate outreach campaign.

    Sets up a target collaboration and configures automated outreach parameters.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        campaign = agent.create_outreach_campaign(
            campaign_name=request.campaign_name,
            product_ids=request.product_ids,
            commission_rate=request.commission_rate,
            target_category=request.target_category,
            min_gmv=request.min_gmv,
            min_followers=request.min_followers,
            max_followers=request.max_followers,
            daily_outreach_target=request.daily_outreach_target,
            invitation_message=request.invitation_message,
        )

        return {"status": "created", "campaign": campaign}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Campaign creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_name}/execute", summary="Execute daily outreach")
async def execute_daily_outreach(campaign_name: str):
    """
    Execute one day's outreach for a campaign.

    Searches for creators, sends invitations, and logs results.
    Respects tier-based outreach limits.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        result = agent.execute_daily_outreach(campaign_name)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Daily outreach failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_name}/follow-up", summary="Send follow-ups")
async def execute_follow_ups(campaign_name: str):
    """
    Send follow-up messages to pending affiliates.

    Follows the 3x/week cadence: Day 3, Day 5, Day 7 after initial outreach.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        result = agent.execute_follow_ups(campaign_name)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Follow-up execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_name}/report", summary="Get campaign report")
async def get_campaign_report(campaign_name: str):
    """Get performance report for a campaign."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        return agent.get_campaign_report(campaign_name)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Campaign report failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# INVITATIONS & MESSAGES
# ========================================================================

@router.post("/invitations/send", summary="Send invitations to creators")
async def send_invitations(request: SendInvitationRequest):
    """Send target collaboration invitations to specific creators."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        result = client.send_invitation(
            collaboration_id=request.collaboration_id,
            creator_ids=request.creator_ids,
            invitation_message=request.invitation_message,
        )

        return result

    except Exception as e:
        logger.error(f"Send invitation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/send", summary="Send message to creator")
async def send_message(request: SendMessageRequest):
    """Send a follow-up message to a creator in an active collaboration."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        result = client.send_creator_message(
            creator_id=request.creator_id,
            message=request.message,
        )

        return result

    except Exception as e:
        logger.error(f"Send message failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# TIER STATUS & PERFORMANCE
# ========================================================================

@router.get("/tier-progress", summary="Get outreach tier progress")
async def get_tier_progress():
    """
    Get current progress toward the next outreach tier.

    Tracks progress toward Tier 3 unlock ($2K affiliate GMV/30d = 7K weekly actions).
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        return agent.get_tier_progress()

    except Exception as e:
        logger.error(f"Tier progress check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outreach-status", summary="Get outreach limits and status")
async def get_outreach_status():
    """Get current outreach tier, remaining actions, and limits."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        return client.get_outreach_status()

    except Exception as e:
        logger.error(f"Outreach status check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", summary="Get affiliate performance metrics")
async def get_affiliate_performance(
    group_by: str = Query("creator", description="Group by: creator, product, daily"),
    days: int = Query(30, ge=1, le=90, description="Lookback period in days"),
):
    """Get affiliate performance metrics grouped by creator, product, or day."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent
        import time

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)

        return client.get_affiliate_performance(
            start_time=start_time,
            end_time=end_time,
            group_by=group_by,
        )

    except Exception as e:
        logger.error(f"Performance fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/affiliate-orders", summary="Get affiliate orders")
async def get_affiliate_orders(
    days: int = Query(30, ge=1, le=90),
    creator_id: Optional[str] = Query(None),
    page_size: int = Query(20, ge=1, le=50),
    page_token: Optional[str] = Query(None),
):
    """Get orders attributed to affiliate creators."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent
        import time

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)

        return client.get_affiliate_orders(
            start_time=start_time,
            end_time=end_time,
            creator_id=creator_id,
            page_size=page_size,
            page_token=page_token,
        )

    except Exception as e:
        logger.error(f"Affiliate orders fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# SAMPLE MANAGEMENT
# ========================================================================

@router.get("/samples", summary="Get sample requests from creators")
async def get_sample_requests(
    status: Optional[str] = Query(None, description="PENDING, APPROVED, SHIPPED, RECEIVED"),
    page_size: int = Query(20, ge=1, le=50),
    page_token: Optional[str] = Query(None),
):
    """Get free sample requests from affiliate creators for fulfillment."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        return client.get_sample_requests(
            status_filter=status,
            page_size=page_size,
            page_token=page_token,
        )

    except Exception as e:
        logger.error(f"Sample requests fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/samples/approve", summary="Approve sample request")
async def approve_sample_request(request: ApproveSampleRequest):
    """Approve a free sample request from an affiliate creator."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        client = agent._get_affiliate_client()

        return client.approve_sample_request(
            request_id=request.request_id,
            shipping_note=request.shipping_note,
        )

    except Exception as e:
        logger.error(f"Sample approval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# SCRIPT GENERATION
# ========================================================================

@router.post("/scripts/generate", summary="Generate affiliate video script")
async def generate_affiliate_script(request: GenerateScriptRequest):
    """
    Generate a video script for affiliates to use.

    Providing scripts dramatically improves affiliate video quality.
    Based on MADA's finding: almost all top-performing videos used
    their scripts partially or fully.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        content, filepath = agent.generate_affiliate_script(
            product_name=request.product_name,
            product_features=request.product_features,
            target_niche=request.target_niche,
            script_style=request.script_style,
        )

        return {
            "script": content,
            "filepath": str(filepath),
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Script generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# DRAFT MESSAGES & BATCH SEND (Core Dashboard Workflow)
# ========================================================================

@router.post("/drafts/generate", summary="Generate draft replies for all pending conversations")
async def generate_drafts(request: GenerateDraftsRequest):
    """
    Generate AI draft replies for every creator with a pending message.

    This is the core daily workflow: pull up the dashboard, review 50 drafts,
    check the good ones, batch send. Each draft is personalized based on
    the creator's profile, their last message, and your style instructions.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        drafts = agent.generate_reply_drafts(
            campaign_name=request.campaign_name,
            style_instructions=request.style_instructions,
        )

        return {
            "drafts": drafts,
            "total": len(drafts),
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Draft generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drafts", summary="Get all current draft messages")
async def get_drafts(
    campaign_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="pending, approved, sent"),
):
    """Get all current draft messages for review."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        drafts = agent.get_drafts(
            campaign_name=campaign_name,
            status_filter=status,
        )

        return {"drafts": drafts, "total": len(drafts)}

    except Exception as e:
        logger.error(f"Get drafts failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/drafts/{draft_id}", summary="Update a draft message")
async def update_draft(draft_id: str, request: UpdateDraftRequest):
    """Edit a draft message before sending."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        updated = agent.update_draft(draft_id=draft_id, message=request.message)

        return {"status": "updated", "draft": updated}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Update draft failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drafts/batch-send", summary="Batch send approved drafts")
async def batch_send_drafts(request: BatchSendRequest):
    """
    Send all checked/approved draft messages in one batch.

    The daily workflow: review drafts, check the good ones, hit send.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        result = agent.batch_send_drafts(draft_ids=request.draft_ids)

        return result

    except Exception as e:
        logger.error(f"Batch send failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# STYLE CHAT AGENT (Refine Message Tone)
# ========================================================================

@router.post("/style-chat", summary="Chat with AI to refine message style")
async def style_chat(request: StyleChatRequest):
    """
    Chat with the AI agent to adjust the tone and style of draft messages.

    Example: "Sound more casual", "Add more urgency", "Reference their
    specific content niche". The agent updates the style config and can
    regenerate all pending drafts with the new style.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        result = agent.process_style_chat(
            instruction=request.instruction,
            example_draft_ids=request.example_drafts,
        )

        return result

    except Exception as e:
        logger.error(f"Style chat failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================
# VIDEO INTELLIGENCE & COMPETITOR RESEARCH
# ========================================================================

@router.post("/research/videos", summary="Research top-performing competitor videos")
async def research_competitor_videos(request: ResearchVideosRequest):
    """
    Discover and analyze top-performing TikTok Shop videos in your niche.

    Uses multiple data sources (TikTok Research API, Kalodata, FastMoss)
    to find viral videos, extract their transcripts, and analyze their
    hooks, selling techniques, and CTAs.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        result = agent.research_competitor_videos(
            category=request.category,
            hashtags=request.hashtags,
            min_views=request.min_views,
            days=request.days,
            limit=request.limit,
        )

        return result

    except Exception as e:
        logger.error(f"Competitor research failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/products", summary="Research top-selling products")
async def research_top_products(
    category: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=90),
    limit: int = Query(20, ge=1, le=50),
):
    """Discover top-selling products on TikTok Shop in a category."""
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        return agent.research_top_products(
            category=category, days=days, limit=limit
        )

    except Exception as e:
        logger.error(f"Product research failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/analyze", summary="Analyze video transcripts manually")
async def analyze_video_transcripts(request: AnalyzeVideosRequest):
    """
    Analyze manually provided video transcripts.

    When API sources aren't configured, paste in video URLs and their
    transcripts to get hook analysis, selling techniques, and patterns.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()
        return agent.analyze_videos_from_urls(video_data=request.videos)

    except Exception as e:
        logger.error(f"Video analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/trending-hashtags", summary="Get trending hashtags")
async def get_trending_hashtags(
    seed_hashtags: Optional[List[str]] = Query(None),
    region: str = Query("US"),
    limit: int = Query(20, ge=1, le=50),
):
    """Get trending hashtags from TikTok Creative Center (free, always available)."""
    try:
        from integrations.tiktok_shop.video_intelligence import VideoIntelligenceClient

        client = VideoIntelligenceClient()
        return client.discover_trending_hashtags(
            seed_hashtags=seed_hashtags,
            region=region,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Hashtag research failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/scripts/generate-from-research",
    summary="Generate script from competitor research"
)
async def generate_data_driven_script(request: DataDrivenScriptRequest):
    """
    Generate a video script informed by competitor video analysis.

    Optionally auto-researches competitor videos first, then generates
    a script that uses the proven hooks, techniques, and CTAs from
    videos that are actually going viral in your niche.
    """
    try:
        from agents.tiktok_affiliate_agent import TikTokAffiliateAgent

        agent = TikTokAffiliateAgent()

        # Auto-research if hashtags or category provided
        research_results = None
        if request.hashtags or request.category:
            research_results = agent.research_competitor_videos(
                category=request.category,
                hashtags=request.hashtags,
                min_views=50000,
                days=7,
                limit=20,
            )

        content, filepath = agent.generate_data_driven_script(
            product_name=request.product_name,
            product_features=request.product_features,
            research_results=research_results,
            target_niche=request.target_niche,
            script_style=request.script_style,
        )

        return {
            "script": content,
            "filepath": str(filepath),
            "research_summary": {
                "videos_analyzed": (
                    research_results.get("analysis", {}).get("videos_analyzed", 0)
                    if research_results else 0
                ),
                "sources_used": (
                    research_results.get("discovery", {}).get("sources_used", [])
                    if research_results else []
                ),
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Data-driven script generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
