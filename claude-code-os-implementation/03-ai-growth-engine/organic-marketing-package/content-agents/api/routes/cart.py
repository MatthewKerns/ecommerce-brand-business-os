"""
Cart tracking and recovery routes.

This module defines API endpoints for abandoned cart tracking and recovery.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import uuid

from api.dependencies import get_request_id
from api.models import ErrorResponse
from pydantic import BaseModel, Field, EmailStr
from services.cart_service import CartService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/cart",
    tags=["cart"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class CartItemRequest(BaseModel):
    """Request model for cart item."""
    product_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique product identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Product name"
    )
    price: float = Field(
        ...,
        gt=0,
        description="Product price"
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Quantity in cart"
    )
    image_url: Optional[str] = Field(
        None,
        max_length=2000,
        description="Product image URL"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-123",
                "name": "Tactical EDC Backpack",
                "price": 89.99,
                "quantity": 1,
                "image_url": "https://example.com/images/backpack.jpg"
            }
        }


class CartTrackRequest(BaseModel):
    """Request model for cart tracking."""
    email: EmailStr = Field(
        ...,
        description="Customer email address"
    )
    cart_items: List[CartItemRequest] = Field(
        ...,
        min_length=1,
        description="Items in the cart"
    )
    source: str = Field(
        default="website",
        pattern="^(website|tiktok_shop)$",
        description="Cart source platform"
    )
    cart_id: Optional[str] = Field(
        None,
        description="Optional cart ID (generated if not provided)"
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional authenticated user ID"
    )
    cart_url: Optional[str] = Field(
        None,
        max_length=2000,
        description="URL to recover the cart"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "customer@example.com",
                "cart_items": [
                    {
                        "product_id": "test-123",
                        "name": "Test Product",
                        "price": 29.99,
                        "quantity": 1
                    }
                ],
                "source": "website"
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class CartTrackResponse(BaseModel):
    """Response model for cart tracking."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    cart_id: str = Field(
        ...,
        description="Cart identifier"
    )
    status: str = Field(
        ...,
        description="Cart status (active, abandoned, recovered)"
    )
    total_value: float = Field(
        ...,
        description="Total cart value"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of tracking event"
    )


class CartRecoveryResponse(BaseModel):
    """Response model for cart recovery."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    cart_id: str = Field(
        ...,
        description="Cart identifier"
    )
    status: str = Field(
        ...,
        description="Recovery status"
    )
    cart_url: Optional[str] = Field(
        None,
        description="URL to redirect customer to"
    )
    message: str = Field(
        ...,
        description="Human-readable message"
    )


class CartAnalyticsResponse(BaseModel):
    """Response model for cart analytics."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    period_days: int = Field(
        ...,
        description="Analysis period in days"
    )
    total_carts: int = Field(
        ...,
        description="Total number of carts tracked"
    )
    abandoned_carts: int = Field(
        ...,
        description="Number of abandoned carts"
    )
    recovered_carts: int = Field(
        ...,
        description="Number of recovered carts"
    )
    recovery_rate: float = Field(
        ...,
        description="Recovery rate percentage"
    )
    total_recovered_value: float = Field(
        ...,
        description="Total revenue recovered"
    )
    email_stats: Dict[str, Any] = Field(
        ...,
        description="Email campaign statistics"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of analytics generation"
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/track",
    response_model=CartTrackResponse,
    status_code=200,
    summary="Track cart event",
    description="Track a cart creation or update event for abandoned cart recovery"
)
async def track_cart(
    request: CartTrackRequest,
    request_id: str = Depends(get_request_id)
) -> CartTrackResponse:
    """
    Track a cart event.

    This endpoint records cart activity for abandoned cart detection and recovery.

    Args:
        request: Cart tracking data including email, items, and source
        request_id: Unique request identifier (injected)

    Returns:
        CartTrackResponse with cart details and status

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    logger.info(
        f"[{request_id}] Tracking cart: email={request.email}, "
        f"items={len(request.cart_items)}, source={request.source}"
    )

    try:
        # Generate cart_id if not provided
        cart_id = request.cart_id or f"cart_{uuid.uuid4().hex[:16]}"

        # Convert cart items to dict format for CartService
        cart_items = [
            {
                "product_id": item.product_id,
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity,
                "image_url": item.image_url
            }
            for item in request.cart_items
        ]

        # Track cart event
        cart_service = CartService()
        cart = cart_service.track_cart_event(
            cart_id=cart_id,
            email=request.email,
            cart_items=cart_items,
            platform=request.source,
            user_id=request.user_id,
            cart_url=request.cart_url
        )

        logger.info(
            f"[{request_id}] Cart tracked successfully: cart_id={cart.cart_id}, "
            f"total_value=${cart.total_value:.2f}"
        )

        return CartTrackResponse(
            request_id=request_id,
            cart_id=cart.cart_id,
            status=cart.status,
            total_value=float(cart.total_value),
            timestamp=cart.updated_at or cart.created_at
        )

    except ValueError as e:
        logger.warning(f"[{request_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error tracking cart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalServerError",
                "message": "Failed to track cart event",
                "request_id": request_id
            }
        )


@router.get(
    "/recover/{cart_id}",
    response_model=CartRecoveryResponse,
    status_code=200,
    summary="Recover cart",
    description="Mark a cart as recovered when customer clicks recovery link"
)
async def recover_cart(
    cart_id: str,
    request_id: str = Depends(get_request_id)
) -> CartRecoveryResponse:
    """
    Handle cart recovery link click.

    This endpoint is called when a customer clicks a cart recovery link in an email.
    It marks the cart as recovered and returns the cart URL for redirection.

    Args:
        cart_id: Cart identifier from recovery link
        request_id: Unique request identifier (injected)

    Returns:
        CartRecoveryResponse with recovery status and redirect URL

    Raises:
        HTTPException: 404 if cart not found, 500 for server errors
    """
    logger.info(f"[{request_id}] Processing cart recovery: cart_id={cart_id}")

    try:
        cart_service = CartService()

        # Get cart details
        cart = cart_service.get_cart_by_id(cart_id)

        if not cart:
            logger.warning(f"[{request_id}] Cart not found: {cart_id}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NotFound",
                    "message": f"Cart not found: {cart_id}",
                    "request_id": request_id
                }
            )

        # Mark cart as recovered
        recovered_cart = cart_service.recover_cart(cart_id)

        logger.info(
            f"[{request_id}] Cart recovered successfully: cart_id={cart_id}, "
            f"value=${recovered_cart.total_value:.2f}"
        )

        return CartRecoveryResponse(
            request_id=request_id,
            cart_id=recovered_cart.cart_id,
            status=recovered_cart.status,
            cart_url=recovered_cart.cart_url,
            message="Cart recovered successfully. Redirecting to checkout..."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error recovering cart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalServerError",
                "message": "Failed to recover cart",
                "request_id": request_id
            }
        )


@router.get(
    "/analytics",
    response_model=CartAnalyticsResponse,
    status_code=200,
    summary="Get cart analytics",
    description="Retrieve abandoned cart and recovery analytics"
)
async def get_cart_analytics(
    days: int = 30,
    request_id: str = Depends(get_request_id)
) -> CartAnalyticsResponse:
    """
    Get cart recovery analytics.

    Returns analytics data including abandonment rates, recovery rates,
    and email performance metrics.

    Args:
        days: Number of days to analyze (default: 30, max: 365)
        request_id: Unique request identifier (injected)

    Returns:
        CartAnalyticsResponse with comprehensive analytics data

    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    logger.info(f"[{request_id}] Getting cart analytics for last {days} days")

    try:
        # Validate days parameter
        if days < 1 or days > 365:
            raise ValueError("days must be between 1 and 365")

        # Get analytics from service
        cart_service = CartService()
        analytics = cart_service.get_recovery_analytics(days=days)

        logger.info(
            f"[{request_id}] Analytics retrieved: "
            f"abandoned={analytics['abandoned_carts']}, "
            f"recovered={analytics['recovered_carts']}, "
            f"rate={analytics['recovery_rate']}%"
        )

        return CartAnalyticsResponse(
            request_id=request_id,
            period_days=analytics["period_days"],
            total_carts=analytics["total_carts"],
            abandoned_carts=analytics["abandoned_carts"],
            recovered_carts=analytics["recovered_carts"],
            recovery_rate=analytics["recovery_rate"],
            total_recovered_value=analytics["total_recovered_value"],
            email_stats=analytics["email_stats"],
            timestamp=datetime.utcnow()
        )

    except ValueError as e:
        logger.warning(f"[{request_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error getting analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve cart analytics",
                "request_id": request_id
            }
        )


@router.get(
    "/{cart_id}",
    status_code=200,
    summary="Get cart details",
    description="Retrieve cart details and items"
)
async def get_cart(
    cart_id: str,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Get cart details.

    Retrieves cart information including status, items, and value.

    Args:
        cart_id: Cart identifier
        request_id: Unique request identifier (injected)

    Returns:
        Dict containing cart details and items

    Raises:
        HTTPException: 404 if cart not found, 500 for server errors
    """
    logger.info(f"[{request_id}] Getting cart details: cart_id={cart_id}")

    try:
        cart_service = CartService()

        # Get cart
        cart = cart_service.get_cart_by_id(cart_id)

        if not cart:
            logger.warning(f"[{request_id}] Cart not found: {cart_id}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NotFound",
                    "message": f"Cart not found: {cart_id}",
                    "request_id": request_id
                }
            )

        # Get cart items
        items = cart_service.get_cart_items(cart_id)

        logger.info(
            f"[{request_id}] Cart details retrieved: cart_id={cart_id}, "
            f"items={len(items)}, status={cart.status}"
        )

        return {
            "request_id": request_id,
            "cart_id": cart.cart_id,
            "email": cart.email,
            "user_id": cart.user_id,
            "platform": cart.platform,
            "status": cart.status,
            "total_value": float(cart.total_value),
            "currency": cart.currency,
            "cart_url": cart.cart_url,
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.product_name,
                    "price": float(item.price),
                    "quantity": item.quantity,
                    "image_url": item.product_image_url
                }
                for item in items
            ],
            "created_at": cart.created_at.isoformat() if cart.created_at else None,
            "updated_at": cart.updated_at.isoformat() if cart.updated_at else None,
            "abandoned_at": cart.abandoned_at.isoformat() if cart.abandoned_at else None,
            "recovered_at": cart.recovered_at.isoformat() if cart.recovered_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting cart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve cart details",
                "request_id": request_id
            }
        )
