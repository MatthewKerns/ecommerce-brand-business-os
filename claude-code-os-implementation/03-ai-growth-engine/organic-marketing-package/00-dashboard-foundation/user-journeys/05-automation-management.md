# User Journey: Automation Command Center

## Overview

The Automation Command Center is the **system-wide control panel** for all running automations across TikTok Studio, AEO Optimizer, and Email Marketing. It provides a single view to monitor, pause, resume, configure, and troubleshoot every automation in the system.

Each tab also has its own automation settings (documented in the respective user journeys). The Command Center is where you go when you need to:
- See everything running at a glance
- Make system-wide changes (pause everything, change all approval modes)
- Monitor automation health across all systems
- Review the progressive trust status across all channels
- Handle errors that span multiple systems
- Audit what automations have done

The Command Center lives as a dedicated section in the sidebar, always accessible.

---

## Navigation

```
Dashboard (/)
├── Overview
├── Quick Stats
└── System Health

🎬 TikTok Studio (/tiktok)
🔍 AEO Optimizer (/aeo)
📧 Email Marketing (/email)
───────────────────
⚡ Automation Center (/automation)  ◀── THIS JOURNEY
├── Dashboard
├── Trust & Approval
├── Health & Recovery
├── Activity Logs
└── Settings
───────────────────
📋 Content Calendar
📈 Analytics
🏷️ Brand Guide
⚙️ Settings
```

---

## Journey Map: Automation Dashboard

### Main View

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ AUTOMATION COMMAND CENTER                                 │
│                                                               │
│  SYSTEM STATUS: ● All Systems Operational                    │
│  Last check: 2 minutes ago                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ACTIVE AUTOMATIONS: 14                              │    │
│  │  Paused: 1  |  Errors: 0  |  Warnings: 2            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─ TIKTOK STUDIO ──────────────────────────────────┐       │
│  │                                                    │       │
│  │  🔥 Fire    ● Running  Smart Autopilot  5x/week  │       │
│  │  🌍 Earth   ● Running  Manual Review    4x/week  │       │
│  │  💧 Water   ● Running  Smart Autopilot  5x/week  │       │
│  │  🌬️ Air     ● Running  Manual Review    5x/week  │       │
│  │                                                    │       │
│  │  Today: 2 published, 1 scheduled, 1 in review    │       │
│  │  Trust: Fire ★★☆ | Earth ★☆☆ | Water ★★☆ | Air ★☆☆│    │
│  │                                           [Manage] │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ AEO OPTIMIZER ──────────────────────────────────┐       │
│  │                                                    │       │
│  │  Blog Generation   ● Running  Manual Review        │       │
│  │  Visibility Scan   ● Running  Weekly               │       │
│  │  Citation Tracking  ● Running  Bi-weekly           │       │
│  │  Competitor Watch   ● Running  Continuous          │       │
│  │                                                    │       │
│  │  This week: 1 post published, next scan tomorrow  │       │
│  │  Trust: Blog ★☆☆ (14/20 toward Smart Autopilot)  │       │
│  │                                           [Manage] │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ EMAIL MARKETING ────────────────────────────────┐       │
│  │                                                    │       │
│  │  Welcome Seq    ● Running  Smart Autopilot         │       │
│  │  Nurture Seq    ● Running  Manual Review           │       │
│  │  Post-Purchase  ● Running  Smart Autopilot         │       │
│  │  Win-Back       ○ Paused   (user paused 2d ago)   │       │
│  │  Platform Sync  ● Running  Real-time              │       │
│  │                                                    │       │
│  │  Today: 12 emails sent, 0 errors, 45 in queue    │       │
│  │  Trust: Welcome ★★☆ | Nurture ★☆☆ | PostP ★★☆   │       │
│  │                                           [Manage] │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  NEEDS YOUR ATTENTION                                         │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ⚠️ Win-Back sequence has been paused for 2 days.  │     │
│  │     [Resume]  [View Reason]  [Keep Paused]         │     │
│  │                                                      │     │
│  │  ⚠️ TikTok Air channel: 3 drafts awaiting review  │     │
│  │     for 48+ hours. Content may become stale.        │     │
│  │     [Review Now]  [Auto-reschedule]                 │     │
│  │                                                      │     │
│  │  💡 Fire channel eligible for Smart Autopilot       │     │
│  │     upgrade. 90.5% approval rate over 42 reviews.  │     │
│  │     [Enable Smart Autopilot]  [Keep Manual]        │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  GLOBAL ACTIONS                                               │
│  [🔴 Emergency Pause All]  [▶️ Resume All Paused]            │
│  [View Activity Logs]  [Automation Settings]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Journey: Emergency Pause

When a user clicks [Emergency Pause All]:

```
┌─────────────────────────────────────────────────────────────┐
│  🔴 EMERGENCY PAUSE — Confirm                                │
│                                                               │
│  This will immediately pause ALL automations:                │
│                                                               │
│  WILL STOP:                                                   │
│  • All TikTok auto-publishing (4 channels)                   │
│  • All email sequence sends (45 subscribers mid-sequence)    │
│  • All blog post auto-publishing                             │
│  • All scheduled campaigns                                    │
│                                                               │
│  WILL CONTINUE (monitoring only — no sends/publishes):       │
│  • AI visibility scans                                        │
│  • Citation tracking                                          │
│  • Competitor monitoring                                      │
│  • Performance data collection                                │
│                                                               │
│  Nothing is deleted. All queued content is preserved.         │
│  Subscribers mid-sequence are held in place.                  │
│  You can resume at any time.                                  │
│                                                               │
│  Duration:                                                    │
│  ○ Until I resume manually                                    │
│  ○ Pause for [24 hours ▼], then auto-resume                 │
│  ○ Pause until [date picker]                                 │
│                                                               │
│  [🔴 CONFIRM EMERGENCY PAUSE]  [Cancel]                      │
└─────────────────────────────────────────────────────────────┘
```

After confirming:

```
┌─────────────────────────────────────────────────────────────┐
│  🔴 ALL AUTOMATIONS PAUSED                                   │
│                                                               │
│  Paused at: March 1, 2026 at 2:15 PM                        │
│  Duration: Until manually resumed                             │
│                                                               │
│  What's paused:                                               │
│  ⏸️ TikTok: 4 channels paused (6 posts held in queue)       │
│  ⏸️ Email: 3 sequences paused (45 subscribers held)          │
│  ⏸️ AEO: Blog publishing paused (1 draft held)              │
│                                                               │
│  Still running (read-only monitoring):                        │
│  ● AI visibility scan  ● Citation tracking                   │
│  ● Competitor watch     ● Performance data                    │
│                                                               │
│  [▶️ Resume Everything]                                       │
│  [Resume Selectively...]                                      │
│  [View What's Queued]                                         │
└─────────────────────────────────────────────────────────────┘
```

### Selective Resume

```
┌─────────────────────────────────────────────────────────────┐
│  RESUME — Select What to Restart                             │
│                                                               │
│  TIKTOK STUDIO                                                │
│  ☑️ 🔥 Fire (2 posts queued)                                 │
│  ☑️ 🌍 Earth (1 post queued)                                 │
│  ☑️ 💧 Water (2 posts queued)                                │
│  ☐ 🌬️ Air (1 post queued) — keep paused                     │
│                                                               │
│  AEO OPTIMIZER                                                │
│  ☑️ Blog Publishing (1 draft queued)                         │
│                                                               │
│  EMAIL MARKETING                                              │
│  ☑️ Welcome Sequence (12 subscribers held)                   │
│  ☑️ Nurture Sequence (18 subscribers held)                   │
│  ☑️ Post-Purchase (15 subscribers held)                      │
│  ☐ Win-Back — keep paused (was paused before emergency)     │
│                                                               │
│  When resuming:                                               │
│  ○ Resume immediately — queued items send/publish now        │
│  ○ Resume on original schedule — items shift to next         │
│    available time slot                                        │
│  ○ Resume tomorrow at [9:00 AM ▼]                            │
│                                                               │
│  [Resume Selected]  [Cancel]                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Journey: Trust & Approval Management

### Trust Overview

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ TRUST & APPROVAL — Overview                               │
│                                                               │
│  The system earns your trust over time. As you approve        │
│  more content without edits, each automation can              │
│  progressively unlock higher autonomy levels.                 │
│                                                               │
│  TRUST LEVELS:                                                │
│  ★☆☆ Manual Review — You approve everything                  │
│  ★★☆ Smart Autopilot — Auto-publish if quality passes       │
│  ★★★ Full Autopilot — Everything runs, you review after     │
│                                                               │
│  ┌─ TIKTOK CHANNELS ───────────────────────────────┐       │
│  │                                                    │       │
│  │  🔥 Fire   ★★☆ Smart Autopilot                   │       │
│  │     42 reviewed | 90.5% no-edit | 0 rejected       │       │
│  │     Next level: 95%+ rate over 50 auto-publishes   │       │
│  │     [Downgrade to Manual]  [View History]          │       │
│  │                                                    │       │
│  │  🌍 Earth  ★☆☆ Manual Review                      │       │
│  │     8 reviewed | 75% no-edit | 0 rejected          │       │
│  │     Progress to Smart Autopilot:                   │       │
│  │     ████████████████░░░░░░░░░░ 53%                │       │
│  │     Need: 30 reviews, <15% edit rate              │       │
│  │                                                    │       │
│  │  💧 Water  ★★☆ Smart Autopilot                    │       │
│  │     35 reviewed | 91.4% no-edit | 0 rejected       │       │
│  │     Next level: 95%+ rate over 50 auto-publishes   │       │
│  │     [Downgrade to Manual]  [View History]          │       │
│  │                                                    │       │
│  │  🌬️ Air    ★☆☆ Manual Review                      │       │
│  │     12 reviewed | 83.3% no-edit | 0 rejected       │       │
│  │     Progress: ████████████████████░░░░░ 80%       │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ AEO BLOG POSTS ────────────────────────────────┐       │
│  │                                                    │       │
│  │  Blog Publishing  ★☆☆ Manual Review               │       │
│  │  14 reviewed | 78.6% no-edit                       │       │
│  │  Progress to Smart Autopilot:                      │       │
│  │  ██████████████░░░░░░░░░░░░░░ 70%                │       │
│  │  Need: 20 reviews, <10% edit rate                 │       │
│  │  (Higher bar — blog content is permanent)          │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ EMAIL SEQUENCES ───────────────────────────────┐       │
│  │                                                    │       │
│  │  Welcome      ★★☆ Smart Autopilot                 │       │
│  │  16 reviewed | 91% no-edit                         │       │
│  │  [Downgrade to Manual]  [View History]             │       │
│  │                                                    │       │
│  │  Nurture      ★☆☆ Manual Review                   │       │
│  │  10 reviewed | 72% no-edit (needs improvement)     │       │
│  │  Progress: ██████████░░░░░░░░░░░░░░░░ 44%        │       │
│  │                                                    │       │
│  │  Post-Purch   ★★☆ Smart Autopilot                 │       │
│  │  15 reviewed | 88% no-edit                         │       │
│  │  [Downgrade to Manual]  [View History]             │       │
│  │                                                    │       │
│  │  Win-Back     ★☆☆ Manual Review (insufficient data)│       │
│  │  4 reviewed | too few to assess                    │       │
│  │                                                    │       │
│  │  ⚠️ Campaigns: Always require manual approval     │       │
│  │  (by design — one-shot sends are too risky)        │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  GLOBAL ACTIONS                                               │
│  [Set Everything to Manual Review]                            │
│  [Enable Smart Autopilot for All Eligible]                   │
│  [View Trust History]                                         │
└─────────────────────────────────────────────────────────────┘
```

### Trust History & Audit

```
┌─────────────────────────────────────────────────────────────┐
│  TRUST HISTORY — 🔥 Fire Channel                             │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │                                                      │     │
│  │  March 1   ★★☆ Smart Autopilot enabled             │     │
│  │            Reason: 42 reviews, 90.5% no-edit rate  │     │
│  │            Auto-publish threshold: Quality >85     │     │
│  │                                                      │     │
│  │  Feb 15    ★☆☆ Approached threshold                │     │
│  │            30 reviews completed, rate at 86.7%     │     │
│  │            System: "Getting close to Smart Autopilot"│    │
│  │                                                      │     │
│  │  Jan 20    ★☆☆ Manual Review (initial)             │     │
│  │            Channel connected and automation started │     │
│  │                                                      │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  APPROVAL DETAIL                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Total reviews: 42                                  │     │
│  │  Approved without edits: 38 (90.5%)                │     │
│  │  Approved with minor edits: 3 (7.1%)              │     │
│  │  Approved with major edits: 1 (2.4%)              │     │
│  │  Rejected: 0 (0%)                                  │     │
│  │                                                      │     │
│  │  Edit reasons:                                      │     │
│  │  • "Changed CTA wording" (2x)                      │     │
│  │  • "Added product mention" (1x)                    │     │
│  │  • "Rewrote hook completely" (1x)                  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  Since Smart Autopilot was enabled:                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Auto-published: 8                                  │     │
│  │  Flagged for review (below threshold): 2           │     │
│  │  User overrides after auto-publish: 0              │     │
│  │                                                      │     │
│  │  Performance vs. manually reviewed:                 │     │
│  │  Auto-published avg views: 8,200                   │     │
│  │  Manually reviewed avg views: 7,900                │     │
│  │  Difference: +3.8% (autopilot performing well)     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  [Downgrade to Manual]  [Adjust Quality Threshold]           │
│  [Export Audit Report]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Journey: Health & Recovery

### System Health Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ AUTOMATION HEALTH                                         │
│                                                               │
│  SYSTEM STATUS: ● Operational (99.8% uptime, 30 days)       │
│                                                               │
│  ┌─ CONNECTIONS ────────────────────────────────────┐       │
│  │                                                    │       │
│  │  TikTok API        ● Connected    45ms   [Test]   │       │
│  │  Klaviyo            ● Connected    120ms  [Test]   │       │
│  │  Blog CMS           ● Connected    89ms   [Test]   │       │
│  │  AI Provider         ● Connected    340ms  [Test]   │       │
│  │                                                    │       │
│  │  All connections healthy. Last check: 5 min ago.  │       │
│  │  Auto-check interval: Every 5 minutes              │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ ERROR SUMMARY (Last 7 Days) ────────────────────┐       │
│  │                                                    │       │
│  │  Total errors: 4                                   │       │
│  │  Auto-recovered: 4 (100%)                          │       │
│  │  Escalated to user: 0                              │       │
│  │                                                    │       │
│  │  Breakdown:                                        │       │
│  │  • TikTok API timeout: 2 (auto-retried, resolved)│       │
│  │  • Klaviyo rate limit: 1 (auto-throttled, resumed)│       │
│  │  • AI generation timeout: 1 (retried, completed)  │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ AUTOMATION THROUGHPUT ──────────────────────────┐       │
│  │                                                    │       │
│  │  Last 7 days:                                      │       │
│  │  TikTok: 18 posts published (target: 19)  ✅      │       │
│  │  AEO: 1 blog post published (target: 1)   ✅      │       │
│  │  Email: 156 emails sent (0 failures)       ✅      │       │
│  │                                                    │       │
│  │  Approval queue latency:                           │       │
│  │  Avg time from draft to approval: 4.2 hours       │       │
│  │  Longest wait: 48 hours (Air channel draft)       │       │
│  │  ⚠️ Consider reviewing drafts more frequently,    │       │
│  │  or enabling Smart Autopilot for eligible channels│       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  [View Full Error Log]  [Configure Alert Rules]              │
│  [Run Health Check Now]  [Export Health Report]              │
└─────────────────────────────────────────────────────────────┘
```

### Error Recovery Log

```
┌─────────────────────────────────────────────────────────────┐
│  AUTOMATION — Error & Recovery Log                           │
│                                                               │
│  Filter: [All Systems ▼]  [All Severity ▼]  [Last 7 Days ▼]│
│                                                               │
│  ┌──────┬───────────┬────────────┬──────────┬─────────┐    │
│  │ Time │ System    │ Error      │ Recovery │ Status  │    │
│  ├──────┼───────────┼────────────┼──────────┼─────────┤    │
│  │ 9:58 │ TikTok    │ API timeout│ Retry 2/4│ ✅ Fixed│    │
│  │ AM   │ 🔥 Fire   │ on publish │ after 4s │         │    │
│  ├──────┼───────────┼────────────┼──────────┼─────────┤    │
│  │ 9:45 │ Klaviyo   │ Rate limit │ Throttled│ ✅ Fixed│    │
│  │ AM   │ Email     │ 429 error  │ 60s wait │         │    │
│  ├──────┼───────────┼────────────┼──────────┼─────────┤    │
│  │ Yest │ AI        │ Generation │ Retry w/ │ ✅ Fixed│    │
│  │ 3PM  │ AEO Blog  │ timeout    │ fallback │         │    │
│  ├──────┼───────────┼────────────┼──────────┼─────────┤    │
│  │ 2d   │ TikTok    │ API timeout│ Retry 1/4│ ✅ Fixed│    │
│  │ ago  │ 💧 Water  │ on metrics │ after 2s │         │    │
│  └──────┴───────────┴────────────┴──────────┴─────────┘    │
│                                                               │
│  All errors auto-recovered. No user intervention needed.     │
│                                                               │
│  [Export Log]  [Configure Alert Thresholds]                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Journey: Activity Logs

### What Automations Did

```
┌─────────────────────────────────────────────────────────────┐
│  AUTOMATION — Activity Log                                   │
│                                                               │
│  Everything your automations have done, in one feed.          │
│                                                               │
│  Filter: [All ▼]  [Today ▼]  Search: [_______________]     │
│                                                               │
│  TODAY                                                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │  10:15 AM  📧 Email: Welcome email sent to         │     │
│  │            jane@example.com (auto — Smart Autopilot)│     │
│  │                                                      │     │
│  │  10:02 AM  🎬 TikTok: "Hot take: [topic]"          │     │
│  │            published to 🔥 Fire (auto — Smart AP)   │     │
│  │            Brand check: ✅ | Quality: 92            │     │
│  │                                                      │     │
│  │  10:00 AM  📧 Email: Platform sync completed        │     │
│  │            12 new subscribers imported               │     │
│  │                                                      │     │
│  │   9:58 AM  🔄 TikTok: API timeout on publish,      │     │
│  │            auto-retried → success (attempt 2)       │     │
│  │                                                      │     │
│  │   9:45 AM  🎬 TikTok: Content generated for        │     │
│  │            🌍 Earth — queued for manual review      │     │
│  │                                                      │     │
│  │   8:00 AM  🔍 AEO: Trend scan completed,           │     │
│  │            2 content opportunities identified       │     │
│  │                                                      │     │
│  │   6:00 AM  🔍 AEO: Weekly visibility scan          │     │
│  │            Score: 34/100 (no change)                │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  YESTERDAY                                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  6:00 PM  🎬 TikTok: 💧 Water post published      │     │
│  │  3:00 PM  📧 Email: Nurture email sent (22 recip.) │     │
│  │  2:00 PM  🎬 TikTok: 🔥 Fire post flagged for     │     │
│  │           review (brand check: avoided word found)  │     │
│  │  1:00 PM  📧 Email: A/B test concluded, Variant B  │     │
│  │           wins (subject line update applied)        │     │
│  │  ...                                                │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  [Load More]  [Export Full Log]  [Configure What's Logged]  │
└─────────────────────────────────────────────────────────────┘
```

---

## Journey: Global Automation Settings

### Settings Page

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ AUTOMATION SETTINGS                                       │
│                                                               │
│  ┌─ GLOBAL DEFAULTS ───────────────────────────────┐       │
│  │                                                    │       │
│  │  Default approval mode for new automations:        │       │
│  │  ● Manual Review                                   │       │
│  │  ○ Smart Autopilot (if trust level allows)         │       │
│  │                                                    │       │
│  │  Brand check enforcement:                          │       │
│  │  ● Required (content can't publish if it fails)   │       │
│  │  ○ Advisory (flag but allow publish)              │       │
│  │  ○ Disabled (not recommended)                     │       │
│  │                                                    │       │
│  │  Quiet hours (no auto-publishing):                 │       │
│  │  [11:00 PM ▼] to [6:00 AM ▼] [Timezone ▼]       │       │
│  │  ☑️ Apply to TikTok                               │       │
│  │  ☑️ Apply to Email                                │       │
│  │  ☐ Apply to Blog (blog posts aren't time-sensitive)│      │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ ERROR RECOVERY ────────────────────────────────┐       │
│  │                                                    │       │
│  │  Auto-retry on API errors:                         │       │
│  │  ● Enabled (4 attempts, exponential backoff)      │       │
│  │  ○ Disabled (notify me immediately on first error)│       │
│  │                                                    │       │
│  │  Auto-reconnect on disconnection:                  │       │
│  │  ● Enabled (retry every 30 min for 24h)           │       │
│  │  ○ Disabled (notify me, wait for manual reconnect)│       │
│  │                                                    │       │
│  │  Auto-throttle on rate limits:                     │       │
│  │  ● Enabled (reduce frequency, auto-resume)        │       │
│  │  ○ Disabled (pause and notify)                    │       │
│  │                                                    │       │
│  │  Performance-triggered pause:                      │       │
│  │  ● Enabled (pause auto-publish if metrics drop)   │       │
│  │  ○ Disabled (keep publishing regardless)          │       │
│  │  Trigger: [3 ▼] consecutive underperformers       │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ NOTIFICATIONS ─────────────────────────────────┐       │
│  │                                                    │       │
│  │  How to receive automation alerts:                 │       │
│  │  ☑️ In-app notifications                          │       │
│  │  ☑️ Email digest (daily summary)                  │       │
│  │  ☐ SMS (critical alerts only)                     │       │
│  │  ☐ Slack webhook                                  │       │
│  │                                                    │       │
│  │  Alert me for:                                     │       │
│  │  ☑️ Errors that required escalation               │       │
│  │  ☑️ Auto-recovery events (info only)              │       │
│  │  ☑️ Trust level changes                           │       │
│  │  ☑️ Content auto-published (daily summary)        │       │
│  │  ☑️ Safety threshold breaches                     │       │
│  │  ☑️ Drafts waiting >24h for review                │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  ┌─ TRUST SYSTEM CONFIGURATION ────────────────────┐       │
│  │                                                    │       │
│  │  Trust advancement:                                │       │
│  │  ● Automatic (system prompts when eligible)       │       │
│  │  ○ Manual (I'll upgrade trust levels myself)      │       │
│  │                                                    │       │
│  │  Trust revocation:                                 │       │
│  │  ● Automatic (drops level on poor performance)    │       │
│  │  ○ Manual (warn me but don't auto-downgrade)      │       │
│  │                                                    │       │
│  │  Custom thresholds:                                │       │
│  │  TikTok — Smart Autopilot: [30 ▼] reviews,       │       │
│  │    [85% ▼] no-edit rate                           │       │
│  │  AEO — Smart Autopilot: [20 ▼] reviews,          │       │
│  │    [90% ▼] no-edit rate                           │       │
│  │  Email — Smart Autopilot: [15 ▼] reviews,        │       │
│  │    [85% ▼] no-edit rate                           │       │
│  │                                                    │       │
│  │  [Reset to Defaults]                               │       │
│  └────────────────────────────────────────────────────┘       │
│                                                               │
│  [Save Changes]  [Reset All to Defaults]                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Edge Cases

### Brand Guide Updated — Cascade Impact

When the brand guide changes, it affects all automations:

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ BRAND GUIDE UPDATED — Automation Impact                   │
│                                                               │
│  Your brand guide was just updated. Here's what's affected:  │
│                                                               │
│  QUEUED CONTENT (needs re-check):                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │  🎬 TikTok: 6 scheduled posts                      │     │
│  │  → AI is re-running brand check against new guide  │     │
│  │  → 4 passed  |  2 flagged for review               │     │
│  │                                                      │     │
│  │  🔍 AEO: 2 blog drafts                             │     │
│  │  → Re-checking brand voice match                   │     │
│  │  → 1 passed  |  1 needs voice adjustment           │     │
│  │                                                      │     │
│  │  📧 Email: 15 template emails in active sequences  │     │
│  │  → Re-checking language compliance                  │     │
│  │  → 14 passed  |  1 uses newly-avoided term         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  AUTOMATION IMPACT:                                           │
│  • Smart Autopilot temporarily paused on flagged content    │
│  • Flagged items queued for your review                      │
│  • Passed items continue as scheduled                        │
│  • Channel agents updated with new brand context             │
│                                                               │
│  [Review Flagged Content (3 items)]                          │
│  [Auto-Fix All Flagged Items]                                │
│  [Dismiss — I'll Handle Later]                               │
└─────────────────────────────────────────────────────────────┘
```

### Multiple Automations Competing

When frequency caps prevent simultaneous sends:

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ SCHEDULING CONFLICT                                       │
│                                                               │
│  Two automations want to send to the same subscriber:        │
│                                                               │
│  jane@example.com is scheduled to receive:                    │
│  📧 10:00 AM — Nurture Sequence Email 3                     │
│  📧 10:00 AM — Promotional Campaign: Spring Sale            │
│                                                               │
│  Your frequency cap: Max 1 email per subscriber per day      │
│                                                               │
│  Resolution (auto-applied based on priority rules):          │
│  ✅ Nurture Email 3 — sends at 10:00 AM (higher priority)   │
│  ⏳ Spring Sale Campaign — delayed to tomorrow 10:00 AM     │
│                                                               │
│  This was handled automatically. Adjust priority rules       │
│  in Automation Settings if you want different behavior.      │
│                                                               │
│  [View Priority Rules]  [Override This Decision]  [OK]       │
└─────────────────────────────────────────────────────────────┘
```

### Trust Level Auto-Revoked

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ TRUST LEVEL CHANGE — 🔥 Fire Channel                     │
│                                                               │
│  Smart Autopilot → Manual Review                              │
│                                                               │
│  Reason: 3 consecutive auto-published posts underperformed   │
│  target metrics (views below 50% of channel average).        │
│                                                               │
│  What this means:                                             │
│  • All Fire channel content now requires your approval       │
│  • 2 scheduled posts moved to review queue                   │
│  • Auto-publishing paused until trust is re-earned           │
│                                                               │
│  To re-earn Smart Autopilot:                                  │
│  • Review and approve 10 consecutive drafts with             │
│    <15% edit rate                                             │
│  • Performance must return to target levels                   │
│                                                               │
│  AI Analysis: "The last 3 Fire posts used a 'hot take'       │
│  format on topics that didn't resonate with your audience.   │
│  Consider mixing in more competition and reaction content    │
│  — those formats have 2x the engagement on this channel."    │
│                                                               │
│  [Review Queued Content]  [Adjust Content Strategy]          │
│  [Override — Re-enable Smart Autopilot]                       │
└─────────────────────────────────────────────────────────────┘
```

---

## How This Section Connects to Others

| Connected Tab | How Automation Center Interacts |
|--------------|-------------------------------|
| **Brand Guide** | Brand guide changes trigger content re-checks across all automations. Automation Center shows the cascade impact and manages re-approval. |
| **TikTok Studio** | Each channel's automation settings are configurable both from TikTok Studio and from the Command Center. Trust levels, pause/resume, and error recovery are synced. |
| **AEO Optimizer** | Blog generation cadence, publishing mode, and monitoring frequency are configurable from both AEO and the Command Center. |
| **Email Marketing** | Sequence status, frequency caps, safety thresholds, and platform sync are manageable from both Email Marketing and the Command Center. |
| **Analytics** | Automation throughput metrics (posts published, emails sent, error rates) feed into the analytics dashboard. |
| **Settings** | Global automation defaults, notification preferences, and trust thresholds live in Settings but are accessible from the Command Center. |

---

## Data Model

```typescript
interface AutomationState {
  id: string;
  workspaceId: string;
  globalStatus: 'operational' | 'paused' | 'emergency_paused';
  pausedAt?: Date;
  pauseExpiresAt?: Date;
  pauseReason?: string;
}

interface AutomationItem {
  id: string;
  workspaceId: string;
  system: 'tiktok' | 'aeo' | 'email';
  subsystem: string; // 'fire', 'earth', 'blog_generation', 'welcome_sequence', etc.
  status: 'running' | 'paused' | 'error' | 'disabled';
  trustLevel: 1 | 2 | 3; // Manual, Smart Autopilot, Full Autopilot
  trustStats: TrustStats;
  errorRecoveryPolicy: ErrorRecoveryPolicy;
  pausedAt?: Date;
  pauseExpiresAt?: Date;
  lastActivity: Date;
  createdAt: Date;
  updatedAt: Date;
}

interface TrustStats {
  automationItemId: string;
  totalReviews: number;
  approvedWithoutEdits: number;
  approvedWithEdits: number;
  rejected: number;
  noEditRate: number; // percentage
  autoPublished: number;
  autoPublishOverrides: number;
  overrideRate: number; // percentage
  currentLevel: 1 | 2 | 3;
  nextLevelRequirements: {
    reviewsNeeded: number;
    rateNeeded: number;
    currentProgress: number; // percentage toward next level
  };
  levelHistory: {
    level: number;
    changedAt: Date;
    reason: string; // "earned", "revoked_performance", "revoked_overrides", "manual_downgrade"
  }[];
}

interface ErrorRecoveryPolicy {
  autoRetry: boolean;
  maxRetries: number;
  backoffStrategy: 'exponential' | 'linear' | 'fixed';
  autoReconnect: boolean;
  reconnectInterval: number; // minutes
  reconnectMaxDuration: number; // hours
  autoThrottle: boolean;
  performancePause: boolean;
  performancePauseThreshold: number; // consecutive underperformers
}

interface AutomationLog {
  id: string;
  workspaceId: string;
  automationItemId: string;
  type: 'action' | 'error' | 'recovery' | 'trust_change' | 'pause' | 'resume' | 'config_change';
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  details: Record<string, any>;
  recoveryAction?: string;
  recoveryResult?: 'success' | 'failed' | 'escalated';
  timestamp: Date;
}

interface AutomationSettings {
  workspaceId: string;
  defaultApprovalMode: 'manual' | 'smart_autopilot';
  brandCheckEnforcement: 'required' | 'advisory' | 'disabled';
  quietHours: {
    enabled: boolean;
    start: string; // "23:00"
    end: string; // "06:00"
    timezone: string;
    appliesTo: ('tiktok' | 'email' | 'blog')[];
  };
  errorRecovery: {
    autoRetry: boolean;
    autoReconnect: boolean;
    autoThrottle: boolean;
    performancePause: boolean;
  };
  notifications: {
    channels: ('in_app' | 'email' | 'sms' | 'slack')[];
    alertTypes: {
      errors: boolean;
      recoveries: boolean;
      trustChanges: boolean;
      autoPublished: boolean;
      safetyBreaches: boolean;
      staleDrafts: boolean;
    };
  };
  trustConfig: {
    advancementMode: 'automatic' | 'manual';
    revocationMode: 'automatic' | 'manual';
    thresholds: {
      tiktok: { reviewsNeeded: number; noEditRate: number };
      aeo: { reviewsNeeded: number; noEditRate: number };
      email: { reviewsNeeded: number; noEditRate: number };
    };
  };
  frequencyCaps: {
    email: {
      maxPerDay: number;
      maxPerWeek: number;
      priorityOrder: string[]; // ['transactional', 'sequence', 'campaign', 'winback']
    };
    tiktok: {
      maxPerDay: number;
      minHoursBetween: number;
      maxPerWeek: number;
    };
  };
  updatedAt: Date;
}
```
