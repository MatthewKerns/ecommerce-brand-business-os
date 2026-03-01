"""
Services Package

This package contains business logic services for the AI Content Agents system.
Services handle complex operations that involve multiple components, external APIs,
and database transactions.

Available Services:
    - PublishingService: Handles publishing scheduled content to TikTok Shop
    - NotificationService: Handles notifications for publishing events
    - CartService: Handles abandoned cart tracking and recovery business logic
    - EmailService: Handles email delivery via SendGrid for cart recovery
"""

from .publishing_service import PublishingService
from .notification_service import NotificationService
from .cart_service import CartService
from .email_service import EmailService

__all__ = [
    "PublishingService",
    "NotificationService",
    "CartService",
    "EmailService"
]
