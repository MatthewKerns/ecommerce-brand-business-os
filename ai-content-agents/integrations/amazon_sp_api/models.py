"""
Amazon SP-API MCF Data Models

Data models for Multi-Channel Fulfillment (MCF) orders, inventory, and shipment tracking.
These models represent the core entities used in Amazon's MCF API operations.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ShippingSpeedCategory(str, Enum):
    """MCF shipping speed options"""
    STANDARD = "Standard"
    EXPEDITED = "Expedited"
    PRIORITY = "Priority"


class FulfillmentOrderStatus(str, Enum):
    """MCF fulfillment order status values"""
    RECEIVED = "Received"
    INVALID = "Invalid"
    PLANNING = "Planning"
    PROCESSING = "Processing"
    CANCELLED = "Cancelled"
    COMPLETE = "Complete"
    COMPLETE_PARTIALLED = "CompletePartialled"
    UNFULFILLABLE = "Unfulfillable"


class PackageStatus(str, Enum):
    """MCF package tracking status values"""
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    RETURNING = "RETURNING"
    RETURNED = "RETURNED"
    UNDELIVERABLE = "UNDELIVERABLE"
    DELAYED = "DELAYED"
    AVAILABLE_FOR_PICKUP = "AVAILABLE_FOR_PICKUP"
    CUSTOMER_ACTION = "CUSTOMER_ACTION"


@dataclass
class Address:
    """
    Shipping address for MCF fulfillment orders

    Attributes:
        name: Recipient name
        address_line1: First line of address
        city: City
        state_or_province_code: State/province code (e.g., 'CA', 'TX')
        postal_code: Postal/ZIP code
        country_code: ISO country code (e.g., 'US')
        address_line2: Optional second address line
        address_line3: Optional third address line
        district_or_county: Optional district/county
        phone: Optional phone number
    """
    name: str
    address_line1: str
    city: str
    state_or_province_code: str
    postal_code: str
    country_code: str
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None
    district_or_county: Optional[str] = None
    phone: Optional[str] = None

    def to_sp_api_dict(self) -> Dict[str, str]:
        """
        Convert to Amazon SP-API address format

        Returns:
            Dictionary formatted for SP-API requests
        """
        address_dict = {
            "name": self.name,
            "addressLine1": self.address_line1,
            "city": self.city,
            "stateOrProvinceCode": self.state_or_province_code,
            "postalCode": self.postal_code,
            "countryCode": self.country_code
        }

        if self.address_line2:
            address_dict["addressLine2"] = self.address_line2
        if self.address_line3:
            address_dict["addressLine3"] = self.address_line3
        if self.district_or_county:
            address_dict["districtOrCounty"] = self.district_or_county
        if self.phone:
            address_dict["phone"] = self.phone

        return address_dict


@dataclass
class MCFOrderItem:
    """
    Individual item in an MCF fulfillment order

    Attributes:
        seller_sku: Merchant's SKU for the item
        seller_fulfillment_order_item_id: Unique ID for this item in the order
        quantity: Quantity to fulfill
        per_unit_declared_value: Optional declared value per unit (for insurance)
        per_unit_price: Optional price per unit
    """
    seller_sku: str
    seller_fulfillment_order_item_id: str
    quantity: int
    per_unit_declared_value: Optional[Dict[str, Any]] = None
    per_unit_price: Optional[Dict[str, Any]] = None

    def to_sp_api_dict(self) -> Dict[str, Any]:
        """
        Convert to Amazon SP-API item format

        Returns:
            Dictionary formatted for SP-API requests
        """
        item_dict = {
            "sellerSku": self.seller_sku,
            "sellerFulfillmentOrderItemId": self.seller_fulfillment_order_item_id,
            "quantity": self.quantity
        }

        if self.per_unit_declared_value:
            item_dict["perUnitDeclaredValue"] = self.per_unit_declared_value
        if self.per_unit_price:
            item_dict["perUnitPrice"] = self.per_unit_price

        return item_dict


@dataclass
class MCFFulfillmentOrder:
    """
    Complete MCF fulfillment order

    Attributes:
        seller_fulfillment_order_id: Unique order ID from merchant
        marketplace_id: Amazon marketplace ID
        displayable_order_id: Customer-facing order ID
        displayable_order_date: Customer-facing order date
        displayable_order_comment: Comment to display to customer
        shipping_speed_category: Shipping speed (Standard/Expedited/Priority)
        destination_address: Shipping address
        items: List of items to fulfill
        fulfillment_action: Optional fulfillment action (Ship/Hold)
        fulfillment_policy: Optional fulfillment policy (FillOrKill/FillAll/FillAllAvailable)
        notification_emails: Optional list of notification email addresses
        status: Current order status
        status_updated_date: When status was last updated
        received_date: When order was received by Amazon
    """
    seller_fulfillment_order_id: str
    marketplace_id: str
    displayable_order_id: str
    displayable_order_date: str
    displayable_order_comment: str
    shipping_speed_category: ShippingSpeedCategory
    destination_address: Address
    items: List[MCFOrderItem]
    fulfillment_action: Optional[str] = "Ship"
    fulfillment_policy: Optional[str] = "FillOrKill"
    notification_emails: Optional[List[str]] = None
    status: Optional[FulfillmentOrderStatus] = None
    status_updated_date: Optional[datetime] = None
    received_date: Optional[datetime] = None

    def to_sp_api_dict(self) -> Dict[str, Any]:
        """
        Convert to Amazon SP-API fulfillment order format

        Returns:
            Dictionary formatted for SP-API createFulfillmentOrder request
        """
        order_dict = {
            "sellerFulfillmentOrderId": self.seller_fulfillment_order_id,
            "marketplaceId": self.marketplace_id,
            "displayableOrderId": self.displayable_order_id,
            "displayableOrderDate": self.displayable_order_date,
            "displayableOrderComment": self.displayable_order_comment,
            "shippingSpeedCategory": self.shipping_speed_category.value,
            "destinationAddress": self.destination_address.to_sp_api_dict(),
            "items": [item.to_sp_api_dict() for item in self.items]
        }

        if self.fulfillment_action:
            order_dict["fulfillmentAction"] = self.fulfillment_action
        if self.fulfillment_policy:
            order_dict["fulfillmentPolicy"] = self.fulfillment_policy
        if self.notification_emails:
            order_dict["notificationEmails"] = self.notification_emails

        return order_dict

    @classmethod
    def from_sp_api_response(cls, data: Dict[str, Any]) -> 'MCFFulfillmentOrder':
        """
        Create MCFFulfillmentOrder from SP-API response

        Args:
            data: Response data from SP-API getFulfillmentOrder

        Returns:
            MCFFulfillmentOrder instance
        """
        # Parse address
        address_data = data.get("destinationAddress", {})
        address = Address(
            name=address_data.get("name", ""),
            address_line1=address_data.get("addressLine1", ""),
            city=address_data.get("city", ""),
            state_or_province_code=address_data.get("stateOrProvinceCode", ""),
            postal_code=address_data.get("postalCode", ""),
            country_code=address_data.get("countryCode", ""),
            address_line2=address_data.get("addressLine2"),
            address_line3=address_data.get("addressLine3"),
            district_or_county=address_data.get("districtOrCounty"),
            phone=address_data.get("phone")
        )

        # Parse items
        items = []
        for item_data in data.get("items", []):
            item = MCFOrderItem(
                seller_sku=item_data.get("sellerSku", ""),
                seller_fulfillment_order_item_id=item_data.get("sellerFulfillmentOrderItemId", ""),
                quantity=item_data.get("quantity", 0),
                per_unit_declared_value=item_data.get("perUnitDeclaredValue"),
                per_unit_price=item_data.get("perUnitPrice")
            )
            items.append(item)

        # Parse dates
        status_updated = data.get("statusUpdatedDateTime")
        received = data.get("receivedDateTime")

        return cls(
            seller_fulfillment_order_id=data.get("sellerFulfillmentOrderId", ""),
            marketplace_id=data.get("marketplaceId", ""),
            displayable_order_id=data.get("displayableOrderId", ""),
            displayable_order_date=data.get("displayableOrderDateTime", ""),
            displayable_order_comment=data.get("displayableOrderComment", ""),
            shipping_speed_category=ShippingSpeedCategory(data.get("shippingSpeedCategory", "Standard")),
            destination_address=address,
            items=items,
            fulfillment_action=data.get("fulfillmentAction"),
            fulfillment_policy=data.get("fulfillmentPolicy"),
            notification_emails=data.get("notificationEmails"),
            status=FulfillmentOrderStatus(data["fulfillmentOrderStatus"]) if "fulfillmentOrderStatus" in data else None,
            status_updated_date=datetime.fromisoformat(status_updated.replace('Z', '+00:00')) if status_updated else None,
            received_date=datetime.fromisoformat(received.replace('Z', '+00:00')) if received else None
        )


@dataclass
class MCFPackage:
    """
    MCF package tracking information

    Attributes:
        package_number: Package number assigned by Amazon
        carrier_code: Shipping carrier code (e.g., 'UPS', 'FEDEX')
        tracking_number: Carrier tracking number
        status: Current package status
        estimated_arrival_date: Estimated delivery date
        items: List of items in this package
    """
    package_number: int
    carrier_code: str
    tracking_number: Optional[str] = None
    status: Optional[PackageStatus] = None
    estimated_arrival_date: Optional[datetime] = None
    items: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_sp_api_response(cls, data: Dict[str, Any]) -> 'MCFPackage':
        """
        Create MCFPackage from SP-API response

        Args:
            data: Response data from SP-API package tracking

        Returns:
            MCFPackage instance
        """
        estimated_arrival = data.get("estimatedArrivalDateTime")

        return cls(
            package_number=data.get("packageNumber", 0),
            carrier_code=data.get("carrierCode", ""),
            tracking_number=data.get("trackingNumber"),
            status=PackageStatus(data["currentStatus"]) if "currentStatus" in data else None,
            estimated_arrival_date=datetime.fromisoformat(estimated_arrival.replace('Z', '+00:00')) if estimated_arrival else None,
            items=data.get("packageItems", [])
        )


@dataclass
class MCFShipment:
    """
    MCF shipment with package tracking

    Attributes:
        fulfillment_shipment_id: Amazon shipment ID
        fulfillment_center_id: Amazon fulfillment center ID
        shipment_status: Current shipment status
        packages: List of packages in this shipment
        estimated_arrival_date: Overall estimated delivery date
    """
    fulfillment_shipment_id: str
    fulfillment_center_id: str
    shipment_status: str
    packages: List[MCFPackage] = field(default_factory=list)
    estimated_arrival_date: Optional[datetime] = None

    @classmethod
    def from_sp_api_response(cls, data: Dict[str, Any]) -> 'MCFShipment':
        """
        Create MCFShipment from SP-API response

        Args:
            data: Response data from SP-API shipment tracking

        Returns:
            MCFShipment instance
        """
        packages = [
            MCFPackage.from_sp_api_response(pkg_data)
            for pkg_data in data.get("fulfillmentShipmentPackage", [])
        ]

        estimated_arrival = data.get("estimatedArrivalDateTime")

        return cls(
            fulfillment_shipment_id=data.get("amazonShipmentId", ""),
            fulfillment_center_id=data.get("fulfillmentCenterId", ""),
            shipment_status=data.get("shippingStatus", ""),
            packages=packages,
            estimated_arrival_date=datetime.fromisoformat(estimated_arrival.replace('Z', '+00:00')) if estimated_arrival else None
        )


@dataclass
class MCFInventoryItem:
    """
    MCF inventory item with availability information

    Attributes:
        seller_sku: Merchant's SKU
        fn_sku: Amazon fulfillment network SKU
        asin: Amazon Standard Identification Number
        condition: Item condition (e.g., 'NewItem', 'UsedLikeNew')
        total_quantity: Total quantity in all FC locations
        fulfillable_quantity: Quantity available for fulfillment
        inbound_working_quantity: Quantity in inbound shipments
        inbound_shipped_quantity: Quantity shipped to Amazon
        inbound_receiving_quantity: Quantity being received
    """
    seller_sku: str
    fn_sku: Optional[str] = None
    asin: Optional[str] = None
    condition: str = "NewItem"
    total_quantity: int = 0
    fulfillable_quantity: int = 0
    inbound_working_quantity: int = 0
    inbound_shipped_quantity: int = 0
    inbound_receiving_quantity: int = 0

    @classmethod
    def from_sp_api_response(cls, data: Dict[str, Any]) -> 'MCFInventoryItem':
        """
        Create MCFInventoryItem from SP-API response

        Args:
            data: Response data from SP-API inventory query

        Returns:
            MCFInventoryItem instance
        """
        return cls(
            seller_sku=data.get("sellerSku", ""),
            fn_sku=data.get("fnSku"),
            asin=data.get("asin"),
            condition=data.get("condition", "NewItem"),
            total_quantity=data.get("totalQuantity", 0),
            fulfillable_quantity=data.get("fulfillableQuantity", 0),
            inbound_working_quantity=data.get("inboundWorkingQuantity", 0),
            inbound_shipped_quantity=data.get("inboundShippedQuantity", 0),
            inbound_receiving_quantity=data.get("inboundReceivingQuantity", 0)
        )

    @property
    def is_available(self) -> bool:
        """Check if item has fulfillable inventory"""
        return self.fulfillable_quantity > 0

    @property
    def total_inbound(self) -> int:
        """Calculate total inbound quantity"""
        return (
            self.inbound_working_quantity +
            self.inbound_shipped_quantity +
            self.inbound_receiving_quantity
        )
