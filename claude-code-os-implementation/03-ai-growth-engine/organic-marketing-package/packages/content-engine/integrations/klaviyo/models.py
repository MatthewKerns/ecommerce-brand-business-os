"""
Klaviyo API Data Models

Data models for Klaviyo profiles, events, lists, and segmentation.
These models represent the core entities used in Klaviyo's email marketing API operations.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProfileSubscriptionStatus(str, Enum):
    """Klaviyo profile subscription status values"""
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    NEVER_SUBSCRIBED = "never_subscribed"


class ListOptInProcess(str, Enum):
    """Klaviyo list opt-in process types"""
    SINGLE_OPT_IN = "single_opt_in"
    DOUBLE_OPT_IN = "double_opt_in"


class ConsentStatus(str, Enum):
    """Email/SMS consent status values"""
    SUBSCRIBED = "SUBSCRIBED"
    UNSUBSCRIBED = "UNSUBSCRIBED"
    NEVER_SUBSCRIBED = "NEVER_SUBSCRIBED"


@dataclass
class ProfileLocation:
    """
    Geographic location data for a profile

    Attributes:
        address1: First line of address
        address2: Optional second line of address
        city: City name
        country: Country name or code
        region: State/province/region
        zip: Postal/ZIP code
        timezone: IANA timezone (e.g., 'America/New_York')
        latitude: Geographic latitude
        longitude: Geographic longitude
    """
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    zip: Optional[str] = None
    timezone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_klaviyo_dict(self) -> Dict[str, Any]:
        """
        Convert to Klaviyo API location format

        Returns:
            Dictionary formatted for Klaviyo API requests
        """
        location_dict = {}

        if self.address1:
            location_dict["address1"] = self.address1
        if self.address2:
            location_dict["address2"] = self.address2
        if self.city:
            location_dict["city"] = self.city
        if self.country:
            location_dict["country"] = self.country
        if self.region:
            location_dict["region"] = self.region
        if self.zip:
            location_dict["zip"] = self.zip
        if self.timezone:
            location_dict["timezone"] = self.timezone
        if self.latitude is not None:
            location_dict["latitude"] = self.latitude
        if self.longitude is not None:
            location_dict["longitude"] = self.longitude

        return location_dict


@dataclass
class KlaviyoProfile:
    """
    Klaviyo customer profile

    Represents a customer/contact in Klaviyo's system with all associated
    demographic and behavioral data.

    Attributes:
        email: Primary email address (required for most operations)
        profile_id: Klaviyo's unique profile ID (set by API)
        external_id: Your system's unique ID for this customer
        phone_number: Phone number in E.164 format (e.g., +14155552671)
        first_name: First/given name
        last_name: Last/family name
        organization: Company/organization name
        title: Job title
        image: URL to profile image
        location: Geographic location data
        properties: Custom properties/attributes (flexible key-value pairs)
        subscription_status: Email subscription status
        subscribed_at: When profile subscribed to email
        unsubscribed_at: When profile unsubscribed from email
        created: When profile was created in Klaviyo
        updated: When profile was last updated
    """
    email: Optional[str] = None
    profile_id: Optional[str] = None
    external_id: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    title: Optional[str] = None
    image: Optional[str] = None
    location: Optional[ProfileLocation] = None
    properties: Optional[Dict[str, Any]] = None
    subscription_status: Optional[ProfileSubscriptionStatus] = None
    subscribed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    def to_klaviyo_dict(self) -> Dict[str, Any]:
        """
        Convert to Klaviyo API profile format

        Returns:
            Dictionary formatted for Klaviyo API createProfile/updateProfile request
        """
        attributes = {}

        if self.email:
            attributes["email"] = self.email
        if self.external_id:
            attributes["external_id"] = self.external_id
        if self.phone_number:
            attributes["phone_number"] = self.phone_number
        if self.first_name:
            attributes["first_name"] = self.first_name
        if self.last_name:
            attributes["last_name"] = self.last_name
        if self.organization:
            attributes["organization"] = self.organization
        if self.title:
            attributes["title"] = self.title
        if self.image:
            attributes["image"] = self.image
        if self.location:
            attributes["location"] = self.location.to_klaviyo_dict()
        if self.properties:
            attributes["properties"] = self.properties

        profile_dict = {
            "type": "profile",
            "attributes": attributes
        }

        # Include profile_id if updating existing profile
        if self.profile_id:
            profile_dict["id"] = self.profile_id

        return {"data": profile_dict}

    @classmethod
    def from_klaviyo_response(cls, response_data: Dict[str, Any]) -> "KlaviyoProfile":
        """
        Create KlaviyoProfile from API response

        Args:
            response_data: Response data from Klaviyo API

        Returns:
            KlaviyoProfile instance populated from response
        """
        data = response_data.get("data", {})
        attributes = data.get("attributes", {})
        profile_id = data.get("id")

        location_data = attributes.get("location")
        location = None
        if location_data:
            location = ProfileLocation(**location_data)

        return cls(
            profile_id=profile_id,
            email=attributes.get("email"),
            external_id=attributes.get("external_id"),
            phone_number=attributes.get("phone_number"),
            first_name=attributes.get("first_name"),
            last_name=attributes.get("last_name"),
            organization=attributes.get("organization"),
            title=attributes.get("title"),
            image=attributes.get("image"),
            location=location,
            properties=attributes.get("properties"),
            created=attributes.get("created"),
            updated=attributes.get("updated")
        )


@dataclass
class KlaviyoEvent:
    """
    Klaviyo event for tracking customer actions

    Represents a behavioral event (purchase, page view, email open, etc.)
    associated with a customer profile.

    Attributes:
        event_name: Name of the event (e.g., 'Placed Order', 'Viewed Product')
        profile: Profile identifier (email, phone, or profile_id)
        timestamp: When the event occurred (defaults to current time)
        event_id: Unique event ID (optional, for deduplication)
        value: Monetary value associated with event (e.g., order total)
        properties: Custom event properties (e.g., product details, order items)
        metric_id: Klaviyo metric ID (set by API)
        profile_id: Associated profile ID (set by API)
    """
    event_name: str
    profile: Dict[str, str]  # {"email": "..."} or {"phone_number": "..."} or {"id": "..."}
    timestamp: Optional[datetime] = None
    event_id: Optional[str] = None
    value: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None
    metric_id: Optional[str] = None
    profile_id: Optional[str] = None

    def to_klaviyo_dict(self) -> Dict[str, Any]:
        """
        Convert to Klaviyo API event format

        Returns:
            Dictionary formatted for Klaviyo API createEvent request
        """
        attributes = {
            "metric": {"data": {"type": "metric", "attributes": {"name": self.event_name}}},
            "profile": {"data": {"type": "profile", "attributes": self.profile}}
        }

        # Add timestamp (use current time if not specified)
        if self.timestamp:
            attributes["time"] = self.timestamp.isoformat()
        else:
            attributes["time"] = datetime.utcnow().isoformat()

        # Add optional unique event ID for deduplication
        if self.event_id:
            attributes["unique_id"] = self.event_id

        # Add monetary value if present
        if self.value is not None:
            attributes["value"] = self.value

        # Add custom properties
        if self.properties:
            attributes["properties"] = self.properties

        event_dict = {
            "type": "event",
            "attributes": attributes
        }

        return {"data": event_dict}

    @classmethod
    def from_klaviyo_response(cls, response_data: Dict[str, Any]) -> "KlaviyoEvent":
        """
        Create KlaviyoEvent from API response

        Args:
            response_data: Response data from Klaviyo API

        Returns:
            KlaviyoEvent instance populated from response
        """
        data = response_data.get("data", {})
        attributes = data.get("attributes", {})

        # Extract metric name
        metric_data = attributes.get("metric", {}).get("data", {})
        metric_attrs = metric_data.get("attributes", {})
        event_name = metric_attrs.get("name", "")

        # Extract profile identifier
        profile_data = attributes.get("profile", {}).get("data", {})
        profile_attrs = profile_data.get("attributes", {})

        timestamp_str = attributes.get("time")
        timestamp = None
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return cls(
            event_name=event_name,
            profile=profile_attrs,
            timestamp=timestamp,
            event_id=attributes.get("unique_id"),
            value=attributes.get("value"),
            properties=attributes.get("properties"),
            metric_id=metric_data.get("id"),
            profile_id=profile_data.get("id")
        )


@dataclass
class KlaviyoList:
    """
    Klaviyo email list

    Represents an email list/segment for organizing and targeting subscribers.

    Attributes:
        name: List name (required for creation)
        list_id: Klaviyo's unique list ID (set by API)
        opt_in_process: How subscribers are added (single or double opt-in)
        created: When list was created
        updated: When list was last updated
        profile_count: Number of profiles in the list
        folder: Folder name for organization
    """
    name: str
    list_id: Optional[str] = None
    opt_in_process: Optional[ListOptInProcess] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    profile_count: Optional[int] = None
    folder: Optional[str] = None

    def to_klaviyo_dict(self) -> Dict[str, Any]:
        """
        Convert to Klaviyo API list format

        Returns:
            Dictionary formatted for Klaviyo API createList/updateList request
        """
        attributes = {
            "name": self.name
        }

        if self.opt_in_process:
            attributes["opt_in_process"] = self.opt_in_process.value

        list_dict = {
            "type": "list",
            "attributes": attributes
        }

        # Include list_id if updating existing list
        if self.list_id:
            list_dict["id"] = self.list_id

        return {"data": list_dict}

    @classmethod
    def from_klaviyo_response(cls, response_data: Dict[str, Any]) -> "KlaviyoList":
        """
        Create KlaviyoList from API response

        Args:
            response_data: Response data from Klaviyo API

        Returns:
            KlaviyoList instance populated from response
        """
        data = response_data.get("data", {})
        attributes = data.get("attributes", {})
        list_id = data.get("id")

        # Parse opt-in process
        opt_in_str = attributes.get("opt_in_process")
        opt_in_process = None
        if opt_in_str:
            try:
                opt_in_process = ListOptInProcess(opt_in_str)
            except ValueError:
                pass

        # Parse timestamps
        created_str = attributes.get("created")
        created = None
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        updated_str = attributes.get("updated")
        updated = None
        if updated_str:
            try:
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return cls(
            list_id=list_id,
            name=attributes.get("name", ""),
            opt_in_process=opt_in_process,
            created=created,
            updated=updated,
            profile_count=attributes.get("profile_count"),
            folder=attributes.get("folder")
        )


@dataclass
class KlaviyoSegment:
    """
    Klaviyo segment definition

    Represents a dynamic segment for targeting customers based on criteria.

    Attributes:
        name: Segment name
        segment_id: Klaviyo's unique segment ID (set by API)
        definition: Segment filter definition (criteria for inclusion)
        created: When segment was created
        updated: When segment was last updated
        profile_count: Estimated number of profiles in segment
    """
    name: str
    segment_id: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    profile_count: Optional[int] = None

    def to_klaviyo_dict(self) -> Dict[str, Any]:
        """
        Convert to Klaviyo API segment format

        Returns:
            Dictionary formatted for Klaviyo API createSegment/updateSegment request
        """
        attributes = {
            "name": self.name
        }

        if self.definition:
            attributes["definition"] = self.definition

        segment_dict = {
            "type": "segment",
            "attributes": attributes
        }

        # Include segment_id if updating existing segment
        if self.segment_id:
            segment_dict["id"] = self.segment_id

        return {"data": segment_dict}

    @classmethod
    def from_klaviyo_response(cls, response_data: Dict[str, Any]) -> "KlaviyoSegment":
        """
        Create KlaviyoSegment from API response

        Args:
            response_data: Response data from Klaviyo API

        Returns:
            KlaviyoSegment instance populated from response
        """
        data = response_data.get("data", {})
        attributes = data.get("attributes", {})
        segment_id = data.get("id")

        # Parse timestamps
        created_str = attributes.get("created")
        created = None
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        updated_str = attributes.get("updated")
        updated = None
        if updated_str:
            try:
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return cls(
            segment_id=segment_id,
            name=attributes.get("name", ""),
            definition=attributes.get("definition"),
            created=created,
            updated=updated,
            profile_count=attributes.get("profile_count")
        )


@dataclass
class ListMembership:
    """
    Relationship between a profile and a list

    Used for adding/removing profiles to/from lists.

    Attributes:
        profile_id: Klaviyo profile ID or identifier dict
        list_id: Klaviyo list ID
        subscribed: Whether profile is subscribed to the list
        consent_status: Email consent status
    """
    profile_id: str
    list_id: str
    subscribed: bool = True
    consent_status: Optional[ConsentStatus] = None

    def to_klaviyo_dict(self) -> Dict[str, Any]:
        """
        Convert to Klaviyo API list membership format

        Returns:
            Dictionary formatted for Klaviyo API list subscription requests
        """
        # For adding profiles to lists
        return {
            "data": [
                {
                    "type": "profile",
                    "id": self.profile_id
                }
            ]
        }


@dataclass
class MetricAggregate:
    """
    Aggregated metric data for reporting

    Attributes:
        metric_id: Klaviyo metric ID
        metric_name: Metric name (e.g., 'Placed Order')
        count: Number of events
        unique_count: Number of unique profiles who triggered event
        total_value: Sum of all event values
        average_value: Average event value
        date_start: Start of aggregation period
        date_end: End of aggregation period
    """
    metric_id: str
    metric_name: str
    count: int = 0
    unique_count: int = 0
    total_value: Optional[float] = None
    average_value: Optional[float] = None
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None

    @classmethod
    def from_klaviyo_response(cls, response_data: Dict[str, Any]) -> "MetricAggregate":
        """
        Create MetricAggregate from API response

        Args:
            response_data: Response data from Klaviyo API

        Returns:
            MetricAggregate instance populated from response
        """
        data = response_data.get("data", {})
        attributes = data.get("attributes", {})

        return cls(
            metric_id=data.get("id", ""),
            metric_name=attributes.get("name", ""),
            count=attributes.get("count", 0),
            unique_count=attributes.get("unique_count", 0),
            total_value=attributes.get("total_value"),
            average_value=attributes.get("average_value"),
            date_start=attributes.get("date_start"),
            date_end=attributes.get("date_end")
        )
