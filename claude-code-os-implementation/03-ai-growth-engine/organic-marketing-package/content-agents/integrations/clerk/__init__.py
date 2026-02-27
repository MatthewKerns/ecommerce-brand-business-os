"""
Clerk integration for user authentication and sync to Klaviyo.

This module handles Clerk webhooks for syncing user data to Klaviyo
for email marketing automation.
"""

from .webhook_handler import ClerkWebhookHandler

__all__ = ["ClerkWebhookHandler"]