# User Journey: Email Marketing

## Overview

The Email Marketing tab is the **relationship automation engine**. It manages the full email lifecycle — capture, welcome, nurture, sell, and retain — through automated sequences that speak in the brand's voice.

This product serves two very different users:

1. **Experienced Marketers (Top 1%)** — Already running email marketing on Klaviyo, Mailchimp, or another platform. They want a single place to manage TikTok content, blog content, and email content. They need to **connect their existing platform** and let the system enhance what they already have.

2. **New to Email** — Haven't set up email marketing yet. They want to automate everything from scratch. They need a **guided walkthrough** where an AI agent asks questions, understands their situation, and builds out a complete email strategy — welcome sequence, nurture sequence, the full playbook.

Both paths end at the same place: a unified email management interface that works alongside TikTok Studio and AEO Optimizer.

---

## Journey Map: First-Time User

### Entry Point

User has completed brand guide setup and clicks "Email Marketing" in the sidebar for the first time.

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Welcome                                   │
│                                                               │
│  Email is where you turn attention into relationships         │
│  and relationships into revenue. Let's get you set up.        │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │                                                  │          │
│  │  🔗 I ALREADY HAVE EMAIL MARKETING               │          │
│  │                                                  │          │
│  │  Connect your existing email platform (Klaviyo,  │          │
│  │  Mailchimp, etc.) and manage everything from     │          │
│  │  one place alongside your TikTok and blog        │          │
│  │  content.                                        │          │
│  │                                                  │          │
│  │  [Connect My Platform]                           │          │
│  │                                                  │          │
│  └────────────────────────────────────────────────┘          │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │                                                  │          │
│  │  🚀 I'M STARTING FROM SCRATCH                    │          │
│  │                                                  │          │
│  │  No email marketing yet? Perfect. Our AI will    │          │
│  │  build your complete email strategy — welcome     │          │
│  │  sequences, nurture flows, and automation —       │          │
│  │  from a single conversation.                     │          │
│  │                                                  │          │
│  │  [Build My Email Strategy]                       │          │
│  │                                                  │          │
│  └────────────────────────────────────────────────┘          │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │                                                  │          │
│  │  💬 NOT SURE? TALK TO AN AGENT                   │          │
│  │                                                  │          │
│  │  Tell our AI about your current situation and    │          │
│  │  it will recommend the right path — whether      │          │
│  │  that's connecting what you have or building      │          │
│  │  something new.                                  │          │
│  │                                                  │          │
│  │  [Chat with Email Strategist]                    │          │
│  │                                                  │          │
│  └────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

### Path A: Connect Existing Email Platform

**Step 1 — Platform Selection**

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Connect Your Platform                     │
│                                                               │
│  Select your email marketing platform:                        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Klaviyo     │  │  Mailchimp   │  │  SendGrid    │     │
│  │   [Connect]   │  │   [Connect]  │  │   [Connect]  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  ActiveCampaign│ │  ConvertKit  │  │  Drip        │     │
│  │   [Connect]   │  │   [Connect]  │  │   [Connect]  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐                                            │
│  │  Other /     │                                            │
│  │  Custom API  │                                            │
│  │  [Configure] │                                            │
│  └──────────────┘                                            │
│                                                               │
│  Don't see yours? We support any platform with an API.        │
│  [Request Integration]                                        │
└─────────────────────────────────────────────────────────────┘
```

**Step 2 — API Connection**

Example for Klaviyo (similar flow for all platforms):

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Connect Klaviyo                           │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │                                                  │          │
│  │  API Key:                                        │          │
│  │  ┌──────────────────────────────────────────┐   │          │
│  │  │ pk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     │   │          │
│  │  └──────────────────────────────────────────┘   │          │
│  │                                                  │          │
│  │  Where to find your API key:                     │          │
│  │  Klaviyo → Settings → API Keys → Create Key     │          │
│  │                                                  │          │
│  │  Permissions needed:                              │          │
│  │  ✅ Read/write access to lists and segments      │          │
│  │  ✅ Read/write access to campaigns and flows     │          │
│  │  ✅ Read access to metrics and analytics         │          │
│  │  ✅ Read/write access to profiles                │          │
│  │                                                  │          │
│  │  [Test Connection]                               │          │
│  │                                                  │          │
│  └────────────────────────────────────────────────┘          │
│                                                               │
│  Your API key is encrypted and stored securely.               │
│  You can revoke access at any time from Settings.             │
└─────────────────────────────────────────────────────────────┘
```

```
User Action: Enters API key and clicks [Test Connection]
System Response: Tests connection, validates permissions

Success:
  ✅ Connection successful
  ✅ 3 lists found (2,450 total contacts)
  ✅ 5 active flows detected
  ✅ 12 campaign templates found

Failure:
  ❌ Connection failed: Invalid API key
  or
  ⚠️ Connection successful but missing permissions:
     ❌ Cannot write to campaigns (read-only key)
     → Please create a key with full read/write access
```

**Step 3 — Import & Analyze Existing Setup**

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Analyzing Your Existing Setup             │
│                                                               │
│  ✅ Connected to Klaviyo                                      │
│                                                               │
│  Importing your current email marketing data...               │
│                                                               │
│  ✅ Lists & Segments: 3 lists, 8 segments (2,450 contacts)  │
│  ✅ Active Flows: 5 automated sequences                      │
│  ⏳ Campaign History: Importing last 90 days...              │
│  ⏳ Performance Data: Analyzing open rates, clicks...        │
│  ⏳ Templates: Scanning for brand consistency...             │
│                                                               │
│  ──────────────────────────────────────────────────           │
│                                                               │
│  While this runs, tell me about your goals:                   │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │  💬 AI: "I can see you've already got a solid    │          │
│  │  email operation running. What made you look      │          │
│  │  for a unified platform?                          │          │
│  │                                                  │          │
│  │  Are you primarily looking to:                    │          │
│  │  • Get all your content (TikTok, blog, email)    │          │
│  │    managed in one place?                          │          │
│  │  • Improve your email content with AI?            │          │
│  │  • Better coordinate email with your TikTok       │          │
│  │    and blog content strategy?                     │          │
│  │  • Something else?"                               │          │
│  │                                                  │          │
│  │  ┌──────────────────────────────────────────┐   │          │
│  │  │ Type your response...            [Send]  │   │          │
│  │  └──────────────────────────────────────────┘   │          │
│  └────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

**Step 4 — Existing Setup Review**

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Your Current Setup                        │
│                                                               │
│  Here's what I found in your Klaviyo account:                │
│                                                               │
│  ┌─ LISTS & CONTACTS ──────────────────────────────┐       │
│  │                                                    │       │
│  │  Total Contacts: 2,450                             │       │
│  │  Active: 2,180 (89%)                              │       │
│  │  Unsubscribed: 270 (11%)                          │       │
│  │                                                    │       │
│  │  Main List: "Newsletter" — 1,890 contacts         │       │
│  │  List 2: "Customers" — 430 contacts               │       │
│  │  List 3: "VIP" — 130 contacts                     │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ ACTIVE FLOWS ──────────────────────────────────┐       │
│  │                                                    │       │
│  │  1. Welcome Series (3 emails)                     │       │
│  │     Open rate: 52% | Click rate: 11%              │       │
│  │     ⚠️ Below potential — brand voice mismatch     │       │
│  │                                                    │       │
│  │  2. Abandoned Cart (2 emails)                     │       │
│  │     Open rate: 41% | Recovery rate: 8%            │       │
│  │     ✅ Performing well                             │       │
│  │                                                    │       │
│  │  3. Post-Purchase (2 emails)                      │       │
│  │     Open rate: 48% | Review rate: 3%              │       │
│  │     ⚠️ Missing cross-sell opportunity              │       │
│  │                                                    │       │
│  │  4. Win-Back (1 email)                            │       │
│  │     Open rate: 18%                                │       │
│  │     ❌ Underperforming — needs rewrite            │       │
│  │                                                    │       │
│  │  5. Browse Abandonment (1 email)                  │       │
│  │     Open rate: 35% | Click rate: 6%              │       │
│  │     ✅ Average performance                         │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ AI RECOMMENDATIONS ────────────────────────────┐       │
│  │                                                    │       │
│  │  Based on your brand guide and current setup:      │       │
│  │                                                    │       │
│  │  1. 🔴 Welcome Series needs a brand voice rewrite │       │
│  │     Your brand guide says [voice characteristics]  │       │
│  │     but your welcome emails sound generic.         │       │
│  │     Estimated impact: +15% open rate               │       │
│  │                                                    │       │
│  │  2. 🟡 Missing nurture sequence                    │       │
│  │     You jump from welcome to nothing. A 4-week     │       │
│  │     nurture flow could convert 8-12% more leads.   │       │
│  │                                                    │       │
│  │  3. 🟡 Post-purchase is too short                  │       │
│  │     Add a cross-sell email at day 14 and a         │       │
│  │     review request at day 30.                      │       │
│  │                                                    │       │
│  │  4. 🔴 Win-back needs complete rewrite             │       │
│  │     Single email at 18% open rate = not working.   │       │
│  │     Recommend 3-email win-back with escalating     │       │
│  │     offers.                                        │       │
│  │                                                    │       │
│  │  [Fix These Issues Now]  [I'll Handle It Later]   │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  [Go to Email Dashboard]                                      │
└─────────────────────────────────────────────────────────────┘
```

**Step 5 — Fix with AI (if user chooses)**

When user clicks [Fix These Issues Now]:

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — AI Optimization Queue                     │
│                                                               │
│  I'll generate improved versions of your underperforming      │
│  emails. You review and approve before anything changes       │
│  in your Klaviyo account.                                     │
│                                                               │
│  ┌─ QUEUE ──────────────────────────────────────────┐       │
│  │                                                    │       │
│  │  ⏳ Rewriting Welcome Series (3 emails)           │       │
│  │     Using brand voice: [characteristics]           │       │
│  │     Keeping: Your existing timing and triggers    │       │
│  │     Changing: Subject lines, body copy, CTAs      │       │
│  │                                                    │       │
│  │  ⏳ Creating Nurture Sequence (4 emails)          │       │
│  │     New automated flow for non-purchasers          │       │
│  │     Educational content → Social proof → Offer    │       │
│  │                                                    │       │
│  │  ⏳ Extending Post-Purchase (adding 2 emails)     │       │
│  │     Day 14: Cross-sell recommendation             │       │
│  │     Day 30: Review request                        │       │
│  │                                                    │       │
│  │  ⏳ Rebuilding Win-Back (3 emails)                │       │
│  │     "We miss you" → Value reminder → Final offer  │       │
│  │                                                    │       │
│  │  Estimated time: 3-5 minutes                      │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  Each email will be ready for your review before              │
│  syncing back to Klaviyo.                                     │
└─────────────────────────────────────────────────────────────┘
```

---

### Path B: Build From Scratch

**Step 1 — AI Strategy Conversation**

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Let's Build Your Email Strategy           │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │  💬 AI: "I've read your brand guide. Let me      │          │
│  │  ask a few questions so I can build an email      │          │
│  │  strategy that actually fits your business.       │          │
│  │                                                  │          │
│  │  First — how are people currently finding          │          │
│  │  your brand? TikTok, search, word of mouth,      │          │
│  │  paid ads? What's driving the most traffic        │          │
│  │  to your website right now?"                      │          │
│  └────────────────────────────────────────────────┘          │
│                                                               │
│  ┌──────────────────────────────────────────────────┐        │
│  │ Type your response...                     [Send] │        │
│  └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**Step 2 — Guided Conversation (5-10 minutes)**

The AI agent walks through these topics, adapting based on answers:

```
AI: "Got it. So TikTok is your main traffic driver.
     That's perfect — TikTok → email capture → automated
     nurture is one of the highest-converting funnels
     in e-commerce right now.

     Next question: When someone visits your website
     from TikTok, what happens? Do you have an email
     capture in place — pop-up, discount offer, anything?"

User: "No, nothing. People just browse and leave."

AI: "That's actually good news — it means there's a huge
     untapped opportunity. Every visitor who leaves without
     giving you their email is a missed relationship.

     Here's what I recommend for capture:
     A gamified pop-up — scratch-to-win or spin-to-win —
     that offers a discount in exchange for their email.
     These convert 2-3x better than standard pop-ups because
     they feel like a game, not an interruption.

     Does that sound good, or do you prefer a simpler
     approach like a straight discount offer?"

User: "Scratch to win sounds cool, let's do that."

AI: "Great choice. Now let me ask about the post-capture
     strategy. Once someone gives you their email, what
     should they experience?

     I'm going to recommend a 4-sequence system:

     1. Welcome Sequence (Days 0-7)
        Deliver the prize, tell your brand story,
        build trust, convert to first purchase.

     2. Nurture Sequence (Weeks 2-5)
        For people who didn't buy yet. Educational
        content, social proof, soft offers.

     3. Post-Purchase (triggered on first order)
        Setup tips, review request, cross-sell.

     4. Win-Back (triggered on 30+ days inactive)
        Re-engagement with escalating offers.

     This covers the entire customer lifecycle
     automatically. You set it up once and it runs
     forever. Sound right?"

User: "Yes, that's exactly what I need."

AI: "Perfect. Last few questions:

     What's a reasonable discount for new subscribers?
     Most brands in your space do 10-15% off first order.

     And what email platform do you want to use?
     I recommend Klaviyo for e-commerce — it integrates
     with Shopify and has the best segmentation.
     But we support others too."

User: "10% off works. And yeah, let's use Klaviyo."

AI: "All set. I'm going to generate your complete email
     strategy now — all 4 sequences, fully written in
     your brand voice, with subject lines, body copy,
     and timing built in.

     Give me about 3 minutes."
```

**Step 3 — Strategy Generated**

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Your Strategy is Ready                    │
│                                                               │
│  I've built a complete email automation system for you.       │
│                                                               │
│  ┌─ CAPTURE: Scratch-to-Win Pop-Up ─────────────────┐      │
│  │                                                    │      │
│  │  Trigger: After 5 seconds on site                  │      │
│  │  Prize distribution:                               │      │
│  │  • 40%: 10% off first order                       │      │
│  │  • 25%: 15% off first order                       │      │
│  │  • 20%: Free shipping                             │      │
│  │  • 10%: 20% off first order                       │      │
│  │  • 5%: Mystery bonus gift                         │      │
│  │                                                    │      │
│  │  Fields: Email (required), First name (optional),  │      │
│  │  "[What do you collect/use?]" dropdown            │      │
│  │  (for segmentation)                                │      │
│  │                                          [Edit]   │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ┌─ SEQUENCE 1: Welcome (4 emails, Days 0-7) ──────┐      │
│  │                                                    │      │
│  │  📧 Day 0: "Your Prize is Here"                   │      │
│  │     Deliver discount, brand intro, excitement     │      │
│  │                                                    │      │
│  │  📧 Day 2: "The Story Behind [Brand Name]"       │      │
│  │     Brand origin, values, differentiation          │      │
│  │                                                    │      │
│  │  📧 Day 4: "What [Audience] Need to Know"        │      │
│  │     Educational value, authority building          │      │
│  │                                                    │      │
│  │  📧 Day 7: "Your Prize Expires Tomorrow"         │      │
│  │     Urgency + social proof + final CTA            │      │
│  │                                                    │      │
│  │  [Review All Emails]                [Edit]        │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ┌─ SEQUENCE 2: Nurture (4 emails, Weeks 2-5) ─────┐      │
│  │                                                    │      │
│  │  📧 Week 2: Educational content + soft product    │      │
│  │  📧 Week 3: Customer reviews + social proof       │      │
│  │  📧 Week 4: Community spotlight / story           │      │
│  │  📧 Week 5: Special offer for non-purchasers     │      │
│  │                                                    │      │
│  │  [Review All Emails]                [Edit]        │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ┌─ SEQUENCE 3: Post-Purchase (4 emails) ───────────┐      │
│  │                                                    │      │
│  │  📧 Immediate: Order confirmation + excitement    │      │
│  │  📧 Day 3: Setup/care tips                        │      │
│  │  📧 Day 14: Review request                        │      │
│  │  📧 Day 30: Cross-sell recommendation             │      │
│  │                                                    │      │
│  │  [Review All Emails]                [Edit]        │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  ┌─ SEQUENCE 4: Win-Back (3 emails) ────────────────┐      │
│  │                                                    │      │
│  │  📧 Day 30 inactive: "We miss you" + value       │      │
│  │  📧 Day 37 inactive: Social proof + soft offer    │      │
│  │  📧 Day 44 inactive: Final offer + urgency       │      │
│  │                                                    │      │
│  │  [Review All Emails]                [Edit]        │      │
│  └────────────────────────────────────────────────────┘      │
│                                                               │
│  [Review Everything Before Activating]                        │
│  [Connect Klaviyo & Deploy]                                   │
│  [Chat with Strategist About Changes]                         │
└─────────────────────────────────────────────────────────────┘
```

**Step 4 — Individual Email Review**

When user clicks [Review All Emails] on any sequence:

```
┌─────────────────────────────────────────────────────────────┐
│  WELCOME SEQUENCE — Email 1 of 4                             │
│                                                               │
│  ┌─ PREVIEW ────────────────────────────────────────┐       │
│  │                                                    │       │
│  │  Subject: "You just won [Prize]. Here's your code."│       │
│  │  Preview: "Your [brand] journey starts now."       │       │
│  │  Send: Immediately after signup                    │       │
│  │                                                    │       │
│  │  ────────────────────────────────────────────      │       │
│  │                                                    │       │
│  │  [Rendered email preview showing full layout,      │       │
│  │   header image, body copy, CTA button, footer]     │       │
│  │                                                    │       │
│  │  ────────────────────────────────────────────      │       │
│  │                                                    │       │
│  │  BRAND CHECK:                                      │       │
│  │  ✅ Voice: Matches brand guide                     │       │
│  │  ✅ Language: Uses preferred terms                 │       │
│  │  ✅ Tone: Welcoming + confident (on brand)        │       │
│  │  ✅ CTA: Clear and aligned with brand positioning │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  [Approve]  [Edit Subject Line]  [Edit Body]                 │
│  [Rewrite with Different Tone]  [◀ Prev] [Next ▶]          │
└─────────────────────────────────────────────────────────────┘
```

**Step 5 — Platform Connection & Deployment**

Once all emails are reviewed and approved:

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Connect & Deploy                          │
│                                                               │
│  All emails are reviewed and approved. Time to go live.       │
│                                                               │
│  Step 1: Connect your email platform                          │
│  ┌────────────────────────────────────────────────┐          │
│  │  Platform: Klaviyo                               │          │
│  │  API Key: [________________________]            │          │
│  │  [Test Connection]                               │          │
│  └────────────────────────────────────────────────┘          │
│                                                               │
│  Step 2: What we'll create in your Klaviyo account            │
│  ┌────────────────────────────────────────────────┐          │
│  │                                                  │          │
│  │  ✅ 4 automated flows (15 total emails)          │          │
│  │  ✅ Email templates matching your brand          │          │
│  │  ✅ Trigger rules and timing                     │          │
│  │  ✅ Segmentation rules                           │          │
│  │                                                  │          │
│  │  ⚠️ Nothing will send until you activate each     │          │
│  │     flow in Klaviyo. We set them up as drafts.   │          │
│  └────────────────────────────────────────────────┘          │
│                                                               │
│  [Deploy to Klaviyo]                                          │
│                                                               │
│  Or: [Export as Templates] (deploy manually)                  │
└─────────────────────────────────────────────────────────────┘
```

**Step 6 — Deployment Complete**

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — You're Live                               │
│                                                               │
│  ✅ All sequences deployed to Klaviyo                         │
│                                                               │
│  Status:                                                      │
│  ✅ Welcome Sequence: Active (will send on new signups)      │
│  ✅ Nurture Sequence: Active (triggers after welcome ends)   │
│  ✅ Post-Purchase: Active (triggers on first order)          │
│  ✅ Win-Back: Active (triggers on 30-day inactivity)         │
│                                                               │
│  Next steps:                                                  │
│  1. Set up your email capture (scratch-to-win) on your       │
│     website → [Setup Guide]                                   │
│  2. Add TikTok bio link to email capture page                │
│  3. Monitor performance from this dashboard                   │
│                                                               │
│  [Go to Email Dashboard]                                      │
└─────────────────────────────────────────────────────────────┘
```

---

### Path C: Chat with Email Strategist (Hybrid)

For users who aren't sure which path to take:

```
AI: "Tell me about your current email marketing situation.
     Do you have any email setup at all — even a basic
     newsletter? And what platform are you on?"

User: "I have Klaviyo set up with a basic welcome email
       but it's pretty generic. I just never had time
       to build it out properly."

AI: "Got it — so you have infrastructure but need strategy.
     That's actually the best starting point.

     Here's what I recommend:

     1. Connect your Klaviyo account so I can see what
        you've got (that basic welcome email, your list
        size, any segments you've set up)

     2. I'll analyze what's there and build on it —
        rewrite your welcome email in your brand voice,
        then add the nurture, post-purchase, and win-back
        sequences you're missing

     3. Everything syncs back to your existing Klaviyo
        account — no migration needed

     Want to start by connecting your Klaviyo?"

User: "Yeah, let's do that."

System: Routes to Path A, Step 1 (Platform Selection)
```

The AI agent adapts the path based on the conversation, blending elements of Path A and Path B as needed.

---

## Journey Map: Returning User — Email Dashboard

### Dashboard Entry

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Dashboard                                 │
│                                                               │
│  Connected: Klaviyo • 2,450 contacts • 4 active flows       │
│                                                               │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │  Emails  │  Open    │  Click   │  Revenue │              │
│  │   Sent   │  Rate    │  Rate    │ (30 day) │              │
│  │  1,245   │  48.2%   │  12.8%   │  $3,890  │              │
│  │  ↑ 320   │  ↑ 3.1%  │  ↑ 1.2%  │  ↑ 22%  │              │
│  └──────────┴──────────┴──────────┴──────────┘              │
│                                                               │
│  SEQUENCE PERFORMANCE                                         │
│  ┌────────────────────────────────────────────────────┐     │
│  │                                                      │     │
│  │  Welcome    ████████████████████ 65% open  ✅       │     │
│  │  Nurture    ██████████████░░░░░░ 42% open  ✅       │     │
│  │  Post-Purch ████████████████░░░░ 52% open  ✅       │     │
│  │  Win-Back   ████████░░░░░░░░░░░░ 24% open  ⚠️      │     │
│  │                                                      │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  NEEDS YOUR ATTENTION                                         │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ⚡ 2 email drafts ready for review                 │     │
│  │  ⚡ Win-back sequence underperforming — AI has      │     │
│  │     generated an A/B test variant                   │     │
│  │  ⚡ 45 new subscribers this week (+12% vs last)    │     │
│  │  💡 AI suggestion: Add a seasonal campaign for     │     │
│  │     [upcoming event/holiday]                        │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  [Review Drafts]  [View Sequences]  [Create Campaign]        │
│  [View Subscribers]  [A/B Tests]                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Returning Workflow: Visual Sequence Builder

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL SEQUENCES — Visual Builder                            │
│                                                               │
│  Sequence: Welcome Series                                     │
│  Status: Active • 450 currently enrolled                     │
│                                                               │
│     [Signup Trigger]                                          │
│          ↓                                                    │
│     ┌──────────────────────┐                                 │
│     │ 📧 "Your Prize"      │  Open: 72%  Click: 18%        │
│     │    Day 0              │                                 │
│     └──────────┬───────────┘                                 │
│                ↓                                              │
│          [Wait 2 Days]                                        │
│                ↓                                              │
│     ┌──────────────────────┐                                 │
│     │ 📧 "The Story Behind"│  Open: 61%  Click: 14%        │
│     │    Day 2              │                                 │
│     └──────────┬───────────┘                                 │
│                ↓                                              │
│          [Wait 2 Days]                                        │
│                ↓                                              │
│     ┌──────────┴───────────┐                                 │
│     │    Opened Email 2?    │                                 │
│     ├─── YES ──┬── NO ─────┤                                 │
│     ↓          ↓            ↓                                 │
│  ┌────────┐  ┌──────────────┐                                │
│  │📧 Tips │  │📧 Re-engage  │                                │
│  │ Day 4  │  │  Day 5       │                                │
│  │ 58%    │  │  38%         │                                │
│  └───┬────┘  └──────┬───────┘                                │
│      ↓               ↓                                       │
│  [Wait 3 Days]  [Wait 2 Days]                                │
│      ↓               ↓                                       │
│  ┌────────┐  ┌──────────────┐                                │
│  │📧 Last │  │📧 Final Offer│                                │
│  │ Chance  │  │  Day 7       │                                │
│  │ Day 7  │  │  35%         │                                │
│  └────────┘  └──────────────┘                                │
│                                                               │
│  [+ Add Step]  [Edit Step (click any node)]                  │
│  [Test Sequence]  [View Live Enrollments]                     │
│  [Duplicate Sequence]  [A/B Test a Step]                     │
└─────────────────────────────────────────────────────────────┘
```

---

### Returning Workflow: Create Campaign

For one-time campaigns (promotions, announcements, seasonal):

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — New Campaign                              │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │  🎯 AI-RECOMMENDED CAMPAIGN                       │        │
│  │                                                   │        │
│  │  Based on your calendar and audience activity:     │        │
│  │                                                   │        │
│  │  "[Seasonal/Event] Campaign"                      │        │
│  │  Send to: Active subscribers who haven't          │        │
│  │  purchased in 14+ days (890 contacts)             │        │
│  │  Best send time: Tuesday 10 AM (your audience's   │        │
│  │  highest open rate window)                        │        │
│  │                                                   │        │
│  │  [Generate This Campaign]                         │        │
│  └─────────────────────────────────────────────────┘        │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │  ✏️ CUSTOM CAMPAIGN                               │        │
│  │                                                   │        │
│  │  Campaign Name: [________________________]       │        │
│  │  Type: ○ Promotional  ○ Announcement  ○ Content  │        │
│  │  Audience: [All Subscribers ▼]                    │        │
│  │  Topic: [________________________]               │        │
│  │                                                   │        │
│  │  [Generate Email]                                 │        │
│  └─────────────────────────────────────────────────┘        │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │  💬 BRAINSTORM WITH AI                            │        │
│  │                                                   │        │
│  │  "I want to run a campaign but I'm not sure       │        │
│  │   what to send. Help me figure it out."           │        │
│  │                                                   │        │
│  │  [Start Conversation]                             │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

### Returning Workflow: Subscriber Management

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Subscribers                               │
│                                                               │
│  Total: 2,450 | Active: 2,180 | New this week: 45           │
│                                                               │
│  Search: [________________________]  Filter: [All ▼]        │
│                                                               │
│  ┌────────┬──────────────────┬─────────┬────────┬────────┐ │
│  │ Status │ Email            │ Source  │ Tags   │ Joined │ │
│  ├────────┼──────────────────┼─────────┼────────┼────────┤ │
│  │ ● Active│ jane@example.com│ TikTok │ VIP,   │ 2d ago │ │
│  │        │                  │        │ Customer│        │ │
│  ├────────┼──────────────────┼─────────┼────────┼────────┤ │
│  │ ● Active│ mark@example.com│ Website│ Lead   │ 5d ago │ │
│  ├────────┼──────────────────┼─────────┼────────┼────────┤ │
│  │ ○ Cold │ old@example.com  │ Import │ Cold   │ 90d ago│ │
│  └────────┴──────────────────┴─────────┴────────┴────────┘ │
│                                                               │
│  Segments:                                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  VIP Customers: 130 contacts                        │     │
│  │  Active Leads (no purchase): 1,620 contacts         │     │
│  │  Cold (no opens in 30 days): 270 contacts          │     │
│  │  [Segment by Product Interest]: Available           │     │
│  │                                                      │     │
│  │  [+ Create Segment]  [Import Subscribers]           │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  [Export List]  [Sync with Klaviyo]  [Clean Inactive]        │
└─────────────────────────────────────────────────────────────┘
```

---

## Automation Management

### Sequence Automation Controls

Each email sequence has its own automation panel, plus a global control view:

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Automation Settings                       │
│                                                               │
│  SEQUENCE STATUS                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Welcome Sequence:     [ON ●───] Active             │     │
│  │  Nurture Sequence:     [ON ●───] Active             │     │
│  │  Post-Purchase:        [ON ●───] Active             │     │
│  │  Win-Back:             [───○ OFF] Paused            │     │
│  │  ──────────────────────────────────                 │     │
│  │  Platform Sync:        [ON ●───] Real-time          │     │
│  │  A/B Testing:          [ON ●───] Active on 2 tests  │     │
│  │  List Hygiene:         [ON ●───] Weekly auto-clean  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  SENDING MODE                                                 │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Current: Manual Review for New Emails              │     │
│  │                                                      │     │
│  │  Your approval stats (last 60 days):                │     │
│  │  • 18 emails reviewed (new and revised)             │     │
│  │  • 15 approved without edits (83.3%)                │     │
│  │  • 3 edited before approval                         │     │
│  │  • 0 rejected                                       │     │
│  │                                                      │     │
│  │  ⚡ Smart Autopilot eligible for:                    │     │
│  │  ✅ Welcome Sequence (91% no-edit rate)             │     │
│  │  ✅ Post-Purchase (88% no-edit rate)                │     │
│  │  ⚠️ Nurture (72% — needs improvement)              │     │
│  │  ⚠️ Win-Back (too few data points)                 │     │
│  │                                                      │     │
│  │  ○ Manual Review (current)                          │     │
│  │    All new and revised emails require approval.     │     │
│  │                                                      │     │
│  │  ○ Smart Autopilot (per sequence)                   │     │
│  │    Auto-send sequence emails that pass:             │     │
│  │    ✅ Brand voice match > [90% ▼]                   │     │
│  │    ✅ Spam score < [2.0 ▼]                          │     │
│  │    ✅ No brand language violations                   │     │
│  │    ✅ Subject line quality > [80 ▼]                 │     │
│  │    Campaigns always require manual approval.        │     │
│  │                                                      │     │
│  │  ○ Full Autopilot (earned per sequence)             │     │
│  │    Sequence emails auto-send. Campaigns still       │     │
│  │    require approval. Daily digest of sends.         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  FREQUENCY CAPS                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Max emails per subscriber per day: [1 ▼]          │     │
│  │  Max emails per subscriber per week: [3 ▼]         │     │
│  │  Priority order (when capped):                      │     │
│  │  1. Transactional (order confirmations) — always   │     │
│  │  2. Active sequence step — high priority            │     │
│  │  3. Campaign — medium priority                      │     │
│  │  4. Win-back — low priority (can wait)             │     │
│  │                                                      │     │
│  │  ⚠️ If a subscriber would receive 2 emails in one  │     │
│  │  day, the lower-priority email is delayed 24h.     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  SAFETY THRESHOLDS                                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Auto-pause a sequence if:                          │     │
│  │  ☑️ Unsubscribe rate exceeds [0.5% ▼] in a day    │     │
│  │  ☑️ Bounce rate exceeds [3% ▼]                     │     │
│  │  ☑️ Spam complaints exceed [0.1% ▼]                │     │
│  │  ☑️ Open rate drops below [15% ▼] for 3 sends     │     │
│  │                                                      │     │
│  │  When auto-paused:                                  │     │
│  │  → Sequence stops sending new emails               │     │
│  │  → AI analyzes the problem and suggests fixes      │     │
│  │  → User receives alert with diagnosis + fix options│     │
│  │  → Subscribers in the sequence are held, not lost  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  QUICK ACTIONS                                                │
│  [Pause All Sequences]  [Pause Only Campaigns]               │
│  [View Automation Logs]  [Go to Command Center]              │
└─────────────────────────────────────────────────────────────┘
```

### Progressive Trust for Email Sending

Email has the most nuanced trust model because sends are irreversible and directly impact subscriber relationships:

```
TRUST LEVELS — EMAIL:

Level 1 — Manual Review (Default)
  Requirement: New setup, no history
  Behavior: All new emails and revisions require approval
  Existing approved sequences run automatically (they were
  reviewed during setup). Only NEW or CHANGED emails need review.
  Threshold to advance: 15+ email approvals, <15% edit rate

Level 2 — Smart Autopilot (Per Sequence)
  Requirement: 15+ approvals per sequence, <15% edit rate
  Earned independently per sequence — your Welcome Sequence
  can reach Smart Autopilot while Win-Back stays Manual.
  Behavior: Auto-send if brand check + spam check + quality pass
  One-time campaigns ALWAYS require manual approval at this level.
  System prompt: "Your Welcome Sequence emails have been
  approved 16 times with only 1 edit. Enable Smart Autopilot?
  New emails meeting quality thresholds will auto-activate.
  Below-threshold emails go to your review queue."

Level 3 — Full Autopilot (Per Sequence)
  Requirement: 30+ auto-sent without manual override
  Behavior: All sequence emails auto-activate
  Campaigns still require manual send confirmation
  (Campaigns are one-shot — too risky for full autopilot)
  Notification: Weekly digest of sends, performance, and
  any safety threshold triggers

Trust revocation triggers (EMAIL-SPECIFIC):
  • Unsubscribe rate spikes above threshold → immediate pause
  • Bounce rate exceeds threshold → drops to Manual
  • User manually edits 3+ auto-sent emails → drops one level
  • Spam complaint filed → drops to Manual immediately
  • Open rate decline for 3 consecutive sends → warning + review

IMPORTANT: One-time campaigns never reach Full Autopilot.
They always require human confirmation before sending.
This is a safety design choice, not a trust limitation.
```

### Error Recovery & Self-Healing

```
┌─────────────────────────────────────────────────────────────┐
│  AUTOMATION HEALTH — Email Marketing                         │
│                                                               │
│  Platform: Klaviyo • Status: ● Connected                     │
│  Last sync: 2 minutes ago                                     │
│                                                               │
│  Recent Events:                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ✅ 10:15 AM — Welcome email sent to new subscriber│     │
│  │  ✅ 10:00 AM — Platform sync completed (12 new)   │     │
│  │  🔄 9:45 AM — Klaviyo API rate limit hit,          │     │
│  │     auto-throttled, resuming in 60s                │     │
│  │  ✅ 9:46 AM — Throttle released, sends resumed    │     │
│  │  ✅ 9:30 AM — A/B test concluded: Variant B wins  │     │
│  │  ⚠️ 8:00 AM — 2 bounces detected, contacts cleaned│     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  Error Recovery Policy:                                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Platform Disconnection:                            │     │
│  │  → Auto-retry: 4 attempts (exponential backoff)   │     │
│  │  → During disconnect: Queue unsent emails          │     │
│  │  → Auto-reconnect attempts every 30 min for 24h   │     │
│  │  → After 24h: Alert user, pause all sends         │     │
│  │  → Queued emails send in order once reconnected   │     │
│  │                                                      │     │
│  │  Failed Send:                                       │     │
│  │  → Auto-retry: 3 attempts over 30 minutes         │     │
│  │  → If content rejected by platform: flag for       │     │
│  │    review (may contain spam-trigger words)         │     │
│  │  → If rate limited: auto-throttle and resume       │     │
│  │                                                      │     │
│  │  Bounce Handling:                                   │     │
│  │  → Hard bounce: Auto-remove from active lists     │     │
│  │  → Soft bounce: Retry 3x, then suppress for 30d  │     │
│  │  → Bounce rate alert if >3% in any batch          │     │
│  │                                                      │     │
│  │  Safety Threshold Breach:                           │     │
│  │  → Auto-pause the affected sequence immediately   │     │
│  │  → AI diagnoses the problem (which email, why)    │     │
│  │  → Generates fix suggestion (new subject line,     │     │
│  │    revised copy, changed timing)                   │     │
│  │  → User reviews diagnosis + approves fix           │     │
│  │  → Sequence resumes with fix applied               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  [View Full Logs]  [Configure Recovery Policy]               │
│  [Test Platform Connection]  [Send Test Email]               │
└─────────────────────────────────────────────────────────────┘
```

### Sequence Pause & Resume

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL — Pause Sequence                                      │
│                                                               │
│  Pausing: Welcome Sequence                                    │
│  Currently enrolled: 45 subscribers mid-sequence              │
│                                                               │
│  What happens to enrolled subscribers?                         │
│  ○ Hold in place — resume from where they stopped            │
│  ○ Complete current step, then hold                          │
│  ○ Remove from sequence (they won't receive remaining        │
│    emails even after resume)                                  │
│                                                               │
│  Duration:                                                    │
│  ○ Until I resume manually                                    │
│  ○ Pause for [7 ▼] days, then auto-resume                   │
│  ○ Pause until [date picker]                                 │
│                                                               │
│  ⚠️ New signups during pause will be queued and enrolled     │
│  when the sequence resumes. No subscribers are lost.          │
│                                                               │
│  [Confirm Pause]  [Cancel]                                    │
└─────────────────────────────────────────────────────────────┘
```

### Bulk Operations

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL — Bulk Actions                                        │
│                                                               │
│  Select sequences:                                            │
│  ☑️ Welcome  ☑️ Nurture  ☑️ Post-Purchase  ☐ Win-Back       │
│                                                               │
│  Action:                                                      │
│  ┌────────────────────────────────────────────────────┐     │
│  │  [Pause All Selected]                               │     │
│  │  [Resume All Selected]                              │     │
│  │  [Set All to Manual Review]                         │     │
│  │  [Rewrite All in Brand Voice] (re-generates copy   │     │
│  │   for all emails using current brand guide)         │     │
│  │  [A/B Test Subject Lines] (generates variant       │     │
│  │   subject lines for all emails in selected seqs)   │     │
│  │  [Export All Templates]                             │     │
│  │  [Sync All to Platform Now]                         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  [Confirm Action]  [Cancel]                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Edge Cases

### Platform Disconnected

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ CONNECTION LOST — Klaviyo                                 │
│                                                               │
│  Your Klaviyo API key has expired or been revoked.            │
│  Email sequences continue to run in Klaviyo (they're         │
│  independent), but we can't sync data or push updates.       │
│                                                               │
│  Impact:                                                      │
│  • Performance data is stale (last sync: 2 days ago)        │
│  • New email drafts can't be deployed                        │
│  • Subscriber data won't update                              │
│                                                               │
│  [Reconnect Now]  [Generate New API Key (guide)]             │
└─────────────────────────────────────────────────────────────┘
```

### Switching Email Platforms

```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL MARKETING — Switch Platform                           │
│                                                               │
│  Current: Klaviyo (2,450 contacts, 4 active flows)           │
│  Switching to: Mailchimp                                      │
│                                                               │
│  What will migrate:                                           │
│  ✅ All email templates and copy                              │
│  ✅ Sequence logic and timing                                 │
│  ⚠️ Subscriber list (you'll need to export/import)           │
│  ⚠️ Historical performance data stays in Klaviyo             │
│                                                               │
│  Your existing Klaviyo flows will continue running            │
│  until you deactivate them. We recommend:                     │
│  1. Set up everything in Mailchimp first                     │
│  2. Test the new sequences                                    │
│  3. Migrate subscribers                                       │
│  4. Then deactivate Klaviyo flows                            │
│                                                               │
│  [Start Migration]  [Cancel]                                  │
└─────────────────────────────────────────────────────────────┘
```

### High Unsubscribe Rate Alert

```
┌─────────────────────────────────────────────────────────────┐
│  🔴 ALERT — Unsubscribe Rate Spike                           │
│                                                               │
│  Your unsubscribe rate jumped to 1.2% this week              │
│  (normal: <0.3%)                                              │
│                                                               │
│  Affected: "Nurture Sequence — Email 3"                      │
│  (the promotional email)                                      │
│                                                               │
│  AI Analysis: "This email's promotional tone is a sharp       │
│  contrast from the educational tone of emails 1-2.           │
│  Subscribers who signed up for value are rejecting            │
│  the sudden sales pitch. Consider softening the offer        │
│  or adding more value before the ask."                        │
│                                                               │
│  [Pause This Email]  [Generate Softer Version]               │
│  [View Detailed Analytics]                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## How This Tab Connects to Others

| Connected Tab | How Email Marketing Feeds/Receives |
|--------------|-----------------------------------|
| **Brand Guide** | Brand voice, language rules, and positioning shape every email. Email templates are regenerated when brand guide updates. |
| **TikTok Studio** | TikTok CTAs ("link in bio") drive email captures. TikTok content themes can be repurposed into email content. High-performing TikTok topics become email subject lines. |
| **AEO Optimizer** | New blog posts can be distributed via email campaigns. Blog subscriber captures feed the email list. Educational blog content can be excerpted for nurture emails. |
| **Content Calendar** | All email campaigns and sequence emails appear in the unified calendar alongside TikTok and blog content. |
| **Analytics** | Email metrics (open rate, click rate, revenue) feed the unified dashboard. Cross-channel attribution tracks TikTok → email → purchase and blog → email → purchase journeys. |

---

## Data Model

```typescript
interface EmailPlatformConnection {
  id: string;
  workspaceId: string;
  platform: 'klaviyo' | 'mailchimp' | 'sendgrid' | 'activecampaign' | 'convertkit' | 'drip' | 'custom';
  apiKey: string; // encrypted
  connectionStatus: 'connected' | 'disconnected' | 'expired';
  lastSyncAt: Date;
  syncConfig: {
    autoSync: boolean;
    syncFrequency: 'realtime' | 'hourly' | 'daily';
    syncDirections: ('push' | 'pull')[];
  };
  importedData: {
    lists: number;
    contacts: number;
    flows: number;
    templates: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

interface EmailSequence {
  id: string;
  workspaceId: string;
  platformConnectionId: string;
  externalId?: string; // ID in the connected platform
  name: string;
  type: 'welcome' | 'nurture' | 'post_purchase' | 'win_back' | 'custom';
  status: 'draft' | 'active' | 'paused' | 'completed';
  trigger: {
    type: 'signup' | 'purchase' | 'tag_added' | 'inactivity' | 'custom';
    config: Record<string, any>;
  };
  steps: SequenceStep[];
  metrics: {
    enrolled: number;
    completed: number;
    converted: number;
    revenue: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

interface SequenceStep {
  id: string;
  sequenceId: string;
  order: number;
  type: 'email' | 'wait' | 'condition' | 'action';
  config: EmailStepConfig | WaitStepConfig | ConditionStepConfig;
}

interface EmailStepConfig {
  subject: string;
  preheader: string;
  body: string; // HTML
  textBody: string;
  brandCheckResult: {
    passed: boolean;
    voiceMatch: number; // percentage
    violations: string[];
  };
  metrics?: {
    sent: number;
    opened: number;
    clicked: number;
    unsubscribed: number;
    revenue: number;
  };
}

interface WaitStepConfig {
  duration: number; // seconds
  durationLabel: string; // "2 days", "1 week"
}

interface ConditionStepConfig {
  type: 'email_opened' | 'email_clicked' | 'purchased' | 'tag_exists' | 'custom';
  referenceStepId?: string;
  yesPath: string; // step ID
  noPath: string; // step ID
}

interface EmailCampaignDraft {
  id: string;
  workspaceId: string;
  name: string;
  type: 'promotional' | 'announcement' | 'content' | 'seasonal';
  audience: {
    segmentId?: string;
    estimatedRecipients: number;
  };
  content: {
    subject: string;
    preheader: string;
    body: string;
    textBody: string;
  };
  brandCheckResult: {
    passed: boolean;
    voiceMatch: number;
    violations: string[];
  };
  scheduledAt?: Date;
  status: 'generating' | 'draft' | 'approved' | 'scheduled' | 'sent';
  metrics?: {
    sent: number;
    opened: number;
    clicked: number;
    unsubscribed: number;
    revenue: number;
  };
  createdAt: Date;
  updatedAt: Date;
}
```
