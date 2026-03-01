# Automatic Session Context Loading

Implement automatic loading of relevant context at the start of each session including recent work, active projects, current OBG, and pending tasks. No manual context restoration required.

## Rationale
This is THE #1 differentiator vs ChatGPT/Claude workflows (pain-6-1, gap-1). Every competitor AI tool requires users to re-explain their situation each session. Automatic context loading transforms the user experience from 'starting over' to 'continuing where you left off'.

## User Stories
- As a user, I want the AI to remember what I worked on yesterday so that I don't waste time re-explaining context
- As an entrepreneur, I want my strategic goals always present so that every conversation stays aligned with my OBG

## Acceptance Criteria
- [ ] Session starts with summary of last session's work within 5 seconds
- [ ] Active projects and their status automatically available to AI
- [ ] OBG and current tier priorities loaded without user action
- [ ] Context includes last 7 days of productivity scores
- [ ] Users can override with '/fresh' to start clean session
