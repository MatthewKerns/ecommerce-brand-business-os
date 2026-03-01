# Analytics & Tracking Plan

## Overview

Track everything. The entire organic marketing strategy lives or dies by the numbers. Saves are the primary metric, but we track the full funnel from TikTok view to purchase to prove this system works — first for Infinity Vault, then as proof when selling the service.

---

## Primary Metric: SAVES

### Why Saves Matter Most

TikTok saves are the strongest signal of purchase intent in organic content:

- **Save = "I want this later"** — either to buy or to reference
- **Educational content saves** = "I want to learn this" (Air channel)
- **Product content saves** = "I want to buy this" (Water channel)
- **Hype content saves** = "I want to share/rewatch this" (Fire channel)
- **Story content saves** = "This resonated with me" (Earth channel)

Saves also boost the TikTok algorithm more than likes, meaning high-save content gets pushed to more people organically.

### Save Rate Benchmarks
| Performance | Save Rate | What It Means |
|-------------|-----------|---------------|
| Below average | < 1% | Content not compelling enough to save |
| Average | 1-2% | Standard TikTok performance |
| Good | 2-4% | Content is resonating |
| Excellent | 4-7% | Highly valuable/desirable content |
| Viral | 7%+ | Exceptional — study and replicate |

**Our target: 3-5% average save rate across channels**

---

## Full Funnel Metrics

### Stage 1: Awareness (TikTok Content)
| Metric | Source | Tracked Per |
|--------|--------|------------|
| Video Views | TikTok API / MCF Connector | Video, Channel, Week |
| Unique Viewers | TikTok API | Channel, Week |
| Impressions | TikTok API | Video, Channel |
| Follower Count | TikTok API | Channel, Daily |
| Follower Growth Rate | Calculated | Channel, Week |

### Stage 2: Engagement (Saves + Interaction)
| Metric | Source | Tracked Per |
|--------|--------|------------|
| Saves | TikTok API / MCF Connector | Video, Channel, Week |
| Save Rate | Calculated (Saves/Views) | Video, Channel |
| Comments | TikTok API | Video, Channel |
| Shares | TikTok API | Video, Channel |
| Average Watch Time | TikTok API | Video, Channel |
| Completion Rate | TikTok API | Video, Channel |
| Profile Visits from Video | TikTok API | Video, Channel |

### Stage 3: Traffic (Click-Through)
| Metric | Source | Tracked Per |
|--------|--------|------------|
| TikTok Shop Clicks | TikTok Shop API | Video, Channel |
| Bio Link Clicks | Link tracking (UTM) | Channel, Day |
| infinitycards.com Visits (from TikTok) | GA4 / UTM | Channel, Day |
| Blog Visits (from TikTok) | GA4 / UTM | Post, Channel |

### Stage 4: Capture (Email)
| Metric | Source | Tracked Per |
|--------|--------|------------|
| Scratch & Win Impressions | Pop-up platform | Day |
| Scratch & Win Completion Rate | Pop-up platform | Day |
| Email Captures | Email platform | Day, Source |
| Capture Rate (visitors → email) | Calculated | Day |
| Game Preference Distribution | Email platform | Segment |

### Stage 5: Nurture (Email Engagement)
| Metric | Source | Tracked Per |
|--------|--------|------------|
| Email Open Rate | Email platform (Klaviyo) | Sequence, Email |
| Email Click Rate | Email platform | Sequence, Email |
| Unsubscribe Rate | Email platform | Sequence, Email |
| Sequence Completion Rate | Email platform | Sequence |

### Stage 6: Conversion (Purchase)
| Metric | Source | Tracked Per |
|--------|--------|------------|
| TikTok Shop Orders | TikTok Shop API / MCF Connector | Channel, Day |
| infinitycards.com Orders | Website platform | Source, Day |
| Revenue (TikTok Shop) | TikTok Shop API | Channel, Day |
| Revenue (Website) | Website platform | Source, Day |
| Average Order Value | Calculated | Channel, Source |
| Conversion Rate (traffic → purchase) | Calculated | Channel |
| Email → Purchase Rate | Email platform + attribution | Sequence |

### Stage 7: Fulfillment & Satisfaction
| Metric | Source | Tracked Per |
|--------|--------|------------|
| MCF Orders Created | Amazon MCF API | Day |
| Fulfillment Time | Amazon MCF API | Order |
| Shipping Transit Time | Tracking API | Order |
| Return Rate | Amazon MCF + TikTok Shop | Month |
| Review Rate | Amazon / TikTok | Month |
| Review Sentiment | Manual / AI analysis | Month |

---

## Channel Performance Dashboard

### Per-Channel Scorecard (Weekly)

```
╔══════════════════════════════════════════════════════════════╗
║  CHANNEL SCORECARD — Week of [DATE]                         ║
╠══════════════╦═══════╦═══════╦═══════╦═══════╦══════════════╣
║ Metric       ║  Air  ║ Water ║ Fire  ║ Earth ║    Total     ║
╠══════════════╬═══════╬═══════╬═══════╬═══════╬══════════════╣
║ Videos Posted║       ║       ║       ║       ║              ║
║ Total Views  ║       ║       ║       ║       ║              ║
║ Total Saves  ║       ║       ║       ║       ║              ║
║ Save Rate    ║       ║       ║       ║       ║              ║
║ Comments     ║       ║       ║       ║       ║              ║
║ Shares       ║       ║       ║       ║       ║              ║
║ New Followers║       ║       ║       ║       ║              ║
║ Shop Clicks  ║       ║       ║       ║       ║              ║
║ Orders       ║       ║       ║       ║       ║              ║
║ Revenue      ║       ║       ║       ║       ║              ║
╚══════════════╩═══════╩═══════╩═══════╩═══════╩══════════════╝
```

### Monthly Funnel Report

```
Views → Saves → Clicks → Emails → Purchases → Revenue

[Total Views]
    ↓ [Save Rate %]
[Total Saves]
    ↓ [Click Rate %]
[Site Visits]
    ↓ [Capture Rate %]
[Email Captures]
    ↓ [Conversion Rate %]
[Purchases]
    ↓ [AOV]
[Revenue]

Cost: $0 (organic)
ROAS: ∞ (technically)
Effective CPA: $0
```

---

## UTM Tracking Structure

### UTM Parameters for TikTok → Website Traffic

```
infinitycards.com?utm_source=tiktok&utm_medium=organic&utm_campaign={channel}&utm_content={video_id}
```

| Parameter | Values |
|-----------|--------|
| utm_source | tiktok |
| utm_medium | organic |
| utm_campaign | air / water / fire / earth |
| utm_content | video_id or content_description |

### Link in Bio Setup
Each channel gets a unique tracked link:
- Air: `infinitycards.com/?utm_source=tiktok&utm_medium=organic&utm_campaign=air`
- Water: `infinitycards.com/?utm_source=tiktok&utm_medium=organic&utm_campaign=water`
- Fire: `infinitycards.com/?utm_source=tiktok&utm_medium=organic&utm_campaign=fire`
- Earth: `infinitycards.com/?utm_source=tiktok&utm_medium=organic&utm_campaign=earth`

---

## Blog & AEO Tracking

### Blog Metrics
| Metric | Source | Frequency |
|--------|--------|-----------|
| Organic Traffic | GA4 | Weekly |
| Top Pages | GA4 | Weekly |
| Keyword Rankings | Search Console / Ahrefs | Weekly |
| Email Captures from Blog | Email platform | Weekly |
| Blog → Purchase Attribution | GA4 + email platform | Monthly |

### AEO Monitoring
| AI Assistant | Test Queries | Frequency | Tracked In |
|-------------|-------------|-----------|------------|
| ChatGPT | 10 target queries | Weekly | Spreadsheet |
| Claude | 10 target queries | Weekly | Spreadsheet |
| Perplexity | 10 target queries | Weekly | Spreadsheet |
| Gemini | 10 target queries | Monthly | Spreadsheet |

**AEO Score**: % of target queries where Infinity Vault appears in AI response

---

## Reporting Cadence

### Daily (Automated)
- Video views and saves for content posted that day
- New email captures
- Orders and revenue

### Weekly (Dashboard Review)
- Channel scorecard (all 4 channels)
- Save rate trends
- Top-performing content (highest save rate)
- Email sequence performance
- Revenue by source

### Monthly (Strategic Review)
- Full funnel report
- Channel comparison
- Content type analysis (which formats get most saves)
- AEO monitoring results
- Blog performance
- Month-over-month growth
- ROI calculation (time invested vs revenue generated)

### Quarterly (Service Packaging)
- Case study metrics compilation
- Before/after comparison
- Key wins and learnings
- System improvements

---

## Tools & Integrations

| Tool | Purpose | Data Flow |
|------|---------|-----------|
| MCF Connector | TikTok metrics + order fulfillment | TikTok API → Analytics |
| GA4 | Website traffic and conversion | infinitycards.com events |
| Klaviyo / Email Platform | Email metrics | Open/click/conversion data |
| Google Search Console | SEO rankings | Keyword position tracking |
| TikTok Analytics (native) | Backup/verification | In-app metrics |
| Spreadsheet/Dashboard | Consolidated reporting | Manual + API pulls |

---

## The Metrics That Sell the Service

When packaging this as a service, these are the numbers that close deals:

1. **"$0 ad spend, $X revenue"** — the headline
2. **Save rate above industry average** — content quality proof
3. **Email capture rate** — funnel effectiveness
4. **Email → purchase conversion** — automation working
5. **Month-over-month organic growth** — compound effect
6. **Ad spend reduction %** — the money saved
7. **Effective CPA vs paid CPA** — the comparison that wins
