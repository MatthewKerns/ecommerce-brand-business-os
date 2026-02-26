# MCF Connector Integration Overview

## What It Is

A custom MCP (Model Context Protocol) Connector app that bridges TikTok Shop with Amazon Multi-Channel Fulfillment (MCF) and provides analytics integrations. Being developed in a separate repository.

This document describes what the connector does, how it fits into the organic marketing package, and the data flows between systems.

---

## Core Function: TikTok Shop Orders → Amazon FBA Fulfillment

When a customer buys through TikTok Shop, the order needs to be fulfilled. Instead of managing separate inventory and shipping for TikTok, the MCF Connector routes TikTok Shop orders to Amazon's Multi-Channel Fulfillment service — using inventory already stored in Amazon FBA warehouses.

### Order Flow
```
Customer sees organic TikTok content
    ↓
Clicks product in TikTok Shop
    ↓
Completes purchase on TikTok
    ↓
TikTok Shop Order Created
    ↓
MCF Connector receives order webhook
    ↓
Connector transforms order data → Amazon MCF format
    ↓
Submits fulfillment request to Amazon MCF API
    ↓
Amazon FBA warehouse picks, packs, ships
    ↓
Tracking number sent back to TikTok Shop
    ↓
Customer gets their gear
```

### Why MCF?
- **No duplicate inventory**: Use existing Amazon FBA stock
- **Amazon's logistics**: Fast, reliable shipping
- **Lower cost**: No need for separate 3PL for TikTok orders
- **Scalable**: As TikTok volume grows, fulfillment scales automatically
- **Simple**: One inventory pool across Amazon + TikTok

---

## Secondary Function: TikTok Shop Metrics Integration

Beyond order fulfillment, the connector also pulls TikTok Shop data into our analytics system. This is critical for tracking the organic marketing strategy's performance.

### Metrics Pulled from TikTok Shop API

**Video Performance Metrics**:
| Metric | Description | Why It Matters |
|--------|-------------|---------------|
| Video Views | Total views per video | Reach measurement |
| Video Saves | Number of saves | High-intent engagement (key metric) |
| Save Rate | Saves / Views | Content quality signal |
| Comments | Number of comments | Community engagement |
| Shares | Number of shares | Viral potential |
| Watch Time | Average view duration | Content quality signal |
| Profile Visits | Views → profile visits | Funnel progression |

**Shop Metrics**:
| Metric | Description | Why It Matters |
|--------|-------------|---------------|
| Product Views | Views on shop listing | Purchase intent |
| Add to Cart | Cart additions | High purchase intent |
| Orders | Completed purchases | Revenue |
| Revenue | Total sales | Bottom line |
| Conversion Rate | Views → purchases | Shop effectiveness |
| Return Rate | Returns / orders | Product satisfaction |

**Channel-Level Metrics** (Per Elemental Channel):
| Metric | Air | Water | Fire | Earth |
|--------|-----|-------|------|-------|
| Followers | — | — | — | — |
| Follower Growth | — | — | — | — |
| Avg Views/Video | — | — | — | — |
| Avg Saves/Video | — | — | — | — |
| Shop Clicks | — | — | — | — |
| Revenue Attributed | — | — | — | — |

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCF CONNECTOR                         │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  TikTok Shop │    │   Order      │    │  Amazon    │ │
│  │  API Client  │───▶│  Transformer │───▶│  MCF API   │ │
│  │              │    │              │    │  Client    │ │
│  └──────┬───────┘    └──────────────┘    └─────┬──────┘ │
│         │                                       │        │
│  ┌──────▼───────┐                        ┌──────▼──────┐ │
│  │  Metrics     │                        │  Tracking   │ │
│  │  Collector   │                        │  Sync       │ │
│  │  (Saves,     │                        │  (Shipping  │ │
│  │   Views,     │                        │   numbers   │ │
│  │   Revenue)   │                        │   back to   │ │
│  └──────┬───────┘                        │   TikTok)   │ │
│         │                                └─────────────┘ │
│  ┌──────▼───────┐                                        │
│  │  Analytics   │                                        │
│  │  Dashboard   │                                        │
│  │  Export      │                                        │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

---

## TikTok Shop API Endpoints Used

### Content Publishing API
- `POST /content/post/publish/` — Schedule and publish videos
- `GET /content/post/list/` — List published content
- `GET /content/post/info/` — Get video performance data

### Shop API
- `GET /order/list/` — Retrieve new orders
- `GET /order/detail/` — Get order details for fulfillment
- `POST /fulfillment/shipping_info/` — Update tracking info
- `GET /product/list/` — Product catalog sync
- `GET /analytics/shop/` — Shop-level analytics

### Data API (Metrics)
- `GET /data/video/list/` — Video performance metrics
- `GET /data/shop/overview/` — Shop performance overview

---

## Amazon MCF API Endpoints Used

### Fulfillment API
- `POST /fba/outbound/createFulfillmentOrder` — Create MCF order
- `GET /fba/outbound/getFulfillmentOrder` — Check order status
- `GET /fba/outbound/getPackageTrackingDetails` — Get tracking

### Inventory API
- `GET /fba/inventory/summaries` — Check FBA stock levels
- Inventory sync to prevent overselling across channels

---

## Authentication & Security

### TikTok Shop
- OAuth 2.0 app authorization
- App Key + App Secret
- Access Token (refreshable)
- Seller account authorization required

### Amazon SP-API (MCF)
- LWA (Login with Amazon) OAuth
- AWS IAM role + STS tokens
- SP-API credentials (client ID + secret)
- Refresh token for persistent access

### Security Requirements
- All credentials stored as environment variables (never in code)
- API tokens encrypted at rest
- Rate limiting respected for both APIs
- Webhook signature verification for TikTok order notifications
- Error handling with retry logic for network failures

---

## How This Connects to the Organic Marketing Package

The MCF Connector is the operational backbone:

1. **TikTok Content Automation** creates and posts videos → viewers buy in TikTok Shop → **MCF Connector fulfills the order**
2. **Analytics & Tracking** needs metrics → **MCF Connector pulls saves, views, revenue data**
3. **Email Marketing** needs purchase data for post-purchase sequences → **MCF Connector can trigger events on order creation**
4. **Service Packaging** needs to show ROI → **MCF Connector provides the revenue attribution data**

Without the connector, TikTok Shop orders can't be fulfilled efficiently and analytics are manual.

---

## Development Status

| Component | Status | Location |
|-----------|--------|----------|
| MCF Connector Core App | In Development | Separate repository |
| TikTok Shop API Integration | In Development | Separate repository |
| Amazon MCF API Integration | Planned | Separate repository |
| Metrics Collection | Planned | Separate repository |
| Analytics Dashboard | Planned | This repo (06-analytics) |
| Order Webhook Handler | Planned | Separate repository |

---

## Setup for Infinity Vault (First Account)

### Prerequisites
1. TikTok Shop Seller Account (approved and active)
2. TikTok Shop API app (approved for Content + Shop + Data scopes)
3. Amazon Seller Central account with FBA inventory
4. Amazon SP-API app (approved for Fulfillment scope)
5. Products listed in both TikTok Shop and Amazon

### Configuration
```
TIKTOK_APP_KEY=<your-app-key>
TIKTOK_APP_SECRET=<your-app-secret>
TIKTOK_ACCESS_TOKEN=<your-access-token>
TIKTOK_SHOP_ID=<your-shop-id>

AMAZON_CLIENT_ID=<your-sp-api-client-id>
AMAZON_CLIENT_SECRET=<your-sp-api-client-secret>
AMAZON_REFRESH_TOKEN=<your-refresh-token>
AMAZON_SELLER_ID=<your-seller-id>
AMAZON_MARKETPLACE_ID=<us-marketplace-id>
```

### Verify Integration
1. Create test order in TikTok Shop
2. Confirm MCF Connector picks up order
3. Confirm Amazon MCF fulfillment request created
4. Confirm tracking number synced back to TikTok Shop
5. Confirm metrics collection working (saves, views)
