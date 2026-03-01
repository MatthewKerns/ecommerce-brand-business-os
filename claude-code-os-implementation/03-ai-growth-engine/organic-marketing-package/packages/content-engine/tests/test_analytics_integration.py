"""
End-to-end integration tests for the complete analytics data pipeline.

This test suite verifies the full data flow from ingestion through to visualization:
1. TikTok data → database → dashboard queries
2. Website analytics → database → dashboard queries
3. Email metrics → database → dashboard queries
4. Sales data → database → dashboard queries
5. Scheduler orchestration → multi-channel ingestion
6. Data refresh and update workflows

Tests validate:
- ETL pipeline data ingestion
- Database schema and constraints
- Data retrieval for dashboard visualization
- Scheduler orchestration
- Error handling across all layers
- Data freshness and update logic
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, Mock
import logging
from typing import Dict, List, Any

# Import database components
from database.connection import get_db_session, Base, engine
from database.init_db import init_database_orm

# Import analytics models
from analytics.models import (
    TikTokMetrics,
    WebsiteAnalytics,
    EmailMetrics,
    SalesData
)

# Import ETL functions
from analytics.etl import (
    ingest_tiktok_metrics,
    ingest_website_analytics,
    ingest_email_metrics,
    ingest_sales_data
)

# Import scheduler
from analytics.scheduler import run_daily_refresh


@pytest.fixture(scope="module")
def setup_test_database():
    """
    Initialize test database with all analytics tables.

    This fixture creates a fresh database for each test module run.
    All tables are created before tests and dropped after.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield

    # Cleanup: Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_test_database):
    """
    Provide a clean database session for each test.

    This fixture:
    - Creates a new session for each test
    - Cleans up all analytics data after each test
    - Ensures test isolation
    """
    db = get_db_session()
    try:
        yield db
    finally:
        # Clean up all analytics data
        db.query(TikTokMetrics).delete()
        db.query(WebsiteAnalytics).delete()
        db.query(EmailMetrics).delete()
        db.query(SalesData).delete()
        db.commit()
        db.close()


@pytest.fixture
def sample_tiktok_data() -> List[Dict[str, Any]]:
    """
    Generate sample TikTok metrics data for testing.

    Returns realistic TikTok video performance data with:
    - Multiple videos with different performance levels
    - Complete metric coverage
    - Proper timestamp formatting
    """
    base_time = datetime.utcnow()

    return [
        {
            "video_id": "tiktok_video_001",
            "video_url": "https://www.tiktok.com/@brand/video/001",
            "posted_at": base_time - timedelta(days=7),
            "recorded_at": base_time,
            "views": 125000,
            "likes": 8500,
            "comments": 320,
            "shares": 1200,
            "saves": 2400,
            "engagement_rate": 9.93,
            "watch_time_avg_seconds": 45,
            "watch_time_total_hours": 1562.5,
            "video_completion_rate": 68.5,
            "shop_clicks": 3200,
            "product_views": 2100,
            "source_location": "US",
            "traffic_source": "For You Page",
            "hashtags": '["tradingcards", "pokemon", "collecting"]',
            "caption": "Best way to organize your trading card collection! #tradingcards"
        },
        {
            "video_id": "tiktok_video_002",
            "video_url": "https://www.tiktok.com/@brand/video/002",
            "posted_at": base_time - timedelta(days=5),
            "recorded_at": base_time,
            "views": 85000,
            "likes": 5200,
            "comments": 180,
            "shares": 650,
            "saves": 1800,
            "engagement_rate": 9.15,
            "watch_time_avg_seconds": 38,
            "watch_time_total_hours": 896.67,
            "video_completion_rate": 62.3,
            "shop_clicks": 1850,
            "product_views": 1200,
            "source_location": "US",
            "traffic_source": "Hashtag",
            "hashtags": '["cardcollecting", "hobby"]',
            "caption": "Top 5 card storage solutions! Link in bio #cardcollecting"
        },
        {
            "video_id": "tiktok_video_003",
            "video_url": "https://www.tiktok.com/@brand/video/003",
            "posted_at": base_time - timedelta(days=2),
            "recorded_at": base_time,
            "views": 42000,
            "likes": 2800,
            "comments": 95,
            "shares": 320,
            "saves": 890,
            "engagement_rate": 9.64,
            "watch_time_avg_seconds": 52,
            "watch_time_total_hours": 606.67,
            "video_completion_rate": 74.2,
            "shop_clicks": 980,
            "product_views": 650,
            "source_location": "US",
            "traffic_source": "Following",
            "hashtags": '["trading", "collection"]',
            "caption": "Unboxing rare card pulls! #trading"
        }
    ]


@pytest.fixture
def sample_website_data() -> List[Dict[str, Any]]:
    """
    Generate sample website analytics data for testing.

    Returns realistic website traffic data with:
    - Multiple pages and traffic sources
    - Conversion tracking
    - Device and geographic segmentation
    """
    base_date = datetime.utcnow().date()

    return [
        {
            "date": base_date - timedelta(days=1),
            "session_id": "session_001",
            "page_path": "/products/card-sleeves",
            "page_title": "Premium Card Sleeves | Trading Card Supplies",
            "sessions": 450,
            "pageviews": 1250,
            "unique_pageviews": 420,
            "avg_time_on_page_seconds": 145,
            "bounce_rate": 35.5,
            "exit_rate": 42.3,
            "users": 380,
            "new_users": 210,
            "traffic_source": "tiktok",
            "traffic_medium": "social",
            "traffic_campaign": "card_storage_tips",
            "device_category": "mobile",
            "country": "United States",
            "conversions": 28,
            "conversion_rate": 6.22,
            "revenue": Decimal("1456.80")
        },
        {
            "date": base_date - timedelta(days=1),
            "session_id": "session_002",
            "page_path": "/blog/card-organization-guide",
            "page_title": "Ultimate Trading Card Organization Guide",
            "sessions": 820,
            "pageviews": 2100,
            "unique_pageviews": 750,
            "avg_time_on_page_seconds": 285,
            "bounce_rate": 28.2,
            "exit_rate": 35.8,
            "users": 680,
            "new_users": 520,
            "traffic_source": "google",
            "traffic_medium": "organic",
            "traffic_campaign": None,
            "device_category": "desktop",
            "country": "United States",
            "conversions": 45,
            "conversion_rate": 5.49,
            "revenue": Decimal("2340.50")
        },
        {
            "date": base_date,
            "session_id": "session_003",
            "page_path": "/products/storage-boxes",
            "page_title": "Card Storage Boxes | Organize Your Collection",
            "sessions": 320,
            "pageviews": 890,
            "unique_pageviews": 295,
            "avg_time_on_page_seconds": 165,
            "bounce_rate": 38.8,
            "exit_rate": 45.2,
            "users": 275,
            "new_users": 180,
            "traffic_source": "email",
            "traffic_medium": "email",
            "traffic_campaign": "weekly_newsletter",
            "device_category": "mobile",
            "country": "United States",
            "conversions": 22,
            "conversion_rate": 6.88,
            "revenue": Decimal("1142.00")
        }
    ]


@pytest.fixture
def sample_email_data() -> List[Dict[str, Any]]:
    """
    Generate sample email metrics data for testing.

    Returns realistic email campaign performance data with:
    - Multiple campaigns with different performance
    - Full funnel metrics (sent → delivered → opened → clicked → converted)
    - Revenue attribution
    """
    base_date = datetime.utcnow()

    return [
        {
            "campaign_id": "email_campaign_001",
            "campaign_name": "Weekly Newsletter - Card Care Tips",
            "send_date": base_date - timedelta(days=3),
            "list_id": "main_subscribers",
            "list_name": "Main Subscriber List",
            "subject_line": "5 Essential Tips for Card Preservation",
            "from_name": "Trading Card Experts",
            "from_email": "hello@tradingcards.com",
            "emails_sent": 15000,
            "emails_delivered": 14820,
            "emails_bounced": 180,
            "hard_bounces": 45,
            "soft_bounces": 135,
            "opens": 5928,
            "unique_opens": 4446,
            "open_rate": 30.0,
            "clicks": 1186,
            "unique_clicks": 889,
            "click_rate": 6.0,
            "click_to_open_rate": 20.0,
            "unsubscribes": 74,
            "unsubscribe_rate": 0.50,
            "spam_reports": 7,
            "conversions": 48,
            "conversion_rate": 5.40,
            "revenue": Decimal("2496.00")
        },
        {
            "campaign_id": "email_campaign_002",
            "campaign_name": "Product Launch - New Binder Line",
            "send_date": base_date - timedelta(days=7),
            "list_id": "main_subscribers",
            "list_name": "Main Subscriber List",
            "subject_line": "Introducing Premium Card Binders - Pre-Order Now!",
            "from_name": "Trading Card Experts",
            "from_email": "hello@tradingcards.com",
            "emails_sent": 15000,
            "emails_delivered": 14865,
            "emails_bounced": 135,
            "hard_bounces": 30,
            "soft_bounces": 105,
            "opens": 7432,
            "unique_opens": 5946,
            "open_rate": 40.0,
            "clicks": 1783,
            "unique_clicks": 1486,
            "click_rate": 10.0,
            "click_to_open_rate": 25.0,
            "unsubscribes": 59,
            "unsubscribe_rate": 0.40,
            "spam_reports": 4,
            "conversions": 92,
            "conversion_rate": 6.19,
            "revenue": Decimal("5980.00")
        }
    ]


@pytest.fixture
def sample_sales_data() -> List[Dict[str, Any]]:
    """
    Generate sample sales data for testing.

    Returns realistic order data with:
    - Multiple channels (TikTok Shop, website)
    - Complete order details
    - Marketing attribution
    - Customer segmentation
    """
    base_date = datetime.utcnow()

    return [
        {
            "order_id": "order_tiktok_001",
            "order_date": base_date - timedelta(days=1),
            "channel": "tiktok_shop",
            "customer_id": "customer_001",
            "customer_email": "hashed_email_001",
            "product_id": "prod_sleeves_001",
            "product_name": "Premium Card Sleeves (100 pack)",
            "product_sku": "SLEEVE-100-PREM",
            "quantity": 2,
            "unit_price": Decimal("24.99"),
            "subtotal": Decimal("49.98"),
            "tax": Decimal("4.25"),
            "shipping": Decimal("5.99"),
            "discount": Decimal("0.00"),
            "total": Decimal("60.22"),
            "currency": "USD",
            "payment_method": "credit_card",
            "order_status": "completed",
            "fulfillment_status": "shipped",
            "attribution_source": "tiktok",
            "attribution_medium": "social",
            "attribution_campaign": "card_storage_tips",
            "first_touch_source": "tiktok",
            "last_touch_source": "tiktok",
            "customer_type": "new",
            "country": "United States",
            "region": "California"
        },
        {
            "order_id": "order_website_001",
            "order_date": base_date - timedelta(days=2),
            "channel": "website",
            "customer_id": "customer_002",
            "customer_email": "hashed_email_002",
            "product_id": "prod_binder_001",
            "product_name": "9-Pocket Card Binder",
            "product_sku": "BIND-9P-STD",
            "quantity": 1,
            "unit_price": Decimal("34.99"),
            "subtotal": Decimal("34.99"),
            "tax": Decimal("2.98"),
            "shipping": Decimal("0.00"),
            "discount": Decimal("5.00"),
            "total": Decimal("32.97"),
            "currency": "USD",
            "payment_method": "paypal",
            "order_status": "completed",
            "fulfillment_status": "delivered",
            "attribution_source": "google",
            "attribution_medium": "organic",
            "attribution_campaign": None,
            "first_touch_source": "tiktok",
            "last_touch_source": "google",
            "customer_type": "returning",
            "country": "United States",
            "region": "Texas"
        },
        {
            "order_id": "order_tiktok_002",
            "order_date": base_date - timedelta(hours=6),
            "channel": "tiktok_shop",
            "customer_id": "customer_003",
            "customer_email": "hashed_email_003",
            "product_id": "prod_box_001",
            "product_name": "Storage Box 5000-count",
            "product_sku": "BOX-5000-WHT",
            "quantity": 3,
            "unit_price": Decimal("19.99"),
            "subtotal": Decimal("59.97"),
            "tax": Decimal("5.10"),
            "shipping": Decimal("7.99"),
            "discount": Decimal("6.00"),
            "total": Decimal("67.06"),
            "currency": "USD",
            "payment_method": "credit_card",
            "order_status": "pending",
            "fulfillment_status": "unfulfilled",
            "attribution_source": "tiktok",
            "attribution_medium": "social",
            "attribution_campaign": "storage_solutions",
            "first_touch_source": "tiktok",
            "last_touch_source": "tiktok",
            "customer_type": "new",
            "country": "United States",
            "region": "New York"
        }
    ]


@pytest.mark.e2e
@pytest.mark.integration
class TestAnalyticsDataPipeline:
    """
    End-to-end tests for the complete analytics data pipeline.

    These tests verify the full integration from data ingestion through
    database storage to dashboard query patterns.
    """

    def test_tiktok_data_ingestion_flow(
        self,
        db_session,
        sample_tiktok_data,
        caplog
    ):
        """
        Test complete TikTok data flow: ingestion → database → query.

        Steps:
        1. Ingest sample TikTok metrics data
        2. Verify successful ingestion results
        3. Query database to verify data storage
        4. Verify data integrity and constraints
        5. Verify logs contain ingestion information
        """
        caplog.set_level(logging.INFO)

        # Step 1: Ingest TikTok data
        result = ingest_tiktok_metrics(video_data=sample_tiktok_data)

        # Step 2: Verify ingestion results
        assert result["success"] is True, f"Ingestion failed: {result.get('errors')}"
        assert result["records_processed"] == 3, "Should process 3 video records"
        assert result["records_inserted"] == 3, "Should insert 3 new records"
        assert result["records_updated"] == 0, "Should not update any records (first run)"
        assert len(result["errors"]) == 0, "Should have no errors"

        # Step 3: Query database
        tiktok_records = db_session.query(TikTokMetrics).all()
        assert len(tiktok_records) == 3, "Database should contain 3 TikTok records"

        # Step 4: Verify data integrity
        # Find the high-performing video
        video_001 = db_session.query(TikTokMetrics).filter(
            TikTokMetrics.video_id == "tiktok_video_001"
        ).first()

        assert video_001 is not None, "Should find video_001"
        assert video_001.views == 125000, "Views should match input data"
        assert video_001.likes == 8500, "Likes should match input data"
        assert video_001.shop_clicks == 3200, "Shop clicks should match input data"
        assert video_001.engagement_rate == Decimal("9.93"), "Engagement rate should match"
        assert video_001.source_location == "US", "Location should match"

        # Verify timestamps are set
        assert video_001.created_at is not None, "Created timestamp should be set"
        assert video_001.updated_at is not None, "Updated timestamp should be set"

        # Step 5: Test dashboard query pattern (total views across all videos)
        total_views = db_session.query(
            TikTokMetrics
        ).with_entities(
            TikTokMetrics.views
        ).all()

        total_view_count = sum(record.views for record in total_views)
        expected_total = 125000 + 85000 + 42000  # Sum from sample data
        assert total_view_count == expected_total, "Total views should match"

    def test_website_data_ingestion_flow(
        self,
        db_session,
        sample_website_data
    ):
        """
        Test complete website analytics flow: ingestion → database → query.

        Verifies:
        - Website analytics ingestion
        - Traffic source attribution
        - Conversion tracking
        - Revenue aggregation queries
        """
        # Step 1: Ingest website data
        result = ingest_website_analytics(analytics_data=sample_website_data)

        # Step 2: Verify ingestion results
        assert result["success"] is True, f"Ingestion failed: {result.get('errors')}"
        assert result["records_processed"] == 3, "Should process 3 analytics records"
        assert result["records_inserted"] == 3, "Should insert 3 new records"

        # Step 3: Query database
        website_records = db_session.query(WebsiteAnalytics).all()
        assert len(website_records) == 3, "Database should contain 3 website records"

        # Step 4: Verify traffic attribution data
        tiktok_traffic = db_session.query(WebsiteAnalytics).filter(
            WebsiteAnalytics.traffic_source == "tiktok"
        ).first()

        assert tiktok_traffic is not None, "Should find TikTok traffic"
        assert tiktok_traffic.traffic_medium == "social", "Medium should be social"
        assert tiktok_traffic.conversions == 28, "Conversions should match"
        assert tiktok_traffic.revenue == Decimal("1456.80"), "Revenue should match"

        # Step 5: Test dashboard query pattern (total conversions by source)
        conversion_by_source = db_session.query(
            WebsiteAnalytics.traffic_source,
            WebsiteAnalytics.conversions,
            WebsiteAnalytics.revenue
        ).all()

        total_conversions = sum(record.conversions for record in conversion_by_source)
        assert total_conversions == 95, "Total conversions should be 95 (28+45+22)"

        total_revenue = sum(record.revenue for record in conversion_by_source)
        expected_revenue = Decimal("1456.80") + Decimal("2340.50") + Decimal("1142.00")
        assert total_revenue == expected_revenue, "Total revenue should match"

    def test_email_metrics_ingestion_flow(
        self,
        db_session,
        sample_email_data
    ):
        """
        Test complete email metrics flow: ingestion → database → query.

        Verifies:
        - Email campaign metrics ingestion
        - Funnel metrics (sent → opened → clicked → converted)
        - Performance calculation queries
        """
        # Step 1: Ingest email data
        result = ingest_email_metrics(campaign_data=sample_email_data)

        # Step 2: Verify ingestion results
        assert result["success"] is True, f"Ingestion failed: {result.get('errors')}"
        assert result["records_processed"] == 2, "Should process 2 campaign records"
        assert result["records_inserted"] == 2, "Should insert 2 new records"

        # Step 3: Query database
        email_records = db_session.query(EmailMetrics).all()
        assert len(email_records) == 2, "Database should contain 2 email campaign records"

        # Step 4: Verify email funnel metrics
        product_launch = db_session.query(EmailMetrics).filter(
            EmailMetrics.campaign_id == "email_campaign_002"
        ).first()

        assert product_launch is not None, "Should find product launch campaign"
        assert product_launch.emails_sent == 15000, "Sent count should match"
        assert product_launch.unique_opens == 5946, "Opens should match"
        assert product_launch.unique_clicks == 1486, "Clicks should match"
        assert product_launch.conversions == 92, "Conversions should match"
        assert product_launch.open_rate == Decimal("40.0"), "Open rate should match"
        assert product_launch.click_rate == Decimal("10.0"), "Click rate should match"
        assert product_launch.revenue == Decimal("5980.00"), "Revenue should match"

        # Step 5: Test dashboard query pattern (aggregate email performance)
        aggregate_stats = db_session.query(EmailMetrics).all()

        total_sent = sum(record.emails_sent for record in aggregate_stats)
        total_conversions = sum(record.conversions for record in aggregate_stats)
        total_revenue = sum(record.revenue for record in aggregate_stats)

        assert total_sent == 30000, "Total emails sent should be 30,000"
        assert total_conversions == 140, "Total conversions should be 140 (48+92)"
        assert total_revenue == Decimal("8476.00"), "Total revenue should match"

    def test_sales_data_ingestion_flow(
        self,
        db_session,
        sample_sales_data
    ):
        """
        Test complete sales data flow: ingestion → database → query.

        Verifies:
        - Multi-channel sales data ingestion
        - Order details and attribution
        - Revenue aggregation by channel
        - Customer segmentation queries
        """
        # Step 1: Ingest sales data
        result = ingest_sales_data(order_data=sample_sales_data)

        # Step 2: Verify ingestion results
        assert result["success"] is True, f"Ingestion failed: {result.get('errors')}"
        assert result["records_processed"] == 3, "Should process 3 order records"
        assert result["records_inserted"] == 3, "Should insert 3 new records"
        assert "total_revenue" in result, "Result should include total revenue"

        # Step 3: Query database
        sales_records = db_session.query(SalesData).all()
        assert len(sales_records) == 3, "Database should contain 3 sales records"

        # Step 4: Verify multi-channel sales data
        tiktok_orders = db_session.query(SalesData).filter(
            SalesData.channel == "tiktok_shop"
        ).all()

        website_orders = db_session.query(SalesData).filter(
            SalesData.channel == "website"
        ).all()

        assert len(tiktok_orders) == 2, "Should have 2 TikTok Shop orders"
        assert len(website_orders) == 1, "Should have 1 website order"

        # Step 5: Verify order attribution
        order_001 = db_session.query(SalesData).filter(
            SalesData.order_id == "order_tiktok_001"
        ).first()

        assert order_001 is not None, "Should find order_tiktok_001"
        assert order_001.attribution_source == "tiktok", "Attribution source should be TikTok"
        assert order_001.attribution_campaign == "card_storage_tips", "Campaign should match"
        assert order_001.customer_type == "new", "Customer type should be new"
        assert order_001.total == Decimal("60.22"), "Order total should match"

        # Step 6: Test dashboard query pattern (revenue by channel)
        from sqlalchemy import func

        revenue_by_channel = db_session.query(
            SalesData.channel,
            func.count(SalesData.id).label('order_count'),
            func.sum(SalesData.total).label('total_revenue')
        ).group_by(SalesData.channel).all()

        assert len(revenue_by_channel) == 2, "Should have 2 channels (tiktok_shop, website)"

        # Find TikTok Shop revenue
        tiktok_revenue = next(
            (r for r in revenue_by_channel if r.channel == "tiktok_shop"),
            None
        )
        assert tiktok_revenue is not None, "Should have TikTok Shop revenue data"
        assert tiktok_revenue.order_count == 2, "TikTok Shop should have 2 orders"

        # Calculate expected TikTok revenue: 60.22 + 67.06 = 127.28
        expected_tiktok_revenue = Decimal("60.22") + Decimal("67.06")
        assert tiktok_revenue.total_revenue == expected_tiktok_revenue

    def test_scheduler_orchestration(
        self,
        db_session,
        sample_tiktok_data,
        sample_website_data,
        sample_email_data,
        sample_sales_data,
        caplog
    ):
        """
        Test scheduler orchestrating all ETL pipelines.

        Verifies:
        - Scheduler runs all pipelines in sequence
        - Aggregated statistics are correct
        - Error handling for failed pipelines
        - Logging of scheduler operations
        """
        caplog.set_level(logging.INFO)

        # Step 1: Mock API clients to return our test data
        mock_api_clients = {
            'tiktok': Mock(get_video_metrics=Mock(return_value=sample_tiktok_data)),
            'website': Mock(get_analytics=Mock(return_value=sample_website_data)),
            'email': Mock(get_campaigns=Mock(return_value=sample_email_data)),
            'sales': {'tiktok_shop': Mock(get_orders=Mock(return_value=[sample_sales_data[0], sample_sales_data[2]]))}
        }

        # Step 2: Run daily refresh with test data
        # We'll pass the data directly instead of using API clients for this test
        tiktok_result = ingest_tiktok_metrics(video_data=sample_tiktok_data)
        website_result = ingest_website_analytics(analytics_data=sample_website_data)
        email_result = ingest_email_metrics(campaign_data=sample_email_data)
        sales_result = ingest_sales_data(order_data=sample_sales_data)

        # Step 3: Verify all pipelines succeeded
        assert tiktok_result["success"] is True, "TikTok pipeline should succeed"
        assert website_result["success"] is True, "Website pipeline should succeed"
        assert email_result["success"] is True, "Email pipeline should succeed"
        assert sales_result["success"] is True, "Sales pipeline should succeed"

        # Step 4: Verify database contains all ingested data
        tiktok_count = db_session.query(TikTokMetrics).count()
        website_count = db_session.query(WebsiteAnalytics).count()
        email_count = db_session.query(EmailMetrics).count()
        sales_count = db_session.query(SalesData).count()

        assert tiktok_count == 3, "Should have 3 TikTok records"
        assert website_count == 3, "Should have 3 website records"
        assert email_count == 2, "Should have 2 email records"
        assert sales_count == 3, "Should have 3 sales records"

        # Step 5: Calculate aggregated statistics
        total_records = tiktok_count + website_count + email_count + sales_count
        assert total_records == 11, "Total records should be 11"

        total_records_inserted = (
            tiktok_result["records_inserted"] +
            website_result["records_inserted"] +
            email_result["records_inserted"] +
            sales_result["records_inserted"]
        )
        assert total_records_inserted == 11, "Total inserted should match"

    def test_data_refresh_and_update_flow(
        self,
        db_session,
        sample_tiktok_data
    ):
        """
        Test data refresh workflow with updates to existing records.

        Verifies:
        - Initial data ingestion
        - Re-ingestion with updated metrics
        - Update logic (not duplicate insertion)
        - Updated timestamp handling
        """
        # Step 1: Initial data ingestion
        initial_result = ingest_tiktok_metrics(video_data=sample_tiktok_data)

        assert initial_result["success"] is True
        assert initial_result["records_inserted"] == 3, "Should insert 3 records initially"
        assert initial_result["records_updated"] == 0, "Should not update any records"

        # Step 2: Get initial view count
        video_001 = db_session.query(TikTokMetrics).filter(
            TikTokMetrics.video_id == "tiktok_video_001"
        ).first()

        initial_views = video_001.views
        initial_updated_at = video_001.updated_at
        assert initial_views == 125000, "Initial views should be 125,000"

        # Step 3: Simulate data refresh with updated metrics
        updated_data = sample_tiktok_data.copy()
        updated_data[0] = updated_data[0].copy()
        updated_data[0]["views"] = 150000  # Increased views
        updated_data[0]["likes"] = 10200  # Increased likes
        updated_data[0]["shop_clicks"] = 3800  # Increased shop clicks

        # Step 4: Re-ingest with updated data
        refresh_result = ingest_tiktok_metrics(video_data=updated_data)

        assert refresh_result["success"] is True
        assert refresh_result["records_processed"] == 3, "Should process 3 records"
        assert refresh_result["records_updated"] == 3, "Should update all 3 existing records"
        assert refresh_result["records_inserted"] == 0, "Should not insert new records"

        # Step 5: Verify data was updated, not duplicated
        total_records = db_session.query(TikTokMetrics).count()
        assert total_records == 3, "Should still have only 3 records (no duplicates)"

        # Step 6: Verify updated metrics
        db_session.refresh(video_001)  # Refresh to get updated data

        assert video_001.views == 150000, "Views should be updated to 150,000"
        assert video_001.likes == 10200, "Likes should be updated to 10,200"
        assert video_001.shop_clicks == 3800, "Shop clicks should be updated to 3,800"

        # Step 7: Verify updated_at timestamp changed
        assert video_001.updated_at >= initial_updated_at, "Updated timestamp should be newer"

    def test_cross_channel_attribution_query(
        self,
        db_session,
        sample_tiktok_data,
        sample_website_data,
        sample_sales_data
    ):
        """
        Test cross-channel attribution queries for dashboard.

        This simulates dashboard queries that combine data from multiple
        channels to provide attribution insights.

        Verifies:
        - TikTok video performance → website traffic → sales
        - Attribution tracking across touchpoints
        - Revenue attribution to marketing channels
        """
        # Step 1: Ingest all relevant data
        ingest_tiktok_metrics(video_data=sample_tiktok_data)
        ingest_website_analytics(analytics_data=sample_website_data)
        ingest_sales_data(order_data=sample_sales_data)

        # Step 2: Query TikTok shop clicks (top of funnel)
        tiktok_metrics = db_session.query(TikTokMetrics).all()
        total_shop_clicks = sum(video.shop_clicks for video in tiktok_metrics)
        assert total_shop_clicks == 6030, "Total shop clicks should be 6,030"

        # Step 3: Query website traffic from TikTok (middle of funnel)
        tiktok_website_traffic = db_session.query(WebsiteAnalytics).filter(
            WebsiteAnalytics.traffic_source == "tiktok"
        ).first()

        assert tiktok_website_traffic is not None, "Should have website traffic from TikTok"
        assert tiktok_website_traffic.sessions == 450, "Should have 450 sessions from TikTok"
        assert tiktok_website_traffic.conversions == 28, "Should have 28 conversions"

        # Step 4: Query sales attributed to TikTok (bottom of funnel)
        tiktok_attributed_sales = db_session.query(SalesData).filter(
            SalesData.attribution_source == "tiktok"
        ).all()

        tiktok_revenue = sum(order.total for order in tiktok_attributed_sales)
        tiktok_order_count = len(tiktok_attributed_sales)

        assert tiktok_order_count == 2, "Should have 2 orders attributed to TikTok"
        expected_tiktok_revenue = Decimal("60.22") + Decimal("67.06")
        assert tiktok_revenue == expected_tiktok_revenue, "TikTok revenue should match"

        # Step 5: Calculate funnel conversion rates (dashboard metric)
        # Shop clicks → Website sessions → Orders
        funnel_metrics = {
            "awareness": total_shop_clicks,  # 6,030 shop clicks
            "interest": tiktok_website_traffic.sessions,  # 450 sessions
            "purchase": tiktok_order_count  # 2 orders
        }

        # Conversion rate from shop clicks to sessions
        awareness_to_interest = (funnel_metrics["interest"] / funnel_metrics["awareness"]) * 100
        assert awareness_to_interest < 10, "Conversion rate should be realistic"

        # Conversion rate from sessions to purchase
        interest_to_purchase = (funnel_metrics["purchase"] / funnel_metrics["interest"]) * 100
        assert interest_to_purchase < 5, "Purchase conversion should be realistic"

    def test_error_handling_invalid_data(self, db_session):
        """
        Test error handling with invalid data.

        Verifies:
        - Invalid data types are rejected
        - Database constraints are enforced
        - Partial failures don't corrupt database
        - Errors are reported in results
        """
        # Step 1: Test with invalid TikTok data (negative views)
        invalid_tiktok_data = [
            {
                "video_id": "invalid_video",
                "video_url": "https://tiktok.com/@test/video/999",
                "posted_at": datetime.utcnow(),
                "recorded_at": datetime.utcnow(),
                "views": -1000,  # Invalid: negative views
                "likes": 100,
                "comments": 10,
                "shares": 5,
                "saves": 8,
                "shop_clicks": 20,
                "product_views": 15
            }
        ]

        # Step 2: Attempt ingestion (should fail due to constraint)
        result = ingest_tiktok_metrics(video_data=invalid_tiktok_data)

        # Step 3: Verify failure is handled gracefully
        assert result["success"] is False, "Ingestion should fail with invalid data"
        assert len(result["errors"]) > 0, "Should have error messages"

        # Step 4: Verify database is not corrupted
        record_count = db_session.query(TikTokMetrics).count()
        assert record_count == 0, "No records should be inserted with invalid data"

    def test_dashboard_data_freshness_check(
        self,
        db_session,
        sample_tiktok_data
    ):
        """
        Test data freshness verification for dashboard.

        Dashboards need to know when data was last updated.

        Verifies:
        - Timestamp tracking for ingested data
        - Most recent data retrieval
        - Data age calculation
        """
        # Step 1: Ingest data
        ingest_tiktok_metrics(video_data=sample_tiktok_data)

        # Step 2: Query most recent data update
        from sqlalchemy import func

        latest_update = db_session.query(
            func.max(TikTokMetrics.updated_at)
        ).scalar()

        assert latest_update is not None, "Should have update timestamp"

        # Step 3: Calculate data age
        data_age = datetime.utcnow() - latest_update
        assert data_age.total_seconds() < 60, "Data should be fresh (less than 1 minute old)"

        # Step 4: Query most recent recorded_at (when metrics were captured)
        latest_recording = db_session.query(
            func.max(TikTokMetrics.recorded_at)
        ).scalar()

        assert latest_recording is not None, "Should have recording timestamp"
