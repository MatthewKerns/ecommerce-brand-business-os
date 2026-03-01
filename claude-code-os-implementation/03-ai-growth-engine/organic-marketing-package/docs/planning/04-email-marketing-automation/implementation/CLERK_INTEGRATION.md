# Clerk Integration Guide

How to connect Clerk (infinityvaultcards.com auth) to the Email Marketing Package.

## Current State

- ✅ **Scratch-and-win captures emails** → Stored in Clerk
- ✅ **Clerk manages user authentication** for infinityvaultcards.com
- ❌ **Missing**: Automatic sync from Clerk → Email Marketing System

## Integration Options

### Option 1: Webhook-Based (Recommended)

Set up Clerk webhooks to automatically sync new users to the email marketing system.

#### 1. Create Webhook Endpoint

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix';
import { headers } from 'next/headers';
import { WebhookEvent } from '@clerk/nextjs/server';
import { EmailAutomation } from '@organic-marketing/email-automation';

const emailSystem = new EmailAutomation({
  // ... config
});

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET!;

  // Get headers
  const headerPayload = headers();
  const svix_id = headerPayload.get("svix-id");
  const svix_timestamp = headerPayload.get("svix-timestamp");
  const svix_signature = headerPayload.get("svix-signature");

  // Get body
  const body = await req.text();

  // Verify webhook
  const wh = new Webhook(WEBHOOK_SECRET);
  let evt: WebhookEvent;

  try {
    evt = wh.verify(body, {
      "svix-id": svix_id!,
      "svix-timestamp": svix_timestamp!,
      "svix-signature": svix_signature!,
    }) as WebhookEvent;
  } catch (err) {
    return new Response('Invalid signature', { status: 400 });
  }

  // Handle user.created event
  if (evt.type === 'user.created') {
    const { id, email_addresses, first_name, last_name, public_metadata } = evt.data;

    // Create lead in email system
    await emailSystem.leads.create({
      email: email_addresses[0].email_address,
      firstName: first_name,
      lastName: last_name,
      source: 'scratch_and_win',
      customFields: [
        { key: 'clerk_id', value: id, type: 'text' },
        { key: 'game_preference', value: public_metadata.gamePreference, type: 'text' },
        { key: 'prize_code', value: public_metadata.prizeCode, type: 'text' },
        { key: 'prize_type', value: public_metadata.prizeType, type: 'text' },
      ],
      consentGiven: true,
      consentSource: 'scratch_and_win_opt_in',
    });

    // Enroll in welcome sequence
    await emailSystem.enrollInWelcomeSequence(
      email_addresses[0].email_address,
      first_name,
      'scratch_and_win'
    );
  }

  // Handle user.updated event
  if (evt.type === 'user.updated') {
    const { id, email_addresses, first_name, last_name } = evt.data;

    const lead = await emailSystem.leads.getByEmail(email_addresses[0].email_address);
    if (lead) {
      await emailSystem.leads.update(lead.id, {
        firstName: first_name,
        lastName: last_name,
      });
    }
  }

  return new Response('Webhook processed', { status: 200 });
}
```

#### 2. Configure Clerk Dashboard

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Navigate to **Webhooks**
3. Create endpoint: `https://infinityvaultcards.com/api/webhooks/clerk`
4. Select events:
   - `user.created`
   - `user.updated`
   - `user.deleted`
5. Copy signing secret to `CLERK_WEBHOOK_SECRET`

### Option 2: Batch Import (One-Time)

Import all existing Clerk users into the email marketing system.

```typescript
// scripts/import-clerk-users.ts
import { clerkClient } from '@clerk/nextjs';
import { EmailAutomation } from '@organic-marketing/email-automation';

const emailSystem = new EmailAutomation({
  gmail: {
    clientId: process.env.GMAIL_CLIENT_ID!,
    clientSecret: process.env.GMAIL_CLIENT_SECRET!,
    refreshToken: process.env.GMAIL_REFRESH_TOKEN!,
    redirectUri: process.env.GMAIL_REDIRECT_URI!,
    senderEmail: process.env.GMAIL_SENDER_EMAIL!,
  },
  ai: {
    provider: 'gemini',
    apiKey: process.env.GEMINI_API_KEY!,
  },
  storage: {
    type: 'google-sheets',
    config: {
      spreadsheetId: process.env.GOOGLE_SHEETS_ID!,
      credentials: {
        clientEmail: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL!,
        privateKey: process.env.GOOGLE_SERVICE_ACCOUNT_KEY!,
      },
    },
  },
});

async function importClerkUsers() {
  const limit = 100;
  let offset = 0;
  let hasMore = true;

  while (hasMore) {
    const users = await clerkClient.users.getUserList({
      limit,
      offset,
    });

    for (const user of users) {
      // Check if lead already exists
      const existingLead = await emailSystem.leads.getByEmail(
        user.emailAddresses[0].emailAddress
      );

      if (!existingLead) {
        // Create new lead
        const lead = await emailSystem.leads.create({
          email: user.emailAddresses[0].emailAddress,
          firstName: user.firstName || undefined,
          lastName: user.lastName || undefined,
          source: 'clerk_import',
          customFields: [
            { key: 'clerk_id', value: user.id, type: 'text' },
            {
              key: 'game_preference',
              value: user.publicMetadata.gamePreference || 'unknown',
              type: 'text'
            },
            {
              key: 'created_at',
              value: new Date(user.createdAt).toISOString(),
              type: 'date'
            },
          ],
          consentGiven: true,
          consentSource: 'clerk_user_registration',
        });

        console.log(`Imported: ${lead.email}`);
      } else {
        console.log(`Skipped (exists): ${existingLead.email}`);
      }
    }

    hasMore = users.length === limit;
    offset += limit;
  }

  console.log('Import complete!');
}

importClerkUsers().catch(console.error);
```

### Option 3: Real-Time Sync Component

Create a React component that syncs on user login.

```typescript
// components/EmailSyncProvider.tsx
'use client';

import { useUser } from '@clerk/nextjs';
import { useEffect } from 'react';

export function EmailSyncProvider({ children }: { children: React.ReactNode }) {
  const { user, isLoaded } = useUser();

  useEffect(() => {
    if (isLoaded && user) {
      // Sync user to email system
      fetch('/api/email/sync-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clerkId: user.id,
          email: user.emailAddresses[0].emailAddress,
          firstName: user.firstName,
          lastName: user.lastName,
          metadata: user.publicMetadata,
        }),
      }).catch(console.error);
    }
  }, [isLoaded, user]);

  return <>{children}</>;
}
```

## Scratch-and-Win Specific Integration

Since the scratch-and-win flow captures specific data, enhance the integration:

### 1. Capture Prize Data

When a user claims a prize, update their Clerk metadata:

```typescript
// app/claim/success/page.tsx
import { clerkClient } from '@clerk/nextjs';

async function onPrizeClaimed(userId: string, prizeData: any) {
  // Update Clerk user metadata
  await clerkClient.users.updateUserMetadata(userId, {
    publicMetadata: {
      prizeCode: prizeData.code,
      prizeType: prizeData.type, // '10_off', '15_off', '20_off', 'free_shipping'
      prizeClaimed: true,
      prizeClaimedAt: new Date().toISOString(),
      gamePreference: prizeData.gamePreference, // Pokemon, Magic, Yu-Gi-Oh
    },
  });

  // This will trigger the webhook to update the email system
}
```

### 2. Create Prize-Specific Welcome Sequence

```typescript
const prizeWelcomeSequence = await emailSystem.sequences.create({
  name: 'Welcome - Scratch & Win Winners',
  status: 'active',
  triggerType: 'immediate',

  steps: [
    {
      id: 'deliver_prize',
      type: 'email',
      name: 'Deliver Prize Code',
      config: {
        subject: '🎉 {{firstName}}, your {{prizeType}} prize is here!',
        body: `Your lucky spin got you {{prizeDescription}}!

        Your prize code: {{prizeCode}}

        Use it at checkout for instant savings on your favorite {{gamePreference}} products.

        [Shop {{gamePreference}} Now]`,
      },
    },
    {
      id: 'wait_1_day',
      type: 'wait',
      config: { duration: 24 },
    },
    {
      id: 'game_specific_recommendations',
      type: 'email',
      name: 'Game-Specific Product Recommendations',
      config: {
        templateId: 'product_recommendations',
        // Content varies based on gamePreference custom field
      },
    },
  ],

  entryConditions: [
    { field: 'source', operator: 'equals', value: 'scratch_and_win' },
    { field: 'customFields.prize_code', operator: 'exists' },
  ],
});
```

### 3. Track Prize Redemption

When a prize code is used at checkout:

```typescript
// In your checkout handler
async function onCheckout(orderId: string, customerId: string, promoCode?: string) {
  if (promoCode) {
    const lead = await emailSystem.leads.getByCustomField('clerk_id', customerId);
    if (lead) {
      await emailSystem.leads.update(lead.id, {
        customFields: [
          ...lead.customFields,
          { key: 'prize_redeemed', value: true, type: 'boolean' },
          { key: 'first_purchase_date', value: new Date(), type: 'date' },
        ],
        status: 'converted',
      });
    }
  }
}
```

## Environment Variables

Add to your `.env.local`:

```env
# Clerk Webhook
CLERK_WEBHOOK_SECRET=whsec_xxxxx

# Email System (in addition to existing)
GOOGLE_SHEETS_ID=your-leads-spreadsheet-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=service@account.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_KEY="-----BEGIN PRIVATE KEY-----\n..."
```

## Testing the Integration

1. **Test Webhook**:
   ```bash
   npm run test:clerk-webhook
   ```

2. **Test Import**:
   ```bash
   npm run import:clerk-users -- --dry-run
   ```

3. **Verify in Google Sheets**:
   - Check leads are appearing with correct source
   - Verify custom fields contain Clerk data
   - Confirm enrollment in sequences

## Monitoring

Set up alerts for:
- Failed webhook deliveries in Clerk dashboard
- Email bounces for imported leads
- Low engagement rates for scratch-and-win segment

## Next Steps

1. Set up webhook endpoint
2. Run initial import of existing Clerk users
3. Create prize-specific email sequences
4. Test with a few accounts
5. Monitor engagement metrics
6. Optimize email content based on game preferences