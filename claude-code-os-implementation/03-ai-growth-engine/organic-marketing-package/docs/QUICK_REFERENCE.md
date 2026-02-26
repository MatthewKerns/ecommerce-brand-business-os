# Quick Reference Guide

## Overview

This is a quick reference for developers working on the E-Commerce Brand Business OS AI Content Agents. For detailed information, see the full documentation in `docs/`.

---

## Architecture Overview

### Monorepo Structure

```
ecommerce-brand-business-os/
├── ai-content-agents/         # Python service layer
│   ├── agents/                # Agent implementations
│   ├── config/                # Configuration & brand context
│   ├── database/              # Database models & schema
│   ├── api/                   # REST API endpoints
│   ├── tests/                 # Test suite
│   └── logs/                  # Application logs
└── claude-code-os-implementation/  # Knowledge layer
    ├── 03-ai-growth-engine/   # Business strategy
    ├── 04-content-team/       # Content & brand strategy
    └── [other departments]
```

### Agent Hierarchy

```python
BaseAgent (base_agent.py)
    ├── BlogAgent      # Blog posts, listicles, how-to guides
    ├── SocialAgent    # Instagram, Reddit, content calendars
    ├── AmazonAgent    # Product titles, bullets, descriptions
    └── CompetitorAgent # Competitor analysis, review mining
```

**Core Pattern**: All agents inherit from `BaseAgent` which provides:
- Brand context loading
- Anthropic API integration
- System prompt building
- Content generation & saving

See `docs/ARCHITECTURE.md` for full details.

---

## Quick Start

### Setup

```bash
# 1. Install dependencies
cd ai-content-agents
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY='your-key-here'

# 3. Verify setup
python test_setup.py

# 4. Try quick start examples
python quick_start.py
```

### Generate Content (CLI)

```bash
# Blog post
python generate_content.py blog post "Tournament Prep Tips"

# Social media
python generate_content.py social instagram "Pre-game ritual"

# Amazon listing
python generate_content.py amazon title "Premium Card Binder"

# Competitor analysis
python generate_content.py competitor analyze "Competitor ASIN"
```

---

## API Endpoints

### Base URL
`http://localhost:8000` (development)

### Start API Server

```bash
cd ai-content-agents
uvicorn api.main:app --reload
```

### Key Endpoints

#### Universal Content Generation
```http
POST /api/content/generate
Content-Type: application/json

{
  "content_type": "blog",
  "prompt": "Write about tactical backpacks",
  "parameters": {
    "pillar": "Battle-Ready Lifestyle",
    "max_tokens": 4096
  }
}
```

#### Blog Content
```http
POST /api/blog/generate

{
  "topic": "Tournament preparation tips",
  "pillar": "Battle-Ready Lifestyle",
  "content_format": "listicle",
  "target_word_count": 1500,
  "seo_keywords": ["tcg", "tournament", "prep"]
}
```

#### Social Media
```http
POST /api/social/generate

{
  "platform": "instagram",
  "topic": "Pre-game ritual",
  "content_pillar": "Battle-Ready Lifestyle",
  "include_hashtags": true
}
```

#### Amazon Listing
```http
POST /api/amazon/generate

{
  "content_type": "title",
  "product_name": "Premium Card Binder",
  "key_features": ["9-pocket", "scratch-resistant"],
  "target_keywords": ["trading card binder", "tcg storage"]
}
```

See `docs/API_DESIGN.md` for full API documentation.

---

## Testing Commands

### Run All Tests

```bash
# Basic test run
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=ai-content-agents --cov-report=term-missing

# Fail if coverage below 70%
pytest --cov=ai-content-agents --cov-fail-under=70

# Generate HTML coverage report
pytest --cov=ai-content-agents --cov-report=html
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Specific test file
pytest ai-content-agents/tests/test_blog_agent.py

# Specific test
pytest ai-content-agents/tests/test_blog_agent.py::TestBlogAgent::test_generate_post

# Tests matching pattern
pytest -k "test_generate"

# Run in parallel (faster)
pytest -n auto
```

### Test by Category

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Coverage Requirements

- **Minimum**: 70% code coverage
- **Scope**: All Python modules (agents, config, API, database)
- **Exemptions**: Config constants, migration scripts, CLI entry points

See `docs/TESTING_GUIDE.md` for full testing documentation.

---

## Logging Configuration

### Get Logger

```python
from logging_config import get_logger

# Basic logger
logger = get_logger('my_component')

# Custom log level
logger = get_logger('my_component', log_level='DEBUG')

# Custom log directory
from pathlib import Path
logger = get_logger('my_component', log_dir=Path('./custom_logs'))
```

### Logging Levels

| Level | Use Case | Example |
|-------|----------|---------|
| `DEBUG` | Detailed diagnostic info | Variable values, function entry/exit |
| `INFO` | General informational | "Agent initialized", "Content generated" |
| `WARNING` | Unexpected but recoverable | "Using default config", "Retrying request" |
| `ERROR` | Error events | "Content generation failed", "API error" |
| `CRITICAL` | Critical system errors | "Database connection lost", "Invalid API key" |

### Logging Patterns

```python
# Success logging
logger.info("Content generation started", extra={
    "agent": self.agent_name,
    "prompt_length": len(prompt)
})

# Error logging with stack trace
try:
    content = self.generate_content(prompt)
except ContentGenerationError as e:
    logger.error(
        f"Generation failed: {e.message}",
        extra={"error_code": e.error_code},
        exc_info=True  # Include stack trace
    )
    raise

# Warning logging
if not file_path.exists():
    logger.warning(
        f"File not found: {file_path}",
        extra={"expected_path": str(file_path)}
    )
```

### Log Files

- **Location**: `ai-content-agents/logs/`
- **Format**: `{agent_name}_YYYYMMDD.log`
- **Example**: `blog_agent_20250226.log`

See `docs/ERROR_HANDLING.md` for full error handling and logging standards.

---

## Common Patterns

### 1. Creating a New Agent

```python
from agents.base_agent import BaseAgent
from config.config import DEFAULT_MODEL
from logging_config import get_logger

class MyAgent(BaseAgent):
    """Custom agent for specific content type"""

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__("my_agent", model)
        self.logger = get_logger('my_agent')

    def generate_custom_content(self, topic: str, **kwargs) -> str:
        """Generate custom content"""
        system_context = f"""
        You are a content expert specializing in {topic}.
        Follow the brand voice and strategy from the loaded context.
        """

        prompt = f"Create content about: {topic}"

        self.logger.info(f"Generating content for topic: {topic}")

        content = self.generate_content(
            prompt=prompt,
            system_context=system_context
        )

        self.logger.info("Content generated successfully")
        return content
```

### 2. Configuration Access

```python
from config.config import (
    BRAND_NAME,
    BRAND_TAGLINE,
    CONTENT_PILLARS,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    ANTHROPIC_API_KEY
)

# Use in your code
print(f"Generating content for {BRAND_NAME}")
print(f"Content pillars: {', '.join(CONTENT_PILLARS)}")
```

### 3. Exception Handling

```python
from exceptions import (
    ContentGenerationError,
    AuthenticationError,
    ValidationError,
    RateLimitError
)

try:
    content = agent.generate_content(prompt)
except ValidationError as e:
    logger.error(f"Invalid input: {e.message}")
    # Handle validation error
except RateLimitError as e:
    retry_after = e.details.get('retry_after_seconds', 60)
    logger.warning(f"Rate limited, retry after {retry_after}s")
    # Implement retry logic
except ContentGenerationError as e:
    logger.error(f"Generation failed: {e.message}", exc_info=True)
    # Handle generation failure
except Exception as e:
    logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
    raise
```

### 4. Database Operations

```python
from database.connection import get_db
from database.models import ContentHistory

# Get database session
db = next(get_db())

try:
    # Create record
    content_record = ContentHistory(
        content_type="blog_post",
        topic="My Topic",
        content="Generated content...",
        agent_name="BlogAgent"
    )
    db.add(content_record)
    db.commit()

    # Query records
    recent_content = db.query(ContentHistory)\
        .filter(ContentHistory.content_type == "blog_post")\
        .order_by(ContentHistory.created_at.desc())\
        .limit(10)\
        .all()

finally:
    db.close()
```

### 5. Testing Pattern

```python
import pytest
from unittest.mock import Mock, patch

class TestMyAgent:
    """Test suite for MyAgent"""

    @pytest.fixture
    def mock_client(self):
        """Mock Anthropic API client"""
        mock = Mock()
        mock.messages.create.return_value = Mock(
            content=[Mock(text="Generated content")]
        )
        return mock

    @pytest.fixture
    def my_agent(self, mock_client):
        """Create agent with mocked client"""
        with patch('agents.base_agent.anthropic.Anthropic', return_value=mock_client):
            from agents.my_agent import MyAgent
            return MyAgent()

    def test_generate_content_success(self, my_agent):
        """Test successful content generation"""
        result = my_agent.generate_custom_content("test topic")
        assert result == "Generated content"
        assert len(result) > 0
```

---

## Configuration Files

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY='your-api-key-here'

# Optional (defaults shown)
export DEFAULT_MODEL='claude-sonnet-4-5-20250929'
export DEFAULT_MAX_TOKENS='4096'
```

### Brand Context Files

Located in `claude-code-os-implementation/`:

```
04-content-team/
├── brand-voice-guide.md      # Tone, style, vocabulary
└── content-strategy.md       # Content approach & pillars

03-ai-growth-engine/
├── positioning/
│   └── brand-strategy.md     # Market positioning
└── business-definition/
    ├── value-proposition.md  # Core value prop
    └── target-market.md      # Audience definition
```

---

## Key Constants

### Brand Identity

```python
BRAND_NAME = "Infinity Vault"
BRAND_TAGLINE = "Show Up Battle Ready"
BRAND_PROMISE = "Show up to every game feeling confident, prepared, and respected"
```

### Content Pillars

```python
CONTENT_PILLARS = [
    "Battle-Ready Lifestyle",
    "Gear & Equipment",
    "Community Champion",
    "Collector's Journey"
]
```

### Target Channels

```python
CHANNELS = {
    "amazon": "Primary revenue channel",
    "instagram": "Visual showcase",
    "reddit": "Community engagement",
    "discord": "Direct community",
    "youtube": "Brand awareness",
    "blog": "SEO and thought leadership"
}
```

---

## Database Schema

### ContentHistory Table

```sql
CREATE TABLE content_history (
    id INTEGER PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,  -- blog_post, social_post, etc.
    topic TEXT,
    content TEXT NOT NULL,
    agent_name VARCHAR(50),
    model VARCHAR(100),
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Query Examples

```python
# Get all blog posts
blog_posts = db.query(ContentHistory)\
    .filter(ContentHistory.content_type == "blog_post")\
    .all()

# Get content from last 7 days
from datetime import datetime, timedelta
week_ago = datetime.now() - timedelta(days=7)
recent = db.query(ContentHistory)\
    .filter(ContentHistory.created_at >= week_ago)\
    .all()

# Count by content type
from sqlalchemy import func
counts = db.query(
    ContentHistory.content_type,
    func.count(ContentHistory.id)
).group_by(ContentHistory.content_type).all()
```

See `docs/DATABASE_SCHEMA.md` for full schema documentation.

---

## Common Commands Cheat Sheet

```bash
# Setup
python test_setup.py                    # Verify system setup
python quick_start.py                   # Try examples

# Testing
pytest                                  # Run all tests
pytest -v --cov                         # Verbose with coverage
pytest -k "blog"                        # Test blog functionality
pytest --cov-fail-under=70              # Enforce coverage

# API
uvicorn api.main:app --reload           # Start dev server
uvicorn api.main:app --port 8080        # Custom port
curl http://localhost:8000/health       # Health check

# Logging
tail -f logs/blog_agent_*.log           # Watch blog agent logs
tail -f logs/api_*.log                  # Watch API logs
grep ERROR logs/*.log                   # Find errors in logs

# Database
python ai-content-agents/database/init_db.py  # Initialize database
sqlite3 ai-content-agents/content.db          # Open database CLI

# Linting (optional)
flake8 ai-content-agents/               # Check code style
black ai-content-agents/                # Format code
mypy ai-content-agents/                 # Type checking
```

---

## Troubleshooting

### Common Issues

**Issue**: `ANTHROPIC_API_KEY not found`
```bash
# Solution: Set environment variable
export ANTHROPIC_API_KEY='your-key-here'
# Or add to ~/.bashrc or ~/.zshrc for persistence
```

**Issue**: Import errors
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Tests failing
```bash
# Solution: Check test setup
python test_setup.py
# Run tests with verbose output to see details
pytest -v -s
```

**Issue**: Coverage below 70%
```bash
# Solution: Generate HTML report to see what's missing
pytest --cov=ai-content-agents --cov-report=html
open htmlcov/index.html
# Add tests for uncovered lines
```

**Issue**: API connection errors
```bash
# Solution: Verify API server is running
curl http://localhost:8000/health
# If not running:
uvicorn api.main:app --reload
```

---

## Resources

### Documentation
- [Architecture](./ARCHITECTURE.md) - System design & patterns
- [API Design](./API_DESIGN.md) - REST API specification
- [Testing Guide](./TESTING_GUIDE.md) - Testing standards & patterns
- [Error Handling](./ERROR_HANDLING.md) - Exception handling & logging
- [Database Schema](./DATABASE_SCHEMA.md) - Database structure

### External Links
- [Anthropic API Docs](https://docs.anthropic.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [pytest Docs](https://docs.pytest.org/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

**Last Updated**: 2026-02-26
**Maintained By**: AI Content Agents Team
**Questions?** See full documentation in `docs/` directory
