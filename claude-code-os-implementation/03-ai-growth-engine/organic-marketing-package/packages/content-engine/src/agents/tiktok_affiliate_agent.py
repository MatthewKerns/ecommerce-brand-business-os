"""
TikTok Shop Affiliate Outreach Agent

Manages the complete affiliate outreach lifecycle:
- Creator discovery and scoring
- Campaign creation and invitation sending
- Follow-up cadence management
- Script generation for affiliates
- Performance tracking and tier progression

This agent replicates the $2K/mo TikTok agency playbook (MADA model)
using automated affiliate API outreach at scale.
"""
import json
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from config.config import (
    TIKTOK_OUTPUT_DIR,
    TIKTOK_SHOP_APP_KEY,
    TIKTOK_SHOP_APP_SECRET,
    TIKTOK_SHOP_ACCESS_TOKEN,
    BRAND_NAME,
    BRAND_TAGLINE,
)

logger = logging.getLogger(__name__)


class TikTokAffiliateAgent(BaseAgent):
    """
    Agent for automating TikTok Shop affiliate outreach at scale.

    Implements the proven agency playbook:
    1. Search creators by GMV, followers, category
    2. Send personalized invitations with product scripts
    3. Follow up 3x/week with pending affiliates
    4. Track performance and optimize toward Tier 3 unlock

    Outreach Tier System:
    - Tier 1: 1,000 one-time actions (new shop)
    - Tier 2: 2,000/week to micro-influencers (<20K followers)
    - Tier 3: 7,000/week to ANY affiliate (unlocked at $2K affiliate GMV/30d)
    """

    # Default filters for MADA-style outreach
    DEFAULT_SEARCH_FILTERS = {
        "min_gmv_30d": 1000.0,  # $1K+ monthly GMV (MADA standard)
        "min_followers": 1000,
        "min_video_count": 10,
    }

    # Follow-up cadence (days after initial outreach)
    FOLLOW_UP_SCHEDULE = [3, 5, 7]  # 3x/week like MADA

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        super().__init__(agent_name="tiktok_affiliate_agent")

        self.app_key = app_key or TIKTOK_SHOP_APP_KEY
        self.app_secret = app_secret or TIKTOK_SHOP_APP_SECRET
        self.access_token = access_token or TIKTOK_SHOP_ACCESS_TOKEN

        self._affiliate_client = None

        # Output directory for campaign data
        self.output_dir = TIKTOK_OUTPUT_DIR / "affiliate-outreach"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_affiliate_client(self):
        """Get or create the affiliate API client."""
        if self._affiliate_client is None:
            if not self.app_key or not self.app_secret:
                raise ValueError(
                    "TikTok Shop credentials not configured. "
                    "Set TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_SECRET in .env"
                )

            from integrations.tiktok_shop.client import TikTokShopClient
            from integrations.tiktok_shop.affiliate_client import (
                TikTokShopAffiliateClient,
            )

            base_client = TikTokShopClient(
                app_key=self.app_key,
                app_secret=self.app_secret,
                access_token=self.access_token,
            )
            self._affiliate_client = TikTokShopAffiliateClient(base_client)

        return self._affiliate_client

    # ========================================================================
    # CAMPAIGN MANAGEMENT
    # ========================================================================

    def create_outreach_campaign(
        self,
        campaign_name: str,
        product_ids: List[str],
        commission_rate: float = 15.0,
        target_category: Optional[str] = None,
        min_gmv: float = 1000.0,
        min_followers: int = 1000,
        max_followers: Optional[int] = None,
        daily_outreach_target: int = 50,
        invitation_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new affiliate outreach campaign.

        This sets up a target collaboration and configures automated outreach
        parameters. The campaign can then be executed daily.

        Args:
            campaign_name: Name for the campaign
            product_ids: Product IDs to promote
            commission_rate: Commission percentage (default 15%)
            target_category: TikTok Shop category filter
            min_gmv: Minimum creator GMV in last 30 days
            min_followers: Minimum follower count
            max_followers: Maximum follower count (Tier 2 = 20K limit)
            daily_outreach_target: How many creators to reach per day
            invitation_message: Custom invitation text (max 500 chars)

        Returns:
            Campaign configuration dictionary

        Example:
            >>> agent = TikTokAffiliateAgent()
            >>> campaign = agent.create_outreach_campaign(
            ...     campaign_name='March TCG Binder Push',
            ...     product_ids=['prod_binder_123', 'prod_box_456'],
            ...     commission_rate=15.0,
            ...     target_category='toys_and_games',
            ...     min_gmv=1000.0,
            ...     daily_outreach_target=50,
            ... )
        """
        client = self._get_affiliate_client()

        # Create the target collaboration
        collab = client.create_target_collaboration(
            product_ids=product_ids,
            commission_rate=commission_rate,
            collaboration_name=campaign_name,
        )

        collaboration_id = collab.get("data", {}).get("collaboration_id")

        # Build campaign config
        campaign = {
            "campaign_name": campaign_name,
            "collaboration_id": collaboration_id,
            "product_ids": product_ids,
            "commission_rate": commission_rate,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "search_filters": {
                "category": target_category,
                "min_gmv_30d": min_gmv,
                "min_followers": min_followers,
                "max_followers": max_followers,
            },
            "daily_outreach_target": daily_outreach_target,
            "invitation_message": invitation_message or self._default_invitation(),
            "stats": {
                "total_invitations_sent": 0,
                "total_accepted": 0,
                "total_rejected": 0,
                "total_pending": 0,
                "videos_received": 0,
                "gmv_generated": 0.0,
            },
            "outreach_log": [],
        }

        # Save campaign config
        filepath = self.output_dir / f"campaign_{campaign_name.replace(' ', '_').lower()}.json"
        with open(filepath, "w") as f:
            json.dump(campaign, f, indent=2)

        logger.info(f"Created campaign '{campaign_name}' (collab: {collaboration_id})")
        return campaign

    def execute_daily_outreach(
        self,
        campaign_name: str,
    ) -> Dict[str, Any]:
        """
        Execute one day's worth of outreach for a campaign.

        This is the core automation loop:
        1. Load campaign config
        2. Check outreach tier and remaining actions
        3. Search for new creators matching filters
        4. Send batch invitations
        5. Log results

        Args:
            campaign_name: Name of the campaign to execute

        Returns:
            Dictionary with outreach results for the day

        Example:
            >>> result = agent.execute_daily_outreach('March TCG Binder Push')
            >>> print(f"Sent {result['invitations_sent']} invitations today")
        """
        client = self._get_affiliate_client()

        # Load campaign
        filepath = self.output_dir / f"campaign_{campaign_name.replace(' ', '_').lower()}.json"
        if not filepath.exists():
            raise ValueError(f"Campaign '{campaign_name}' not found")

        with open(filepath) as f:
            campaign = json.load(f)

        if campaign["status"] != "active":
            logger.info(f"Campaign '{campaign_name}' is {campaign['status']}, skipping")
            return {"status": "skipped", "reason": campaign["status"]}

        # Check outreach status
        outreach_status = client.get_outreach_status()
        remaining = outreach_status.get("data", {}).get("actions_remaining", 0)
        current_tier = outreach_status.get("data", {}).get("current_tier", 1)

        if remaining <= 0:
            logger.warning("No outreach actions remaining this week")
            return {"status": "limit_reached", "remaining": 0}

        # Calculate how many to send today
        target = min(campaign["daily_outreach_target"], remaining)
        logger.info(
            f"Executing daily outreach for '{campaign_name}': "
            f"target={target}, remaining={remaining}, tier={current_tier}"
        )

        # Execute batch outreach
        result = client.batch_search_and_invite(
            collaboration_id=campaign["collaboration_id"],
            search_filters=campaign["search_filters"],
            invitation_message=campaign["invitation_message"],
            max_invitations=target,
        )

        # Update campaign stats
        campaign["stats"]["total_invitations_sent"] += result["invitations_sent"]

        # Log this outreach run
        campaign["outreach_log"].append({
            "date": datetime.now().isoformat(),
            "invitations_sent": result["invitations_sent"],
            "invitations_failed": result["invitations_failed"],
            "tier": current_tier,
            "remaining_after": remaining - result["invitations_sent"],
        })

        # Save updated campaign
        with open(filepath, "w") as f:
            json.dump(campaign, f, indent=2)

        return {
            "status": "completed",
            "campaign": campaign_name,
            "invitations_sent": result["invitations_sent"],
            "invitations_failed": result["invitations_failed"],
            "creators_invited": result.get("creators_invited", []),
            "tier": current_tier,
            "remaining_actions": remaining - result["invitations_sent"],
        }

    # ========================================================================
    # FOLLOW-UP MANAGEMENT
    # ========================================================================

    def execute_follow_ups(
        self,
        campaign_name: str,
    ) -> Dict[str, Any]:
        """
        Send follow-up messages to pending affiliates.

        MADA follows up 3x/week. This checks for creators who received
        invitations but haven't responded, and sends follow-up messages.

        Args:
            campaign_name: Campaign name

        Returns:
            Follow-up results
        """
        client = self._get_affiliate_client()

        filepath = self.output_dir / f"campaign_{campaign_name.replace(' ', '_').lower()}.json"
        if not filepath.exists():
            raise ValueError(f"Campaign '{campaign_name}' not found")

        with open(filepath) as f:
            campaign = json.load(f)

        # Get pending invitations
        pending = client.get_invitation_status(
            collaboration_id=campaign["collaboration_id"],
            status_filter="PENDING",
            page_size=50,
        )

        pending_invitations = pending.get("data", {}).get("invitations", [])
        follow_ups_sent = 0

        for invitation in pending_invitations:
            creator_id = invitation.get("creator_id")
            invited_at = invitation.get("invited_at")

            if not invited_at:
                continue

            # Calculate days since invitation
            invite_time = datetime.fromisoformat(invited_at)
            days_since = (datetime.now() - invite_time).days

            # Check if follow-up is due
            for follow_up_day in self.FOLLOW_UP_SCHEDULE:
                if days_since == follow_up_day:
                    follow_up_num = self.FOLLOW_UP_SCHEDULE.index(follow_up_day) + 1
                    message = self._follow_up_message(follow_up_num)

                    try:
                        client.send_creator_message(
                            creator_id=creator_id,
                            message=message,
                        )
                        follow_ups_sent += 1
                        logger.info(
                            f"Follow-up #{follow_up_num} sent to {creator_id} "
                            f"(day {days_since})"
                        )
                    except Exception as e:
                        logger.warning(f"Follow-up to {creator_id} failed: {e}")

        return {
            "campaign": campaign_name,
            "pending_count": len(pending_invitations),
            "follow_ups_sent": follow_ups_sent,
        }

    # ========================================================================
    # SCRIPT GENERATION
    # ========================================================================

    def generate_affiliate_script(
        self,
        product_name: str,
        product_features: List[str],
        target_niche: str = "TCG collectors",
        script_style: str = "review",
    ) -> tuple[str, Path]:
        """
        Generate a video script for affiliates to use.

        MADA's key insight: providing scripts to affiliates dramatically
        improves video quality and conversion. Almost all top-performing
        videos used their scripts partially or fully.

        Args:
            product_name: Product name
            product_features: Key features to highlight
            target_niche: Target audience niche
            script_style: Script type ('review', 'unboxing', 'tutorial', 'comparison')

        Returns:
            Tuple of (script_content, file_path)
        """
        features_text = "\n".join(f"- {f}" for f in product_features)

        prompt = f"""Create a TikTok affiliate video script for a creator promoting this product:

PRODUCT: {product_name}
BRAND: {BRAND_NAME}
STYLE: {script_style}
TARGET AUDIENCE: {target_niche}

KEY FEATURES:
{features_text}

REQUIREMENTS (based on top-performing affiliate video analysis):
1. Hook in first 3 seconds (bold statement, question, or surprising claim)
2. Show the product within first 5 seconds
3. Demonstrate 2-3 key features with visuals
4. Share personal reaction/opinion (authenticity converts)
5. End with strong CTA: "Link in bio" / "Shop now" / limited-time offer
6. Keep total length 30-60 seconds
7. Include text overlay suggestions for key moments
8. Suggest trending sound/music style

FORMAT:
[HOOK - 0-3s]
Visual: [what to show]
Script: [what to say]
Text overlay: [on-screen text]

[FEATURE SHOWCASE - 4-25s]
Visual: [what to show]
Script: [what to say]
Text overlay: [on-screen text]

[PERSONAL TAKE - 26-40s]
Visual: [what to show]
Script: [what to say]
Text overlay: [on-screen text]

[CTA - 41-50s]
Visual: [what to show]
Script: [what to say]
Text overlay: [on-screen text]

[CAPTION & HASHTAGS]
Caption:
Hashtags:

Write the script now. Make it feel authentic, not scripted."""

        system_context = f"""You are a TikTok affiliate marketing expert.
Your scripts have generated millions of views and hundreds of thousands in sales.

Brand: {BRAND_NAME} - "{BRAND_TAGLINE}"
Strategy: Provide affiliates with proven scripts that feel authentic.
Goal: High view count + high conversion rate.

Key principle from agency experience:
"Almost all top-performing videos were made using our scripts, partially or fully."
The script should feel natural but hit all conversion points."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=self.output_dir / "scripts",
            system_context=system_context,
            metadata={
                "type": "affiliate_script",
                "product": product_name,
                "style": script_style,
                "niche": target_niche,
            },
        )

    # ========================================================================
    # PERFORMANCE TRACKING
    # ========================================================================

    def get_tier_progress(self) -> Dict[str, Any]:
        """
        Get current progress toward the next outreach tier.

        Critical for tracking the path to Tier 3 ($2K affiliate GMV/30d)
        which unlocks 7,000 weekly outreach actions to any affiliate.

        Returns:
            Dictionary with tier progress details
        """
        client = self._get_affiliate_client()

        outreach_status = client.get_outreach_status()
        gmv_summary = client.get_affiliate_gmv_summary(days=30)

        current_tier = outreach_status.get("data", {}).get("current_tier", 1)
        affiliate_gmv = gmv_summary.get("data", {}).get("total_gmv", 0.0)

        # Determine next tier requirements
        if current_tier == 1:
            next_tier = 2
            requirement = "Make 1 affiliate sale ($1 minimum)"
            progress_pct = min(100, (affiliate_gmv / 1.0) * 100) if affiliate_gmv > 0 else 0
        elif current_tier == 2:
            next_tier = 3
            requirement = "$2,000 affiliate GMV in last 30 days"
            progress_pct = min(100, (affiliate_gmv / 2000.0) * 100)
        else:
            next_tier = None
            requirement = "Maximum tier reached"
            progress_pct = 100

        return {
            "current_tier": current_tier,
            "next_tier": next_tier,
            "requirement": requirement,
            "affiliate_gmv_30d": affiliate_gmv,
            "progress_percent": round(progress_pct, 1),
            "weekly_limit": outreach_status.get("data", {}).get("weekly_limit", 0),
            "actions_remaining": outreach_status.get("data", {}).get("actions_remaining", 0),
            "max_follower_limit": outreach_status.get("data", {}).get("max_follower_limit"),
        }

    def get_campaign_report(
        self,
        campaign_name: str,
    ) -> Dict[str, Any]:
        """
        Generate a performance report for a campaign.

        Args:
            campaign_name: Campaign name

        Returns:
            Campaign performance report
        """
        client = self._get_affiliate_client()

        filepath = self.output_dir / f"campaign_{campaign_name.replace(' ', '_').lower()}.json"
        if not filepath.exists():
            raise ValueError(f"Campaign '{campaign_name}' not found")

        with open(filepath) as f:
            campaign = json.load(f)

        # Get latest invitation status
        accepted = client.get_invitation_status(
            collaboration_id=campaign["collaboration_id"],
            status_filter="ACCEPTED",
        )
        rejected = client.get_invitation_status(
            collaboration_id=campaign["collaboration_id"],
            status_filter="REJECTED",
        )
        pending = client.get_invitation_status(
            collaboration_id=campaign["collaboration_id"],
            status_filter="PENDING",
        )

        # Get affiliate performance for this collaboration
        performance = client.get_affiliate_performance(
            group_by="creator",
        )

        total_sent = campaign["stats"]["total_invitations_sent"]
        accepted_count = len(accepted.get("data", {}).get("invitations", []))
        rejected_count = len(rejected.get("data", {}).get("invitations", []))
        pending_count = len(pending.get("data", {}).get("invitations", []))

        return {
            "campaign_name": campaign_name,
            "created_at": campaign["created_at"],
            "status": campaign["status"],
            "total_invitations_sent": total_sent,
            "accepted": accepted_count,
            "rejected": rejected_count,
            "pending": pending_count,
            "acceptance_rate": (
                round(accepted_count / total_sent * 100, 1) if total_sent > 0 else 0
            ),
            "performance": performance.get("data", {}),
            "outreach_history": campaign["outreach_log"][-10:],  # Last 10 runs
        }

    # ========================================================================
    # MESSAGE TEMPLATES
    # ========================================================================

    def _default_invitation(self) -> str:
        """Default affiliate invitation message (500 char limit)."""
        return (
            f"Your content shows you genuinely care about the TCG community - "
            f"that's our vibe too. I'm from {BRAND_NAME}, where we make premium "
            f"scratch-resistant trading card binders with lifetime warranties. "
            f"Built for players and collectors who refuse to show up unprepared. "
            f"Your audience deserves gear that matches their passion. "
            f"Excited to collaborate and bring battle-ready equipment to your "
            f"community. Let's make this happen - your followers will thank you "
            f"for introducing them to quality that lasts!"
        )

    def _follow_up_message(self, follow_up_number: int) -> str:
        """Generate follow-up message based on the follow-up number."""
        messages = {
            1: (
                f"Hey! Just following up on our collaboration invite. "
                f"We'd love to send you a free {BRAND_NAME} binder to try out. "
                f"No obligations - just quality gear for your collection. "
                f"Let us know if you're interested!"
            ),
            2: (
                f"Quick check-in! Our invite is still open if you're interested. "
                f"We've been getting great feedback from other creators. "
                f"Happy to answer any questions about {BRAND_NAME} products."
            ),
            3: (
                f"Last follow-up! Just wanted to make sure you saw our invite. "
                f"No pressure at all - the door is always open. "
                f"Thanks for the amazing content you create!"
            ),
        }
        return messages.get(follow_up_number, messages[3])
