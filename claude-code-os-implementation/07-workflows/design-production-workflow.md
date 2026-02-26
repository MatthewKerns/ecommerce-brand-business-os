# Design Production Workflow

*End-to-end process for creating listing images and brand assets*

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DESIGN PRODUCTION PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. IDENTIFY      2. BRIEF         3. SOURCE        4. PRODUCE         │
│  ─────────────    ─────────────    ─────────────    ─────────────      │
│  What needs       Fill out         Find & hire      Execute &          │
│  design work?     design brief     freelancer       iterate            │
│       │                │                │                │             │
│       ▼                ▼                ▼                ▼             │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐       │
│  │CTR/CVR  │      │Template │      │Fiverr   │      │Review   │       │
│  │Analysis │─────▶│Complete │─────▶│Posting  │─────▶│Cycles   │       │
│  └─────────┘      └─────────┘      └─────────┘      └─────────┘       │
│                                                           │             │
│                                                           ▼             │
│  5. VALIDATE      6. DEPLOY        7. TEST          8. ITERATE        │
│  ─────────────    ─────────────    ─────────────    ─────────────      │
│  Brand & CTR      Upload to        A/B test vs      Learn &           │
│  check            Amazon           current          repeat            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: IDENTIFY (What Needs Design?)

### Trigger Points for New Design Work

| Trigger | Priority | Action |
|---------|----------|--------|
| CTR below benchmark (<3%) | High | Main image redesign |
| CVR below benchmark (<15%) | High | Secondary images / A+ content |
| New product launch | Critical | Full image set needed |
| Competitor improving | Medium | Differentiation update |
| Seasonal campaign | Medium | Promotional assets |
| A/B test needed | Standard | Variant creation |

### Decision Matrix

```
Is CTR below target?
    │
    ├── YES → Main Image Redesign Project
    │         └── Fill out Design Brief (Main Image focus)
    │
    └── NO → Is CVR below target?
              │
              ├── YES → Secondary Images / A+ Content Project
              │         └── Fill out Design Brief (CVR focus)
              │
              └── NO → Maintain current assets
                       └── Schedule quarterly refresh review
```

### Weekly Design Review Checklist
- [ ] Review CTR/CVR metrics for all ASINs
- [ ] Check competitor main images for changes
- [ ] Identify any underperforming listings
- [ ] Prioritize design projects for the week
- [ ] Allocate budget for freelancer work

---

## Phase 2: BRIEF (Create the Design Brief)

### Process
1. Open `09-templates/design-brief-template.md`
2. Copy template to new file: `designs/briefs/[ASIN]-[AssetType]-[Date].md`
3. Complete ALL sections
4. Gather reference images
5. Prepare brand asset links
6. Review brief for completeness

### Brief Quality Checklist
- [ ] Project name and deadline clear
- [ ] Brand requirements specified
- [ ] CTR/CVR optimization requirements included
- [ ] Specific creative direction provided
- [ ] Reference images attached
- [ ] Technical specs correct
- [ ] Deliverables listed

### Time Investment
- Simple brief (main image variant): 15-20 minutes
- Complex brief (full image set): 45-60 minutes
- A+ content brief: 30-45 minutes

---

## Phase 3: SOURCE (Find & Hire Freelancer)

### Fiverr Search Strategy

**Search Terms**:
- "Amazon product photography"
- "Amazon main image design"
- "Product rendering 3D"
- "Amazon listing images"
- "A+ content design Amazon"

**Filter Criteria**:
- Seller Level: Level 2 or Top Rated
- Reviews: 4.8+ stars, 50+ reviews minimum
- Delivery: Within your deadline
- Price: Budget-appropriate

### Freelancer Evaluation Checklist

| Criteria | Weight | Check |
|----------|--------|-------|
| Portfolio quality matches our style | 30% | [ ] |
| Experience with Amazon listings | 20% | [ ] |
| Reviews mention communication | 15% | [ ] |
| Turnaround time fits deadline | 15% | [ ] |
| Price within budget | 10% | [ ] |
| Offers revisions | 10% | [ ] |

### Budget Guidelines

| Asset Type | Budget Range | Notes |
|------------|--------------|-------|
| Main Image (render) | $50-150 | Higher for complex products |
| Main Image (photography) | $100-300 | Includes product shipping |
| Secondary Images (set of 6) | $150-400 | Infographics included |
| A+ Content Module | $50-100 per module | 5-7 modules typical |
| Full Listing Package | $300-800 | Main + secondary + A+ |

### Hiring Message Template

```
Hi [Name],

I'm looking for [specific asset type] for my Amazon listing.

BRAND: Infinity Vault - Premium TCG storage (card binders, deck boxes)
STYLE: Battle-ready, premium feel, dramatic lighting, metallic accents

WHAT I NEED:
- [Specific deliverable 1]
- [Specific deliverable 2]
- [Specific deliverable 3]

I have:
✓ Product renders/photos
✓ Brand guidelines and color codes
✓ Reference images for style direction
✓ Clear technical specifications

TIMELINE: [Your deadline]

Before ordering, can you confirm:
1. You can match the premium style shown in [reference]?
2. Turnaround time for first draft?
3. What's included in revisions?

Thanks!
```

---

## Phase 4: PRODUCE (Execute & Iterate)

### Handoff to Designer

1. **Initial Order**
   - Place order with requirements in description
   - Attach design brief PDF
   - Share brand assets folder (Dropbox/Drive link)
   - Set clear first draft deadline

2. **Kick-off Message**
   - Confirm they received all assets
   - Ask for any clarifying questions
   - Establish communication cadence

### Review Process

**Draft 1 Review** (24-48 hours after delivery):
- [ ] Does it match the brief direction?
- [ ] Brand colors and feel correct?
- [ ] Technical specs met?
- [ ] Initial gut reaction - would this win clicks?

**Feedback Format**:
```
OVERALL: [Good start / Needs work / Major revision needed]

KEEP:
- [What's working well]
- [Elements to preserve]

CHANGE:
- [Specific change 1 + why]
- [Specific change 2 + why]

QUESTIONS:
- [Any clarifying questions]
```

**Draft 2 Review**:
- [ ] Previous feedback addressed?
- [ ] Any new issues introduced?
- [ ] Ready for brand check?

---

## Phase 5: VALIDATE (Brand & CTR Check)

### Brand Compliance Checklist

| Element | Requirement | Pass? |
|---------|-------------|-------|
| Color palette | Black + gold/silver metallics | [ ] |
| Typography | Bold, clean, professional | [ ] |
| Imagery feel | Premium, not commodity | [ ] |
| Language | "Battle-ready" vocabulary | [ ] |
| Trust signals | Warranty badge visible | [ ] |
| Overall vibe | Hero archetype energy | [ ] |

### CTR Prediction Checklist

| Factor | Check |
|--------|-------|
| Stands out in Amazon search grid | [ ] |
| Product clearly visible | [ ] |
| Differentiated from competitors | [ ] |
| Quality signals obvious | [ ] |
| Would YOU click this? | [ ] |

### Final Approval Questions
1. Does this feel "Battle-Ready"?
2. Would this make a customer feel empowered?
3. Does this look premium, not commodity?
4. Is there a clear reason to click?

---

## Phase 6: DEPLOY (Upload to Amazon)

### Pre-Upload Checklist
- [ ] Final files downloaded
- [ ] Correct dimensions verified
- [ ] File names organized
- [ ] Current images backed up
- [ ] Test timing considered (avoid launches during high-traffic periods)

### Upload Process
1. Go to Amazon Seller Central → Inventory → Manage Inventory
2. Select ASIN → Edit
3. Navigate to Images tab
4. Upload new image(s)
5. Save and verify preview
6. Document upload date for testing

### Post-Upload Verification
- [ ] Images displaying correctly
- [ ] No Amazon rejection/warnings
- [ ] Mobile view checked
- [ ] Compare to competitor grid

---

## Phase 7: TEST (A/B Test vs Current)

### Test Setup (Amazon Manage Your Experiments)

1. Navigate to Brands → Manage Your Experiments
2. Select "A+ Content" or "Main Image" experiment
3. Upload test variant
4. Set test duration (minimum 7 days)
5. Define success metric (CTR for main image)

### Alternative Testing (ProductPinion)
- Use for pre-launch validation
- Compare 2-4 variants before going live
- Quick turnaround (24-48 hours)
- Lower risk than live testing

### Testing Rules
| Rule | Reason |
|------|--------|
| One variable at a time | Know what caused the change |
| Minimum 7 days | Statistical significance |
| Document everything | Build learnings database |
| Winner becomes new control | Continuous improvement |

---

## Phase 8: ITERATE (Learn & Repeat)

### Post-Test Analysis

**Document for Each Test**:
```
TEST: [Name]
DATE: [Start] - [End]
VARIANT A: [Description]
VARIANT B: [Description]
RESULT: [Winner + % improvement]
LEARNING: [What did we learn?]
NEXT TEST: [What to test next based on this]
```

### Learning Database
Store all test results in: `02-operations/metrics/testing/image-tests-log.md`

### Continuous Improvement Cycle
```
Test Result
    │
    ├── Winner found → Deploy winner → Plan next test
    │
    └── No winner → Analyze why → Create new hypothesis → Test again
```

---

## Quick Reference: Project Timelines

| Project Type | Brief | Hire | Produce | Validate | Deploy | Test | Total |
|--------------|-------|------|---------|----------|--------|------|-------|
| Main Image | 1 day | 1 day | 3-5 days | 1 day | 1 day | 7+ days | 2-3 weeks |
| Image Set | 1 day | 1-2 days | 5-7 days | 1-2 days | 1 day | 7+ days | 3-4 weeks |
| A+ Content | 1 day | 1-2 days | 7-10 days | 2 days | 1 day | 14+ days | 4-5 weeks |

---

## Automation Opportunities

### Now (Manual but Systematized)
- Template-based brief creation
- Saved Fiverr seller list
- Standardized feedback format
- Testing log documentation

### Future (Partial Automation)
- AI-generated brief first drafts
- Automated test result tracking
- Competitor image monitoring alerts
- Performance dashboard integration

### Long-term (Service/Agency)
- DesignForce subscription (unlimited designs)
- Dedicated designer relationship
- Faster turnaround, consistent quality
- No hiring overhead per project

---

*"The fastest path to automated listing design is systematized processes with clear handoffs. Perfect the system first, then scale."*
