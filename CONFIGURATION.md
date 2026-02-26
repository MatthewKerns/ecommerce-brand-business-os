# Configuration & Secrets Management Guide

A comprehensive guide to setting up, securing, and managing configuration across the E-Commerce Brand Business OS. This system supports multi-environment deployment (development, staging, production) with secure credential management for both Python and TypeScript services.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Environment Setup](#environment-setup)
4. [Python Service Configuration](#python-service-configuration)
5. [TypeScript Service Configuration](#typescript-service-configuration)
6. [Encryption & Security](#encryption--security)
7. [OAuth Setup](#oauth-setup)
8. [Multi-Environment Deployment](#multi-environment-deployment)
9. [Secrets Management](#secrets-management)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The configuration system provides:

- **Environment-specific settings** — Separate configurations for development, staging, and production
- **Secure credential storage** — Encrypted secrets at rest, never committed to version control
- **Type-safe validation** — Runtime validation with Python typing and TypeScript zod schemas
- **Automatic token refresh** — OAuth token management for Gmail and other services
- **Centralized management** — Consistent patterns across Python and TypeScript services

### Architecture

```
Configuration System
├── Python (ai-content-agents/)
│   ├── .env.development          # Development environment config
│   ├── .env.staging             # Staging environment config
│   ├── .env.production          # Production environment config
│   ├── config/secrets.py        # Encryption utilities (Fernet)
│   ├── config/environments.py   # Environment-aware loader
│   └── config/config.py         # Main configuration module
│
└── TypeScript (04-email-marketing-automation/)
    ├── .env.development          # Development environment config
    ├── .env.staging             # Staging environment config
    ├── .env.production          # Production environment config
    ├── src/config/index.ts      # Type-safe config with zod
    └── src/config/secrets.ts    # OAuth & encryption utilities
```

---

## Quick Start

### 1. Generate Encryption Key

```bash
# For Python services
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# For TypeScript services
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 2. Create Environment Files

```bash
# Python service
cd ai-content-agents
cp .env.example .env.development
cp .env.example .env.staging
cp .env.example .env.production

# TypeScript service
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation
cp .env.example .env.development
cp .env.example .env.staging
cp .env.example .env.production
```

### 3. Configure Your Environment

Edit `.env.development` (or `.env.staging`/`.env.production`) with your credentials:

```bash
# Set environment
ENVIRONMENT=development

# Add encryption key (generated in step 1)
ENCRYPTION_KEY=your-generated-key-here

# Add API keys
ANTHROPIC_API_KEY=sk-ant-...

# Add OAuth credentials (see OAuth Setup section)
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-secret
GMAIL_REFRESH_TOKEN=your-refresh-token
```

### 4. Verify Setup

```bash
# Python service
cd ai-content-agents
python test_setup.py

# TypeScript service
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation
npm run build
```

---

## Environment Setup

### Environment Variables

The system uses the `ENVIRONMENT` variable to determine which configuration to load:

| Environment | Value | Description |
|-------------|-------|-------------|
| **Development** | `development` | Local development with debug logging |
| **Staging** | `staging` | Pre-production testing environment |
| **Production** | `production` | Live production deployment |

**Set the environment:**

```bash
# In your .env file
ENVIRONMENT=development

# Or as a shell variable
export ENVIRONMENT=staging

# Or inline with commands
ENVIRONMENT=production python generate_content.py
```

### Environment File Priority

Configuration is loaded in this order (later sources override earlier ones):

1. Base `.env` file (if exists)
2. Environment-specific `.env.{environment}` file
3. Existing environment variables (highest priority)

---

## Python Service Configuration

### Directory Structure

```
ai-content-agents/
├── .env.example              # Template with all options
├── .env.development          # Development config
├── .env.staging             # Staging config
├── .env.production          # Production config
├── config/
│   ├── config.py            # Main configuration
│   ├── secrets.py           # Encryption utilities
│   └── environments.py      # Environment loader
└── requirements.txt         # Dependencies (includes cryptography)
```

### Installation

```bash
cd ai-content-agents
pip install -r requirements.txt
```

**Required dependencies:**
- `cryptography>=41.0.0` — For Fernet encryption
- `python-dotenv>=1.0.0` — For .env file loading

### Configuration Options

**Environment & Encryption:**
```bash
# Environment selection
ENVIRONMENT=development

# Encryption key for secrets at rest
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=base64-encoded-key-here
```

**Anthropic API:**
```bash
# API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Model selection
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Optional: Generation settings
MAX_TOKENS=4096
TEMPERATURE=1.0
```

### Usage in Code

```python
from config.config import ANTHROPIC_API_KEY, MAX_TOKENS
from config.environments import load_environment_config, get_environment

# Load environment-specific configuration
config = load_environment_config()  # Auto-detects from ENVIRONMENT var
# Or specify explicitly:
# config = load_environment_config("staging")

# Check current environment
env = get_environment()
print(f"Running in {env} mode")

# Use configuration values
print(f"Using API key: {ANTHROPIC_API_KEY[:10]}...")
```

### Encryption Example

```python
from config.secrets import SecretsManager, encrypt_secret, decrypt_secret

# Initialize manager (uses ENCRYPTION_KEY from env)
manager = SecretsManager()

# Encrypt sensitive data
api_key = "sk-ant-secret-key"
encrypted = manager.encrypt(api_key)
print(f"Encrypted: {encrypted}")

# Decrypt when needed
decrypted = manager.decrypt(encrypted)
print(f"Decrypted: {decrypted}")

# Convenience functions
encrypted = encrypt_secret("sensitive-data")
decrypted = decrypt_secret(encrypted)

# Encrypt/decrypt files
from pathlib import Path
manager.encrypt_file(Path("secrets.txt"), Path("secrets.enc"))
manager.decrypt_file(Path("secrets.enc"), Path("secrets.txt"))
```

---

## TypeScript Service Configuration

### Directory Structure

```
04-email-marketing-automation/implementation/
├── .env.example                  # Template with all options
├── .env.development             # Development config
├── .env.staging                # Staging config
├── .env.production             # Production config
├── src/
│   └── config/
│       ├── index.ts            # Main config with zod validation
│       └── secrets.ts          # OAuth & encryption utilities
└── package.json                # Dependencies (includes zod)
```

### Installation

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation
npm install
```

**Required dependencies:**
- `zod` — Runtime schema validation
- `dotenv` — Environment file loading

### Configuration Options

**Environment & Encryption:**
```bash
# Environment selection
ENVIRONMENT=development

# Encryption key for credentials
# Generate with: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
ENCRYPTION_KEY=your-hex-encoded-key
```

**Gmail OAuth:**
```bash
# OAuth credentials from Google Cloud Console
GMAIL_CLIENT_ID=123456789-xxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxx
GMAIL_REFRESH_TOKEN=1//xxx
GMAIL_REDIRECT_URI=http://localhost:3000/auth/gmail/callback
GMAIL_SENDER_EMAIL=noreply@yourdomain.com
GMAIL_SENDER_NAME=Your Company
```

**AI Providers:**
```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Google Gemini (optional)
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash

# OpenAI (optional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

**Google Sheets:**
```bash
# Service account credentials
GOOGLE_SHEETS_ID=1abc...xyz
GOOGLE_SERVICE_ACCOUNT_EMAIL=service@project.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

**Analytics & Security:**
```bash
# HMAC webhook verification
WEBHOOK_SECRET=your-secret-here

# Optional rate limiting
GMAIL_DAILY_QUOTA=250
RATE_LIMIT_REQUESTS_PER_SECOND=10
```

### Usage in Code

```typescript
import { loadEnvironmentConfig, getGmailConfig, getAIConfig } from './config';
import { loadOAuthCredentials, validateOAuthCredentials } from './config/secrets';

// Load environment-specific config
loadEnvironmentConfig();

// Get validated configuration
const gmailConfig = getGmailConfig();
const aiConfig = getAIConfig('claude');

// OAuth credential management
const credentials = loadOAuthCredentials('GMAIL');
const validation = validateOAuthCredentials(credentials);

if (!validation.isValid) {
  console.error('Invalid OAuth credentials:', validation.errors);
  process.exit(1);
}
```

### Type-Safe Configuration

The TypeScript config uses zod schemas for runtime validation:

```typescript
// Config is fully typed and validated
const config = getGmailConfig();
// TypeScript knows:
// config.clientId: string
// config.clientSecret: string
// config.refreshToken: string
// config.redirectUri: string (validated as URL)
// config.senderEmail: string (validated as email)
// config.senderName?: string
```

---

## Encryption & Security

### Encryption Key Generation

**Python (Fernet symmetric encryption):**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Output: gAAAAABh... (44 characters, base64-encoded)
```

**TypeScript (AES-256-GCM):**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Output: a1b2c3d4... (64 characters, hex-encoded)
```

### Storing Encryption Keys

**Never commit encryption keys to version control!**

**Secure storage options:**

1. **Environment variables** (recommended for local development):
   ```bash
   export ENCRYPTION_KEY='your-generated-key'
   ```

2. **Secrets managers** (recommended for production):
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **CI/CD secrets** (for automated deployments):
   - GitHub Secrets
   - GitLab CI/CD Variables
   - CircleCI Environment Variables

### Security Best Practices

✅ **DO:**
- Generate unique keys for each environment
- Rotate keys periodically (especially after team changes)
- Use strong, randomly-generated keys
- Store keys in secure secrets managers
- Set restrictive file permissions on .env files (`chmod 600`)
- Use `.gitignore` to exclude all `.env*` files except `.env.example`

❌ **DON'T:**
- Commit `.env` files to version control
- Share keys via email, Slack, or messaging apps
- Use weak or predictable keys
- Reuse keys across environments
- Log decrypted secrets

### Secrets Encryption Example

**Python - Encrypt sensitive config values:**
```python
from config.secrets import SecretsManager

manager = SecretsManager()

# Encrypt API key before storing
api_key = "sk-ant-very-secret-key"
encrypted_key = manager.encrypt(api_key)

# Store encrypted value in database or config
# Later, decrypt when needed:
decrypted_key = manager.decrypt(encrypted_key)
```

**TypeScript - Encrypt credentials:**
```typescript
import { encryptCredentials, decryptCredentials } from './config/secrets';

// Encrypt OAuth credentials for storage
const credentials = {
  clientId: 'abc123',
  clientSecret: 'secret456',
  refreshToken: 'refresh789'
};

const encryptionKey = process.env.ENCRYPTION_KEY!;
const encrypted = encryptCredentials(credentials, encryptionKey);

// Later, decrypt when needed
const decrypted = decryptCredentials(encrypted, encryptionKey);
```

---

## OAuth Setup

### Gmail OAuth Configuration

Gmail integration requires OAuth 2.0 credentials from Google Cloud Console.

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

#### Step 2: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose application type: **Web application**
4. Configure:
   - **Name**: "Email Marketing Automation"
   - **Authorized JavaScript origins**: `http://localhost:3000`
   - **Authorized redirect URIs**: `http://localhost:3000/auth/gmail/callback`
5. Click "Create"
6. Save the **Client ID** and **Client Secret**

#### Step 3: Generate Refresh Token

Use Google's OAuth 2.0 Playground or this Node.js script:

```javascript
// get-gmail-token.js
const { google } = require('googleapis');
const readline = require('readline');

const oauth2Client = new google.auth.OAuth2(
  'YOUR_CLIENT_ID',
  'YOUR_CLIENT_SECRET',
  'http://localhost:3000/auth/gmail/callback'
);

const scopes = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.readonly'
];

const url = oauth2Client.generateAuthUrl({
  access_type: 'offline',
  scope: scopes,
});

console.log('Authorize this app by visiting:', url);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question('Enter the code from the page: ', async (code) => {
  const { tokens } = await oauth2Client.getToken(code);
  console.log('\nRefresh token:', tokens.refresh_token);
  rl.close();
});
```

**Run:**
```bash
npm install googleapis
node get-gmail-token.js
```

#### Step 4: Add to Environment Config

```bash
# .env.development
GMAIL_CLIENT_ID=123456789-xxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxx
GMAIL_REFRESH_TOKEN=1//xxx-refresh-token-here
GMAIL_REDIRECT_URI=http://localhost:3000/auth/gmail/callback
GMAIL_SENDER_EMAIL=noreply@yourdomain.com
GMAIL_SENDER_NAME=Your Company Name
```

#### Step 5: Verify OAuth Setup

```typescript
import { GmailClient } from './core/email/gmail-client';

const client = new GmailClient();
await client.initialize();

// Test sending
await client.sendEmail({
  to: 'test@example.com',
  subject: 'OAuth Test',
  body: 'If you receive this, OAuth is working!',
  isHtml: false
});
```

### Token Refresh

The system automatically refreshes OAuth tokens before they expire:

**Python:**
```python
# Handled automatically by config/secrets.py
from config.secrets import get_secrets_manager

manager = get_secrets_manager()
# Token refresh is automatic when accessing OAuth credentials
```

**TypeScript:**
```typescript
// Handled by GmailClient
import { GmailClient } from './core/email/gmail-client';

const client = new GmailClient();
// Token is automatically refreshed before each API call
await client.sendEmail({...});
```

---

## Multi-Environment Deployment

### Environment Strategies

#### Development Environment

**Purpose:** Local development and testing

**Configuration:**
```bash
# .env.development
ENVIRONMENT=development

# Use sandbox/test credentials
ANTHROPIC_API_KEY=sk-ant-test-...
GMAIL_SENDER_EMAIL=dev@example.com

# Enable debug logging
LOG_LEVEL=debug

# Use lower rate limits
GMAIL_DAILY_QUOTA=50
```

**Usage:**
```bash
# Explicitly set environment
export ENVIRONMENT=development

# Or inline
ENVIRONMENT=development python generate_content.py blog post "Test Post"
```

#### Staging Environment

**Purpose:** Pre-production testing with production-like data

**Configuration:**
```bash
# .env.staging
ENVIRONMENT=staging

# Use production API keys but separate credentials
ANTHROPIC_API_KEY=sk-ant-staging-...
GMAIL_SENDER_EMAIL=staging@example.com

# Production-level rate limits
GMAIL_DAILY_QUOTA=250

# Moderate logging
LOG_LEVEL=info
```

**Deployment:**
```bash
# Set environment in deployment pipeline
export ENVIRONMENT=staging

# Deploy to staging server
git push staging main
```

#### Production Environment

**Purpose:** Live production system serving real users

**Configuration:**
```bash
# .env.production
ENVIRONMENT=production

# Production credentials (managed by secrets manager)
ANTHROPIC_API_KEY=${AWS_SECRET_ANTHROPIC_KEY}
GMAIL_SENDER_EMAIL=noreply@yourdomain.com

# Strict rate limits
GMAIL_DAILY_QUOTA=250

# Minimal logging
LOG_LEVEL=warning
```

**Security Notes for Production:**
- Never store `.env.production` in version control
- Use secrets managers (AWS Secrets Manager, GCP Secret Manager, etc.)
- Enable encryption at rest for all secrets
- Implement IP whitelisting for API access
- Monitor for suspicious activity

### Deployment Checklist

**Before deploying to a new environment:**

- [ ] Generate unique encryption key for environment
- [ ] Create environment-specific `.env.{environment}` file
- [ ] Configure secrets manager (production only)
- [ ] Set up OAuth credentials (separate for each environment)
- [ ] Verify API quotas and rate limits
- [ ] Test configuration loading
- [ ] Run security scan for exposed secrets
- [ ] Set file permissions (`chmod 600 .env.*`)
- [ ] Configure monitoring and alerting
- [ ] Document environment-specific settings

### CI/CD Integration

**GitHub Actions example:**

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up environment
        run: |
          echo "ENVIRONMENT=staging" >> $GITHUB_ENV
          echo "ANTHROPIC_API_KEY=${{ secrets.STAGING_ANTHROPIC_KEY }}" >> .env.staging
          echo "ENCRYPTION_KEY=${{ secrets.STAGING_ENCRYPTION_KEY }}" >> .env.staging

      - name: Install dependencies
        run: |
          cd ai-content-agents
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd ai-content-agents
          python test_setup.py

      - name: Deploy
        run: |
          # Your deployment script
          ./deploy-staging.sh
```

---

## Secrets Management

### .gitignore Configuration

**Ensure these entries in `.gitignore`:**

```gitignore
# Environment files
.env
.env.local
.env.*.local
.env.development
.env.staging
.env.production

# Keep example files
!.env.example

# Encrypted secrets (if using file-based encryption)
*.encrypted
*.enc
secrets/

# OAuth tokens
*token*
*oauth*
credentials.json
```

### Checking for Exposed Secrets

**Pre-commit hook:**

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for common secret patterns
if git diff --cached | grep -iE '(api[_-]?key|secret|password|token).*=.*[a-zA-Z0-9]{20}'; then
  echo "❌ ERROR: Potential secret detected in commit!"
  echo "Review your changes and remove any sensitive data."
  exit 1
fi

# Check for .env files
if git diff --cached --name-only | grep -E '^\.env$|^\.env\.(development|staging|production)$'; then
  echo "❌ ERROR: Attempted to commit .env file!"
  echo "Only .env.example should be committed."
  exit 1
fi

echo "✅ Pre-commit checks passed"
exit 0
```

**Make executable:**
```bash
chmod +x .git/hooks/pre-commit
```

### Manual Secret Scan

```bash
# Scan for exposed secrets in repository
git diff --cached | grep -iE '(api[_-]?key|secret|password|token).*=.*[a-zA-Z0-9]{20}' && echo 'SECRETS DETECTED' || echo 'OK'

# Check if .env files are tracked
git ls-files | grep -E '^\\.env$' && echo 'FAILED: .env should not be committed' || echo 'OK'

# Scan commit history for secrets (use git-secrets tool)
git secrets --scan-history
```

### Rotating Secrets

**When to rotate:**
- Suspected compromise or exposure
- Team member departure
- Regular security policy (e.g., every 90 days)
- After any security incident

**Rotation procedure:**

1. **Generate new keys:**
   ```bash
   # New encryption key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **Update secrets manager:**
   ```bash
   # AWS example
   aws secretsmanager update-secret \
     --secret-id production/encryption-key \
     --secret-string "new-key-here"
   ```

3. **Re-encrypt existing secrets:**
   ```python
   from config.secrets import SecretsManager

   old_manager = SecretsManager(old_encryption_key)
   new_manager = SecretsManager(new_encryption_key)

   # Decrypt with old key, encrypt with new key
   for secret in encrypted_secrets:
       decrypted = old_manager.decrypt(secret)
       re_encrypted = new_manager.encrypt(decrypted)
       # Store re-encrypted value
   ```

4. **Update environment configurations**

5. **Revoke old credentials:**
   - Anthropic API: Disable old key in console
   - Gmail OAuth: Revoke tokens in Google Cloud Console

6. **Verify all services:**
   ```bash
   # Test each environment
   ENVIRONMENT=development python test_setup.py
   ENVIRONMENT=staging python test_setup.py
   ENVIRONMENT=production python test_setup.py
   ```

---

## Troubleshooting

### Common Issues

#### "Environment configuration file not found"

**Error:**
```
FileNotFoundError: Environment configuration file not found: .env.development
Please create it based on .env.example
```

**Solution:**
```bash
# Copy example file
cp .env.example .env.development

# Or create all environments
cp .env.example .env.development
cp .env.example .env.staging
cp .env.example .env.production

# Edit with your credentials
nano .env.development
```

#### "Failed to decrypt value"

**Error:**
```
ValueError: Failed to decrypt value: Invalid token
```

**Causes:**
- Wrong encryption key
- Data corrupted
- Encrypted with different key

**Solution:**
```python
# Verify encryption key
import os
print(f"ENCRYPTION_KEY: {os.getenv('ENCRYPTION_KEY')[:10]}...")

# Re-encrypt with correct key
from config.secrets import SecretsManager
manager = SecretsManager("correct-key-here")
encrypted = manager.encrypt("your-secret")
```

#### "Invalid OAuth credentials"

**Error:**
```
Invalid OAuth credentials: ['Refresh token is missing or invalid']
```

**Solution:**
1. Verify Gmail OAuth setup (see [OAuth Setup](#oauth-setup))
2. Check token in `.env.{environment}`:
   ```bash
   grep GMAIL_REFRESH_TOKEN .env.development
   ```
3. Regenerate refresh token if expired

#### TypeScript Build Errors

**Error:**
```
error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'
```

**Solution:**
```typescript
// Ensure all required config is set
import { validateConfig } from './config';

try {
  validateConfig();
} catch (error) {
  console.error('Configuration validation failed:', error.message);
  process.exit(1);
}
```

#### Missing Dependencies

**Python:**
```bash
# Install all dependencies
cd ai-content-agents
pip install -r requirements.txt

# Or specific packages
pip install cryptography python-dotenv
```

**TypeScript:**
```bash
# Install all dependencies
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation
npm install

# Or specific packages
npm install zod dotenv
```

### Debugging Configuration

**Python:**
```python
from config.environments import load_environment_config, get_environment

# Check current environment
env = get_environment()
print(f"Environment: {env}")

# Load and inspect config
config = load_environment_config()
print(f"Loaded {len(config)} configuration values")

# Check specific values (masked)
import os
api_key = os.getenv('ANTHROPIC_API_KEY', '')
print(f"API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
```

**TypeScript:**
```typescript
import { loadEnvironmentConfig, getEnvironment } from './config';

// Check environment
const env = getEnvironment();
console.log(`Environment: ${env}`);

// Load configuration
loadEnvironmentConfig();

// Check loaded values (masked)
const apiKey = process.env.ANTHROPIC_API_KEY || '';
console.log(`API Key: ${apiKey.slice(0, 10)}...${apiKey.slice(-4)}`);
```

### Verifying Configuration

**Complete verification script:**

```bash
#!/bin/bash
# verify-config.sh

echo "🔍 Configuration Verification"
echo "=============================="

# Check Python service
echo -e "\n📦 Python Service (ai-content-agents)"
cd ai-content-agents

if [ -f .env.development ]; then
  echo "✅ .env.development exists"
else
  echo "❌ .env.development missing"
fi

if python -c "from config.secrets import SecretsManager; print('OK')" 2>/dev/null; then
  echo "✅ Secrets module working"
else
  echo "❌ Secrets module failed"
fi

if python -c "from config.environments import load_environment_config; print('OK')" 2>/dev/null; then
  echo "✅ Environments module working"
else
  echo "❌ Environments module failed"
fi

# Check TypeScript service
echo -e "\n📦 TypeScript Service (email-automation)"
cd ../claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation

if [ -f .env.development ]; then
  echo "✅ .env.development exists"
else
  echo "❌ .env.development missing"
fi

if npx tsc --noEmit 2>&1 | grep -q 'error' ; then
  echo "❌ TypeScript compilation failed"
else
  echo "✅ TypeScript compilation passed"
fi

echo -e "\n✨ Verification complete"
```

**Run:**
```bash
chmod +x verify-config.sh
./verify-config.sh
```

---

## Additional Resources

### Documentation
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Gmail API Overview](https://developers.google.com/gmail/api)
- [Google Cloud OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Cryptography Library](https://cryptography.io/en/latest/)
- [Zod Schema Validation](https://zod.dev/)

### Security Best Practices
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [12 Factor App - Config](https://12factor.net/config)

### Tools
- [git-secrets](https://github.com/awslabs/git-secrets) — Prevent committing secrets
- [trufflehog](https://github.com/trufflesecurity/trufflehog) — Scan for exposed secrets
- [dotenv-vault](https://www.dotenv.org/security/) — Encrypted .env file management

---

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review relevant module documentation:
   - Python: `ai-content-agents/config/`
   - TypeScript: `04-email-marketing-automation/implementation/src/config/`
3. Verify environment setup with verification script
4. Check logs for detailed error messages

---

*"Security is not a product, but a process."* — Bruce Schneier
