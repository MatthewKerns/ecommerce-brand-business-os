# TikTok Shop API Integration - Setup Guide

This guide walks you through the complete setup process for TikTok Shop API integration, from creating a seller account to obtaining API credentials and testing the OAuth flow.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create TikTok Shop Seller Account](#step-1-create-tiktok-shop-seller-account)
4. [Step 2: Create TikTok Shop API App](#step-2-create-tiktok-shop-api-app)
5. [Step 3: Configure Environment](#step-3-configure-environment)
6. [Step 4: Test OAuth Flow](#step-4-test-oauth-flow)
7. [Step 5: Validate Integration](#step-5-validate-integration)
8. [Troubleshooting](#troubleshooting)
9. [Resources](#resources)

---

## Overview

The TikTok Shop API integration enables your application to:
- **Authenticate** with TikTok Shop using OAuth 2.0
- **Sync products** from your TikTok Shop catalog
- **Retrieve orders** and order details
- **Update inventory** levels
- **Fetch analytics** and performance metrics
- **Manage content** (videos, posts)

This setup typically takes 3-5 business days due to TikTok Shop approval processes.

---

## Prerequisites

Before starting, ensure you have:

- **Business Requirements:**
  - [ ] Registered business entity (LLC, Corporation, etc.)
  - [ ] Business Tax ID (EIN, VAT number, etc.)
  - [ ] Business bank account
  - [ ] Business address
  - [ ] Business contact information

- **Technical Requirements:**
  - [ ] Domain name (for redirect URIs)
  - [ ] HTTPS-enabled server (for webhooks, if needed)
  - [ ] Python 3.8+ development environment

- **Documentation:**
  - [ ] Business registration documents
  - [ ] Tax documents
  - [ ] Identity verification (passport, driver's license)
  - [ ] Bank account verification

---

## Step 1: Create TikTok Shop Seller Account

### 1.1 Register for TikTok Shop

1. **Visit TikTok Shop Seller Portal:**
   - Go to: https://seller.tiktokshop.com/
   - Click "Sign Up" or "Register"

2. **Choose Account Type:**
   - Select your region (US, UK, SEA, etc.)
   - Choose "Business Account" (recommended for API access)

3. **Provide Business Information:**
   - Business name
   - Business type (LLC, Corporation, Sole Proprietorship)
   - Business registration number
   - Tax identification number
   - Business address
   - Contact information (email, phone)

4. **Identity Verification:**
   - Upload business registration documents
   - Upload tax documents (W9, EIN letter, etc.)
   - Upload identity verification documents (passport, driver's license)
   - Provide authorized representative information

5. **Bank Account Setup:**
   - Link business bank account for payouts
   - Verify account with micro-deposits (if required)

6. **Shop Configuration:**
   - Set up shop name and description
   - Upload shop logo and banner
   - Configure shipping settings
   - Set up payment methods

### 1.2 Wait for Approval

- **Timeline:** 1-3 business days
- **Status:** Check your email and seller dashboard for updates
- **Next Steps:** Once approved, proceed to Step 2

### 1.3 Document Your Account Details

After approval, record these details for reference:

```
Seller Account Information:
- Seller ID: ___________________
- Shop Name: ___________________
- Region: ___________________
- Account Email: ___________________
- Approval Date: ___________________
```

---

## Step 2: Create TikTok Shop API App

### 2.1 Access Partner Portal

1. **Navigate to TikTok Shop Partner Portal:**
   - Go to: https://partner.tiktokshop.com/
   - Log in with your seller account credentials

2. **Navigate to Developer Center:**
   - Click "Developer" or "API Management" in the menu
   - Select "Create App" or "New Application"

### 2.2 Create API Application

1. **Basic Information:**
   - **App Name:** Enter a descriptive name (e.g., "My Brand Content Automation")
   - **App Type:** Select one of:
     - "Self-developed App" (if building for your own shop)
     - "Third-party App" (if building for multiple shops)
   - **App Description:** Describe your app's purpose
   - **App Icon:** Upload a 512x512 PNG logo

2. **App Capabilities:**
   Select the APIs you need access to:
   - [ ] **Content API** - For video and post management
   - [ ] **Shop API** - For products, orders, inventory
   - [ ] **Data API** - For analytics and metrics
   - [ ] **Fulfillment API** - For order fulfillment (optional)
   - [ ] **Finance API** - For financial data (optional)

3. **OAuth Configuration:**
   - **Redirect URIs:** Add authorized redirect URIs
     - Development: `http://localhost:8000/callback`
     - Production: `https://yourdomain.com/oauth/callback`
   - **Webhook URL:** (Optional) For real-time event notifications
     - Example: `https://yourdomain.com/webhooks/tiktok`

4. **Scopes/Permissions:**
   Request specific scopes based on your needs:
   - `product.read` - Read product information
   - `product.write` - Create/update products
   - `order.read` - Read order information
   - `order.write` - Update order status
   - `inventory.read` - Read inventory levels
   - `inventory.write` - Update inventory
   - `analytics.read` - Read analytics data
   - `content.read` - Read content (videos, posts)
   - `content.write` - Create/update content

   **Important:** Request all scopes you'll need upfront. Changing scopes after approval requires creating a new app.

5. **Terms and Conditions:**
   - Review TikTok Shop API Terms of Service
   - Review Data Usage Policy
   - Accept terms and conditions

### 2.3 Submit for Approval

1. **Review Application:**
   - Double-check all information
   - Ensure all required scopes are selected
   - Verify redirect URIs are correct

2. **Submit Application:**
   - Click "Submit for Review"
   - Wait for approval notification

3. **Approval Timeline:**
   - **Standard:** 1-5 business days
   - **Status Updates:** Check email and partner portal

### 2.4 Retrieve API Credentials

Once approved:

1. **Access App Details:**
   - Go to Partner Portal → Developer → Your App
   - Navigate to "Credentials" or "API Keys" section

2. **Copy Credentials:**
   ```
   App Key: ___________________
   App Secret: ___________________
   ```

   **Security Warning:** Keep these credentials secure! Never commit them to version control.

3. **Document App Details:**
   ```
   API App Information:
   - App Name: ___________________
   - App Key: ___________________
   - App Secret: [STORED SECURELY]
   - Scopes Approved: ___________________
   - Approval Date: ___________________
   ```

---

## Step 3: Configure Environment

### 3.1 Create Environment File

1. **Navigate to project directory:**
   ```bash
   cd ai-content-agents
   ```

2. **Copy example environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file:**
   ```bash
   # Open in your preferred editor
   nano .env
   # or
   vim .env
   # or
   code .env
   ```

### 3.2 Add TikTok Shop Credentials

Update the `.env` file with your credentials:

```env
# TikTok Shop API Configuration
TIKTOK_SHOP_APP_KEY=your-actual-app-key-here
TIKTOK_SHOP_APP_SECRET=your-actual-app-secret-here

# Optional: Access token (obtained through OAuth flow)
# TIKTOK_SHOP_ACCESS_TOKEN=
# TIKTOK_SHOP_REFRESH_TOKEN=

# Optional: Shop ID (for multi-shop scenarios)
# TIKTOK_SHOP_SHOP_ID=
```

### 3.3 Verify Configuration

Test that credentials are loaded correctly:

```bash
cd ai-content-agents
python -c "from config.config import TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET; print('✓ Configuration loaded successfully')"
```

Expected output:
```
✓ Configuration loaded successfully
```

### 3.4 Secure Your Credentials

**Important Security Steps:**

1. **Never commit .env file:**
   ```bash
   # Verify .env is in .gitignore
   cat .gitignore | grep .env
   ```

2. **Restrict file permissions:**
   ```bash
   chmod 600 .env
   ```

3. **Use environment variables in production:**
   - Set credentials via hosting platform (Heroku, AWS, etc.)
   - Don't use .env files in production

---

## Step 4: Test OAuth Flow

### 4.1 Run OAuth Test Script

The OAuth test script will guide you through the complete authentication flow:

```bash
cd ai-content-agents
python test_oauth_flow.py
```

### 4.2 Follow Interactive Prompts

The script will:

1. **Validate Credentials** - Checks that your App Key and Secret are configured
2. **Initialize OAuth Handler** - Creates OAuth client instance
3. **Generate Authorization URL** - Creates URL for user authorization
4. **Exchange Authorization Code** - Converts code to access token
5. **Test Token Refresh** - Validates token refresh functionality
6. **Test Signature Generation** - Verifies API request signing

### 4.3 Complete Authorization Flow

When the script provides an authorization URL:

1. **Copy the URL** from the terminal
2. **Open in a web browser**
3. **Log in** with your TikTok Shop seller account
4. **Authorize the application** - Review and approve requested scopes
5. **Copy the authorization code** from the redirect URL
   - Look for `code=` parameter in the URL
   - Example: `http://localhost:8000/callback?code=ABC123...`
6. **Paste the code** back into the test script

### 4.4 Save Access Tokens

After successful token exchange, the script will display:

```
Access Token: eyJhbGc...
Refresh Token: def456...
Expires In: 86400 seconds
```

**Add these to your .env file:**

```env
TIKTOK_SHOP_ACCESS_TOKEN=eyJhbGc...
TIKTOK_SHOP_REFRESH_TOKEN=def456...
```

### 4.5 OAuth Flow Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| "Invalid app_key" | Verify App Key in .env matches Partner Portal |
| "Invalid redirect_uri" | Ensure redirect URI matches exactly (including protocol) |
| "Authorization code expired" | Code expires in ~10 minutes, request a new one |
| "Invalid scope" | Ensure requested scopes are approved for your app |
| "Network error" | Check internet connection, firewall settings |

---

## Step 5: Validate Integration

### 5.1 Test API Client

Create a simple test script to verify API access:

```python
# test_api.py
from integrations.tiktok_shop.client import TikTokShopClient
from config.config import TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET
import os

# Get access token from environment
access_token = os.getenv('TIKTOK_SHOP_ACCESS_TOKEN')

# Initialize client
client = TikTokShopClient(
    app_key=TIKTOK_SHOP_APP_KEY,
    app_secret=TIKTOK_SHOP_APP_SECRET,
    access_token=access_token
)

# Test: Get products
print("Testing product retrieval...")
products = client.get_products(page_size=5)
print(f"✓ Retrieved {len(products.get('data', {}).get('products', []))} products")

# Test: Get orders
print("\nTesting order retrieval...")
orders = client.get_orders(page_size=5)
print(f"✓ Retrieved {len(orders.get('data', {}).get('orders', []))} orders")

print("\n✓ API integration working correctly!")
```

Run the test:
```bash
cd ai-content-agents
python test_api.py
```

### 5.2 Test TikTokShopAgent

Test the high-level agent interface:

```python
# test_agent.py
from agents.tiktok_shop_agent import TikTokShopAgent
import os

# Initialize agent
agent = TikTokShopAgent()
agent.set_access_token(os.getenv('TIKTOK_SHOP_ACCESS_TOKEN'))

# Test: Sync products
print("Testing product sync...")
products = agent.sync_products(max_products=10)
print(f"✓ Synced {len(products)} products")

# Test: Get analytics
print("\nTesting analytics...")
analytics = agent.get_analytics()
print(f"✓ Retrieved analytics data")

print("\n✓ TikTokShopAgent working correctly!")
```

Run the test:
```bash
cd ai-content-agents
python test_agent.py
```

### 5.3 Document Results

Update `VALIDATION.md` with your test results:
- Mark each test as ✅ Passed, ⏳ Pending, or ❌ Failed
- Document any errors or issues encountered
- Note any deviations from expected behavior

---

## Troubleshooting

### Common Issues

#### Issue: "Missing credentials" error

**Symptom:**
```
TikTokShopAuthError: Missing required credentials
```

**Solution:**
1. Check that .env file exists: `ls -la .env`
2. Verify credentials are set: `cat .env | grep TIKTOK`
3. Ensure no typos in variable names
4. Restart application after updating .env

---

#### Issue: "Invalid app_key" error

**Symptom:**
```
TikTokShopAuthError: Invalid app_key
```

**Solution:**
1. Verify App Key in Partner Portal
2. Copy the EXACT key (no extra spaces)
3. Check for any hidden characters
4. Ensure app is approved and active

---

#### Issue: "Unauthorized" or "Access token expired"

**Symptom:**
```
TikTokShopAuthError: Unauthorized (401)
```

**Solution:**
1. Check if access token has expired (typically 24 hours)
2. Use refresh token to get new access token:
   ```python
   from integrations.tiktok_shop.oauth import TikTokShopOAuth
   oauth = TikTokShopOAuth(app_key, app_secret)
   new_tokens = oauth.refresh_access_token(refresh_token)
   # Update .env with new tokens
   ```
3. Re-run OAuth flow if refresh token also expired

---

#### Issue: Rate limit errors

**Symptom:**
```
TikTokShopRateLimitError: Rate limit exceeded
```

**Solution:**
- Rate limiter should handle this automatically
- Verify rate limiter is enabled in client
- Check rate limiter configuration (10 req/sec default)
- Reduce request frequency if needed

---

#### Issue: Scope permission errors

**Symptom:**
```
TikTokShopAuthError: Insufficient permissions
```

**Solution:**
1. Check requested operation requires specific scope
2. Verify scope is approved in Partner Portal
3. If scope is missing, create new API app with required scopes
4. Complete OAuth flow again with new credentials

---

### Getting Help

If you encounter issues not covered here:

1. **Check TikTok Shop API Documentation:**
   - https://partner.tiktokshop.com/doc

2. **Review API Status:**
   - Check for any TikTok Shop API outages or maintenance

3. **Contact TikTok Shop Support:**
   - Partner Portal → Support → Submit Ticket
   - Include: App Key, error messages, request/response logs

4. **Check Validation Documentation:**
   - Review `VALIDATION.md` for similar issues and solutions

---

## Resources

### Official Documentation

- **TikTok Shop Seller Center:** https://seller.tiktokshop.com/
- **TikTok Shop Partner Portal:** https://partner.tiktokshop.com/
- **API Documentation:** https://partner.tiktokshop.com/doc
- **Developer Forum:** https://developers.tiktok.com/community/

### Integration Documentation

- **OAuth Flow Guide:** `./ai-content-agents/integrations/tiktok_shop/README.md`
- **API Client Reference:** `./ai-content-agents/integrations/tiktok_shop/client.py`
- **Agent Reference:** `./ai-content-agents/agents/tiktok_shop_agent.py`
- **Quick Start Examples:** `./ai-content-agents/quick_start.py`

### Test Scripts

- **OAuth Test:** `./ai-content-agents/test_oauth_flow.py`
- **Validation Checklist:** `../api/VALIDATION.md`

---

## Next Steps

After completing this setup:

1. ✅ Complete all tests in `VALIDATION.md`
2. ✅ Document any issues or deviations
3. ✅ Familiarize yourself with the API client and agent interfaces
4. ✅ Review the code examples in `quick_start.py`
5. ✅ Start building your TikTok Shop integration!

---

**Last Updated:** 2025-02-26

**Version:** 1.0.0

**Status:** Ready for Testing
