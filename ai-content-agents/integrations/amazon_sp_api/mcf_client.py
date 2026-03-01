"""
Amazon SP-API Multi-Channel Fulfillment (MCF) Client

Provides high-level interface for Amazon MCF operations including order creation,
shipment tracking, and inventory management. Uses the SP-API Python library for
low-level API communication.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from sp_api.api import FulfillmentOutbound, FbaInventory
from sp_api.base import Marketplaces, SellingApiException

from integrations.amazon_sp_api.auth import SPAPIAuth, get_sp_api_credentials
from integrations.amazon_sp_api.models import (
    MCFFulfillmentOrder,
    MCFShipment,
    MCFPackage,
    MCFInventoryItem,
    FulfillmentOrderStatus
)
from config.config import AMAZON_MARKETPLACE_ID


class MCFClientError(Exception):
    """Exception raised for MCF client errors"""
    pass


class MCFClient:
    """
    Amazon Multi-Channel Fulfillment API Client

    Provides methods for creating MCF orders, tracking shipments, and querying inventory.
    Handles authentication, request formatting, and response parsing automatically.
    """

    def __init__(
        self,
        auth: Optional[SPAPIAuth] = None,
        marketplace_id: Optional[str] = None
    ):
        """
        Initialize MCF client

        Args:
            auth: Optional SPAPIAuth instance (creates default if not provided)
            marketplace_id: Optional marketplace ID (defaults to config)

        Raises:
            MCFClientError: If authentication initialization fails
        """
        try:
            # Use provided auth or get credentials from default
            if auth:
                self.auth = auth
                credentials = auth.get_credentials()
            else:
                credentials = get_sp_api_credentials()
                self.auth = SPAPIAuth()

            self.marketplace_id = marketplace_id or credentials["marketplace_id"]
            self.region = credentials["region"]
            self.access_token = credentials["access_token"]

            # Initialize SP-API clients
            self._init_api_clients()

        except Exception as e:
            raise MCFClientError(f"Failed to initialize MCF client: {str(e)}")

    def _init_api_clients(self) -> None:
        """Initialize SP-API client instances"""
        # Map region to marketplace enum
        marketplace_map = {
            "us-east-1": Marketplaces.US,
            "eu-west-1": Marketplaces.UK,
            "us-west-2": Marketplaces.US
        }

        self.marketplace = marketplace_map.get(self.region, Marketplaces.US)

        # Initialize API clients with credentials
        credentials = {
            "refresh_token": self.auth.refresh_token,
            "lwa_app_id": self.auth.client_id,
            "lwa_client_secret": self.auth.client_secret
        }

        self.fulfillment_client = FulfillmentOutbound(
            credentials=credentials,
            marketplace=self.marketplace
        )

        self.inventory_client = FbaInventory(
            credentials=credentials,
            marketplace=self.marketplace
        )

    def create_fulfillment_order(
        self,
        order: MCFFulfillmentOrder
    ) -> Dict[str, Any]:
        """
        Create a new MCF fulfillment order

        Args:
            order: MCFFulfillmentOrder instance with order details

        Returns:
            Dictionary containing the API response with order confirmation

        Raises:
            MCFClientError: If order creation fails

        Example:
            >>> from integrations.amazon_sp_api.models import (
            ...     MCFFulfillmentOrder, MCFOrderItem, Address, ShippingSpeedCategory
            ... )
            >>> address = Address(
            ...     name="John Doe",
            ...     address_line1="123 Main St",
            ...     city="Seattle",
            ...     state_or_province_code="WA",
            ...     postal_code="98101",
            ...     country_code="US"
            ... )
            >>> items = [
            ...     MCFOrderItem(
            ...         seller_sku="DECK-BOX-001",
            ...         seller_fulfillment_order_item_id="item-1",
            ...         quantity=2
            ...     )
            ... ]
            >>> order = MCFFulfillmentOrder(
            ...     seller_fulfillment_order_id="ORDER-12345",
            ...     marketplace_id="ATVPDKIKX0DER",
            ...     displayable_order_id="ORDER-12345",
            ...     displayable_order_date="2024-01-15T10:00:00Z",
            ...     displayable_order_comment="Thank you for your order!",
            ...     shipping_speed_category=ShippingSpeedCategory.STANDARD,
            ...     destination_address=address,
            ...     items=items
            ... )
            >>> client = MCFClient()
            >>> response = client.create_fulfillment_order(order)
        """
        try:
            # Convert order to SP-API format
            order_data = order.to_sp_api_dict()

            # Ensure marketplace ID is set
            if not order_data.get("marketplaceId"):
                order_data["marketplaceId"] = self.marketplace_id

            # Make API request
            response = self.fulfillment_client.create_fulfillment_order(
                body=order_data
            )

            if response.errors:
                error_messages = [err.get("message", str(err)) for err in response.errors]
                raise MCFClientError(f"Order creation failed: {', '.join(error_messages)}")

            return {
                "success": True,
                "seller_fulfillment_order_id": order.seller_fulfillment_order_id,
                "response": response.payload if hasattr(response, 'payload') else {}
            }

        except SellingApiException as e:
            raise MCFClientError(f"SP-API error creating order: {str(e)}")
        except Exception as e:
            raise MCFClientError(f"Unexpected error creating order: {str(e)}")

    def get_fulfillment_order(
        self,
        seller_fulfillment_order_id: str
    ) -> MCFFulfillmentOrder:
        """
        Retrieve details of an existing MCF fulfillment order

        Args:
            seller_fulfillment_order_id: The merchant's order ID

        Returns:
            MCFFulfillmentOrder instance with current order details

        Raises:
            MCFClientError: If order retrieval fails
        """
        try:
            response = self.fulfillment_client.get_fulfillment_order(
                sellerFulfillmentOrderId=seller_fulfillment_order_id
            )

            if response.errors:
                error_messages = [err.get("message", str(err)) for err in response.errors]
                raise MCFClientError(f"Order retrieval failed: {', '.join(error_messages)}")

            order_data = response.payload
            return MCFFulfillmentOrder.from_sp_api_response(order_data)

        except SellingApiException as e:
            raise MCFClientError(f"SP-API error retrieving order: {str(e)}")
        except Exception as e:
            raise MCFClientError(f"Unexpected error retrieving order: {str(e)}")

    def cancel_fulfillment_order(
        self,
        seller_fulfillment_order_id: str
    ) -> Dict[str, Any]:
        """
        Cancel an MCF fulfillment order

        Args:
            seller_fulfillment_order_id: The merchant's order ID to cancel

        Returns:
            Dictionary containing cancellation confirmation

        Raises:
            MCFClientError: If order cancellation fails

        Note:
            Orders can only be cancelled before they enter the Pending or Processing state
        """
        try:
            response = self.fulfillment_client.cancel_fulfillment_order(
                sellerFulfillmentOrderId=seller_fulfillment_order_id
            )

            if response.errors:
                error_messages = [err.get("message", str(err)) for err in response.errors]
                raise MCFClientError(f"Order cancellation failed: {', '.join(error_messages)}")

            return {
                "success": True,
                "seller_fulfillment_order_id": seller_fulfillment_order_id,
                "response": response.payload if hasattr(response, 'payload') else {}
            }

        except SellingApiException as e:
            raise MCFClientError(f"SP-API error cancelling order: {str(e)}")
        except Exception as e:
            raise MCFClientError(f"Unexpected error cancelling order: {str(e)}")

    def get_package_tracking_details(
        self,
        package_number: int
    ) -> MCFPackage:
        """
        Get tracking details for a specific package

        Args:
            package_number: The Amazon package number

        Returns:
            MCFPackage instance with tracking information

        Raises:
            MCFClientError: If tracking retrieval fails
        """
        try:
            response = self.fulfillment_client.get_package_tracking_details(
                packageNumber=package_number
            )

            if response.errors:
                error_messages = [err.get("message", str(err)) for err in response.errors]
                raise MCFClientError(f"Package tracking retrieval failed: {', '.join(error_messages)}")

            package_data = response.payload
            return MCFPackage.from_sp_api_response(package_data)

        except SellingApiException as e:
            raise MCFClientError(f"SP-API error retrieving package tracking: {str(e)}")
        except Exception as e:
            raise MCFClientError(f"Unexpected error retrieving package tracking: {str(e)}")

    def list_all_fulfillment_orders(
        self,
        query_start_date: Optional[datetime] = None,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all MCF fulfillment orders with optional date filtering

        Args:
            query_start_date: Optional start date for filtering orders
            next_token: Optional pagination token from previous request

        Returns:
            Dictionary containing list of orders and pagination info

        Raises:
            MCFClientError: If order listing fails
        """
        try:
            params = {}

            if query_start_date:
                params["queryStartDate"] = query_start_date.isoformat()

            if next_token:
                params["nextToken"] = next_token

            response = self.fulfillment_client.list_all_fulfillment_orders(**params)

            if response.errors:
                error_messages = [err.get("message", str(err)) for err in response.errors]
                raise MCFClientError(f"Order listing failed: {', '.join(error_messages)}")

            payload = response.payload
            orders = []

            for order_data in payload.get("fulfillmentOrders", []):
                try:
                    orders.append(MCFFulfillmentOrder.from_sp_api_response(order_data))
                except Exception as parse_error:
                    # Log parse error but continue processing other orders
                    continue

            return {
                "orders": orders,
                "next_token": payload.get("nextToken"),
                "has_more": bool(payload.get("nextToken"))
            }

        except SellingApiException as e:
            raise MCFClientError(f"SP-API error listing orders: {str(e)}")
        except Exception as e:
            raise MCFClientError(f"Unexpected error listing orders: {str(e)}")

    def get_inventory_summaries(
        self,
        seller_skus: Optional[List[str]] = None,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get inventory availability for MCF-eligible SKUs

        Args:
            seller_skus: Optional list of specific SKUs to query (queries all if not provided)
            next_token: Optional pagination token from previous request

        Returns:
            Dictionary containing inventory items and pagination info

        Raises:
            MCFClientError: If inventory query fails

        Example:
            >>> client = MCFClient()
            >>> result = client.get_inventory_summaries(seller_skus=["DECK-BOX-001"])
            >>> for item in result["inventory_items"]:
            ...     print(f"{item.seller_sku}: {item.fulfillable_quantity} available")
        """
        try:
            params = {
                "granularityType": "Marketplace",
                "granularityId": self.marketplace_id,
                "marketplaceIds": [self.marketplace_id]
            }

            if seller_skus:
                params["sellerSkus"] = seller_skus

            if next_token:
                params["nextToken"] = next_token

            response = self.inventory_client.get_inventory_summaries(**params)

            if response.errors:
                error_messages = [err.get("message", str(err)) for err in response.errors]
                raise MCFClientError(f"Inventory query failed: {', '.join(error_messages)}")

            payload = response.payload
            inventory_items = []

            for item_data in payload.get("inventorySummaries", []):
                try:
                    inventory_items.append(MCFInventoryItem.from_sp_api_response(item_data))
                except Exception as parse_error:
                    # Log parse error but continue processing other items
                    continue

            return {
                "inventory_items": inventory_items,
                "next_token": payload.get("pagination", {}).get("nextToken"),
                "has_more": bool(payload.get("pagination", {}).get("nextToken"))
            }

        except SellingApiException as e:
            raise MCFClientError(f"SP-API error querying inventory: {str(e)}")
        except Exception as e:
            raise MCFClientError(f"Unexpected error querying inventory: {str(e)}")

    def check_sku_availability(
        self,
        seller_sku: str,
        required_quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Check if a specific SKU has sufficient inventory available

        Args:
            seller_sku: The merchant's SKU to check
            required_quantity: Minimum quantity needed (default: 1)

        Returns:
            Dictionary with availability status and quantity information

        Example:
            >>> client = MCFClient()
            >>> result = client.check_sku_availability("DECK-BOX-001", required_quantity=5)
            >>> if result["available"]:
            ...     print(f"In stock: {result['fulfillable_quantity']} units")
        """
        try:
            result = self.get_inventory_summaries(seller_skus=[seller_sku])

            if not result["inventory_items"]:
                return {
                    "available": False,
                    "seller_sku": seller_sku,
                    "fulfillable_quantity": 0,
                    "message": "SKU not found in inventory"
                }

            item = result["inventory_items"][0]

            return {
                "available": item.fulfillable_quantity >= required_quantity,
                "seller_sku": seller_sku,
                "fulfillable_quantity": item.fulfillable_quantity,
                "required_quantity": required_quantity,
                "total_quantity": item.total_quantity,
                "total_inbound": item.total_inbound
            }

        except MCFClientError:
            raise
        except Exception as e:
            raise MCFClientError(f"Unexpected error checking SKU availability: {str(e)}")

    def refresh_credentials(self) -> None:
        """
        Force refresh of access token and reinitialize API clients

        Useful when credentials expire or need to be updated
        """
        try:
            # Force token refresh
            new_token = self.auth.get_access_token(force_refresh=True)
            self.access_token = new_token

            # Reinitialize API clients with new token
            self._init_api_clients()

        except Exception as e:
            raise MCFClientError(f"Failed to refresh credentials: {str(e)}")
