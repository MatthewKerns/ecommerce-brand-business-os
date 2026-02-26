# AI Content Agents - Test Suite

This directory contains the test suite for the AI Content Agents system, including unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py          # Shared pytest fixtures and configuration
├── test_e2e.py          # End-to-end workflow tests
└── README.md            # This file
```

## Running Tests

### Run All Tests

```bash
pytest ai-content-agents/tests/
```

### Run Specific Test File

```bash
pytest ai-content-agents/tests/test_e2e.py
```

### Run with Verbose Output

```bash
pytest ai-content-agents/tests/ -v
```

### Run with Coverage

```bash
pytest ai-content-agents/tests/ --cov=ai-content-agents --cov-report=html
```

### Run Only E2E Tests

```bash
pytest ai-content-agents/tests/ -m e2e
```

### Run Excluding Slow Tests

```bash
pytest ai-content-agents/tests/ -m "not slow"
```

## Test Categories

### End-to-End Tests (`test_e2e.py`)

Tests the complete workflow from API request through agent processing to database logging.

**Key Tests:**
- `test_blog_generation_workflow`: Tests full API → Agent → Database flow
- `test_error_handling_workflow`: Verifies error handling across all layers
- `test_concurrent_requests_workflow`: Tests concurrent request processing
- `test_request_response_time`: Validates performance requirements
- `test_health_endpoint`: Checks API health endpoint
- `test_api_status_endpoint`: Verifies system status reporting

## Prerequisites

### Required Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Environment Setup

The tests require the following to be running:
- API server (started automatically by test fixtures)
- Database (SQLite for tests, configured in conftest.py)

## Test Environment

Tests run in an isolated environment with:
- `ENVIRONMENT=test`
- `LOG_LEVEL=DEBUG`
- Separate test database (SQLite)
- Captured logging output

## Writing New Tests

### Example Test Structure

```python
import pytest

@pytest.mark.asyncio
class TestMyFeature:
    async def test_my_feature(self, http_client):
        """Test description."""
        response = await http_client.get("/api/endpoint")
        assert response.status_code == 200
```

### Using Fixtures

Common fixtures available:
- `http_client`: Async HTTP client for API requests
- `db_connection`: Database connection for verification
- `log_capture`: Captures log output for assertions
- `api_server`: Manages API server lifecycle

## Continuous Integration

These tests are run automatically in CI/CD pipeline on:
- Pull requests
- Pushes to main branch
- Scheduled runs (daily)

## Troubleshooting

### Server Won't Start

If tests fail with "API server failed to start":
1. Check if port 8000 is already in use
2. Verify API dependencies are installed
3. Check API logs for startup errors

### Database Errors

If database tests fail:
1. Ensure test database directory is writable
2. Check database schema migrations are current
3. Verify database client is installed

### Timeout Errors

If tests timeout:
1. Increase timeout values in test configuration
2. Check for blocking operations in agent code
3. Verify external service availability

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use fixtures for setup/teardown
3. **Assertions**: Use descriptive assertion messages
4. **Mocking**: Mock external services appropriately
5. **Performance**: Keep tests fast; mark slow tests with `@pytest.mark.slow`

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [httpx documentation](https://www.python-httpx.org/)
