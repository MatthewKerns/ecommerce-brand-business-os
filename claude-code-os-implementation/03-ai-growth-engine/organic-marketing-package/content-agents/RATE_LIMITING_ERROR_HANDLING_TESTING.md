# TikTok Shop Rate Limiting & Error Handling Testing

This document describes the comprehensive testing infrastructure for validating rate limiting and error handling in the TikTok Shop API integration.

## Overview

The rate limiting and error handling testing validates:

1. **Token Bucket Rate Limiter**: Ensures the rate limiter correctly throttles API requests
2. **API Client Integration**: Verifies the API client respects rate limits
3. **Error Classification**: Tests proper exception types for different error scenarios
4. **Retry Logic**: Validates automatic retry with exponential backoff for transient errors
5. **Error Recovery**: Tests the system's resilience to various failure modes

## Test Infrastructure

### Test Scripts

#### `test_rate_limiting_errors.py`
Comprehensive test suite covering:
- Rate limiter basic functionality (token acquisition, refill, reset)
- Rate limiter under load (30 rapid consecutive requests)
- API client rate limiting integration (15 real API calls)
- Authentication error handling (invalid/missing tokens)
- Validation error handling (invalid parameters)
- Not found error handling (invalid resource IDs)
- Retry logic simulation (server, network, rate limit errors)

#### `run_rate_limiting_tests.sh`
Shell script wrapper for executing the test suite with proper error handling and reporting.

## Test Scenarios

### 1. Rate Limiter Basic Functionality

**Purpose**: Validate the token bucket algorithm implementation

**Tests**:
- Initial bucket is full with configured capacity
- Tokens are consumed on `acquire()`
- Tokens refill at configured rate over time
- Non-blocking acquire works correctly
- Reset refills bucket to full capacity
- Thread-safe operations

**Expected Outcome**: All operations complete successfully without race conditions or timing issues.

### 2. Rate Limiter Under Load

**Purpose**: Validate throttling under rapid consecutive requests

**Configuration**:
- Rate: 10 requests/second
- Burst capacity: 20 tokens
- Test load: 30 rapid requests

**Expected Behavior**:
- First 20 requests use burst capacity (immediate)
- Next 10 requests throttled (wait for token refill)
- Total time: ~1-2 seconds
- Effective rate: ~10-15 req/s

**Key Validation**: No requests dropped, all complete successfully.

### 3. API Client Rate Limiting

**Purpose**: Verify rate limiting during real API calls

**Configuration**:
- 15 rapid consecutive `list_products()` calls
- Rate limiter: 10 req/s

**Expected Behavior**:
- Rate limiter throttles requests automatically
- No `TikTokShopRateLimitError` from API
- Effective rate stays at or below 10 req/s
- All API responses correct

**Key Validation**: Rate limiter prevents API rate limit errors.

### 4. Authentication Error Handling

**Tests**:
- Invalid access token → `TikTokShopAuthError`
- Missing access token → `TikTokShopAuthError`
- Expired access token → `TikTokShopAuthError`

**Expected Behavior**:
- Errors detected immediately
- No retry attempts (permanent failure)
- Clear error messages
- Response data captured for debugging

### 5. Validation Error Handling

**Tests**:
- Invalid parameters (e.g., `page_size=-1`)
- Invalid data types
- Missing required fields

**Expected Behavior**:
- Raises `TikTokShopValidationError`
- No retry attempts (permanent failure)
- Error message indicates which field failed

### 6. Not Found Error Handling

**Tests**:
- Invalid product ID
- Invalid order ID
- Deleted resources

**Expected Behavior**:
- Raises `TikTokShopNotFoundError`
- No retry attempts (permanent failure)
- Error includes resource ID

### 7. Server Error Retry Logic

**Tests**:
- 5xx HTTP status codes
- Internal server errors
- Service temporarily unavailable

**Expected Behavior**:
- Raises `TikTokShopServerError`
- Automatic retry with exponential backoff
- Max 2 retry attempts
- Backoff: 2s → 4s → 8s
- Error raised after max retries

### 8. Network Error Retry Logic

**Tests**:
- Connection timeout
- Connection refused
- DNS resolution failure

**Expected Behavior**:
- Raises `TikTokShopNetworkError`
- Automatic retry with exponential backoff
- Max 2 retry attempts
- Original exception preserved

### 9. Rate Limit Error Retry Logic

**Tests**:
- 429 HTTP status code
- API rate limit exceeded

**Expected Behavior**:
- Raises `TikTokShopRateLimitError`
- Automatic retry with exponential backoff
- Uses API `retry_after` if provided
- Falls back to exponential backoff
- Max 3 retry attempts

### 10. Non-Retryable Error Handling

**Tests**:
- Authentication errors
- Validation errors
- Not found errors

**Expected Behavior**:
- Errors fail immediately
- No retry attempts
- No wait time
- Error details preserved

## Running the Tests

### Prerequisites

1. **For Offline Tests** (rate limiter only):
   ```bash
   # No credentials needed
   cd ai-content-agents
   python test_rate_limiting_errors.py
   ```

2. **For Full Integration Tests**:
   ```bash
   # Configure credentials in .env
   TIKTOK_SHOP_APP_KEY=your-app-key
   TIKTOK_SHOP_APP_SECRET=your-app-secret
   TIKTOK_SHOP_ACCESS_TOKEN=your-access-token

   # Run tests
   cd ai-content-agents
   python test_rate_limiting_errors.py
   ```

### Using the Shell Script

```bash
cd ai-content-agents
./run_rate_limiting_tests.sh
```

The script:
- Checks for `.env` file
- Runs all test scenarios
- Displays formatted results
- Exits with appropriate status code

## Test Output

### Console Output

The test script provides formatted output with:
- ✓ Success indicators (green)
- ✗ Error indicators (red)
- ℹ Information messages (blue)
- ⚠ Warning messages (yellow)

### Test Report File

Results are saved to `test_rate_limiting_errors_report.json`:

```json
{
  "timestamp": "2025-02-26 12:00:00",
  "total_tests": 8,
  "passed_tests": 8,
  "failed_tests": 0,
  "results": {
    "Rate Limiter Basic": "PASS",
    "Rate Limiter Load": "PASS",
    "API Client Rate Limiting": "PASS",
    "Auth Error Handling": "PASS",
    "Validation Error Handling": "PASS",
    "Not Found Error Handling": "PASS",
    "Retry Logic Simulation": "PASS"
  }
}
```

## Implementation Details

### Rate Limiter Configuration

From `client.py`:
```python
DEFAULT_RATE_LIMIT = 10.0  # requests per second
DEFAULT_BURST_CAPACITY = 20  # allow burst requests
```

### Retry Configuration

From `client.py`:
```python
MAX_RETRY_ATTEMPTS = 3  # for rate limit errors
MAX_SERVER_ERROR_RETRIES = 2
MAX_NETWORK_ERROR_RETRIES = 2
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 32.0
```

### Error Classification

| Error Type | Retryable | Max Retries | Backoff Strategy |
|------------|-----------|-------------|------------------|
| Rate Limit | Yes | 3 | API retry_after or exponential |
| Server Error | Yes | 2 | Exponential |
| Network Error | Yes | 2 | Exponential |
| Auth Error | No | 0 | Immediate fail |
| Validation Error | No | 0 | Immediate fail |
| Not Found Error | No | 0 | Immediate fail |

### Exponential Backoff Formula

```python
wait_time = min(INITIAL_BACKOFF_SECONDS * (2 ** retry_count), MAX_BACKOFF_SECONDS)
```

Example progression:
- Retry 0: 2.0s (1.0 * 2^0)
- Retry 1: 4.0s (1.0 * 2^1)
- Retry 2: 8.0s (1.0 * 2^2)
- Retry 3: 16.0s (1.0 * 2^3)
- Retry 4: 32.0s (capped at MAX_BACKOFF_SECONDS)

## Expected Performance

| Operation | Expected Time |
|-----------|---------------|
| Rate limiter basic (5 tokens) | < 1 second |
| Rate limiter load (30 requests @ 10/s) | 1-2 seconds |
| API client rate limiting (15 requests) | 1.5-2 seconds |
| Auth error (immediate fail) | < 0.5 seconds |
| Validation error (immediate fail) | < 0.5 seconds |
| Not found error (immediate fail) | < 0.5 seconds |
| Server error retry (2 retries) | ~6 seconds total |
| Network error retry (2 retries) | ~6 seconds total |
| Rate limit retry (3 retries) | ~14 seconds total |

## Troubleshooting

### Tests Skip API Integration

**Symptom**: Message "Skipping API integration tests (credentials not configured)"

**Solution**: Configure credentials in `.env` file:
```bash
cp .env.example .env
# Edit .env and add your credentials
```

### Rate Limiter Tests Fail

**Possible Causes**:
- System clock issues (affects timing)
- High CPU load (affects sleep precision)
- Thread contention

**Solution**: Run tests on a system with stable clock and low load.

### API Tests Return Errors

**Possible Causes**:
- Invalid credentials
- Expired access token
- Network connectivity issues
- TikTok Shop API downtime

**Solution**:
1. Verify credentials are correct
2. Refresh access token using `test_oauth_flow.py`
3. Check network connectivity
4. Check TikTok Shop API status

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Test Rate Limiting

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd ai-content-agents
          pip install -r requirements.txt
      - name: Run offline tests
        run: |
          cd ai-content-agents
          python test_rate_limiting_errors.py
```

### With Secrets (Full Integration)

```yaml
      - name: Configure credentials
        env:
          TIKTOK_SHOP_APP_KEY: ${{ secrets.TIKTOK_SHOP_APP_KEY }}
          TIKTOK_SHOP_APP_SECRET: ${{ secrets.TIKTOK_SHOP_APP_SECRET }}
          TIKTOK_SHOP_ACCESS_TOKEN: ${{ secrets.TIKTOK_SHOP_ACCESS_TOKEN }}
        run: |
          cd ai-content-agents
          echo "TIKTOK_SHOP_APP_KEY=$TIKTOK_SHOP_APP_KEY" > .env
          echo "TIKTOK_SHOP_APP_SECRET=$TIKTOK_SHOP_APP_SECRET" >> .env
          echo "TIKTOK_SHOP_ACCESS_TOKEN=$TIKTOK_SHOP_ACCESS_TOKEN" >> .env
      - name: Run full integration tests
        run: |
          cd ai-content-agents
          ./run_rate_limiting_tests.sh
```

## Best Practices

### When to Run These Tests

1. **Before Deployment**: Always run full test suite
2. **After Code Changes**: Run affected test scenarios
3. **CI/CD Pipeline**: Run offline tests on every commit
4. **Scheduled**: Run full integration tests daily with real credentials

### Interpreting Results

- **All Pass**: System is working correctly
- **Rate Limiter Fails**: Check token bucket implementation
- **API Tests Fail**: Check credentials, network, API status
- **Retry Logic Fails**: Verify backoff calculations and max retries

### Maintenance

1. **Update Rate Limits**: If TikTok changes API limits, update `DEFAULT_RATE_LIMIT`
2. **Adjust Retry Logic**: Tune retry attempts and backoff based on API behavior
3. **Monitor API Changes**: Watch for new error codes or response formats
4. **Update Tests**: Add new test cases for newly discovered edge cases

## Related Documentation

- [VALIDATION.md](./VALIDATION.md) - Complete validation checklist
- [integrations/tiktok_shop/README.md](./integrations/tiktok_shop/README.md) - TikTok Shop integration docs
- [integrations/tiktok_shop/rate_limiter.py](./integrations/tiktok_shop/rate_limiter.py) - Rate limiter implementation
- [integrations/tiktok_shop/client.py](./integrations/tiktok_shop/client.py) - API client implementation
- [integrations/tiktok_shop/exceptions.py](./integrations/tiktok_shop/exceptions.py) - Custom exceptions

## Support

For issues or questions:
1. Check error messages in test output
2. Review VALIDATION.md for expected behavior
3. Consult TikTok Shop API documentation
4. Check implementation code for configuration values
