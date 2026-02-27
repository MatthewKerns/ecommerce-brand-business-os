"""
TikTok ETL pipeline for ingesting video performance metrics into the data warehouse.

This module provides functionality to fetch TikTok analytics data and store it
in the unified analytics database for cross-channel attribution and analysis.
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.connection import get_db_session
from analytics.models import TikTokMetrics


def ingest_tiktok_metrics(
    video_data: Optional[List[Dict[str, Any]]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    api_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Ingest TikTok video metrics into the data warehouse.

    This function fetches TikTok analytics data and stores it in the database.
    It can accept pre-fetched data or fetch from TikTok API directly.

    Args:
        video_data: Optional pre-fetched video metrics data
        start_date: Start date for fetching metrics (defaults to 7 days ago)
        end_date: End date for fetching metrics (defaults to now)
        api_client: Optional TikTok API client for fetching data

    Returns:
        Dict with ingestion results:
            - success: Whether ingestion succeeded
            - records_processed: Number of records processed
            - records_inserted: Number of new records inserted
            - records_updated: Number of existing records updated
            - errors: List of error messages if any

    Example:
        >>> result = ingest_tiktok_metrics()
        >>> print(f"Processed {result['records_processed']} records")
    """
    result = {
        "success": False,
        "records_processed": 0,
        "records_inserted": 0,
        "records_updated": 0,
        "errors": []
    }

    # Set default date range if not provided
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    db = None
    try:
        # Get database session
        db = get_db_session()

        # Fetch data from API if not provided
        if video_data is None:
            if api_client is not None:
                video_data = _fetch_from_api(api_client, start_date, end_date)
            else:
                # If no data and no API client, return with warning
                result["errors"].append(
                    "No video data provided and no API client available. "
                    "Please provide either video_data or api_client parameter."
                )
                return result

        # Process each video's metrics
        for video_record in video_data:
            try:
                # Check if record already exists
                existing_record = db.query(TikTokMetrics).filter(
                    TikTokMetrics.video_id == video_record.get("video_id"),
                    TikTokMetrics.recorded_at == video_record.get("recorded_at")
                ).first()

                if existing_record:
                    # Update existing record
                    _update_record(existing_record, video_record)
                    result["records_updated"] += 1
                else:
                    # Create new record
                    new_record = _create_record(video_record)
                    db.add(new_record)
                    result["records_inserted"] += 1

                result["records_processed"] += 1

            except Exception as e:
                result["errors"].append(
                    f"Error processing video {video_record.get('video_id', 'unknown')}: {str(e)}"
                )
                continue

        # Commit all changes
        db.commit()
        result["success"] = len(result["errors"]) == 0

    except SQLAlchemyError as e:
        if db:
            db.rollback()
        result["errors"].append(f"Database error: {str(e)}")

    except Exception as e:
        if db:
            db.rollback()
        result["errors"].append(f"Unexpected error: {str(e)}")

    finally:
        if db:
            db.close()

    return result


def _fetch_from_api(
    api_client: Any,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """
    Fetch video metrics from TikTok API.

    Args:
        api_client: TikTok API client instance
        start_date: Start date for metrics
        end_date: End date for metrics

    Returns:
        List of video metric dictionaries

    Note:
        This is a placeholder for actual API integration.
        Implement actual API calls based on TikTok Shop client.
    """
    # This would integrate with the TikTok Shop client from mcf-connector
    # For now, return empty list as placeholder
    try:
        # Example integration point:
        # video_metrics = api_client.getVideoMetrics(
        #     start_date=start_date.isoformat(),
        #     end_date=end_date.isoformat()
        # )
        # return video_metrics
        return []
    except Exception as e:
        raise Exception(f"Failed to fetch data from TikTok API: {str(e)}")


def _create_record(video_data: Dict[str, Any]) -> TikTokMetrics:
    """
    Create a new TikTokMetrics record from video data.

    Args:
        video_data: Dictionary containing video metrics

    Returns:
        TikTokMetrics: New database record
    """
    return TikTokMetrics(
        video_id=video_data.get("video_id"),
        video_url=video_data.get("video_url"),
        posted_at=video_data.get("posted_at", datetime.utcnow()),
        recorded_at=video_data.get("recorded_at", datetime.utcnow()),
        views=video_data.get("views", 0),
        likes=video_data.get("likes", 0),
        comments=video_data.get("comments", 0),
        shares=video_data.get("shares", 0),
        saves=video_data.get("saves", 0),
        engagement_rate=video_data.get("engagement_rate"),
        watch_time_avg_seconds=video_data.get("watch_time_avg_seconds"),
        watch_time_total_hours=video_data.get("watch_time_total_hours"),
        video_completion_rate=video_data.get("video_completion_rate"),
        shop_clicks=video_data.get("shop_clicks", 0),
        product_views=video_data.get("product_views", 0),
        source_location=video_data.get("source_location"),
        traffic_source=video_data.get("traffic_source"),
        hashtags=video_data.get("hashtags"),
        caption=video_data.get("caption"),
    )


def _update_record(
    existing_record: TikTokMetrics,
    video_data: Dict[str, Any]
) -> None:
    """
    Update an existing TikTokMetrics record with new data.

    Args:
        existing_record: Existing database record
        video_data: Dictionary containing updated metrics
    """
    # Update metrics that may have changed
    existing_record.views = video_data.get("views", existing_record.views)
    existing_record.likes = video_data.get("likes", existing_record.likes)
    existing_record.comments = video_data.get("comments", existing_record.comments)
    existing_record.shares = video_data.get("shares", existing_record.shares)
    existing_record.saves = video_data.get("saves", existing_record.saves)
    existing_record.engagement_rate = video_data.get(
        "engagement_rate", existing_record.engagement_rate
    )
    existing_record.watch_time_avg_seconds = video_data.get(
        "watch_time_avg_seconds", existing_record.watch_time_avg_seconds
    )
    existing_record.watch_time_total_hours = video_data.get(
        "watch_time_total_hours", existing_record.watch_time_total_hours
    )
    existing_record.video_completion_rate = video_data.get(
        "video_completion_rate", existing_record.video_completion_rate
    )
    existing_record.shop_clicks = video_data.get("shop_clicks", existing_record.shop_clicks)
    existing_record.product_views = video_data.get("product_views", existing_record.product_views)
    existing_record.updated_at = datetime.utcnow()


def get_metrics_summary(
    video_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get summary statistics for TikTok metrics.

    Args:
        video_id: Optional specific video ID to filter by
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Dict with summary statistics:
            - total_videos: Number of unique videos
            - total_views: Total views across all videos
            - total_engagement: Total engagement (likes + comments + shares + saves)
            - total_shop_clicks: Total shop clicks
            - avg_engagement_rate: Average engagement rate

    Example:
        >>> summary = get_metrics_summary()
        >>> print(f"Total views: {summary['total_views']}")
    """
    db = None
    try:
        db = get_db_session()
        query = db.query(TikTokMetrics)

        # Apply filters
        if video_id:
            query = query.filter(TikTokMetrics.video_id == video_id)
        if start_date:
            query = query.filter(TikTokMetrics.recorded_at >= start_date)
        if end_date:
            query = query.filter(TikTokMetrics.recorded_at <= end_date)

        metrics = query.all()

        # Calculate summary
        unique_videos = set(m.video_id for m in metrics)
        total_views = sum(m.views for m in metrics)
        total_engagement = sum(
            m.likes + m.comments + m.shares + m.saves for m in metrics
        )
        total_shop_clicks = sum(m.shop_clicks for m in metrics)

        engagement_rates = [m.engagement_rate for m in metrics if m.engagement_rate is not None]
        avg_engagement_rate = (
            sum(engagement_rates) / len(engagement_rates)
            if engagement_rates else 0
        )

        return {
            "total_videos": len(unique_videos),
            "total_views": total_views,
            "total_engagement": total_engagement,
            "total_shop_clicks": total_shop_clicks,
            "avg_engagement_rate": avg_engagement_rate,
        }

    except Exception as e:
        return {
            "error": f"Failed to get metrics summary: {str(e)}"
        }

    finally:
        if db:
            db.close()
