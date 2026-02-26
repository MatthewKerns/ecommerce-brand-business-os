# E-Commerce Brand Business OS

An AI-powered Business Operating System for running an e-commerce brand with Claude Code. Built on 13 productivity principles refined over 20 years, this system automates planning, tracks productivity, maintains strategic alignment, and generates brand-aligned content at scale.

## Overview

This repository contains two integrated components:

1. **Business Operating System** (`claude-code-os-implementation/`) — A structured framework of AI agents, templates, workflows, and knowledge bases organized into 10 departments. Designed to be used with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) as the execution layer.

2. **AI Content Agents** (`ai-content-agents/`) — A Python toolkit that uses the Anthropic API to generate brand-aligned marketing content across blog, social media, Amazon listings, and competitor analysis channels.

The business context is **Infinity Vault**, a premium trading card binder brand sold via Amazon FBA, positioned as "Battle-Ready Equipment" for serious TCG/Pokemon collectors and tournament players.

## Repository Structure

```
ecommerce-brand-business-os/
├── README.md                          # This file
├── ai-content-agents/                 # Python content generation toolkit
│   ├── agents/                        # Specialized AI agents (blog, social, Amazon, competitor)
│   ├── config/                        # Configuration and brand settings
│   ├── generate_content.py            # CLI entry point
│   ├── quick_start.py                 # Quick start examples
│   ├── test_setup.py                  # Setup verification
│   └── requirements.txt               # Python dependencies
├── claude-code-os-implementation/     # Business Operating System
│   ├── 01-executive-office/           # Strategic planning & daily roadmaps
│   ├── 02-operations/                 # Productivity tracking & project management
│   ├── 03-ai-growth-engine/           # Strategic framework, positioning & growth
│   ├── 04-content-team/               # Content strategy & brand voice
│   ├── 05-hr-department/              # AI agent creation & management
│   ├── 06-knowledge-base/             # Core principles, architecture & reference docs
│   ├── 07-workflows/                  # Daily, weekly & monthly routines
│   ├── 08-technical-architecture/     # System design & integrations
│   ├── 09-templates/                  # Reusable prompts, agent guides & design briefs
│   └── 10-implementation-roadmap/     # Phased rollout plan & 12-month roadmap
└── original_youtube_transcript.txt    # Source transcript for the system demo video
```

## Business OS Departments

### 01 — Executive Office
Strategic planning and daily roadmap generation. Includes daily/weekly/monthly planning automation, strategic alignment verification, priority-based task organization (Tier 1/2/3), and OBG (One Big Obsessional Goal) tracking.

### 02 — Operations
Productivity tracking and project management. Daily productivity assessments on a 1-10 scale, project status monitoring, pattern recognition in work habits, and metrics dashboards.

### 03 — AI Growth Engine
Strategic advisory and business alignment. Houses the business definition (model, value proposition, target market, competitive advantage), strategic framework (vision, mission, OBG, pillars), market positioning, Amazon listings upgrade plans, and TikTok influencer outreach playbooks.

### 04 — Content Team
Content strategy and brand voice guidelines. Defines the brand voice, content pillars, and implementation plan for the Magnetic Content OS.

### 05 — HR Department
AI agent creation and management. Framework for building, refining, and deploying custom AI agents with consistent quality.

### 06 — Knowledge Base
The persistent memory layer. Contains the 13 foundational principles, system architecture documentation, the CTRCVR designer guide, and cross-department knowledge integration.

### 07 — Workflows
Automated daily, weekly, and monthly routines. Includes the complete daily workflow (morning planning, midday check, evening assessment), weekly strategic planning, monthly reviews, design production workflows, and Fiverr hiring SOPs.

### 08 — Technical Architecture
System design documentation covering the distributed AI agent architecture, inter-agent communication, memory systems, and department integration.

### 09 — Templates
Reusable assets including agent creation guides, design brief templates, and specific prompt examples.

### 10 — Implementation Roadmap
The master implementation guide (12-week phased rollout) and a 12-month automation roadmap for scaling the system.

## AI Content Agents

A Python-based content generation system with four specialized agents:

| Agent | Purpose |
|---|---|
| **BlogAgent** | SEO-optimized blog posts, listicles, how-to guides, series outlines |
| **SocialAgent** | Instagram captions, Reddit posts, carousel scripts, content calendars |
| **AmazonAgent** | Product titles, bullet points, descriptions, A+ content, backend keywords |
| **CompetitorAgent** | Listing analysis, review mining, multi-competitor comparison, content gap identification |

All generated content is automatically infused with the Infinity Vault brand voice and "Battle-Ready" positioning.

See [`ai-content-agents/README.md`](ai-content-agents/README.md) for full usage instructions.

## Architecture

The system follows a **hybrid monorepo architecture** that separates business knowledge from execution logic:

### Design Principles

1. **Separation of Concerns**: Business knowledge (markdown) is separated from execution logic (Python)
2. **Inheritance-Based Agent Design**: All specialized agents inherit from a common `BaseAgent` class
3. **Configuration-Driven**: Brand context and settings are centralized in configuration files
4. **Path-Based Organization**: Clear directory structure for discoverability and maintenance
5. **Zero Friction Execution**: Simple CLI interfaces and minimal setup requirements

### Agent Hierarchy

```
BaseAgent (base_agent.py)
    │
    ├── BlogAgent - SEO-optimized long-form content
    ├── SocialAgent - Platform-specific social media content
    ├── AmazonAgent - E-commerce listing optimization
    └── CompetitorAgent - Market analysis and insights
```

### Data Flow

```
Brand Knowledge (markdown) → config.py → BaseAgent → Specialized Agent → Anthropic API → Generated Content
```

All agents automatically load brand voice, strategy, and positioning from the knowledge layer and inject it into their prompts.

**Read more:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## API

The AI Content Agents system provides both CLI and programmatic interfaces:

### Command Line Interface (CLI)

```bash
# Universal content generation
python generate_content.py blog post "Your Topic" --pillar "Battle-Ready Lifestyle" --words 1500
python generate_content.py social instagram "Topic" --image "Image description"
python generate_content.py amazon title "Product Name" --features "feature1,feature2"
```

### Python API

```python
from agents import BlogAgent, SocialAgent, AmazonAgent

# Generate blog post
blog_agent = BlogAgent()
content, path = blog_agent.generate_blog_post(
    topic="10 Tournament Mistakes TCG Players Make",
    content_pillar="Battle-Ready Lifestyle",
    word_count=1500
)

# Generate social content
social_agent = SocialAgent()
content, path = social_agent.generate_instagram_post(
    topic="Pre-tournament ritual",
    content_pillar="Battle-Ready Lifestyle"
)
```

### REST API (Planned)

A FastAPI-based REST API is planned for Phase 2, exposing:
- `POST /api/content/generate` - Universal content generation
- `POST /api/blog/generate` - Blog-specific generation
- `POST /api/social/generate` - Social media generation
- `POST /api/amazon/generate` - Amazon listing optimization

**Read more:** [`docs/API_DESIGN.md`](docs/API_DESIGN.md)

## Testing

The system maintains **70% minimum test coverage** to ensure reliability and prevent regressions.

### Running Tests

```bash
cd ai-content-agents

# Run all tests
pytest

# Run with coverage report
pytest --cov=ai-content-agents --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=ai-content-agents --cov-report=html
open htmlcov/index.html

# Fail if coverage is below 70%
pytest --cov=ai-content-agents --cov-report=term-missing --cov-fail-under=70
```

### Test Structure

```
ai-content-agents/tests/
├── conftest.py                 # Shared fixtures
├── fixtures/                   # Mock API responses
├── test_base_agent.py          # BaseAgent tests
├── test_blog_agent.py          # BlogAgent tests
├── test_social_agent.py        # SocialAgent tests
├── test_amazon_agent.py        # AmazonAgent tests
└── test_api.py                 # API integration tests
```

### Testing Philosophy

- **Test First, Fix Later**: Write tests before implementing new features
- **Isolated Testing**: Tests should not rely on external services (mocked APIs)
- **Fast Feedback**: Unit tests run in seconds
- **Real-World Scenarios**: Integration tests mirror actual usage

**Read more:** [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md)

## The 13 Foundational Principles

These principles, refined over 20 years, form the backbone of the system:

**Foundation Philosophy**
1. The Entropy Principle — Accept imperfection, focus on what matters
2. Zero Friction Discipline — Remove barriers to create sustainable discipline
3. The Spartan Rule — Lean operations with brutal elimination

**Execution Mechanics**
4. Breaking Constraints — Find the bottleneck and break it
5. Today Over Tomorrow — Execute now, plan later
6. Input Over Output — Control what you can control

**Strategic Alignment**
7. One Big Obsessional Goal (OBG) — Single-point focus
8. Strategic Filtering — Every action must serve the OBG
9. Alignment Checking — Continuous verification against priorities

**Force Multipliers**
10. AI Agent Teams — Specialized agents for specialized tasks
11. Compound Learning — Every interaction improves the system
12. Persistent Memory — No lost context or forgotten projects
13. Frictionless Execution — Systems that run themselves

## Getting Started

### Business OS (Claude Code)

1. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
2. Read the [START_HERE guide](claude-code-os-implementation/01-executive-office/START_HERE.md)
3. Define your OBG (One Big Obsessional Goal)
4. Generate your first daily roadmap
5. Configure daily/weekly/monthly workflows from `07-workflows/`

### AI Content Agents (Python)

```bash
cd ai-content-agents
pip install -r requirements.txt
export ANTHROPIC_API_KEY='your-api-key'

# Generate content
python generate_content.py blog post "Your Topic Here" --pillar "Battle-Ready Lifestyle" --words 1500
python generate_content.py social instagram "Your topic" --image "Description of image"
python generate_content.py amazon title "Product Name" --features "feature1,feature2"
```

See [`ai-content-agents/README.md`](ai-content-agents/README.md) for the full CLI reference and Python API.

## Configuration

Both the Business OS and AI Content Agents require proper configuration before use. The system supports multi-environment deployment (development, staging, production) with secure credential management.

### Quick Configuration Setup

1. **Generate encryption keys** for secure credential storage:
   ```bash
   # For Python services
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

   # For TypeScript services
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```

2. **Create environment files** from examples:
   ```bash
   # Python AI content agents
   cd ai-content-agents
   cp .env.example .env.development

   # TypeScript email automation (if applicable)
   cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation
   cp .env.example .env.development
   ```

3. **Configure credentials** in `.env.development`:
   ```bash
   ENVIRONMENT=development
   ENCRYPTION_KEY=your-generated-key
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

4. **Verify setup**:
   ```bash
   # Python service
   cd ai-content-agents
   python test_setup.py

   # TypeScript service (if applicable)
   npm run build
   ```

### Full Configuration Guide

For complete documentation on configuration, secrets management, OAuth setup, multi-environment deployment, and troubleshooting, see:

**[📖 CONFIGURATION.md](CONFIGURATION.md)** — Complete configuration and secrets management guide

Topics covered:
- Environment-specific configuration (development/staging/production)
- Secure credential storage with encryption
- Gmail OAuth setup for email automation
- API key management (Anthropic, Google, OpenAI)
- Security best practices and secrets rotation
- CI/CD integration and deployment checklists
- Troubleshooting common configuration issues

## Built With

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — Anthropic's CLI for AI-powered development and automation
- [Anthropic API](https://docs.anthropic.com/) — Claude AI models for content generation
- Python 3 — AI content agent runtime
- Markdown — Knowledge base, templates, and documentation format

---

*"The easier it is to do the right thing, the more likely you will do it consistently."*
