# TikTok Outreach Automation System

## Overview

This automation system allows you to generate personalized outreach messages at scale. Given a list of TikTok handles (or criteria to find them), the system produces ready-to-send messages customized for each creator.

---

## Architecture

```
INPUT                    PROCESS                      OUTPUT
─────                    ───────                      ──────
TikTok handles    →    Profile analysis    →    Personalized messages
  OR                   Content review             ready to send
Search criteria   →    Niche classification  →   Tracking spreadsheet
                       Template selection          Follow-up schedule
                       Message generation
```

---

## Workflow 1: Batch Message Generation from Handle List

### When to Use
You have a list of TikTok handles and need personalized outreach messages for each one.

### Input Format

Create a CSV or simple list with the following info per creator:

```
@handle, Name (if known), Follower Count, Primary Niche, Notable Video/Detail
```

**Example Input**:
```
@pokemonpullking, Alex, 45000, Pokemon pack openings, Amazing alt art Charizard pull video
@mtgtourneylife, Jordan, 12000, MTG tournaments, Weekly FNM vlogs from local game store
@cardcollectorjess, Jess, 78000, Pokemon collection, Vintage binder tour with 1st edition cards
@tcgdaily, Marcus, 23000, Mixed TCG, Reviews binders and card accessories regularly
@gamernerd_setup, Kim, 156000, Gaming lifestyle, Hobby room tours featuring card collections
```

### Process: AI-Powered Message Generation

Use the following prompt with Claude or ChatGPT to generate personalized messages in batch:

```
SYSTEM PROMPT:
You are an outreach specialist for Infinity Vault, a premium trading card
binder brand. Your brand voice is confident, passionate, empowering, and
direct. You speak the language of gaming and fantasy.

Brand details:
- Product: Premium scratch-resistant trading card binders (2-pack)
- Key differentiator: Lifetime warranty
- Positioning: "Battle-ready equipment" not "storage"
- Tagline: "Show Up Battle Ready"

Your job: Generate personalized TikTok DM outreach messages for each
creator in the list below. Each message must:
1. Reference something specific about their content (use the Notable
   Video/Detail provided, or infer from their niche)
2. Briefly introduce Infinity Vault (1-2 sentences, not salesy)
3. Explain why their content specifically caught our attention
4. Make a clear, low-pressure offer (free product, no obligations)
5. End with a simple next step

Tone: Like one enthusiast reaching out to another. Genuine, not corporate.

Keep each message under 150 words (TikTok DMs should be concise).

CREATOR LIST:
[Paste your CSV list here]

Generate one personalized message per creator. Format as:

---
TO: @handle (Name)
TEMPLATE TYPE: [Pack Opening / Tournament / Collection / Lifestyle / Rising Creator]
MESSAGE:
[The personalized message]
---
```

### Example Output

```
---
TO: @pokemonpullking (Alex)
TEMPLATE TYPE: Pack Opening
MESSAGE:
Hey Alex! That alt art Charizard pull had me out of my seat - your
reactions are what make pack openings worth watching.

I'm with Infinity Vault - we make scratch-resistant trading card
binders with a lifetime warranty, built for collectors who actually
care about keeping their pulls in mint condition.

Your audience clearly loves the pull, but I bet they'd also love
seeing how to protect those cards properly. Would you be down to
try out a free 2-pack of our binders? No strings - just quality
gear for a quality creator.

Drop me your address and I'll ship them out!

- [Your Name], Infinity Vault
---
```

---

## Workflow 2: Influencer Discovery + Message Generation

### When to Use
You don't have handles yet. You need the system to help identify potential influencers AND generate outreach.

### Step 1: AI-Assisted Discovery Prompt

```
SYSTEM PROMPT:
You are a TikTok influencer researcher for Infinity Vault, a premium
trading card binder brand targeting TCG (Pokemon, MTG, Yu-Gi-Oh)
players and collectors.

Based on the following criteria, suggest 30 TikTok search strategies
that would help find ideal influencer partners:

TARGET PROFILE:
- Creates content about: Trading cards, card collecting, Pokemon,
  MTG, pack openings, collection organization, tournament play
- Follower range: 5,000 - 250,000
- Engagement rate: 3%+
- Posts consistently (3+ times per week)
- Audience: 18-35, passionate about TCG/gaming

For each search strategy, provide:
1. Exact TikTok search term or hashtag
2. What type of creator you'll find
3. What to look for in their content
4. Estimated number of relevant creators you'll find
```

### Step 2: Manual Research Phase

Using the search strategies from Step 1:
1. Execute each search on TikTok
2. For each promising creator, record:
   - @handle
   - Display name
   - Follower count
   - Primary content niche
   - One specific video you'd reference
   - Engagement rate estimate (eyeball likes vs. followers)
3. Add to tracking spreadsheet

### Step 3: Batch Message Generation

Feed your collected handles into Workflow 1 above.

---

## Workflow 3: Follow-Up Automation

### Automated Follow-Up Schedule

| Day | Action | Message |
|-----|--------|---------|
| Day 0 | Initial outreach sent | Template message |
| Day 5-7 | Follow-up 1 (if no response) | Gentle bump |
| Day 14 | Follow-up 2 (if no response) | Final follow-up |
| Day 21 | Archive if no response | Mark as "No Response" |

### Follow-Up Batch Prompt

```
SYSTEM PROMPT:
Generate follow-up messages for the following creators who haven't
responded to our initial outreach. Keep messages short (under 50 words),
friendly, and low-pressure.

This is follow-up #[1 or 2].

CREATORS WHO NEED FOLLOW-UP:
[List of @handles and their original outreach date]

For follow-up #1: Friendly bump, assume they missed it
For follow-up #2: Final check-in, no pressure, leave the door open
```

---

## Workflow 4: Response Management

### When a Creator Responds Positively

**Prompt for generating response**:
```
A TikTok creator (@[handle], [name], [niche]) responded positively
to our outreach. Generate a response that:
1. Expresses genuine enthusiasm
2. Lists what we'll send them (2x premium binders)
3. Asks for shipping address
4. Mentions affiliate code opportunity (if applicable)
5. Sets expectations (no pressure on timeline or content)
Keep it under 100 words, warm and casual tone.
```

### When a Creator Asks Questions

Common questions and prepared responses:

| Question | Response |
|----------|----------|
| "What's the catch?" | "No catch! We send free product to creators we genuinely admire. If you love the binders and they naturally fit your content, amazing. If not, you still keep them. We'd rather earn a mention than buy one." |
| "Do I have to post?" | "Nope, zero obligation. We'd rather you use and genuinely enjoy the product. If it earns a spot in your content naturally, that means way more than a forced post." |
| "Can I get paid instead?" | "We typically start with product gifting to make sure the fit is right. If the partnership works well, we're open to discussing paid collaborations and affiliate commissions. Let's start with getting you some binders!" |
| "What commission do you offer?" | "We offer 10-15% commission through a unique affiliate link or discount code. Happy to set that up once you've had a chance to try the product." |

---

## Workflow 5: Weekly Outreach Cadence

### Weekly Schedule

| Day | Task | Target |
|-----|------|--------|
| Monday | Research: Find 10 new creators | 10 new handles |
| Tuesday | Score and prioritize new finds | Updated spreadsheet |
| Wednesday | Generate and send batch outreach | 10 new messages sent |
| Thursday | Send follow-ups for previous batches | All overdue follow-ups |
| Friday | Respond to replies, ship product | All positive responses handled |

### Monthly Metrics to Track

| Metric | Target | Actual |
|--------|--------|--------|
| Outreach messages sent | 40/month | |
| Response rate | 10-15% | |
| Products shipped | 4-6/month | |
| Content pieces created about us | 2-3/month | |
| Sales from affiliate links | Track | |
| New followers from creator mentions | Track | |

---

## Quick-Start: Generate 20 Messages Right Now

### Step 1: Collect 20 Handles

Spend 45 minutes on TikTok searching:
1. "pokemon card binder" (find 5 creators)
2. "trading card collection" (find 5 creators)
3. "mtg tournament" (find 3 creators)
4. "pokemon pack opening" (find 5 creators)
5. #cardtok (find 2 creators)

For each, note: @handle, name, followers, one specific video detail.

### Step 2: Generate Messages

Paste your 20 handles into the batch generation prompt (Workflow 1).

### Step 3: Send

Copy each generated message, personalize further if needed, and send via TikTok DM.

### Step 4: Track

Log each outreach in your tracking spreadsheet with date sent.

### Step 5: Follow Up

Set calendar reminders for Day 5-7 and Day 14 follow-ups.

---

## Tools Integration

### If Using TikTok Shop

- Connect affiliate program through TikTok Shop Seller Center
- Generate unique affiliate links for each creator
- Track sales attribution automatically through TikTok's system
- Use TikTok's Creator Marketplace for paid campaign management

### If Using Amazon Attribution

- Create unique Amazon Attribution links for each creator
- Track traffic and sales from TikTok to Amazon listings
- Measure ROI per creator partnership
- Use data to identify highest-performing creator niches

### Spreadsheet Template

Create a Google Sheet with these tabs:
1. **Discovery Pipeline** - All found creators, scored
2. **Active Outreach** - Messages sent, status tracking
3. **Partnerships** - Active partnerships, content, sales
4. **Analytics** - Response rates, ROI, performance data

---

## Scaling Beyond Manual Outreach

### Phase 1 (Now): Manual + AI-Assisted
- Manual discovery on TikTok
- AI generates personalized messages
- Manual sending and tracking
- **Capacity**: 40-60 outreach/month

### Phase 2 (Month 2): Semi-Automated
- Use Kalodata/Fastmoss for creator discovery
- AI generates all messages
- Use scheduling tool for follow-ups
- **Capacity**: 100+ outreach/month

### Phase 3 (Month 3+): TikTok Shop Integration
- Launch TikTok Shop for Infinity Vault
- Use TikTok's affiliate marketplace for creator matching
- Automated commission tracking
- Creators apply to partner (inbound pipeline)
- **Capacity**: Unlimited (inbound + outbound)

---

*"Automation doesn't replace authenticity - it removes the friction that prevents authentic outreach at scale. The personalization makes the difference."*
