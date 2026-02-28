# Brand Onboarding & Channel Setup

## Overview

The onboarding flow is how a brand owner goes from "I have a brand" to "I have a fully configured content automation engine with immersive channel workspaces." The entire process is conversational — no forms, no spreadsheets, no 50-field configuration panels. You upload your brand guide and talk through the rest.

---

## The Onboarding Journey

```
┌──────────────────────────────────────────────────────────────┐
│                     ONBOARDING FLOW                          │
│                                                              │
│  Step 1: Upload Brand Guide                                  │
│    ↓  "Here's who we are"                                    │
│                                                              │
│  Step 2: Brand Understanding Session                         │
│    ↓  AI reads the guide, confirms understanding, asks Qs    │
│                                                              │
│  Step 3: Channel Selection (0-4 channels + shop page)        │
│    ↓  "How many channels do you want to start with?"         │
│                                                              │
│  Step 4: Channel Strategy Conversations (per channel)        │
│    ↓  Build each channel's identity through natural dialogue  │
│                                                              │
│  Step 5: Trend Source Configuration                           │
│    ↓  "Where does your audience hang out online?"             │
│                                                              │
│  Step 6: Content Engine Activation                            │
│    ↓  Inputs defined → automation starts generating           │
│                                                              │
│  ✅ You're live                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 1: Upload Brand Guide

### What You Upload
A brand strategy document — this can be anything from a polished brand book to a rough strategy doc. The system accepts:

- PDF brand guides
- Markdown or text documents
- Slide decks (PDF export)
- Even a brain-dump document with notes

### What the System Extracts
The AI reads the uploaded document and identifies:

| Element | What It Looks For | Example |
|---------|------------------|---------|
| **Brand name** | Company/product name | "Infinity Vault" |
| **Brand voice** | Tone, language, personality | "Confident, passionate, empowering, direct" |
| **Positioning** | How the brand differentiates | "Battle-ready equipment, NOT commodity storage" |
| **Target audience** | Who the brand serves | "Serious TCG players, collectors, tournament grinders" |
| **Products** | What the brand sells | "Card binders, deck boxes, storage solutions" |
| **Content pillars** | Core themes for messaging | "Battle-Ready Lifestyle, Gear & Equipment, Community, Collector's Journey" |
| **Brand language** | Words to use and avoid | Use: "equipment, gear, arsenal" / Avoid: "storage, box, container" |
| **Competitors** | Who the brand competes against | "Ultra Pro, Dragon Shield, Ultimate Guard" |
| **Values** | What the brand stands for | "Every player deserves to show up prepared and respected" |

### If You Don't Have a Brand Guide
That's okay. The system can help you build one through a guided conversation:

```
AI: "Let's start from scratch. Tell me about your brand in your own words.
     What do you sell, who do you sell it to, and why does it matter?"

User: "I sell premium card storage for TCG players. Like binders and deck
      boxes. But I don't want to be just another storage company..."

AI: "Got it — you want to be more than commodity storage. What do you want
     your customers to FEEL when they use your products?"

User: "Like they're serious players. Like they showed up ready."

AI: "That's powerful. 'Show up ready.' Let me start building your brand
     framework around that identity..."
```

---

## Step 2: Brand Understanding Session

After the brand guide is uploaded (or created through conversation), the AI runs a **Brand Understanding Session** — a short conversation to confirm it understood correctly and fill any gaps.

### The Conversation

```
AI: "I've read your brand guide. Here's what I understand about [BRAND_NAME]:

     POSITIONING: You position [products] as [positioning statement].
     Your brand isn't about [commodity framing] — it's about [aspirational framing].

     AUDIENCE: You're speaking to [audience description]. They care about
     [key motivations].

     VOICE: Your brand voice is [voice characteristics]. You use language like
     [brand language examples] and avoid [anti-language].

     Does this feel right? Anything I'm missing or misunderstanding?"

User: "Yeah that's close but we're also really big on community. Like we
      want to be the brand that shows up at local game stores, that supports
      the community, not just sells to it."

AI: "That's a critical dimension — community champion, not just product seller.
     I'm adding 'Community Champion' as a core brand pillar. This will directly
     influence your Earth channel content (if you set one up). Anything else?"
```

### Output
The session produces a **Brand Context File** — a structured document that becomes Layer 1 of every channel agent's system prompt. This is stored and can be updated at any time through the Brand Building sidebar.

---

## Step 3: Channel Selection

### The Options

The system supports a flexible channel setup:

```
┌──────────────────────────────────────────────────────────┐
│  YOUR TIKTOK PRESENCE                                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  🏪 TikTok Shop Seller Page (Required)            │    │
│  │  Your main storefront. Products listed here.     │    │
│  │  You can post content directly to this page.     │    │
│  │  [Always active]                                 │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  MARKETING CHANNELS (Optional, 0-4)                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ ☁ AIR    │  │ ~ WATER  │  │ 🔥 FIRE   │  │ ⛰ EARTH  │ │
│  │          │  │          │  │          │  │          │ │
│  │ Educate  │  │ Showcase │  │ Hype     │  │ Connect  │ │
│  │          │  │          │  │          │  │          │ │
│  │ [Add]    │  │ [Add]    │  │ [Add]    │  │ [Add]    │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                          │
│  Recommended: Start with 1-2 channels, expand as you     │
│  find your rhythm. The AI helps you scale when ready.    │
└──────────────────────────────────────────────────────────┘
```

### Starting Simple

You don't have to launch all four channels. The system is designed for progressive expansion:

**Just the Shop Page**: Post content directly to your TikTok Shop seller page. No elemental strategy yet — just get content out. The system still helps with scripting and scheduling.

**Shop + 1 Channel**: Pick the channel that most matches your current strength. If you're naturally educational, start with Air. If your product photographs well, start with Water. The system focuses all its energy on making that one channel excellent.

**Shop + 2-3 Channels**: Expand as you develop your content muscle. The system helps you identify when you're ready for another channel based on consistency and performance.

**Full 4-Channel Strategy**: The complete elemental system. Each channel has its own identity, workspace, and AI agent. This is the recommended end state for maximum organic reach.

### Channel Selection Conversation

```
AI: "Your brand is set up. Now let's talk about your TikTok presence.

     You'll always have your TikTok Shop seller page — that's your storefront.
     On top of that, you can add up to 4 marketing channels, each with a
     distinct identity and purpose.

     The four elements are:
     • Air — Educational content, tips, how-tos (builds trust)
     • Water — Product showcases, satisfying visuals (creates desire)
     • Fire — Competition, hype, reactions (builds energy)
     • Earth — Community stories, nostalgia (builds belonging)

     How many channels do you want to start with? I'd recommend starting
     with 1-2 and expanding once you're consistent."

User: "Let's start with Fire and Water. Those feel most natural for us."

AI: "Great choices. Water will showcase your products beautifully, and Fire
     will tap into the competitive TCG energy. Let's set up Water first —
     hop into the Water workspace and I'll meet you there."
```

---

## Step 4: Channel Strategy Conversations

For each channel the brand owner activates, they enter that channel's workspace and have a **strategy conversation** with the channel's AI agent. This is where the depth gets built.

### What the Conversation Covers

The agent guides the user through defining:

1. **Content pillars for this channel** — What specific topics and angles will this channel cover?
2. **Target audience refinement** — Within the brand's overall audience, who does this channel speak to most directly?
3. **Voice calibration** — How does the brand voice adapt for this channel's element?
4. **Content formats** — What types of videos will this channel produce?
5. **Product integration rules** — How and how often do products appear?
6. **Trend sources** — What communities, hashtags, and platforms should the agent monitor?
7. **Success metrics** — What does "winning" look like for this channel?

### Example: Setting Up the Fire Channel

```
Fire Agent: "Welcome to Fire. I'm your competitive energy partner.
            I've read your brand guide — [BRAND] is all about showing up
            battle-ready. Fire is where we channel that energy into content
            that makes people's hearts race.

            Let's define what Fire means for YOUR brand.
            What gets your community fired up?"

User: "Pack openings for sure. And tournament prep. And honestly just hot
      takes about the meta. Like people love debating what's overrated."

Fire Agent: "Perfect. So your Fire pillars are:
            1. Pack Rip Energy — chase card pulls, reactions, the rush
            2. Tournament Culture — prep, game day, showing up ready
            3. Meta Takes — bold opinions, rankings, debates

            For tone — Fire for you is high energy but not toxic. We want
            intense, confident, passionate — like the player who talks
            trash with a smile because they know they're backing it up.

            Does that land?"

User: "Yeah exactly. Confident trash talk, not mean."

Fire Agent: "Got it. 'Confident energy, not arrogance.' I'll weave that into
            every script I generate. Now let's talk about your content formats..."
```

### Output
Each channel strategy conversation produces a **Channel Identity Context** — the structured data that becomes Layer 2 of the agent's system prompt. This includes all decisions made during the conversation and can be refined over time through ongoing dialogue.

---

## Step 5: Trend Source Configuration

For each active channel, the user configures where the AI should pull trend signals from.

### Default Sources (Pre-configured)
The system comes with default trend sources based on the brand's niche:

```
AI: "Based on your brand (TCG products), I've pre-configured these
     trend sources for your Fire channel:

     • Reddit: r/PokemonTCG, r/mtg (hot posts, meta discussions)
     • Twitter/X: #PokemonTCG, #MTG, #TCG (breaking news, drama)
     • TikTok: #PackOpening, #TCGCommunity (viral content, format trends)
     • Tournament sites: Recent results and meta shifts

     Want to add, remove, or adjust any of these?"

User: "Add r/yugioh too — we serve all TCG players, not just Pokemon."

AI: "Added. I'll also monitor Yu-Gi-Oh specific hashtags on TikTok.
     Your Fire feed will now include signals from all three TCG communities."
```

### Custom Sources
Users can add:
- Specific subreddits
- Twitter/X accounts or hashtags to follow
- TikTok hashtags or creator accounts
- YouTube channels to monitor
- Discord servers (via webhook)
- RSS feeds from niche news sites
- Google Trends topics

---

## Step 6: Content Engine Activation

Once the brand guide is uploaded, channels are configured, and trend sources are set — the content automation engine has everything it needs.

### What "Activation" Means

```
INPUTS DEFINED:
  ✅ Brand voice, strategy, positioning → HOW to speak
  ✅ Channel identity and pillars → WHAT to say
  ✅ Target audience → WHO to speak to
  ✅ Trend sources → WHAT'S happening now
  ✅ Content format templates → HOW to structure it
  ✅ Product integration rules → WHEN to mention products
  ✅ Posting schedule → WHEN to publish

AUTOMATION CAN NOW:
  → Generate draft scripts on schedule
  → Surface trend-based content opportunities
  → Propose weekly content calendars
  → Create first drafts that match brand voice and channel identity
  → Track performance and suggest optimizations
```

### The Human-in-the-Loop

Automation generates content, but a human reviews it before it goes live. The flow:

```
AI generates draft → Draft appears in channel queue → Marketer reviews →
  → Approve (schedule for posting)
  → Edit (refine in chat with channel agent)
  → Reject (agent learns what didn't work)
  → Regenerate (new approach to same topic)
```

Over time, as the system learns what gets approved and what gets rejected, the quality of first drafts improves and the review cycle gets faster.

---

## The Brand Building Sidebar

### A Dedicated Space for Brand Strategy

The app includes a **Brand Building sidebar tab** — a persistent space where the brand owner can:

1. **View their brand context** — Everything the system knows about the brand, in plain language
2. **Update the brand guide** — Upload a new version or edit specific sections
3. **Review channel identities** — See the strategy summary for each active channel
4. **Refine through conversation** — Chat with a Brand Strategist agent to evolve positioning
5. **See brand consistency scores** — How well is the content matching the brand voice?

### Why It's a Sidebar Tab (Not a Separate Page)

The brand context should be **always accessible**, not buried in settings. When a marketer is creating Fire content and wonders "wait, does this match our brand voice?", they should be able to glance at the sidebar and see the brand guide. It's the constant reference point — the source of truth.

```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR                                                │
│                                                         │
│  📊 Dashboard                                           │
│  ☁ Air Channel                                          │
│  ~ Water Channel                                        │
│  🔥 Fire Channel                                         │
│  ⛰ Earth Channel                                        │
│  ─────────────                                          │
│  📋 Content Calendar                                     │
│  📈 Analytics                                            │
│  ─────────────                                          │
│  🏷️ Brand Guide  ← Always accessible                    │
│  ⚙️ Settings                                             │
└─────────────────────────────────────────────────────────┘
```

### Brand Guide View

When you open the Brand Guide sidebar:

```
┌─────────────────────────────────────────────────┐
│  🏷️ BRAND GUIDE — Infinity Vault                 │
│                                                 │
│  POSITIONING                                    │
│  Battle-ready equipment for serious TCG players │
│  "Show Up Battle Ready"                         │
│  [Edit]                                         │
│                                                 │
│  VOICE                                          │
│  Confident, passionate, empowering, direct      │
│  Never arrogant. Always community-first.        │
│  [Edit]                                         │
│                                                 │
│  LANGUAGE                                       │
│  ✅ Use: equipment, gear, arsenal, vault         │
│  ❌ Avoid: storage, box, container, case         │
│  [Edit]                                         │
│                                                 │
│  AUDIENCE                                       │
│  Serious TCG players (18-35)                    │
│  Tournament grinders, collectors, LGS regulars  │
│  [Edit]                                         │
│                                                 │
│  PILLARS                                        │
│  1. Battle-Ready Lifestyle                      │
│  2. Gear & Equipment                            │
│  3. Community Champion                          │
│  4. Collector's Journey                         │
│  [Edit]                                         │
│                                                 │
│  [Upload New Brand Guide]                       │
│  [Chat with Brand Strategist]                   │
└─────────────────────────────────────────────────┘
```

---

## Scaling: From One Person to a Team

The system is designed so one person can manage it all — but as the brand grows, roles can split:

| Role | Responsibility | Channels |
|------|---------------|----------|
| **Brand Owner** | Sets strategy, defines voice, approves brand-level changes | Brand Guide, all channels (high-level) |
| **Content Manager** | Daily content operations, reviews AI drafts, manages calendars | All 4 channels |
| **Channel Specialist** (optional) | Deep focus on one element's content quality | 1-2 specific channels |

The workspace permissions and role system allow brands to grow their team without losing strategic consistency — because the strategy is baked into the AI agents, not stored in one person's head.

---

## Summary: What the Onboarding Really Does

The onboarding flow captures the **inputs to content automation**:

1. **Brand context** → The AI knows how to speak
2. **Channel strategy** → The AI knows what to say on each channel
3. **Trend sources** → The AI knows what's happening now
4. **Human preferences** → The AI knows what gets approved

These inputs, embedded in the front-facing app through immersive channel workspaces, are what make automated content feel human, on-brand, and strategically intentional. The app's job is to make defining and refining these inputs feel natural — like having a conversation, not configuring software.
