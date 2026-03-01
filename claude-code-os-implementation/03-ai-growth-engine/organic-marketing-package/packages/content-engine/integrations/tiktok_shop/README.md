# TikTok Shop API Integration

Complete Python integration for TikTok Shop APIs including OAuth 2.0 authentication, Shop API for product/order management, Content API for video/post management, and Data API for analytics.

## 🎯 What This Does

This integration provides a full-featured Python client for interacting with TikTok Shop:

- **OAuth 2.0 Authentication**: Complete authorization flow with token management
- **Shop API**: Product listing, order management, inventory updates
- **Content API**: Video uploads, post creation, content management
- **Data API**: Performance analytics, metrics tracking
- **Automatic Rate Limiting**: Built-in rate limiter prevents API quota issues
- **Smart Error Handling**: Automatic retry with exponential backoff for transient errors
- **Type-Safe**: Full type hints for better IDE support

## 🚀 Quick Start

### 1. Prerequisites

Before using this integration, you need:

1. **TikTok Shop Seller Account** - Apply at https://seller.tiktok.com
2. **TikTok Shop API Application** - Create an app in TikTok Shop Partner Portal
3. **API Credentials** - Get your `app_key` and `app_secret`
4. **API Scopes** - Request access to:
   - Shop API (product and order management)
   - Content API (video and post management)
   - Data API (analytics and metrics)

### 2. Set Your API Credentials

Add your TikTok Shop credentials to `.env`:

```bash
# TikTok Shop API Configuration
TIKTOK_SHOP_APP_KEY=your_app_key_here
TIKTOK_SHOP_APP_SECRET=your_app_secret_here
TIKTOK_SHOP_API_BASE_URL=https://open-api.tiktokglobalshop.com
```

Or set them as environment variables:

```bash
export TIKTOK_SHOP_APP_KEY='your_app_key_here'
export TIKTOK_SHOP_APP_SECRET='your_app_secret_here'
```

### 3. Complete OAuth Flow

**Step 1: Generate Authorization URL**

```python
from integrations.tiktok_shop.oauth import TikTokShopOAuth

# Initialize OAuth handler
oauth = TikTokShopOAuth(
    app_key='your_app_key',
    app_secret='your_app_secret'
)

# Generate authorization URL
auth_url = oauth.generate_authorization_url(
    redirect_uri='https://yourapp.com/callback',
    state='random_state_string'  # For CSRF protection
)

print(f"Visit this URL to authorize: {auth_url}")
# Redirect user to auth_url in your web app
```

**Step 2: Exchange Authorization Code for Token**

After user authorizes, TikTok Shop redirects to your `redirect_uri` with an authorization code:

```python
# Extract auth_code from callback URL parameters
auth_code = request.args.get('code')

# Exchange code for access token
tokens = oauth.exchange_code_for_token(auth_code)

access_token = tokens['access_token']
refresh_token = tokens['refresh_token']
expires_in = tokens['expires_in']  # Seconds until token expires

# Store these tokens securely (database, encrypted storage, etc.)
```

**Step 3: Refresh Expired Tokens**

```python
# When access token expires, refresh it
new_tokens = oauth.refresh_access_token(refresh_token)

access_token = new_tokens['access_token']
refresh_token = new_tokens['refresh_token']  # TikTok rotates refresh tokens

# Update stored tokens
```

### 4. Use the API Client

Once you have an access token, you can use the TikTok Shop API:

```python
from integrations.tiktok_shop.client import TikTokShopClient

# Initialize client with credentials and access token
client = TikTokShopClient(
    app_key='your_app_key',
    app_secret='your_app_secret',
    access_token='user_access_token'
)

# Get products
response = client.get_products(page_size=10, status='ACTIVE')
products = response['data']['products']

# Get orders
response = client.get_orders(
    page_size=20,
    order_status='AWAITING_SHIPMENT'
)
orders = response['data']['orders']

# Update inventory
client.update_inventory(
    product_id='1234567890',
    quantity=100
)
```

## 📖 API Reference

### Shop API - Products, Orders, Inventory

#### Get Products

```python
# Get all products with pagination
response = client.get_products(
    page_size=20,          # Max 100
    page_number=1,
    status='ACTIVE',       # 'ACTIVE', 'INACTIVE', 'DRAFT'
    search_query='binder'  # Optional search
)

products = response['data']['products']
total = response['data']['total']
has_more = response['data']['more']
```

#### Get Product Details

```python
product = client.get_product('1234567890')
print(product['data']['title'])
print(product['data']['price'])
print(product['data']['inventory'])
```

#### Get Orders

```python
# Get orders with filters
import time

response = client.get_orders(
    page_size=20,
    page_number=1,
    order_status='AWAITING_SHIPMENT',  # See order statuses below
    start_time=int(time.time()) - (7 * 24 * 60 * 60),  # Last 7 days
    end_time=int(time.time())
)

orders = response['data']['orders']
```

**Order Statuses:**
- `UNPAID` - Order placed but not paid
- `AWAITING_SHIPMENT` - Paid, waiting to ship
- `AWAITING_COLLECTION` - Shipped, waiting for pickup
- `IN_TRANSIT` - In delivery
- `DELIVERED` - Delivered to customer
- `COMPLETED` - Order completed
- `CANCELLED` - Order cancelled

#### Get Order Details

```python
order = client.get_order('ORDER123456')
print(order['data']['order_status'])
print(order['data']['payment']['total_amount'])
print(order['data']['items'])
```

#### Manage Inventory

```python
# Update product inventory
result = client.update_inventory(
    product_id='1234567890',
    quantity=50,
    sku_id='SKU123'  # Optional, for specific variant
)

# Get current inventory
inventory = client.get_inventory('1234567890')
available = inventory['data']['available_quantity']
reserved = inventory['data']['reserved_quantity']
```

### Content API - Videos and Posts

#### Get Videos

```python
response = client.get_videos(
    page_size=20,
    page_number=1,
    video_status='PUBLISHED',  # 'PUBLISHED', 'DRAFT', 'PROCESSING', 'FAILED'
    start_time=start_timestamp,
    end_time=end_timestamp
)

videos = response['data']['videos']
```

#### Get Video Details

```python
video = client.get_video('VIDEO123456')
print(video['data']['title'])
print(video['data']['url'])
print(video['data']['view_count'])
print(video['data']['like_count'])
```

#### Upload Video

```python
result = client.upload_video(
    video_url='https://example.com/video.mp4',
    title='Check out our Premium Card Binders!',
    description='Battle-ready storage for serious TCG players',
    product_ids=['1234567890', '0987654321'],
    tags=['tcg', 'pokemon', 'cardprotection']
)

video_id = result['data']['video_id']
status = result['data']['status']
```

#### Delete Video

```python
client.delete_video('VIDEO123456')
```

#### Manage Posts

```python
# Get posts
response = client.get_posts(
    page_size=20,
    post_status='PUBLISHED'  # 'PUBLISHED', 'DRAFT', 'SCHEDULED'
)

# Get post details
post = client.get_post('POST123456')

# Create post
result = client.create_post(
    content='New arrivals just dropped! 🔥',
    media_urls=['https://example.com/image.jpg'],
    product_ids=['1234567890'],
    tags=['newarrivals', 'tcg'],
    scheduled_time=future_timestamp  # Optional, for scheduling
)

# Delete post
client.delete_post('POST123456')
```

### Data API - Analytics and Performance

#### Get Analytics

```python
import time

# Get analytics for last 7 days
end_time = int(time.time())
start_time = end_time - (7 * 24 * 60 * 60)

response = client.get_analytics(
    start_time=start_time,
    end_time=end_time,
    metrics=['views', 'clicks', 'conversions', 'revenue'],
    dimension='daily',  # 'product', 'video', 'post', 'daily'
    page_size=20
)

analytics = response['data']['analytics']
```

#### Get Performance Metrics

```python
# Get product performance metrics
metrics = client.get_performance_metrics(
    resource_type='product',  # 'product', 'video', 'post'
    resource_id='1234567890',
    start_time=start_timestamp,
    end_time=end_timestamp,
    metrics=['views', 'clicks', 'conversion_rate', 'revenue']
)

conversion_rate = metrics['data']['metrics']['conversion_rate']
revenue = metrics['data']['metrics']['revenue']
views = metrics['data']['metrics']['views']
```

## 🔧 Advanced Features

### Rate Limiting

The client automatically handles rate limiting using a token bucket algorithm:

```python
# Default rate limit: 10 requests per second
# The client will automatically throttle requests to stay within limits

# Rate limiting is transparent - just make your requests normally
for product_id in product_ids:
    product = client.get_product(product_id)
    # Client automatically paces requests
```

### Error Handling

The integration uses a comprehensive exception hierarchy:

```python
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,         # Base exception
    TikTokShopAuthError,        # Authentication errors
    TikTokShopRateLimitError,   # Rate limit errors
    TikTokShopValidationError,  # Invalid parameters
    TikTokShopNotFoundError,    # Resource not found
    TikTokShopServerError,      # Server errors (5xx)
    TikTokShopNetworkError      # Network/timeout errors
)

try:
    products = client.get_products(page_size=10)
except TikTokShopAuthError as e:
    # Handle authentication failure
    print(f"Auth error: {e.message}")
    # Maybe refresh token?
except TikTokShopRateLimitError as e:
    # Handle rate limit
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
    # Retry request
except TikTokShopValidationError as e:
    # Handle validation error
    print(f"Invalid parameters: {e.message}")
except TikTokShopNotFoundError as e:
    # Handle not found
    print(f"Resource not found: {e.message}")
except TikTokShopServerError as e:
    # Handle server error
    print(f"TikTok Shop server error: {e.message}")
    # Maybe retry later?
except TikTokShopNetworkError as e:
    # Handle network error
    print(f"Network error: {e.message}")
    # Check connection?
except TikTokShopAPIError as e:
    # Catch-all for any TikTok Shop API error
    print(f"API error: {e.message}")
```

### Automatic Retry with Backoff

The client automatically retries transient errors:

- **Rate Limit Errors**: Retries up to 3 times with exponential backoff
- **Server Errors (5xx)**: Retries up to 2 times with exponential backoff
- **Network Errors**: Retries up to 2 times with exponential backoff

```python
# This automatically retries on transient errors
try:
    products = client.get_products()
except TikTokShopRateLimitError:
    # Only raised if max retries exceeded
    print("Rate limit error after all retries")
```

### Webhook Signature Validation

Validate incoming webhooks from TikTok Shop:

```python
from integrations.tiktok_shop.oauth import TikTokShopOAuth

oauth = TikTokShopOAuth(app_key, app_secret)

# In your webhook endpoint
@app.route('/tiktok-webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-TikTok-Shop-Signature')
    timestamp = request.headers.get('X-TikTok-Shop-Timestamp')
    body = request.get_data(as_text=True)

    # Validate signature
    if not oauth.validate_webhook_signature(signature, timestamp, body):
        return 'Invalid signature', 401

    # Process webhook
    data = request.json
    # Handle event...

    return 'OK', 200
```

### Request Signatures

All API requests are automatically signed for security:

```python
# Signatures are generated automatically by the client
# You don't need to handle this manually

# But if you need to generate a signature manually:
signature = oauth.generate_signature(
    path='/api/products/search',
    params={'page_size': 10, 'page_number': 1}
)
```

## 🔐 Security Best Practices

### 1. Store Credentials Securely

Never hardcode credentials in your code:

```python
# ❌ BAD - Don't do this
client = TikTokShopClient(
    app_key='abc123',
    app_secret='secret456'
)

# ✅ GOOD - Use environment variables
import os
from config.config import TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET

client = TikTokShopClient(
    app_key=TIKTOK_SHOP_APP_KEY,
    app_secret=TIKTOK_SHOP_APP_SECRET
)
```

### 2. Encrypt Stored Tokens

Store access and refresh tokens encrypted:

```python
# Use a proper encryption library
from cryptography.fernet import Fernet

# Encrypt token before storing
encrypted_token = encrypt(access_token, encryption_key)
db.save_token(user_id, encrypted_token)

# Decrypt when using
encrypted_token = db.get_token(user_id)
access_token = decrypt(encrypted_token, encryption_key)
```

### 3. Use HTTPS for Webhooks

Always use HTTPS for webhook endpoints to prevent man-in-the-middle attacks.

### 4. Validate All Webhook Requests

Always validate webhook signatures before processing:

```python
if not oauth.validate_webhook_signature(signature, timestamp, body):
    return 'Unauthorized', 401
```

### 5. Implement Token Refresh Logic

Refresh tokens before they expire:

```python
# Store token expiration time
token_expires_at = time.time() + tokens['expires_in']

# Check before making requests
if time.time() >= token_expires_at - 300:  # Refresh 5 minutes early
    tokens = oauth.refresh_access_token(refresh_token)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    token_expires_at = time.time() + tokens['expires_in']
    # Update stored tokens
```

## 📋 Complete Example

Here's a complete example that ties everything together:

```python
import os
import time
from integrations.tiktok_shop.oauth import TikTokShopOAuth
from integrations.tiktok_shop.client import TikTokShopClient
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError
)

# Configuration
APP_KEY = os.environ.get('TIKTOK_SHOP_APP_KEY')
APP_SECRET = os.environ.get('TIKTOK_SHOP_APP_SECRET')
REDIRECT_URI = 'https://yourapp.com/callback'

# Step 1: OAuth Flow (one-time setup per user)
def authorize_user():
    oauth = TikTokShopOAuth(APP_KEY, APP_SECRET)

    # Generate auth URL
    auth_url = oauth.generate_authorization_url(
        redirect_uri=REDIRECT_URI,
        state='secure_random_string'
    )

    print(f"Visit: {auth_url}")
    # In a web app, redirect user to auth_url

    # After user authorizes, extract code from callback
    auth_code = input("Enter authorization code: ")

    # Exchange for tokens
    tokens = oauth.exchange_code_for_token(auth_code)

    # Store these securely
    return tokens['access_token'], tokens['refresh_token']

# Step 2: Use the API
def sync_products(access_token):
    try:
        # Initialize client
        client = TikTokShopClient(APP_KEY, APP_SECRET, access_token)

        # Get all products
        all_products = []
        page = 1

        while True:
            response = client.get_products(
                page_size=100,
                page_number=page,
                status='ACTIVE'
            )

            products = response['data']['products']
            all_products.extend(products)

            if not response['data'].get('more', False):
                break

            page += 1

        print(f"Synced {len(all_products)} products")

        # Process each product
        for product in all_products:
            product_id = product['id']

            # Get detailed info
            details = client.get_product(product_id)

            # Get performance metrics
            end_time = int(time.time())
            start_time = end_time - (30 * 24 * 60 * 60)  # Last 30 days

            metrics = client.get_performance_metrics(
                resource_type='product',
                resource_id=product_id,
                start_time=start_time,
                end_time=end_time,
                metrics=['views', 'clicks', 'conversions', 'revenue']
            )

            print(f"Product: {details['data']['title']}")
            print(f"Views: {metrics['data']['metrics']['views']}")
            print(f"Revenue: ${metrics['data']['metrics']['revenue']}")

    except TikTokShopAuthError as e:
        print(f"Authentication failed: {e}")
        # Maybe refresh token here
    except TikTokShopRateLimitError as e:
        print(f"Rate limited. Waiting {e.retry_after}s...")
        time.sleep(e.retry_after)
        # Retry the operation
    except TikTokShopAPIError as e:
        print(f"API error: {e}")

# Step 3: Sync orders
def sync_orders(access_token):
    client = TikTokShopClient(APP_KEY, APP_SECRET, access_token)

    try:
        # Get orders awaiting shipment
        response = client.get_orders(
            page_size=100,
            order_status='AWAITING_SHIPMENT'
        )

        orders = response['data']['orders']

        for order in orders:
            order_id = order['id']

            # Get full order details
            details = client.get_order(order_id)

            print(f"Order {order_id}:")
            print(f"  Total: ${details['data']['payment']['total_amount']}")
            print(f"  Items: {len(details['data']['items'])}")

            # Process order for fulfillment...

    except TikTokShopAPIError as e:
        print(f"Error syncing orders: {e}")

# Main execution
if __name__ == '__main__':
    # One-time: Get access token
    access_token, refresh_token = authorize_user()

    # Regular operations
    sync_products(access_token)
    sync_orders(access_token)
```

## ⚠️ Important Notes

### API Limitations

- **Rate Limits**: Default 10 requests per second (configurable per app)
- **Pagination**: Maximum 100 items per page
- **Token Expiry**: Access tokens expire (check `expires_in` field)
- **Refresh Token Rotation**: TikTok rotates refresh tokens - always update both tokens

### Testing

- Use TikTok Shop's sandbox environment for testing
- Test OAuth flow thoroughly before production
- Validate error handling for all exception types
- Test rate limiting behavior under load

### Production Checklist

- [ ] Store credentials in environment variables or secure vault
- [ ] Encrypt access and refresh tokens in database
- [ ] Implement automatic token refresh before expiry
- [ ] Set up webhook endpoints with signature validation
- [ ] Monitor API usage and rate limits
- [ ] Implement proper error logging
- [ ] Set up retry logic for failed requests
- [ ] Use HTTPS for all communication

## 📚 Additional Resources

- [TikTok Shop API Documentation](https://partner.tiktokshop.com/docv2/page/650aa8f6e7d0f302be66f7b8)
- [TikTok Shop Seller Center](https://seller.tiktok.com)
- [TikTok Shop Partner Portal](https://partner.tiktokshop.com)
- [OAuth 2.0 Specification](https://oauth.net/2/)

## 🐛 Troubleshooting

### "Authentication error: Invalid access token"

- Token may be expired - try refreshing it
- Verify token is correctly stored and retrieved
- Check if user revoked app access

### "Rate limit exceeded"

- Client automatically retries with backoff
- If still occurring, reduce request frequency
- Consider batching operations

### "Resource not found"

- Verify the product/order/video ID is correct
- Resource may have been deleted
- Check if you have permission to access the resource

### "Validation error: Invalid parameters"

- Check parameter types and formats
- Review API documentation for parameter requirements
- Ensure required fields are provided

## 💡 Tips

1. **Batch Operations**: When possible, use pagination to fetch multiple items instead of individual requests
2. **Cache Data**: Cache product/inventory data to reduce API calls
3. **Webhooks**: Use webhooks for real-time updates instead of polling
4. **Monitor Usage**: Track your API usage to stay within rate limits
5. **Error Recovery**: Implement proper error handling and retry logic for production use
