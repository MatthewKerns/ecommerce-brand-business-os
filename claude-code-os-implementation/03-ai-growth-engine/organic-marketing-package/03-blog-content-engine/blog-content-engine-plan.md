# Blog Content Engine Plan

## Overview

A systematic blog content production engine that serves two masters: traditional SEO (Google rankings) and AEO (AI assistant recommendations). Every blog post is designed to rank, get cited, and drive organic traffic to infinitycards.com.

This builds on the existing BlogAgent (`ai-content-agents/agents/blog_agent.py`) and content strategy (`04-content-team/content-strategy.md`).

---

## Blog Strategy

### Mission
Become the authoritative voice in TCG storage, tournament preparation, and card collection care. Every post reinforces the "Battle-Ready Equipment" positioning while providing genuine value that both Google and AI assistants recognize as authoritative.

### Content Pillars → Blog Categories
| Content Pillar | Blog Category | SEO Target | AEO Target |
|---------------|---------------|------------|------------|
| Battle-Ready Lifestyle | Tournament Prep & Strategy | "TCG tournament preparation" | "How to prepare for a card game tournament" |
| Gear & Equipment | Product Guides & Comparisons | "Best TCG binder" / "card binder review" | "What's the best binder for trading cards?" |
| Community Champion | Community Stories & Features | "local game store near me" / "TCG community" | "Where to play trading card games" |
| Collector's Journey | Collection Care & Education | "How to protect trading cards" | "How should I store expensive cards?" |

---

## Content Types & Templates

### 1. Authoritative Guides (AEO Priority)
**Purpose**: Answer the exact questions people ask AI assistants
**Format**: 2,000-3,000 words, comprehensive, well-structured
**Frequency**: 2/month

**Example Topics**:
- "The Complete Guide to Protecting Your Trading Card Collection"
- "Tournament Day Preparation: Everything You Need to Know"
- "How to Choose the Right Card Binder: Expert Buying Guide"

**Template Structure**:
```
1. Direct answer in first paragraph (AI extraction point)
2. Table of contents
3. Why this matters (emotional hook)
4. Detailed breakdown with H2/H3 sections
5. Product recommendations (natural Infinity Vault mention)
6. FAQ section (structured data)
7. CTA to infinitycards.com
```

### 2. Comparison & "Best Of" Posts (SEO + AEO)
**Purpose**: Win "vs" queries and buying-intent searches
**Format**: 1,500-2,500 words with comparison tables
**Frequency**: 2/month

**Example Topics**:
- "5 Best Card Binders for Serious Collectors [2026]"
- "Card Binder Comparison: What Tournament Players Actually Use"
- "Premium vs Budget Card Storage: Is It Worth the Upgrade?"

### 3. How-To & Educational Posts (Saves Driver)
**Purpose**: Provide actionable value, drive TikTok saves when cross-posted
**Format**: 1,000-1,500 words, step-by-step
**Frequency**: 4/month

**Example Topics**:
- "How to Organize Your Tournament Deck in 10 Minutes"
- "5 Signs Your Card Storage is Damaging Your Collection"
- "The Pre-Game Ritual That Wins Tournaments"

### 4. Listicles & Quick Reads (Social Amplification)
**Purpose**: Shareable content that drives social traffic and backlinks
**Format**: 800-1,200 words
**Frequency**: 2/month

**Example Topics**:
- "10 Cards That Will Be Worth 10x in 5 Years"
- "7 Mistakes New Collectors Make (And How to Avoid Them)"
- "8 Things Every Tournament Player Carries in Their Bag"

---

## Content Calendar (Monthly Template)

### Week 1
- **Monday**: Authoritative Guide post (AEO focus)
- **Wednesday**: How-To post (educational)
- **Friday**: Cross-post top-performing TikTok content as blog format

### Week 2
- **Monday**: Comparison/Best Of post (buying intent)
- **Wednesday**: How-To post (educational)
- **Friday**: Community story or LGS feature

### Week 3
- **Monday**: How-To post (educational)
- **Wednesday**: Listicle (shareable)
- **Friday**: Authoritative Guide post (AEO focus)

### Week 4
- **Monday**: Comparison post (buying intent)
- **Wednesday**: How-To post (educational)
- **Friday**: Listicle or trending topic response

**Total**: ~10-12 posts/month

---

## SEO + AEO Optimization Checklist

### Every Post Must Include:

**SEO Requirements**:
- [ ] Primary keyword in title, H1, first paragraph, URL slug
- [ ] 2-3 secondary keywords naturally integrated
- [ ] Meta description (150-160 chars) with primary keyword
- [ ] Internal links to product pages and related posts
- [ ] External links to authoritative sources
- [ ] Image alt tags with keywords
- [ ] Schema markup (Article, FAQ, HowTo as appropriate)
- [ ] Mobile-friendly formatting
- [ ] Page speed optimized (compressed images)

**AEO Requirements**:
- [ ] Direct, concise answer in first 2-3 sentences
- [ ] Clear, factual statements AI can extract
- [ ] Specific product mentions with context (not just links)
- [ ] FAQ section with Q&A format
- [ ] Unique brand positioning woven throughout
- [ ] Data points and specific numbers
- [ ] Updated date visible (AI favors fresh content)

**Brand Requirements**:
- [ ] Brand voice (confident, passionate, empowering)
- [ ] Brand language (battle-ready, gear, arsenal — NOT storage, box)
- [ ] Content pillar alignment
- [ ] CTA to infinitycards.com
- [ ] Emotional connection (identity, not just utility)

---

## Blog → TikTok → Email Cross-Pollination

Content flows between channels:

```
Blog Post: "5 Signs Your Card Storage is Damaging Your Collection"
    ↓
TikTok (Air Channel): 60-second video hitting the 5 signs
    ↓
TikTok CTA: "Full guide at infinitycards.com"
    ↓
Blog CTA: "Scratch & win for 20% off" → email capture
    ↓
Email: "Hey, remember that card storage guide? Here's a deal."
```

Every blog post should have a TikTok derivative planned. Every TikTok video with high saves should get a blog post expansion.

---

## Technical Setup (infinitycards.com)

### Blog Platform Requirements
- Fast loading (Core Web Vitals passing)
- Schema markup support
- RSS feed for content distribution
- Email capture integration (pop-up, inline forms)
- Social sharing buttons
- Related posts section
- Comment system (community engagement)
- Analytics (GA4 or equivalent)

### URL Structure
```
infinitycards.com/blog/                          (blog index)
infinitycards.com/blog/best-tcg-binders-2026/    (posts)
infinitycards.com/blog/category/tournament-prep/  (categories)
infinitycards.com/blog/category/collection-care/  (categories)
```

---

## Content Production Workflow

### Using the Existing BlogAgent

The existing `BlogAgent` in `ai-content-agents/agents/blog_agent.py` handles:
- Blog post generation with brand voice
- SEO keyword integration
- Content pillar alignment
- Listicle and how-to generation
- Blog series planning

### Enhanced Workflow
```
1. Keyword research (target queries from AEO plan)
   ↓
2. Content brief (topic, keywords, pillar, AEO queries targeted)
   ↓
3. BlogAgent generates draft
   ↓
4. Human review + edit (add personal stories, specific examples)
   ↓
5. SEO + AEO checklist pass
   ↓
6. Publish on infinitycards.com
   ↓
7. Create TikTok derivative content
   ↓
8. Share on Reddit/Discord (community channels)
   ↓
9. Track rankings + AI citations
```

---

## Metrics & Tracking

| Metric | Baseline | Month 3 Target | Month 6 Target |
|--------|----------|----------------|----------------|
| Posts published/month | 0 | 10 | 12 |
| Organic traffic/month | 0 | 1,000 | 10,000 |
| Avg time on page | — | 3+ min | 4+ min |
| Email captures from blog | 0 | 50/month | 200/month |
| Keywords ranking (top 20) | 0 | 15 | 50 |
| AI citation rate | 0% | 25% | 50% |
| Blog → TikTok saves | — | Track | Optimize |
| Blog → Purchase attribution | 0 | Track | Optimize |

---

## Priority Content Queue (First 30 Days)

1. "The Complete Guide to Protecting Your Trading Card Collection" (AEO anchor)
2. "Best Card Binders for Serious Collectors [2026]" (SEO buying intent)
3. "How to Prepare for Your First TCG Tournament" (AEO + educational)
4. "5 Signs Your Card Storage is Destroying Your Collection" (viral potential)
5. "Card Binder Comparison: Premium vs Budget" (SEO comparison)
6. "The Pre-Game Ritual: How Top Players Prepare" (brand story)
7. "10 Cards Every Pokemon Collector Should Protect" (listicle + SEO)
8. "Why Tournament Players Are Switching to Battle-Ready Gear" (brand + AEO)
