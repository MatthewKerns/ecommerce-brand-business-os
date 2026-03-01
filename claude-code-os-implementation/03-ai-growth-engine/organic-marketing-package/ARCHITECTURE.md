# Organic Marketing Package Architecture

## System Overview

The Organic Marketing Package is a comprehensive AI-powered marketing automation system designed as a monorepo containing multiple integrated services. It enables automated content generation, multi-channel publishing, and performance analytics for e-commerce brands.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Dashboard (Next.js)                      │
│                    [Coming Soon - Feature 30-41]                 │
├─────────────────────────────────────────────────────────────────┤
│                      API Gateway / Auth Layer                    │
│                         [JWT - Feature 30]                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        Content Engine API                        │
│                          (FastAPI/Python)                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Blog Routes  │Social Routes │Amazon Routes │Review Routes │ │
│  ├──────────────┼──────────────┼──────────────┼──────────────┤ │
│  │  AI Agents   │  AI Agents   │  AI Agents   │Task Manager │ │
│  │  (Claude)    │  (Claude)    │  (Claude)    │   (Async)    │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                         Data Layer                               │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │   SQLite     │  PostgreSQL  │    Redis     │  File Store  │ │
│  │  (Dev/Test)  │(Production) │   (Cache)    │  (Output)    │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                     External Integrations                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │  TikTok Shop │   Klaviyo    │ Amazon SP-API│   Claude AI  │ │
│  │     API      │Email Platform│     (MCF)    │   (Content)  │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Package Structure

### `/packages/content-engine/` - Core AI System

The content engine is the heart of the system, providing AI-powered content generation and management.

#### Components

1. **AI Agents** (`src/agents/`)
   - `BaseAgent`: Abstract base class with brand context loading
   - `BlogAgent`: SEO-optimized blog content generation
   - `SocialAgent`: Multi-platform social media content
   - `AmazonAgent`: E-commerce listing optimization
   - `TikTokShopAgent`: TikTok product listings and video scripts
   - `CompetitorAgent`: Market analysis and review mining
   - `AEOAgent`: Answer Engine Optimization for AI search
   - `SEOResearchAgent`: Keyword research and content optimization

2. **REST API** (`src/api/`)
   - FastAPI application with 17+ route modules
   - Swagger/OpenAPI documentation
   - CORS support for frontend integration
   - Error handling and validation
   - Review workflow endpoints
   - Task management for async operations

3. **Database Layer** (`src/database/`)
   - SQLAlchemy ORM models
   - Migration system
   - Content versioning
   - Citation tracking
   - Abandoned cart recovery

4. **Integrations** (`src/integrations/`)
   - TikTok Shop OAuth and API client
   - Klaviyo email platform connector
   - Amazon SP-API for MCF
   - Extensible integration framework

5. **Configuration** (`src/config/`)
   - Centralized configuration management
   - Environment variable handling
   - Brand context paths
   - API credentials

### `/packages/dashboard/` - Management UI [Planned]

Next.js-based dashboard for system management and content operations.

#### Planned Features
- Content generation interface
- Campaign management
- Real-time analytics
- Workflow automation builder
- Credential management

### `/packages/mcf-connector/` - Multi-Channel Fulfillment [Planned]

TypeScript service for order routing and inventory management.

#### Planned Features
- TikTok Shop → Amazon MCF order routing
- Real-time inventory sync
- Shipment tracking
- Error recovery and retry logic

## 🔄 Data Flow

### Content Generation Flow

```
1. User Request (Dashboard/API)
        ↓
2. API Route Handler
        ↓
3. Agent Selection & Initialization
        ↓
4. Brand Context Loading
        ↓
5. Claude AI API Call
        ↓
6. Content Generation
        ↓
7. Database Persistence
        ↓
8. File System Storage
        ↓
9. Response to User
```

### Review Workflow

```
1. Initial Content Generation
        ↓
2. Save as Version 1
        ↓
3. Review & Edit
        ↓
4. Save as Version 2
        ↓
5. Approval Process
        ↓
6. Publish to Platforms
```

## 🔐 Security Architecture

### Authentication & Authorization
- JWT-based authentication (Feature-30)
- API key management for external services
- Environment-based credential storage
- OAuth 2.0 for TikTok Shop

### Data Security
- Encrypted credential storage
- HTTPS/TLS for all API communication
- Input validation and sanitization
- SQL injection prevention via ORM

## 🚀 Deployment Architecture

### Development
```
- Local SQLite database
- Single FastAPI server
- Hot-reload enabled
- Mock external services for testing
```

### Production
```
- PostgreSQL database
- Multiple FastAPI workers (Gunicorn)
- Redis for caching and sessions
- Load balancer (Nginx/Traefik)
- Container orchestration (Docker/K8s)
```

## 📊 Database Schema

### Core Tables

1. **content**
   - Stores all generated content
   - Versioning support
   - Metadata and timestamps

2. **reviews**
   - Review workflow tracking
   - Approval status
   - Version relationships

3. **tasks**
   - Async task management
   - Status tracking
   - Result storage

4. **citations**
   - Source tracking
   - Content relationships

5. **abandoned_carts**
   - Cart recovery data
   - Email campaign tracking

## 🔌 Integration Points

### Inbound
- REST API endpoints for all operations
- Webhook receivers for platform events
- OAuth callbacks for authentication

### Outbound
- Claude AI API for content generation
- TikTok Shop API for product management
- Klaviyo API for email campaigns
- Amazon SP-API for fulfillment

## 📈 Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Redis for shared state
- Load balancer distribution

### Performance Optimization
- Content caching strategies
- Async task processing
- Database query optimization
- CDN for static assets

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **AI**: Claude (Anthropic)
- **Task Queue**: Celery (planned)
- **Cache**: Redis (planned)

### Frontend (Planned)
- **Framework**: Next.js 14
- **UI Library**: React
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query

### Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus/Grafana (planned)

## 🔄 Development Workflow

1. **Local Development**
   - Clone repository
   - Set up virtual environment
   - Configure `.env` file
   - Run development server

2. **Testing**
   - Unit tests for agents
   - Integration tests for API
   - E2E tests for workflows
   - Performance testing

3. **Deployment**
   - Build Docker image
   - Push to registry
   - Deploy to staging
   - Run smoke tests
   - Deploy to production

## 📚 Key Design Patterns

### Agent Inheritance Pattern
All agents inherit from `BaseAgent`, providing:
- Consistent brand context loading
- Standardized content generation
- Unified error handling
- Common output formatting

### Repository Pattern
Database operations abstracted through repositories:
- Clean separation of concerns
- Testable data access
- Database-agnostic design

### Strategy Pattern
Content generation strategies based on platform:
- Platform-specific formatting
- Optimized for each channel
- Extensible for new platforms

## 🎯 Design Principles

1. **Modularity**: Each component is self-contained
2. **Extensibility**: Easy to add new agents/integrations
3. **Scalability**: Designed for growth
4. **Maintainability**: Clear separation of concerns
5. **Testability**: Comprehensive test coverage

## 🚦 Current Status

### ✅ Implemented
- Core content generation agents
- FastAPI REST API
- Database layer with migrations
- TikTok Shop & Klaviyo integrations
- Review workflow system
- E2E testing framework

### 🚧 In Progress
- Frontend-backend bridge (Feature-30)
- JWT authentication
- Dashboard UI components

### 📋 Planned
- Real-time analytics dashboard
- Email sequence builder
- Workflow automation
- MCF connector service

## 📖 Related Documentation

- [README](README.md) - Getting started guide
- [MIGRATION_GUIDE](MIGRATION_GUIDE.md) - Structure migration reference
- [Content Engine README](packages/content-engine/README.md) - Detailed agent docs
- [Roadmap](/.auto-claude/roadmap/roadmap.json) - Feature planning