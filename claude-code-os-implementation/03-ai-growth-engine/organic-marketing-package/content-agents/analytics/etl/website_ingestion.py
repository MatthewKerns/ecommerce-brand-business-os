"""
Website analytics ETL pipeline for ingesting GA4 or website analytics data into the data warehouse.

This module provides functionality to fetch website analytics data and store it
in the unified analytics database for cross-channel attribution and analysis.
"""
import os
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.connection import get_db_session
from analytics.models import WebsiteAnalytics


def ingest_website_analytics(
    analytics_data: Optional[List[Dict[str, Any]]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    api_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Ingest website analytics data into the data warehouse.

    This function fetches website analytics data (GA4 or equivalent) and stores it
    in the database. It can accept pre-fetched data or fetch from analytics API directly.

    Args:
        analytics_data: Optional pre-fetched analytics data
        start_date: Start date for fetching metrics (defaults to 7 days ago)
        end_date: End date for fetching metrics (defaults to today)
        api_client: Optional GA4/analytics API client for fetching data

    Returns:
        Dict with ingestion results:
            - success: Whether ingestion succeeded
            - records_processed: Number of records processed
            - records_inserted: Number of new records inserted
            - records_updated: Number of existing records updated
            - errors: List of error messages if any

    Example:
        >>> result = ingest_website_analytics()
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
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    db = None
    try:
        # Get database session
        db = get_db_session()

        # Fetch data from API if not provided
        if analytics_data is None:
            if api_client is not None:
                analytics_data = _fetch_from_api(api_client, start_date, end_date)
            else:
                # If no data and no API client, return with warning
                result["errors"].append(
                    "No analytics data provided and no API client available. "
                    "Please provide either analytics_data or api_client parameter."
                )
                return result

        # Process each analytics record
        for analytics_record in analytics_data:
            try:
                # Check if record already exists
                # Uniqueness based on: date + page_path + session_id (or just date + page_path if session_id is null)
                existing_record = db.query(WebsiteAnalytics).filter(
                    WebsiteAnalytics.date == analytics_record.get("date"),
                    WebsiteAnalytics.page_path == analytics_record.get("page_path"),
                    WebsiteAnalytics.session_id == analytics_record.get("session_id")
                ).first()

                if existing_record:
                    # Update existing record
                    _update_record(existing_record, analytics_record)
                    result["records_updated"] += 1
                else:
                    # Create new record
                    new_record = _create_record(analytics_record)
                    db.add(new_record)
                    result["records_inserted"] += 1

                result["records_processed"] += 1

            except Exception as e:
                result["errors"].append(
                    f"Error processing analytics for page {analytics_record.get('page_path', 'unknown')} "
                    f"on {analytics_record.get('date', 'unknown')}: {str(e)}"
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
    start_date: date,
    end_date: date
) -> List[Dict[str, Any]]:
    """
    Fetch website analytics from GA4 or analytics API.

    Args:
        api_client: GA4/analytics API client instance
        start_date: Start date for metrics
        end_date: End date for metrics

    Returns:
        List of analytics data dictionaries

    Note:
        This is a placeholder for actual API integration.
        Implement actual API calls based on GA4 or analytics platform.
    """
    # This would integrate with GA4 API or similar analytics platform
    # For now, return empty list as placeholder
    try:
        # Example integration point for GA4:
        # from google.analytics.data_v1beta import BetaAnalyticsDataClient
        # from google.analytics.data_v1beta.types import (
        #     RunReportRequest,
        #     DateRange,
        #     Dimension,
        #     Metric,
        # )
        #
        # response = api_client.run_report(
        #     property=f"properties/{property_id}",
        #     date_ranges=[DateRange(start_date=start_date.isoformat(), end_date=end_date.isoformat())],
        #     dimensions=[
        #         Dimension(name="pagePath"),
        #         Dimension(name="pageTitle"),
        #         Dimension(name="sessionSource"),
        #         Dimension(name="sessionMedium"),
        #         Dimension(name="deviceCategory"),
        #         Dimension(name="country"),
        #     ],
        #     metrics=[
        #         Metric(name="sessions"),
        #         Metric(name="screenPageViews"),
        #         Metric(name="activeUsers"),
        #         Metric(name="newUsers"),
        #         Metric(name="bounceRate"),
        #         Metric(name="averageSessionDuration"),
        #         Metric(name="conversions"),
        #         Metric(name="totalRevenue"),
        #     ],
        # )
        # return _transform_ga4_response(response)
        return []
    except Exception as e:
        raise Exception(f"Failed to fetch data from website analytics API: {str(e)}")


def _create_record(analytics_data: Dict[str, Any]) -> WebsiteAnalytics:
    """
    Create a new WebsiteAnalytics record from analytics data.

    Args:
        analytics_data: Dictionary containing website analytics metrics

    Returns:
        WebsiteAnalytics: New database record
    """
    return WebsiteAnalytics(
        date=analytics_data.get("date", date.today()),
        session_id=analytics_data.get("session_id"),
        page_path=analytics_data.get("page_path"),
        page_title=analytics_data.get("page_title"),
        sessions=analytics_data.get("sessions", 0),
        pageviews=analytics_data.get("pageviews", 0),
        unique_pageviews=analytics_data.get("unique_pageviews", 0),
        avg_time_on_page_seconds=analytics_data.get("avg_time_on_page_seconds"),
        bounce_rate=analytics_data.get("bounce_rate"),
        exit_rate=analytics_data.get("exit_rate"),
        users=analytics_data.get("users", 0),
        new_users=analytics_data.get("new_users", 0),
        traffic_source=analytics_data.get("traffic_source"),
        traffic_medium=analytics_data.get("traffic_medium"),
        traffic_campaign=analytics_data.get("traffic_campaign"),
        device_category=analytics_data.get("device_category"),
        country=analytics_data.get("country"),
        conversions=analytics_data.get("conversions", 0),
        conversion_rate=analytics_data.get("conversion_rate"),
        revenue=analytics_data.get("revenue"),
    )


def _update_record(
    existing_record: WebsiteAnalytics,
    analytics_data: Dict[str, Any]
) -> None:
    """
    Update an existing WebsiteAnalytics record with new data.

    Args:
        existing_record: Existing database record
        analytics_data: Dictionary containing updated metrics
    """
    # Update metrics that may have changed
    existing_record.page_title = analytics_data.get("page_title", existing_record.page_title)
    existing_record.sessions = analytics_data.get("sessions", existing_record.sessions)
    existing_record.pageviews = analytics_data.get("pageviews", existing_record.pageviews)
    existing_record.unique_pageviews = analytics_data.get(
        "unique_pageviews", existing_record.unique_pageviews
    )
    existing_record.avg_time_on_page_seconds = analytics_data.get(
        "avg_time_on_page_seconds", existing_record.avg_time_on_page_seconds
    )
    existing_record.bounce_rate = analytics_data.get("bounce_rate", existing_record.bounce_rate)
    existing_record.exit_rate = analytics_data.get("exit_rate", existing_record.exit_rate)
    existing_record.users = analytics_data.get("users", existing_record.users)
    existing_record.new_users = analytics_data.get("new_users", existing_record.new_users)
    existing_record.traffic_source = analytics_data.get("traffic_source", existing_record.traffic_source)
    existing_record.traffic_medium = analytics_data.get("traffic_medium", existing_record.traffic_medium)
    existing_record.traffic_campaign = analytics_data.get("traffic_campaign", existing_record.traffic_campaign)
    existing_record.device_category = analytics_data.get("device_category", existing_record.device_category)
    existing_record.country = analytics_data.get("country", existing_record.country)
    existing_record.conversions = analytics_data.get("conversions", existing_record.conversions)
    existing_record.conversion_rate = analytics_data.get("conversion_rate", existing_record.conversion_rate)
    existing_record.revenue = analytics_data.get("revenue", existing_record.revenue)
    existing_record.updated_at = datetime.utcnow()


def get_analytics_summary(
    page_path: Optional[str] = None,
    traffic_source: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Get summary statistics for website analytics.

    Args:
        page_path: Optional specific page path to filter by
        traffic_source: Optional traffic source to filter by
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Dict with summary statistics:
            - total_sessions: Total sessions
            - total_pageviews: Total pageviews
            - total_users: Total users
            - total_conversions: Total conversions
            - total_revenue: Total revenue
            - avg_bounce_rate: Average bounce rate
            - avg_conversion_rate: Average conversion rate

    Example:
        >>> summary = get_analytics_summary(traffic_source="organic")
        >>> print(f"Total sessions: {summary['total_sessions']}")
    """
    db = None
    try:
        db = get_db_session()
        query = db.query(WebsiteAnalytics)

        # Apply filters
        if page_path:
            query = query.filter(WebsiteAnalytics.page_path == page_path)
        if traffic_source:
            query = query.filter(WebsiteAnalytics.traffic_source == traffic_source)
        if start_date:
            query = query.filter(WebsiteAnalytics.date >= start_date)
        if end_date:
            query = query.filter(WebsiteAnalytics.date <= end_date)

        analytics = query.all()

        # Calculate summary
        total_sessions = sum(a.sessions for a in analytics)
        total_pageviews = sum(a.pageviews for a in analytics)
        total_users = sum(a.users for a in analytics)
        total_conversions = sum(a.conversions for a in analytics)
        total_revenue = sum(a.revenue for a in analytics if a.revenue is not None)

        bounce_rates = [a.bounce_rate for a in analytics if a.bounce_rate is not None]
        avg_bounce_rate = (
            sum(bounce_rates) / len(bounce_rates)
            if bounce_rates else 0
        )

        conversion_rates = [a.conversion_rate for a in analytics if a.conversion_rate is not None]
        avg_conversion_rate = (
            sum(conversion_rates) / len(conversion_rates)
            if conversion_rates else 0
        )

        return {
            "total_sessions": total_sessions,
            "total_pageviews": total_pageviews,
            "total_users": total_users,
            "total_conversions": total_conversions,
            "total_revenue": float(total_revenue) if total_revenue else 0,
            "avg_bounce_rate": float(avg_bounce_rate) if avg_bounce_rate else 0,
            "avg_conversion_rate": float(avg_conversion_rate) if avg_conversion_rate else 0,
        }

    except Exception as e:
        return {
            "error": f"Failed to get analytics summary: {str(e)}"
        }

    finally:
        if db:
            db.close()
