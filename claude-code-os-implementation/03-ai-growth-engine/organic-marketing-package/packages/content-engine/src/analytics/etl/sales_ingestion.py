"""
Sales data ETL pipeline for ingesting order data from all channels into the data warehouse.

This module provides functionality to fetch sales data from TikTok Shop, website, and other
channels, storing it in the unified analytics database for cross-channel attribution and
revenue analysis.
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
from analytics.models import SalesData


def ingest_sales_data(
    order_data: Optional[List[Dict[str, Any]]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    channel: Optional[str] = None,
    api_clients: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Ingest sales order data from all channels into the data warehouse.

    This function fetches order data from TikTok Shop, website, and other channels,
    storing it in a unified sales database. It can accept pre-fetched data or fetch
    from multiple channel APIs.

    Args:
        order_data: Optional pre-fetched order data (list of order dictionaries)
        start_date: Start date for fetching orders (defaults to 30 days ago)
        end_date: End date for fetching orders (defaults to now)
        channel: Optional channel filter ('tiktok_shop', 'website', 'amazon', 'other')
        api_clients: Optional dict of API clients by channel name
            Example: {'tiktok_shop': tiktok_client, 'website': shopify_client}

    Returns:
        Dict with ingestion results:
            - success: Whether ingestion succeeded
            - records_processed: Number of records processed
            - records_inserted: Number of new records inserted
            - records_updated: Number of existing records updated
            - total_revenue: Sum of all order totals processed
            - errors: List of error messages if any

    Example:
        >>> # Ingest pre-fetched data
        >>> orders = [{'order_id': 'TS123', 'channel': 'tiktok_shop', ...}]
        >>> result = ingest_sales_data(order_data=orders)
        >>> print(f"Processed {result['records_processed']} orders")

        >>> # Fetch from API clients
        >>> clients = {'tiktok_shop': tiktok_client, 'website': shopify_client}
        >>> result = ingest_sales_data(api_clients=clients)
        >>> print(f"Total revenue: ${result['total_revenue']}")
    """
    result = {
        "success": False,
        "records_processed": 0,
        "records_inserted": 0,
        "records_updated": 0,
        "total_revenue": 0.0,
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
        if order_data is None:
            if api_clients is not None:
                order_data = _fetch_from_apis(
                    api_clients, start_date, end_date, channel
                )
            else:
                # If no data and no API clients, return with warning
                result["errors"].append(
                    "No order data provided and no API clients available. "
                    "Please provide either order_data or api_clients parameter."
                )
                return result

        # Filter by channel if specified
        if channel and order_data:
            order_data = [
                order for order in order_data
                if order.get("channel") == channel
            ]

        # Process each order
        for order_record in order_data:
            try:
                # Validate channel
                order_channel = order_record.get("channel")
                if order_channel not in ["tiktok_shop", "website", "amazon", "other"]:
                    result["errors"].append(
                        f"Invalid channel '{order_channel}' for order "
                        f"{order_record.get('order_id', 'unknown')}. "
                        "Must be one of: tiktok_shop, website, amazon, other"
                    )
                    continue

                # Check if record already exists (by order_id)
                existing_record = db.query(SalesData).filter(
                    SalesData.order_id == order_record.get("order_id")
                ).first()

                if existing_record:
                    # Update existing record (e.g., status changes, refunds)
                    _update_record(existing_record, order_record)
                    result["records_updated"] += 1
                else:
                    # Create new record
                    new_record = _create_record(order_record)
                    db.add(new_record)
                    result["records_inserted"] += 1

                # Track total revenue
                order_total = float(order_record.get("total", 0))
                result["total_revenue"] += order_total
                result["records_processed"] += 1

            except Exception as e:
                result["errors"].append(
                    f"Error processing order {order_record.get('order_id', 'unknown')}: {str(e)}"
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


def _fetch_from_apis(
    api_clients: Dict[str, Any],
    start_date: datetime,
    end_date: datetime,
    channel_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch order data from multiple channel APIs.

    Args:
        api_clients: Dict of API clients by channel name
        start_date: Start date for orders
        end_date: End date for orders
        channel_filter: Optional channel to filter to

    Returns:
        List of order dictionaries from all channels

    Note:
        This is a placeholder for actual API integration.
        Implement actual API calls based on TikTok Shop client and e-commerce platform.
    """
    all_orders = []

    try:
        # Determine which channels to fetch from
        channels_to_fetch = (
            [channel_filter] if channel_filter
            else api_clients.keys()
        )

        for channel_name in channels_to_fetch:
            if channel_name not in api_clients:
                continue

            client = api_clients[channel_name]

            # Example integration for TikTok Shop
            if channel_name == "tiktok_shop":
                # Integration with TikTok Shop API from mcf-connector
                # orders = client.getOrders(
                #     start_date=start_date.isoformat(),
                #     end_date=end_date.isoformat(),
                #     status=['completed', 'pending']
                # )
                # all_orders.extend([{**order, 'channel': 'tiktok_shop'} for order in orders])
                pass

            # Example integration for website (Shopify, WooCommerce, etc.)
            elif channel_name == "website":
                # Integration with e-commerce platform API
                # orders = client.get_orders(
                #     created_at_min=start_date.isoformat(),
                #     created_at_max=end_date.isoformat(),
                #     status='any'
                # )
                # all_orders.extend([{**order, 'channel': 'website'} for order in orders])
                pass

            # Example integration for Amazon
            elif channel_name == "amazon":
                # Integration with Amazon SP-API
                # orders = client.list_orders(
                #     CreatedAfter=start_date.isoformat(),
                #     CreatedBefore=end_date.isoformat()
                # )
                # all_orders.extend([{**order, 'channel': 'amazon'} for order in orders])
                pass

        return all_orders

    except Exception as e:
        raise Exception(f"Failed to fetch data from channel APIs: {str(e)}")


def _create_record(order_data: Dict[str, Any]) -> SalesData:
    """
    Create a new SalesData record from order data.

    Args:
        order_data: Dictionary containing order details

    Returns:
        SalesData: New database record

    Note:
        Automatically calculates subtotal from quantity * unit_price if not provided.
        Handles both full order objects and minimal order data.
    """
    # Calculate subtotal if not provided
    subtotal = order_data.get("subtotal")
    if subtotal is None:
        quantity = order_data.get("quantity", 1)
        unit_price = order_data.get("unit_price", 0)
        subtotal = quantity * unit_price

    # Calculate total if not provided
    total = order_data.get("total")
    if total is None:
        tax = order_data.get("tax", 0)
        shipping = order_data.get("shipping", 0)
        discount = order_data.get("discount", 0)
        total = subtotal + tax + shipping - discount

    return SalesData(
        order_id=order_data.get("order_id"),
        order_date=order_data.get("order_date", datetime.utcnow()),
        channel=order_data.get("channel"),

        # Customer information
        customer_id=order_data.get("customer_id"),
        customer_email=order_data.get("customer_email"),

        # Product information
        product_id=order_data.get("product_id"),
        product_name=order_data.get("product_name"),
        product_sku=order_data.get("product_sku"),

        # Order details
        quantity=order_data.get("quantity", 1),
        unit_price=order_data.get("unit_price", 0),
        subtotal=subtotal,
        tax=order_data.get("tax", 0),
        shipping=order_data.get("shipping", 0),
        discount=order_data.get("discount", 0),
        total=total,
        currency=order_data.get("currency", "USD"),

        # Payment information
        payment_method=order_data.get("payment_method"),

        # Order status
        order_status=order_data.get("order_status", "pending"),
        fulfillment_status=order_data.get("fulfillment_status", "unfulfilled"),

        # Marketing attribution
        attribution_source=order_data.get("attribution_source"),
        attribution_medium=order_data.get("attribution_medium"),
        attribution_campaign=order_data.get("attribution_campaign"),
        first_touch_source=order_data.get("first_touch_source"),
        last_touch_source=order_data.get("last_touch_source"),

        # Customer segmentation
        customer_type=order_data.get("customer_type"),
        country=order_data.get("country"),
        region=order_data.get("region"),
    )


def _update_record(
    existing_record: SalesData,
    order_data: Dict[str, Any]
) -> None:
    """
    Update an existing SalesData record with new data.

    This is particularly useful for updating order status, fulfillment status,
    or adding attribution data that may be enriched after initial order creation.

    Args:
        existing_record: Existing SalesData database record
        order_data: Dictionary containing updated order details
    """
    # Update order status if changed
    if "order_status" in order_data:
        existing_record.order_status = order_data["order_status"]

    if "fulfillment_status" in order_data:
        existing_record.fulfillment_status = order_data["fulfillment_status"]

    # Update financial data (e.g., for refunds)
    if "total" in order_data:
        existing_record.total = order_data["total"]

    if "discount" in order_data:
        existing_record.discount = order_data["discount"]

    # Update attribution data (may be enriched later)
    if "attribution_source" in order_data:
        existing_record.attribution_source = order_data["attribution_source"]

    if "attribution_medium" in order_data:
        existing_record.attribution_medium = order_data["attribution_medium"]

    if "attribution_campaign" in order_data:
        existing_record.attribution_campaign = order_data["attribution_campaign"]

    if "first_touch_source" in order_data:
        existing_record.first_touch_source = order_data["first_touch_source"]

    if "last_touch_source" in order_data:
        existing_record.last_touch_source = order_data["last_touch_source"]

    # Update customer type (e.g., new -> returning)
    if "customer_type" in order_data:
        existing_record.customer_type = order_data["customer_type"]

    # Update payment method if changed
    if "payment_method" in order_data:
        existing_record.payment_method = order_data["payment_method"]

    # Timestamp is automatically updated by SQLAlchemy onupdate


def get_sales_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    channel: Optional[str] = None,
    group_by: str = "channel"
) -> Dict[str, Any]:
    """
    Get summary statistics for sales data.

    Args:
        start_date: Start date for summary (defaults to 30 days ago)
        end_date: End date for summary (defaults to now)
        channel: Optional channel filter
        group_by: How to group results ('channel', 'date', 'product', 'attribution')

    Returns:
        Dict with summary statistics:
            - total_orders: Total number of orders
            - total_revenue: Total revenue
            - avg_order_value: Average order value
            - by_group: Statistics broken down by group_by parameter

    Example:
        >>> summary = get_sales_summary(group_by='channel')
        >>> print(f"Total revenue: ${summary['total_revenue']}")
        >>> for channel, stats in summary['by_group'].items():
        ...     print(f"{channel}: {stats['orders']} orders, ${stats['revenue']}")
    """
    # Set default date range
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    db = None
    try:
        db = get_db_session()

        # Build base query
        query = db.query(SalesData).filter(
            SalesData.order_date >= start_date,
            SalesData.order_date <= end_date
        )

        # Apply channel filter if specified
        if channel:
            query = query.filter(SalesData.channel == channel)

        # Get all records
        records = query.all()

        # Calculate overall statistics
        total_orders = len(records)
        total_revenue = sum(float(record.total) for record in records)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Group statistics
        by_group = {}

        if group_by == "channel":
            # Group by sales channel
            for record in records:
                key = record.channel
                if key not in by_group:
                    by_group[key] = {"orders": 0, "revenue": 0}
                by_group[key]["orders"] += 1
                by_group[key]["revenue"] += float(record.total)

        elif group_by == "date":
            # Group by order date
            for record in records:
                key = record.order_date.date().isoformat()
                if key not in by_group:
                    by_group[key] = {"orders": 0, "revenue": 0}
                by_group[key]["orders"] += 1
                by_group[key]["revenue"] += float(record.total)

        elif group_by == "product":
            # Group by product
            for record in records:
                key = record.product_name or record.product_id or "Unknown"
                if key not in by_group:
                    by_group[key] = {"orders": 0, "revenue": 0, "quantity": 0}
                by_group[key]["orders"] += 1
                by_group[key]["revenue"] += float(record.total)
                by_group[key]["quantity"] += record.quantity

        elif group_by == "attribution":
            # Group by attribution source
            for record in records:
                key = record.attribution_source or "Unknown"
                if key not in by_group:
                    by_group[key] = {"orders": 0, "revenue": 0}
                by_group[key]["orders"] += 1
                by_group[key]["revenue"] += float(record.total)

        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "by_group": by_group,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    except Exception as e:
        return {
            "error": str(e),
            "total_orders": 0,
            "total_revenue": 0,
            "avg_order_value": 0,
            "by_group": {}
        }

    finally:
        if db:
            db.close()
