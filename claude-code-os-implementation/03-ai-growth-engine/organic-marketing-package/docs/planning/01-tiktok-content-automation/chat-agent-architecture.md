# Chat Agent Architecture

## Overview

Each TikTok channel has a **dedicated AI chat agent** — not a generic assistant, but a character with a specific persona, strategic depth, and set of workflows tailored to that channel's purpose. The agent is the brand owner's creative partner for that channel.

This document defines how these agents are built, what powers them, and how they interact with the broader content automation system.

---

## Core Concept: Channel Agents as Creative Partners

A channel agent is not a chatbot that answers questions. It's a **strategic creative partner** that:

1. **Knows the brand deeply** — brand voice, strategy, positioning, target market, product catalog
2. **Knows its channel's strategy** — the element's philosophy, content pillars, audience, emotional frequency
3. **Knows what's happening now** — real-time trends, community signals, current events in the space
4. **Knows what's worked before** — content performance data, save rates, top-performing formats
5. **Has dedicated workflows** — not just freeform chat, but structured modes for specific creative tasks

The agent acts as if it wakes up every day thinking about this one channel. It has opinions. It spots opportunities. It proactively suggests content ideas based on what's trending.

---

## Agent Architecture

### System Prompt Layers

Each agent's system prompt is assembled from multiple context layers:

```
┌─────────────────────────────────────────────┐
│  Layer 1: BRAND FOUNDATION                  │
│  ─────────────────────────────────────────  │
│  • Brand voice guide                        │
│  • Brand strategy                           │
│  • Value proposition                        │
│  • Target market profiles                   │
│  • Content strategy                         │
│  • Product catalog & positioning            │
│                                             │
│  (Shared across all 4 channel agents)       │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│  Layer 2: CHANNEL IDENTITY                  │
│  ─────────────────────────────────────────  │
│  • Element philosophy & emotional frequency │
│  • Channel-specific content pillars         │
│  • Target audience for this channel         │
│  • Persona voice & personality              │
│  • Content format templates                 │
│  • Product integration rules                │
│  • Posting schedule & cadence               │
│                                             │
│  (Unique per channel — Air, Water, etc.)    │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│  Layer 3: LIVE CONTEXT                      │
│  ─────────────────────────────────────────  │
│  • Trending topics from configured sources  │
│  • Recent community discussions             │
│  • Current events in the TCG space          │
│  • Competitor content activity              │
│  • Seasonal / calendar context              │
│                                             │
│  (Refreshed on each session start)          │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│  Layer 4: PERFORMANCE MEMORY                │
│  ─────────────────────────────────────────  │
│  • This channel's content performance data  │
│  • Top-performing videos & why they worked  │
│  • Save rates, engagement patterns          │
│  • What formats are resonating              │
│  • Content gaps to fill                     │
│                                             │
│  (Updated from analytics pipeline)          │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│  Layer 5: CONVERSATION HISTORY              │
│  ─────────────────────────────────────────  │
│  • Previous sessions with this agent        │
│  • Decisions made, direction set            │
│  • Brand owner's preferences & style        │
│  • Ongoing creative threads                 │
│                                             │
│  (Persisted across sessions)                │
└─────────────────────────────────────────────┘
```

### How Context is Loaded

**On agent initialization (opening the channel workspace):**
1. Brand foundation context loaded from brand guide files (same paths as `BaseAgent._load_brand_context()`)
2. Channel identity loaded from channel configuration (`TIKTOK_CHANNELS`, `CHANNEL_THEMES` in config.py)
3. Live context fetched from trend intelligence service
4. Performance data pulled from analytics pipeline
5. Conversation history loaded from persistent storage

**During conversation:**
- Agent can request fresh trend data on demand ("Let me check what's trending right now...")
- Performance data refreshes on explicit request
- New context from user input gets incorporated naturally

---

## The Four Agent Personas

### Air Agent — The Wise Mentor

**System prompt personality block:**
```
You are the Air Channel Agent for [BRAND_NAME]. Your role is The Wise Mentor.

You think like an experienced educator and strategist in the [NICHE] space.
Your voice is calm, measured, and authoritative — never condescending, always
generous with knowledge.

When you greet the user, reference something current and educational from
the trend feed. Offer to help with teaching-focused content.

Your content philosophy: Every piece of Air content should make someone
feel smarter and more prepared. The save button is your primary success metric
because people save content they want to reference later.

You naturally organize information into frameworks, numbered lists, and
clear hierarchies. When brainstorming, you ask "What does your audience
need to understand?" and "What misconception can we correct?"
```

### Water Agent — The Experience Curator

**System prompt personality block:**
```
You are the Water Channel Agent for [BRAND_NAME]. Your role is The Experience Curator.

You think like a creative director and visual storyteller. You see the world
in terms of how things look, sound, and feel on screen. You're always thinking
about the sensory experience.

When you greet the user, reference a visual trend or aesthetic opportunity.
Offer to help craft a product experience.

Your content philosophy: Every piece of Water content should create desire.
The viewer should WANT what they're seeing before they've consciously decided.
Loop rate and shop clicks are your primary success metrics.

You naturally think in shots, angles, textures, and audio pairings. When
brainstorming, you ask "What does this FEEL like?" and "What's the most
satisfying moment?"
```

### Fire Agent — The Hype Commander

**System prompt personality block:**
```
You are the Fire Channel Agent for [BRAND_NAME]. Your role is The Hype Commander.

You bring energy to every interaction. You think like a sports commentator
and competitive strategist. Every moment is potentially epic. Every piece of
content should raise someone's heart rate.

When you greet the user, reference something happening RIGHT NOW that the
community is passionate about. Create urgency. Offer to help react fast.

Your content philosophy: Every piece of Fire content should make someone
feel something intensely — excitement, competitive fire, the urge to debate.
Comment volume and share rate are your primary success metrics.

You naturally think in moments — the pull, the win, the reaction, the take.
When brainstorming, you ask "What's the community fired up about?" and
"What take are you willing to defend?"
```

### Earth Agent — The Community Elder

**System prompt personality block:**
```
You are the Earth Channel Agent for [BRAND_NAME]. Your role is The Community Elder.

You value people over products, stories over statistics, belonging over
performance. You speak from a place of deep connection to the community
and genuine care for the humans in it.

When you greet the user, reference a community story or emotional moment
you've noticed. Offer to help tell someone's story.

Your content philosophy: Every piece of Earth content should make someone
feel seen and connected. The comments section should fill with people sharing
their own stories. Follow rate and comment quality are your primary metrics.

You naturally think in narratives and emotional arcs. When brainstorming,
you ask "Whose story deserves to be told?" and "What memory does this trigger?"
```

---

## Agent Workflows

Each agent offers structured workflows alongside freeform chat. When a user opens the chat, the agent can suggest entering a specific mode based on context (time of day, pending content, trending signals).

### Shared Workflows (All Channels)

**1. Content Calendar Builder**
```
Trigger: "Plan my week" / "What should I post this week?" / Agent suggests proactively
Flow:
  1. Agent reviews upcoming posting schedule for this channel
  2. Pulls trending topics from live context
  3. Reviews recent performance data for format inspiration
  4. Proposes a week of content with specific topics, formats, and hooks
  5. User refines through conversation
  6. Agent outputs final calendar with draft scripts
Output: Structured content calendar with draft scripts for each slot
```

**2. Trend Review**
```
Trigger: "What's trending?" / Agent surfaces unread trend signals on session start
Flow:
  1. Agent presents top trend signals from configured sources
  2. Filters through this channel's strategic lens
  3. For each trend, suggests a content angle specific to this channel
  4. User selects which trends to pursue
  5. Agent develops selected trends into content concepts
Output: Content concepts tied to current trends
```

**3. Performance Debrief**
```
Trigger: "How did we do?" / "What worked this week?" / Weekly prompt
Flow:
  1. Agent pulls performance data for this channel's recent content
  2. Identifies top performers and analyzes why they worked
  3. Identifies underperformers and diagnoses issues
  4. Suggests adjustments to content strategy
  5. Proposes experiments for next week
Output: Performance summary with strategic recommendations
```

**4. Script Generator**
```
Trigger: "Write me a script for..." / User selects content concept from calendar
Flow:
  1. Agent confirms the topic, format, and target emotion
  2. Generates hook options (3-5 alternatives)
  3. User selects hook direction
  4. Agent writes full script with timing, visual notes, audio suggestions
  5. User refines through conversation
  6. Agent outputs final script ready for production
Output: Production-ready script with hook, body, CTA, and production notes
```

### Channel-Specific Workflows

| Channel | Unique Workflow | Purpose |
|---------|----------------|---------|
| Air | **Myth Buster Builder** | Takes a common misconception and builds a structured debunk script |
| Air | **How-To Sequencer** | Plans a multi-part educational series on a topic |
| Water | **Shot List Generator** | Creates a detailed shot list with angles, lighting, and product staging |
| Water | **Before/After Storyboard** | Plans transformation content with visual notes for each phase |
| Fire | **React Mode** | Speed workflow — breaking news in, reaction script out in under 5 minutes |
| Fire | **Hot Take Framer** | Takes a raw opinion and frames it for maximum engagement without toxicity |
| Earth | **Story Mining** | Scans community sources for stories worth telling, packages them as content concepts |
| Earth | **Spotlight Planner** | Plans a community member or LGS feature with interview prompts and narrative structure |

---

## Trend Intelligence Integration

### How Live Data Feeds Into Agents

```
┌──────────────────────────────────────────────┐
│  TREND INTELLIGENCE SERVICE                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Reddit   │  │ Twitter  │  │  TikTok  │   │
│  │  Scraper  │  │  Stream  │  │ Trending │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘   │
│        │             │             │         │
│        └─────────────┼─────────────┘         │
│                      │                       │
│              ┌───────▼────────┐              │
│              │  Signal Router │              │
│              │  (classifies   │              │
│              │   by channel)  │              │
│              └───────┬────────┘              │
│                      │                       │
│     ┌────────┬───────┼───────┬────────┐      │
│     │        │       │       │        │      │
│   ┌─▼──┐  ┌─▼──┐  ┌─▼──┐  ┌─▼──┐    │      │
│   │Air │  │Water│  │Fire│  │Earth│    │      │
│   │Feed│  │Feed│  │Feed│  │Feed│    │      │
│   └────┘  └────┘  └────┘  └────┘    │      │
│                                       │      │
└──────────────────────────────────────────────┘
```

**Signal classification rules:**
- Educational content, questions, tips → Air
- Aesthetic content, product reveals, visual trends → Water
- Breaking news, drama, competition, hot takes → Fire
- Personal stories, nostalgia, community events → Earth
- Some signals are relevant to multiple channels and appear in multiple feeds

**Each channel's feed shows:**
- Unread signal count (badge on channel selector)
- Signals sorted by relevance and recency
- For each signal: source, summary, suggested content angle
- "Ignore" / "Save for later" / "Create content from this" actions

---

## Connecting to the Existing Codebase

### Current Implementation: `TikTokChannelAgent`

The existing `content-agents/agents/tiktok_channel_agent.py` provides the foundation:

- Inherits from `BaseAgent` which loads brand context from markdown files
- Has channel configurations via `TIKTOK_CHANNELS` and `CHANNEL_THEMES` in config
- Can generate content per channel element
- Can build content calendars
- Can create cross-channel strategies

**What needs to extend:**
1. **Persona layer** — Add channel-specific persona prompts on top of the base system prompt
2. **Conversational mode** — Current agent is single-request/response; needs multi-turn conversation support
3. **Trend context injection** — Feed live trend data into the system prompt before each interaction
4. **Performance context** — Pull analytics data into agent context
5. **Conversation persistence** — Store and reload conversation history per channel per user
6. **Workflow state machine** — Track which workflow the user is in and maintain flow state

### API Extension Points

The existing `content-agents/api/routes/tiktok_channels.py` handles REST endpoints. For the chat agent experience:

```
New endpoints needed:

POST /api/channels/{element}/chat
  → Send message to channel agent, receive response
  → Includes workflow state, trend context, conversation history

GET /api/channels/{element}/trends
  → Fetch current trend signals for this channel
  → Filtered and classified by the signal router

GET /api/channels/{element}/performance
  → Channel performance summary for agent context

GET /api/channels/{element}/history
  → Conversation history for this channel

POST /api/channels/{element}/workflows/{workflow_name}
  → Enter a specific workflow mode
  → Returns initial workflow prompt and state
```

### Dashboard Integration

The `dashboard/` Next.js app needs:

1. **Channel workspace pages** — `/channels/air`, `/channels/water`, `/channels/fire`, `/channels/earth`
2. **Theme provider** — CSS variables that shift based on active channel
3. **Chat component** — Streaming chat interface with the channel agent
4. **Trend feed component** — Real-time signal display with actions
5. **Content queue component** — Draft/scheduled/published content for this channel
6. **Performance widget** — Key metrics for this channel

---

## Onboarding: Building Your Channel Agent

When a brand owner first sets up a channel, they don't fill out a form — they have a **conversation** with the agent to build its character:

```
Agent: "Welcome to your new Air channel. I'm going to be your creative
       partner for educational content. But first, I need to understand
       your brand. I've read your brand guide — here's what I understand
       so far: [summary]. Let me ask you a few things..."

Agent: "What does your audience struggle with most? What questions do
       they ask over and over?"

User:  "They always ask about card protection — what sleeves to use,
       how to store things, whether penny sleeves are good enough..."

Agent: "Perfect. Card protection education is a natural Air pillar.
       Here's what I'm thinking for our content approach:
       1. 'Quick Protection Tips' — 15-second myth-busting clips
       2. 'The Full Guide' — deep dives on specific protection topics
       3. 'Mistake Spotlights' — showing what NOT to do
       Does that resonate? What would you adjust?"
```

This conversational setup creates a **natural, low-friction onboarding** that captures the brand owner's vision without forcing them into structured forms. The agent stores these decisions as part of its channel identity context.

---

## Multi-Brand Support

The architecture is designed to work for any e-commerce brand, not just Infinity Vault:

- **Brand foundation** is loaded from uploaded brand guide (not hardcoded)
- **Channel themes** are configurable per brand (elements are the default; a fashion brand might use Seasons instead)
- **Trend sources** are configurable per brand and niche
- **Persona prompts** adapt based on brand voice and industry
- **Content format templates** adjust based on product type and audience

The elemental framework (Air, Water, Fire, Earth) is the **recommended default** because it naturally maps to the four content archetypes (Educate, Showcase, Hype, Connect), but brands can customize the metaphor to fit their identity.
