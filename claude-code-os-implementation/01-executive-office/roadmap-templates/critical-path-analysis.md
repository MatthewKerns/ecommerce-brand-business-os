# Critical Path Analysis Template

## Purpose
Identify the sequence of tasks that determines the minimum project duration. Any delay on the critical path delays the entire project.

---

## Project: [Name]
**End Goal**:
**Deadline**:
**Total Duration**:

---

## Step 1: List All Tasks

| ID | Task | Duration | Predecessors |
|----|------|----------|--------------|
| A | | days | - |
| B | | days | A |
| C | | days | A |
| D | | days | B, C |
| E | | days | D |
| F | | days | E |

---

## Step 2: Build the Network

```
         ┌──[B: X days]──┐
[A: X]──┤                ├──[D: X]──[E: X]──[F: X]
         └──[C: X days]──┘
```

---

## Step 3: Calculate Early Start/Finish

| Task | Duration | Early Start | Early Finish |
|------|----------|-------------|--------------|
| A | | Day 0 | |
| B | | | |
| C | | | |
| D | | | |
| E | | | |
| F | | | |

**Project Early Finish**: Day ___

---

## Step 4: Calculate Late Start/Finish

| Task | Duration | Late Start | Late Finish |
|------|----------|------------|-------------|
| F | | | Project End |
| E | | | |
| D | | | |
| C | | | |
| B | | | |
| A | | Day 0 | |

---

## Step 5: Calculate Float (Slack)

| Task | Early Start | Late Start | Float | Critical? |
|------|-------------|------------|-------|-----------|
| A | | | | Yes/No |
| B | | | | Yes/No |
| C | | | | Yes/No |
| D | | | | Yes/No |
| E | | | | Yes/No |
| F | | | | Yes/No |

**Float = Late Start - Early Start**
**Critical Path tasks have Float = 0**

---

## Step 6: Identify Critical Path

### Critical Path Sequence
```
[Task] → [Task] → [Task] → [Task] → [END]
   X days    X days    X days    X days
```

**Total Critical Path Duration**: ___ days

### Non-Critical Tasks (Have Float)
| Task | Float Available | Can Delay By |
|------|-----------------|--------------|
| | days | without affecting end |
| | days | without affecting end |

---

## Critical Path Management

### Protecting the Critical Path

**Daily Questions**:
1. Are all critical path tasks on schedule?
2. What's the status of today's critical task?
3. Are there any threats to critical path tasks?

**If Critical Path Slips**:
1. Can we add resources to recover?
2. Can we fast-track (parallel tasks)?
3. Can we reduce scope?
4. Must we adjust the deadline?

### Acceleration Options

| Task | Normal Duration | Crashed Duration | Cost to Crash |
|------|-----------------|------------------|---------------|
| | days | days | |
| | days | days | |

---

## Visual Timeline

### Gantt View
```
Week 1    Week 2    Week 3    Week 4
|---------|---------|---------|---------|
[====A====]
          [====B====]        (Critical)
          [==C==]            (Float: X days)
                    [====D====] (Critical)
                              [==E==] (Critical)
                                    [==F==]
```

---

## Risk Focus

### Critical Path Risks
| Task | Risk | Probability | Impact | Mitigation |
|------|------|-------------|--------|------------|
| | | H/M/L | Delays project | |
| | | H/M/L | Delays project | |

### Buffer Strategy
- **Project Buffer**: ___ days added to end
- **Feeding Buffers**: ___ days before critical path joins

---

## Monitoring Dashboard

### Current Status
| Critical Task | Status | % Complete | On Track? |
|---------------|--------|------------|-----------|
| | | | 🟢🟡🔴 |
| | | | 🟢🟡🔴 |
| | | | 🟢🟡🔴 |

### Overall Critical Path Health
- [ ] 🟢 Green: On or ahead of schedule
- [ ] 🟡 Yellow: Minor delays, recoverable
- [ ] 🔴 Red: Significant delay, deadline at risk

---

## For Infinity Vault 90-Day Plan

### Critical Path Example
```
Price Test Complete → Reference Price Set → Black Friday Prep → Execute
      (2 weeks)      →    (by Oct 20)     →    (2 weeks)     → (Nov 22)
```

**Critical Deadline**: October 20 (Reference Price)
- This is immovable
- Everything before it is on the critical path
- No float available

### R&D Critical Path
```
Ideas (100) → Screen (10) → Validate (3) → Supplier (1) → Launch Ready
 (3 weeks)  →  (2 weeks)  →  (2 weeks)  →  (3 weeks)  →   (2 weeks)
```

**Total Duration**: 12 weeks (fits in 90 days)
**No Float**: Must start immediately

---

*"Focus on the critical path. Everything else can wait if needed."*
