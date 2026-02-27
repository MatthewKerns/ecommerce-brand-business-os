"""
ETL pipelines for ingesting analytics data from various channels.
Provides data ingestion modules for TikTok, website, email, and sales data.
"""
from .tiktok_ingestion import ingest_tiktok_metrics
from .website_ingestion import ingest_website_analytics

__all__ = [
    "ingest_tiktok_metrics",
    "ingest_website_analytics",
]
