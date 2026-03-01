# User Journey: Brand Guide Upload & Management

## Overview

The Brand Guide tab is the **foundation of the entire system**. Every AI agent, every content template, every email sequence pulls from the brand context established here. Without a brand guide, the other tabs function generically. With one, they become personalized content engines tuned to the brand's voice, positioning, and audience.

This is the first thing a new user interacts with, and the reference point every returning user checks when something feels off-brand.

---

## Journey Map: First-Time User

### Entry Point
User signs up, completes Clerk authentication, lands on the dashboard for the first time.

```
┌─────────────────────────────────────────────────────────────┐
│  DASHBOARD — First Visit                                    │
│                                                             │
│  Welcome to your Organic Marketing OS.                      │
│                                                             │
│  To get started, we need to understand your brand.          │
│  Everything — your TikTok content, email sequences,         │
│  blog strategy — flows from your brand identity.            │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │                                                   │       │
│  │     📄  Upload Your Brand Guide                   │       │
│  │                                                   │       │
│  │     PDF, markdown, or text document              │       │
│  │     containing your brand strategy,              │       │
│  │     voice guide, or positioning notes.           │       │
│  │                                                   │       │
│  │     [Upload Document]                            │       │
│  │                                                   │       │
│  │     ─── or ───                                   │       │
│  │                                                   │       │
│  │     🗣️  Build It Through Conversation             │       │
│  │                                                   │       │
│  │     Don't have a doc? No problem.                │       │
│  │     Our AI will help you define your brand       │       │
│  │     through a guided conversation.               │       │
│  │                                                   │       │
│  │     [Start Brand Conversation]                   │       │
│  │                                                   │       │
│  └─────────────────────────────────────────────────┘       │
│                                                             │
│  (All other sidebar tabs show as locked/disabled until      │
│   brand guide is established)                               │
└─────────────────────────────────────────────────────────────┘
```

### Path A: Upload Document

**Step 1 — File Upload**
```
User Action: Clicks [Upload Document]
System Response: File picker opens (accepts .pdf, .md, .txt, .docx)
User Action: Selects their brand guide file
System Response: Upload progress indicator → "Processing your brand guide..."
```

**Step 2 — AI Processing (15-30 seconds)**
```
System: Reads the document and extracts brand elements
Display: Progress indicator with stages:
  ✅ Document uploaded
  ⏳ Reading brand voice...
  ⏳ Identifying positioning...
  ⏳ Extracting audience profiles...
  ⏳ Mapping content pillars...
```

**Step 3 — Brand Understanding Review**
```
┌─────────────────────────────────────────────────────────────┐
│  BRAND GUIDE — Review What We Found                         │
│                                                             │
│  I've read your brand guide. Here's what I understand:      │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  BRAND NAME                                    │          │
│  │  Infinity Vault                                │          │
│  │                                     [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  POSITIONING                                   │          │
│  │  Battle-ready equipment for serious TCG        │          │
│  │  players and collectors. Premium protection    │          │
│  │  gear, not commodity storage.                  │          │
│  │                                     [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  BRAND VOICE                                   │          │
│  │  Confident, passionate, empowering, direct.    │          │
│  │  Speaks like a fellow competitor who wants      │          │
│  │  everyone to show up prepared.                  │          │
│  │                                     [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  TARGET AUDIENCE                               │          │
│  │  Serious TCG players (18-35), tournament       │          │
│  │  grinders, dedicated collectors, LGS regulars  │          │
│  │                                     [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  CONTENT PILLARS                               │          │
│  │  1. Battle-Ready Lifestyle                     │          │
│  │  2. Gear & Equipment                           │          │
│  │  3. Community Champion                         │          │
│  │  4. Collector's Journey                        │          │
│  │                                     [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  BRAND LANGUAGE                                │          │
│  │  ✅ Use: equipment, gear, arsenal, vault       │          │
│  │  ❌ Avoid: storage, box, container, case       │          │
│  │                                     [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  ⚠️  GAPS DETECTED                             │          │
│  │                                                │          │
│  │  Your brand guide doesn't mention:             │          │
│  │  • Competitor positioning                      │          │
│  │  • Product catalog details                     │          │
│  │  • Mission or values statement                 │          │
│  │                                                │          │
│  │  [Fill gaps with AI conversation]              │          │
│  │  [Skip for now — I'll add these later]         │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  [Looks Good — Save & Continue]     [Start Over]           │
└─────────────────────────────────────────────────────────────┘
```

**Step 4 — Gap-Filling Conversation (optional)**
If user clicks [Fill gaps with AI conversation]:

```
AI: "Your brand guide is solid but I noticed a few gaps.
     Let me ask a few quick questions to fill them in.

     First — who are your main competitors?
     The brands your customers compare you to."

User: "Ultra Pro, Vault X, Dragon Shield, Ultimate Guard"

AI: "Got it. And how do you want to be positioned against them?
     Are you the premium option? The community-driven option?
     The most innovative?"

User: "Premium and community-driven. We're not the cheapest
      and we don't want to be."

AI: "Perfect. 'Premium quality, community first.' That positions
     you clearly against Ultra Pro (commodity), Dragon Shield
     (sleeves-only), and Vault X (budget premium).

     One more — what products do you sell? Just a quick list
     so the system can reference them in content."

User: "Card binders, deck boxes, accessories like playmats
      and sleeves. Launching tournament bags soon."

AI: "All captured. Your brand context is now complete.
     I'll use this across every channel and content type.
     Ready to continue?"
```

**Step 5 — Confirmation & Unlock**
```
System: Saves brand context to database
Display: Success animation → "Your brand is set up"
Effect: All sidebar tabs unlock (TikTok Studio, AEO, Email Marketing)
Redirect: Dashboard overview with brand summary card visible
```

### Path B: Build Through Conversation

**Step 1 — Conversation Opens**
```
┌─────────────────────────────────────────────────────────────┐
│  BRAND GUIDE — Let's Build Your Brand Identity              │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │ AI: Let's figure out who your brand is. I'll    │       │
│  │     ask questions, you talk — I'll organize     │       │
│  │     it all into a brand guide when we're done.  │       │
│  │                                                   │       │
│  │     First things first: What's your brand name   │       │
│  │     and what do you sell?                        │       │
│  └─────────────────────────────────────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │ Type your response...                    [Send] │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Step 2 — Guided Q&A (5-10 minutes)**

The AI walks through these topics in natural conversation order:
1. Brand name and product category
2. What makes you different from competitors
3. Who your ideal customer is
4. How you want your brand to sound/feel
5. Words you love and words you hate
6. What you want people to feel when they interact with your brand
7. Your brand's origin story (if available)

**Step 3 — AI Generates Brand Guide**
```
AI: "Based on our conversation, here's your brand guide.
     Take a look and tell me if anything needs adjusting."

System: Displays the same review screen as Path A (Step 3)
```

**Step 4 → Same as Path A Steps 4-5**

---

## Journey Map: Returning User

### Daily Check-In (Sidebar Tab)

The Brand Guide lives as a persistent sidebar tab, always accessible from any page.

```
┌─────────────────────────────────────────────────────────────┐
│  SIDEBAR                    │  MAIN CONTENT AREA            │
│                             │                                │
│  📊 Dashboard               │  (whatever tab is active)      │
│  🎬 TikTok Studio           │                                │
│  🔍 AEO Optimizer           │                                │
│  📧 Email Marketing         │                                │
│  ─────────────────          │                                │
│  📋 Content Calendar        │                                │
│  📈 Analytics               │                                │
│  ─────────────────          │                                │
│  🏷️ Brand Guide  ◀──────── │  ← Click to open brand panel   │
│  ⚙️ Settings                │                                │
└─────────────────────────────┴────────────────────────────────┘
```

### When User Clicks "Brand Guide"

```
┌─────────────────────────────────────────────────────────────┐
│  🏷️ BRAND GUIDE — Infinity Vault                            │
│                                                             │
│  Brand Health Score: 92/100                                 │
│  Last updated: 2 days ago                                   │
│                                                             │
│  ┌─ POSITIONING ────────────────────────────────┐          │
│  │  Battle-ready equipment for serious TCG       │          │
│  │  players and collectors.                      │          │
│  │  "Show Up Battle Ready"                       │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─ VOICE ──────────────────────────────────────┐          │
│  │  Confident, passionate, empowering, direct    │          │
│  │  Never arrogant. Always community-first.      │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─ LANGUAGE ───────────────────────────────────┐          │
│  │  ✅ Use: equipment, gear, arsenal, vault      │          │
│  │  ❌ Avoid: storage, box, container, case      │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─ AUDIENCE ───────────────────────────────────┐          │
│  │  Serious TCG players (18-35)                  │          │
│  │  Tournament grinders, collectors, LGS regs    │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─ PILLARS ────────────────────────────────────┐          │
│  │  1. Battle-Ready Lifestyle                    │          │
│  │  2. Gear & Equipment                          │          │
│  │  3. Community Champion                        │          │
│  │  4. Collector's Journey                       │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─ PRODUCTS ───────────────────────────────────┐          │
│  │  Card binders, deck boxes, playmats,          │          │
│  │  sleeves, tournament bags (coming soon)        │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─ COMPETITORS ────────────────────────────────┐          │
│  │  Ultra Pro, Vault X, Dragon Shield,           │          │
│  │  Ultimate Guard                               │          │
│  │                                    [Edit ✏️]  │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ─────────────────────────────────────────────────          │
│                                                             │
│  [Upload New Brand Guide]                                   │
│  [Chat with Brand Strategist]                               │
│  [Export Brand Guide as PDF]                                │
│  [View Brand Consistency Report]                            │
└─────────────────────────────────────────────────────────────┘
```

### Editing a Section

When user clicks [Edit] on any section:

```
┌──────────────────────────────────────────────┐
│  EDIT: Positioning                            │
│                                               │
│  Current:                                     │
│  "Battle-ready equipment for serious TCG      │
│   players and collectors."                    │
│                                               │
│  ┌─────────────────────────────────────┐     │
│  │ Battle-ready equipment for serious   │     │
│  │ TCG players and collectors.          │     │
│  │                                       │     │
│  └─────────────────────────────────────┘     │
│                                               │
│  💡 AI Suggestion:                            │
│  "Based on your recent content performance,   │
│  consider emphasizing 'collector protection'   │
│  alongside 'battle-ready' — your Air channel   │
│  content about card protection has the highest │
│  save rates."                                 │
│                                               │
│  [Save Changes]  [Chat About This]  [Cancel]  │
└──────────────────────────────────────────────┘
```

### "Chat with Brand Strategist"

Opens a dedicated chat agent focused on brand evolution:

```
AI: "Hey — I see your brand guide was last updated 2 days ago.
     A few things I've noticed from your content performance:

     1. Your Air channel content about card protection is
        outperforming everything else (6.2% save rate)
     2. The 'battle-ready' language resonates most in Fire content
     3. Your Earth content is building strong community response

     Want to explore evolving your positioning based on
     what's actually resonating? Or is there something
     specific you want to adjust?"
```

---

## Edge Cases

### No Brand Guide Yet (Other Tabs)
If a user tries to access TikTok Studio, AEO, or Email Marketing before setting up their brand guide:

```
┌─────────────────────────────────────────────────┐
│  ⚠️ Brand Guide Required                         │
│                                                  │
│  This tab uses your brand voice, positioning,    │
│  and audience data to generate on-brand content. │
│                                                  │
│  Set up your brand guide first — it takes about  │
│  5 minutes.                                      │
│                                                  │
│  [Go to Brand Guide Setup]                       │
│                                                  │
│  Or: [Use Generic Settings] (not recommended)    │
└─────────────────────────────────────────────────┘
```

### Uploading a New Brand Guide (Replacing Existing)
```
System: "Uploading a new brand guide will update the context
        used across all your channels and content.

        Your current brand guide will be archived (you can
        restore it anytime).

        All AI agents will use the new brand context going
        forward. Existing drafts won't be affected.

        [Upload & Replace]  [Cancel]"
```

### Brand Guide is Stale (30+ Days Without Update)
```
Dashboard notification:
"Your brand guide hasn't been updated in 45 days.
 Your brand may have evolved — want to review it?
 [Review Brand Guide]  [Dismiss]"
```

---

## How This Tab Connects to Others

| Connected Tab | How Brand Guide Feeds It |
|--------------|-------------------------|
| **TikTok Studio** | Brand voice, pillars, and language rules are injected into every channel agent's system prompt. Products list feeds product showcase content. |
| **AEO Optimizer** | Brand positioning and competitor list determine which AI queries to target. Brand narrative fuels differentiation content. |
| **Email Marketing** | Brand voice shapes email tone. Welcome sequence references brand story. Language rules apply to every email template. |
| **Content Calendar** | Content pillars define the categories used for scheduling and tagging content across all channels. |
| **Analytics** | Brand consistency scoring compares published content against brand guide rules. |

---

## Data Model

The Brand Guide produces a structured `BrandContext` object stored in the database:

```typescript
interface BrandContext {
  id: string;
  workspaceId: string;
  brandName: string;
  positioning: string;
  tagline?: string;
  voice: {
    characteristics: string[];
    description: string;
  };
  audience: {
    demographics: string;
    psychographics: string;
    segments: string[];
  };
  pillars: string[];
  language: {
    preferred: string[];
    avoided: string[];
  };
  products: Product[];
  competitors: Competitor[];
  values?: string[];
  originStory?: string;
  sourceDocument?: string; // URL to uploaded file
  version: number;
  createdAt: Date;
  updatedAt: Date;
}
```

This object is loaded as Layer 1 of every AI agent's context across the entire system.
