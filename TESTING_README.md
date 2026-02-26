# TikTok Shop API Integration - Testing Guide

This directory contains comprehensive testing documentation and scripts for validating the TikTok Shop API integration.

## Quick Start

### Prerequisites
- TikTok Shop seller account (approved)
- TikTok Shop API app (approved with required scopes)
- Credentials configured in `.env` file

### Run Tests

```bash
# 1. Test OAuth flow
cd ai-content-agents
python test_oauth_flow.py

# 2. Follow prompts to complete OAuth authorization

# 3. Document results in VALIDATION.md
```

## Testing Documentation

### 📋 [VALIDATION.md](./VALIDATION.md)
Comprehensive validation checklist with 22 test cases covering:
- Prerequisites setup
- OAuth flow testing (6 tests)
- API client testing (4 tests)
- Rate limiting & error handling (4 tests)
- TikTokShopAgent testing (4 tests)
- Integration testing (2 tests)
- Security validation (2 tests)

**Use this document to:**
- Track testing progress
- Document test results
- Record any issues or blockers
- Provide sign-off approval

### 📖 [TIKTOK_SHOP_SETUP_GUIDE.md](./TIKTOK_SHOP_SETUP_GUIDE.md)
Step-by-step setup guide covering:
- Creating TikTok Shop seller account
- Creating TikTok Shop API app
- Configuring OAuth settings
- Obtaining API credentials
- Environment configuration
- Troubleshooting common issues

**Use this guide to:**
- Set up TikTok Shop seller account
- Create and configure API app
- Complete OAuth flow
- Troubleshoot setup issues

### 🧪 [test_oauth_flow.py](./ai-content-agents/test_oauth_flow.py)
Interactive test script for OAuth validation:
- Validates credentials configuration
- Initializes OAuth handler
- Generates authorization URL
- Exchanges authorization code for tokens
- Tests token refresh
- Tests signature generation

**Use this script to:**
- Validate OAuth implementation
- Test authentication flow end-to-end
- Troubleshoot OAuth issues
- Obtain access tokens for testing

## Testing Workflow

### Step 1: Setup (1-5 business days)
1. Read [TIKTOK_SHOP_SETUP_GUIDE.md](./TIKTOK_SHOP_SETUP_GUIDE.md)
2. Create TikTok Shop seller account
3. Create TikTok Shop API app
4. Wait for approvals
5. Configure `.env` file with credentials

### Step 2: OAuth Testing (15 minutes)
1. Run `python test_oauth_flow.py`
2. Follow interactive prompts
3. Complete OAuth authorization in browser
4. Obtain and save access tokens
5. Update `.env` with tokens
6. Document results in [VALIDATION.md](./VALIDATION.md) (Tests 1-6)

### Step 3: API Client Testing (30 minutes)
1. Test product sync functionality
2. Test order retrieval
3. Test analytics data fetching
4. Document results in [VALIDATION.md](./VALIDATION.md) (Tests 7-10)

### Step 4: Error Handling Testing (30 minutes)
1. Test rate limiting behavior
2. Test retry logic
3. Test error handling with invalid requests
4. Document results in [VALIDATION.md](./VALIDATION.md) (Tests 11-14)

### Step 5: Agent Testing (30 minutes)
1. Test TikTokShopAgent initialization
2. Test product sync via agent
3. Test order sync via agent
4. Test analytics via agent
5. Document results in [VALIDATION.md](./VALIDATION.md) (Tests 15-18)

### Step 6: Integration Testing (1 hour)
1. Run end-to-end workflow test
2. Test quick start examples
3. Document results in [VALIDATION.md](./VALIDATION.md) (Tests 19-20)

### Step 7: Security Validation (15 minutes)
1. Run secrets scanning
2. Test signature validation
3. Document results in [VALIDATION.md](./VALIDATION.md) (Tests 21-22)

### Step 8: Sign-off
1. Review all test results
2. Document any known issues or blockers
3. Provide recommendations
4. Complete sign-off section in [VALIDATION.md](./VALIDATION.md)

## Test Status Legend

- ✅ **Passed** - Test completed successfully with expected results
- ⏳ **Pending** - Test not yet started or awaiting prerequisites
- ❌ **Failed** - Test failed or had unexpected results
- ⚠️ **Blocked** - Test blocked by external dependency

## Directory Structure

```
.
├── TESTING_README.md                        # This file
├── VALIDATION.md                            # Validation checklist and results
├── TIKTOK_SHOP_SETUP_GUIDE.md              # Setup guide
└── ai-content-agents/
    ├── test_oauth_flow.py                   # OAuth test script
    ├── integrations/tiktok_shop/
    │   ├── oauth.py                         # OAuth implementation
    │   ├── client.py                        # API client
    │   ├── exceptions.py                    # Custom exceptions
    │   ├── rate_limiter.py                  # Rate limiting
    │   └── README.md                        # Integration docs
    └── agents/
        └── tiktok_shop_agent.py             # High-level agent
```

## Common Issues

### OAuth Flow Issues

**Problem:** "Invalid app_key" error
- **Solution:** Verify App Key in `.env` matches Partner Portal exactly

**Problem:** "Authorization code expired"
- **Solution:** Code expires in ~10 minutes, request a new one

**Problem:** "Invalid redirect_uri"
- **Solution:** Ensure redirect URI matches exactly (including protocol)

### API Client Issues

**Problem:** "Unauthorized (401)" error
- **Solution:** Access token may be expired, use refresh token or re-run OAuth flow

**Problem:** Rate limit errors
- **Solution:** Rate limiter should handle automatically, check configuration

**Problem:** "Insufficient permissions" error
- **Solution:** Verify required scopes are approved in Partner Portal

### Environment Issues

**Problem:** "Missing credentials" error
- **Solution:** Check `.env` file exists and has correct variable names

**Problem:** Configuration not loading
- **Solution:** Restart Python interpreter after updating `.env`

## Getting Help

1. **Review Setup Guide:** [TIKTOK_SHOP_SETUP_GUIDE.md](./TIKTOK_SHOP_SETUP_GUIDE.md)
2. **Check Troubleshooting Section:** See setup guide for common solutions
3. **Review Integration Docs:** `./ai-content-agents/integrations/tiktok_shop/README.md`
4. **Contact TikTok Support:** Submit ticket in Partner Portal

## Contributing to Tests

When adding new tests:
1. Add test case to [VALIDATION.md](./VALIDATION.md) with:
   - Test ID and name
   - Test procedure
   - Expected results
   - Space for actual results
2. Update this README with test description
3. Add troubleshooting guidance if applicable

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| TikTok Shop Account Setup | 1-3 business days | Business documentation |
| API App Creation & Approval | 1-5 business days | Seller account approval |
| Environment Configuration | 15 minutes | API credentials |
| OAuth Testing | 15 minutes | Environment configured |
| API Client Testing | 30 minutes | OAuth completed |
| Error Handling Testing | 30 minutes | API client working |
| Agent Testing | 30 minutes | API client working |
| Integration Testing | 1 hour | All components working |
| Security Validation | 15 minutes | All tests completed |
| **Total Active Testing Time** | **~3.5 hours** | |
| **Total Elapsed Time** | **3-8 business days** | (includes approval wait times) |

## Success Criteria

All tests in [VALIDATION.md](./VALIDATION.md) should be marked as ✅ Passed, with:
- [ ] OAuth flow working end-to-end
- [ ] API client can fetch products, orders, and analytics
- [ ] Rate limiting prevents API errors
- [ ] Error handling works for all error types
- [ ] TikTokShopAgent provides high-level interface
- [ ] Integration tests pass
- [ ] No hardcoded secrets in code
- [ ] Documentation is complete and accurate

## Next Steps After Testing

Once all tests pass:
1. Mark subtask-6-1 as completed in `implementation_plan.json`
2. Proceed to subtask-6-2 (Test product sync with real data)
3. Continue with remaining validation subtasks
4. Complete final QA sign-off

---

**Last Updated:** 2025-02-26

**For Questions:** See [TIKTOK_SHOP_SETUP_GUIDE.md](./TIKTOK_SHOP_SETUP_GUIDE.md) troubleshooting section
