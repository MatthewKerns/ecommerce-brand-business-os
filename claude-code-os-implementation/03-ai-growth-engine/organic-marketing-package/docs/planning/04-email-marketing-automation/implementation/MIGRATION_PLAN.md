# Email Marketing Package Migration Plan

## Overview
Extracting core email marketing components from nurture-leads-automation into a niche-agnostic, reusable email marketing package.

## Core Components to Migrate

### 1. Email Infrastructure
- **Gmail API Integration** (`lib/gmail.ts`)
  - OAuth2 authentication
  - MIME message building
  - Thread management
  - Retry logic
  - Attachment support

### 2. Lead Management System
- **Lead Data Model** (abstracted)
  - Core fields: email, name, status, source, tags
  - Custom fields support (configurable per niche)
  - Engagement tracking
  - Unsubscribe handling

- **Google Sheets Integration** (`lib/google-sheets.ts`)
  - CRUD operations
  - Bidirectional sync
  - Batch operations
  - Data validation

### 3. Sequence Engine
- **Sequence Management** (`lib/ai/nurture-engine.ts`)
  - Configurable sequence patterns
  - Scheduling logic
  - Status tracking
  - Approval workflows

- **Template System**
  - Dynamic variable substitution
  - Template library
  - A/B testing support
  - Preview capabilities

### 4. AI Content Generation (abstracted)
- **AI Engine Interface** (`lib/ai/`)
  - Provider agnostic (Gemini, OpenAI, Claude)
  - Prompt templates (customizable per niche)
  - Safety filters
  - Content personalization

### 5. Analytics & Tracking
- **Event Tracking** (`api/analytics/`)
  - Open tracking (pixel)
  - Click tracking
  - Reply detection
  - Conversion funnel
  - HMAC security

### 6. API Layer
- **RESTful Endpoints**
  - Lead management
  - Sequence operations
  - Template CRUD
  - Analytics queries
  - Webhook receivers

## Components to Abstract/Replace

### 1. Niche-Specific Content
- ❌ Energy sector references
- ❌ B2B-specific fields
- ❌ Win story system (make it generic "case studies")
- ✅ Generic "success story" system

### 2. Configuration
- ❌ Hardcoded sequence patterns
- ✅ Configurable sequence builder
- ✅ Custom field definitions
- ✅ Flexible tagging system

### 3. UI Components
- ❌ Energy-specific dashboards
- ✅ Generic email marketing dashboard
- ✅ Customizable metrics cards
- ✅ Theme/branding configuration

## New Architecture

```
email-marketing-package/
├── core/                    # Core functionality
│   ├── email/              # Email sending infrastructure
│   │   ├── providers/      # Gmail, SendGrid, etc.
│   │   ├── templates/      # Template engine
│   │   └── tracking/       # Analytics tracking
│   ├── leads/              # Lead management
│   │   ├── models/         # Data models
│   │   ├── storage/        # Storage adapters (Sheets, DB)
│   │   └── import/         # Import/export
│   ├── sequences/          # Sequence management
│   │   ├── engine/         # Core sequence logic
│   │   ├── scheduler/      # Scheduling system
│   │   └── workflows/      # Approval workflows
│   └── ai/                 # AI integration
│       ├── providers/      # Gemini, OpenAI, Claude
│       ├── prompts/        # Prompt templates
│       └── personalization/# Personalization engine
├── api/                     # API layer
│   ├── rest/               # REST endpoints
│   ├── webhooks/           # Webhook handlers
│   └── graphql/            # Optional GraphQL
├── ui/                      # UI components (React)
│   ├── components/         # Reusable components
│   ├── dashboard/          # Dashboard views
│   └── config/             # Configuration UI
├── config/                  # Configuration
│   ├── default.json        # Default settings
│   ├── schema.json         # Config schema
│   └── examples/           # Example configs
└── tests/                   # Test suite
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── fixtures/           # Test data
```

## Implementation Steps

### Phase 1: Core Extraction (Week 1)
1. Set up package structure
2. Extract Gmail API integration
3. Extract Google Sheets integration
4. Abstract lead data model
5. Create provider interfaces

### Phase 2: Abstraction Layer (Week 1-2)
1. Build configuration system
2. Create template engine
3. Abstract AI prompts
4. Build sequence builder
5. Implement custom fields

### Phase 3: API & UI (Week 2)
1. Create REST API
2. Build webhook system
3. Port dashboard components
4. Create configuration UI
5. Add theming support

### Phase 4: Integration (Week 3)
1. Connect to scratch-and-win
2. Add blog subscriber import
3. Create TikTok lead capture
4. Build analytics dashboard
5. Test end-to-end flow

## Configuration Examples

### E-commerce Configuration
```json
{
  "niche": "ecommerce",
  "lead_fields": {
    "game_preference": "select",
    "purchase_history": "array",
    "cart_value": "number"
  },
  "sequences": {
    "welcome": {
      "emails": 4,
      "interval_days": 3,
      "templates": ["welcome", "brand_story", "value_prop", "urgency"]
    },
    "abandonment": {
      "emails": 3,
      "interval_hours": [24, 72, 168],
      "templates": ["reminder", "discount", "last_chance"]
    }
  },
  "tracking": {
    "conversion_events": ["purchase", "add_to_cart", "wishlist"]
  }
}
```

### B2B Configuration
```json
{
  "niche": "b2b",
  "lead_fields": {
    "company": "text",
    "role": "text",
    "industry": "select",
    "company_size": "select"
  },
  "sequences": {
    "nurture": {
      "emails": 12,
      "interval_days": 14,
      "templates": ["insight", "case_study", "tip", "soft_pitch"]
    }
  },
  "tracking": {
    "conversion_events": ["meeting_booked", "demo_requested", "contract_signed"]
  }
}
```

## Migration Benefits

1. **Reusability** - One system for all niches
2. **Maintainability** - Single codebase
3. **Flexibility** - Configuration-driven
4. **Scalability** - Multi-tenant capable
5. **Integration** - Clean API interfaces

## Next Steps
1. Review and approve plan
2. Set up package structure
3. Begin Phase 1 extraction
4. Create test harness
5. Document API interfaces