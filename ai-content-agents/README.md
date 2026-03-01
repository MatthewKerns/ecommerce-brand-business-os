# AI Content Agents

A Python-based content generation and e-commerce integration system for the Infinity Vault brand. This toolkit leverages the Anthropic API to generate brand-aligned marketing content and provides production-ready integrations with major e-commerce platforms.

## Overview

AI Content Agents is a modular system that combines intelligent content generation with platform integrations to streamline e-commerce operations. The system consists of:

- **Content Generation Agents**: Specialized AI agents for blog posts, social media, Amazon listings, and competitor analysis
- **Platform Integrations**: Production-ready connections to TikTok Shop and Amazon SP-API
- **REST API**: FastAPI-based API for programmatic access to all functionality
- **Database Layer**: SQLAlchemy ORM for persistent content storage and retrieval
- **Testing Framework**: Comprehensive unit and integration tests

## Features

### Content Generation Agents

| Agent | Purpose | Capabilities |
|-------|---------|-------------|
| **BlogAgent** | SEO-optimized blog content | Blog posts, listicles, how-to guides, series outlines |
| **SocialAgent** | Social media content | Instagram captions, Reddit posts, carousel scripts, content calendars |
| **AmazonAgent** | Amazon listing optimization | Product titles, bullet points, descriptions, A+ content, backend keywords |
| **CompetitorAgent** | Competitive intelligence | Listing analysis, review mining, comparison reports, content gap identification |
| **TikTokShopAgent** | TikTok Shop management | Product synchronization, order management, analytics, OAuth authentication |

All content is automatically aligned with the **Infinity Vault** brand voice: authoritative, battle-tested, and positioned as "Battle-Ready Equipment" for serious TCG/Pokemon collectors and tournament players.

### Platform Integrations

#### TikTok Shop Integration
- **OAuth2 Authentication**: Complete OAuth flow with token management
- **Product Synchronization**: Bi-directional catalog sync
- **Order Management**: Real-time order retrieval and processing
- **Analytics Dashboard**: Performance metrics and order analytics
- **Rate Limiting**: Intelligent throttling with exponential backoff

#### Amazon SP-API Multi-Channel Fulfillment (MCF)
- **SP-API Authentication**: LWA (Login with Amazon) OAuth implementation with automatic token refresh
- **MCF Order Creation**: Route TikTok orders (or any channel) to Amazon's fulfillment network
- **Inventory Management**: Real-time inventory level queries for MCF-eligible SKUs
- **Shipment Tracking**: Retrieve tracking numbers and delivery status
- **Order Lifecycle**: Create, retrieve, cancel, and list fulfillment orders

The MCF integration solves a critical market gap: **reliable 2-3 day shipping for TikTok Shop orders** using Amazon's proven fulfillment infrastructure. This is the core differentiator that no competitor currently offers.

📚 **Detailed MCF Documentation**: See [`integrations/amazon_sp_api/README.md`](./integrations/amazon_sp_api/README.md) for:
- Complete setup instructions (Seller Central, SP-API app registration, refresh token generation)
- API reference for all MCFClient methods
- Code examples for order creation, inventory queries, and shipment tracking
- Error handling patterns and troubleshooting guide
- Security best practices and rate limit management

### REST API

FastAPI-based REST API with:
- Full CRUD operations for all content types
- OpenAPI/Swagger documentation
- Centralized error handling
- Request validation with Pydantic models
- Production-ready deployment patterns

### Database Layer

SQLAlchemy ORM with:
- Content persistence for all generated content
- Migration system for schema updates
- Relationship management between entities
- Query optimization and indexing

## Installation

### Prerequisites

- Python 3.9 or higher
- Virtual environment tool (venv, virtualenv, or conda)
- Active Anthropic API key
- (Optional) Amazon Seller Central account with FBA inventory for MCF
- (Optional) TikTok Shop seller account

### Setup

1. **Clone the repository**:
   ```bash
   cd ai-content-agents
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```bash
   # Anthropic API
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # Amazon SP-API (for MCF integration)
   AMAZON_SELLER_ID=A1BCDEFGH2IJKL
   AMAZON_SP_API_CLIENT_ID=amzn1.application-oa2-client.xxxxxxxxxxxxx
   AMAZON_SP_API_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   AMAZON_SP_API_REFRESH_TOKEN=Atzr|IwEBIxxxxxxxxxxxxxxxxxxxxxx
   AMAZON_SP_API_REGION=us-east-1
   AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER

   # TikTok Shop (optional)
   TIKTOK_SHOP_APP_KEY=your_app_key
   TIKTOK_SHOP_APP_SECRET=your_app_secret
   ```

5. **Verify installation**:
   ```bash
   python -m pytest tests/ -v
   ```

## Quick Start

### Generate Blog Content

```python
from agents.blog_agent import BlogAgent

agent = BlogAgent()
blog_post = agent.generate_blog_post(
    topic="How to Protect Your Pokemon Cards During Tournament Travel",
    tone="authoritative",
    word_count=1200
)
print(blog_post)
```

### Create MCF Fulfillment Order

```python
from integrations.amazon_sp_api.mcf_client import MCFClient
from integrations.amazon_sp_api.models import (
    Address, MCFOrderItem, MCFFulfillmentOrder, ShippingSpeedCategory
)

# Initialize MCF client (uses environment variables)
client = MCFClient()

# Define shipping address
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
print(f"✓ Order created: {response}")
```

### Check MCF Inventory

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

### Generate Amazon Listing

```python
from agents.amazon_agent import AmazonAgent

agent = AmazonAgent()
listing = agent.generate_listing(
    product_name="Infinity Vault Premium 12-Pocket Binder",
    features=["Archival-safe pages", "Reinforced D-rings", "Tournament-ready"],
    target_keywords=["pokemon card binder", "tcg storage", "trading card protection"]
)
print(listing["title"])
print(listing["bullet_points"])
```

## Project Structure

```
ai-content-agents/
├── agents/                     # Content generation agents
│   ├── base_agent.py          # Base agent class with common functionality
│   ├── blog_agent.py          # Blog content generation
│   ├── social_agent.py        # Social media content
│   ├── amazon_agent.py        # Amazon listing optimization
│   ├── competitor_agent.py    # Competitive analysis
│   └── tiktok_shop_agent.py   # TikTok Shop integration
├── integrations/              # Platform integrations
│   ├── amazon_sp_api/         # Amazon SP-API MCF integration
│   │   ├── auth.py            # LWA OAuth authentication
│   │   ├── mcf_client.py      # MCF API client
│   │   ├── models.py          # Data models for orders and inventory
│   │   └── README.md          # Detailed MCF documentation
│   └── tiktok_shop/           # TikTok Shop integration
│       ├── auth.py            # OAuth2 authentication
│       ├── client.py          # TikTok Shop API client
│       └── models.py          # Data models for products and orders
├── api/                       # FastAPI REST API
│   ├── routes/                # API route definitions
│   ├── models.py              # Pydantic request/response models
│   └── main.py                # API application entry point
├── database/                  # Database layer
│   ├── models.py              # SQLAlchemy ORM models
│   ├── migrations/            # Alembic migration scripts
│   └── connection.py          # Database connection management
├── config/                    # Configuration management
│   ├── config.py              # Environment-based configuration
│   ├── secrets.py             # Encrypted secrets management
│   └── .env.example           # Environment variable template
├── tests/                     # Test suite
│   ├── test_amazon_sp_auth.py # MCF authentication tests
│   ├── test_mcf_client.py     # MCF client tests
│   ├── test_agents.py         # Content agent tests
│   └── conftest.py            # Pytest configuration and fixtures
├── examples/                  # Example scripts and usage demonstrations
│   └── test_mcf_integration.py # MCF integration test example
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md                  # This file
```

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test Suites

```bash
# MCF authentication tests
python -m pytest tests/test_amazon_sp_auth.py -v

# MCF client tests
python -m pytest tests/test_mcf_client.py -v

# Content agent tests
python -m pytest tests/test_agents.py -v
```

### Integration Tests

Run MCF integration test (requires valid Amazon credentials):

```bash
# Dry-run mode (safe, no orders created)
python examples/test_mcf_integration.py --dry-run

# Test specific SKU
python examples/test_mcf_integration.py --sku DECK-BOX-001

# Full integration test (creates real order - use with caution)
python examples/test_mcf_integration.py
```

## Configuration

### Environment Variables

All sensitive credentials are managed through environment variables. See `.env.example` for the complete list of required and optional variables.

**Required for core functionality**:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

**Required for MCF integration**:
- `AMAZON_SELLER_ID`: Your Amazon Seller/Merchant ID
- `AMAZON_SP_API_CLIENT_ID`: SP-API application client ID
- `AMAZON_SP_API_CLIENT_SECRET`: SP-API application secret
- `AMAZON_SP_API_REFRESH_TOKEN`: LWA refresh token
- `AMAZON_SP_API_REGION`: AWS region (e.g., us-east-1)
- `AMAZON_MARKETPLACE_ID`: Amazon marketplace ID (e.g., ATVPDKIKX0DER for US)

**Required for TikTok Shop integration**:
- `TIKTOK_SHOP_APP_KEY`: TikTok Shop app key
- `TIKTOK_SHOP_APP_SECRET`: TikTok Shop app secret

### Multi-Environment Support

The system supports multiple environments (development, staging, production):

```bash
# Development (default)
export ENVIRONMENT=development

# Staging
export ENVIRONMENT=staging

# Production
export ENVIRONMENT=production
```

Each environment can have its own `.env.{environment}` file.

## Security Best Practices

### Credential Storage
- **Never commit credentials** to version control
- Store credentials in environment variables or secure vaults (AWS Secrets Manager, HashiCorp Vault)
- Use `.env` files locally (automatically excluded from git via `.gitignore`)
- Rotate API keys and refresh tokens periodically

### Token Management
- Access tokens are automatically cached and refreshed
- Thread-safe token refresh prevents race conditions
- Tokens expire after 3600 seconds (1 hour)
- Refresh tokens are long-lived but can be revoked

### API Rate Limits
- Implement exponential backoff for retries
- Monitor API usage in respective platform dashboards
- Cache data when possible to reduce API calls

## Troubleshooting

### MCF Authentication Errors

**Error**: `SPAPIAuthError: Missing required credentials`

**Solution**: Verify all Amazon SP-API environment variables are set:
```bash
echo $AMAZON_SP_API_CLIENT_ID
echo $AMAZON_SP_API_CLIENT_SECRET
echo $AMAZON_SP_API_REFRESH_TOKEN
```

### MCF Order Creation Fails

**Common causes**:
- SKU not found or not MCF-eligible
- Invalid shipping address format
- Insufficient inventory
- Marketplace ID mismatch

**Debug steps**:
1. Verify SKU exists: `client.get_inventory_summaries(skus=["YOUR-SKU"])`
2. Check address format matches SP-API requirements
3. Confirm marketplace ID matches your Seller Central region

### Content Generation Issues

**Error**: `AnthropicAPIError: rate_limit_error`

**Solution**: Implement rate limiting in your application or reduce concurrent requests.

## Contributing

When contributing to this project:

1. Follow existing code patterns and conventions
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure all tests pass before submitting
5. Use clear, descriptive commit messages

## Resources

### Amazon SP-API
- [SP-API Documentation](https://developer-docs.amazon.com/sp-api/)
- [MCF API Reference](https://developer-docs.amazon.com/sp-api/docs/fulfillment-outbound-api-v2020-07-01-reference)
- [Marketplace IDs](https://developer-docs.amazon.com/sp-api/docs/marketplace-ids)

### TikTok Shop
- [TikTok Shop API Documentation](https://partner.tiktokshop.com/docv2/page/6507ead7b99d02028a0252a8)

### Anthropic
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Model Specifications](https://docs.anthropic.com/claude/docs/models-overview)

## License

This project is part of the E-Commerce Brand Business OS. Refer to the main repository license for terms.

## Related Documentation

- [Main README](../README.md)
- [MCF Integration Guide](./integrations/amazon_sp_api/README.md)
- [Configuration Guide](../CONFIGURATION.md)
- [Business Operating System Documentation](../claude-code-os-implementation/README.md)
