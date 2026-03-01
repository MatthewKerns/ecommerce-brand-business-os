# MCF Connector

TypeScript service for Multi-Channel Fulfillment, bridging TikTok Shop orders to Amazon MCF.

## Features

- Order routing between TikTok Shop and Amazon MCF
- Inventory synchronization across channels
- Shipment tracking and status updates
- TikTok Shop metrics collection (saves, views, engagement)

## Setup

```bash
cd packages/mcf-connector
npm install
cp .env.example .env
```

## Development

```bash
npm run dev          # Start with file watching
npm run build        # Compile TypeScript
npm run test         # Run all tests
npm run test:unit    # Unit tests only
npm run test:e2e     # End-to-end tests
```

## Previous Location

Migrated from `mcf-connector/` in the package root.
