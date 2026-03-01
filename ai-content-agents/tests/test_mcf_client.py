"""
Unit tests for Amazon SP-API MCF Client

Tests cover:
- MCFClient initialization and configuration
- MCF order creation and management
- Order retrieval and cancellation
- Package tracking and shipment details
- Inventory queries and SKU availability checks
- Pagination and error handling
- Credential refresh functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any


# Mock fixtures for config and auth
@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    """Mock Amazon SP-API configuration for all tests"""
    monkeypatch.setenv("AMAZON_SELLER_ID", "TEST_SELLER_123")
    monkeypatch.setenv("AMAZON_SP_API_CLIENT_ID", "amzn1.application-oa2-client.test123")
    monkeypatch.setenv("AMAZON_SP_API_CLIENT_SECRET", "test_client_secret_456")
    monkeypatch.setenv("AMAZON_SP_API_REFRESH_TOKEN", "Atzr|test_refresh_token_789")
    monkeypatch.setenv("AMAZON_SP_API_REGION", "us-east-1")
    monkeypatch.setenv("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")


@pytest.fixture
def mock_auth():
    """Mock SPAPIAuth instance"""
    auth = Mock()
    auth.client_id = "test_client_id"
    auth.client_secret = "test_client_secret"
    auth.refresh_token = "test_refresh_token"
    auth.get_credentials.return_value = {
        "access_token": "test_access_token",
        "seller_id": "TEST_SELLER_123",
        "region": "us-east-1",
        "marketplace_id": "ATVPDKIKX0DER"
    }
    auth.get_access_token.return_value = "test_access_token"
    return auth


@pytest.fixture
def sample_address():
    """Sample address for testing"""
    from integrations.amazon_sp_api.models import Address
    return Address(
        name="John Doe",
        address_line1="123 Main St",
        city="Seattle",
        state_or_province_code="WA",
        postal_code="98101",
        country_code="US",
        phone="206-555-0100"
    )


@pytest.fixture
def sample_order_item():
    """Sample order item for testing"""
    from integrations.amazon_sp_api.models import MCFOrderItem
    return MCFOrderItem(
        seller_sku="DECK-BOX-001",
        seller_fulfillment_order_item_id="item-1",
        quantity=2
    )


@pytest.fixture
def sample_fulfillment_order(sample_address, sample_order_item):
    """Sample fulfillment order for testing"""
    from integrations.amazon_sp_api.models import (
        MCFFulfillmentOrder,
        ShippingSpeedCategory
    )
    return MCFFulfillmentOrder(
        seller_fulfillment_order_id="ORDER-12345",
        marketplace_id="ATVPDKIKX0DER",
        displayable_order_id="ORDER-12345",
        displayable_order_date="2024-01-15T10:00:00Z",
        displayable_order_comment="Thank you for your order!",
        shipping_speed_category=ShippingSpeedCategory.STANDARD,
        destination_address=sample_address,
        items=[sample_order_item]
    )


@pytest.fixture
def mock_fulfillment_api_success():
    """Mock successful FulfillmentOutbound API response"""
    response = Mock()
    response.errors = None
    response.payload = {"success": True}
    return response


@pytest.fixture
def mock_inventory_api_success():
    """Mock successful FbaInventory API response"""
    response = Mock()
    response.errors = None
    response.payload = {
        "inventorySummaries": [
            {
                "sellerSku": "DECK-BOX-001",
                "fnSku": "X001ABC123",
                "asin": "B08XYZ1234",
                "condition": "NewItem",
                "totalQuantity": 100,
                "fulfillableQuantity": 95,
                "inboundWorkingQuantity": 0,
                "inboundShippedQuantity": 0,
                "inboundReceivingQuantity": 5
            }
        ],
        "pagination": {}
    }
    return response


class TestMCFClientInitialization:
    """Tests for MCFClient initialization and setup"""

    @patch('integrations.amazon_sp_api.mcf_client.get_sp_api_credentials')
    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_init_with_default_auth(self, mock_fba, mock_fulfillment, mock_get_creds, mock_config):
        """Test initialization with default authentication"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_get_creds.return_value = {
            "access_token": "test_token",
            "seller_id": "TEST_SELLER",
            "region": "us-east-1",
            "marketplace_id": "ATVPDKIKX0DER"
        }

        client = MCFClient()

        assert client.marketplace_id == "ATVPDKIKX0DER"
        assert client.region == "us-east-1"
        assert client.access_token == "test_token"
        mock_get_creds.assert_called_once()

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_init_with_custom_auth(self, mock_fba, mock_fulfillment, mock_auth):
        """Test initialization with custom auth instance"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        client = MCFClient(auth=mock_auth)

        assert client.marketplace_id == "ATVPDKIKX0DER"
        assert client.region == "us-east-1"
        assert client.access_token == "test_access_token"
        mock_auth.get_credentials.assert_called_once()

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_init_with_custom_marketplace(self, mock_fba, mock_fulfillment, mock_auth):
        """Test initialization with custom marketplace ID"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        client = MCFClient(auth=mock_auth, marketplace_id="A1F83G8C2ARO7P")

        assert client.marketplace_id == "A1F83G8C2ARO7P"

    @patch('integrations.amazon_sp_api.mcf_client.get_sp_api_credentials')
    def test_init_failure_raises_error(self, mock_get_creds, mock_config):
        """Test initialization failure raises MCFClientError"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_get_creds.side_effect = Exception("Auth failed")

        with pytest.raises(MCFClientError) as exc_info:
            MCFClient()

        assert "Failed to initialize MCF client" in str(exc_info.value)

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_init_creates_api_clients(self, mock_fba, mock_fulfillment, mock_auth):
        """Test that initialization creates both API clients"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        client = MCFClient(auth=mock_auth)

        mock_fulfillment.assert_called_once()
        mock_fba.assert_called_once()
        assert hasattr(client, 'fulfillment_client')
        assert hasattr(client, 'inventory_client')


class TestCreateFulfillmentOrder:
    """Tests for creating MCF fulfillment orders"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_create_order_success(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        sample_fulfillment_order,
        mock_fulfillment_api_success
    ):
        """Test successful order creation"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.create_fulfillment_order.return_value = mock_fulfillment_api_success
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        result = client.create_fulfillment_order(sample_fulfillment_order)

        assert result["success"] is True
        assert result["seller_fulfillment_order_id"] == "ORDER-12345"
        mock_fulfillment_instance.create_fulfillment_order.assert_called_once()

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_create_order_sets_marketplace_id(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        sample_fulfillment_order,
        mock_fulfillment_api_success
    ):
        """Test that marketplace ID is set if not provided"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.create_fulfillment_order.return_value = mock_fulfillment_api_success
        mock_fulfillment.return_value = mock_fulfillment_instance

        # Clear marketplace ID from order
        sample_fulfillment_order.marketplace_id = ""

        client = MCFClient(auth=mock_auth)
        result = client.create_fulfillment_order(sample_fulfillment_order)

        # Verify marketplace ID was added in API call
        call_args = mock_fulfillment_instance.create_fulfillment_order.call_args
        assert call_args[1]["body"]["marketplaceId"] == "ATVPDKIKX0DER"

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_create_order_api_error(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        sample_fulfillment_order
    ):
        """Test order creation handles API errors"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_response = Mock()
        mock_response.errors = [{"message": "Invalid SKU"}]

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.create_fulfillment_order.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.create_fulfillment_order(sample_fulfillment_order)

        assert "Order creation failed" in str(exc_info.value)
        assert "Invalid SKU" in str(exc_info.value)

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_create_order_selling_api_exception(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        sample_fulfillment_order
    ):
        """Test order creation handles SellingApiException"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError
        from sp_api.base import SellingApiException

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.create_fulfillment_order.side_effect = SellingApiException("API Error")
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.create_fulfillment_order(sample_fulfillment_order)

        assert "SP-API error creating order" in str(exc_info.value)


class TestGetFulfillmentOrder:
    """Tests for retrieving MCF fulfillment orders"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_order_success(self, mock_fba, mock_fulfillment, mock_auth, sample_address):
        """Test successful order retrieval"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "sellerFulfillmentOrderId": "ORDER-12345",
            "marketplaceId": "ATVPDKIKX0DER",
            "displayableOrderId": "ORDER-12345",
            "displayableOrderDateTime": "2024-01-15T10:00:00Z",
            "displayableOrderComment": "Thank you!",
            "shippingSpeedCategory": "Standard",
            "fulfillmentOrderStatus": "Processing",
            "destinationAddress": sample_address.to_sp_api_dict(),
            "items": [
                {
                    "sellerSku": "DECK-BOX-001",
                    "sellerFulfillmentOrderItemId": "item-1",
                    "quantity": 2
                }
            ]
        }

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.get_fulfillment_order.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        order = client.get_fulfillment_order("ORDER-12345")

        assert order.seller_fulfillment_order_id == "ORDER-12345"
        assert order.displayable_order_id == "ORDER-12345"
        assert len(order.items) == 1
        mock_fulfillment_instance.get_fulfillment_order.assert_called_once_with(
            sellerFulfillmentOrderId="ORDER-12345"
        )

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_order_api_error(self, mock_fba, mock_fulfillment, mock_auth):
        """Test get order handles API errors"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_response = Mock()
        mock_response.errors = [{"message": "Order not found"}]

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.get_fulfillment_order.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.get_fulfillment_order("INVALID-ORDER")

        assert "Order retrieval failed" in str(exc_info.value)
        assert "Order not found" in str(exc_info.value)


class TestCancelFulfillmentOrder:
    """Tests for cancelling MCF fulfillment orders"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_cancel_order_success(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        mock_fulfillment_api_success
    ):
        """Test successful order cancellation"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.cancel_fulfillment_order.return_value = mock_fulfillment_api_success
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        result = client.cancel_fulfillment_order("ORDER-12345")

        assert result["success"] is True
        assert result["seller_fulfillment_order_id"] == "ORDER-12345"
        mock_fulfillment_instance.cancel_fulfillment_order.assert_called_once_with(
            sellerFulfillmentOrderId="ORDER-12345"
        )

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_cancel_order_api_error(self, mock_fba, mock_fulfillment, mock_auth):
        """Test cancel order handles API errors"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_response = Mock()
        mock_response.errors = [{"message": "Order cannot be cancelled"}]

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.cancel_fulfillment_order.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.cancel_fulfillment_order("ORDER-12345")

        assert "Order cancellation failed" in str(exc_info.value)


class TestGetPackageTracking:
    """Tests for package tracking retrieval"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_tracking_success(self, mock_fba, mock_fulfillment, mock_auth):
        """Test successful package tracking retrieval"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "packageNumber": 123456,
            "carrierCode": "UPS",
            "trackingNumber": "1Z999AA10123456784",
            "currentStatus": "IN_TRANSIT",
            "estimatedArrivalDateTime": "2024-01-20T15:00:00Z",
            "packageItems": []
        }

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.get_package_tracking_details.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        package = client.get_package_tracking_details(123456)

        assert package.package_number == 123456
        assert package.carrier_code == "UPS"
        assert package.tracking_number == "1Z999AA10123456784"
        mock_fulfillment_instance.get_package_tracking_details.assert_called_once_with(
            packageNumber=123456
        )

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_tracking_api_error(self, mock_fba, mock_fulfillment, mock_auth):
        """Test package tracking handles API errors"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_response = Mock()
        mock_response.errors = [{"message": "Package not found"}]

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.get_package_tracking_details.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.get_package_tracking_details(999999)

        assert "Package tracking retrieval failed" in str(exc_info.value)


class TestListAllFulfillmentOrders:
    """Tests for listing fulfillment orders with pagination"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_list_orders_success(self, mock_fba, mock_fulfillment, mock_auth, sample_address):
        """Test successful order listing"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "fulfillmentOrders": [
                {
                    "sellerFulfillmentOrderId": "ORDER-1",
                    "marketplaceId": "ATVPDKIKX0DER",
                    "displayableOrderId": "ORDER-1",
                    "displayableOrderDateTime": "2024-01-15T10:00:00Z",
                    "displayableOrderComment": "Test",
                    "shippingSpeedCategory": "Standard",
                    "destinationAddress": sample_address.to_sp_api_dict(),
                    "items": []
                }
            ],
            "nextToken": None
        }

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.list_all_fulfillment_orders.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        result = client.list_all_fulfillment_orders()

        assert len(result["orders"]) == 1
        assert result["next_token"] is None
        assert result["has_more"] is False

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_list_orders_with_pagination(self, mock_fba, mock_fulfillment, mock_auth, sample_address):
        """Test order listing with pagination token"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "fulfillmentOrders": [],
            "nextToken": "next_page_token_123"
        }

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.list_all_fulfillment_orders.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        result = client.list_all_fulfillment_orders(next_token="prev_token")

        assert result["next_token"] == "next_page_token_123"
        assert result["has_more"] is True

        call_args = mock_fulfillment_instance.list_all_fulfillment_orders.call_args
        assert call_args[1]["nextToken"] == "prev_token"

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_list_orders_with_date_filter(self, mock_fba, mock_fulfillment, mock_auth):
        """Test order listing with date filtering"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {"fulfillmentOrders": [], "nextToken": None}

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.list_all_fulfillment_orders.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        start_date = datetime(2024, 1, 1)
        result = client.list_all_fulfillment_orders(query_start_date=start_date)

        call_args = mock_fulfillment_instance.list_all_fulfillment_orders.call_args
        assert "queryStartDate" in call_args[1]
        assert "2024-01-01" in call_args[1]["queryStartDate"]

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_list_orders_skips_parse_errors(self, mock_fba, mock_fulfillment, mock_auth):
        """Test that order listing continues when individual orders fail to parse"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "fulfillmentOrders": [
                {"invalid": "data"},  # This will fail to parse
                {"more_invalid": "data"}
            ],
            "nextToken": None
        }

        mock_fulfillment_instance = Mock()
        mock_fulfillment_instance.list_all_fulfillment_orders.return_value = mock_response
        mock_fulfillment.return_value = mock_fulfillment_instance

        client = MCFClient(auth=mock_auth)
        result = client.list_all_fulfillment_orders()

        # Should return empty list but not crash
        assert result["orders"] == []


class TestGetInventorySummaries:
    """Tests for inventory queries"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_inventory_success(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        mock_inventory_api_success
    ):
        """Test successful inventory query"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_inventory_api_success
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.get_inventory_summaries()

        assert len(result["inventory_items"]) == 1
        assert result["inventory_items"][0].seller_sku == "DECK-BOX-001"
        assert result["inventory_items"][0].fulfillable_quantity == 95
        assert result["has_more"] is False

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_inventory_specific_skus(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        mock_inventory_api_success
    ):
        """Test inventory query with specific SKUs"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_inventory_api_success
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.get_inventory_summaries(seller_skus=["DECK-BOX-001", "DECK-BOX-002"])

        call_args = mock_inventory_instance.get_inventory_summaries.call_args
        assert call_args[1]["sellerSkus"] == ["DECK-BOX-001", "DECK-BOX-002"]

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_inventory_with_pagination(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth
    ):
        """Test inventory query with pagination"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "inventorySummaries": [],
            "pagination": {"nextToken": "next_page_token"}
        }

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_response
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.get_inventory_summaries(next_token="prev_token")

        assert result["next_token"] == "next_page_token"
        assert result["has_more"] is True

        call_args = mock_inventory_instance.get_inventory_summaries.call_args
        assert call_args[1]["nextToken"] == "prev_token"

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_get_inventory_api_error(self, mock_fba, mock_fulfillment, mock_auth):
        """Test inventory query handles API errors"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_response = Mock()
        mock_response.errors = [{"message": "Invalid marketplace"}]

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_response
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.get_inventory_summaries()

        assert "Inventory query failed" in str(exc_info.value)


class TestCheckSkuAvailability:
    """Tests for SKU availability checking"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_check_sku_available(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        mock_inventory_api_success
    ):
        """Test SKU availability check for available item"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_inventory_api_success
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.check_sku_availability("DECK-BOX-001", required_quantity=10)

        assert result["available"] is True
        assert result["seller_sku"] == "DECK-BOX-001"
        assert result["fulfillable_quantity"] == 95
        assert result["required_quantity"] == 10

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_check_sku_insufficient_quantity(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        mock_inventory_api_success
    ):
        """Test SKU availability check for insufficient quantity"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_inventory_api_success
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.check_sku_availability("DECK-BOX-001", required_quantity=100)

        assert result["available"] is False
        assert result["fulfillable_quantity"] == 95
        assert result["required_quantity"] == 100

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_check_sku_not_found(self, mock_fba, mock_fulfillment, mock_auth):
        """Test SKU availability check for non-existent SKU"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_response = Mock()
        mock_response.errors = None
        mock_response.payload = {
            "inventorySummaries": [],
            "pagination": {}
        }

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_response
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.check_sku_availability("INVALID-SKU")

        assert result["available"] is False
        assert result["fulfillable_quantity"] == 0
        assert "not found" in result["message"]

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_check_sku_includes_total_inbound(
        self,
        mock_fba,
        mock_fulfillment,
        mock_auth,
        mock_inventory_api_success
    ):
        """Test that SKU availability includes total inbound quantity"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_inventory_instance = Mock()
        mock_inventory_instance.get_inventory_summaries.return_value = mock_inventory_api_success
        mock_fba.return_value = mock_inventory_instance

        client = MCFClient(auth=mock_auth)
        result = client.check_sku_availability("DECK-BOX-001")

        assert "total_inbound" in result
        assert result["total_inbound"] == 5  # From mock data


class TestRefreshCredentials:
    """Tests for credential refresh functionality"""

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_refresh_credentials_success(self, mock_fba, mock_fulfillment, mock_auth):
        """Test successful credential refresh"""
        from integrations.amazon_sp_api.mcf_client import MCFClient

        mock_auth.get_access_token.return_value = "new_access_token"

        client = MCFClient(auth=mock_auth)
        old_token = client.access_token

        client.refresh_credentials()

        mock_auth.get_access_token.assert_called_with(force_refresh=True)
        assert client.access_token == "new_access_token"

    @patch('integrations.amazon_sp_api.mcf_client.FulfillmentOutbound')
    @patch('integrations.amazon_sp_api.mcf_client.FbaInventory')
    def test_refresh_credentials_error(self, mock_fba, mock_fulfillment, mock_auth):
        """Test credential refresh handles errors"""
        from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

        mock_auth.get_access_token.side_effect = Exception("Token refresh failed")

        client = MCFClient(auth=mock_auth)

        with pytest.raises(MCFClientError) as exc_info:
            client.refresh_credentials()

        assert "Failed to refresh credentials" in str(exc_info.value)


class TestErrorHandling:
    """Tests for error handling edge cases"""

    def test_mcf_client_error_is_exception(self):
        """Test that MCFClientError is a proper Exception"""
        from integrations.amazon_sp_api.mcf_client import MCFClientError

        assert issubclass(MCFClientError, Exception)

        error = MCFClientError("Test error")
        assert str(error) == "Test error"


def test_mcf_client_imports():
    """Test that all key components can be imported"""
    from integrations.amazon_sp_api.mcf_client import (
        MCFClient,
        MCFClientError
    )

    assert MCFClient is not None
    assert MCFClientError is not None
