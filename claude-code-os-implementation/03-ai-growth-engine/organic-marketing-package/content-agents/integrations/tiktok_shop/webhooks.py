"""
TikTok Shop Webhook Handler

This module provides webhook handling functionality for TikTok Shop events,
including cart updates, order events, and inventory changes.
"""
import hmac
import hashlib
import time
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopValidationError
)

# Configure logging
logger = logging.getLogger(__name__)


class TikTokShopWebhookHandler:
    """
    Handler for TikTok Shop webhook events

    This class provides functionality for:
    - Validating webhook signatures
    - Parsing webhook payloads
    - Processing different webhook event types
    - Handling cart-related webhook events

    Attributes:
        app_secret: TikTok Shop application secret for signature validation
        event_handlers: Dictionary mapping event types to handler functions
    """

    # Webhook signature algorithm
    SIGNATURE_ALGORITHM = "sha256"

    # Maximum timestamp drift allowed (5 minutes)
    MAX_TIMESTAMP_DRIFT = 300

    # Supported webhook event types
    CART_UPDATED_EVENT = "cart_updated"
    CART_ABANDONED_EVENT = "cart_abandoned"
    ORDER_CREATED_EVENT = "order_created"
    ORDER_UPDATED_EVENT = "order_updated"

    def __init__(self, app_secret: str):
        """
        Initialize webhook handler

        Args:
            app_secret: TikTok Shop application secret for signature validation

        Raises:
            TikTokShopAuthError: If app_secret is missing

        Example:
            >>> handler = TikTokShopWebhookHandler('app_secret')
            >>> handler.register_handler('cart_updated', process_cart_update)
        """
        if not app_secret:
            raise TikTokShopAuthError(
                "Missing required credential: app_secret is required for webhook validation"
            )

        self.app_secret = app_secret
        self.event_handlers: Dict[str, Callable] = {}

        logger.info("TikTok Shop webhook handler initialized")

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler function for a specific event type

        Args:
            event_type: Type of webhook event (e.g., 'cart_updated')
            handler: Callable function to handle the event

        Example:
            >>> handler = TikTokShopWebhookHandler('app_secret')
            >>> handler.register_handler('cart_updated', lambda data: print(data))
        """
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    def validate_signature(
        self,
        payload: str,
        signature: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Validate webhook signature to ensure authenticity

        This method verifies that the webhook request came from TikTok Shop
        by validating the HMAC signature.

        Args:
            payload: Raw webhook payload string
            signature: Signature provided in webhook headers
            timestamp: Request timestamp (Unix timestamp as string)

        Returns:
            True if signature is valid, False otherwise

        Raises:
            TikTokShopValidationError: If signature validation fails

        Example:
            >>> handler = TikTokShopWebhookHandler('app_secret')
            >>> is_valid = handler.validate_signature(payload, signature, timestamp)
            >>> if not is_valid:
            ...     raise Exception("Invalid webhook signature")
        """
        try:
            # Check timestamp if provided (prevent replay attacks)
            if timestamp:
                try:
                    timestamp_int = int(timestamp)
                    current_time = int(time.time())
                    drift = abs(current_time - timestamp_int)

                    if drift > self.MAX_TIMESTAMP_DRIFT:
                        logger.warning(
                            f"Webhook timestamp drift too large: {drift}s "
                            f"(max: {self.MAX_TIMESTAMP_DRIFT}s)"
                        )
                        raise TikTokShopValidationError(
                            f"Webhook timestamp drift exceeds maximum allowed: {drift}s",
                            status_code=400
                        )
                except ValueError:
                    logger.warning(f"Invalid timestamp format: {timestamp}")
                    raise TikTokShopValidationError(
                        "Invalid timestamp format",
                        status_code=400
                    )

            # Compute expected signature
            # TikTok Shop signature format: HMAC-SHA256(app_secret, payload)
            message = payload.encode('utf-8')
            secret = self.app_secret.encode('utf-8')
            expected_signature = hmac.new(
                secret,
                message,
                hashlib.sha256
            ).hexdigest()

            # Compare signatures (constant-time comparison to prevent timing attacks)
            is_valid = hmac.compare_digest(expected_signature, signature)

            if not is_valid:
                logger.warning("Webhook signature validation failed")
                raise TikTokShopAuthError(
                    "Invalid webhook signature",
                    status_code=401
                )

            logger.debug("Webhook signature validated successfully")
            return True

        except (TikTokShopValidationError, TikTokShopAuthError):
            raise
        except Exception as e:
            logger.error(f"Error validating webhook signature: {str(e)}", exc_info=True)
            raise TikTokShopValidationError(
                f"Signature validation failed: {str(e)}",
                status_code=400
            )

    def parse_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate webhook payload

        Args:
            payload: Raw webhook payload dictionary

        Returns:
            Parsed and validated payload data

        Raises:
            TikTokShopValidationError: If payload is invalid

        Example:
            >>> handler = TikTokShopWebhookHandler('app_secret')
            >>> parsed = handler.parse_payload(raw_payload)
            >>> event_type = parsed['event_type']
        """
        try:
            # Validate required fields
            if 'event_type' not in payload:
                raise TikTokShopValidationError(
                    "Missing required field: event_type",
                    status_code=400
                )

            event_type = payload['event_type']

            # Validate event type
            valid_events = [
                self.CART_UPDATED_EVENT,
                self.CART_ABANDONED_EVENT,
                self.ORDER_CREATED_EVENT,
                self.ORDER_UPDATED_EVENT
            ]

            if event_type not in valid_events:
                logger.warning(f"Unknown event type received: {event_type}")
                # Don't raise error for unknown events, just log and continue
                # This allows handling new event types gracefully

            logger.info(f"Parsed webhook payload: event_type={event_type}")

            return payload

        except TikTokShopValidationError:
            raise
        except Exception as e:
            logger.error(f"Error parsing webhook payload: {str(e)}", exc_info=True)
            raise TikTokShopValidationError(
                f"Failed to parse webhook payload: {str(e)}",
                status_code=400
            )

    def process_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook event

        This method routes the event to the appropriate handler based on event type.

        Args:
            payload: Validated webhook payload

        Returns:
            Result from the event handler

        Raises:
            TikTokShopAPIError: If event processing fails

        Example:
            >>> handler = TikTokShopWebhookHandler('app_secret')
            >>> handler.register_handler('cart_updated', process_cart)
            >>> result = handler.process_event(payload)
        """
        try:
            event_type = payload.get('event_type')

            logger.info(f"Processing webhook event: {event_type}")

            # Check if handler is registered for this event type
            if event_type not in self.event_handlers:
                logger.warning(
                    f"No handler registered for event type: {event_type}. "
                    "Event will be acknowledged but not processed."
                )
                return {
                    'success': True,
                    'message': f"Event acknowledged (no handler for {event_type})"
                }

            # Call the registered handler
            handler = self.event_handlers[event_type]
            result = handler(payload)

            logger.info(f"Successfully processed {event_type} event")

            return result

        except Exception as e:
            logger.error(
                f"Error processing webhook event: {str(e)}",
                exc_info=True
            )
            raise TikTokShopAPIError(
                f"Failed to process webhook event: {str(e)}",
                status_code=500
            )

    def handle_cart_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle cart-related webhook events

        This method processes cart update and cart abandoned events from TikTok Shop.

        Args:
            payload: Webhook payload containing cart data

        Returns:
            Dictionary containing processed cart information

        Raises:
            TikTokShopValidationError: If cart data is invalid

        Example:
            >>> handler = TikTokShopWebhookHandler('app_secret')
            >>> cart_data = handler.handle_cart_event(payload)
            >>> cart_id = cart_data['cart_id']
        """
        try:
            event_type = payload.get('event_type')
            cart_data = payload.get('cart_data', {})

            # Validate cart data
            if not cart_data:
                raise TikTokShopValidationError(
                    "Missing cart_data in webhook payload",
                    status_code=400
                )

            # Extract cart information
            result = {
                'event_type': event_type,
                'cart_id': cart_data.get('cart_id'),
                'user_email': cart_data.get('user_email') or cart_data.get('email'),
                'user_id': cart_data.get('user_id'),
                'items': cart_data.get('items', []),
                'total_value': cart_data.get('total_value', 0),
                'currency': cart_data.get('currency', 'USD'),
                'cart_url': cart_data.get('cart_url'),
                'timestamp': cart_data.get('timestamp') or int(time.time()),
                'platform': 'tiktok_shop'
            }

            # Validate required fields
            if not result['user_email']:
                raise TikTokShopValidationError(
                    "Missing required field: user_email or email in cart_data",
                    status_code=400
                )

            if not result['items']:
                logger.warning("Cart event received with no items")

            logger.info(
                f"Processed cart event: cart_id={result['cart_id']}, "
                f"email={result['user_email']}, items={len(result['items'])}"
            )

            return result

        except TikTokShopValidationError:
            raise
        except Exception as e:
            logger.error(f"Error handling cart event: {str(e)}", exc_info=True)
            raise TikTokShopValidationError(
                f"Failed to process cart event: {str(e)}",
                status_code=400
            )


def create_webhook_handler(app_secret: str) -> TikTokShopWebhookHandler:
    """
    Factory function to create a configured webhook handler

    Args:
        app_secret: TikTok Shop application secret

    Returns:
        Configured TikTokShopWebhookHandler instance

    Example:
        >>> handler = create_webhook_handler('app_secret')
        >>> handler.register_handler('cart_updated', process_cart_update)
    """
    return TikTokShopWebhookHandler(app_secret)
