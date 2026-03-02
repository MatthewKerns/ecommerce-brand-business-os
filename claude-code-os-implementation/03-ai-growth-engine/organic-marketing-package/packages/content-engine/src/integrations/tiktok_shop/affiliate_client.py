"""
TikTok Shop Affiliate Seller API Client

This module provides the affiliate-specific API client for managing creator
outreach, collaborations, and affiliate performance tracking through the
TikTok Shop Affiliate Seller APIs.

Key capabilities:
- Search and browse affiliate creators with filters (GMV, followers, category)
- Send target collaboration invitations to specific creators
- Create and manage open collaborations
- Track affiliate performance metrics
- Manage outreach campaigns with rate-limit awareness

Reference: https://partner.tiktokshop.com/docv2/page/affiliate-seller-api-overview
"""
import time
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from enum import Enum

from integrations.tiktok_shop.client import TikTokShopClient
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopValidationError,
)

logger = logging.getLogger(__name__)


class AffiliateOutreachTier(Enum):
    """TikTok Shop affiliate outreach tier levels"""
    TIER_1 = "tier_1"  # New shop: 1,000 one-time actions
    TIER_2 = "tier_2"  # After 1st affiliate sale: 2,000/week, <20K followers
    TIER_3 = "tier_3"  # After $2K affiliate GMV/30d: 7,000/week, no limits


class CollaborationType(Enum):
    """Types of affiliate collaborations"""
    OPEN = "OPEN"       # Any creator can join
    TARGET = "TARGET"   # Invitation to specific creators


class CreatorSortField(Enum):
    """Sort fields for creator search"""
    GMV_30D = "gmv_30d"
    FOLLOWERS = "follower_count"
    VIDEO_COUNT = "video_count"
    SALES_30D = "sales_30d"
    ENGAGEMENT_RATE = "engagement_rate"


class SortOrder(Enum):
    """Sort order"""
    ASC = "ASC"
    DESC = "DESC"


class TikTokShopAffiliateClient:
    """
    Client for TikTok Shop Affiliate Seller API operations.

    This client wraps the base TikTokShopClient to provide affiliate-specific
    functionality including creator discovery, outreach, collaboration management,
    and performance tracking.

    The TikTok Shop Affiliate API allows sellers to:
    - Search creators by GMV, follower count, category, and other filters
    - Send target collaboration invitations with custom messages
    - Create open collaborations for products
    - Track affiliate video performance and GMV attribution
    - Monitor outreach limits and tier status

    Attributes:
        client: Base TikTokShopClient instance for making API requests
        _outreach_count: Tracks outreach actions for rate limit awareness
        _outreach_reset_time: When the weekly outreach counter resets (Sunday)
    """

    # Affiliate API path prefix (TikTok Shop API v2)
    AFFILIATE_API_PREFIX = "/api/affiliate/seller"

    # Outreach limits per tier
    TIER_LIMITS = {
        AffiliateOutreachTier.TIER_1: {"weekly_limit": 1000, "max_followers": None},
        AffiliateOutreachTier.TIER_2: {"weekly_limit": 2000, "max_followers": 20000},
        AffiliateOutreachTier.TIER_3: {"weekly_limit": 7000, "max_followers": None},
    }

    def __init__(self, client: TikTokShopClient):
        """
        Initialize the Affiliate Client.

        Args:
            client: An authenticated TikTokShopClient instance

        Example:
            >>> base_client = TikTokShopClient('app_key', 'app_secret', 'token')
            >>> affiliate = TikTokShopAffiliateClient(base_client)
        """
        self.client = client
        self._outreach_count = 0
        self._outreach_reset_time = self._next_sunday()

    def _next_sunday(self) -> datetime:
        """Calculate next Sunday midnight (outreach counter reset)."""
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0 and now.hour >= 0:
            days_until_sunday = 7
        return (now + timedelta(days=days_until_sunday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # ========================================================================
    # CREATOR SEARCH & DISCOVERY
    # ========================================================================

    def search_creators(
        self,
        category: Optional[str] = None,
        min_gmv_30d: Optional[float] = None,
        max_gmv_30d: Optional[float] = None,
        min_followers: Optional[int] = None,
        max_followers: Optional[int] = None,
        min_sales_30d: Optional[int] = None,
        min_video_count: Optional[int] = None,
        min_engagement_rate: Optional[float] = None,
        keyword: Optional[str] = None,
        sort_by: CreatorSortField = CreatorSortField.GMV_30D,
        sort_order: SortOrder = SortOrder.DESC,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for affiliate creators with filters.

        This endpoint allows sellers to browse the TikTok Shop affiliate
        marketplace and find creators that match specific criteria. Essential
        for building targeted outreach lists.

        Args:
            category: Product category filter (e.g., 'toys_and_games')
            min_gmv_30d: Minimum GMV in last 30 days (e.g., 1000.0 for $1K+)
            max_gmv_30d: Maximum GMV in last 30 days
            min_followers: Minimum follower count
            max_followers: Maximum follower count (Tier 2 limit: 20,000)
            min_sales_30d: Minimum number of sales in last 30 days
            min_video_count: Minimum number of videos posted
            min_engagement_rate: Minimum engagement rate (0.0-1.0)
            keyword: Search keyword for creator bio/content
            sort_by: Field to sort results by
            sort_order: Sort direction (ASC or DESC)
            page_size: Number of results per page (max 50)
            page_token: Pagination token for next page

        Returns:
            Dictionary containing:
                - creators: List of creator profiles with metrics
                - total: Total number of matching creators
                - next_page_token: Token for fetching next page

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> affiliate = TikTokShopAffiliateClient(client)
            >>> # Find top-performing creators in toys/games with $1K+ monthly GMV
            >>> results = affiliate.search_creators(
            ...     category='toys_and_games',
            ...     min_gmv_30d=1000.0,
            ...     min_followers=5000,
            ...     sort_by=CreatorSortField.GMV_30D,
            ...     page_size=20
            ... )
            >>> for creator in results['data']['creators']:
            ...     print(f"{creator['nickname']}: ${creator['gmv_30d']} GMV")
        """
        params = {
            "page_size": min(page_size, 50),
            "sort_field": sort_by.value,
            "sort_order": sort_order.value,
        }

        # Apply filters
        if category:
            params["category"] = category
        if min_gmv_30d is not None:
            params["min_gmv_30d"] = min_gmv_30d
        if max_gmv_30d is not None:
            params["max_gmv_30d"] = max_gmv_30d
        if min_followers is not None:
            params["min_follower_count"] = min_followers
        if max_followers is not None:
            params["max_follower_count"] = max_followers
        if min_sales_30d is not None:
            params["min_sales_30d"] = min_sales_30d
        if min_video_count is not None:
            params["min_video_count"] = min_video_count
        if min_engagement_rate is not None:
            params["min_engagement_rate"] = min_engagement_rate
        if keyword:
            params["keyword"] = keyword
        if page_token:
            params["page_token"] = page_token

        return self.client._make_request(
            method="POST",
            path=f"{self.AFFILIATE_API_PREFIX}/search_creators",
            data=params,
        )

    def get_creator_profile(self, creator_id: str) -> Dict[str, Any]:
        """
        Get detailed profile for a specific creator.

        Args:
            creator_id: TikTok creator/affiliate ID

        Returns:
            Dictionary containing creator details:
                - creator_id: Unique identifier
                - nickname: Display name
                - avatar_url: Profile image URL
                - follower_count: Number of followers
                - bio: Creator bio text
                - categories: Content categories
                - gmv_30d: GMV in last 30 days
                - sales_30d: Sales count in last 30 days
                - video_count: Total video count
                - engagement_rate: Average engagement rate
                - collaboration_status: Current collaboration status with seller

        Example:
            >>> profile = affiliate.get_creator_profile('creator_123')
            >>> print(f"{profile['data']['nickname']}: {profile['data']['follower_count']} followers")
        """
        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/creator_profile",
            params={"creator_id": creator_id},
        )

    # ========================================================================
    # TARGET COLLABORATIONS (Direct Outreach)
    # ========================================================================

    def create_target_collaboration(
        self,
        product_ids: List[str],
        commission_rate: float,
        collaboration_name: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a target collaboration for inviting specific creators.

        A target collaboration defines the products, commission rate, and terms
        for inviting creators to promote specific products.

        Args:
            product_ids: List of TikTok Shop product IDs to include
            commission_rate: Commission percentage (e.g., 15.0 for 15%)
            collaboration_name: Optional name for the collaboration
            start_time: Collaboration start time (Unix timestamp)
            end_time: Collaboration end time (Unix timestamp)

        Returns:
            Dictionary containing:
                - collaboration_id: Unique ID for the new collaboration
                - status: Collaboration status

        Raises:
            TikTokShopValidationError: If parameters are invalid

        Example:
            >>> collab = affiliate.create_target_collaboration(
            ...     product_ids=['prod_123', 'prod_456'],
            ...     commission_rate=15.0,
            ...     collaboration_name='March 2026 TCG Push'
            ... )
            >>> collab_id = collab['data']['collaboration_id']
        """
        if not product_ids:
            raise TikTokShopValidationError("At least one product_id is required")
        if commission_rate < 1.0 or commission_rate > 80.0:
            raise TikTokShopValidationError(
                "Commission rate must be between 1% and 80%"
            )

        data = {
            "product_ids": product_ids,
            "commission_rate": commission_rate,
        }

        if collaboration_name:
            data["collaboration_name"] = collaboration_name
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time

        return self.client._make_request(
            method="POST",
            path=f"{self.AFFILIATE_API_PREFIX}/create_target_collaboration",
            data=data,
        )

    def send_invitation(
        self,
        collaboration_id: str,
        creator_ids: List[str],
        invitation_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send target collaboration invitations to specific creators.

        This is the core outreach action. Each invitation consumes one outreach
        action from your weekly limit. The message is displayed to the creator
        along with product details and commission rate.

        Args:
            collaboration_id: ID of the target collaboration
            creator_ids: List of creator IDs to invite (max 20 per request)
            invitation_message: Optional personalized message (max 500 chars)

        Returns:
            Dictionary containing:
                - success_count: Number of invitations sent
                - failed_count: Number of failed invitations
                - failed_creator_ids: List of creator IDs that failed
                - remaining_outreach_actions: Actions remaining this week

        Raises:
            TikTokShopValidationError: If parameters invalid or outreach limit hit
            TikTokShopAPIError: If API request fails

        Example:
            >>> result = affiliate.send_invitation(
            ...     collaboration_id='collab_123',
            ...     creator_ids=['creator_1', 'creator_2'],
            ...     invitation_message='Love your TCG content! Check out our binders.'
            ... )
            >>> print(f"Sent: {result['data']['success_count']}")
            >>> print(f"Remaining: {result['data']['remaining_outreach_actions']}")
        """
        if not creator_ids:
            raise TikTokShopValidationError("At least one creator_id is required")
        if len(creator_ids) > 20:
            raise TikTokShopValidationError("Maximum 20 creators per invitation batch")
        if invitation_message and len(invitation_message) > 500:
            raise TikTokShopValidationError(
                f"Invitation message exceeds 500 char limit "
                f"({len(invitation_message)} chars)"
            )

        data = {
            "collaboration_id": collaboration_id,
            "creator_ids": creator_ids,
        }

        if invitation_message:
            data["invitation_message"] = invitation_message

        response = self.client._make_request(
            method="POST",
            path=f"{self.AFFILIATE_API_PREFIX}/send_invitation",
            data=data,
        )

        # Track outreach count
        success_count = response.get("data", {}).get("success_count", 0)
        self._outreach_count += success_count
        logger.info(
            f"Sent {success_count} invitations. "
            f"Weekly total: {self._outreach_count}"
        )

        return response

    def get_invitation_status(
        self,
        collaboration_id: str,
        creator_ids: Optional[List[str]] = None,
        status_filter: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get status of sent invitations for a target collaboration.

        Args:
            collaboration_id: Target collaboration ID
            creator_ids: Optional filter by specific creator IDs
            status_filter: Filter by status ('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED')
            page_size: Results per page (max 50)
            page_token: Pagination token

        Returns:
            Dictionary containing invitation status details

        Example:
            >>> status = affiliate.get_invitation_status(
            ...     collaboration_id='collab_123',
            ...     status_filter='ACCEPTED'
            ... )
            >>> for inv in status['data']['invitations']:
            ...     print(f"{inv['creator_nickname']}: {inv['status']}")
        """
        params = {
            "collaboration_id": collaboration_id,
            "page_size": min(page_size, 50),
        }

        if creator_ids:
            params["creator_ids"] = creator_ids
        if status_filter:
            params["status"] = status_filter
        if page_token:
            params["page_token"] = page_token

        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/invitation_status",
            params=params,
        )

    # ========================================================================
    # OPEN COLLABORATIONS
    # ========================================================================

    def create_open_collaboration(
        self,
        product_ids: List[str],
        commission_rate: float,
        collaboration_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an open collaboration that any eligible creator can join.

        Open collaborations make products available in the affiliate marketplace
        for any creator to discover and promote.

        Args:
            product_ids: List of product IDs to make available
            commission_rate: Commission percentage for affiliates
            collaboration_name: Optional name

        Returns:
            Dictionary with collaboration details

        Example:
            >>> collab = affiliate.create_open_collaboration(
            ...     product_ids=['prod_123'],
            ...     commission_rate=15.0,
            ...     collaboration_name='Infinity Vault Open Program'
            ... )
        """
        if not product_ids:
            raise TikTokShopValidationError("At least one product_id is required")

        data = {
            "product_ids": product_ids,
            "commission_rate": commission_rate,
        }

        if collaboration_name:
            data["collaboration_name"] = collaboration_name

        return self.client._make_request(
            method="POST",
            path=f"{self.AFFILIATE_API_PREFIX}/create_open_collaboration",
            data=data,
        )

    def search_open_collaboration_products(
        self,
        collaboration_id: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search products in open collaborations.

        Args:
            collaboration_id: Optional filter by collaboration
            page_size: Results per page
            page_token: Pagination token

        Returns:
            Dictionary with product collaboration details
        """
        params = {"page_size": min(page_size, 50)}

        if collaboration_id:
            params["collaboration_id"] = collaboration_id
        if page_token:
            params["page_token"] = page_token

        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/open_collaboration_products",
            params=params,
        )

    # ========================================================================
    # AFFILIATE PERFORMANCE & ANALYTICS
    # ========================================================================

    def get_affiliate_orders(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        creator_id: Optional[str] = None,
        collaboration_id: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get orders attributed to affiliate creators.

        Args:
            start_time: Start timestamp (defaults to 30 days ago)
            end_time: End timestamp (defaults to now)
            creator_id: Filter by specific creator
            collaboration_id: Filter by collaboration
            page_size: Results per page
            page_token: Pagination token

        Returns:
            Dictionary containing affiliate order details

        Example:
            >>> orders = affiliate.get_affiliate_orders(
            ...     start_time=int(time.time()) - 30*24*3600,
            ...     end_time=int(time.time())
            ... )
            >>> total_gmv = sum(o['order_amount'] for o in orders['data']['orders'])
        """
        if not end_time:
            end_time = int(time.time())
        if not start_time:
            start_time = end_time - (30 * 24 * 60 * 60)

        params = {
            "start_time": start_time,
            "end_time": end_time,
            "page_size": min(page_size, 50),
        }

        if creator_id:
            params["creator_id"] = creator_id
        if collaboration_id:
            params["collaboration_id"] = collaboration_id
        if page_token:
            params["page_token"] = page_token

        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/affiliate_orders",
            params=params,
        )

    def get_affiliate_performance(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        creator_id: Optional[str] = None,
        group_by: str = "creator",
    ) -> Dict[str, Any]:
        """
        Get affiliate performance metrics.

        Args:
            start_time: Start timestamp
            end_time: End timestamp
            creator_id: Filter by creator
            group_by: Group results by 'creator', 'product', or 'daily'

        Returns:
            Dictionary containing performance metrics:
                - total_gmv: Total GMV from affiliates
                - total_orders: Total affiliate orders
                - total_commission: Total commission paid
                - creators/products/daily: Grouped metrics

        Example:
            >>> perf = affiliate.get_affiliate_performance(group_by='creator')
            >>> for c in perf['data']['creators']:
            ...     print(f"{c['nickname']}: ${c['gmv']} GMV, {c['video_count']} videos")
        """
        if not end_time:
            end_time = int(time.time())
        if not start_time:
            start_time = end_time - (30 * 24 * 60 * 60)

        params = {
            "start_time": start_time,
            "end_time": end_time,
            "group_by": group_by,
        }

        if creator_id:
            params["creator_id"] = creator_id

        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/performance",
            params=params,
        )

    def get_affiliate_gmv_summary(
        self,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get affiliate GMV summary for the last N days.

        This is critical for tracking progress toward Tier 3 unlock ($2K/30d).

        Args:
            days: Number of days to look back (default 30)

        Returns:
            Dictionary with GMV summary including tier status

        Example:
            >>> summary = affiliate.get_affiliate_gmv_summary(days=30)
            >>> gmv = summary['data']['total_gmv']
            >>> print(f"Affiliate GMV: ${gmv}")
            >>> print(f"Tier 3 progress: ${gmv}/$2,000")
        """
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)

        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/gmv_summary",
            params={"start_time": start_time, "end_time": end_time},
        )

    # ========================================================================
    # OUTREACH MANAGEMENT & TIER STATUS
    # ========================================================================

    def get_outreach_status(self) -> Dict[str, Any]:
        """
        Get current outreach tier status and remaining actions.

        Returns:
            Dictionary containing:
                - current_tier: Current outreach tier (1, 2, or 3)
                - weekly_limit: Maximum outreach actions per week
                - actions_used: Actions used this week
                - actions_remaining: Actions remaining this week
                - max_follower_limit: Max follower count for outreach (null = unlimited)
                - tier_requirements: Requirements for next tier
                - affiliate_gmv_30d: Current affiliate GMV (for Tier 3 tracking)
                - reset_time: When the weekly counter resets (Sunday)

        Example:
            >>> status = affiliate.get_outreach_status()
            >>> tier = status['data']['current_tier']
            >>> remaining = status['data']['actions_remaining']
            >>> print(f"Tier {tier}: {remaining} actions remaining")
        """
        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/outreach_status",
        )

    def get_sample_requests(
        self,
        status_filter: Optional[str] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get free sample requests from affiliate creators.

        After sending invitations, creators can request free product samples.
        This endpoint tracks those requests for fulfillment.

        Args:
            status_filter: Filter by status ('PENDING', 'APPROVED', 'SHIPPED', 'RECEIVED')
            page_size: Results per page
            page_token: Pagination token

        Returns:
            Dictionary containing sample request details

        Example:
            >>> requests = affiliate.get_sample_requests(status_filter='PENDING')
            >>> for req in requests['data']['sample_requests']:
            ...     print(f"{req['creator_nickname']} wants {req['product_name']}")
        """
        params = {"page_size": min(page_size, 50)}

        if status_filter:
            params["status"] = status_filter
        if page_token:
            params["page_token"] = page_token

        return self.client._make_request(
            method="GET",
            path=f"{self.AFFILIATE_API_PREFIX}/sample_requests",
            params=params,
        )

    def approve_sample_request(
        self,
        request_id: str,
        shipping_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve a free sample request from an affiliate creator.

        Args:
            request_id: Sample request ID
            shipping_note: Optional note for the creator about shipping

        Returns:
            Dictionary with approval confirmation
        """
        data = {"request_id": request_id}
        if shipping_note:
            data["shipping_note"] = shipping_note

        return self.client._make_request(
            method="POST",
            path=f"{self.AFFILIATE_API_PREFIX}/approve_sample",
            data=data,
        )

    # ========================================================================
    # CREATOR MESSAGING
    # ========================================================================

    def send_creator_message(
        self,
        creator_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Send a follow-up message to a creator in an active collaboration.

        Args:
            creator_id: Creator ID
            message: Message content (max 500 chars)

        Returns:
            Dictionary with message delivery status

        Example:
            >>> affiliate.send_creator_message(
            ...     creator_id='creator_123',
            ...     message='Thanks for joining! Here is the script for your video...'
            ... )
        """
        if not message:
            raise TikTokShopValidationError("Message cannot be empty")
        if len(message) > 500:
            raise TikTokShopValidationError(
                f"Message exceeds 500 char limit ({len(message)} chars)"
            )

        return self.client._make_request(
            method="POST",
            path=f"{self.AFFILIATE_API_PREFIX}/send_message",
            data={"creator_id": creator_id, "message": message},
        )

    # ========================================================================
    # BATCH OPERATIONS (For Campaign Automation)
    # ========================================================================

    def batch_search_and_invite(
        self,
        collaboration_id: str,
        search_filters: Dict[str, Any],
        invitation_message: str,
        max_invitations: int = 50,
        tier: AffiliateOutreachTier = AffiliateOutreachTier.TIER_2,
    ) -> Dict[str, Any]:
        """
        Search for creators matching criteria and send batch invitations.

        This is the core automation method that replicates what agencies like
        MADA do manually. It searches for creators, filters them, and sends
        invitations in batches respecting tier limits.

        Args:
            collaboration_id: Target collaboration to invite creators to
            search_filters: Filters for creator search (same as search_creators params)
            invitation_message: Message to include with invitation (max 500 chars)
            max_invitations: Maximum invitations to send in this batch
            tier: Current outreach tier (determines limits)

        Returns:
            Dictionary containing:
                - total_found: Creators matching search criteria
                - invitations_sent: Number of invitations sent
                - invitations_failed: Number that failed
                - remaining_actions: Actions remaining this week
                - creators_invited: List of invited creator details

        Example:
            >>> result = affiliate.batch_search_and_invite(
            ...     collaboration_id='collab_123',
            ...     search_filters={
            ...         'category': 'toys_and_games',
            ...         'min_gmv_30d': 1000.0,
            ...         'min_followers': 5000,
            ...         'max_followers': 20000,
            ...     },
            ...     invitation_message='Your TCG content is awesome!...',
            ...     max_invitations=50
            ... )
            >>> print(f"Sent {result['invitations_sent']} invitations")
        """
        tier_config = self.TIER_LIMITS[tier]
        max_followers = tier_config.get("max_followers")

        # Apply tier follower limit
        if max_followers and search_filters.get("max_followers", float("inf")) > max_followers:
            search_filters["max_followers"] = max_followers
            logger.info(f"Applied Tier {tier.value} follower limit: {max_followers}")

        total_sent = 0
        total_failed = 0
        creators_invited = []
        page_token = None

        while total_sent < max_invitations:
            # Search for creators
            search_result = self.search_creators(
                page_size=min(20, max_invitations - total_sent),
                page_token=page_token,
                **search_filters,
            )

            creators = search_result.get("data", {}).get("creators", [])
            if not creators:
                break

            # Extract creator IDs for invitation batch
            batch_ids = [c["creator_id"] for c in creators]

            # Send invitations in batches of 20
            for i in range(0, len(batch_ids), 20):
                batch = batch_ids[i : i + 20]

                try:
                    invite_result = self.send_invitation(
                        collaboration_id=collaboration_id,
                        creator_ids=batch,
                        invitation_message=invitation_message,
                    )

                    batch_sent = invite_result.get("data", {}).get("success_count", 0)
                    batch_failed = invite_result.get("data", {}).get("failed_count", 0)

                    total_sent += batch_sent
                    total_failed += batch_failed

                    # Track invited creators
                    for creator in creators[i : i + len(batch)]:
                        creators_invited.append({
                            "creator_id": creator.get("creator_id"),
                            "nickname": creator.get("nickname"),
                            "follower_count": creator.get("follower_count"),
                            "gmv_30d": creator.get("gmv_30d"),
                        })

                    logger.info(
                        f"Batch sent: {batch_sent} success, {batch_failed} failed. "
                        f"Running total: {total_sent}/{max_invitations}"
                    )

                except TikTokShopAPIError as e:
                    logger.warning(f"Batch invitation failed: {e}")
                    total_failed += len(batch)

                if total_sent >= max_invitations:
                    break

            # Get next page
            page_token = search_result.get("data", {}).get("next_page_token")
            if not page_token:
                break

        return {
            "total_found": search_result.get("data", {}).get("total", 0),
            "invitations_sent": total_sent,
            "invitations_failed": total_failed,
            "creators_invited": creators_invited,
        }
