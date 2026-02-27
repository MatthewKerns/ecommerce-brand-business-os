"""
Email ETL pipeline for ingesting email campaign metrics into the data warehouse.

This module provides functionality to fetch email marketing analytics data and store it
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
from analytics.models import EmailMetrics


def ingest_email_metrics(
    campaign_data: Optional[List[Dict[str, Any]]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    api_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Ingest email campaign metrics into the data warehouse.

    This function fetches email marketing analytics data and stores it in the database.
    It can accept pre-fetched data or fetch from Klaviyo/email platform API directly.

    Args:
        campaign_data: Optional pre-fetched campaign metrics data
        start_date: Start date for fetching metrics (defaults to 30 days ago)
        end_date: End date for fetching metrics (defaults to now)
        api_client: Optional Klaviyo/email platform API client for fetching data

    Returns:
        Dict with ingestion results:
            - success: Whether ingestion succeeded
            - records_processed: Number of records processed
            - records_inserted: Number of new records inserted
            - records_updated: Number of existing records updated
            - errors: List of error messages if any

    Example:
        >>> result = ingest_email_metrics()
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
        start_date = end_date - timedelta(days=30)

    db = None
    try:
        # Get database session
        db = get_db_session()

        # Fetch data from API if not provided
        if campaign_data is None:
            if api_client is not None:
                campaign_data = _fetch_from_api(api_client, start_date, end_date)
            else:
                # If no data and no API client, return with warning
                result["errors"].append(
                    "No campaign data provided and no API client available. "
                    "Please provide either campaign_data or api_client parameter."
                )
                return result

        # Process each campaign's metrics
        for campaign_record in campaign_data:
            try:
                # Check if record already exists (by campaign_id - unique constraint)
                existing_record = db.query(EmailMetrics).filter(
                    EmailMetrics.campaign_id == campaign_record.get("campaign_id")
                ).first()

                if existing_record:
                    # Update existing record
                    _update_record(existing_record, campaign_record)
                    result["records_updated"] += 1
                else:
                    # Create new record
                    new_record = _create_record(campaign_record)
                    db.add(new_record)
                    result["records_inserted"] += 1

                result["records_processed"] += 1

            except Exception as e:
                result["errors"].append(
                    f"Error processing campaign {campaign_record.get('campaign_id', 'unknown')}: {str(e)}"
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
    Fetch campaign metrics from Klaviyo or email platform API.

    Args:
        api_client: Klaviyo/email platform API client instance
        start_date: Start date for metrics
        end_date: End date for metrics

    Returns:
        List of campaign metric dictionaries

    Note:
        This is a placeholder for actual API integration.
        Implement actual API calls based on Klaviyo or chosen email platform.
    """
    # This would integrate with Klaviyo API or other email platform
    # For now, return empty list as placeholder
    try:
        # Example integration point for Klaviyo:
        # campaigns = api_client.Campaigns.get_campaigns(
        #     filter={
        #         'greater-than(send_time,{})'.format(start_date.isoformat()),
        #         'less-than(send_time,{})'.format(end_date.isoformat())
        #     }
        # )
        # campaign_metrics = []
        # for campaign in campaigns:
        #     metrics = api_client.Campaigns.get_campaign_metrics(campaign['id'])
        #     campaign_metrics.append({
        #         'campaign_id': campaign['id'],
        #         'campaign_name': campaign['name'],
        #         'send_date': campaign['send_time'],
        #         'subject_line': campaign['subject_line'],
        #         'from_name': campaign['from_name'],
        #         'from_email': campaign['from_email'],
        #         'emails_sent': metrics['emails_sent'],
        #         'emails_delivered': metrics['emails_delivered'],
        #         'opens': metrics['opens'],
        #         'unique_opens': metrics['unique_opens'],
        #         'clicks': metrics['clicks'],
        #         'unique_clicks': metrics['unique_clicks'],
        #         # ... other metrics
        #     })
        # return campaign_metrics
        return []
    except Exception as e:
        raise Exception(f"Failed to fetch data from email platform API: {str(e)}")


def _create_record(campaign_data: Dict[str, Any]) -> EmailMetrics:
    """
    Create a new EmailMetrics record from campaign data.

    Args:
        campaign_data: Dictionary containing campaign metrics

    Returns:
        EmailMetrics: New database record
    """
    return EmailMetrics(
        campaign_id=campaign_data.get("campaign_id"),
        campaign_name=campaign_data.get("campaign_name"),
        send_date=campaign_data.get("send_date", datetime.utcnow()),
        list_id=campaign_data.get("list_id"),
        list_name=campaign_data.get("list_name"),
        subject_line=campaign_data.get("subject_line"),
        from_name=campaign_data.get("from_name"),
        from_email=campaign_data.get("from_email"),
        emails_sent=campaign_data.get("emails_sent", 0),
        emails_delivered=campaign_data.get("emails_delivered", 0),
        emails_bounced=campaign_data.get("emails_bounced", 0),
        hard_bounces=campaign_data.get("hard_bounces", 0),
        soft_bounces=campaign_data.get("soft_bounces", 0),
        opens=campaign_data.get("opens", 0),
        unique_opens=campaign_data.get("unique_opens", 0),
        open_rate=campaign_data.get("open_rate"),
        clicks=campaign_data.get("clicks", 0),
        unique_clicks=campaign_data.get("unique_clicks", 0),
        click_rate=campaign_data.get("click_rate"),
        click_to_open_rate=campaign_data.get("click_to_open_rate"),
        unsubscribes=campaign_data.get("unsubscribes", 0),
        unsubscribe_rate=campaign_data.get("unsubscribe_rate"),
        spam_reports=campaign_data.get("spam_reports", 0),
        conversions=campaign_data.get("conversions", 0),
        conversion_rate=campaign_data.get("conversion_rate"),
        revenue=campaign_data.get("revenue"),
    )


def _update_record(
    existing_record: EmailMetrics,
    campaign_data: Dict[str, Any]
) -> None:
    """
    Update an existing EmailMetrics record with new data.

    Args:
        existing_record: Existing database record to update
        campaign_data: Dictionary containing updated campaign metrics
    """
    # Update campaign metadata (in case name or details changed)
    if campaign_data.get("campaign_name") is not None:
        existing_record.campaign_name = campaign_data["campaign_name"]
    if campaign_data.get("list_id") is not None:
        existing_record.list_id = campaign_data["list_id"]
    if campaign_data.get("list_name") is not None:
        existing_record.list_name = campaign_data["list_name"]
    if campaign_data.get("subject_line") is not None:
        existing_record.subject_line = campaign_data["subject_line"]
    if campaign_data.get("from_name") is not None:
        existing_record.from_name = campaign_data["from_name"]
    if campaign_data.get("from_email") is not None:
        existing_record.from_email = campaign_data["from_email"]

    # Update delivery metrics
    if campaign_data.get("emails_sent") is not None:
        existing_record.emails_sent = campaign_data["emails_sent"]
    if campaign_data.get("emails_delivered") is not None:
        existing_record.emails_delivered = campaign_data["emails_delivered"]
    if campaign_data.get("emails_bounced") is not None:
        existing_record.emails_bounced = campaign_data["emails_bounced"]
    if campaign_data.get("hard_bounces") is not None:
        existing_record.hard_bounces = campaign_data["hard_bounces"]
    if campaign_data.get("soft_bounces") is not None:
        existing_record.soft_bounces = campaign_data["soft_bounces"]

    # Update engagement metrics
    if campaign_data.get("opens") is not None:
        existing_record.opens = campaign_data["opens"]
    if campaign_data.get("unique_opens") is not None:
        existing_record.unique_opens = campaign_data["unique_opens"]
    if campaign_data.get("open_rate") is not None:
        existing_record.open_rate = campaign_data["open_rate"]
    if campaign_data.get("clicks") is not None:
        existing_record.clicks = campaign_data["clicks"]
    if campaign_data.get("unique_clicks") is not None:
        existing_record.unique_clicks = campaign_data["unique_clicks"]
    if campaign_data.get("click_rate") is not None:
        existing_record.click_rate = campaign_data["click_rate"]
    if campaign_data.get("click_to_open_rate") is not None:
        existing_record.click_to_open_rate = campaign_data["click_to_open_rate"]

    # Update negative metrics
    if campaign_data.get("unsubscribes") is not None:
        existing_record.unsubscribes = campaign_data["unsubscribes"]
    if campaign_data.get("unsubscribe_rate") is not None:
        existing_record.unsubscribe_rate = campaign_data["unsubscribe_rate"]
    if campaign_data.get("spam_reports") is not None:
        existing_record.spam_reports = campaign_data["spam_reports"]

    # Update conversion metrics
    if campaign_data.get("conversions") is not None:
        existing_record.conversions = campaign_data["conversions"]
    if campaign_data.get("conversion_rate") is not None:
        existing_record.conversion_rate = campaign_data["conversion_rate"]
    if campaign_data.get("revenue") is not None:
        existing_record.revenue = campaign_data["revenue"]

    # Updated_at is handled automatically by SQLAlchemy


def get_metrics_summary(
    db: Any,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    list_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get summary statistics for email campaigns.

    Args:
        db: Database session
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        list_id: Optional list ID for filtering

    Returns:
        Dict containing summary statistics:
            - total_campaigns: Total number of campaigns
            - total_emails_sent: Total emails sent
            - avg_open_rate: Average open rate
            - avg_click_rate: Average click rate
            - avg_conversion_rate: Average conversion rate
            - total_revenue: Total revenue from emails

    Example:
        >>> db = get_db_session()
        >>> summary = get_metrics_summary(db, list_id="primary_list")
        >>> print(f"Average open rate: {summary['avg_open_rate']}%")
    """
    query = db.query(EmailMetrics)

    # Apply filters
    if start_date:
        query = query.filter(EmailMetrics.send_date >= start_date)
    if end_date:
        query = query.filter(EmailMetrics.send_date <= end_date)
    if list_id:
        query = query.filter(EmailMetrics.list_id == list_id)

    campaigns = query.all()

    if not campaigns:
        return {
            "total_campaigns": 0,
            "total_emails_sent": 0,
            "avg_open_rate": 0,
            "avg_click_rate": 0,
            "avg_conversion_rate": 0,
            "total_revenue": 0
        }

    total_emails_sent = sum(c.emails_sent for c in campaigns)

    # Calculate weighted averages (weighted by emails sent)
    total_opens_weight = sum(
        (c.open_rate or 0) * c.emails_sent for c in campaigns if c.open_rate is not None
    )
    total_clicks_weight = sum(
        (c.click_rate or 0) * c.emails_sent for c in campaigns if c.click_rate is not None
    )
    total_conversion_weight = sum(
        (c.conversion_rate or 0) * c.emails_sent for c in campaigns if c.conversion_rate is not None
    )

    avg_open_rate = total_opens_weight / total_emails_sent if total_emails_sent > 0 else 0
    avg_click_rate = total_clicks_weight / total_emails_sent if total_emails_sent > 0 else 0
    avg_conversion_rate = total_conversion_weight / total_emails_sent if total_emails_sent > 0 else 0

    total_revenue = sum(c.revenue or 0 for c in campaigns)

    return {
        "total_campaigns": len(campaigns),
        "total_emails_sent": total_emails_sent,
        "avg_open_rate": round(float(avg_open_rate), 2),
        "avg_click_rate": round(float(avg_click_rate), 2),
        "avg_conversion_rate": round(float(avg_conversion_rate), 2),
        "total_revenue": round(float(total_revenue), 2)
    }
