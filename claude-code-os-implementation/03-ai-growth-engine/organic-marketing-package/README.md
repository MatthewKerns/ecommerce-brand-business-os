# Organic Marketing Package

This package contains all the implementation code for the organic marketing automation system, organized as a monorepo with multiple integrated packages.

## 🏗️ Monorepo Structure

```
organic-marketing-package/
├── packages/
│   ├── content-engine/     # Core AI content generation system
│   ├── dashboard/          # Next.js management interface (coming soon)
│   └── mcf-connector/      # Multi-Channel Fulfillment service (planned)
└── .auto-claude/          # Auto-Claude configuration and roadmap
```

## 📦 Packages

### 1. Content Engine (`packages/content-engine/`)

**Complete AI-powered content generation system** with:

#### Core Components
- **AI Agents** (`src/agents/`)
  - BlogAgent - SEO-optimized blog content
  - SocialAgent - Multi-platform social media
  - AmazonAgent - E-commerce listing optimization
  - CompetitorAgent - Market analysis
  - TikTokShopAgent - TikTok product listings & video scripts
  - AEOAgent - Answer Engine Optimization
  - SEOResearchAgent - Keyword research & optimization

- **FastAPI REST API** (`src/api/`)
  - 17+ route modules for all agents
  - Review workflows with version management
  - Task endpoints for async operations
  - Full Swagger documentation at `/api/docs`

- **Integrations** (`src/integrations/`)
  - TikTok Shop API client with OAuth
  - Klaviyo email platform integration
  - Amazon SP-API connector (MCF ready)

- **Database** (`src/database/`)
  - SQLAlchemy models for content persistence
  - Migration system for schema management
  - Content history and citation tracking

#### Directory Structure
```
packages/content-engine/
├── src/                    # All source code
│   ├── agents/            # AI content generation agents
│   ├── api/               # FastAPI routes and endpoints
│   ├── config/            # Configuration management
│   ├── database/          # Database models and migrations
│   ├── integrations/      # External service integrations
│   └── utils/             # Shared utilities
├── tests/                  # Test suites
│   ├── e2e/              # End-to-end tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
│   └── testing/          # Testing guides
├── scripts/               # Utility scripts
│   └── start_services.sh  # Start API server
├── examples/              # Usage examples
└── output/                # Generated content output
```

### 2. Dashboard (`packages/dashboard/`) - Coming Soon
Next.js management interface for:
- Content generation UI
- Campaign management
- Analytics visualization
- System configuration

### 3. MCF Connector (`packages/mcf-connector/`) - Planned
TypeScript service for Multi-Channel Fulfillment:
- Order routing between platforms
- Inventory synchronization
- Shipment tracking

## 🚀 Quick Start

### For Content Engine (Currently Available)

```bash
# Navigate to content engine
cd packages/content-engine

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Start the API server
./scripts/start_services.sh
# API will be available at http://localhost:8001

# Access API documentation
open http://localhost:8001/api/docs
```

### Generate Content via API

```bash
# Generate blog post
curl -X POST http://localhost:8001/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "10 Tournament Mistakes TCG Players Make",
    "content_pillar": "Battle-Ready Lifestyle",
    "word_count": 1500
  }'

# Generate social media content
curl -X POST http://localhost:8001/api/social/instagram/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Pre-tournament ritual",
    "content_pillar": "Battle-Ready Lifestyle"
  }'
```

## 📖 Documentation

### Content Engine Documentation
- **[README](packages/content-engine/README.md)** - Comprehensive guide for content generation
- **[API Routes](packages/content-engine/src/api/)** - All API endpoints and their usage
- **[Testing Guide](packages/content-engine/docs/testing/)** - E2E and integration testing
- **[Integration Docs](packages/content-engine/src/integrations/)** - External service setup

### Roadmap & Planning
- **[Roadmap](/.auto-claude/roadmap/roadmap.json)** - Feature roadmap with 40+ planned enhancements
- **[Build Button Fix](/.auto-claude/roadmap/BUILD_BUTTON_FIX.md)** - Recent roadmap updates
- **[Enhancement Summary](/.auto-claude/roadmap/ROADMAP_ENHANCEMENT_SUMMARY.md)** - Latest roadmap additions

## 🔧 Development

### Running Tests

```bash
# Content Engine tests
cd packages/content-engine
pytest tests/                    # Run all tests
pytest tests/e2e/               # Run E2E tests only
pytest tests/integration/       # Run integration tests
```

### API Development

The FastAPI server includes:
- Auto-reload in development mode
- Swagger UI at `/api/docs`
- ReDoc at `/api/redoc`
- OpenAPI schema at `/api/openapi.json`

### Environment Variables

Required environment variables for content-engine:
```
ANTHROPIC_API_KEY=your-api-key-here
OPENAI_API_KEY=optional-for-embeddings
TIKTOK_APP_ID=your-tiktok-app-id
TIKTOK_APP_SECRET=your-tiktok-secret
KLAVIYO_API_KEY=your-klaviyo-key
```

## 🗺️ Current Status

### ✅ Completed
- Core content generation agents (15+ agents)
- FastAPI REST API with full documentation
- Database schema and migrations
- TikTok Shop & Klaviyo integrations
- Review workflow system
- E2E testing framework

### 🚧 In Progress
- Frontend-backend bridge (feature-30)
- Authentication layer (JWT)
- Dashboard UI components

### 📋 Planned
- Blog Content Creation UI (feature-32)
- Social Media Pipeline (feature-33)
- Real-time Analytics (feature-35)
- Email Sequence Builder (feature-37)
- Workflow Automation (feature-39)

See [roadmap](/.auto-claude/roadmap/roadmap.json) for complete feature list.

## 🤝 Contributing

1. Check the roadmap for planned features
2. Create a worktree for development
3. Follow the monorepo structure
4. Add tests for new features
5. Update documentation

## 📚 Resources

- [Content Engine README](packages/content-engine/README.md) - Detailed agent documentation
- [API Documentation](http://localhost:8001/api/docs) - Interactive API docs (when running)
- [Testing Guide](packages/content-engine/docs/testing/) - Testing best practices
