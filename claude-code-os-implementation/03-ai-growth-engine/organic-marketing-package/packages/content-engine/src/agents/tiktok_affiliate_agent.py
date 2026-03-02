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

    # ========================================================================
    # DRAFT MESSAGE MANAGEMENT (Core Dashboard Workflow)
    # ========================================================================

    def _load_drafts(self) -> List[Dict[str, Any]]:
        """Load all draft messages from disk."""
        drafts_file = self.output_dir / "drafts.json"
        if drafts_file.exists():
            with open(drafts_file) as f:
                return json.load(f)
        return []

    def _save_drafts(self, drafts: List[Dict[str, Any]]) -> None:
        """Save draft messages to disk."""
        drafts_file = self.output_dir / "drafts.json"
        with open(drafts_file, "w") as f:
            json.dump(drafts, f, indent=2)

    def _load_style_config(self) -> Dict[str, Any]:
        """Load the current message style configuration."""
        style_file = self.output_dir / "style_config.json"
        if style_file.exists():
            with open(style_file) as f:
                return json.load(f)
        return {
            "tone": "friendly, authentic, enthusiastic but not salesy",
            "length": "2-4 sentences, under 500 chars",
            "personality": "fellow creator/collector who genuinely uses the product",
            "avoid": "corporate speak, pushy sales language, generic templates",
            "include": "reference their specific content, show genuine interest",
            "custom_instructions": "",
        }

    def _save_style_config(self, config: Dict[str, Any]) -> None:
        """Save message style configuration."""
        style_file = self.output_dir / "style_config.json"
        with open(style_file, "w") as f:
            json.dump(config, f, indent=2)

    def generate_reply_drafts(
        self,
        campaign_name: Optional[str] = None,
        style_instructions: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate AI draft replies for every creator needing a response.

        The daily workflow: this generates one draft per pending conversation
        so you can review 50+ at once, check the good ones, and batch send.

        Args:
            campaign_name: Optional filter by campaign
            style_instructions: Optional override for message style

        Returns:
            List of draft objects with creator info and draft message
        """
        client = self._get_affiliate_client()
        style = self._load_style_config()

        if style_instructions:
            style["custom_instructions"] = style_instructions

        # Get all pending invitations and active conversations that need replies
        drafts = []
        campaigns = self._list_campaigns(campaign_name)

        for campaign in campaigns:
            collab_id = campaign.get("collaboration_id")
            if not collab_id:
                continue

            # Get pending invitations (creators we invited but haven't responded)
            try:
                pending = client.get_invitation_status(
                    collaboration_id=collab_id,
                    status_filter="PENDING",
                    page_size=50,
                )
                pending_list = pending.get("data", {}).get("invitations", [])
            except Exception:
                pending_list = []

            # Get accepted creators (active conversations)
            try:
                accepted = client.get_invitation_status(
                    collaboration_id=collab_id,
                    status_filter="ACCEPTED",
                    page_size=50,
                )
                accepted_list = accepted.get("data", {}).get("invitations", [])
            except Exception:
                accepted_list = []

            # Generate drafts for pending (follow-up messages)
            for inv in pending_list:
                creator_id = inv.get("creator_id", "")
                nickname = inv.get("creator_nickname", "Creator")
                days_pending = inv.get("days_since_invitation", 0)

                draft_msg = self._generate_single_draft(
                    creator_nickname=nickname,
                    context="follow_up",
                    days_pending=days_pending,
                    style=style,
                    creator_details=inv,
                )

                drafts.append({
                    "draft_id": f"draft_{creator_id}_{int(time.time())}",
                    "creator_id": creator_id,
                    "creator_nickname": nickname,
                    "creator_followers": inv.get("creator_followers"),
                    "creator_gmv_30d": inv.get("creator_gmv_30d"),
                    "campaign_name": campaign.get("campaign_name", ""),
                    "collaboration_id": collab_id,
                    "context": "follow_up",
                    "days_pending": days_pending,
                    "draft_message": draft_msg,
                    "status": "pending",
                    "generated_at": datetime.now().isoformat(),
                })

            # Generate drafts for accepted (thank you / next steps)
            for inv in accepted_list:
                creator_id = inv.get("creator_id", "")
                nickname = inv.get("creator_nickname", "Creator")

                draft_msg = self._generate_single_draft(
                    creator_nickname=nickname,
                    context="accepted",
                    style=style,
                    creator_details=inv,
                )

                drafts.append({
                    "draft_id": f"draft_{creator_id}_{int(time.time())}",
                    "creator_id": creator_id,
                    "creator_nickname": nickname,
                    "creator_followers": inv.get("creator_followers"),
                    "creator_gmv_30d": inv.get("creator_gmv_30d"),
                    "campaign_name": campaign.get("campaign_name", ""),
                    "collaboration_id": collab_id,
                    "context": "accepted",
                    "draft_message": draft_msg,
                    "status": "pending",
                    "generated_at": datetime.now().isoformat(),
                })

        self._save_drafts(drafts)
        return drafts

    def _generate_single_draft(
        self,
        creator_nickname: str,
        context: str,
        style: Dict[str, Any],
        creator_details: Optional[Dict] = None,
        days_pending: int = 0,
    ) -> str:
        """Generate a single draft message using the style config."""
        style_desc = (
            f"Tone: {style['tone']}\n"
            f"Length: {style['length']}\n"
            f"Personality: {style['personality']}\n"
            f"Avoid: {style['avoid']}\n"
            f"Include: {style['include']}"
        )
        if style.get("custom_instructions"):
            style_desc += f"\nCustom: {style['custom_instructions']}"

        followers = creator_details.get("creator_followers", "unknown") if creator_details else "unknown"
        gmv = creator_details.get("creator_gmv_30d", "unknown") if creator_details else "unknown"

        if context == "follow_up":
            prompt = (
                f"Write a short follow-up message to @{creator_nickname} "
                f"({followers} followers, ${gmv} GMV/30d). "
                f"They were invited {days_pending} days ago and haven't responded. "
                f"This is for {BRAND_NAME} trading card storage products.\n\n"
                f"STYLE:\n{style_desc}\n\n"
                f"Keep it under 500 characters. One message, no subject line."
            )
        elif context == "accepted":
            prompt = (
                f"Write a welcome/thank-you message to @{creator_nickname} "
                f"({followers} followers) who just accepted our affiliate invite. "
                f"Tell them we're sending a free sample and will include a script "
                f"with the package. For {BRAND_NAME} trading card binders.\n\n"
                f"STYLE:\n{style_desc}\n\n"
                f"Keep it under 500 characters. One message, no subject line."
            )
        else:
            prompt = (
                f"Write a message to @{creator_nickname} for {BRAND_NAME}.\n\n"
                f"STYLE:\n{style_desc}\n\n"
                f"Keep it under 500 characters."
            )

        try:
            content, _ = self.generate_and_save(
                prompt=prompt,
                output_dir=self.output_dir / "draft_cache",
                system_context=f"You write TikTok affiliate messages for {BRAND_NAME}. "
                f"Be authentic, not corporate. Max 500 chars.",
            )
            return content.strip()
        except Exception as e:
            logger.warning(f"Draft generation failed for {creator_nickname}: {e}")
            # Fallback to template
            if context == "follow_up":
                return self._follow_up_message(min(days_pending // 2, 3))
            return f"Thanks for joining us @{creator_nickname}! We're sending your free sample now."

    def get_drafts(
        self,
        campaign_name: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all current drafts, optionally filtered."""
        drafts = self._load_drafts()

        if campaign_name:
            drafts = [d for d in drafts if d.get("campaign_name") == campaign_name]
        if status_filter:
            drafts = [d for d in drafts if d.get("status") == status_filter]

        return drafts

    def update_draft(self, draft_id: str, message: str) -> Dict[str, Any]:
        """Update a single draft message."""
        drafts = self._load_drafts()

        for draft in drafts:
            if draft["draft_id"] == draft_id:
                draft["draft_message"] = message
                draft["manually_edited"] = True
                self._save_drafts(drafts)
                return draft

        raise ValueError(f"Draft '{draft_id}' not found")

    def batch_send_drafts(self, draft_ids: List[str]) -> Dict[str, Any]:
        """
        Send all approved draft messages in one batch.

        Args:
            draft_ids: List of draft IDs to send

        Returns:
            Batch send results
        """
        client = self._get_affiliate_client()
        drafts = self._load_drafts()

        sent = 0
        failed = 0
        errors = []

        for draft in drafts:
            if draft["draft_id"] not in draft_ids:
                continue
            if draft["status"] == "sent":
                continue

            try:
                client.send_creator_message(
                    creator_id=draft["creator_id"],
                    message=draft["draft_message"],
                )
                draft["status"] = "sent"
                draft["sent_at"] = datetime.now().isoformat()
                sent += 1
            except Exception as e:
                draft["status"] = "failed"
                failed += 1
                errors.append({
                    "draft_id": draft["draft_id"],
                    "creator": draft["creator_nickname"],
                    "error": str(e),
                })

        self._save_drafts(drafts)

        return {
            "sent": sent,
            "failed": failed,
            "errors": errors,
            "total_requested": len(draft_ids),
        }

    def process_style_chat(
        self,
        instruction: str,
        example_draft_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Process a style chat message to refine draft message tone.

        The user says something like "sound more casual" or "reference their
        niche more" and this updates the style config and optionally regenerates
        drafts.

        Args:
            instruction: User's style feedback
            example_draft_ids: Optional draft IDs to reference as examples

        Returns:
            Updated style config and regenerated sample drafts
        """
        style = self._load_style_config()

        # Get example drafts for context
        examples = ""
        if example_draft_ids:
            drafts = self._load_drafts()
            for d in drafts:
                if d["draft_id"] in example_draft_ids:
                    examples += f"\n- To @{d['creator_nickname']}: \"{d['draft_message']}\""

        prompt = f"""You are managing the message style for TikTok affiliate outreach.

CURRENT STYLE CONFIG:
- Tone: {style['tone']}
- Length: {style['length']}
- Personality: {style['personality']}
- Avoid: {style['avoid']}
- Include: {style['include']}
- Custom: {style.get('custom_instructions', 'none')}

USER FEEDBACK: "{instruction}"
{f'EXAMPLE DRAFTS THEY ARE REFERRING TO:{examples}' if examples else ''}

Based on the user's feedback, output the UPDATED style config as JSON with these exact keys:
tone, length, personality, avoid, include, custom_instructions

Only change what the user asked to change. Keep everything else the same.
Output ONLY the JSON object, no markdown or explanation."""

        try:
            result, _ = self.generate_and_save(
                prompt=prompt,
                output_dir=self.output_dir / "style_cache",
                system_context="You update message style configurations. Output only valid JSON.",
            )

            # Parse the updated config
            import re
            json_match = re.search(r'\{[^{}]*\}', result, re.DOTALL)
            if json_match:
                updated_style = json.loads(json_match.group())
                # Merge with existing to preserve any keys not in response
                style.update(updated_style)
        except Exception as e:
            logger.warning(f"Style chat AI parsing failed: {e}")
            # Fallback: just append the instruction
            style["custom_instructions"] = (
                f"{style.get('custom_instructions', '')} | {instruction}".strip(" | ")
            )

        self._save_style_config(style)

        return {
            "updated_style": style,
            "message": f"Style updated based on: '{instruction}'",
            "tip": "Use POST /drafts/generate to regenerate all drafts with the new style.",
        }

    def _list_campaigns(self, campaign_name: Optional[str] = None) -> List[Dict]:
        """List all campaigns or a specific one."""
        campaigns = []
        for f in self.output_dir.glob("campaign_*.json"):
            with open(f) as fh:
                campaign = json.load(fh)
                if campaign_name and campaign.get("campaign_name") != campaign_name:
                    continue
                campaigns.append(campaign)
        return campaigns

    # ========================================================================
    # VIDEO INTELLIGENCE & DATA-DRIVEN SCRIPTS
    # ========================================================================

    def _get_video_intelligence(self):
        """Get or create the video intelligence client."""
        from integrations.tiktok_shop.video_intelligence import VideoIntelligenceClient
        from config.config import (
            TIKTOK_RESEARCH_API_TOKEN,
            KALODATA_API_KEY,
            FASTMOSS_API_KEY,
        )

        return VideoIntelligenceClient(
            tiktok_research_token=TIKTOK_RESEARCH_API_TOKEN or None,
            kalodata_api_key=KALODATA_API_KEY or None,
            fastmoss_api_key=FASTMOSS_API_KEY or None,
        )

    def research_competitor_videos(
        self,
        category: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        min_views: int = 100000,
        days: int = 7,
        limit: int = 30,
    ) -> Dict[str, Any]:
        """
        Research top-performing competitor videos in your niche.

        Discovers trending videos, analyzes their hooks, structures, and
        selling techniques, and returns actionable patterns.

        Args:
            category: Product category
            hashtags: Relevant hashtags to search
            min_views: Minimum view count
            days: Lookback period
            limit: Max videos to analyze

        Returns:
            Research results with videos and pattern analysis
        """
        intel = self._get_video_intelligence()

        # Discover trending videos
        discovery = intel.discover_trending_videos(
            category=category,
            hashtags=hashtags,
            min_views=min_views,
            days=days,
            limit=limit,
        )

        # Analyze videos that have transcripts
        videos_with_transcripts = [
            v for v in discovery["videos"] if v.get("transcript")
        ]

        analysis = None
        if videos_with_transcripts:
            analysis = intel.batch_analyze_videos(videos_with_transcripts)

        # Save research results
        results = {
            "discovery": discovery,
            "analysis": analysis,
            "researched_at": datetime.now().isoformat(),
        }

        filepath = self.output_dir / "research" / f"competitor_research_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        return results

    def research_top_products(
        self,
        category: Optional[str] = None,
        days: int = 30,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Research top-selling products in a category on TikTok Shop.

        Args:
            category: Product category
            days: Lookback period
            limit: Max products

        Returns:
            Top products with sales metrics
        """
        intel = self._get_video_intelligence()
        return intel.discover_top_products(
            category=category, days=days, limit=limit
        )

    def analyze_videos_from_urls(
        self,
        video_data: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Analyze manually provided video data (URLs + transcripts).

        When API sources aren't available, you can manually input
        video URLs and their transcripts for analysis.

        Args:
            video_data: List of dicts with 'url' and 'transcript' keys

        Returns:
            Analysis results with patterns and recommendations
        """
        intel = self._get_video_intelligence()
        return intel.batch_analyze_videos(video_data)

    def generate_data_driven_script(
        self,
        product_name: str,
        product_features: List[str],
        research_results: Optional[Dict[str, Any]] = None,
        target_niche: str = "TCG collectors",
        script_style: str = "review",
    ) -> tuple[str, Path]:
        """
        Generate a video script informed by competitor video analysis.

        Takes research results from research_competitor_videos() and uses
        the discovered patterns (top hooks, selling techniques, CTAs) to
        generate a script that follows what's actually working.

        Args:
            product_name: Product to promote
            product_features: Key features
            research_results: Output from research_competitor_videos()
            target_niche: Audience niche
            script_style: Video style

        Returns:
            Tuple of (script_content, file_path)
        """
        features_text = "\n".join(f"- {f}" for f in product_features)

        # Extract intelligence from research
        intel_context = ""
        if research_results and research_results.get("analysis"):
            analysis = research_results["analysis"]
            patterns = analysis.get("common_patterns", {})

            top_techniques = patterns.get("top_techniques", [])
            hook_types = patterns.get("hook_types", [])

            if top_techniques:
                intel_context += "\n\nTOP SELLING TECHNIQUES FROM VIRAL VIDEOS:\n"
                for t in top_techniques[:5]:
                    intel_context += f"- {t['technique']} (used in {t['frequency']} videos)\n"

            if hook_types:
                intel_context += "\nMOST EFFECTIVE HOOK TYPES:\n"
                for h in hook_types[:3]:
                    intel_context += f"- {h['type']} hooks (used {h['count']} times)\n"

            # Add example hooks from top videos
            top_videos = research_results.get("discovery", {}).get("videos", [])[:3]
            if top_videos:
                intel_context += "\nEXAMPLE HOOKS FROM TOP-PERFORMING VIDEOS:\n"
                for v in top_videos:
                    if v.get("transcript"):
                        first_sentence = v["transcript"].split(".")[0][:100]
                        views = v.get("views", 0)
                        intel_context += f"- \"{first_sentence}\" ({views:,} views)\n"

        prompt = f"""Create a TikTok affiliate video script for a creator promoting this product.

PRODUCT: {product_name}
BRAND: {BRAND_NAME}
STYLE: {script_style}
TARGET AUDIENCE: {target_niche}

KEY FEATURES:
{features_text}
{intel_context}

IMPORTANT: Use the competitor intelligence above to inform your hook style,
selling techniques, and CTA approach. The data shows what's actually working
in this niche right now.

REQUIREMENTS:
1. Hook in first 3 seconds using the most effective hook type from the data
2. Show the product within first 5 seconds
3. Use the top selling techniques identified in competitor analysis
4. Share personal reaction/opinion (authenticity converts)
5. End with strong CTA matching what works in this niche
6. Keep total length 30-60 seconds
7. Include text overlay suggestions for key moments

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
Hashtags:"""

        system_context = (
            f"You are a TikTok affiliate marketing expert who creates scripts "
            f"based on data from top-performing competitor videos. "
            f"Brand: {BRAND_NAME} - \"{BRAND_TAGLINE}\". "
            f"Your scripts feel authentic but incorporate proven patterns "
            f"from videos that have generated millions of views."
        )

        return self.generate_and_save(
            prompt=prompt,
            output_dir=self.output_dir / "scripts",
            system_context=system_context,
            metadata={
                "type": "data_driven_script",
                "product": product_name,
                "style": script_style,
                "niche": target_niche,
                "has_research_data": research_results is not None,
            },
        )

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
