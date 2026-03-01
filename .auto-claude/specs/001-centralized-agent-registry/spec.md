# Centralized Agent Registry

Create a unified registry that catalogs all AI agents with their capabilities, prompts, input/output specifications, and invocation methods. Enables discoverability and consistent agent management.

## Rationale
Currently agent prompts are scattered across multiple markdown files making it hard to understand what agents exist and how to use them. A centralized registry addresses the technical debt and mirrors how Obsidian users struggle with plugin management (pain-2-2, pain-2-6).

## User Stories
- As a user, I want to see all available agents in one place so that I know what capabilities the system has
- As a developer, I want agent definitions standardized so that I can easily add or modify agents

## Acceptance Criteria
- [ ] Single JSON/YAML file contains all agent definitions
- [ ] Each agent has documented inputs, outputs, and trigger methods
- [ ] Agents can be listed via /agents command
- [ ] Agent prompts are validated for required fields
- [ ] Documentation auto-generated from registry
