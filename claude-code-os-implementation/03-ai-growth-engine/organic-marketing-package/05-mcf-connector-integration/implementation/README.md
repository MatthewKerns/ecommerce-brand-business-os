# MCF Connector - Order Routing Engine

Automated order routing connector that seamlessly fulfills TikTok Shop orders through Amazon Multi-Channel Fulfillment (MCF). This solves the critical logistics challenge of TikTok Shop's Fulfillment by TikTok (FBT) by leveraging Amazon's proven infrastructure.

## Problem Solved

TikTok Shop sellers face **six-figure losses** due to:
- **FBT Logistics Chaos**: Unreliable fulfillment causing late deliveries and account penalties
- **Manual MCF Process**: Time-consuming order entry and tracking updates
- **Inventory Desync**: Overselling across channels leading to cancellations

This connector **eliminates all three problems** by automating the entire TikTok → Amazon MCF workflow.

## Architecture Overview

```
┌─────────────────┐
│  TikTok Shop    │
├─────────────────┤
│ • New Orders    │ ← Polled every 5 minutes
│ • Order Status  │ ← Tracking updates synced
│ • Inventory     │ ← Stock levels synced
└────────┬────────┘
         │
    ┌────▼─────────┐
    │   Connector  │
    ├──────────────┤
    │ • Validator  │ → Address normalization
    │ • Transformer│ → Order format conversion
    │ • Router     │ → Orchestration logic
    │ • Sync       │ → Tracking + Inventory
    └────┬─────────┘
         │
   ┌─────▼──────────┐
   │  Amazon MCF    │
   ├────────────────┤
   │ • Create Order │ → Fulfillment requests
   │ • Track Status │ → Shipment tracking
   │ • Check Stock  │ → Inventory levels
   └────────────────┘
```

## Features

### 1. Automated Order Routing
- **5-Minute Detection**: New TikTok orders automatically detected
- **Smart Validation**: Address normalization, duplicate detection
- **SKU Mapping**: TikTok product IDs → Amazon SKUs
- **Error Handling**: Failed orders flagged with clear error messages

### 2. Tracking Synchronization
- **4-Hour Guarantee**: Tracking numbers synced to TikTok within 4 hours of shipment
- **Real-Time Updates**: Automatic polling of MCF fulfillment status
- **Multi-Carrier Support**: UPS, FedEx, USPS tracking formats

### 3. Inventory Management
- **Pre-Order Validation**: Check Amazon FBA stock before creating MCF orders
- **Overselling Prevention**: Real-time inventory sync across channels
- **Low Stock Alerts**: Notifications when inventory falls below threshold

### 4. Enterprise Reliability
- **Retry Logic**: Exponential backoff for API failures
- **Rate Limit Handling**: Automatic throttling and queuing
- **Audit Trail**: Complete order history and status tracking
- **Webhook Notifications**: Real-time alerts for critical events

## Installation

```bash
npm install @organic-marketing/mcf-connector
```

## Quick Start

### 1. Configure API Credentials

```typescript
import { MCFConnector } from '@organic-marketing/mcf-connector';

const connector = new MCFConnector({
  // TikTok Shop configuration
  tiktok: {
    appKey: process.env.TIKTOK_APP_KEY,
    appSecret: process.env.TIKTOK_APP_SECRET,
    shopId: process.env.TIKTOK_SHOP_ID,
    accessToken: process.env.TIKTOK_ACCESS_TOKEN,
    refreshToken: process.env.TIKTOK_REFRESH_TOKEN
  },

  // Amazon MCF configuration
  amazon: {
    clientId: process.env.AMAZON_CLIENT_ID,
    clientSecret: process.env.AMAZON_CLIENT_SECRET,
    refreshToken: process.env.AMAZON_REFRESH_TOKEN,
    marketplaceId: process.env.AMAZON_MARKETPLACE_ID,
    sellerId: process.env.AMAZON_SELLER_ID,
    awsAccessKey: process.env.AMAZON_AWS_ACCESS_KEY,
    awsSecretKey: process.env.AMAZON_AWS_SECRET_KEY,
    region: process.env.AMAZON_REGION
  },

  // Connector settings
  settings: {
    orderPollInterval: 5, // minutes
    trackingSyncInterval: 30, // minutes
    inventorySyncInterval: 60, // minutes
    maxRetryAttempts: 3,
    retryBackoffMs: 1000
  }
});
```

### 2. Start the Connector

```typescript
// Start automatic order routing
await connector.start();

// Monitor status
connector.on('order.detected', (order) => {
  console.log(`New TikTok order detected: ${order.id}`);
});

connector.on('order.routed', (order) => {
  console.log(`Order ${order.id} routed to MCF: ${order.mcfOrderId}`);
});

connector.on('tracking.synced', (tracking) => {
  console.log(`Tracking synced for order ${tracking.orderId}: ${tracking.trackingNumber}`);
});

connector.on('error', (error) => {
  console.error(`Connector error: ${error.message}`);
});
```

### 3. Manual Order Routing

```typescript
// Route a specific order
const result = await connector.routeOrder('tiktok-order-id-123');

if (result.success) {
  console.log(`Order routed successfully: ${result.mcfOrderId}`);
} else {
  console.error(`Routing failed: ${result.error}`);
}
```

## Order Flow

### Step 1: Order Detection
```typescript
// Connector polls TikTok Shop API every 5 minutes
const newOrders = await connector.tiktok.getOrders({
  status: 'AWAITING_SHIPMENT',
  updatedAfter: lastPollTime
});
```

### Step 2: Order Validation
```typescript
// Validate and normalize order data
const validationResult = await connector.validator.validate(order);

if (!validationResult.valid) {
  // Flag for manual review
  await connector.flagOrder(order.id, validationResult.errors);
}
```

### Step 3: Order Transformation
```typescript
// Transform TikTok order to MCF format
const mcfOrder = await connector.transformer.transform(order, {
  skuMappings: {
    'tiktok-product-123': 'AMAZON-SKU-456'
  },
  shippingSpeed: 'Standard' // or 'Expedited', 'Priority'
});
```

### Step 4: Inventory Check
```typescript
// Verify Amazon FBA inventory before creating MCF order
const inventory = await connector.amazon.getInventory(mcfOrder.items);

if (!inventory.sufficient) {
  await connector.flagOrder(order.id, 'Insufficient inventory');
  return;
}
```

### Step 5: MCF Order Creation
```typescript
// Create fulfillment order in Amazon MCF
const mcfResponse = await connector.amazon.createFulfillmentOrder(mcfOrder);

if (mcfResponse.success) {
  await connector.updateOrderStatus(order.id, 'ROUTED_TO_MCF');
}
```

### Step 6: Tracking Sync
```typescript
// Poll MCF for tracking updates (every 30 minutes)
const tracking = await connector.amazon.getTracking(mcfOrder.id);

if (tracking.available) {
  // Sync tracking back to TikTok Shop
  await connector.tiktok.updateTracking(order.id, {
    trackingNumber: tracking.number,
    carrier: tracking.carrier,
    shippedAt: tracking.shippedAt
  });
}
```

## SKU Mapping Configuration

```typescript
// Define product mappings between TikTok and Amazon
const skuMappings = {
  // TikTok Product ID: Amazon SKU
  '7123456789012': 'POKEMON-BOOSTER-BOX',
  '7123456789013': 'MTG-COLLECTOR-BOX',
  '7123456789014': 'YUGIOH-DECK-TIN'
};

await connector.configureSKUMappings(skuMappings);

// Or load from external source
await connector.loadSKUMappings('https://your-api.com/mappings.json');
```

## Address Normalization

```typescript
// Automatic address validation and normalization
const address = {
  name: 'John Doe',
  line1: '123 main st',  // lowercase, no unit
  line2: '',
  city: 'new york',      // lowercase
  state: 'NY',
  postalCode: '10001',
  country: 'US',
  phone: '(555) 123-4567'
};

const normalized = await connector.validator.normalizeAddress(address);

// Result:
{
  name: 'John Doe',
  line1: '123 Main St',  // Capitalized
  line2: '',
  city: 'New York',      // Capitalized
  state: 'NY',
  postalCode: '10001',
  country: 'US',
  phone: '+15551234567'  // E.164 format
}
```

## Error Handling

```typescript
// Failed orders are automatically flagged with detailed errors
connector.on('order.failed', async (failure) => {
  console.log(`Order ${failure.orderId} failed: ${failure.reason}`);

  // Common failure reasons:
  // - 'INVALID_ADDRESS': Address validation failed
  // - 'INSUFFICIENT_INVENTORY': Out of stock on Amazon
  // - 'SKU_NOT_MAPPED': TikTok product has no Amazon SKU mapping
  // - 'MCF_API_ERROR': Amazon MCF API error
  // - 'TIKTOK_API_ERROR': TikTok Shop API error

  // Send notification to operations team
  await sendSlackAlert({
    channel: '#fulfillment-alerts',
    message: `Order ${failure.orderId} failed: ${failure.reason}`,
    orderDetails: failure.order
  });
});
```

## Testing

```bash
# Run unit tests
npm test

# Run integration tests (requires sandbox credentials)
npm run test:integration

# Test TikTok API connection
npm run test:tiktok

# Test Amazon MCF API connection
npm run test:amazon

# End-to-end test with test order
npm run test:e2e
```

## Environment Variables

See `.env.example` for complete configuration. Key variables:

```env
# Required: TikTok Shop credentials
TIKTOK_APP_KEY=
TIKTOK_APP_SECRET=
TIKTOK_SHOP_ID=
TIKTOK_ACCESS_TOKEN=

# Required: Amazon MCF credentials
AMAZON_CLIENT_ID=
AMAZON_CLIENT_SECRET=
AMAZON_REFRESH_TOKEN=
AMAZON_SELLER_ID=
AMAZON_AWS_ACCESS_KEY=
AMAZON_AWS_SECRET_KEY=

# Optional: Connector settings
ORDER_POLL_INTERVAL_MINUTES=5
TRACKING_SYNC_INTERVAL_MINUTES=30
INVENTORY_SYNC_INTERVAL_MINUTES=60
```

## Monitoring & Alerts

### Webhook Events

The connector emits these webhook events:

```typescript
{
  'order.detected': { orderId, tiktokOrderId, detectedAt },
  'order.validated': { orderId, validationResult },
  'order.routed': { orderId, mcfOrderId, routedAt },
  'order.failed': { orderId, reason, error },
  'tracking.synced': { orderId, trackingNumber, carrier, syncedAt },
  'inventory.low': { sku, currentStock, threshold },
  'connector.started': { startedAt },
  'connector.stopped': { stoppedAt }
}
```

### Metrics to Monitor

```typescript
// Built-in metrics
const metrics = await connector.getMetrics();

console.log({
  ordersDetected: metrics.ordersDetected,
  ordersRouted: metrics.ordersRouted,
  ordersFailed: metrics.ordersFailed,
  successRate: metrics.successRate,
  averageRoutingTime: metrics.averageRoutingTime,
  trackingsSynced: metrics.trackingsSynced
});
```

## Production Considerations

1. **Rate Limits**:
   - TikTok Shop: 600 requests/minute per app
   - Amazon SP-API: Varies by endpoint (typically 10-30 requests/second)
   - Connector handles rate limiting automatically

2. **Security**:
   - Never commit credentials to version control
   - Use environment variables or secrets manager
   - Rotate access tokens regularly
   - Verify webhook signatures (HMAC)

3. **Scaling**:
   - For high volume (>1000 orders/day), consider queue-based architecture
   - Use Redis for order state tracking
   - Deploy multiple connector instances with distributed locking

4. **Monitoring**:
   - Set up alerts for failed orders
   - Monitor API error rates
   - Track fulfillment SLA compliance
   - Dashboard for real-time order status

5. **Backup**:
   - Store order history in database
   - Regular backups of SKU mappings
   - Audit trail for all API calls

## API Reference

### MCFConnector

#### `constructor(config: ConnectorConfig)`
Creates a new connector instance.

#### `start(): Promise<void>`
Starts automatic order polling and routing.

#### `stop(): Promise<void>`
Stops the connector and cleans up resources.

#### `routeOrder(orderId: string): Promise<RoutingResult>`
Manually route a specific order.

#### `getOrderStatus(orderId: string): Promise<OrderStatus>`
Get current status of an order.

#### `configureSKUMappings(mappings: Record<string, string>): Promise<void>`
Update SKU mappings between TikTok and Amazon.

#### `getMetrics(): Promise<ConnectorMetrics>`
Get connector performance metrics.

### Events

- `order.detected` - New TikTok order detected
- `order.validated` - Order passed validation
- `order.routed` - Order successfully routed to MCF
- `order.failed` - Order routing failed
- `tracking.synced` - Tracking number synced to TikTok
- `inventory.low` - Low inventory alert
- `error` - Connector error

## Troubleshooting

### "Unable to authenticate with TikTok Shop"
- Verify `TIKTOK_APP_KEY` and `TIKTOK_APP_SECRET` are correct
- Check if access token is expired (refresh every 24 hours)
- Ensure shop ID matches the authorized shop

### "Amazon MCF order creation failed"
- Verify AWS credentials and SP-API permissions
- Check if seller ID and marketplace ID are correct
- Ensure MCF is enabled for your seller account

### "SKU not found" errors
- Verify SKU mappings are configured correctly
- Check if Amazon SKU exists in your inventory
- Ensure SKU is eligible for MCF fulfillment

### "Address validation failed"
- Review address format requirements
- Check for missing required fields (name, line1, city, state, postal code)
- Verify country code is supported by Amazon MCF

## Roadmap

- [ ] Database adapter for order history (PostgreSQL, MySQL)
- [ ] Admin dashboard for order management
- [ ] Advanced SKU mapping with variants
- [ ] Multi-warehouse support
- [ ] Shopify integration for inventory sync
- [ ] Predictive inventory management
- [ ] A/B testing for shipping speeds
- [ ] Cost optimization (MCF vs FBT)

## License

MIT

## Support

For issues or questions:
- Open an issue in the repository
- Email support: support@yourdomain.com
- Documentation: https://docs.yourdomain.com/mcf-connector

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.
