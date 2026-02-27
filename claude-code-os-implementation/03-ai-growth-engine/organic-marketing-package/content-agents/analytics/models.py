"""
Analytics data models for unified marketing data warehouse.
Defines SQLAlchemy ORM models for TikTok metrics, website analytics, email metrics, and sales data.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    Integer, Numeric, String, Text, Index, Date
)
from sqlalchemy.orm import relationship
import sys
from pathlib import Path

# Add parent directory to path to import Base
sys.path.append(str(Path(__file__).parent.parent))
from database.connection import Base


class TikTokMetrics(Base):
    """
    Stores TikTok video performance metrics for tracking organic reach and engagement.

    Attributes:
        id: Primary key
        video_id: TikTok video identifier
        video_url: URL to the TikTok video
        posted_at: When the video was posted
        recorded_at: When these metrics were recorded
        views: Total video views
        likes: Total likes
        comments: Total comments
        shares: Total shares
        saves: Total saves/bookmarks
        engagement_rate: Calculated engagement rate (percentage)
        watch_time_avg_seconds: Average watch time in seconds
        watch_time_total_hours: Total watch time in hours
        shop_clicks: Clicks to TikTok Shop
        product_views: Product detail page views from video
        video_completion_rate: Percentage of viewers who watched to end
        source_location: Geographic source (US, UK, etc.)
        traffic_source: How users found the video
        hashtags: JSON list of hashtags used
        caption: Video caption text
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "tiktok_metrics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Video Identification
    video_id = Column(String(100), nullable=False, index=True)
    video_url = Column(String(500))
    posted_at = Column(DateTime, nullable=False, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Engagement Metrics
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    saves = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(Numeric(5, 2))  # Percentage (0.00-100.00)

    # Watch Metrics
    watch_time_avg_seconds = Column(Integer)
    watch_time_total_hours = Column(Numeric(12, 2))
    video_completion_rate = Column(Numeric(5, 2))  # Percentage

    # Commerce Metrics
    shop_clicks = Column(Integer, default=0, nullable=False)
    product_views = Column(Integer, default=0, nullable=False)

    # Demographic & Traffic
    source_location = Column(String(100))
    traffic_source = Column(String(100))

    # Content Metadata
    hashtags = Column(Text)  # JSON stored as text
    caption = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Table constraints
    __table_args__ = (
        CheckConstraint("views >= 0", name="check_views"),
        CheckConstraint("likes >= 0", name="check_likes"),
        CheckConstraint("comments >= 0", name="check_comments"),
        CheckConstraint("shares >= 0", name="check_shares"),
        CheckConstraint("saves >= 0", name="check_saves"),
        CheckConstraint("shop_clicks >= 0", name="check_shop_clicks"),
        CheckConstraint("product_views >= 0", name="check_product_views"),
        CheckConstraint("engagement_rate >= 0 AND engagement_rate <= 100", name="check_engagement_rate"),
        CheckConstraint("video_completion_rate >= 0 AND video_completion_rate <= 100", name="check_completion_rate"),
        Index("idx_tiktok_video_date", "video_id", "recorded_at"),
    )

    def __repr__(self):
        return f"<TikTokMetrics(id={self.id}, video_id='{self.video_id}', views={self.views})>"


class WebsiteAnalytics(Base):
    """
    Stores website analytics data for tracking visitor behavior and conversions.

    Attributes:
        id: Primary key
        date: Date for these analytics
        session_id: Optional session identifier
        page_path: URL path visited
        page_title: Page title
        sessions: Number of sessions
        pageviews: Total pageviews
        unique_pageviews: Unique pageviews
        avg_time_on_page_seconds: Average time on page
        bounce_rate: Bounce rate percentage
        exit_rate: Exit rate percentage
        users: Number of users
        new_users: Number of new users
        traffic_source: Traffic source (organic, social, direct, etc.)
        traffic_medium: Traffic medium
        traffic_campaign: Campaign identifier
        device_category: Device type (desktop, mobile, tablet)
        country: User country
        conversions: Number of conversions
        conversion_rate: Conversion rate percentage
        revenue: Revenue generated (in USD)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "website_analytics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Time Dimension
    date = Column(Date, nullable=False, index=True)
    session_id = Column(String(100), index=True)

    # Page Information
    page_path = Column(String(500), nullable=False, index=True)
    page_title = Column(String(500))

    # Traffic Metrics
    sessions = Column(Integer, default=0, nullable=False)
    pageviews = Column(Integer, default=0, nullable=False)
    unique_pageviews = Column(Integer, default=0, nullable=False)
    avg_time_on_page_seconds = Column(Integer)

    # Engagement Metrics
    bounce_rate = Column(Numeric(5, 2))  # Percentage
    exit_rate = Column(Numeric(5, 2))  # Percentage

    # User Metrics
    users = Column(Integer, default=0, nullable=False)
    new_users = Column(Integer, default=0, nullable=False)

    # Traffic Attribution
    traffic_source = Column(String(100), index=True)
    traffic_medium = Column(String(100))
    traffic_campaign = Column(String(200), index=True)

    # Demographic
    device_category = Column(String(50))
    country = Column(String(100))

    # Conversion Metrics
    conversions = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Numeric(5, 2))  # Percentage
    revenue = Column(Numeric(12, 2))  # USD

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Table constraints
    __table_args__ = (
        CheckConstraint("sessions >= 0", name="check_sessions"),
        CheckConstraint("pageviews >= 0", name="check_pageviews"),
        CheckConstraint("unique_pageviews >= 0", name="check_unique_pageviews"),
        CheckConstraint("users >= 0", name="check_users"),
        CheckConstraint("new_users >= 0", name="check_new_users"),
        CheckConstraint("conversions >= 0", name="check_conversions"),
        CheckConstraint("bounce_rate >= 0 AND bounce_rate <= 100", name="check_bounce_rate"),
        CheckConstraint("exit_rate >= 0 AND exit_rate <= 100", name="check_exit_rate"),
        CheckConstraint("conversion_rate >= 0 AND conversion_rate <= 100", name="check_conversion_rate"),
        Index("idx_website_date_source", "date", "traffic_source"),
    )

    def __repr__(self):
        return f"<WebsiteAnalytics(id={self.id}, date='{self.date}', pageviews={self.pageviews})>"


class EmailMetrics(Base):
    """
    Stores email marketing campaign metrics for tracking email performance.

    Attributes:
        id: Primary key
        campaign_id: Email campaign identifier
        campaign_name: Campaign name
        send_date: When email was sent
        list_id: Email list identifier
        list_name: Email list name
        subject_line: Email subject line
        from_name: Sender name
        from_email: Sender email address
        emails_sent: Total emails sent
        emails_delivered: Total emails delivered
        emails_bounced: Total bounced emails
        hard_bounces: Hard bounces
        soft_bounces: Soft bounces
        opens: Total opens
        unique_opens: Unique opens
        open_rate: Open rate percentage
        clicks: Total clicks
        unique_clicks: Unique clicks
        click_rate: Click rate percentage
        click_to_open_rate: Click-to-open rate percentage
        unsubscribes: Total unsubscribes
        unsubscribe_rate: Unsubscribe rate percentage
        spam_reports: Spam complaint count
        conversions: Number of conversions from email
        conversion_rate: Conversion rate percentage
        revenue: Revenue generated from email (in USD)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "email_metrics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Campaign Identification
    campaign_id = Column(String(100), nullable=False, index=True, unique=True)
    campaign_name = Column(String(500), nullable=False)
    send_date = Column(DateTime, nullable=False, index=True)

    # List Information
    list_id = Column(String(100), index=True)
    list_name = Column(String(500))

    # Email Content
    subject_line = Column(String(500))
    from_name = Column(String(200))
    from_email = Column(String(200))

    # Delivery Metrics
    emails_sent = Column(Integer, default=0, nullable=False)
    emails_delivered = Column(Integer, default=0, nullable=False)
    emails_bounced = Column(Integer, default=0, nullable=False)
    hard_bounces = Column(Integer, default=0, nullable=False)
    soft_bounces = Column(Integer, default=0, nullable=False)

    # Engagement Metrics
    opens = Column(Integer, default=0, nullable=False)
    unique_opens = Column(Integer, default=0, nullable=False)
    open_rate = Column(Numeric(5, 2))  # Percentage
    clicks = Column(Integer, default=0, nullable=False)
    unique_clicks = Column(Integer, default=0, nullable=False)
    click_rate = Column(Numeric(5, 2))  # Percentage
    click_to_open_rate = Column(Numeric(5, 2))  # Percentage

    # Negative Metrics
    unsubscribes = Column(Integer, default=0, nullable=False)
    unsubscribe_rate = Column(Numeric(5, 2))  # Percentage
    spam_reports = Column(Integer, default=0, nullable=False)

    # Conversion Metrics
    conversions = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Numeric(5, 2))  # Percentage
    revenue = Column(Numeric(12, 2))  # USD

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Table constraints
    __table_args__ = (
        CheckConstraint("emails_sent >= 0", name="check_emails_sent"),
        CheckConstraint("emails_delivered >= 0", name="check_emails_delivered"),
        CheckConstraint("emails_bounced >= 0", name="check_emails_bounced"),
        CheckConstraint("hard_bounces >= 0", name="check_hard_bounces"),
        CheckConstraint("soft_bounces >= 0", name="check_soft_bounces"),
        CheckConstraint("opens >= 0", name="check_opens"),
        CheckConstraint("unique_opens >= 0", name="check_unique_opens"),
        CheckConstraint("clicks >= 0", name="check_clicks"),
        CheckConstraint("unique_clicks >= 0", name="check_unique_clicks"),
        CheckConstraint("unsubscribes >= 0", name="check_unsubscribes"),
        CheckConstraint("spam_reports >= 0", name="check_spam_reports"),
        CheckConstraint("conversions >= 0", name="check_conversions"),
        CheckConstraint("open_rate >= 0 AND open_rate <= 100", name="check_open_rate"),
        CheckConstraint("click_rate >= 0 AND click_rate <= 100", name="check_click_rate"),
        CheckConstraint("click_to_open_rate >= 0 AND click_to_open_rate <= 100", name="check_cto_rate"),
        CheckConstraint("unsubscribe_rate >= 0 AND unsubscribe_rate <= 100", name="check_unsub_rate"),
        CheckConstraint("conversion_rate >= 0 AND conversion_rate <= 100", name="check_email_conversion_rate"),
        Index("idx_email_campaign_date", "campaign_id", "send_date"),
    )

    def __repr__(self):
        return f"<EmailMetrics(id={self.id}, campaign_id='{self.campaign_id}', open_rate={self.open_rate})>"


class SalesData(Base):
    """
    Stores unified sales data from all channels (TikTok Shop, website, etc.).

    Attributes:
        id: Primary key
        order_id: Unique order identifier
        order_date: Date of order
        channel: Sales channel (tiktok_shop, website, etc.)
        customer_id: Customer identifier
        customer_email: Customer email (hashed for privacy)
        product_id: Product identifier
        product_name: Product name
        product_sku: Product SKU
        quantity: Quantity ordered
        unit_price: Price per unit (in USD)
        subtotal: Subtotal amount (in USD)
        tax: Tax amount (in USD)
        shipping: Shipping cost (in USD)
        discount: Discount amount (in USD)
        total: Total order amount (in USD)
        currency: Currency code (default USD)
        payment_method: Payment method used
        order_status: Order status (pending, completed, cancelled, refunded)
        fulfillment_status: Fulfillment status (unfulfilled, fulfilled, shipped, delivered)
        attribution_source: Marketing attribution source
        attribution_medium: Marketing attribution medium
        attribution_campaign: Marketing attribution campaign
        first_touch_source: First touch attribution
        last_touch_source: Last touch attribution
        customer_type: Customer type (new, returning)
        country: Customer country
        region: Customer region/state
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "sales_data"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Order Identification
    order_id = Column(String(100), nullable=False, index=True, unique=True)
    order_date = Column(DateTime, nullable=False, index=True)
    channel = Column(String(50), nullable=False, index=True)

    # Customer Information
    customer_id = Column(String(100), index=True)
    customer_email = Column(String(255))  # Should be hashed

    # Product Information
    product_id = Column(String(100), index=True)
    product_name = Column(String(500))
    product_sku = Column(String(100), index=True)

    # Order Details
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax = Column(Numeric(12, 2), default=0)
    shipping = Column(Numeric(12, 2), default=0)
    discount = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")

    # Payment Information
    payment_method = Column(String(100))

    # Order Status
    order_status = Column(String(50), nullable=False, default="pending")
    fulfillment_status = Column(String(50), default="unfulfilled")

    # Marketing Attribution
    attribution_source = Column(String(100), index=True)
    attribution_medium = Column(String(100))
    attribution_campaign = Column(String(200), index=True)
    first_touch_source = Column(String(100))
    last_touch_source = Column(String(100))

    # Customer Segmentation
    customer_type = Column(String(50))  # new, returning
    country = Column(String(100))
    region = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Table constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity"),
        CheckConstraint("unit_price >= 0", name="check_unit_price"),
        CheckConstraint("subtotal >= 0", name="check_subtotal"),
        CheckConstraint("tax >= 0", name="check_tax"),
        CheckConstraint("shipping >= 0", name="check_shipping"),
        CheckConstraint("discount >= 0", name="check_discount"),
        CheckConstraint("total >= 0", name="check_total"),
        CheckConstraint(
            "channel IN ('tiktok_shop', 'website', 'amazon', 'other')",
            name="check_channel"
        ),
        CheckConstraint(
            "order_status IN ('pending', 'completed', 'cancelled', 'refunded')",
            name="check_order_status"
        ),
        CheckConstraint(
            "fulfillment_status IN ('unfulfilled', 'fulfilled', 'shipped', 'delivered', 'cancelled')",
            name="check_fulfillment_status"
        ),
        CheckConstraint(
            "customer_type IN ('new', 'returning', NULL)",
            name="check_customer_type"
        ),
        Index("idx_sales_date_channel", "order_date", "channel"),
        Index("idx_sales_attribution", "attribution_source", "attribution_campaign"),
    )

    def __repr__(self):
        return f"<SalesData(id={self.id}, order_id='{self.order_id}', total={self.total})>"
