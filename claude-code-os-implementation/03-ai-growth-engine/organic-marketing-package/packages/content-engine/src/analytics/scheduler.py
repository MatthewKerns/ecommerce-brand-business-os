"""
Analytics data pipeline scheduler for orchestrating all ETL processes.

This module provides functionality to run and schedule all analytics data
ingestion pipelines (TikTok, website, email, sales) in a coordinated manner.
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from analytics.etl import (
    ingest_tiktok_metrics,
    ingest_website_analytics,
    ingest_email_metrics,
    ingest_sales_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_daily_refresh(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    channels: Optional[List[str]] = None,
    api_clients: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run daily refresh of all analytics data pipelines.

    This function orchestrates all ETL pipelines to ingest data from TikTok,
    website, email, and sales channels into the unified data warehouse.

    Args:
        start_date: Start date for data refresh (defaults to yesterday)
        end_date: End date for data refresh (defaults to now)
        channels: List of channels to refresh (defaults to all: ['tiktok', 'website', 'email', 'sales'])
        api_clients: Optional dict of API clients for each channel
            Example: {
                'tiktok': tiktok_api_client,
                'website': ga4_client,
                'email': klaviyo_client,
                'sales': {'tiktok_shop': ts_client, 'website': shopify_client}
            }

    Returns:
        Dict with overall refresh results:
            - success: Whether all pipelines succeeded
            - timestamp: When refresh was run
            - duration_seconds: Total execution time
            - channels_processed: List of channels that were processed
            - results: Dict with individual pipeline results
            - summary: Aggregated statistics
            - errors: List of error messages if any

    Example:
        >>> # Run daily refresh for all channels
        >>> result = run_daily_refresh()
        >>> if result['success']:
        ...     print(f"Refreshed {result['summary']['total_records']} records")

        >>> # Run refresh for specific channels
        >>> result = run_daily_refresh(channels=['tiktok', 'sales'])

        >>> # Run refresh with custom date range
        >>> start = datetime(2024, 1, 1)
        >>> end = datetime(2024, 1, 31)
        >>> result = run_daily_refresh(start_date=start, end_date=end)
    """
    start_time = datetime.utcnow()

    result = {
        "success": False,
        "timestamp": start_time.isoformat(),
        "duration_seconds": 0,
        "channels_processed": [],
        "results": {},
        "summary": {
            "total_records_processed": 0,
            "total_records_inserted": 0,
            "total_records_updated": 0,
            "total_revenue": 0.0,
        },
        "errors": []
    }

    # Set default date range if not provided
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        # Default to yesterday for daily refresh
        start_date = end_date - timedelta(days=1)

    # Set default channels if not provided
    if channels is None:
        channels = ['tiktok', 'website', 'email', 'sales']

    # Initialize API clients dict if not provided
    if api_clients is None:
        api_clients = {}

    logger.info(f"Starting daily refresh for channels: {channels}")
    logger.info(f"Date range: {start_date.isoformat()} to {end_date.isoformat()}")

    # Run TikTok ingestion
    if 'tiktok' in channels:
        try:
            logger.info("Running TikTok metrics ingestion...")
            tiktok_result = ingest_tiktok_metrics(
                start_date=start_date,
                end_date=end_date,
                api_client=api_clients.get('tiktok')
            )
            result["results"]["tiktok"] = tiktok_result
            result["channels_processed"].append("tiktok")

            # Update summary
            result["summary"]["total_records_processed"] += tiktok_result.get("records_processed", 0)
            result["summary"]["total_records_inserted"] += tiktok_result.get("records_inserted", 0)
            result["summary"]["total_records_updated"] += tiktok_result.get("records_updated", 0)

            if not tiktok_result.get("success"):
                result["errors"].extend([f"TikTok: {err}" for err in tiktok_result.get("errors", [])])

            logger.info(f"TikTok ingestion completed: {tiktok_result.get('records_processed', 0)} records")

        except Exception as e:
            error_msg = f"TikTok ingestion failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["results"]["tiktok"] = {"success": False, "error": str(e)}

    # Run website analytics ingestion
    if 'website' in channels:
        try:
            logger.info("Running website analytics ingestion...")
            website_result = ingest_website_analytics(
                start_date=start_date,
                end_date=end_date,
                api_client=api_clients.get('website')
            )
            result["results"]["website"] = website_result
            result["channels_processed"].append("website")

            # Update summary
            result["summary"]["total_records_processed"] += website_result.get("records_processed", 0)
            result["summary"]["total_records_inserted"] += website_result.get("records_inserted", 0)
            result["summary"]["total_records_updated"] += website_result.get("records_updated", 0)

            if not website_result.get("success"):
                result["errors"].extend([f"Website: {err}" for err in website_result.get("errors", [])])

            logger.info(f"Website ingestion completed: {website_result.get('records_processed', 0)} records")

        except Exception as e:
            error_msg = f"Website ingestion failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["results"]["website"] = {"success": False, "error": str(e)}

    # Run email metrics ingestion
    if 'email' in channels:
        try:
            logger.info("Running email metrics ingestion...")
            email_result = ingest_email_metrics(
                start_date=start_date,
                end_date=end_date,
                api_client=api_clients.get('email')
            )
            result["results"]["email"] = email_result
            result["channels_processed"].append("email")

            # Update summary
            result["summary"]["total_records_processed"] += email_result.get("records_processed", 0)
            result["summary"]["total_records_inserted"] += email_result.get("records_inserted", 0)
            result["summary"]["total_records_updated"] += email_result.get("records_updated", 0)

            if not email_result.get("success"):
                result["errors"].extend([f"Email: {err}" for err in email_result.get("errors", [])])

            logger.info(f"Email ingestion completed: {email_result.get('records_processed', 0)} records")

        except Exception as e:
            error_msg = f"Email ingestion failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["results"]["email"] = {"success": False, "error": str(e)}

    # Run sales data ingestion
    if 'sales' in channels:
        try:
            logger.info("Running sales data ingestion...")
            sales_result = ingest_sales_data(
                start_date=start_date,
                end_date=end_date,
                api_clients=api_clients.get('sales')
            )
            result["results"]["sales"] = sales_result
            result["channels_processed"].append("sales")

            # Update summary
            result["summary"]["total_records_processed"] += sales_result.get("records_processed", 0)
            result["summary"]["total_records_inserted"] += sales_result.get("records_inserted", 0)
            result["summary"]["total_records_updated"] += sales_result.get("records_updated", 0)
            result["summary"]["total_revenue"] += sales_result.get("total_revenue", 0.0)

            if not sales_result.get("success"):
                result["errors"].extend([f"Sales: {err}" for err in sales_result.get("errors", [])])

            logger.info(f"Sales ingestion completed: {sales_result.get('records_processed', 0)} records, "
                       f"${sales_result.get('total_revenue', 0):.2f} revenue")

        except Exception as e:
            error_msg = f"Sales ingestion failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["results"]["sales"] = {"success": False, "error": str(e)}

    # Calculate duration
    end_time = datetime.utcnow()
    result["duration_seconds"] = (end_time - start_time).total_seconds()

    # Determine overall success
    result["success"] = len(result["errors"]) == 0

    # Log final summary
    if result["success"]:
        logger.info(
            f"Daily refresh completed successfully in {result['duration_seconds']:.2f}s: "
            f"{result['summary']['total_records_processed']} records processed, "
            f"{result['summary']['total_records_inserted']} inserted, "
            f"{result['summary']['total_records_updated']} updated"
        )
    else:
        logger.error(
            f"Daily refresh completed with {len(result['errors'])} errors in {result['duration_seconds']:.2f}s"
        )

    return result


def run_incremental_refresh(
    lookback_hours: int = 24,
    channels: Optional[List[str]] = None,
    api_clients: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run incremental refresh for recent data only.

    This is useful for more frequent updates (e.g., hourly) to keep data fresh
    without reprocessing the entire history.

    Args:
        lookback_hours: How many hours to look back (default: 24)
        channels: List of channels to refresh (defaults to all)
        api_clients: Optional dict of API clients for each channel

    Returns:
        Dict with refresh results (same format as run_daily_refresh)

    Example:
        >>> # Run hourly incremental refresh
        >>> result = run_incremental_refresh(lookback_hours=1)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=lookback_hours)

    logger.info(f"Running incremental refresh for last {lookback_hours} hours")

    return run_daily_refresh(
        start_date=start_date,
        end_date=end_date,
        channels=channels,
        api_clients=api_clients
    )


def run_backfill(
    start_date: datetime,
    end_date: datetime,
    channels: Optional[List[str]] = None,
    batch_days: int = 7,
    api_clients: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run backfill for historical data in batches.

    This function processes historical data in smaller batches to avoid
    overwhelming the database or API rate limits.

    Args:
        start_date: Start date for backfill
        end_date: End date for backfill
        channels: List of channels to backfill (defaults to all)
        batch_days: Number of days to process in each batch (default: 7)
        api_clients: Optional dict of API clients for each channel

    Returns:
        Dict with backfill results:
            - success: Whether backfill succeeded
            - batches_processed: Number of batches completed
            - batch_results: List of results for each batch
            - summary: Aggregated statistics across all batches
            - errors: List of error messages if any

    Example:
        >>> # Backfill last 3 months of data
        >>> start = datetime(2024, 1, 1)
        >>> end = datetime(2024, 3, 31)
        >>> result = run_backfill(start_date=start, end_date=end)
    """
    result = {
        "success": False,
        "batches_processed": 0,
        "batch_results": [],
        "summary": {
            "total_records_processed": 0,
            "total_records_inserted": 0,
            "total_records_updated": 0,
            "total_revenue": 0.0,
        },
        "errors": []
    }

    logger.info(f"Starting backfill from {start_date.isoformat()} to {end_date.isoformat()}")
    logger.info(f"Processing in {batch_days}-day batches")

    # Process in batches
    current_start = start_date
    batch_num = 0

    while current_start < end_date:
        batch_num += 1
        current_end = min(current_start + timedelta(days=batch_days), end_date)

        logger.info(f"Processing batch {batch_num}: {current_start.isoformat()} to {current_end.isoformat()}")

        try:
            batch_result = run_daily_refresh(
                start_date=current_start,
                end_date=current_end,
                channels=channels,
                api_clients=api_clients
            )

            result["batch_results"].append({
                "batch_num": batch_num,
                "start_date": current_start.isoformat(),
                "end_date": current_end.isoformat(),
                "result": batch_result
            })

            result["batches_processed"] += 1

            # Update summary
            if batch_result.get("summary"):
                result["summary"]["total_records_processed"] += batch_result["summary"].get("total_records_processed", 0)
                result["summary"]["total_records_inserted"] += batch_result["summary"].get("total_records_inserted", 0)
                result["summary"]["total_records_updated"] += batch_result["summary"].get("total_records_updated", 0)
                result["summary"]["total_revenue"] += batch_result["summary"].get("total_revenue", 0.0)

            if not batch_result.get("success"):
                result["errors"].extend([f"Batch {batch_num}: {err}" for err in batch_result.get("errors", [])])

        except Exception as e:
            error_msg = f"Batch {batch_num} failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        # Move to next batch
        current_start = current_end

    # Determine overall success
    result["success"] = len(result["errors"]) == 0

    logger.info(
        f"Backfill completed: {result['batches_processed']} batches, "
        f"{result['summary']['total_records_processed']} total records processed"
    )

    return result


def get_refresh_status() -> Dict[str, Any]:
    """
    Get status of the most recent data refresh for each channel.

    This function queries the database to determine when each channel
    was last updated and what the data coverage is.

    Returns:
        Dict with status information for each channel:
            - channel: Channel name
            - last_update: Timestamp of most recent data
            - record_count: Total records in database
            - date_range: Earliest and latest data points
            - freshness_hours: How old the most recent data is

    Example:
        >>> status = get_refresh_status()
        >>> for channel, info in status.items():
        ...     print(f"{channel}: last updated {info['freshness_hours']} hours ago")
    """
    from database.connection import get_db_session
    from analytics.models import TikTokMetrics, WebsiteAnalytics, EmailMetrics, SalesData
    from sqlalchemy import func

    status = {}
    db = None

    try:
        db = get_db_session()

        # Check TikTok metrics
        tiktok_stats = db.query(
            func.count(TikTokMetrics.id).label('count'),
            func.max(TikTokMetrics.recorded_at).label('latest'),
            func.min(TikTokMetrics.recorded_at).label('earliest')
        ).first()

        if tiktok_stats and tiktok_stats.count > 0:
            freshness = (datetime.utcnow() - tiktok_stats.latest).total_seconds() / 3600 if tiktok_stats.latest else None
            status['tiktok'] = {
                'record_count': tiktok_stats.count,
                'last_update': tiktok_stats.latest.isoformat() if tiktok_stats.latest else None,
                'date_range': {
                    'earliest': tiktok_stats.earliest.isoformat() if tiktok_stats.earliest else None,
                    'latest': tiktok_stats.latest.isoformat() if tiktok_stats.latest else None
                },
                'freshness_hours': round(freshness, 2) if freshness else None
            }

        # Check website analytics
        website_stats = db.query(
            func.count(WebsiteAnalytics.id).label('count'),
            func.max(WebsiteAnalytics.date).label('latest'),
            func.min(WebsiteAnalytics.date).label('earliest')
        ).first()

        if website_stats and website_stats.count > 0:
            freshness = (datetime.utcnow() - datetime.combine(website_stats.latest, datetime.min.time())).total_seconds() / 3600 if website_stats.latest else None
            status['website'] = {
                'record_count': website_stats.count,
                'last_update': website_stats.latest.isoformat() if website_stats.latest else None,
                'date_range': {
                    'earliest': website_stats.earliest.isoformat() if website_stats.earliest else None,
                    'latest': website_stats.latest.isoformat() if website_stats.latest else None
                },
                'freshness_hours': round(freshness, 2) if freshness else None
            }

        # Check email metrics
        email_stats = db.query(
            func.count(EmailMetrics.id).label('count'),
            func.max(EmailMetrics.sent_at).label('latest'),
            func.min(EmailMetrics.sent_at).label('earliest')
        ).first()

        if email_stats and email_stats.count > 0:
            freshness = (datetime.utcnow() - email_stats.latest).total_seconds() / 3600 if email_stats.latest else None
            status['email'] = {
                'record_count': email_stats.count,
                'last_update': email_stats.latest.isoformat() if email_stats.latest else None,
                'date_range': {
                    'earliest': email_stats.earliest.isoformat() if email_stats.earliest else None,
                    'latest': email_stats.latest.isoformat() if email_stats.latest else None
                },
                'freshness_hours': round(freshness, 2) if freshness else None
            }

        # Check sales data
        sales_stats = db.query(
            func.count(SalesData.id).label('count'),
            func.max(SalesData.order_date).label('latest'),
            func.min(SalesData.order_date).label('earliest')
        ).first()

        if sales_stats and sales_stats.count > 0:
            freshness = (datetime.utcnow() - sales_stats.latest).total_seconds() / 3600 if sales_stats.latest else None
            status['sales'] = {
                'record_count': sales_stats.count,
                'last_update': sales_stats.latest.isoformat() if sales_stats.latest else None,
                'date_range': {
                    'earliest': sales_stats.earliest.isoformat() if sales_stats.earliest else None,
                    'latest': sales_stats.latest.isoformat() if sales_stats.latest else None
                },
                'freshness_hours': round(freshness, 2) if freshness else None
            }

    except Exception as e:
        logger.error(f"Error getting refresh status: {str(e)}")
        status['error'] = str(e)

    finally:
        if db:
            db.close()

    return status


if __name__ == "__main__":
    """
    Run scheduler from command line.

    Usage:
        python scheduler.py                    # Run daily refresh
        python scheduler.py --incremental      # Run incremental (last 24h)
        python scheduler.py --status           # Show refresh status
        python scheduler.py --backfill START END  # Backfill date range

    Examples:
        python scheduler.py
        python scheduler.py --incremental --hours 6
        python scheduler.py --backfill 2024-01-01 2024-01-31
    """
    import argparse

    parser = argparse.ArgumentParser(description='Analytics data pipeline scheduler')
    parser.add_argument('--incremental', action='store_true', help='Run incremental refresh')
    parser.add_argument('--hours', type=int, default=24, help='Lookback hours for incremental')
    parser.add_argument('--status', action='store_true', help='Show refresh status')
    parser.add_argument('--backfill', nargs=2, metavar=('START', 'END'), help='Backfill date range (YYYY-MM-DD)')
    parser.add_argument('--channels', nargs='+', choices=['tiktok', 'website', 'email', 'sales'],
                       help='Specific channels to refresh')

    args = parser.parse_args()

    if args.status:
        # Show status
        status = get_refresh_status()
        print("\n=== Analytics Data Refresh Status ===\n")
        for channel, info in status.items():
            if channel == 'error':
                print(f"Error: {info}")
            else:
                print(f"{channel.upper()}:")
                print(f"  Records: {info.get('record_count', 0):,}")
                print(f"  Last Update: {info.get('last_update', 'N/A')}")
                print(f"  Freshness: {info.get('freshness_hours', 'N/A')} hours ago")
                print()

    elif args.backfill:
        # Run backfill
        start = datetime.fromisoformat(args.backfill[0])
        end = datetime.fromisoformat(args.backfill[1])
        result = run_backfill(start_date=start, end_date=end, channels=args.channels)

        print(f"\n=== Backfill Results ===")
        print(f"Success: {result['success']}")
        print(f"Batches: {result['batches_processed']}")
        print(f"Records Processed: {result['summary']['total_records_processed']:,}")
        print(f"Records Inserted: {result['summary']['total_records_inserted']:,}")
        print(f"Records Updated: {result['summary']['total_records_updated']:,}")
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")

    elif args.incremental:
        # Run incremental refresh
        result = run_incremental_refresh(lookback_hours=args.hours, channels=args.channels)

        print(f"\n=== Incremental Refresh Results ===")
        print(f"Success: {result['success']}")
        print(f"Duration: {result['duration_seconds']:.2f}s")
        print(f"Channels: {', '.join(result['channels_processed'])}")
        print(f"Records Processed: {result['summary']['total_records_processed']:,}")
        print(f"Records Inserted: {result['summary']['total_records_inserted']:,}")
        print(f"Records Updated: {result['summary']['total_records_updated']:,}")
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")

    else:
        # Run daily refresh (default)
        result = run_daily_refresh(channels=args.channels)

        print(f"\n=== Daily Refresh Results ===")
        print(f"Success: {result['success']}")
        print(f"Duration: {result['duration_seconds']:.2f}s")
        print(f"Channels: {', '.join(result['channels_processed'])}")
        print(f"Records Processed: {result['summary']['total_records_processed']:,}")
        print(f"Records Inserted: {result['summary']['total_records_inserted']:,}")
        print(f"Records Updated: {result['summary']['total_records_updated']:,}")
        print(f"Total Revenue: ${result['summary']['total_revenue']:,.2f}")
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
