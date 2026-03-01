# System Architecture

## Overview

This document defines the architectural patterns, structure, and design principles for the E-Commerce Brand Business OS. The system is designed as a hybrid monorepo containing both a structured knowledge framework (Business OS) and executable Python services (AI Content Agents).

## Design Philosophy

The architecture follows these core principles:

1. **Separation of Concerns**: Business knowledge (markdown) is separated from execution logic (Python)
2. **Inheritance-Based Agent Design**: All specialized agents inherit from a common `BaseAgent` class
3. **Configuration-Driven**: Brand context and settings are centralized in configuration files
4. **Path-Based Organization**: Clear directory structure for discoverability and maintenance
5. **Zero Friction Execution**: Simple CLI interfaces and minimal setup requirements

## Monorepo Structure

```
ecommerce-brand-business-os/
├── ai-content-agents/                 # Python service layer
│   ├── agents/                        # AI agent implementations
│   ├── config/                        # Configuration and brand context
│   ├── database/                      # Database models and schema (future)
│   ├── api/                           # REST API layer (future)
│   ├── tests/                         # Test suite (future)
│   └── logs/                          # Application logs (future)
├── claude-code-os-implementation/     # Knowledge and workflow layer
│   ├── 01-executive-office/           # Strategic planning
│   ├── 02-operations/                 # Project management
│   ├── 03-ai-growth-engine/           # Business strategy
│   ├── 04-content-team/               # Content strategy
│   ├── 05-hr-department/              # Agent creation framework
│   ├── 06-knowledge-base/             # Persistent memory
│   ├── 07-workflows/                  # Automation routines
│   ├── 08-technical-architecture/     # System design
│   ├── 09-templates/                  # Reusable assets
│   └── 10-implementation-roadmap/     # Rollout plan
├── docs/                              # Technical documentation
└── .auto-claude/                      # Automation framework
```

### Layer Responsibilities

**Knowledge Layer** (`claude-code-os-implementation/`)
- Stores business strategy, brand voice, and positioning
- Defines workflows and automation routines
- Maintains persistent context and memory
- Provides templates and reusable patterns

**Service Layer** (`ai-content-agents/`)
- Executes content generation via Anthropic API
- Implements agent logic and prompt engineering
- Manages API interactions and error handling
- Provides CLI and future REST API interfaces

## Service Organization

### AI Content Agents Architecture

```
ai-content-agents/
├── agents/
│   ├── base_agent.py          # Abstract base class
│   ├── blog_agent.py          # Blog content specialization
│   ├── social_agent.py        # Social media specialization
│   ├── amazon_agent.py        # E-commerce listing specialization
│   └── competitor_agent.py    # Analysis specialization
├── config/
│   ├── config.py              # Centralized configuration
│   └── __init__.py
├── database/                   # Future: data persistence
├── api/                        # Future: REST endpoints
├── tests/                      # Future: test suite
└── generate_content.py         # CLI entry point
```

### Agent Hierarchy

```
BaseAgent (base_agent.py)
    │
    ├── BlogAgent
    │   └── Specializes in: posts, listicles, series outlines
    │
    ├── SocialAgent
    │   └── Specializes in: Instagram, Reddit, carousels
    │
    ├── AmazonAgent
    │   └── Specializes in: titles, bullets, A+ content
    │
    └── CompetitorAgent
        └── Specializes in: listing analysis, review mining
```

## Design Patterns

### 1. Template Method Pattern (BaseAgent)

The `BaseAgent` class defines the skeleton of content generation while allowing subclasses to override specific steps.

**Key Methods**:
- `_load_brand_context()`: Loads brand voice, strategy, and positioning
- `_build_system_prompt()`: Constructs AI system prompt with brand context
- `generate_content()`: Core generation method using Anthropic API
- `save_output()`: Standardized file saving with metadata
- `generate_and_save()`: Convenience method combining generation and persistence

**Example**:
```python
class BaseAgent:
    def __init__(self, agent_name: str, model: str = DEFAULT_MODEL):
        self.agent_name = agent_name
        self.model = model
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.brand_context = self._load_brand_context()

    def generate_content(self, prompt: str, system_context: str = "",
                        max_tokens: int = DEFAULT_MAX_TOKENS,
                        temperature: float = 1.0) -> str:
        system_prompt = self._build_system_prompt(system_context)
        # Call Anthropic API...
```

### 2. Configuration Centralization

All paths, API keys, and brand constants are defined in `config/config.py`:

```python
# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
BRAND_DIR = BASE_DIR / "claude-code-os-implementation"

# Brand knowledge paths
BRAND_VOICE_PATH = BRAND_DIR / "04-content-team" / "brand-voice-guide.md"
BRAND_STRATEGY_PATH = BRAND_DIR / "03-ai-growth-engine" / "positioning" / "brand-strategy.md"

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 4096

# Brand identity constants
BRAND_NAME = "Infinity Vault"
BRAND_TAGLINE = "Show Up Battle Ready"
```

**Benefits**:
- Single source of truth for configuration
- Easy environment-specific overrides
- Type-safe path construction
- Clear dependency on external brand knowledge

### 3. Dependency Injection via Composition

Agents receive their configuration through composition rather than hardcoded values:

```python
class BlogAgent(BaseAgent):
    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__("blog_agent", model)
        # Inherits brand_context, client, and all base methods
```

### 4. Separation of Concerns

Each specialized agent focuses on a single domain:

- **BlogAgent**: SEO-optimized long-form content
- **SocialAgent**: Platform-specific social media content
- **AmazonAgent**: E-commerce listing optimization
- **CompetitorAgent**: Market analysis and insights

## Data Flow

```
┌─────────────────────┐
│ Brand Knowledge     │
│ (markdown files)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ config.py           │
│ (paths + constants) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ BaseAgent           │
│ (loads context)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Specialized Agent   │
│ (adds prompts)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Anthropic API       │
│ (Claude models)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Generated Content   │
│ (markdown + meta)   │
└─────────────────────┘
```

## Error Handling Strategy

### Current Implementation

Basic exception handling with re-raise:

```python
try:
    message = self.client.messages.create(...)
    return message.content[0].text
except Exception as e:
    print(f"Error generating content: {e}")
    raise
```

### Future Improvements (Phase 4)

1. **Custom Exception Classes**:
   - `AgentError`: Base exception for all agent errors
   - `APIError`: API communication failures
   - `ConfigurationError`: Missing/invalid configuration
   - `ContentGenerationError`: Generation-specific issues

2. **Structured Logging**:
   - Centralized logging configuration
   - Separate log files per service
   - Request/response logging for debugging
   - Performance metrics tracking

3. **Retry Logic**:
   - Exponential backoff for API calls
   - Circuit breaker pattern for external dependencies
   - Graceful degradation when services unavailable

## Testing Strategy

### Test Structure (Future: Phase 3)

```
ai-content-agents/tests/
├── conftest.py                 # Shared fixtures
├── fixtures/
│   └── mock_responses.py       # Mock API responses
├── test_base_agent.py          # BaseAgent tests
├── test_blog_agent.py          # BlogAgent tests
├── test_social_agent.py        # SocialAgent tests
├── test_amazon_agent.py        # AmazonAgent tests
├── test_competitor_agent.py    # CompetitorAgent tests
├── test_api.py                 # API integration tests (future)
└── test_e2e.py                 # End-to-end tests (future)
```

### Coverage Requirements

- **Minimum Coverage**: 70%
- **Unit Tests**: All agent methods
- **Integration Tests**: API endpoints
- **E2E Tests**: Full content generation workflows

### Testing Patterns

1. **Mock Anthropic API**: Use pytest fixtures to avoid real API calls
2. **Brand Context Fixtures**: Pre-loaded brand files for consistent testing
3. **Snapshot Testing**: Verify generated content structure
4. **Property-Based Testing**: Validate output constraints (word count, format)

## Database Design (Future: Phase 2)

### Schema Overview

**content_history**
- Stores all generated content with metadata
- Enables historical analysis and versioning
- Links to agent type and generation parameters

**api_usage**
- Tracks API calls and token consumption
- Monitors rate limits and costs
- Identifies usage patterns

**performance_metrics**
- Records generation time and success rates
- Tracks error patterns
- Supports performance optimization

See `docs/DATABASE_SCHEMA.md` for detailed schema definitions.

## API Design (Future: Phase 5)

### REST Endpoints

```
POST   /api/content/generate      # Generate content (any type)
POST   /api/blog/generate          # Blog-specific generation
POST   /api/social/generate        # Social-specific generation
POST   /api/amazon/generate        # Amazon-specific generation
POST   /api/competitor/analyze     # Competitor analysis
GET    /api/content/history        # Retrieve content history
GET    /api/metrics                # Usage metrics
```

See `docs/API_DESIGN.md` for detailed endpoint specifications.

## Deployment Architecture (Future)

```
┌─────────────────────┐
│ FastAPI App         │
│ (uvicorn)           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AI Content Agents   │
│ (Python services)   │
└──────────┬──────────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
┌──────────────┐  ┌──────────────┐
│ Database     │  │ Anthropic    │
│ (SQLite/PG)  │  │ API          │
└──────────────┘  └──────────────┘
```

## Development Workflow

1. **Local Development**: Direct Python script execution
2. **Testing**: pytest with coverage reporting
3. **API Development**: FastAPI with hot reload
4. **CI/CD**: GitHub Actions for automated testing
5. **Deployment**: Docker containers (future)

## Security Considerations

1. **API Key Management**: Environment variables only, never committed
2. **Input Validation**: Pydantic models for API requests
3. **Rate Limiting**: Prevent API abuse and cost overruns
4. **Error Sanitization**: No sensitive data in error messages
5. **Audit Logging**: Track all content generation requests

## Performance Considerations

1. **Brand Context Caching**: Load once per agent initialization
2. **Connection Pooling**: Reuse HTTP connections to Anthropic API
3. **Async Operations**: Use async/await for concurrent requests (future)
4. **Response Streaming**: Stream large content responses (future)
5. **Database Indexing**: Optimize query performance (future)

## Extensibility

### Adding New Agents

1. Create new file in `agents/` directory
2. Inherit from `BaseAgent`
3. Override `_build_system_prompt()` for specialized context
4. Implement domain-specific methods
5. Add tests in `tests/test_<agent_name>.py`

Example:
```python
from agents.base_agent import BaseAgent

class EmailAgent(BaseAgent):
    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__("email_agent", model)

    def _build_system_prompt(self, additional_context: str = "") -> str:
        base_prompt = super()._build_system_prompt()
        email_context = """
        You are an expert email marketer specializing in e-commerce.
        Create engaging subject lines and persuasive email copy.
        """
        return f"{base_prompt}\n\n{email_context}\n\n{additional_context}"
```

### Adding New Content Types

1. Add method to existing agent class
2. Create specialized prompt templates
3. Define output format and validation
4. Add tests for new content type

## References

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- FastAPI Documentation (future)
- SQLAlchemy Documentation (future)

## Version History

- **v0.1.0** - Initial architecture with BaseAgent and 4 specialized agents
- **v0.2.0** - Planned: Database integration and persistence
- **v0.3.0** - Planned: REST API layer with FastAPI
- **v0.4.0** - Planned: Testing infrastructure and CI/CD
