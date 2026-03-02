"""
TikTok Competitor Video Intelligence

Multi-source module for discovering, analyzing, and learning from
top-performing TikTok Shop videos in a product niche.

Data Sources (layered, uses whatever is available):
1. TikTok Research API - Official video query endpoint (requires approval)
2. TikTok Creative Center - Trending hashtags, top products, top ads (free)
3. Third-party analytics - Kalodata/FastMoss/EchoTik API (paid, most data)
4. Direct scraping fallback - Apify/similar for video metadata + transcripts

Pipeline: Discover videos -> Extract transcripts -> Analyze hooks/structure ->
         Generate optimized scripts -> Feed to affiliate outreach
"""
import json
import logging
import time
import re
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class DataSource(Enum):
    TIKTOK_RESEARCH_API = "tiktok_research_api"
    TIKTOK_CREATIVE_CENTER = "tiktok_creative_center"
    KALODATA = "kalodata"
    FASTMOSS = "fastmoss"
    ECHOTIK = "echotik"
    MANUAL = "manual"


class VideoIntelligenceClient:
    """
    Multi-source client for TikTok video intelligence.

    Tries multiple data sources in priority order and aggregates results.
    Falls back gracefully when a source isn't configured.
    """

    # TikTok Research API (official, requires academic/commercial approval)
    RESEARCH_API_BASE = "https://open.tiktokapis.com/v2/research"
    # TikTok Creative Center (free, browser-based data)
    CREATIVE_CENTER_BASE = "https://ads.tiktok.com/creative_radar_api/v1/popular"
    # Third-party APIs
    KALODATA_API_BASE = "https://api.kalodata.com/v1"
    FASTMOSS_API_BASE = "https://api.fastmoss.com/v1"

    def __init__(
        self,
        tiktok_research_token: Optional[str] = None,
        kalodata_api_key: Optional[str] = None,
        fastmoss_api_key: Optional[str] = None,
        echotik_api_key: Optional[str] = None,
    ):
        self.tiktok_research_token = tiktok_research_token
        self.kalodata_api_key = kalodata_api_key
        self.fastmoss_api_key = fastmoss_api_key
        self.echotik_api_key = echotik_api_key

        self._available_sources = self._detect_sources()
        logger.info(f"Video intelligence sources available: {self._available_sources}")

    def _detect_sources(self) -> List[DataSource]:
        """Detect which data sources are configured."""
        sources = []
        if self.tiktok_research_token:
            sources.append(DataSource.TIKTOK_RESEARCH_API)
        if self.kalodata_api_key:
            sources.append(DataSource.KALODATA)
        if self.fastmoss_api_key:
            sources.append(DataSource.FASTMOSS)
        if self.echotik_api_key:
            sources.append(DataSource.ECHOTIK)
        # Creative Center is always available (public)
        sources.append(DataSource.TIKTOK_CREATIVE_CENTER)
        # Manual is always available as last resort
        sources.append(DataSource.MANUAL)
        return sources

    # ========================================================================
    # TRENDING DISCOVERY
    # ========================================================================

    def discover_trending_videos(
        self,
        category: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        region: str = "US",
        days: int = 7,
        min_views: int = 100000,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Discover top-performing videos in a niche.

        Tries multiple sources and merges results.

        Args:
            category: Product category (e.g., 'toys_and_games', 'trading_cards')
            hashtags: Hashtags to search (e.g., ['#pokemontcg', '#tcgcollector'])
            region: Region code (default 'US')
            days: Lookback period in days
            min_views: Minimum view count filter
            limit: Max results to return

        Returns:
            Dictionary with discovered videos and source metadata
        """
        all_videos = []
        sources_used = []

        # Try TikTok Research API first (most reliable official data)
        if DataSource.TIKTOK_RESEARCH_API in self._available_sources:
            try:
                videos = self._research_api_query(
                    hashtags=hashtags,
                    region=region,
                    days=days,
                    min_views=min_views,
                    limit=limit,
                )
                all_videos.extend(videos)
                sources_used.append("tiktok_research_api")
            except Exception as e:
                logger.warning(f"Research API query failed: {e}")

        # Try Kalodata
        if DataSource.KALODATA in self._available_sources:
            try:
                videos = self._kalodata_trending(
                    category=category,
                    region=region,
                    days=days,
                    limit=limit,
                )
                all_videos.extend(videos)
                sources_used.append("kalodata")
            except Exception as e:
                logger.warning(f"Kalodata query failed: {e}")

        # Try FastMoss
        if DataSource.FASTMOSS in self._available_sources:
            try:
                videos = self._fastmoss_trending(
                    category=category,
                    region=region,
                    days=days,
                    limit=limit,
                )
                all_videos.extend(videos)
                sources_used.append("fastmoss")
            except Exception as e:
                logger.warning(f"FastMoss query failed: {e}")

        # Deduplicate by video_id
        seen = set()
        unique_videos = []
        for v in all_videos:
            vid = v.get("video_id", v.get("url", ""))
            if vid and vid not in seen:
                seen.add(vid)
                unique_videos.append(v)

        # Sort by views descending
        unique_videos.sort(key=lambda v: v.get("views", 0), reverse=True)

        return {
            "videos": unique_videos[:limit],
            "total_found": len(unique_videos),
            "sources_used": sources_used,
            "query": {
                "category": category,
                "hashtags": hashtags,
                "region": region,
                "days": days,
                "min_views": min_views,
            },
        }

    def discover_top_products(
        self,
        category: Optional[str] = None,
        region: str = "US",
        days: int = 30,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Discover top-selling products on TikTok Shop in a category.

        Args:
            category: Product category filter
            region: Region code
            days: Lookback period
            limit: Max results

        Returns:
            Dictionary with top products and metrics
        """
        products = []
        sources_used = []

        if DataSource.KALODATA in self._available_sources:
            try:
                prods = self._kalodata_top_products(
                    category=category, region=region, days=days, limit=limit
                )
                products.extend(prods)
                sources_used.append("kalodata")
            except Exception as e:
                logger.warning(f"Kalodata top products failed: {e}")

        if DataSource.FASTMOSS in self._available_sources:
            try:
                prods = self._fastmoss_top_products(
                    category=category, region=region, days=days, limit=limit
                )
                products.extend(prods)
                sources_used.append("fastmoss")
            except Exception as e:
                logger.warning(f"FastMoss top products failed: {e}")

        # Deduplicate
        seen = set()
        unique = []
        for p in products:
            pid = p.get("product_id", p.get("product_name", ""))
            if pid and pid not in seen:
                seen.add(pid)
                unique.append(p)

        unique.sort(key=lambda p: p.get("gmv", 0), reverse=True)

        return {
            "products": unique[:limit],
            "total_found": len(unique),
            "sources_used": sources_used,
        }

    def discover_trending_hashtags(
        self,
        seed_hashtags: Optional[List[str]] = None,
        region: str = "US",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Discover trending hashtags related to a niche.

        Uses TikTok Creative Center data (free, always available).

        Args:
            seed_hashtags: Starting hashtags to find related trends
            region: Region code
            limit: Max results

        Returns:
            Dictionary with trending hashtags and engagement metrics
        """
        hashtags = []

        try:
            response = requests.get(
                f"{self.CREATIVE_CENTER_BASE}/hashtag/list",
                params={
                    "country_code": region,
                    "period": 7,
                    "page": 1,
                    "limit": limit,
                },
                timeout=15,
            )
            if response.ok:
                data = response.json().get("data", {})
                for h in data.get("list", []):
                    hashtags.append({
                        "hashtag": h.get("hashtag_name", ""),
                        "views": h.get("publish_cnt", 0),
                        "trend": h.get("trend", 0),
                        "video_count": h.get("video_cnt", 0),
                    })
        except Exception as e:
            logger.warning(f"Creative Center hashtag query failed: {e}")

        return {
            "hashtags": hashtags[:limit],
            "seed_hashtags": seed_hashtags,
            "region": region,
        }

    # ========================================================================
    # VIDEO ANALYSIS
    # ========================================================================

    def analyze_video(
        self,
        video_url: Optional[str] = None,
        video_id: Optional[str] = None,
        transcript: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a single video's structure, hook, and selling techniques.

        If transcript is not provided, attempts to extract it from the video URL.

        Args:
            video_url: TikTok video URL
            video_id: TikTok video ID
            transcript: Pre-extracted transcript text

        Returns:
            Structured analysis of the video's marketing approach
        """
        # Build analysis from available data
        analysis = {
            "video_url": video_url,
            "video_id": video_id,
            "transcript": transcript,
            "hook_analysis": None,
            "structure_breakdown": None,
            "selling_techniques": [],
            "cta_analysis": None,
            "estimated_metrics": None,
        }

        if transcript:
            analysis["hook_analysis"] = self._analyze_hook(transcript)
            analysis["structure_breakdown"] = self._analyze_structure(transcript)
            analysis["selling_techniques"] = self._identify_techniques(transcript)
            analysis["cta_analysis"] = self._analyze_cta(transcript)

        return analysis

    def batch_analyze_videos(
        self,
        videos: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze a batch of videos to find common patterns.

        Args:
            videos: List of video objects with transcripts

        Returns:
            Aggregated analysis with common patterns
        """
        analyses = []
        for video in videos:
            analysis = self.analyze_video(
                video_url=video.get("url"),
                video_id=video.get("video_id"),
                transcript=video.get("transcript"),
            )
            analyses.append(analysis)

        # Aggregate patterns
        all_hooks = [a["hook_analysis"] for a in analyses if a["hook_analysis"]]
        all_techniques = []
        for a in analyses:
            all_techniques.extend(a.get("selling_techniques", []))

        # Count technique frequency
        technique_counts = {}
        for t in all_techniques:
            technique_counts[t] = technique_counts.get(t, 0) + 1

        sorted_techniques = sorted(
            technique_counts.items(), key=lambda x: x[1], reverse=True
        )

        return {
            "videos_analyzed": len(analyses),
            "individual_analyses": analyses,
            "common_patterns": {
                "top_techniques": [
                    {"technique": t, "frequency": c} for t, c in sorted_techniques[:10]
                ],
                "hook_types": self._aggregate_hook_types(all_hooks),
            },
        }

    def _analyze_hook(self, transcript: str) -> Dict[str, Any]:
        """Analyze the first 3 seconds / first sentence of a video."""
        sentences = re.split(r'[.!?]+', transcript.strip())
        hook = sentences[0].strip() if sentences else ""

        hook_type = "unknown"
        if "?" in hook:
            hook_type = "question"
        elif any(w in hook.lower() for w in ["stop", "wait", "listen", "omg", "this"]):
            hook_type = "attention_command"
        elif any(w in hook.lower() for w in ["best", "top", "only", "never", "worst"]):
            hook_type = "bold_claim"
        elif any(w in hook.lower() for w in ["i found", "i tried", "i bought", "finally"]):
            hook_type = "personal_story"
        elif any(w in hook.lower() for w in ["$", "save", "deal", "free", "sale"]):
            hook_type = "value_proposition"

        return {
            "hook_text": hook,
            "hook_type": hook_type,
            "word_count": len(hook.split()),
        }

    def _analyze_structure(self, transcript: str) -> Dict[str, Any]:
        """Break down video script structure."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', transcript) if s.strip()]
        total = len(sentences)

        if total == 0:
            return {"sections": [], "total_sentences": 0}

        # Rough section mapping for a typical TikTok
        sections = []
        if total >= 1:
            sections.append({"name": "hook", "text": sentences[0], "position": "0-3s"})
        if total >= 3:
            sections.append({
                "name": "problem_or_feature",
                "text": " ".join(sentences[1:min(3, total)]),
                "position": "3-15s",
            })
        if total >= 5:
            sections.append({
                "name": "demonstration",
                "text": " ".join(sentences[3:min(5, total)]),
                "position": "15-30s",
            })
        if total >= 6:
            sections.append({
                "name": "cta",
                "text": " ".join(sentences[max(total - 2, 5):]),
                "position": "30s+",
            })

        return {"sections": sections, "total_sentences": total}

    def _identify_techniques(self, transcript: str) -> List[str]:
        """Identify selling techniques used in the video."""
        techniques = []
        lower = transcript.lower()

        technique_markers = {
            "social_proof": ["everyone", "viral", "trending", "sold out", "millions", "thousands"],
            "urgency": ["hurry", "limited", "running out", "last chance", "before it's gone", "ends today"],
            "authority": ["expert", "tested", "reviewed", "compared", "professional"],
            "personal_testimony": ["i use", "i love", "changed my", "my favorite", "honest review", "i tried"],
            "value_anchor": ["worth", "costs less", "save", "compared to", "for only", "deal"],
            "fear_of_missing_out": ["don't miss", "you need", "game changer", "life changing", "where has this been"],
            "demonstration": ["watch this", "look at", "see how", "check this out", "let me show"],
            "comparison": ["vs", "versus", "compared to", "better than", "unlike"],
            "objection_handling": ["i know what you're thinking", "but", "the thing is", "trust me"],
            "exclusivity": ["secret", "hidden", "not many people know", "insider"],
        }

        for technique, markers in technique_markers.items():
            if any(marker in lower for marker in markers):
                techniques.append(technique)

        return techniques

    def _analyze_cta(self, transcript: str) -> Dict[str, Any]:
        """Analyze the call-to-action."""
        lower = transcript.lower()

        cta_types = {
            "link_in_bio": ["link in bio", "link in my bio", "check the link"],
            "shop_now": ["shop now", "buy now", "get yours", "grab yours"],
            "comment": ["comment", "drop a comment", "let me know"],
            "follow": ["follow for more", "follow me"],
            "save": ["save this", "bookmark"],
            "tiktok_shop": ["tiktok shop", "yellow basket", "tap the link", "click below"],
        }

        detected = []
        for cta_type, markers in cta_types.items():
            if any(m in lower for m in markers):
                detected.append(cta_type)

        return {
            "cta_types": detected,
            "has_cta": len(detected) > 0,
        }

    def _aggregate_hook_types(self, hooks: List[Dict]) -> List[Dict]:
        """Aggregate hook type frequencies from multiple videos."""
        type_counts = {}
        for h in hooks:
            ht = h.get("hook_type", "unknown")
            type_counts[ht] = type_counts.get(ht, 0) + 1

        return [
            {"type": t, "count": c}
            for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        ]

    # ========================================================================
    # DATA SOURCE IMPLEMENTATIONS
    # ========================================================================

    def _research_api_query(
        self,
        hashtags: Optional[List[str]],
        region: str,
        days: int,
        min_views: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Query TikTok Research API for videos."""
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

        query_conditions = {
            "and": [
                {"field_name": "region_code", "operation": "IN", "field_values": [region]},
            ]
        }

        if hashtags:
            query_conditions["and"].append({
                "field_name": "hashtag_name",
                "operation": "IN",
                "field_values": [h.lstrip("#") for h in hashtags],
            })

        response = requests.post(
            f"{self.RESEARCH_API_BASE}/video/query/",
            headers={
                "Authorization": f"Bearer {self.tiktok_research_token}",
                "Content-Type": "application/json",
            },
            json={
                "query": query_conditions,
                "start_date": start_date,
                "end_date": end_date,
                "max_count": min(limit, 100),
                "fields": "id,video_description,create_time,region_code,"
                          "like_count,comment_count,share_count,view_count,"
                          "hashtag_names,music_id,voice_to_text",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json().get("data", {})

        videos = []
        for v in data.get("videos", []):
            if v.get("view_count", 0) >= min_views:
                videos.append({
                    "video_id": v.get("id"),
                    "description": v.get("video_description", ""),
                    "views": v.get("view_count", 0),
                    "likes": v.get("like_count", 0),
                    "comments": v.get("comment_count", 0),
                    "shares": v.get("share_count", 0),
                    "hashtags": v.get("hashtag_names", []),
                    "transcript": v.get("voice_to_text", ""),
                    "created_at": v.get("create_time", ""),
                    "region": v.get("region_code", ""),
                    "source": "tiktok_research_api",
                    "url": f"https://www.tiktok.com/@/video/{v.get('id', '')}",
                })

        return videos

    def _kalodata_trending(
        self,
        category: Optional[str],
        region: str,
        days: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Query Kalodata for trending videos."""
        params = {
            "region": region,
            "period": f"{days}d",
            "sort_by": "views",
            "limit": limit,
        }
        if category:
            params["category"] = category

        response = requests.get(
            f"{self.KALODATA_API_BASE}/trending/videos",
            headers={"Authorization": f"Bearer {self.kalodata_api_key}"},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        videos = []
        for v in data.get("data", {}).get("videos", []):
            videos.append({
                "video_id": v.get("video_id", ""),
                "description": v.get("description", ""),
                "views": v.get("views", 0),
                "likes": v.get("likes", 0),
                "comments": v.get("comments", 0),
                "shares": v.get("shares", 0),
                "hashtags": v.get("hashtags", []),
                "transcript": v.get("transcript", ""),
                "product_name": v.get("product_name", ""),
                "product_gmv": v.get("product_gmv", 0),
                "creator_name": v.get("creator_name", ""),
                "creator_followers": v.get("creator_followers", 0),
                "source": "kalodata",
                "url": v.get("url", ""),
            })

        return videos

    def _fastmoss_trending(
        self,
        category: Optional[str],
        region: str,
        days: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Query FastMoss for trending videos."""
        params = {
            "country": region,
            "days": days,
            "sort": "views",
            "limit": limit,
        }
        if category:
            params["category"] = category

        response = requests.get(
            f"{self.FASTMOSS_API_BASE}/videos/trending",
            headers={"Authorization": f"Bearer {self.fastmoss_api_key}"},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        videos = []
        for v in data.get("data", []):
            videos.append({
                "video_id": v.get("id", ""),
                "description": v.get("desc", ""),
                "views": v.get("play_count", 0),
                "likes": v.get("digg_count", 0),
                "comments": v.get("comment_count", 0),
                "shares": v.get("share_count", 0),
                "hashtags": v.get("hashtags", []),
                "transcript": v.get("voice_to_text", ""),
                "product_name": v.get("product_title", ""),
                "creator_name": v.get("author_nickname", ""),
                "source": "fastmoss",
                "url": v.get("video_url", ""),
            })

        return videos

    def _kalodata_top_products(
        self,
        category: Optional[str],
        region: str,
        days: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Query Kalodata for top-selling products."""
        params = {
            "region": region,
            "period": f"{days}d",
            "sort_by": "gmv",
            "limit": limit,
        }
        if category:
            params["category"] = category

        response = requests.get(
            f"{self.KALODATA_API_BASE}/products/top",
            headers={"Authorization": f"Bearer {self.kalodata_api_key}"},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        products = []
        for p in data.get("data", {}).get("products", []):
            products.append({
                "product_id": p.get("product_id", ""),
                "product_name": p.get("title", ""),
                "price": p.get("price", 0),
                "gmv": p.get("gmv", 0),
                "sales": p.get("sales_count", 0),
                "rating": p.get("rating", 0),
                "video_count": p.get("related_video_count", 0),
                "top_video_url": p.get("top_video_url", ""),
                "shop_name": p.get("shop_name", ""),
                "commission_rate": p.get("commission_rate", 0),
                "source": "kalodata",
            })

        return products

    def _fastmoss_top_products(
        self,
        category: Optional[str],
        region: str,
        days: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Query FastMoss for top products."""
        params = {
            "country": region,
            "days": days,
            "sort": "sales",
            "limit": limit,
        }
        if category:
            params["category"] = category

        response = requests.get(
            f"{self.FASTMOSS_API_BASE}/products/top",
            headers={"Authorization": f"Bearer {self.fastmoss_api_key}"},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        products = []
        for p in data.get("data", []):
            products.append({
                "product_id": p.get("id", ""),
                "product_name": p.get("title", ""),
                "price": p.get("price", 0),
                "gmv": p.get("revenue", 0),
                "sales": p.get("sales", 0),
                "video_count": p.get("video_count", 0),
                "shop_name": p.get("shop_name", ""),
                "source": "fastmoss",
            })

        return products
