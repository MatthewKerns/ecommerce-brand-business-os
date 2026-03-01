# Amazon SP-API Multi-Channel Fulfillment (MCF) Integration

Amazon Multi-Channel Fulfillment (MCF) integration for the AI Content Agents system. Enables order creation, shipment tracking, and inventory management through Amazon's fulfillment infrastructure.

## Overview

This integration provides a Python interface to Amazon's Selling Partner API (SP-API) focused on Multi-Channel Fulfillment operations. It allows you to:

- **Create MCF Orders**: Route fulfillment orders to Amazon's FBA inventory
- **Track Shipments**: Retrieve tracking numbers and shipment status
- **Query Inventory**: Check available MCF-eligible inventory levels
- **Manage Orders**: List, retrieve, and cancel fulfillment orders

## Prerequisites

### 1. Amazon Seller Central Account

You need an Amazon Seller Central account with:
- Active FBA (Fulfillment by Amazon) inventory
- MCF-eligible SKUs available for fulfillment

### 2. SP-API Application Registration

Register your application in Seller Central to get API credentials:

1. Go to **Seller Central** → **Settings** → **User Permissions**
2. Navigate to **Developer Central** → **Your Developer Profile**
3. Click **Add new app client**
4. Configure your app:
   - **App name**: Your application name
   - **OAuth Redirect URI**: `https://localhost` (for testing)
   - **API Scopes**: Select **Fulfillment** scope
5. Save and note your credentials:
   - **LWA Client ID** (e.g., `amzn1.application-oa2-client.xxx`)
   - **LWA Client Secret**

### 3. Generate Refresh Token

Follow Amazon's [SP-API authorization workflow](https://developer-docs.amazon.com/sp-api/docs/authorizing-selling-partner-api-applications) to generate a refresh token:

1. Construct authorization URL:
   ```
   https://sellercentral.amazon.com/apps/authorize/consent?application_id=YOUR_CLIENT_ID&state=STATE&version=beta
   ```
2. Visit URL and authorize your application
3. Amazon redirects with authorization code
4. Exchange code for refresh token via LWA OAuth endpoint

**Note**: Refresh tokens do not expire but can be revoked. Store securely.

## Installation

### Dependencies

The integration requires the `python-amazon-sp-api` library:

```bash
pip install python-amazon-sp-api
```

All required dependencies are included in `ai-content-agents/requirements.txt`:

```bash
cd ai-content-agents
pip install -r requirements.txt
```

### Environment Configuration

Add Amazon SP-API credentials to your `.env` file:

```bash
# Amazon Seller Partner API Configuration
# See: https://developer-docs.amazon.com/sp-api/docs/what-is-the-selling-partner-api

# Your Amazon Seller/Merchant ID (found in Seller Central → Settings → Account Info)
AMAZON_SELLER_ID=A1BCDEFGH2IJKL

# SP-API Application Credentials (from Developer Central)
AMAZON_SP_API_CLIENT_ID=amzn1.application-oa2-client.xxxxxxxxxxxxx
AMAZON_SP_API_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AMAZON_SP_API_REFRESH_TOKEN=Atzr|IwEBIxxxxxxxxxxxxxxxxxxxxxx

# AWS Region for SP-API endpoints (us-east-1, eu-west-1, us-west-2)
AMAZON_SP_API_REGION=us-east-1

# Amazon Marketplace ID
# US: ATVPDKIKX0DER, CA: A2EUQ1WTGCTBG2, UK: A1F83G8C2ARO7P
# See: https://developer-docs.amazon.com/sp-api/docs/marketplace-ids
AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER
```

Reference `.env.example` for a complete template with all required variables.

### Verify Setup

Test your configuration:

```bash
cd ai-content-agents
python examples/test_mcf_integration.py
```

Expected output:
```
✓ Amazon SP-API credentials verified
✓ Authentication successful
✓ Inventory query successful
```

## Usage

### Basic Example

```python
from integrations.amazon_sp_api.mcf_client import MCFClient
from integrations.amazon_sp_api.models import (
    Address,
    MCFOrderItem,
    MCFFulfillmentOrder,
    ShippingSpeedCategory
)

# Initialize client (uses environment variables)
client = MCFClient()

# Create shipping address
address = Address(
    name="John Doe",
    address_line1="123 Main Street",
    city="Seattle",
    state_or_province_code="WA",
    postal_code="98101",
    country_code="US",
    phone="206-555-0123"
)

# Define order items
items = [
    MCFOrderItem(
        seller_sku="DECK-BOX-001",
        seller_fulfillment_order_item_id="item-1",
        quantity=2
    )
]

# Create fulfillment order
order = MCFFulfillmentOrder(
    seller_fulfillment_order_id="ORDER-12345",
    marketplace_id="ATVPDKIKX0DER",
    displayable_order_id="ORDER-12345",
    displayable_order_date="2024-01-15T10:00:00Z",
    displayable_order_comment="Thank you for your order!",
    shipping_speed_category=ShippingSpeedCategory.STANDARD,
    destination_address=address,
    items=items
)

# Submit order to Amazon MCF
response = client.create_fulfillment_order(order)
print(f"Order created: {response}")
```

### Query Inventory

Check available inventory for MCF fulfillment:

```python
from integrations.amazon_sp_api.mcf_client import MCFClient

client = MCFClient()

# Get inventory for specific SKUs
inventory = client.get_inventory_summaries(skus=["DECK-BOX-001", "BINDER-001"])

for item in inventory:
    print(f"{item.seller_sku}: {item.total_quantity} available")

# Check if specific SKU has sufficient quantity
is_available = client.check_sku_availability("DECK-BOX-001", quantity=5)
print(f"Can fulfill 5 units: {is_available}")
```

### Track Shipments

Retrieve order and tracking information:

```python
from integrations.amazon_sp_api.mcf_client import MCFClient

client = MCFClient()

# Get order details
order = client.get_fulfillment_order("ORDER-12345")
print(f"Order status: {order['status']}")

# Get tracking information
tracking = client.get_package_tracking_details(package_number=123456789)
print(f"Tracking number: {tracking['tracking_number']}")
print(f"Carrier: {tracking['carrier_code']}")
```

### List All Orders

Retrieve fulfillment orders with filtering:

```python
from integrations.amazon_sp_api.mcf_client import MCFClient
from datetime import datetime, timedelta

client = MCFClient()

# Get orders from last 7 days
start_date = datetime.now() - timedelta(days=7)
orders = client.list_all_fulfillment_orders(query_start_date=start_date)

for order in orders:
    print(f"Order {order['seller_fulfillment_order_id']}: {order['status']}")
```

## API Reference

### MCFClient

Main client class for MCF operations.

#### `__init__(auth=None, marketplace_id=None)`

Initialize MCF client.

- **auth** (Optional[SPAPIAuth]): Custom authentication instance (uses env vars if not provided)
- **marketplace_id** (Optional[str]): Override marketplace ID from config

#### `create_fulfillment_order(order: MCFFulfillmentOrder) -> Dict`

Create a new MCF fulfillment order.

- **order**: MCFFulfillmentOrder instance with order details
- **Returns**: API response with order confirmation
- **Raises**: MCFClientError on failure

#### `get_fulfillment_order(order_id: str) -> Dict`

Retrieve fulfillment order details.

- **order_id**: Seller fulfillment order ID
- **Returns**: Order details including status and items
- **Raises**: MCFClientError if order not found

#### `cancel_fulfillment_order(order_id: str) -> Dict`

Cancel a pending fulfillment order.

- **order_id**: Seller fulfillment order ID
- **Returns**: API response confirming cancellation
- **Raises**: MCFClientError if cancellation fails

#### `get_package_tracking_details(package_number: int) -> Dict`

Get tracking information for a package.

- **package_number**: Package tracking number
- **Returns**: Tracking details including carrier and status
- **Raises**: MCFClientError if tracking not found

#### `list_all_fulfillment_orders(query_start_date=None, next_token=None) -> List[Dict]`

List fulfillment orders with optional date filtering.

- **query_start_date** (Optional[datetime]): Filter orders after this date
- **next_token** (Optional[str]): Pagination token
- **Returns**: List of fulfillment order summaries

#### `get_inventory_summaries(skus=None, next_token=None) -> List[MCFInventoryItem]`

Query MCF-eligible inventory levels.

- **skus** (Optional[List[str]]): Filter by specific SKUs
- **next_token** (Optional[str]): Pagination token
- **Returns**: List of inventory items with quantities

#### `check_sku_availability(sku: str, quantity: int) -> bool`

Check if SKU has sufficient inventory.

- **sku**: Seller SKU to check
- **quantity**: Required quantity
- **Returns**: True if available, False otherwise

### Data Models

#### Address

Shipping address for fulfillment orders.

**Fields:**
- `name` (str): Recipient name
- `address_line1` (str): Street address
- `city` (str): City
- `state_or_province_code` (str): State/province code
- `postal_code` (str): ZIP/postal code
- `country_code` (str): ISO country code (e.g., "US")
- `address_line2` (Optional[str]): Apartment/suite
- `phone` (Optional[str]): Contact phone

#### MCFOrderItem

Individual item in a fulfillment order.

**Fields:**
- `seller_sku` (str): Your SKU identifier
- `seller_fulfillment_order_item_id` (str): Unique item ID
- `quantity` (int): Quantity to fulfill
- `per_unit_declared_value` (Optional[Dict]): Item value for customs

#### MCFFulfillmentOrder

Complete fulfillment order specification.

**Fields:**
- `seller_fulfillment_order_id` (str): Your order identifier
- `marketplace_id` (str): Amazon marketplace ID
- `displayable_order_id` (str): Customer-facing order ID
- `displayable_order_date` (str): ISO 8601 order date
- `displayable_order_comment` (str): Packing slip message
- `shipping_speed_category` (ShippingSpeedCategory): Shipping speed
- `destination_address` (Address): Delivery address
- `items` (List[MCFOrderItem]): Order line items
- `notification_emails` (Optional[List[str]]): Notification recipients

#### ShippingSpeedCategory (Enum)

- `STANDARD`: 5-7 business days
- `EXPEDITED`: 3-4 business days
- `PRIORITY`: 1-2 business days

#### FulfillmentOrderStatus (Enum)

- `RECEIVED`: Order received
- `PLANNING`: Processing started
- `PROCESSING`: Picking/packing
- `COMPLETE`: Shipped
- `CANCELLED`: Cancelled by seller
- `UNFULFILLABLE`: Cannot be fulfilled

## Error Handling

All methods may raise `MCFClientError` exceptions:

```python
from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError

client = MCFClient()

try:
    order = client.get_fulfillment_order("ORDER-12345")
except MCFClientError as e:
    print(f"MCF operation failed: {e}")
    # Handle error (retry, log, notify, etc.)
```

Common error scenarios:
- **Authentication failure**: Invalid credentials or expired token
- **Order not found**: Invalid order ID
- **Insufficient inventory**: SKU out of stock
- **Invalid address**: Address validation failed
- **API rate limiting**: Too many requests

## Testing

### Unit Tests

Run comprehensive unit tests:

```bash
cd ai-content-agents
python -m pytest tests/test_amazon_sp_auth.py tests/test_mcf_client.py -v
```

Tests cover:
- Authentication and token management
- Order creation and retrieval
- Inventory queries
- Error handling
- Pagination

### Integration Tests

Run integration tests with real API (requires valid credentials):

```bash
cd ai-content-agents
python examples/test_mcf_integration.py
```

**Dry-run mode** (safe, no orders created):
```bash
python examples/test_mcf_integration.py --dry-run
```

Test specific SKU:
```bash
python examples/test_mcf_integration.py --sku DECK-BOX-001
```

## Security Best Practices

### Credential Storage

- **Never commit credentials** to version control
- Store credentials in environment variables or secure vaults
- Use `.env` files locally (excluded from git via `.gitignore`)
- Rotate refresh tokens periodically

### Token Management

- Access tokens are automatically cached and refreshed
- Tokens expire after 3600 seconds (1 hour)
- Thread-safe token refresh prevents race conditions
- Refresh tokens are long-lived but can be revoked

### API Rate Limits

Amazon SP-API enforces rate limits per endpoint:
- Implement exponential backoff for retries
- Monitor API usage in Seller Central
- Cache inventory data when possible

## Troubleshooting

### Authentication Errors

**Error**: `SPAPIAuthError: Missing required credentials`

**Solution**: Verify all environment variables are set:
```bash
echo $AMAZON_SP_API_CLIENT_ID
echo $AMAZON_SP_API_CLIENT_SECRET
echo $AMAZON_SP_API_REFRESH_TOKEN
```

### Invalid Grant Error

**Error**: `invalid_grant` or `invalid_client`

**Solution**: Refresh token may be invalid. Generate new token via authorization workflow.

### Order Creation Fails

**Error**: `MCFClientError: Order creation failed`

**Possible causes**:
- SKU not found or not MCF-eligible
- Invalid shipping address
- Insufficient inventory
- Marketplace ID mismatch

**Debug steps**:
1. Verify SKU exists: `client.get_inventory_summaries(skus=["YOUR-SKU"])`
2. Check address format matches SP-API requirements
3. Confirm marketplace ID matches your Seller Central region

### Region/Marketplace Mismatch

Ensure your region and marketplace ID match:

| Region | Marketplace ID | Endpoint |
|--------|---------------|----------|
| us-east-1 | ATVPDKIKX0DER | US |
| us-west-2 | ATVPDKIKX0DER | US |
| eu-west-1 | A1F83G8C2ARO7P | UK |

## Resources

### Official Documentation

- [Amazon SP-API Documentation](https://developer-docs.amazon.com/sp-api/)
- [MCF API Reference](https://developer-docs.amazon.com/sp-api/docs/fulfillment-outbound-api-v2020-07-01-reference)
- [Marketplace IDs](https://developer-docs.amazon.com/sp-api/docs/marketplace-ids)
- [SP-API Authorization](https://developer-docs.amazon.com/sp-api/docs/authorizing-selling-partner-api-applications)

### Python Library

- [python-amazon-sp-api on GitHub](https://github.com/saleweaver/python-amazon-sp-api)
- [Library Documentation](https://sp-api-docs.saleweaver.com/)

### Support

For MCF integration issues:
1. Check [SP-API GitHub Issues](https://github.com/amzn/selling-partner-api-docs/issues)
2. Review Seller Central → Help → Contact Us
3. Consult [SP-API Developer Forum](https://github.com/amzn/selling-partner-api-docs/discussions)

## License

This integration is part of the AI Content Agents system. Refer to the main repository license for terms.

## Related Documentation

- [AI Content Agents README](../../README.md)
- [TikTok Shop Integration](../tiktok_shop/README.md)
- [Configuration Guide](../../../CONFIGURATION.md)
