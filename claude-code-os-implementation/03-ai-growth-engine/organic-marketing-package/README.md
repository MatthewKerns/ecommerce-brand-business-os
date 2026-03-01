# Organic Marketing Package

This package contains all the implementation code for the organic marketing automation system.

## Components

### 1. Content Agents (`content-agents/`)
Python-based AI content generation system with:
- Blog, Social, Amazon, Competitor, and TikTok Shop agents
- FastAPI REST API
- Database persistence
- Platform integrations (TikTok Shop, Amazon SP-API)

### 2. MCF Connector (`mcf-connector/`)
TypeScript service for Multi-Channel Fulfillment:
- Order routing between TikTok Shop and Amazon MCF
- Inventory synchronization
- Shipment tracking

### 3. Dashboard (`dashboard/`)
Next.js management interface:
- System health monitoring
- Configuration management
- Metrics visualization
- Multi-tenant workspace support

## Quick Start

```bash
# Install all dependencies
./scripts/setup-all.sh

# Start all services
./scripts/start-services.sh

# Run all tests
./scripts/test-all.sh
```

## Environment Setup

1. Copy `.env.example` files in each component
2. Add your API keys
3. Start services

See [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md) for detailed instructions.

## Documentation

All documentation is organized under [`docs/`](docs/README.md):

- **[Architecture](docs/architecture/)** - System design, database schema, component architecture
- **[API](docs/api/)** - REST API design, error handling, validation
- **[Guides](docs/guides/)** - Setup, configuration, and usage guides
- **[Planning](docs/planning/)** - Phase-based planning documents for each component
- **[Verification](docs/verification/)** - Test results and QA reports
