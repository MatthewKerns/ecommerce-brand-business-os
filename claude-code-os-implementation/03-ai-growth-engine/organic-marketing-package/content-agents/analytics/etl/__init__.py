"""
ETL pipelines for ingesting analytics data from various channels.
Provides data ingestion modules for TikTok, website, email, and sales data.
"""
from .tiktok_ingestion import ingest_tiktok_metrics
from .website_ingestion import ingest_website_analytics
from .email_ingestion import ingest_email_metrics
from .sales_ingestion import ingest_sales_data

__all__ = [
    "ingest_tiktok_metrics",
    "ingest_website_analytics",
    "ingest_email_metrics",
    "ingest_sales_data",
]
