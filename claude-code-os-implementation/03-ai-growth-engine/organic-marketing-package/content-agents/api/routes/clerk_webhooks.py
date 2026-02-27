"""
Clerk webhook endpoints for user sync to Klaviyo.

This module handles incoming webhooks from Clerk for user lifecycle events.
"""

from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import json
import logging
import os
from typing import Optional

# Import webhook handler and Klaviyo client when available
try:
    from integrations.clerk.webhook_handler import ClerkWebhookHandler
    from integrations.klaviyo.client import KlaviyoClient
except ImportError:
    # These will be available after Klaviyo integration is merged
    ClerkWebhookHandler = None
    KlaviyoClient = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/clerk", tags=["webhooks"])

# Initialize webhook handler (will be done after Klaviyo merge)
webhook_handler = None


def get_webhook_handler():
    """Get or initialize the webhook handler."""
    global webhook_handler
    if webhook_handler is None and ClerkWebhookHandler and KlaviyoClient:
        webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
        klaviyo_api_key = os.getenv("KLAVIYO_API_KEY")

        if not webhook_secret:
            logger.error("CLERK_WEBHOOK_SECRET not configured")
            raise ValueError("Clerk webhook secret not configured")

        if not klaviyo_api_key:
            logger.error("KLAVIYO_API_KEY not configured")
            raise ValueError("Klaviyo API key not configured")

        klaviyo_client = KlaviyoClient(api_key=klaviyo_api_key)
        webhook_handler = ClerkWebhookHandler(webhook_secret, klaviyo_client)

    return webhook_handler


@router.post("/")
async def handle_clerk_webhook(
    request: Request,
    svix_id: Optional[str] = Header(None),
    svix_timestamp: Optional[str] = Header(None),
    svix_signature: Optional[str] = Header(None)
):
    """
    Handle incoming Clerk webhooks.

    This endpoint receives webhooks from Clerk for user lifecycle events
    and syncs the data to Klaviyo for email marketing automation.

    Args:
        request: FastAPI request object
        svix_id: Svix webhook ID header
        svix_timestamp: Svix timestamp header
        svix_signature: Svix signature header

    Returns:
        JSONResponse with processing result
    """
    try:
        # Get raw payload for signature verification
        payload = await request.body()

        # Initialize handler
        handler = get_webhook_handler()
        if not handler:
            logger.error("Webhook handler not initialized - Klaviyo integration may not be complete")
            return JSONResponse(
                status_code=503,
                content={"error": "Webhook handler not available"}
            )

        # Verify signature if provided
        if svix_signature:
            if not handler.verify_signature(payload, svix_signature):
                logger.warning("Invalid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse webhook data
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Extract event type and data
        event_type = data.get('type')
        event_data = data.get('data')

        if not event_type or not event_data:
            logger.error("Missing event type or data in webhook")
            raise HTTPException(status_code=400, detail="Missing event type or data")

        # Handle the webhook
        result = handler.handle_webhook(event_type, event_data)

        # Log successful processing
        logger.info(f"Processed Clerk webhook: {event_type}")

        # Track analytics for funnel conversion
        if event_type == 'user.created':
            await track_funnel_conversion(event_data)

        return JSONResponse(
            status_code=200,
            content={"status": "success", "result": result}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error handling Clerk webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


@router.post("/test")
async def test_clerk_webhook():
    """
    Test endpoint to verify Clerk webhook integration is working.

    Returns:
        JSONResponse with configuration status
    """
    webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
    klaviyo_api_key = os.getenv("KLAVIYO_API_KEY")

    status = {
        "clerk_webhook_secret_configured": bool(webhook_secret),
        "klaviyo_api_key_configured": bool(klaviyo_api_key),
        "webhook_handler_available": bool(ClerkWebhookHandler),
        "klaviyo_client_available": bool(KlaviyoClient)
    }

    # Check if handler can be initialized
    try:
        handler = get_webhook_handler()
        status["handler_initialized"] = bool(handler)
    except Exception as e:
        status["handler_initialized"] = False
        status["initialization_error"] = str(e)

    return JSONResponse(content=status)


async def track_funnel_conversion(user_data: dict):
    """
    Track funnel conversion analytics for scratch-win signups.

    Args:
        user_data: User data from Clerk webhook
    """
    try:
        public_metadata = user_data.get('public_metadata', {})

        # Only track if user came from scratch-win
        if public_metadata.get('source') != 'scratch_win':
            return

        # Log conversion for analytics
        # This will be integrated with the analytics pipeline from worktree 013
        logger.info(
            f"Scratch-win conversion: user_id={user_data.get('id')}, "
            f"prize_type={public_metadata.get('prizeType')}"
        )

        # TODO: Send to analytics ETL pipeline after merge
        # analytics.track_event('scratch_win_conversion', {
        #     'user_id': user_data.get('id'),
        #     'prize_type': public_metadata.get('prizeType'),
        #     'timestamp': datetime.utcnow().isoformat()
        # })

    except Exception as e:
        logger.error(f"Error tracking funnel conversion: {str(e)}")


@router.get("/status")
async def webhook_status():
    """
    Check webhook configuration status.

    Returns:
        JSONResponse with detailed configuration status
    """
    return JSONResponse(content={
        "clerk_configured": bool(os.getenv("CLERK_WEBHOOK_SECRET")),
        "klaviyo_configured": bool(os.getenv("KLAVIYO_API_KEY")),
        "handler_available": bool(webhook_handler),
        "endpoints": {
            "webhook": "/api/webhooks/clerk/",
            "test": "/api/webhooks/clerk/test",
            "status": "/api/webhooks/clerk/status"
        }
    })