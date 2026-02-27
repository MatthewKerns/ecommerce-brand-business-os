"""
Klaviyo Sync Service

This module provides the synchronization service for orchestrating data flows between
various sources (TikTok Shop, website, etc.) and Klaviyo email marketing platform.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from integrations.klaviyo.client import KlaviyoClient
from integrations.klaviyo.models import (
    KlaviyoProfile,
    KlaviyoEvent,
    KlaviyoList,
    KlaviyoSegment,
    ProfileLocation
)
from integrations.klaviyo.exceptions import (
    KlaviyoAPIError,
    KlaviyoAuthError,
    KlaviyoValidationError,
    KlaviyoNotFoundError
)
from database.models import (
    KlaviyoProfile as DBKlaviyoProfile,
    KlaviyoSyncHistory,
    KlaviyoSegment as DBKlaviyoSegment
)
from database.connection import get_db_session

# Configure logging
logger = logging.getLogger(__name__)


class KlaviyoSyncService:
    """
    Service for orchestrating data synchronization with Klaviyo

    This service provides high-level methods for syncing customer profiles,
    tracking events, managing lists, and creating segments in Klaviyo.
    It handles:
    - Profile synchronization from multiple sources (TikTok Shop, website, etc.)
    - Order and event tracking
    - List membership management
    - Segment creation and management
    - Sync history tracking in local database

    Attributes:
        client: KlaviyoClient instance for API operations
        db_session: SQLAlchemy database session for tracking sync history
        auto_commit: Whether to automatically commit database changes
    """

    # Default batch size for bulk operations
    DEFAULT_BATCH_SIZE = 100

    # Retry configuration for transient errors
    MAX_RETRY_ATTEMPTS = 3

    # Default list names for customer segments
    DEFAULT_LIST_NAMES = {
        "all_customers": "All Customers",
        "new_subscribers": "New Subscribers",
        "vip_customers": "VIP Customers",
        "active_customers": "Active Customers"
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: Optional[str] = None,
        db_session: Optional[Session] = None,
        auto_commit: bool = True
    ):
        """
        Initialize Klaviyo Sync Service

        Args:
            api_key: Klaviyo private API key (optional, can use environment variable)
            api_base_url: Base URL for Klaviyo API (optional, defaults to production)
            db_session: SQLAlchemy database session (optional, creates new if not provided)
            auto_commit: Whether to automatically commit database changes (default: True)

        Raises:
            KlaviyoAuthError: If required credentials are missing

        Example:
            >>> service = KlaviyoSyncService()
            >>> # Service is ready to sync data

            >>> # With custom session
            >>> with get_db_session() as db:
            ...     service = KlaviyoSyncService(db_session=db, auto_commit=False)
            ...     service.sync_profile(profile_data)
            ...     db.commit()
        """
        self.client = KlaviyoClient(api_key=api_key, api_base_url=api_base_url)
        self.db_session = db_session or get_db_session()
        self.auto_commit = auto_commit
        self._owns_session = db_session is None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session if we own it"""
        if self._owns_session and self.db_session:
            self.db_session.close()

    def _create_sync_history(
        self,
        sync_type: str,
        sync_direction: str = "to_klaviyo",
        profile_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KlaviyoSyncHistory:
        """
        Create a new sync history record

        Args:
            sync_type: Type of sync (profile_sync, event_sync, list_sync, segment_sync, bulk_sync)
            sync_direction: Direction (to_klaviyo, from_klaviyo, bidirectional)
            profile_id: Optional profile ID for profile-specific syncs
            metadata: Optional metadata about the sync operation

        Returns:
            KlaviyoSyncHistory record
        """
        sync_history = KlaviyoSyncHistory(
            profile_id=profile_id,
            sync_type=sync_type,
            sync_direction=sync_direction,
            status="pending",
            records_processed=0,
            records_succeeded=0,
            records_failed=0,
            sync_metadata=str(metadata) if metadata else None,
            started_at=datetime.utcnow()
        )
        self.db_session.add(sync_history)

        if self.auto_commit:
            self.db_session.commit()
        else:
            self.db_session.flush()

        return sync_history

    def _update_sync_history(
        self,
        sync_history: KlaviyoSyncHistory,
        status: str,
        records_processed: int = 0,
        records_succeeded: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update sync history record

        Args:
            sync_history: Sync history record to update
            status: New status (in_progress, completed, failed, partial)
            records_processed: Number of records processed
            records_succeeded: Number of records successfully synced
            records_failed: Number of records that failed
            error_message: Error message if sync failed
            error_details: Detailed error information
        """
        sync_history.status = status
        sync_history.records_processed += records_processed
        sync_history.records_succeeded += records_succeeded
        sync_history.records_failed += records_failed

        if error_message:
            sync_history.error_message = error_message
        if error_details:
            sync_history.error_details = str(error_details)

        if status in ["completed", "failed", "partial"]:
            sync_history.completed_at = datetime.utcnow()
            if sync_history.started_at:
                delta = sync_history.completed_at - sync_history.started_at
                sync_history.duration_ms = int(delta.total_seconds() * 1000)

        if self.auto_commit:
            self.db_session.commit()
        else:
            self.db_session.flush()

    def _save_profile_to_db(
        self,
        klaviyo_profile: KlaviyoProfile
    ) -> DBKlaviyoProfile:
        """
        Save or update Klaviyo profile in local database

        Args:
            klaviyo_profile: KlaviyoProfile from API

        Returns:
            Database KlaviyoProfile record
        """
        # Check if profile already exists
        db_profile = None
        if klaviyo_profile.profile_id:
            db_profile = self.db_session.query(DBKlaviyoProfile).filter(
                DBKlaviyoProfile.klaviyo_profile_id == klaviyo_profile.profile_id
            ).first()

        if db_profile:
            # Update existing profile
            db_profile.email = klaviyo_profile.email
            db_profile.phone_number = klaviyo_profile.phone_number
            db_profile.external_id = klaviyo_profile.external_id
            db_profile.first_name = klaviyo_profile.first_name
            db_profile.last_name = klaviyo_profile.last_name
            db_profile.organization = klaviyo_profile.organization
            db_profile.title = klaviyo_profile.title
            db_profile.image_url = klaviyo_profile.image

            # Update location if provided
            if klaviyo_profile.location:
                db_profile.address1 = klaviyo_profile.location.address1
                db_profile.address2 = klaviyo_profile.location.address2
                db_profile.city = klaviyo_profile.location.city
                db_profile.region = klaviyo_profile.location.region
                db_profile.country = klaviyo_profile.location.country
                db_profile.zip = klaviyo_profile.location.zip
                db_profile.timezone = klaviyo_profile.location.timezone
                db_profile.latitude = klaviyo_profile.location.latitude
                db_profile.longitude = klaviyo_profile.location.longitude

            db_profile.properties = str(klaviyo_profile.properties) if klaviyo_profile.properties else None
            db_profile.last_synced_at = datetime.utcnow()
            db_profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            db_profile = DBKlaviyoProfile(
                klaviyo_profile_id=klaviyo_profile.profile_id,
                email=klaviyo_profile.email,
                phone_number=klaviyo_profile.phone_number,
                external_id=klaviyo_profile.external_id,
                first_name=klaviyo_profile.first_name,
                last_name=klaviyo_profile.last_name,
                organization=klaviyo_profile.organization,
                title=klaviyo_profile.title,
                image_url=klaviyo_profile.image,
                address1=klaviyo_profile.location.address1 if klaviyo_profile.location else None,
                address2=klaviyo_profile.location.address2 if klaviyo_profile.location else None,
                city=klaviyo_profile.location.city if klaviyo_profile.location else None,
                region=klaviyo_profile.location.region if klaviyo_profile.location else None,
                country=klaviyo_profile.location.country if klaviyo_profile.location else None,
                zip=klaviyo_profile.location.zip if klaviyo_profile.location else None,
                timezone=klaviyo_profile.location.timezone if klaviyo_profile.location else None,
                latitude=klaviyo_profile.location.latitude if klaviyo_profile.location else None,
                longitude=klaviyo_profile.location.longitude if klaviyo_profile.location else None,
                properties=str(klaviyo_profile.properties) if klaviyo_profile.properties else None,
                last_synced_at=datetime.utcnow()
            )
            self.db_session.add(db_profile)

        if self.auto_commit:
            self.db_session.commit()
        else:
            self.db_session.flush()

        return db_profile

    # ============================================================================
    # Profile Sync Methods
    # ============================================================================

    def sync_profile(
        self,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        external_id: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[KlaviyoProfile, DBKlaviyoProfile]:
        """
        Sync a single customer profile to Klaviyo

        This method creates or updates a customer profile in Klaviyo and
        saves it to the local database for tracking.

        Args:
            email: Customer email address
            phone_number: Phone number in E.164 format
            external_id: External system ID (e.g., from TikTok Shop)
            first_name: First/given name
            last_name: Last/family name
            location: Location data dictionary
            properties: Custom properties/attributes
            **kwargs: Additional profile attributes

        Returns:
            Tuple of (KlaviyoProfile from API, DBKlaviyoProfile from database)

        Raises:
            KlaviyoValidationError: If profile data is invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> api_profile, db_profile = service.sync_profile(
            ...     email="customer@example.com",
            ...     first_name="John",
            ...     last_name="Doe",
            ...     properties={"source": "tiktok_shop"}
            ... )
            >>> print(api_profile.profile_id)
        """
        # Create sync history record
        sync_history = self._create_sync_history(
            sync_type="profile_sync",
            sync_direction="to_klaviyo",
            metadata={"email": email, "external_id": external_id}
        )

        try:
            # Update status to in_progress
            self._update_sync_history(sync_history, "in_progress")

            # Build location object if provided
            profile_location = None
            if location:
                profile_location = ProfileLocation(**location)

            # Create Klaviyo profile object
            profile = KlaviyoProfile(
                email=email,
                phone_number=phone_number,
                external_id=external_id,
                first_name=first_name,
                last_name=last_name,
                location=profile_location,
                properties=properties,
                **kwargs
            )

            # Check if profile already exists in Klaviyo
            existing_profiles = []
            if email:
                try:
                    existing_profiles = self.client.search_profiles(email=email)
                except KlaviyoNotFoundError:
                    pass

            # Create or update profile in Klaviyo
            if existing_profiles:
                profile.profile_id = existing_profiles[0].profile_id
                api_profile = self.client.update_profile(profile)
                logger.info(f"Updated Klaviyo profile: {api_profile.profile_id}")
            else:
                api_profile = self.client.create_profile(profile)
                logger.info(f"Created Klaviyo profile: {api_profile.profile_id}")

            # Save to local database
            db_profile = self._save_profile_to_db(api_profile)

            # Update sync history
            self._update_sync_history(
                sync_history,
                status="completed",
                records_processed=1,
                records_succeeded=1
            )

            return api_profile, db_profile

        except Exception as e:
            # Update sync history with error
            self._update_sync_history(
                sync_history,
                status="failed",
                records_processed=1,
                records_failed=1,
                error_message=str(e),
                error_details={"type": type(e).__name__}
            )
            logger.error(f"Failed to sync profile: {str(e)}")
            raise

    def sync_profiles_bulk(
        self,
        profiles: List[Dict[str, Any]],
        batch_size: Optional[int] = None
    ) -> Tuple[List[KlaviyoProfile], List[DBKlaviyoProfile], Dict[str, int]]:
        """
        Sync multiple customer profiles to Klaviyo in batches

        Args:
            profiles: List of profile data dictionaries
            batch_size: Number of profiles to process per batch (default: DEFAULT_BATCH_SIZE)

        Returns:
            Tuple of (list of synced API profiles, list of DB profiles, stats dict)
            Stats dict contains: processed, succeeded, failed

        Example:
            >>> profiles = [
            ...     {"email": "customer1@example.com", "first_name": "John"},
            ...     {"email": "customer2@example.com", "first_name": "Jane"}
            ... ]
            >>> api_profiles, db_profiles, stats = service.sync_profiles_bulk(profiles)
            >>> print(f"Synced {stats['succeeded']} of {stats['processed']} profiles")
        """
        batch_size = batch_size or self.DEFAULT_BATCH_SIZE

        # Create sync history record
        sync_history = self._create_sync_history(
            sync_type="bulk_sync",
            sync_direction="to_klaviyo",
            metadata={"total_profiles": len(profiles), "batch_size": batch_size}
        )

        api_profiles = []
        db_profiles = []
        stats = {"processed": 0, "succeeded": 0, "failed": 0}

        try:
            self._update_sync_history(sync_history, "in_progress")

            # Process profiles in batches
            for i in range(0, len(profiles), batch_size):
                batch = profiles[i:i + batch_size]

                for profile_data in batch:
                    stats["processed"] += 1

                    try:
                        api_profile, db_profile = self.sync_profile(**profile_data)
                        api_profiles.append(api_profile)
                        db_profiles.append(db_profile)
                        stats["succeeded"] += 1

                    except Exception as e:
                        stats["failed"] += 1
                        logger.warning(
                            f"Failed to sync profile {profile_data.get('email', 'unknown')}: {str(e)}"
                        )

            # Determine final status
            if stats["failed"] == 0:
                status = "completed"
            elif stats["succeeded"] == 0:
                status = "failed"
            else:
                status = "partial"

            # Update sync history
            self._update_sync_history(
                sync_history,
                status=status,
                records_processed=stats["processed"],
                records_succeeded=stats["succeeded"],
                records_failed=stats["failed"]
            )

            logger.info(
                f"Bulk sync completed: {stats['succeeded']} succeeded, "
                f"{stats['failed']} failed out of {stats['processed']} total"
            )

            return api_profiles, db_profiles, stats

        except Exception as e:
            self._update_sync_history(
                sync_history,
                status="failed",
                error_message=str(e),
                error_details={"type": type(e).__name__}
            )
            logger.error(f"Bulk sync failed: {str(e)}")
            raise

    # ============================================================================
    # Event Tracking Methods
    # ============================================================================

    def track_event(
        self,
        event_name: str,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_external_id: Optional[str] = None,
        value: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track a customer event in Klaviyo

        Args:
            event_name: Name of the event (e.g., 'Placed Order', 'Viewed Product')
            customer_email: Customer email address
            customer_phone: Customer phone number
            customer_external_id: Customer external ID
            value: Monetary value (e.g., order total)
            properties: Custom event properties
            timestamp: When event occurred (defaults to now)
            event_id: Unique event ID for deduplication

        Returns:
            API response data

        Raises:
            KlaviyoValidationError: If event data is invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> service.track_event(
            ...     event_name="Placed Order",
            ...     customer_email="customer@example.com",
            ...     value=99.99,
            ...     properties={"order_id": "12345", "items": 3}
            ... )
        """
        # Create sync history record
        sync_history = self._create_sync_history(
            sync_type="event_sync",
            sync_direction="to_klaviyo",
            metadata={"event_name": event_name}
        )

        try:
            self._update_sync_history(sync_history, "in_progress")

            # Build profile identifier
            profile = {}
            if customer_email:
                profile["email"] = customer_email
            if customer_phone:
                profile["phone_number"] = customer_phone
            if customer_external_id:
                profile["external_id"] = customer_external_id

            if not profile:
                raise KlaviyoValidationError(
                    "At least one customer identifier (email, phone, or external_id) is required"
                )

            # Create event object
            event = KlaviyoEvent(
                event_name=event_name,
                profile=profile,
                timestamp=timestamp,
                event_id=event_id,
                value=value,
                properties=properties
            )

            # Track event in Klaviyo
            response = self.client.track_event(event)
            logger.info(f"Tracked event '{event_name}' for customer {customer_email or customer_phone}")

            # Update sync history
            self._update_sync_history(
                sync_history,
                status="completed",
                records_processed=1,
                records_succeeded=1
            )

            return response

        except Exception as e:
            self._update_sync_history(
                sync_history,
                status="failed",
                records_processed=1,
                records_failed=1,
                error_message=str(e),
                error_details={"type": type(e).__name__}
            )
            logger.error(f"Failed to track event: {str(e)}")
            raise

    def track_events_bulk(
        self,
        events: List[Dict[str, Any]],
        batch_size: Optional[int] = None
    ) -> Tuple[int, int, int]:
        """
        Track multiple events in Klaviyo

        Args:
            events: List of event data dictionaries
            batch_size: Number of events to process per batch

        Returns:
            Tuple of (processed_count, succeeded_count, failed_count)

        Example:
            >>> events = [
            ...     {
            ...         "event_name": "Viewed Product",
            ...         "customer_email": "customer@example.com",
            ...         "properties": {"product_id": "123"}
            ...     }
            ... ]
            >>> processed, succeeded, failed = service.track_events_bulk(events)
        """
        batch_size = batch_size or self.DEFAULT_BATCH_SIZE

        sync_history = self._create_sync_history(
            sync_type="bulk_sync",
            sync_direction="to_klaviyo",
            metadata={"total_events": len(events), "batch_size": batch_size}
        )

        processed = 0
        succeeded = 0
        failed = 0

        try:
            self._update_sync_history(sync_history, "in_progress")

            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]

                for event_data in batch:
                    processed += 1

                    try:
                        self.track_event(**event_data)
                        succeeded += 1

                    except Exception as e:
                        failed += 1
                        logger.warning(
                            f"Failed to track event {event_data.get('event_name', 'unknown')}: {str(e)}"
                        )

            # Determine final status
            if failed == 0:
                status = "completed"
            elif succeeded == 0:
                status = "failed"
            else:
                status = "partial"

            self._update_sync_history(
                sync_history,
                status=status,
                records_processed=processed,
                records_succeeded=succeeded,
                records_failed=failed
            )

            return processed, succeeded, failed

        except Exception as e:
            self._update_sync_history(
                sync_history,
                status="failed",
                error_message=str(e)
            )
            raise

    # ============================================================================
    # List Management Methods
    # ============================================================================

    def get_or_create_list(self, list_name: str) -> KlaviyoList:
        """
        Get existing list by name or create if it doesn't exist

        Args:
            list_name: Name of the list

        Returns:
            KlaviyoList object

        Example:
            >>> vip_list = service.get_or_create_list("VIP Customers")
            >>> print(vip_list.list_id)
        """
        try:
            # Get all lists and search by name
            lists = self.client.get_lists(limit=100)
            for lst in lists:
                if lst.name == list_name:
                    logger.info(f"Found existing list: {list_name}")
                    return lst

            # Create new list if not found
            new_list = KlaviyoList(name=list_name)
            created_list = self.client.create_list(new_list)
            logger.info(f"Created new list: {list_name}")
            return created_list

        except Exception as e:
            logger.error(f"Failed to get or create list '{list_name}': {str(e)}")
            raise

    def add_profile_to_list(
        self,
        list_id: str,
        profile_id: str
    ) -> Dict[str, Any]:
        """
        Add a profile to an email list

        Args:
            list_id: Klaviyo list ID
            profile_id: Klaviyo profile ID

        Returns:
            API response data

        Example:
            >>> service.add_profile_to_list("ABC123", "01HXYZ...")
        """
        return self.client.add_profiles_to_list(list_id, [profile_id])

    def add_profiles_to_list_bulk(
        self,
        list_id: str,
        profile_ids: List[str],
        batch_size: int = 100
    ) -> Tuple[int, int]:
        """
        Add multiple profiles to an email list in batches

        Args:
            list_id: Klaviyo list ID
            profile_ids: List of Klaviyo profile IDs
            batch_size: Number of profiles per batch (max 100 per Klaviyo API)

        Returns:
            Tuple of (total_processed, total_succeeded)

        Example:
            >>> profile_ids = ["01HXYZ1...", "01HXYZ2...", "01HXYZ3..."]
            >>> processed, succeeded = service.add_profiles_to_list_bulk("ABC123", profile_ids)
        """
        total_processed = 0
        total_succeeded = 0

        for i in range(0, len(profile_ids), batch_size):
            batch = profile_ids[i:i + batch_size]
            total_processed += len(batch)

            try:
                self.client.add_profiles_to_list(list_id, batch)
                total_succeeded += len(batch)
                logger.info(f"Added {len(batch)} profiles to list {list_id}")

            except Exception as e:
                logger.warning(f"Failed to add batch to list: {str(e)}")

        return total_processed, total_succeeded

    # ============================================================================
    # Segment Management Methods
    # ============================================================================

    def sync_segments(self) -> List[DBKlaviyoSegment]:
        """
        Sync all segments from Klaviyo to local database

        Returns:
            List of database segment records

        Example:
            >>> segments = service.sync_segments()
            >>> for segment in segments:
            ...     print(f"{segment.name}: {segment.profile_count} profiles")
        """
        sync_history = self._create_sync_history(
            sync_type="segment_sync",
            sync_direction="from_klaviyo"
        )

        db_segments = []

        try:
            self._update_sync_history(sync_history, "in_progress")

            # Get all segments from Klaviyo
            api_segments = self.client.get_segments(limit=100)

            for api_segment in api_segments:
                # Check if segment exists in database
                db_segment = self.db_session.query(DBKlaviyoSegment).filter(
                    DBKlaviyoSegment.klaviyo_segment_id == api_segment.segment_id
                ).first()

                if db_segment:
                    # Update existing segment
                    db_segment.name = api_segment.name
                    db_segment.definition = str(api_segment.definition) if api_segment.definition else None
                    db_segment.profile_count = api_segment.profile_count
                    db_segment.last_synced_at = datetime.utcnow()
                    db_segment.updated_at = datetime.utcnow()
                else:
                    # Create new segment
                    db_segment = DBKlaviyoSegment(
                        klaviyo_segment_id=api_segment.segment_id,
                        name=api_segment.name,
                        segment_type="standard",
                        definition=str(api_segment.definition) if api_segment.definition else None,
                        profile_count=api_segment.profile_count,
                        is_active=True,
                        last_synced_at=datetime.utcnow()
                    )
                    self.db_session.add(db_segment)

                db_segments.append(db_segment)

            if self.auto_commit:
                self.db_session.commit()
            else:
                self.db_session.flush()

            self._update_sync_history(
                sync_history,
                status="completed",
                records_processed=len(api_segments),
                records_succeeded=len(api_segments)
            )

            logger.info(f"Synced {len(api_segments)} segments from Klaviyo")
            return db_segments

        except Exception as e:
            self._update_sync_history(
                sync_history,
                status="failed",
                error_message=str(e)
            )
            logger.error(f"Failed to sync segments: {str(e)}")
            raise

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def get_sync_history(
        self,
        sync_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[KlaviyoSyncHistory]:
        """
        Get sync history records

        Args:
            sync_type: Filter by sync type
            status: Filter by status
            limit: Maximum number of records to return

        Returns:
            List of KlaviyoSyncHistory records

        Example:
            >>> history = service.get_sync_history(sync_type="profile_sync", limit=10)
            >>> for record in history:
            ...     print(f"{record.sync_type}: {record.status}")
        """
        query = self.db_session.query(KlaviyoSyncHistory)

        if sync_type:
            query = query.filter(KlaviyoSyncHistory.sync_type == sync_type)
        if status:
            query = query.filter(KlaviyoSyncHistory.status == status)

        return query.order_by(KlaviyoSyncHistory.created_at.desc()).limit(limit).all()

    def get_profile_by_email(self, email: str) -> Optional[DBKlaviyoProfile]:
        """
        Get profile from local database by email

        Args:
            email: Customer email address

        Returns:
            Database profile record or None if not found

        Example:
            >>> profile = service.get_profile_by_email("customer@example.com")
            >>> if profile:
            ...     print(profile.first_name)
        """
        return self.db_session.query(DBKlaviyoProfile).filter(
            DBKlaviyoProfile.email == email
        ).first()

    def get_profile_by_external_id(self, external_id: str) -> Optional[DBKlaviyoProfile]:
        """
        Get profile from local database by external ID

        Args:
            external_id: External system ID

        Returns:
            Database profile record or None if not found

        Example:
            >>> profile = service.get_profile_by_external_id("tiktok_123456")
            >>> if profile:
            ...     print(profile.email)
        """
        return self.db_session.query(DBKlaviyoProfile).filter(
            DBKlaviyoProfile.external_id == external_id
        ).first()

    # ============================================================================
    # TikTok Shop Integration Methods
    # ============================================================================

    def sync_customers_from_tiktok(
        self,
        tiktok_client,
        page_size: int = 100,
        max_pages: Optional[int] = None,
        order_status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Tuple[List[KlaviyoProfile], Dict[str, int]]:
        """
        Sync customer profiles from TikTok Shop orders to Klaviyo

        This method fetches orders from TikTok Shop, extracts customer information,
        and syncs those customers to Klaviyo. It handles deduplication by checking
        if profiles already exist before creating or updating them.

        Args:
            tiktok_client: TikTokShopClient instance for fetching orders
            page_size: Number of orders to fetch per page (max 100)
            max_pages: Maximum number of pages to process (optional, processes all if not set)
            order_status: Filter by order status (e.g., 'COMPLETED', 'DELIVERED')
            start_time: Start timestamp for order creation time (Unix timestamp)
            end_time: End timestamp for order creation time (Unix timestamp)

        Returns:
            Tuple of (list of synced KlaviyoProfile objects, stats dict)
            Stats dict contains: orders_fetched, customers_found, customers_synced,
                                customers_updated, customers_created, errors

        Raises:
            KlaviyoAPIError: If Klaviyo API requests fail
            TikTokShopAPIError: If TikTok Shop API requests fail

        Example:
            >>> from integrations.tiktok_shop.client import TikTokShopClient
            >>> tiktok_client = TikTokShopClient(app_key, app_secret, access_token)
            >>> profiles, stats = service.sync_customers_from_tiktok(
            ...     tiktok_client,
            ...     order_status='COMPLETED',
            ...     max_pages=10
            ... )
            >>> print(f"Synced {stats['customers_synced']} customers from {stats['orders_fetched']} orders")
        """
        # Create sync history record
        sync_history = self._create_sync_history(
            sync_type="bulk_sync",
            sync_direction="to_klaviyo",
            metadata={
                "source": "tiktok_shop",
                "page_size": page_size,
                "max_pages": max_pages,
                "order_status": order_status
            }
        )

        # Initialize stats tracking
        stats = {
            "orders_fetched": 0,
            "customers_found": 0,
            "customers_synced": 0,
            "customers_updated": 0,
            "customers_created": 0,
            "errors": 0
        }

        synced_profiles = []
        seen_customers = set()  # Track unique customers by email/phone

        try:
            self._update_sync_history(sync_history, "in_progress")
            logger.info("Starting customer sync from TikTok Shop to Klaviyo")

            # Fetch orders from TikTok Shop
            page_number = 1
            has_more = True

            while has_more:
                # Check max_pages limit
                if max_pages and page_number > max_pages:
                    logger.info(f"Reached max_pages limit ({max_pages})")
                    break

                try:
                    # Fetch orders from TikTok Shop
                    logger.info(f"Fetching TikTok Shop orders page {page_number}")
                    response = tiktok_client.get_orders(
                        page_size=page_size,
                        page_number=page_number,
                        order_status=order_status,
                        start_time=start_time,
                        end_time=end_time
                    )

                    # Extract orders from response
                    orders = response.get('data', {}).get('orders', [])
                    stats["orders_fetched"] += len(orders)

                    # Check if more pages exist
                    has_more = response.get('data', {}).get('more', False)

                    # Process each order to extract customer data
                    for order in orders:
                        try:
                            # Extract customer information from order
                            customer_data = self._extract_customer_from_tiktok_order(order)

                            if not customer_data:
                                logger.debug(f"No customer data in order {order.get('order_id')}")
                                continue

                            stats["customers_found"] += 1

                            # Create unique key for deduplication
                            customer_key = customer_data.get("email") or customer_data.get("phone_number")
                            if not customer_key:
                                logger.warning(
                                    f"Order {order.get('order_id')} has no email or phone for customer"
                                )
                                continue

                            # Skip if we've already processed this customer in this sync
                            if customer_key in seen_customers:
                                continue

                            seen_customers.add(customer_key)

                            # Sync customer profile to Klaviyo
                            try:
                                api_profile, db_profile = self.sync_profile(**customer_data)
                                synced_profiles.append(api_profile)
                                stats["customers_synced"] += 1

                                # Track if it was create or update
                                if db_profile.created_at == db_profile.updated_at:
                                    stats["customers_created"] += 1
                                else:
                                    stats["customers_updated"] += 1

                                logger.debug(
                                    f"Synced customer {customer_key} from order {order.get('order_id')}"
                                )

                            except Exception as e:
                                stats["errors"] += 1
                                logger.warning(
                                    f"Failed to sync customer {customer_key}: {str(e)}"
                                )

                        except Exception as e:
                            stats["errors"] += 1
                            logger.warning(
                                f"Failed to process order {order.get('order_id')}: {str(e)}"
                            )

                    # Move to next page
                    page_number += 1

                except Exception as e:
                    # Log error but continue with next page
                    stats["errors"] += 1
                    logger.error(f"Failed to fetch orders page {page_number}: {str(e)}")
                    break

            # Determine final status
            if stats["errors"] == 0:
                status = "completed"
            elif stats["customers_synced"] == 0:
                status = "failed"
            else:
                status = "partial"

            # Update sync history with final stats
            self._update_sync_history(
                sync_history,
                status=status,
                records_processed=stats["customers_found"],
                records_succeeded=stats["customers_synced"],
                records_failed=stats["errors"]
            )

            logger.info(
                f"TikTok Shop customer sync completed: "
                f"{stats['customers_synced']} synced "
                f"({stats['customers_created']} created, {stats['customers_updated']} updated) "
                f"from {stats['orders_fetched']} orders, "
                f"{stats['errors']} errors"
            )

            return synced_profiles, stats

        except Exception as e:
            # Update sync history with error
            self._update_sync_history(
                sync_history,
                status="failed",
                error_message=str(e),
                error_details={"type": type(e).__name__}
            )
            logger.error(f"TikTok Shop customer sync failed: {str(e)}")
            raise

    def _extract_customer_from_tiktok_order(
        self,
        order: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract customer profile data from a TikTok Shop order

        Args:
            order: TikTok Shop order dictionary

        Returns:
            Dictionary of customer data suitable for sync_profile(), or None if insufficient data

        Note:
            TikTok Shop order structure typically includes:
            - recipient_address: Shipping address with name, phone, email, address fields
            - buyer_user_id: TikTok user ID
            - buyer_message: Optional message from buyer
        """
        try:
            # Extract recipient/shipping address (primary source of customer info)
            recipient = order.get('recipient_address', {})

            if not recipient:
                return None

            # Build customer profile data
            customer_data = {}

            # Email (if available)
            email = recipient.get('email') or recipient.get('recipient_email')
            if email:
                customer_data["email"] = email.strip().lower()

            # Phone number
            phone = recipient.get('phone') or recipient.get('phone_number')
            if phone:
                # Clean phone number (remove spaces, dashes)
                customer_data["phone_number"] = phone.replace(" ", "").replace("-", "")

            # Name
            full_name = recipient.get('name') or recipient.get('recipient_name')
            if full_name:
                # Try to split full name into first/last
                name_parts = full_name.strip().split(None, 1)
                if len(name_parts) == 2:
                    customer_data["first_name"] = name_parts[0]
                    customer_data["last_name"] = name_parts[1]
                else:
                    customer_data["first_name"] = name_parts[0]

            # External ID (TikTok Shop user ID or order ID)
            buyer_id = order.get('buyer_user_id') or order.get('buyer_uid')
            order_id = order.get('order_id')

            if buyer_id:
                customer_data["external_id"] = f"tiktok_user_{buyer_id}"
            elif order_id:
                customer_data["external_id"] = f"tiktok_order_{order_id}"

            # Location data
            location = {}

            address1 = recipient.get('address_line1') or recipient.get('address')
            if address1:
                location["address1"] = address1

            address2 = recipient.get('address_line2') or recipient.get('address_detail')
            if address2:
                location["address2"] = address2

            city = recipient.get('city') or recipient.get('district_info', {}).get('city')
            if city:
                location["city"] = city

            region = recipient.get('state') or recipient.get('region')
            if region:
                location["region"] = region

            country = recipient.get('region_code') or recipient.get('country')
            if country:
                location["country"] = country

            zip_code = recipient.get('zipcode') or recipient.get('postal_code')
            if zip_code:
                location["zip"] = zip_code

            if location:
                customer_data["location"] = location

            # Custom properties (order metadata)
            properties = {
                "source": "tiktok_shop",
                "last_order_id": order_id,
                "last_order_status": order.get('order_status'),
                "last_order_date": order.get('create_time')
            }

            # Add payment info if available
            payment = order.get('payment', {})
            if payment:
                properties["last_order_total"] = payment.get('total_amount')
                properties["last_order_currency"] = payment.get('currency')

            customer_data["properties"] = properties

            # Require at least email or phone to proceed
            if not customer_data.get("email") and not customer_data.get("phone_number"):
                return None

            return customer_data

        except Exception as e:
            logger.warning(f"Failed to extract customer data from order: {str(e)}")
            return None

    def sync_order_events(
        self,
        tiktok_client,
        page_size: int = 100,
        max_pages: Optional[int] = None,
        order_status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Tuple[int, Dict[str, int]]:
        """
        Sync order events from TikTok Shop to Klaviyo

        This method fetches orders from TikTok Shop and tracks them as
        "Placed Order" events in Klaviyo for purchase-based segmentation
        and email automation triggers.

        Args:
            tiktok_client: TikTokShopClient instance for fetching orders
            page_size: Number of orders to fetch per page (max 100)
            max_pages: Maximum number of pages to process (optional, processes all if not set)
            order_status: Filter by order status (e.g., 'COMPLETED', 'DELIVERED')
            start_time: Start timestamp for order creation time (Unix timestamp)
            end_time: End timestamp for order creation time (Unix timestamp)

        Returns:
            Tuple of (total events tracked, stats dict)
            Stats dict contains: orders_fetched, events_tracked, events_failed, total_value

        Raises:
            KlaviyoAPIError: If Klaviyo API requests fail
            TikTokShopAPIError: If TikTok Shop API requests fail

        Example:
            >>> from integrations.tiktok_shop.client import TikTokShopClient
            >>> tiktok_client = TikTokShopClient(app_key, app_secret, access_token)
            >>> events_tracked, stats = service.sync_order_events(
            ...     tiktok_client,
            ...     order_status='COMPLETED',
            ...     max_pages=10
            ... )
            >>> print(f"Tracked {stats['events_tracked']} order events worth ${stats['total_value']:.2f}")
        """
        # Create sync history record
        sync_history = self._create_sync_history(
            sync_type="event_sync",
            sync_direction="to_klaviyo",
            metadata={
                "source": "tiktok_shop",
                "event_type": "order_events",
                "page_size": page_size,
                "max_pages": max_pages,
                "order_status": order_status
            }
        )

        # Initialize stats tracking
        stats = {
            "orders_fetched": 0,
            "events_tracked": 0,
            "events_failed": 0,
            "total_value": 0.0
        }

        try:
            self._update_sync_history(sync_history, "in_progress")
            logger.info("Starting order event sync from TikTok Shop to Klaviyo")

            # Fetch orders from TikTok Shop
            page_number = 1
            has_more = True

            while has_more:
                # Check max_pages limit
                if max_pages and page_number > max_pages:
                    logger.info(f"Reached max_pages limit ({max_pages})")
                    break

                try:
                    # Fetch orders from TikTok Shop
                    logger.info(f"Fetching TikTok Shop orders page {page_number}")
                    response = tiktok_client.get_orders(
                        page_size=page_size,
                        page_number=page_number,
                        order_status=order_status,
                        start_time=start_time,
                        end_time=end_time
                    )

                    # Extract orders from response
                    orders = response.get('data', {}).get('orders', [])
                    stats["orders_fetched"] += len(orders)

                    # Check if more pages exist
                    has_more = response.get('data', {}).get('more', False)

                    # Process each order as an event
                    for order in orders:
                        try:
                            # Extract event data from order
                            event_data = self._extract_event_from_tiktok_order(order)

                            if not event_data:
                                logger.debug(f"No event data in order {order.get('order_id')}")
                                stats["events_failed"] += 1
                                continue

                            # Track the order event in Klaviyo
                            try:
                                self.track_event(**event_data)
                                stats["events_tracked"] += 1

                                # Accumulate order value for stats
                                value = event_data.get('value', 0.0)
                                if value:
                                    stats["total_value"] += value

                                logger.debug(
                                    f"Tracked order event for order {order.get('order_id')}"
                                )

                            except Exception as e:
                                stats["events_failed"] += 1
                                logger.warning(
                                    f"Failed to track event for order {order.get('order_id')}: {str(e)}"
                                )

                        except Exception as e:
                            stats["events_failed"] += 1
                            logger.warning(
                                f"Failed to process order {order.get('order_id')}: {str(e)}"
                            )

                    # Move to next page
                    page_number += 1

                except Exception as e:
                    # Log error but continue with next page
                    logger.error(f"Failed to fetch orders page {page_number}: {str(e)}")
                    break

            # Determine final status
            if stats["events_failed"] == 0:
                status = "completed"
            elif stats["events_tracked"] == 0:
                status = "failed"
            else:
                status = "partial"

            # Update sync history with final stats
            self._update_sync_history(
                sync_history,
                status=status,
                records_processed=stats["orders_fetched"],
                records_succeeded=stats["events_tracked"],
                records_failed=stats["events_failed"]
            )

            logger.info(
                f"TikTok Shop order event sync completed: "
                f"{stats['events_tracked']} events tracked "
                f"from {stats['orders_fetched']} orders, "
                f"{stats['events_failed']} failed, "
                f"total value: ${stats['total_value']:.2f}"
            )

            return stats["events_tracked"], stats

        except Exception as e:
            # Update sync history with error
            self._update_sync_history(
                sync_history,
                status="failed",
                error_message=str(e),
                error_details={"type": type(e).__name__}
            )
            logger.error(f"TikTok Shop order event sync failed: {str(e)}")
            raise

    def _extract_event_from_tiktok_order(
        self,
        order: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract Klaviyo event data from a TikTok Shop order

        This method converts a TikTok Shop order into a "Placed Order" event
        for Klaviyo with all relevant order details for segmentation and automation.

        Args:
            order: TikTok Shop order dictionary

        Returns:
            Dictionary of event data suitable for track_event(), or None if insufficient data

        Note:
            TikTok Shop order structure typically includes:
            - order_id: Unique order identifier
            - buyer_user_id: TikTok user ID
            - recipient_address: Shipping address with customer info
            - payment: Payment details including total_amount
            - line_items: List of products in the order
            - order_status: Current order status
            - create_time: Order creation timestamp
        """
        try:
            order_id = order.get('order_id')
            if not order_id:
                return None

            # Extract customer identification
            recipient = order.get('recipient_address', {})
            customer_email = recipient.get('email') or recipient.get('recipient_email')
            customer_phone = recipient.get('phone') or recipient.get('phone_number')

            # Require at least one customer identifier
            if not customer_email and not customer_phone:
                logger.debug(f"Order {order_id} has no customer email or phone")
                return None

            # Clean phone number if present
            if customer_phone:
                customer_phone = customer_phone.replace(" ", "").replace("-", "")

            # Extract external ID
            buyer_id = order.get('buyer_user_id') or order.get('buyer_uid')
            customer_external_id = None
            if buyer_id:
                customer_external_id = f"tiktok_user_{buyer_id}"

            # Extract payment/order value
            payment = order.get('payment', {})
            total_amount = payment.get('total_amount')
            currency = payment.get('currency', 'USD')

            # Convert total_amount to float if it's a string or int
            order_value = None
            if total_amount is not None:
                try:
                    order_value = float(total_amount)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid total_amount in order {order_id}: {total_amount}")

            # Extract line items (products)
            line_items = order.get('line_items', []) or order.get('items', [])
            items_list = []
            item_count = 0

            for item in line_items:
                item_count += item.get('quantity', 1)
                items_list.append({
                    'product_id': item.get('product_id'),
                    'product_name': item.get('product_name') or item.get('sku_name'),
                    'sku_id': item.get('sku_id'),
                    'quantity': item.get('quantity', 1),
                    'price': item.get('sale_price') or item.get('original_price')
                })

            # Build event properties
            properties = {
                'order_id': order_id,
                'order_status': order.get('order_status'),
                'total_price': total_amount,
                'currency': currency,
                'item_count': item_count,
                'items': items_list,
                'source': 'tiktok_shop',
                'shipping_address': {
                    'name': recipient.get('name') or recipient.get('recipient_name'),
                    'address': recipient.get('address_line1') or recipient.get('address'),
                    'city': recipient.get('city'),
                    'region': recipient.get('state') or recipient.get('region'),
                    'country': recipient.get('region_code') or recipient.get('country'),
                    'zip': recipient.get('zipcode') or recipient.get('postal_code')
                }
            }

            # Add payment method if available
            payment_method = payment.get('payment_method')
            if payment_method:
                properties['payment_method'] = payment_method

            # Add tracking number if available
            tracking_number = order.get('tracking_number')
            if tracking_number:
                properties['tracking_number'] = tracking_number

            # Convert order creation time to datetime if available
            timestamp = None
            create_time = order.get('create_time')
            if create_time:
                try:
                    # TikTok Shop typically uses Unix timestamp
                    if isinstance(create_time, int):
                        timestamp = datetime.fromtimestamp(create_time)
                    elif isinstance(create_time, str):
                        # Try to parse ISO format
                        timestamp = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                except Exception as e:
                    logger.warning(f"Failed to parse create_time for order {order_id}: {str(e)}")

            # Build event data for track_event method
            event_data = {
                'event_name': 'Placed Order',
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'customer_external_id': customer_external_id,
                'value': order_value,
                'properties': properties,
                'timestamp': timestamp,
                'event_id': f"tiktok_order_{order_id}"  # For deduplication
            }

            return event_data

        except Exception as e:
            logger.warning(f"Failed to extract event data from order: {str(e)}")
            return None
