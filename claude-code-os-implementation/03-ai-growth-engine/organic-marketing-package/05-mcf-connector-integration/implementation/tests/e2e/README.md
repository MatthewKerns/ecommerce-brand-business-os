# End-to-End Testing Guide

This guide helps you verify the MCF Connector with real TikTok Shop and Amazon MCF sandbox environments.

## Prerequisites

### 1. TikTok Shop Sandbox Account

1. Sign up for TikTok Shop Partner account at https://partner.tiktokshop.com
2. Create a test app in the TikTok Shop Partner Portal
3. Obtain your credentials:
   - App Key
   - App Secret
   - Shop ID
   - Access Token (OAuth 2.0)
   - Refresh Token

### 2. Amazon Seller Central & MCF Sandbox

1. Register for Amazon Seller Central
2. Sign up for Amazon MWS/SP-API Developer account
3. Create a developer application
4. Obtain your credentials:
   - Client ID (LWA Client ID)
   - Client Secret (LWA Client Secret)
   - Refresh Token
   - Seller ID
   - Marketplace ID (e.g., ATVPDKIKX0DER for US)
   - AWS Access Key
   - AWS Secret Key

### 3. Environment Configuration

Create a `.env` file in the implementation directory:

```bash
cp .env.example .env
```

Fill in your sandbox credentials:

```env
# TikTok Shop API Configuration
TIKTOK_APP_KEY=your-sandbox-app-key
TIKTOK_APP_SECRET=your-sandbox-app-secret
TIKTOK_SHOP_ID=your-sandbox-shop-id
TIKTOK_API_BASE_URL=https://open-api.tiktokglobalshop.com
TIKTOK_ACCESS_TOKEN=your-sandbox-access-token
TIKTOK_REFRESH_TOKEN=your-sandbox-refresh-token

# Amazon MCF (Multi-Channel Fulfillment) Configuration
AMAZON_CLIENT_ID=your-sandbox-client-id
AMAZON_CLIENT_SECRET=your-sandbox-client-secret
AMAZON_REFRESH_TOKEN=your-sandbox-refresh-token
AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER
AMAZON_SELLER_ID=your-seller-id
AMAZON_AWS_ACCESS_KEY=your-aws-access-key
AMAZON_AWS_SECRET_KEY=your-aws-secret-key
AMAZON_REGION=us-east-1
AMAZON_API_BASE_URL=https://sellingpartnerapi-na.amazon.com

# Test Configuration
RUN_E2E_TESTS=true
NODE_ENV=test
```

## Running E2E Tests

### Automated Test Suite

Run the automated E2E test suite:

```bash
npm run test:e2e
```

This will:
1. Connect to TikTok Shop and Amazon MCF APIs
2. Fetch pending TikTok orders
3. Validate and transform orders
4. Create MCF fulfillment orders
5. Sync tracking information
6. Verify inventory checks

### Manual Test Flow

Follow these steps to manually verify the full order flow:

#### Step 1: Create Test Order in TikTok Shop Sandbox

1. Log in to TikTok Shop Seller Center (sandbox environment)
2. Create a test product with SKU `TEST-SKU-001`
3. Create a test order with the following details:
   - Product: TEST-SKU-001
   - Quantity: 2
   - Shipping address: Valid US address
   - Status: AWAITING_SHIPMENT

**Expected Result:** Order appears in TikTok Shop with AWAITING_SHIPMENT status

#### Step 2: Verify Connector Detects Order

Run the connector to fetch pending orders:

```bash
npm run start -- --mode=fetch-orders
```

Or use the Node.js REPL:

```javascript
const { MCFConnector } = require('./dist/index');
const { loadConfig } = require('./dist/config');

const config = loadConfig();
const connector = new MCFConnector(config);

// Test connections
await connector.testConnections();

// Fetch pending orders
const result = await connector.routePendingOrders();
console.log('Orders detected:', result.totalOrders);
console.log('Successfully routed:', result.successCount);
```

**Expected Result:**
- Order detected within 5 minutes
- `totalOrders >= 1`
- Order ID matches the test order created in Step 1

#### Step 3: Verify Order Validation Passes

Check the routing result for validation:

```javascript
result.results.forEach(r => {
  console.log('Order ID:', r.orderId);
  console.log('Validation:', r.success ? 'PASSED' : 'FAILED');
  if (r.error && r.error.stage === 'validate') {
    console.log('Validation Error:', r.error.message);
  }
  if (r.warnings) {
    console.log('Warnings:', r.warnings);
  }
});
```

**Expected Result:**
- Validation passes (`r.success === true` or error stage is not 'validate')
- Address normalized correctly (US state abbreviation, phone format)
- No validation errors for required fields

#### Step 4: Verify MCF Fulfillment Order Created

Check Amazon Seller Central for the created fulfillment order:

```javascript
result.results.forEach(r => {
  if (r.success) {
    console.log('TikTok Order ID:', r.orderId);
    console.log('MCF Order ID:', r.mcfOrderId);
    console.log('MCF Order created successfully');
  }
});
```

Then verify in Amazon Seller Central:
1. Go to Orders > Manage Multi-Channel Fulfillment Orders
2. Search for the MCF Order ID
3. Verify order details match the TikTok order

**Expected Result:**
- MCF order created with correct product mapping
- Shipping address matches normalized TikTok address
- Order items and quantities correct

#### Step 5: Verify Tracking Sync Updates TikTok Shop

Wait for MCF to ship the order (in sandbox, this may be simulated), then sync tracking:

```javascript
// Sync tracking for all orders
const syncResult = await connector.syncAllTracking();

console.log('Synced:', syncResult.syncedCount);
console.log('No tracking:', syncResult.noTrackingCount);

syncResult.results.forEach(r => {
  if (r.synced) {
    console.log('Order:', r.orderId);
    console.log('Tracking Number:', r.trackingNumber);
    console.log('Carrier:', r.carrier);
  }
});
```

Then verify in TikTok Shop:
1. Go to Orders > Order List
2. Find the test order
3. Check shipping information

**Expected Result:**
- Tracking number synced to TikTok Shop within 4 hours of shipment
- Carrier information correct
- Order status updated in TikTok Shop

#### Step 6: Verify Inventory Sync Prevents Overselling

Test with a SKU that has 0 inventory:

```javascript
// Check inventory for test SKU
const inventoryResult = await connector.checkInventory(['TEST-SKU-ZERO-STOCK']);

if (!inventoryResult.success) {
  console.log('Inventory check failed:', inventoryResult.error);
} else {
  inventoryResult.summaries.forEach(s => {
    console.log('SKU:', s.sellerSku);
    console.log('Available:', s.fulfillableQuantity);
  });
}

// Try to route an order with 0 stock SKU
const zeroStockResult = await connector.routeOrder('ORDER-WITH-ZERO-STOCK-SKU');

if (!zeroStockResult.success && zeroStockResult.error?.code === 'INSUFFICIENT_INVENTORY') {
  console.log('✓ Overselling prevented correctly');
  console.log('Error:', zeroStockResult.error.message);
}
```

**Expected Result:**
- Order routing blocked when inventory is insufficient
- Error code: `INSUFFICIENT_INVENTORY`
- Clear error message indicating which SKU lacks inventory

## Verification Checklist

Use this checklist to verify all acceptance criteria:

### Order Detection and Routing
- [ ] New TikTok Shop orders detected within 5 minutes
- [ ] Order data fetched correctly from TikTok API
- [ ] Multiple orders processed in batch correctly
- [ ] Pagination handled for large order lists

### Order Validation
- [ ] Required fields validated (recipient name, address, items)
- [ ] Order status validated (only AWAITING_SHIPMENT or AWAITING_COLLECTION)
- [ ] Item validation passes (SKU, quantity checks)
- [ ] Address normalization working (US states, phone numbers)
- [ ] Invalid orders rejected with clear error messages

### Order Transformation
- [ ] TikTok orders transformed to MCF format correctly
- [ ] Address fields mapped properly
- [ ] Item quantities and prices transformed
- [ ] SKU mappings applied when configured
- [ ] Shipping speed determined from delivery option

### MCF Order Creation
- [ ] MCF fulfillment orders created successfully
- [ ] Product mapping correct
- [ ] Shipping address normalized
- [ ] Order comments included
- [ ] API errors handled gracefully

### Tracking Synchronization
- [ ] Tracking numbers fetched from MCF
- [ ] Tracking numbers synced to TikTok Shop
- [ ] Sync completes within 4 hours of shipment
- [ ] Already-synced orders skipped
- [ ] Carrier information included

### Inventory Management
- [ ] Inventory checked before order creation
- [ ] Overselling prevented when stock is 0
- [ ] Low stock warnings generated
- [ ] Inventory cache working (reduces API calls)
- [ ] Batch inventory checks efficient

### Error Handling
- [ ] Failed orders flagged for manual review
- [ ] Clear error messages with error codes
- [ ] Retry logic working for transient errors
- [ ] Non-retryable errors identified correctly
- [ ] Batch processing continues on individual failures

### Performance
- [ ] Order routing completes in < 30 seconds per order
- [ ] Batch processing uses concurrency limits
- [ ] API rate limits respected
- [ ] Memory usage reasonable for large batches

### Security
- [ ] No secrets in code (all in environment variables)
- [ ] API credentials loaded from .env
- [ ] Sensitive data not logged
- [ ] HTTPS used for all API calls

## Troubleshooting

### TikTok Shop API Issues

**Problem:** `TikTokShopError: Unauthorized (401)`
- **Solution:** Check your access token is valid. Refresh the token if expired.

**Problem:** `TikTokShopError: Invalid signature`
- **Solution:** Verify your app secret is correct. Check system time is synchronized.

**Problem:** No orders returned
- **Solution:** Ensure you have test orders in AWAITING_SHIPMENT status in sandbox.

### Amazon MCF API Issues

**Problem:** `AmazonApiError: Unauthorized (401)`
- **Solution:** Refresh your LWA token. Verify client ID and secret are correct.

**Problem:** `AmazonApiError: Invalid AWS signature`
- **Solution:** Check AWS access key and secret key. Verify region is correct.

**Problem:** MCF order creation fails
- **Solution:** Ensure SKUs exist in Amazon inventory. Check address is valid US address.

### Inventory Sync Issues

**Problem:** `INVENTORY_CHECK_FAILED`
- **Solution:** Verify Amazon FBA Inventory API access. Check marketplace ID is correct.

**Problem:** Inventory always shows 0
- **Solution:** Ensure SKUs exist in Amazon FBA inventory. Check inventory summaries API.

### Tracking Sync Issues

**Problem:** No tracking numbers found
- **Solution:** Wait for MCF to ship (can take hours in sandbox). Check order status in Amazon.

**Problem:** Tracking sync fails
- **Solution:** Verify TikTok Shop API permissions for shipping info updates.

## Test Data

### Sample Valid Address

```json
{
  "recipient_name": "John Doe",
  "phone_number": "+1-555-0100",
  "address_line_1": "123 Main St",
  "address_line_2": "Apt 4B",
  "city": "San Francisco",
  "state": "California",
  "postal_code": "94102",
  "country_code": "US"
}
```

### Sample SKU Mapping

```javascript
connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');
connector.addSkuMapping('TIKTOK-SKU-002', 'AMAZON-SKU-002');
```

### Sample Test Order

- **Order ID:** TT-TEST-123456
- **SKU:** TEST-SKU-001
- **Quantity:** 2
- **Status:** AWAITING_SHIPMENT
- **Total:** $59.98 + $5.00 shipping

## Success Criteria

The E2E tests pass when:

1. ✅ All connection tests pass
2. ✅ At least one order detected and routed successfully
3. ✅ Order validation passes for valid orders
4. ✅ MCF fulfillment order created
5. ✅ Tracking information synced (when available)
6. ✅ Inventory checks prevent overselling
7. ✅ Error handling works correctly

## Notes

- Sandbox environments may have limitations (delayed tracking, simulated shipments)
- Some tests require manual setup (creating test orders, configuring inventory)
- E2E tests can take several minutes to complete
- Review console output for detailed test results
- Keep test order IDs for cleanup and verification

## Next Steps

After E2E verification passes:

1. Review all test results and logs
2. Document any issues or edge cases found
3. Update SKU mappings for production SKUs
4. Configure production credentials (separate from sandbox)
5. Set up monitoring and alerting
6. Deploy to staging environment for final verification
7. Deploy to production with gradual rollout
