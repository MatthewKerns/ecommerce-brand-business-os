# Klaviyo Email Marketing Integration

Complete Python integration for Klaviyo's email marketing platform with customer profile management, event tracking, list management, segmentation, and automated data sync from e-commerce platforms.

## 🎯 What This Does

This integration provides a full-featured Python client for Klaviyo email marketing:

- **Profile Management**: Create and update customer profiles with demographic and behavioral data
- **Event Tracking**: Track customer events (purchases, page views, cart abandonment, etc.)
- **List Management**: Manage email lists and subscriber segments
- **Segmentation**: Create and manage dynamic customer segments
- **Data Sync**: Automated synchronization from TikTok Shop and other platforms
- **Compliance**: Built-in unsubscribe and consent management
- **Automatic Rate Limiting**: Token bucket rate limiter prevents API quota issues
- **Smart Error Handling**: Automatic retry with exponential backoff for transient errors
- **Type-Safe**: Full type hints for better IDE support

## 🚀 Quick Start

### 1. Prerequisites

Before using this integration, you need:

1. **Klaviyo Account** - Sign up at https://www.klaviyo.com
2. **Private API Key** - Generate in Klaviyo Settings → Account → API Keys
3. **API Access** - Ensure your account has access to:
   - Profiles API (customer management)
   - Events API (event tracking)
   - Lists API (list management)
   - Segments API (segmentation)

### 2. Set Your API Key

Add your Klaviyo API key to `.env`:

```bash
# Klaviyo API Configuration
# Get your API key from: https://www.klaviyo.com/settings/account/api-keys
KLAVIYO_API_KEY=pk_abc123def456ghi789jkl012mno345pqr
KLAVIYO_API_BASE_URL=https://a.klaviyo.com/api
```

Or set it as an environment variable:

```bash
export KLAVIYO_API_KEY='pk_abc123def456ghi789jkl012mno345pqr'
```

### 3. Basic Usage

#### Create a Customer Profile

```python
from integrations.klaviyo.client import KlaviyoClient
from integrations.klaviyo.models import KlaviyoProfile, ProfileLocation

# Initialize client
client = KlaviyoClient(api_key='your_api_key_here')

# Create a profile with location
location = ProfileLocation(
    city="San Francisco",
    region="CA",
    country="United States",
    zip="94102",
    timezone="America/Los_Angeles"
)

profile = KlaviyoProfile(
    email="customer@example.com",
    first_name="Jane",
    last_name="Doe",
    phone_number="+14155551234",
    location=location,
    properties={
        "favorite_category": "TCG Cards",
        "total_orders": 5,
        "lifetime_value": 299.95
    }
)

# Create or update profile in Klaviyo
result = client.create_or_update_profile(profile)
print(f"Profile created: {result.profile_id}")
```

#### Track an Event

```python
from integrations.klaviyo.models import KlaviyoEvent

# Track a purchase event
event = KlaviyoEvent(
    metric_name="Placed Order",
    customer_email="customer@example.com",
    properties={
        "order_id": "ORD-12345",
        "total_amount": 89.99,
        "currency": "USD",
        "items": [
            {
                "product_id": "PROD-001",
                "name": "Premium Card Binder",
                "quantity": 2,
                "price": 44.99
            }
        ],
        "shipping_method": "Standard",
        "tracking_number": "1Z999AA10123456789"
    }
)

# Send event to Klaviyo
result = client.track_event(event)
print(f"Event tracked: {result.event_id}")
```

#### Manage Email Lists

```python
# Get all lists
lists = client.get_lists()
for email_list in lists:
    print(f"{email_list.name}: {email_list.profile_count} subscribers")

# Create a new list
vip_list = client.get_or_create_list("VIP Customers")

# Add a profile to the list
client.add_profile_to_list(
    list_id=vip_list.list_id,
    email="customer@example.com"
)

# Remove a profile from a list
client.remove_profile_from_list(
    list_id=vip_list.list_id,
    profile_id="PROFILE123"
)
```

## 📖 API Reference

### Profile Management

#### Create or Update Profile

```python
from integrations.klaviyo.models import KlaviyoProfile, ProfileLocation

# Create a profile with full details
profile = KlaviyoProfile(
    email="customer@example.com",           # Required
    phone_number="+14155551234",            # Optional
    external_id="CUSTOMER-001",             # Optional - your system's ID
    first_name="Jane",
    last_name="Doe",
    organization="ACME Corp",
    title="Product Manager",
    location=ProfileLocation(
        address1="123 Main St",
        city="San Francisco",
        region="CA",
        country="United States",
        zip="94102",
        timezone="America/Los_Angeles",
        latitude=37.7749,
        longitude=-122.4194
    ),
    properties={
        # Custom properties for segmentation
        "customer_tier": "gold",
        "loyalty_points": 1500,
        "preferred_contact": "email",
        "interests": ["TCG", "Pokemon", "Magic"]
    }
)

# Create or update (upsert operation)
result = client.create_or_update_profile(profile)
print(f"Profile ID: {result.profile_id}")
print(f"Email: {result.email}")
```

#### Get Profile

```python
# Get by Klaviyo profile ID
profile = client.get_profile("PROFILE123")

# Search by email
profiles = client.search_profiles(email="customer@example.com")
if profiles:
    profile = profiles[0]
    print(f"Found: {profile.first_name} {profile.last_name}")

# Search by phone
profiles = client.search_profiles(phone_number="+14155551234")

# Search by external ID
profiles = client.search_profiles(external_id="CUSTOMER-001")
```

### Event Tracking

#### Track Customer Events

```python
from integrations.klaviyo.models import KlaviyoEvent
from datetime import datetime

# Track a purchase event
purchase_event = KlaviyoEvent(
    metric_name="Placed Order",
    customer_email="customer@example.com",
    properties={
        "order_id": "ORD-12345",
        "total_amount": 149.98,
        "currency": "USD",
        "discount_code": "SAVE20",
        "discount_amount": 30.00,
        "items": [
            {
                "product_id": "PROD-001",
                "name": "Premium Card Binder",
                "sku": "BINDER-RED-L",
                "quantity": 2,
                "price": 44.99
            },
            {
                "product_id": "PROD-002",
                "name": "Card Sleeves Pack",
                "sku": "SLEEVE-100",
                "quantity": 5,
                "price": 12.00
            }
        ]
    },
    timestamp=datetime.utcnow()  # Optional, defaults to now
)

result = client.track_event(purchase_event)

# Track page view
page_view = KlaviyoEvent(
    metric_name="Viewed Product",
    customer_email="customer@example.com",
    properties={
        "product_id": "PROD-001",
        "product_name": "Premium Card Binder",
        "category": "Storage",
        "price": 44.99,
        "url": "https://shop.example.com/products/premium-binder"
    }
)
client.track_event(page_view)

# Track cart abandonment
cart_event = KlaviyoEvent(
    metric_name="Started Checkout",
    customer_email="customer@example.com",
    properties={
        "cart_id": "CART-789",
        "cart_total": 89.99,
        "item_count": 3,
        "checkout_url": "https://shop.example.com/checkout/CART-789"
    }
)
client.track_event(cart_event)
```

#### Get Events

```python
# Get all events for a profile
events = client.get_events(profile_id="PROFILE123")

for event in events:
    print(f"{event.metric_name} at {event.timestamp}")
    print(f"  Properties: {event.properties}")
```

### List Management

#### Working with Lists

```python
# Get all lists
all_lists = client.get_lists()
for email_list in all_lists:
    print(f"{email_list.name} ({email_list.list_id})")
    print(f"  Subscribers: {email_list.profile_count}")
    print(f"  Created: {email_list.created}")

# Get or create a list (idempotent)
vip_list = client.get_or_create_list("VIP Customers")
newsletter_list = client.get_or_create_list("Weekly Newsletter")

# Add profiles to a list
client.add_profile_to_list(
    list_id=vip_list.list_id,
    email="customer@example.com"
)

# Add multiple profiles at once
emails = [
    "customer1@example.com",
    "customer2@example.com",
    "customer3@example.com"
]

for email in emails:
    client.add_profile_to_list(
        list_id=newsletter_list.list_id,
        email=email
    )

# Remove profile from list
client.remove_profile_from_list(
    list_id=vip_list.list_id,
    profile_id="PROFILE123"
)
```

### Segmentation

#### Working with Segments

```python
# Get all segments
segments = client.get_segments()
for segment in segments:
    print(f"{segment.name}: {segment.profile_count} profiles")

# Get profiles in a segment
segment_profiles = client.get_segment_profiles(segment_id="SEGMENT123")
for profile in segment_profiles:
    print(f"  {profile.email} - {profile.first_name} {profile.last_name}")
```

## 🔄 Data Sync Service

The sync service automates data synchronization between your e-commerce platforms and Klaviyo.

### Sync Customers from TikTok Shop

```python
from integrations.klaviyo.sync_service import KlaviyoSyncService

# Initialize sync service
sync_service = KlaviyoSyncService(api_key='your_api_key_here')

# Sync customers from TikTok Shop orders
profiles, stats = sync_service.sync_customers_from_tiktok(
    order_status='COMPLETED',  # Only sync from completed orders
    days_back=30               # Last 30 days
)

print(f"Sync complete!")
print(f"  Orders fetched: {stats['orders_fetched']}")
print(f"  Customers found: {stats['customers_found']}")
print(f"  Customers synced: {stats['customers_synced']}")
print(f"  New profiles created: {stats['customers_created']}")
print(f"  Existing profiles updated: {stats['customers_updated']}")
print(f"  Errors: {stats['errors']}")
```

### Sync Order Events

```python
# Track order events from TikTok Shop
events, stats = sync_service.sync_order_events(
    order_status='COMPLETED',
    days_back=7  # Last 7 days
)

print(f"Event sync complete!")
print(f"  Orders processed: {stats['orders_fetched']}")
print(f"  Events tracked: {stats['events_tracked']}")
print(f"  Total order value: ${stats['total_value']:.2f}")
print(f"  Failed: {stats['events_failed']}")
```

### Bulk Profile Sync

```python
from integrations.klaviyo.models import KlaviyoProfile

# Prepare profiles for bulk sync
profiles = [
    KlaviyoProfile(
        email="customer1@example.com",
        first_name="John",
        last_name="Smith",
        properties={"source": "import"}
    ),
    KlaviyoProfile(
        email="customer2@example.com",
        first_name="Jane",
        last_name="Doe",
        properties={"source": "import"}
    ),
    # ... more profiles
]

# Bulk sync with automatic batching
results, stats = sync_service.sync_profiles_bulk(
    profiles=profiles,
    batch_size=100  # Processes 100 at a time
)

print(f"Bulk sync results:")
print(f"  Total profiles: {stats['total_profiles']}")
print(f"  Created: {stats['profiles_created']}")
print(f"  Updated: {stats['profiles_updated']}")
print(f"  Failed: {stats['profiles_failed']}")
```

### Create Default Segments

```python
# Create standard customer segments
segments = sync_service.create_default_segments()

print("Default segments created:")
for key, segment in segments.items():
    print(f"  {segment.name} ({segment.list_id})")

# Available default segments:
# - All Customers: General customer list
# - New Subscribers: Recently subscribed
# - VIP Customers: High-value customers
# - Active Customers: Recently active
```

### Sync History Tracking

All sync operations are automatically tracked in the database:

```python
from database.models import KlaviyoSyncHistory
from database.connection import get_db_session

# Query sync history
with get_db_session() as session:
    recent_syncs = session.query(KlaviyoSyncHistory)\
        .filter(KlaviyoSyncHistory.sync_type == 'profile_sync')\
        .order_by(KlaviyoSyncHistory.created_at.desc())\
        .limit(10)\
        .all()

    for sync in recent_syncs:
        print(f"{sync.sync_type} - {sync.direction}")
        print(f"  Status: {sync.status}")
        print(f"  Synced: {sync.records_synced}")
        print(f"  Success: {sync.success_count}")
        print(f"  Failed: {sync.failed_count}")
        print(f"  Duration: {sync.duration_seconds}s")
        if sync.error_details:
            print(f"  Errors: {sync.error_details}")
```

## 🔧 Advanced Features

### Rate Limiting

The client automatically handles rate limiting using a token bucket algorithm:

```python
# Default rate limit: 10 requests per second with burst up to 20
# The client will automatically throttle requests to stay within limits

# Rate limiting is transparent - just make your requests normally
for email in customer_emails:
    profile = client.search_profiles(email=email)
    # Client automatically paces requests
```

### Error Handling

The integration uses a comprehensive exception hierarchy:

```python
from integrations.klaviyo.exceptions import (
    KlaviyoAPIError,         # Base exception
    KlaviyoAuthError,        # Authentication errors (401)
    KlaviyoRateLimitError,   # Rate limit errors (429)
    KlaviyoValidationError,  # Invalid parameters (400)
    KlaviyoNotFoundError,    # Resource not found (404)
    KlaviyoServerError,      # Server errors (5xx)
    KlaviyoNetworkError      # Network/timeout errors
)

try:
    profile = client.create_or_update_profile(profile_data)
except KlaviyoAuthError as e:
    # Handle authentication failure
    print(f"Auth error: {e.message}")
    # Check your API key
except KlaviyoRateLimitError as e:
    # Handle rate limit
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
    # Retry request
except KlaviyoValidationError as e:
    # Handle validation error
    print(f"Invalid data: {e.message}")
    # Fix the data and retry
except KlaviyoNotFoundError as e:
    # Handle not found
    print(f"Profile not found: {e.message}")
except KlaviyoServerError as e:
    # Handle server error
    print(f"Klaviyo server error: {e.message}")
    # Retry later
except KlaviyoNetworkError as e:
    # Handle network error
    print(f"Network error: {e.message}")
    # Check connection
except KlaviyoAPIError as e:
    # Catch-all for any Klaviyo API error
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
    profile = client.create_or_update_profile(profile_data)
except KlaviyoRateLimitError:
    # Only raised if max retries exceeded
    print("Rate limit error after all retries")
```

### Custom Timeout Configuration

```python
# Configure request timeout (default: 30 seconds)
client = KlaviyoClient(
    api_key='your_api_key',
    timeout=60  # 60 second timeout
)
```

## 🔐 Security Best Practices

### 1. Store API Keys Securely

Never hardcode API keys in your code:

```python
# ❌ BAD - Don't do this
client = KlaviyoClient(api_key='pk_abc123...')

# ✅ GOOD - Use environment variables
import os
from config.config import KLAVIYO_API_KEY

client = KlaviyoClient(api_key=KLAVIYO_API_KEY)
```

### 2. Use Private API Keys

Klaviyo has two types of API keys:

- **Private API Keys** (pk_*): For server-side use (use this)
- **Public API Keys**: For client-side JavaScript (don't use in Python)

Always use private API keys for server-side integrations.

### 3. Protect Customer Data

- Encrypt customer data in transit (HTTPS - handled automatically)
- Store PII (personally identifiable information) securely
- Implement proper access controls
- Comply with GDPR/CCPA regulations

### 4. Respect Unsubscribe Requests

Always honor unsubscribe requests:

```python
# Check subscription status before sending
profile = client.get_profile(profile_id)
if profile.subscription_status == "unsubscribed":
    # Don't send marketing emails
    pass
else:
    # Safe to send
    pass
```

### 5. Implement Consent Management

```python
# Track email consent
profile = KlaviyoProfile(
    email="customer@example.com",
    properties={
        "email_consent": True,
        "email_consent_date": "2024-01-15",
        "consent_method": "double_opt_in"
    }
)
```

## 📋 Complete Example

Here's a complete example integrating profile management, event tracking, and data sync:

```python
import os
from datetime import datetime, timedelta
from integrations.klaviyo.client import KlaviyoClient
from integrations.klaviyo.sync_service import KlaviyoSyncService
from integrations.klaviyo.models import KlaviyoProfile, KlaviyoEvent, ProfileLocation
from integrations.klaviyo.exceptions import (
    KlaviyoAPIError,
    KlaviyoAuthError,
    KlaviyoRateLimitError
)

# Configuration
API_KEY = os.environ.get('KLAVIYO_API_KEY')

def onboard_new_customer(email, first_name, last_name, phone=None):
    """Onboard a new customer to Klaviyo"""
    try:
        client = KlaviyoClient(api_key=API_KEY)

        # Create profile
        profile = KlaviyoProfile(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            properties={
                "signup_date": datetime.utcnow().isoformat(),
                "source": "website",
                "customer_status": "new"
            }
        )

        result = client.create_or_update_profile(profile)
        print(f"✓ Profile created: {result.profile_id}")

        # Track signup event
        signup_event = KlaviyoEvent(
            metric_name="Signed Up",
            customer_email=email,
            properties={
                "signup_source": "website",
                "signup_date": datetime.utcnow().isoformat()
            }
        )
        client.track_event(signup_event)
        print(f"✓ Signup event tracked")

        # Add to newsletter list
        newsletter = client.get_or_create_list("Newsletter Subscribers")
        client.add_profile_to_list(newsletter.list_id, email=email)
        print(f"✓ Added to newsletter list")

        return result

    except KlaviyoAuthError as e:
        print(f"❌ Authentication failed: {e}")
        return None
    except KlaviyoValidationError as e:
        print(f"❌ Invalid data: {e}")
        return None
    except KlaviyoAPIError as e:
        print(f"❌ API error: {e}")
        return None

def track_purchase(email, order_id, total_amount, items):
    """Track a customer purchase"""
    try:
        client = KlaviyoClient(api_key=API_KEY)

        # Track purchase event
        purchase_event = KlaviyoEvent(
            metric_name="Placed Order",
            customer_email=email,
            properties={
                "order_id": order_id,
                "total_amount": total_amount,
                "currency": "USD",
                "item_count": len(items),
                "items": items,
                "order_date": datetime.utcnow().isoformat()
            }
        )

        result = client.track_event(purchase_event)
        print(f"✓ Purchase tracked: {order_id}")

        # Update profile with purchase data
        profiles = client.search_profiles(email=email)
        if profiles:
            profile = profiles[0]
            current_orders = profile.properties.get("total_orders", 0)
            current_value = profile.properties.get("lifetime_value", 0.0)

            updated_profile = KlaviyoProfile(
                email=email,
                properties={
                    "total_orders": current_orders + 1,
                    "lifetime_value": current_value + total_amount,
                    "last_order_date": datetime.utcnow().isoformat(),
                    "last_order_amount": total_amount
                }
            )
            client.create_or_update_profile(updated_profile)
            print(f"✓ Profile updated with purchase data")

        return result

    except KlaviyoAPIError as e:
        print(f"❌ Error tracking purchase: {e}")
        return None

def sync_tiktok_shop_data():
    """Sync customer and order data from TikTok Shop"""
    try:
        sync_service = KlaviyoSyncService(api_key=API_KEY)

        # Create default segments
        print("Creating default segments...")
        segments = sync_service.create_default_segments()
        print(f"✓ Created {len(segments)} segments")

        # Sync customers from last 30 days
        print("\nSyncing customers from TikTok Shop...")
        profiles, customer_stats = sync_service.sync_customers_from_tiktok(
            order_status='COMPLETED',
            days_back=30
        )

        print(f"✓ Customer sync complete:")
        print(f"  Orders: {customer_stats['orders_fetched']}")
        print(f"  Customers synced: {customer_stats['customers_synced']}")
        print(f"  Created: {customer_stats['customers_created']}")
        print(f"  Updated: {customer_stats['customers_updated']}")

        # Sync order events from last 7 days
        print("\nSyncing order events...")
        events, event_stats = sync_service.sync_order_events(
            order_status='COMPLETED',
            days_back=7
        )

        print(f"✓ Event sync complete:")
        print(f"  Events tracked: {event_stats['events_tracked']}")
        print(f"  Total value: ${event_stats['total_value']:.2f}")
        print(f"  Failed: {event_stats['events_failed']}")

    except KlaviyoAPIError as e:
        print(f"❌ Sync error: {e}")

def get_customer_insights(email):
    """Get insights about a customer"""
    try:
        client = KlaviyoClient(api_key=API_KEY)

        # Get profile
        profiles = client.search_profiles(email=email)
        if not profiles:
            print(f"Customer {email} not found")
            return

        profile = profiles[0]

        print(f"\n📊 Customer Insights: {profile.first_name} {profile.last_name}")
        print(f"Email: {profile.email}")
        print(f"Phone: {profile.phone_number}")
        print(f"Subscription: {profile.subscription_status}")

        # Get custom properties
        if profile.properties:
            print(f"\n💰 Customer Metrics:")
            print(f"  Total Orders: {profile.properties.get('total_orders', 0)}")
            print(f"  Lifetime Value: ${profile.properties.get('lifetime_value', 0):.2f}")
            print(f"  Last Order: {profile.properties.get('last_order_date', 'N/A')}")

        # Get events
        events = client.get_events(profile_id=profile.profile_id)
        print(f"\n📅 Recent Activity ({len(events)} events):")
        for event in events[:5]:  # Show last 5 events
            print(f"  {event.metric_name} - {event.timestamp}")

    except KlaviyoAPIError as e:
        print(f"❌ Error getting insights: {e}")

# Example usage
if __name__ == '__main__':
    # Onboard new customer
    customer = onboard_new_customer(
        email="jane.doe@example.com",
        first_name="Jane",
        last_name="Doe",
        phone="+14155551234"
    )

    # Track a purchase
    if customer:
        track_purchase(
            email="jane.doe@example.com",
            order_id="ORD-12345",
            total_amount=149.98,
            items=[
                {
                    "product_id": "PROD-001",
                    "name": "Premium Card Binder",
                    "quantity": 2,
                    "price": 44.99
                },
                {
                    "product_id": "PROD-002",
                    "name": "Card Sleeves",
                    "quantity": 5,
                    "price": 12.00
                }
            ]
        )

    # Sync data from TikTok Shop
    sync_tiktok_shop_data()

    # Get customer insights
    get_customer_insights("jane.doe@example.com")
```

## ⚠️ Important Notes

### API Limitations

- **Rate Limits**: Default 10 requests per second (burst up to 20)
- **Request Size**: Maximum 5MB per request
- **Batch Size**: Recommended maximum 100 profiles per batch operation
- **Event Properties**: Maximum 1000 custom properties per event

### Best Practices

1. **Use Bulk Operations**: When syncing large datasets, use bulk sync methods
2. **Implement Idempotency**: Profile creation is idempotent (safe to retry)
3. **Track Everything**: Event tracking enables powerful segmentation
4. **Clean Your Data**: Validate email addresses before creating profiles
5. **Monitor Sync History**: Check `KlaviyoSyncHistory` table for sync health

### Testing

- Test with a small dataset first (10-100 profiles)
- Use test email addresses (yourname+test@example.com)
- Verify events appear in Klaviyo dashboard
- Test unsubscribe flow thoroughly
- Validate GDPR/CCPA compliance

### Production Checklist

- [ ] Store API key in environment variables or secure vault
- [ ] Implement error logging and monitoring
- [ ] Set up automated data sync jobs (cron/scheduled tasks)
- [ ] Configure rate limiting appropriately
- [ ] Test unsubscribe and consent management
- [ ] Implement retry logic for failed syncs
- [ ] Monitor sync history for errors
- [ ] Set up alerts for sync failures
- [ ] Document your customer segments
- [ ] Train team on Klaviyo best practices

## 📚 Additional Resources

- [Klaviyo API Documentation](https://developers.klaviyo.com/en/reference/api_overview)
- [Klaviyo Help Center](https://help.klaviyo.com/)
- [Klaviyo Developer Portal](https://developers.klaviyo.com/)
- [Email Marketing Best Practices](https://www.klaviyo.com/marketing-resources)
- [GDPR Compliance Guide](https://www.klaviyo.com/gdpr)

## 🐛 Troubleshooting

### "Authentication error: Invalid API key"

- Verify your API key is correct
- Ensure you're using a **private** API key (starts with `pk_`)
- Check that the API key hasn't been revoked
- Confirm the key has appropriate permissions

### "Rate limit exceeded"

- Client automatically retries with backoff
- If persisting, reduce request frequency
- Consider batching operations
- Check rate limit in Klaviyo account settings

### "Profile not found"

- Verify the profile ID or email is correct
- Profile may not exist - use `search_profiles()` first
- Check if profile was deleted
- Ensure you have permission to access the profile

### "Validation error: Invalid email"

- Email format must be valid (name@domain.com)
- No spaces or special characters (except @ and .)
- Email must not be a disposable/temporary address
- Check for typos in email address

### "Network timeout"

- Check internet connectivity
- Klaviyo API may be experiencing issues
- Increase timeout value if on slow connection
- Implement retry logic for transient failures

### Sync Not Working

- Check sync history in database for error details
- Verify TikTok Shop credentials are valid
- Ensure Klaviyo API key has required permissions
- Check logs for specific error messages
- Test with mock_data=True to isolate issues

### Events Not Appearing in Klaviyo

- Events may take a few minutes to appear
- Verify event was successfully tracked (check return value)
- Check customer email is valid and profile exists
- View events in Klaviyo dashboard under Metrics
- Ensure event name matches expected format

## 💡 Tips

1. **Segment Early**: Create segments as you grow, not after
2. **Track Everything**: More data = better segmentation and targeting
3. **Use External IDs**: Link Klaviyo profiles to your database IDs
4. **Clean Lists Regularly**: Remove inactive subscribers
5. **Test Email Flows**: Use Klaviyo's preview mode before sending
6. **Monitor Engagement**: Track open rates, click rates, unsubscribes
7. **A/B Test**: Use Klaviyo's A/B testing for better results
8. **Automate Wisely**: Set up triggered flows for onboarding, cart abandonment, etc.
9. **Respect Privacy**: Always honor unsubscribe requests immediately
10. **Stay Compliant**: Follow GDPR, CCPA, and CAN-SPAM regulations
