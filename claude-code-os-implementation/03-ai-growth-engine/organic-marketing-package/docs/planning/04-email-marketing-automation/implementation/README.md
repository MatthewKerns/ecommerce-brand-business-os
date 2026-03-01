# Email Marketing Automation Package

A niche-agnostic, fully-featured email marketing automation system extracted from production components. This package provides enterprise-grade email marketing capabilities that can be configured for any industry or use case.

## Architecture Overview

```
┌─────────────────┐
│   Data Sources  │
├─────────────────┤
│ • Clerk Auth    │ ← Email capture from scratch-and-win
│ • Google Sheets │ ← Lead storage & management
│ • Website Forms │ ← Direct capture
│ • API/Webhooks  │ ← External integrations
└────────┬────────┘
         │
    ┌────▼─────┐
    │   Core   │
    ├──────────┤
    │ • Leads  │ → Niche-agnostic lead model
    │ • Email  │ → Gmail API integration
    │ • AI Gen │ → Multi-provider content generation
    │ • Seqs   │ → Flexible sequence engine
    └────┬─────┘
         │
   ┌─────▼──────┐
   │  Outputs   │
   ├────────────┤
   │ • Emails   │ → Personalized campaigns
   │ • Analytics│ → Open/click tracking
   │ • Reports  │ → Performance metrics
   └────────────┘
```

## Current Integration Points

### ✅ What's Connected
- **Clerk → Email Storage**: Scratch-and-win captures emails via Clerk auth
- **Gmail API → Sending**: Full OAuth2 integration with retry logic
- **Google Sheets → Lead Management**: Bidirectional sync for lead data
- **AI Providers → Content**: Support for Gemini, OpenAI, and Claude

### 🔧 What Needs Connection
- **Clerk → This Package**: Import Clerk users as leads
- **This Package → Website**: Publish blog content
- **MCF Connector → Analytics**: Order tracking data
- **TikTok → Lead Capture**: Social commerce leads

## Features

### 1. Lead Management
- **Flexible Data Model**: Core fields + unlimited custom fields
- **Multiple Sources**: Website, social, API, manual, import
- **Segmentation**: Tags, segments, scoring, priority levels
- **Storage Adapters**: Google Sheets (implemented), Database (ready to add)

### 2. Email Infrastructure
- **Gmail API Integration**: OAuth2, MIME building, threading
- **Retry Logic**: Exponential backoff for rate limits
- **Template Variables**: Dynamic content substitution
- **Attachments**: Full MIME multipart support

### 3. Sequence Engine
- **Visual Flow Builder**: Drag-drop sequence creation
- **Conditional Logic**: If/then branching based on any field
- **A/B Testing**: Built-in variant testing with weights
- **Timing Control**: Business hours, skip weekends, timezone aware
- **Actions**: Email, wait, condition, webhook, goal tracking

### 4. AI Content Generation
- **Multi-Provider**: Gemini, OpenAI, Claude support
- **Template Library**: Welcome, nurture, promotional templates
- **Personalization**: Variable substitution, tone control
- **Safety Filters**: Content moderation built-in

### 5. Analytics & Tracking
- **Email Metrics**: Opens, clicks, replies, bounces
- **Conversion Funnel**: Lead → Engaged → Converted
- **HMAC Security**: Signed tracking URLs
- **Real-time Events**: Webhook notifications

## Installation

```bash
npm install @organic-marketing/email-automation
```

## Quick Start

### 1. Configure Providers

```typescript
import { EmailAutomation } from '@organic-marketing/email-automation';

const emailSystem = new EmailAutomation({
  // Gmail configuration
  gmail: {
    clientId: process.env.GMAIL_CLIENT_ID,
    clientSecret: process.env.GMAIL_CLIENT_SECRET,
    refreshToken: process.env.GMAIL_REFRESH_TOKEN,
    redirectUri: process.env.GMAIL_REDIRECT_URI,
    senderEmail: process.env.GMAIL_SENDER_EMAIL,
    senderName: 'Your Company'
  },

  // AI provider (choose one)
  ai: {
    provider: 'gemini',
    apiKey: process.env.GEMINI_API_KEY,
    model: 'gemini-1.5-flash'
  },

  // Lead storage
  storage: {
    type: 'google-sheets',
    spreadsheetId: process.env.GOOGLE_SHEETS_ID,
    credentials: {
      clientEmail: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
      privateKey: process.env.GOOGLE_SERVICE_ACCOUNT_KEY
    }
  }
});
```

### 2. Import Leads from Clerk

```typescript
// Fetch users from Clerk
import { clerkClient } from '@clerk/nextjs';

const clerkUsers = await clerkClient.users.getUserList();

// Import to email system
for (const user of clerkUsers.data) {
  await emailSystem.leads.create({
    email: user.emailAddresses[0].emailAddress,
    firstName: user.firstName,
    lastName: user.lastName,
    source: 'scratch_and_win',
    customFields: [
      { key: 'clerk_id', value: user.id, type: 'text' },
      { key: 'game_preference', value: user.publicMetadata.gamePreference, type: 'text' }
    ],
    consentGiven: true,
    consentSource: 'scratch_and_win_opt_in'
  });
}
```

### 3. Create a Welcome Sequence

```typescript
const welcomeSequence = await emailSystem.sequences.create({
  name: 'Welcome Series - E-commerce',
  description: 'Welcome new scratch-and-win subscribers',
  status: 'active',
  triggerType: 'immediate',

  steps: [
    {
      id: 'welcome_email',
      type: 'email',
      name: 'Welcome & Deliver Prize',
      config: {
        templateId: 'welcome_with_prize',
        subject: 'Welcome {{firstName}}! Your prize code is inside 🎁',
        fromName: 'Infinity Vault'
      }
    },
    {
      id: 'wait_3_days',
      type: 'wait',
      name: 'Wait 3 Days',
      config: { duration: 72, skipWeekends: true }
    },
    {
      id: 'brand_story',
      type: 'email',
      name: 'Brand Story',
      config: {
        templateId: 'brand_story',
        subject: 'The story behind Infinity Vault'
      }
    },
    {
      id: 'check_engagement',
      type: 'condition',
      name: 'Check if Engaged',
      config: {
        conditions: [
          { field: 'engagement.emailsOpened', operator: 'greater_than', value: 0 }
        ],
        trueStep: 'send_offer',
        falseStep: 'send_re_engagement'
      }
    }
  ],

  settings: {
    sendingDays: [1, 2, 3, 4, 5], // Monday-Friday
    sendingHours: { start: 9, end: 17 }, // 9am-5pm
    timezone: 'America/Los_Angeles',
    stopOnReply: true,
    stopOnConversion: true
  }
});
```

### 4. Generate & Send Personalized Emails

```typescript
// Generate content with AI
const content = await emailSystem.ai.generateContent({
  templateId: 'welcome_with_prize',
  variables: {
    companyName: 'Infinity Vault',
    subscriberName: lead.firstName,
    prizeCode: 'SPIN20OFF',
    gamePreference: lead.customFields.find(f => f.key === 'game_preference')?.value,
    nextStep: 'Check out our Pokemon collection'
  },
  tone: 'friendly',
  length: 'medium'
});

// Send the email
await emailSystem.email.send({
  to: lead.email,
  subject: content.subject,
  body: content.body,
  variables: {
    firstName: lead.firstName,
    prizeCode: 'SPIN20OFF'
  }
});
```

## Configuration for Different Niches

### E-commerce (Infinity Vault)
```typescript
{
  niche: 'ecommerce_tcg',
  customFields: [
    { key: 'game_preference', type: 'select', options: ['Pokemon', 'Magic', 'Yu-Gi-Oh'] },
    { key: 'prize_claimed', type: 'boolean' },
    { key: 'purchase_history', type: 'json' },
    { key: 'cart_value', type: 'number' }
  ],
  sequences: {
    welcome: { emails: 4, days: 12 },
    abandonment: { emails: 3, hours: [24, 72, 168] },
    win_back: { emails: 4, days: 30 }
  }
}
```

### B2B Energy (Original Use Case)
```typescript
{
  niche: 'b2b_energy',
  customFields: [
    { key: 'company', type: 'text' },
    { key: 'energy_subsector', type: 'select' },
    { key: 'company_size', type: 'select' },
    { key: 'decision_stage', type: 'select' }
  ],
  sequences: {
    nurture: { emails: 12, days: 180 },
    demo_follow_up: { emails: 3, days: 7 }
  }
}
```

## API Endpoints

The package exposes these REST endpoints when used with Express/Next.js:

```
POST   /api/leads                 - Create lead
GET    /api/leads/:id             - Get lead
PUT    /api/leads/:id             - Update lead
DELETE /api/leads/:id             - Delete lead
GET    /api/leads                 - List leads (with filters)

POST   /api/sequences             - Create sequence
GET    /api/sequences/:id         - Get sequence
POST   /api/sequences/:id/enroll  - Enroll lead

POST   /api/email/send            - Send email
GET    /api/email/templates       - List templates

GET    /api/analytics/track       - Tracking pixel
GET    /api/analytics/click       - Click tracking
GET    /api/analytics/report      - Analytics report
```

## Webhook Events

The system emits these webhook events:

```typescript
{
  'lead.created': { leadId, email, source },
  'lead.updated': { leadId, changes },
  'email.sent': { leadId, messageId, sequenceId },
  'email.opened': { leadId, messageId, timestamp },
  'email.clicked': { leadId, messageId, link },
  'email.bounced': { leadId, messageId, type },
  'sequence.enrolled': { leadId, sequenceId },
  'sequence.completed': { leadId, sequenceId },
  'lead.converted': { leadId, conversionType, value }
}
```

## Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Test email sending (dry run)
npm run test:email -- --dry-run

# Test with sample data
npm run test:sample
```

## Environment Variables

```env
# Gmail OAuth
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-secret
GMAIL_REFRESH_TOKEN=your-refresh-token
GMAIL_REDIRECT_URI=http://localhost:3000/auth/gmail/callback
GMAIL_SENDER_EMAIL=noreply@yourdomain.com

# AI Provider (choose one)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-claude-key

# Google Sheets
GOOGLE_SHEETS_ID=your-spreadsheet-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=service@account.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_KEY="-----BEGIN PRIVATE KEY-----\n..."

# Analytics
WEBHOOK_SECRET=your-hmac-secret

# Optional: Database (if not using Sheets)
DATABASE_URL=postgresql://user:pass@localhost:5432/email_marketing
```

## Migration from Existing Systems

### From nurture-leads-automation
1. Export leads from existing Google Sheet
2. Map custom fields to new schema
3. Import using batch import API
4. Recreate sequences with new builder
5. Update webhook endpoints

### From Clerk Users
1. Use Clerk SDK to fetch all users
2. Map Clerk fields to lead fields
3. Import with source = 'clerk_migration'
4. Set up webhook for new Clerk signups

### From Other Email Platforms
- **Mailchimp**: Use their export API
- **Klaviyo**: CSV export → import
- **ConvertKit**: API migration tool
- **ActiveCampaign**: Direct API sync

## Production Considerations

1. **Rate Limiting**: Gmail API has daily quotas (250 quota units/user/second)
2. **Webhook Security**: Always verify HMAC signatures
3. **Data Privacy**: Implement GDPR compliance (consent tracking included)
4. **Monitoring**: Set up alerts for bounces, low engagement
5. **Backup**: Regular Google Sheets backups or database replication

## Roadmap

- [ ] Database adapter (PostgreSQL, MySQL)
- [ ] SendGrid/Mailgun provider support
- [ ] Visual sequence builder UI
- [ ] Advanced analytics dashboard
- [ ] Shopify/WooCommerce integrations
- [ ] SMS marketing support
- [ ] Predictive send time optimization
- [ ] Advanced personalization with LLMs

## License

MIT

## Support

For issues or questions, please open an issue in the repository.