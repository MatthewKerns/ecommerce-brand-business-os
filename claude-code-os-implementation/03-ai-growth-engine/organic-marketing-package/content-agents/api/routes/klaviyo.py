"""
Klaviyo email marketing integration routes.

This module defines API endpoints for Klaviyo operations including profile management,
list management, event tracking, and segmentation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import time

from api.dependencies import get_request_id
from api.models import ErrorResponse
from pydantic import BaseModel, Field, EmailStr
from integrations.klaviyo.client import KlaviyoClient
from integrations.klaviyo.models import KlaviyoProfile, KlaviyoEvent, KlaviyoList, ProfileLocation
from integrations.klaviyo.exceptions import (
    KlaviyoAPIError,
    KlaviyoAuthError,
    KlaviyoRateLimitError,
    KlaviyoValidationError,
    KlaviyoNotFoundError
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/klaviyo",
    tags=["klaviyo"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class ProfileLocationRequest(BaseModel):
    """Request model for profile location data."""
    address1: Optional[str] = Field(
        None,
        max_length=200,
        description="First line of address"
    )
    address2: Optional[str] = Field(
        None,
        max_length=200,
        description="Second line of address"
    )
    city: Optional[str] = Field(
        None,
        max_length=100,
        description="City name"
    )
    country: Optional[str] = Field(
        None,
        max_length=100,
        description="Country name or code"
    )
    region: Optional[str] = Field(
        None,
        max_length=100,
        description="State/province/region"
    )
    zip: Optional[str] = Field(
        None,
        max_length=20,
        description="Postal/ZIP code"
    )
    timezone: Optional[str] = Field(
        None,
        description="IANA timezone (e.g., 'America/New_York')"
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Geographic latitude"
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Geographic longitude"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "city": "San Francisco",
                "region": "CA",
                "country": "United States",
                "zip": "94102",
                "timezone": "America/Los_Angeles"
            }
        }


class ProfileRequest(BaseModel):
    """Request model for creating or updating a profile."""
    email: EmailStr = Field(
        ...,
        description="Email address (required)"
    )
    phone_number: Optional[str] = Field(
        None,
        description="Phone number with country code (e.g., +1234567890)"
    )
    external_id: Optional[str] = Field(
        None,
        description="External ID from your system"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=100,
        description="First name"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Last name"
    )
    organization: Optional[str] = Field(
        None,
        max_length=200,
        description="Organization name"
    )
    title: Optional[str] = Field(
        None,
        max_length=100,
        description="Job title"
    )
    location: Optional[ProfileLocationRequest] = Field(
        None,
        description="Geographic location"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom properties"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "customer@example.com",
                "phone_number": "+14155551234",
                "first_name": "John",
                "last_name": "Doe",
                "external_id": "customer_12345",
                "location": {
                    "city": "San Francisco",
                    "region": "CA",
                    "country": "United States",
                    "zip": "94102"
                },
                "properties": {
                    "customer_tier": "VIP",
                    "lifetime_value": 5000.00
                }
            }
        }


class EventRequest(BaseModel):
    """Request model for tracking events."""
    metric_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the event/metric (e.g., 'Placed Order', 'Viewed Product')"
    )
    customer_email: EmailStr = Field(
        ...,
        description="Email of the customer who triggered the event"
    )
    customer_phone: Optional[str] = Field(
        None,
        description="Phone number of the customer"
    )
    customer_external_id: Optional[str] = Field(
        None,
        description="External ID of the customer"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Event properties (e.g., product details, order value)"
    )
    time: Optional[datetime] = Field(
        None,
        description="Timestamp of the event (defaults to now)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Placed Order",
                "customer_email": "customer@example.com",
                "properties": {
                    "order_id": "ORD-12345",
                    "total": 149.99,
                    "items": [
                        {
                            "product_id": "PROD-001",
                            "name": "Tactical Backpack",
                            "price": 149.99,
                            "quantity": 1
                        }
                    ]
                }
            }
        }


class ProfileSearchRequest(BaseModel):
    """Request model for searching profiles."""
    email: Optional[EmailStr] = Field(
        None,
        description="Email to search for"
    )
    phone_number: Optional[str] = Field(
        None,
        description="Phone number to search for"
    )
    external_id: Optional[str] = Field(
        None,
        description="External ID to search for"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "customer@example.com"
            }
        }


class AddToListRequest(BaseModel):
    """Request model for adding profiles to a list."""
    profile_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of Klaviyo profile IDs to add to the list"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "profile_ids": ["01H5X...", "01H5Y..."]
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class ProfileResponse(BaseModel):
    """Response model for profile operations."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    profile_id: str = Field(
        ...,
        description="Klaviyo profile ID"
    )
    email: str = Field(
        ...,
        description="Profile email address"
    )
    status: str = Field(
        default="success",
        description="Status of the operation"
    )
    message: str = Field(
        ...,
        description="Human-readable status message"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the operation"
    )


class EventResponse(BaseModel):
    """Response model for event tracking."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    event_id: Optional[str] = Field(
        None,
        description="Event ID (if returned by Klaviyo)"
    )
    metric_name: str = Field(
        ...,
        description="Name of the tracked event"
    )
    status: str = Field(
        default="success",
        description="Status of the operation"
    )
    message: str = Field(
        ...,
        description="Human-readable status message"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the operation"
    )


class ListResponse(BaseModel):
    """Response model for list operations."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    list_id: str = Field(
        ...,
        description="Klaviyo list ID"
    )
    list_name: str = Field(
        ...,
        description="List name"
    )
    profile_count: Optional[int] = Field(
        None,
        description="Number of profiles in the list"
    )
    status: str = Field(
        default="success",
        description="Status of the operation"
    )
    message: str = Field(
        ...,
        description="Human-readable status message"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the operation"
    )


class ListsResponse(BaseModel):
    """Response model for listing all lists."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    lists: List[Dict[str, Any]] = Field(
        ...,
        description="Array of Klaviyo lists"
    )
    count: int = Field(
        ...,
        description="Number of lists returned"
    )
    status: str = Field(
        default="success",
        description="Status of the operation"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the operation"
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/profiles",
    response_model=ProfileResponse,
    summary="Create or update a profile",
    description="Create a new customer profile or update an existing one in Klaviyo"
)
async def create_or_update_profile(
    request: ProfileRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Create or update a customer profile in Klaviyo.

    Args:
        request: Profile data
        request_id: Unique request identifier

    Returns:
        Profile response with created/updated profile info

    Raises:
        HTTPException: If profile operation fails
    """
    logger.info(f"[{request_id}] Creating/updating profile: email='{request.email}'")
    start_time = time.time()

    try:
        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Convert location request to ProfileLocation if provided
        location = None
        if request.location:
            location = ProfileLocation(
                address1=request.location.address1,
                address2=request.location.address2,
                city=request.location.city,
                country=request.location.country,
                region=request.location.region,
                zip=request.location.zip,
                timezone=request.location.timezone,
                latitude=request.location.latitude,
                longitude=request.location.longitude
            )

        # Create profile object
        profile = KlaviyoProfile(
            email=request.email,
            phone_number=request.phone_number,
            external_id=request.external_id,
            first_name=request.first_name,
            last_name=request.last_name,
            organization=request.organization,
            title=request.title,
            location=location,
            properties=request.properties or {}
        )

        # Create or update profile
        result = client.create_or_update_profile(profile)

        # Extract profile ID from result
        profile_id = result.get("id", "")

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"[{request_id}] Successfully created/updated profile "
            f"(profile_id={profile_id}) in {processing_time_ms}ms"
        )

        return {
            "request_id": request_id,
            "profile_id": profile_id,
            "email": request.email,
            "status": "success",
            "message": "Profile created/updated successfully",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except KlaviyoValidationError as e:
        logger.error(f"[{request_id}] Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "KlaviyoValidationError",
                "message": f"Invalid profile data: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except KlaviyoRateLimitError as e:
        logger.error(f"[{request_id}] Rate limit error: {e}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "KlaviyoRateLimitError",
                "message": "Rate limit exceeded. Please try again later.",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error creating/updating profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ProfileOperationError",
                "message": f"Failed to create/update profile: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/profiles/{profile_id}",
    response_model=Dict[str, Any],
    summary="Get a profile by ID",
    description="Retrieve a customer profile from Klaviyo by profile ID"
)
async def get_profile(
    profile_id: str,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Get a customer profile by ID.

    Args:
        profile_id: Klaviyo profile ID
        request_id: Unique request identifier

    Returns:
        Profile data

    Raises:
        HTTPException: If profile retrieval fails
    """
    logger.info(f"[{request_id}] Fetching profile: profile_id='{profile_id}'")
    start_time = time.time()

    try:
        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Get profile
        result = client.get_profile(profile_id)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"[{request_id}] Successfully fetched profile in {processing_time_ms}ms")

        return {
            "request_id": request_id,
            "profile": result,
            "status": "success",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoNotFoundError as e:
        logger.error(f"[{request_id}] Profile not found: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ProfileNotFound",
                "message": f"Profile not found: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ProfileFetchError",
                "message": f"Failed to fetch profile: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/profiles/search",
    response_model=Dict[str, Any],
    summary="Search for profiles",
    description="Search for customer profiles by email, phone, or external ID"
)
async def search_profiles(
    request: ProfileSearchRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Search for customer profiles.

    Args:
        request: Search criteria
        request_id: Unique request identifier

    Returns:
        Matching profiles

    Raises:
        HTTPException: If search fails
    """
    logger.info(f"[{request_id}] Searching profiles")
    start_time = time.time()

    try:
        # Validate at least one search criterion is provided
        if not any([request.email, request.phone_number, request.external_id]):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ValidationError",
                    "message": "At least one search criterion (email, phone_number, or external_id) must be provided",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Search profiles
        result = client.search_profiles(
            email=request.email,
            phone_number=request.phone_number,
            external_id=request.external_id
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"[{request_id}] Successfully searched profiles in {processing_time_ms}ms")

        return {
            "request_id": request_id,
            "profiles": result.get("data", []),
            "count": len(result.get("data", [])),
            "status": "success",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error searching profiles: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ProfileSearchError",
                "message": f"Failed to search profiles: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/events",
    response_model=EventResponse,
    summary="Track an event",
    description="Track a customer event in Klaviyo (e.g., purchase, page view, custom event)"
)
async def track_event(
    request: EventRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Track a customer event.

    Args:
        request: Event data
        request_id: Unique request identifier

    Returns:
        Event response confirming the event was tracked

    Raises:
        HTTPException: If event tracking fails
    """
    logger.info(f"[{request_id}] Tracking event: metric='{request.metric_name}'")
    start_time = time.time()

    try:
        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Create event object
        event = KlaviyoEvent(
            metric_name=request.metric_name,
            customer_email=request.customer_email,
            customer_phone=request.customer_phone,
            customer_external_id=request.customer_external_id,
            properties=request.properties or {},
            time=request.time
        )

        # Track event
        result = client.track_event(event)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"[{request_id}] Successfully tracked event "
            f"'{request.metric_name}' in {processing_time_ms}ms"
        )

        return {
            "request_id": request_id,
            "event_id": result.get("id"),
            "metric_name": request.metric_name,
            "status": "success",
            "message": "Event tracked successfully",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except KlaviyoValidationError as e:
        logger.error(f"[{request_id}] Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "KlaviyoValidationError",
                "message": f"Invalid event data: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error tracking event: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "EventTrackingError",
                "message": f"Failed to track event: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/lists",
    response_model=ListsResponse,
    summary="Get all lists",
    description="Retrieve all email lists from Klaviyo"
)
async def get_lists(
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Get all email lists.

    Args:
        request_id: Unique request identifier

    Returns:
        Lists response with all lists

    Raises:
        HTTPException: If list retrieval fails
    """
    logger.info(f"[{request_id}] Fetching all lists")
    start_time = time.time()

    try:
        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Get all lists
        result = client.get_lists()

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        lists = result.get("data", [])
        logger.info(
            f"[{request_id}] Successfully fetched {len(lists)} lists "
            f"in {processing_time_ms}ms"
        )

        return {
            "request_id": request_id,
            "lists": lists,
            "count": len(lists),
            "status": "success",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching lists: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ListFetchError",
                "message": f"Failed to fetch lists: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/lists/{list_id}/profiles",
    response_model=ListResponse,
    summary="Add profiles to a list",
    description="Add one or more customer profiles to an email list"
)
async def add_profiles_to_list(
    list_id: str,
    request: AddToListRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Add profiles to an email list.

    Args:
        list_id: Klaviyo list ID
        request: Profile IDs to add
        request_id: Unique request identifier

    Returns:
        List response confirming profiles were added

    Raises:
        HTTPException: If operation fails
    """
    logger.info(
        f"[{request_id}] Adding {len(request.profile_ids)} profiles to list '{list_id}'"
    )
    start_time = time.time()

    try:
        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Add profiles to list
        result = client.add_profiles_to_list(list_id, request.profile_ids)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"[{request_id}] Successfully added {len(request.profile_ids)} profiles "
            f"to list in {processing_time_ms}ms"
        )

        return {
            "request_id": request_id,
            "list_id": list_id,
            "list_name": result.get("attributes", {}).get("name", "Unknown"),
            "profile_count": len(request.profile_ids),
            "status": "success",
            "message": f"Successfully added {len(request.profile_ids)} profiles to list",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoNotFoundError as e:
        logger.error(f"[{request_id}] List not found: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ListNotFound",
                "message": f"List not found: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error adding profiles to list: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ListOperationError",
                "message": f"Failed to add profiles to list: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.delete(
    "/lists/{list_id}/profiles/{profile_id}",
    response_model=ListResponse,
    summary="Remove a profile from a list",
    description="Remove a customer profile from an email list"
)
async def remove_profile_from_list(
    list_id: str,
    profile_id: str,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Remove a profile from an email list.

    Args:
        list_id: Klaviyo list ID
        profile_id: Klaviyo profile ID
        request_id: Unique request identifier

    Returns:
        List response confirming profile was removed

    Raises:
        HTTPException: If operation fails
    """
    logger.info(f"[{request_id}] Removing profile '{profile_id}' from list '{list_id}'")
    start_time = time.time()

    try:
        # Initialize Klaviyo client
        client = KlaviyoClient()

        # Remove profile from list
        result = client.remove_profiles_from_list(list_id, [profile_id])

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"[{request_id}] Successfully removed profile from list "
            f"in {processing_time_ms}ms"
        )

        return {
            "request_id": request_id,
            "list_id": list_id,
            "list_name": result.get("attributes", {}).get("name", "Unknown"),
            "profile_count": None,
            "status": "success",
            "message": "Successfully removed profile from list",
            "timestamp": datetime.utcnow()
        }

    except KlaviyoNotFoundError as e:
        logger.error(f"[{request_id}] List or profile not found: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ResourceNotFound",
                "message": f"List or profile not found: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except KlaviyoAuthError as e:
        logger.error(f"[{request_id}] Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "KlaviyoAuthError",
                "message": f"Klaviyo authentication failed: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error removing profile from list: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ListOperationError",
                "message": f"Failed to remove profile from list: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
