# TikTok Shop Integration - Testing Instructions

This guide provides step-by-step instructions for testing the TikTok Shop API integration.

## Prerequisites

Before you begin testing, ensure you have:

1. ✅ **TikTok Shop Seller Account** (approved)
2. ✅ **TikTok Shop API Application** (approved with required scopes)
3. ✅ **Products in Your Shop** (for testing product sync)
4. ✅ **Python 3.8+** installed
5. ✅ **Required dependencies** installed

## Setup

### 1. Install Dependencies

```bash
cd ai-content-agents
pip install -r requirements.txt  # If requirements file exists
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your TikTok Shop credentials:

```bash
# Required credentials
TIKTOK_SHOP_APP_KEY=your-actual-app-key
TIKTOK_SHOP_APP_SECRET=your-actual-app-secret

# Access token (will be obtained through OAuth flow)
# TIKTOK_SHOP_ACCESS_TOKEN=to-be-filled-after-oauth
```

## Testing Workflow

Follow these tests in order, as each step builds on the previous one.

### Step 1: OAuth Flow Testing

**Purpose**: Obtain access token for API authentication

**Test Script**: `test_oauth_flow.py`

**Run**:
```bash
cd ai-content-agents
python test_oauth_flow.py
```

**What it tests**:
- ✓ Credential validation
- ✓ OAuth handler initialization
- ✓ Authorization URL generation
- ✓ Authorization code exchange
- ✓ Access token retrieval
- ✓ Token refresh mechanism
- ✓ Signature generation

**Expected Output**:
- Authorization URL to visit in browser
- Instructions for obtaining authorization code
- Access token and refresh token
- Instructions to add tokens to `.env` file

**Action Required**:
1. Copy the generated authorization URL
2. Open it in your browser
3. Log in with your TikTok Shop seller account
4. Authorize the application
5. Copy the authorization code from the redirect URL
6. Paste it into the test script when prompted
7. **Important**: Copy the access token to your `.env` file

**Update `.env`**:
```bash
TIKTOK_SHOP_ACCESS_TOKEN=your-actual-access-token-from-oauth
```

**Document Results**: Update `VALIDATION.md` Phase 1 section

---

### Step 2: Product Sync Testing

**Purpose**: Validate product listing, filtering, and synchronization

**Test Script**: `test_product_sync.py`

**Prerequisites**:
- ✅ OAuth flow completed (Step 1)
- ✅ Access token added to `.env` file
- ✅ At least one product in your TikTok Shop

**Run**:
```bash
cd ai-content-agents
python test_product_sync.py
```

**What it tests**:
- ✓ Credential and token validation
- ✓ TikTokShopAgent initialization
- ✓ Product listing (basic)
- ✓ Product data structure validation
- ✓ Pagination functionality
- ✓ Status filtering (ACTIVE, INACTIVE, DRAFT)
- ✓ Product details retrieval
- ✓ Full product sync with automatic pagination
- ✓ Rate limiting during requests

**Expected Output**:
- List of products from your TikTok Shop
- Product data structure validation results
- Pagination test results
- Status filter test results
- Product details for specific product
- Full sync completion with product count
- JSON file saved to `output/tiktok/products/`

**Validation Points**:
1. **Product Data Structure**: Verify all required fields are present
   - `product_id`
   - `title`
   - `status`
   - Optional: `description`, `price`, `images`, `inventory`

2. **Pagination**: Verify pages contain different products

3. **Status Filters**: Verify returned products match requested status

4. **Output Files**: Check `output/tiktok/products/` for synced data

**Document Results**: Update `VALIDATION.md` Phase 2 section with:
- Total products synced
- Product data sample
- Performance metrics
- Any issues encountered

---

### Step 3: Order Retrieval Testing

**Purpose**: Validate order fetching and processing

**Status**: ⏳ To be implemented

**Prerequisites**:
- ✅ OAuth flow completed
- ✅ Access token in `.env`
- ✅ Orders in your TikTok Shop (for testing)

**Note**: This will be similar to product sync testing but for orders.

---

### Step 4: Analytics Testing

**Purpose**: Validate analytics and performance metrics retrieval

**Status**: ⏳ To be implemented

**Prerequisites**:
- ✅ OAuth flow completed
- ✅ Access token in `.env`
- ✅ Historical data in your shop

---

### Step 5: Rate Limiting & Error Handling

**Purpose**: Validate rate limiting prevents API errors and error handling works

**What to test**:
1. Make rapid consecutive API calls
2. Verify rate limiter throttles requests
3. Test with invalid credentials
4. Test with invalid product IDs
5. Verify error messages are clear

---

## Troubleshooting

### Common Issues

#### "TIKTOK_SHOP_ACCESS_TOKEN is not configured"
**Solution**: Complete OAuth flow (Step 1) and add access token to `.env` file

#### "Authentication error" during API calls
**Possible causes**:
- Access token expired (tokens typically expire after 24 hours)
- Invalid access token
- API app not approved

**Solution**: Run OAuth flow again to get new access token

#### "No products found in your TikTok Shop"
**Solution**: Add at least one product to your TikTok Shop before testing

#### "Rate limit error"
**Solution**: Rate limiter should prevent this. If you see this error:
- Check rate limiter configuration in `client.py`
- Verify `DEFAULT_RATE_LIMIT` is set correctly (10 requests/second)
- Wait a few moments and try again

#### Import errors
**Solution**:
```bash
# Make sure you're in the correct directory
cd ai-content-agents

# Check Python path
python -c "import sys; print(sys.path)"

# Try running from parent directory with module syntax
cd ..
python -m ai_content_agents.test_product_sync
```

---

## Test Output Locations

### Synced Product Data
- **Location**: `ai-content-agents/output/tiktok/products/`
- **Format**: JSON files with timestamp
- **Example**: `products_sync_all_20240226_143052.json`

### Test Logs
- **Location**: Console output
- **Recommendation**: Redirect to file for documentation
  ```bash
  python test_product_sync.py 2>&1 | tee test_results.log
  ```

### Validation Documentation
- **Location**: `ai-content-agents/VALIDATION.md`
- **Update**: After each test phase

---

## Success Criteria

### OAuth Flow (Step 1)
- ✅ Authorization URL generated
- ✅ Access token received
- ✅ Token added to `.env` file
- ✅ Signature generation works

### Product Sync (Step 2)
- ✅ Products retrieved from API
- ✅ Product data structure matches API docs
- ✅ Pagination works correctly
- ✅ Status filtering works
- ✅ Product details retrieval works
- ✅ Full sync completes without errors
- ✅ Data saved to JSON file
- ✅ No rate limit errors

---

## Next Steps After Testing

1. **Document Results**: Update `VALIDATION.md` with all test results
2. **Review Output**: Check synced data in `output/tiktok/products/`
3. **Mark Subtask Complete**: Update implementation_plan.json
4. **Commit Changes**: Commit test scripts and validation results
5. **Proceed**: Move to next testing phase (orders, analytics)

---

## Useful Commands

```bash
# Check Python version
python --version

# Verify imports work
cd ai-content-agents
python -c "from agents.tiktok_shop_agent import TikTokShopAgent; print('OK')"

# Check environment variables loaded
python -c "from config.config import TIKTOK_SHOP_APP_KEY; print(f'App Key: {TIKTOK_SHOP_APP_KEY[:10]}...')"

# View synced products
ls -lh output/tiktok/products/

# Pretty print JSON
cat output/tiktok/products/products_sync_*.json | python -m json.tool | less
```

---

## API Documentation References

- [TikTok Shop API Documentation](https://partner.tiktokshop.com/docv2/page/650faba97cc8b702f66e32d5)
- [OAuth 2.0 Guide](https://partner.tiktokshop.com/docv2/page/650fab997cc8b702f66e3177)
- [Shop API - Products](https://partner.tiktokshop.com/docv2/page/650fab6b7cc8b702f66e2ff7)
- [Integration README](./integrations/tiktok_shop/README.md)

---

## Support

If you encounter issues:

1. Check `VALIDATION.md` for known issues
2. Review API documentation links above
3. Check TikTok Shop Partner Portal for API app status
4. Verify credentials and token expiry
5. Review error messages - they should be descriptive

---

## Test Checklist

Use this checklist to track your testing progress:

- [ ] Step 1: OAuth Flow Testing
  - [ ] Test script runs successfully
  - [ ] Access token obtained
  - [ ] Token added to `.env`
  - [ ] Results documented in `VALIDATION.md`

- [ ] Step 2: Product Sync Testing
  - [ ] Test script runs successfully
  - [ ] Products retrieved
  - [ ] Data structure validated
  - [ ] Pagination works
  - [ ] Filters work
  - [ ] Sync completes
  - [ ] Output file created
  - [ ] Results documented in `VALIDATION.md`

- [ ] Step 3: Order Testing (future)
- [ ] Step 4: Analytics Testing (future)
- [ ] Step 5: Rate Limiting Testing (future)
- [ ] All results documented
- [ ] Subtask marked complete
- [ ] Changes committed
