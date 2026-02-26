# Testing Guide

## Overview

This document defines the testing strategy, coverage requirements, and best practices for the AI Content Agents system. Comprehensive testing ensures reliability, prevents regressions, and builds user trust—a key competitive advantage over platforms like GoHighLevel that suffer from "constant glitches."

## Testing Philosophy

The testing approach follows these core principles:

1. **Test Coverage Requirement**: Minimum 70% code coverage for all Python modules
2. **Test First, Fix Later**: Write tests before implementing new features when possible
3. **Isolated Testing**: Tests should be independent and not rely on external services
4. **Fast Feedback**: Unit tests should run in seconds, not minutes
5. **Real-World Scenarios**: Integration tests should mirror actual usage patterns

## Test Coverage Requirements

### Minimum Coverage: 70%

All code changes must maintain or improve test coverage above the **70% threshold**. This requirement applies to:

- Agent modules (`ai-content-agents/agents/`)
- Configuration modules (`ai-content-agents/config/`)
- API endpoints (`ai-content-agents/api/`)
- Database models (`ai-content-agents/database/`)
- Utility functions

### Coverage Measurement

Run coverage reports using pytest-cov:

```bash
# Generate coverage report
pytest --cov=ai-content-agents --cov-report=term-missing

# Fail if coverage is below 70%
pytest --cov=ai-content-agents --cov-report=term-missing --cov-fail-under=70

# Generate HTML report for detailed analysis
pytest --cov=ai-content-agents --cov-report=html
open htmlcov/index.html
```

### Coverage Exemptions

The following may be excluded from coverage requirements:
- Configuration files that only contain constants
- Migration scripts (manually tested)
- CLI entry points (covered by integration tests)
- Deprecated code scheduled for removal

## Test Structure

### Directory Organization

```
ai-content-agents/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── mock_responses.py       # Mock API responses
│   ├── test_base_agent.py          # BaseAgent tests
│   ├── test_blog_agent.py          # BlogAgent tests
│   ├── test_social_agent.py        # SocialAgent tests
│   ├── test_amazon_agent.py        # AmazonAgent tests
│   ├── test_competitor_agent.py    # CompetitorAgent tests
│   ├── test_api.py                 # API integration tests
│   ├── test_api_blog.py            # Blog API endpoint tests
│   ├── test_api_social.py          # Social API endpoint tests
│   └── test_e2e.py                 # End-to-end workflow tests
└── pytest.ini                       # Pytest configuration
```

## Testing Patterns

### 1. Unit Testing Agents

**Pattern**: Test agent initialization, method behavior, and error handling independently.

**Example** (from `test_base_agent.py`):

```python
import pytest
from unittest.mock import Mock, patch
from agents.base_agent import BaseAgent


class TestBaseAgent:
    """Test suite for BaseAgent class"""

    @pytest.fixture
    def mock_client(self):
        """Mock Anthropic API client"""
        mock = Mock()
        mock.messages.create.return_value = Mock(
            content=[Mock(text="Generated content")]
        )
        return mock

    @pytest.fixture
    def base_agent(self, mock_client):
        """Create BaseAgent with mocked client"""
        with patch('agents.base_agent.anthropic.Anthropic', return_value=mock_client):
            agent = BaseAgent(agent_name="TestAgent")
            return agent

    def test_initialization(self, base_agent):
        """Test agent initializes correctly"""
        assert base_agent.agent_name == "TestAgent"
        assert base_agent.model == "claude-sonnet-4-5-20250929"
        assert base_agent.brand_context is not None

    def test_generate_content_success(self, base_agent, mock_client):
        """Test successful content generation"""
        result = base_agent.generate_content("Test prompt")

        assert result == "Generated content"
        mock_client.messages.create.assert_called_once()

    def test_generate_content_api_error(self, base_agent, mock_client):
        """Test handling of API errors"""
        mock_client.messages.create.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            base_agent.generate_content("Test prompt")

        assert "API Error" in str(exc_info.value)
```

**Key Patterns**:
- Use `pytest.fixture` for reusable test objects
- Mock external dependencies (Anthropic API)
- Test both success and error paths
- Use descriptive test names that explain what is being tested

### 2. Testing with Fixtures

**Pattern**: Create reusable fixtures in `conftest.py` for common test data.

**Example** (`conftest.py`):

```python
import pytest
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def mock_anthropic_client():
    """
    Mock Anthropic API client that returns realistic responses.
    Used across all agent tests to avoid real API calls.
    """
    mock = Mock()
    mock.messages.create.return_value = Mock(
        content=[Mock(text="Generated blog content about test topic")]
    )
    return mock


@pytest.fixture
def sample_blog_topic():
    """Sample blog topic for testing"""
    return {
        "topic": "Essential Gear for Tactical Readiness",
        "pillar": "Battle-Ready Lifestyle",
        "keywords": ["tactical gear", "EDC", "preparedness"]
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test output files"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_brand_context():
    """Mock brand context files"""
    return {
        "brand_voice": "Direct, knowledgeable, empowering",
        "brand_strategy": "Position as authority in tactical lifestyle",
        "target_market": "Men 25-45 interested in preparedness"
    }
```

**Fixture Scopes**:
- `function` (default): Created/destroyed for each test
- `class`: Shared across test class
- `module`: Shared across test file
- `session`: Shared across entire test run

**Example with scope**:

```python
@pytest.fixture(scope="session")
def database_connection():
    """Database connection shared across all tests"""
    conn = create_test_database()
    yield conn
    conn.close()
```

### 3. Mocking External Services

**Pattern**: Mock Anthropic API calls to avoid real API usage during tests.

**Example** (`fixtures/mock_responses.py`):

```python
class MockAnthropicResponses:
    """Collection of realistic mock responses from Anthropic API"""

    @staticmethod
    def blog_post_response():
        return Mock(
            content=[Mock(text="""
# Essential Gear for Tactical Readiness

When it comes to tactical preparedness, having the right gear isn't just about having the latest equipment—it's about being ready for anything...

## Core EDC Essentials

1. Multi-tool
2. Flashlight
3. First aid kit
            """)]
        )

    @staticmethod
    def social_post_response():
        return Mock(
            content=[Mock(text="Your EDC kit is your first line of defense. What's in yours? 🎯 #TacticalReady #EDC")]
        )

    @staticmethod
    def api_error_response():
        from anthropic import APIError
        raise APIError("Rate limit exceeded")


@pytest.fixture
def mock_responses():
    """Provide access to mock response library"""
    return MockAnthropicResponses()
```

**Usage in tests**:

```python
def test_generate_blog_post(blog_agent, mock_client, mock_responses):
    """Test blog post generation with realistic response"""
    mock_client.messages.create.return_value = mock_responses.blog_post_response()

    result = blog_agent.generate_post("Essential Gear", "Battle-Ready Lifestyle")

    assert "Essential Gear" in result
    assert "EDC" in result
```

### 4. Testing Configuration

**Pattern**: Test configuration loading, validation, and error handling.

**Example**:

```python
import pytest
from config.config import (
    BRAND_VOICE_PATH,
    BRAND_STRATEGY_PATH,
    ANTHROPIC_API_KEY
)


def test_brand_files_exist():
    """Test that required brand context files exist"""
    assert BRAND_VOICE_PATH.exists(), f"Missing: {BRAND_VOICE_PATH}"
    assert BRAND_STRATEGY_PATH.exists(), f"Missing: {BRAND_STRATEGY_PATH}"


def test_api_key_configured():
    """Test that API key is set"""
    assert ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY not configured"
    assert ANTHROPIC_API_KEY != "your-api-key-here", "API key is placeholder"


def test_output_directories_created():
    """Test that output directories are created on import"""
    from config.config import BLOG_OUTPUT_DIR
    assert BLOG_OUTPUT_DIR.exists(), "Blog output directory not created"
```

### 5. Integration Testing API Endpoints

**Pattern**: Test API endpoints with FastAPI's TestClient.

**Example** (`test_api_blog.py`):

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_blog_agent(monkeypatch):
    """Mock BlogAgent to avoid real API calls"""
    class MockBlogAgent:
        def generate_post(self, topic, pillar):
            return f"Generated blog post about {topic}"

    monkeypatch.setattr("api.routes.blog.BlogAgent", MockBlogAgent)


def test_generate_blog_post_success(client, mock_blog_agent):
    """Test successful blog post generation via API"""
    response = client.post(
        "/api/blog/generate",
        json={
            "topic": "Tactical Gear Essentials",
            "pillar": "Battle-Ready Lifestyle",
            "type": "post"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Tactical Gear Essentials" in data["content"]


def test_generate_blog_post_missing_fields(client):
    """Test API validation with missing required fields"""
    response = client.post(
        "/api/blog/generate",
        json={"topic": "Test"}  # Missing 'pillar'
    )

    assert response.status_code == 422  # Validation error
    assert "pillar" in response.text.lower()


def test_generate_blog_post_invalid_type(client):
    """Test API validation with invalid post type"""
    response = client.post(
        "/api/blog/generate",
        json={
            "topic": "Test",
            "pillar": "Battle-Ready Lifestyle",
            "type": "invalid_type"
        }
    )

    assert response.status_code == 422
```

### 6. End-to-End Testing

**Pattern**: Test complete workflows from API request to database logging.

**Example** (`test_e2e.py`):

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.models import ContentHistory
from database.connection import get_db


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Test database with rollback"""
    db = next(get_db())
    yield db
    db.rollback()


def test_full_content_generation_workflow(client, test_db, mock_blog_agent):
    """
    Test end-to-end workflow:
    1. API receives request
    2. Agent generates content
    3. Content is saved to database
    4. Logs are created
    5. Response is returned
    """
    # Step 1: Send API request
    response = client.post(
        "/api/blog/generate",
        json={
            "topic": "E2E Test Topic",
            "pillar": "Battle-Ready Lifestyle",
            "type": "post"
        }
    )

    # Step 2: Verify successful response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    content_id = data["content_id"]

    # Step 3: Verify database record created
    content_record = test_db.query(ContentHistory).filter_by(id=content_id).first()
    assert content_record is not None
    assert content_record.content_type == "blog_post"
    assert content_record.topic == "E2E Test Topic"

    # Step 4: Verify content is stored
    assert len(content_record.content) > 0

    # Step 5: Verify metadata
    assert content_record.created_at is not None
    assert content_record.agent_name == "BlogAgent"
```

## Test Execution

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest ai-content-agents/tests/test_blog_agent.py

# Run specific test
pytest ai-content-agents/tests/test_blog_agent.py::TestBlogAgent::test_generate_post

# Run tests matching pattern
pytest -k "test_generate"

# Run tests in parallel (faster)
pytest -n auto
```

### Running Tests with Coverage

```bash
# Basic coverage report
pytest --cov=ai-content-agents

# Coverage with missing lines
pytest --cov=ai-content-agents --cov-report=term-missing

# Fail if coverage below 70%
pytest --cov=ai-content-agents --cov-fail-under=70

# Generate HTML coverage report
pytest --cov=ai-content-agents --cov-report=html
```

### Test Selection

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only tests that don't require API
pytest -m "not requires_api"

# Skip slow tests
pytest -m "not slow"
```

Mark tests using pytest markers in `pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests that run quickly
    integration: Integration tests requiring services
    e2e: End-to-end tests
    slow: Tests that take more than 1 second
    requires_api: Tests that need real API access
```

## Setup Verification Script

The `test_setup.py` script verifies system configuration before running tests. It checks:

1. **Import Verification**: All modules can be imported
2. **API Key Configuration**: Valid Anthropic API key is set
3. **Brand Files**: Required brand context files exist
4. **Output Directories**: All output directories are created
5. **Agent Initialization**: Agents can be instantiated

**Running setup verification**:

```bash
cd ai-content-agents
python test_setup.py
```

**Expected output**:

```
============================================================
AI CONTENT AGENTS - SETUP TEST
============================================================
Testing imports...
✅ All agent modules imported successfully

Testing API key...
✅ API key found (starts with: sk-ant-api...)

Testing brand context files...
✅ Brand Voice Guide: Found
✅ Brand Strategy: Found
✅ Content Strategy: Found
✅ Value Proposition: Found
✅ Target Market: Found
✅ All brand context files found

Testing output directories...
✅ Blog output directory exists
✅ Social output directory exists
✅ Amazon output directory exists
✅ Competitor output directory exists

Testing agent initialization...
✅ BlogAgent initialized
✅ SocialAgent initialized
✅ AmazonAgent initialized
✅ CompetitorAgent initialized
✅ All agents initialized successfully

============================================================
TEST SUMMARY
============================================================
✅ PASS: Imports
✅ PASS: API Key
✅ PASS: Brand Files
✅ PASS: Output Dirs
✅ PASS: Agent Init

5/5 tests passed

🎉 All tests passed! System is ready to generate content.
```

## Best Practices

### DO ✅

1. **Write descriptive test names**: `test_generate_content_with_valid_topic()`
2. **Test one thing per test**: Keep tests focused and simple
3. **Use fixtures for setup**: Avoid code duplication
4. **Mock external dependencies**: Don't call real APIs in tests
5. **Test error paths**: Verify error handling works correctly
6. **Use assertions liberally**: Multiple assertions are okay if testing same concept
7. **Keep tests fast**: Unit tests should run in milliseconds
8. **Use parameterized tests**: Test multiple inputs with `@pytest.mark.parametrize`

**Example of parameterized test**:

```python
@pytest.mark.parametrize("topic,pillar,expected_length", [
    ("Short Topic", "Battle-Ready Lifestyle", 500),
    ("Medium Length Topic Name", "Battle-Ready Lifestyle", 1500),
    ("Very Long Topic Name That Goes On", "Battle-Ready Lifestyle", 3000),
])
def test_content_length_varies_by_topic(blog_agent, topic, pillar, expected_length):
    """Test that content length varies appropriately"""
    result = blog_agent.generate_post(topic, pillar)
    assert abs(len(result) - expected_length) < 500  # Within 500 chars
```

### DON'T ❌

1. **Don't test implementation details**: Test behavior, not internals
2. **Don't write dependent tests**: Each test should run independently
3. **Don't use real API keys in tests**: Always mock external services
4. **Don't ignore failing tests**: Fix them immediately or mark as `xfail`
5. **Don't write slow tests without marking them**: Use `@pytest.mark.slow`
6. **Don't commit commented-out tests**: Remove or fix them
7. **Don't test third-party code**: Trust that libraries work

## Continuous Integration

Tests run automatically on every commit via GitHub Actions:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=ai-content-agents --cov-fail-under=70
```

### Coverage Badge

Add coverage badge to README:

```markdown
![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)
```

## Debugging Failed Tests

### Common Issues

**Issue**: Test fails with "ANTHROPIC_API_KEY not found"
**Solution**: Mock the client or set test API key in `.env.test`

**Issue**: Test fails intermittently
**Solution**: Test may have race condition or depend on execution order

**Issue**: Coverage report shows uncovered lines
**Solution**: Add tests for error paths and edge cases

### Debug Mode

Run tests with detailed output:

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Show why tests were skipped
pytest -rs
```

## Testing Checklist

Before committing code, verify:

- [ ] All tests pass: `pytest`
- [ ] Coverage above 70%: `pytest --cov --cov-fail-under=70`
- [ ] No linting errors: `flake8 ai-content-agents/`
- [ ] Tests are fast: Unit tests under 100ms each
- [ ] Fixtures are reusable: No duplicate setup code
- [ ] Mocks are used: No real API calls
- [ ] Error paths tested: Both success and failure cases covered
- [ ] Documentation updated: Docstrings for test classes

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Anthropic API documentation](https://docs.anthropic.com/)

---

**Last Updated**: 2026-02-26
**Maintainer**: AI Content Agents Team
**Coverage Requirement**: 70% minimum
