# Packages

Monorepo packages for the Organic Marketing system. Each package is independently buildable and testable.

## Package Overview

| Package | Language | Description |
|---------|----------|-------------|
| `content-engine/` | Python | AI content generation agents (blog, social, TikTok, AEO) with FastAPI API |
| `dashboard/` | TypeScript (Next.js) | Management interface for monitoring, configuration, and analytics |
| `mcf-connector/` | TypeScript | TikTok Shop to Amazon MCF order routing and fulfillment |
| `blog/` | TypeScript (Next.js) | SEO + AEO optimized blog for infinitycards.com |
| `shared/` | TypeScript | Shared types, utilities, and configuration used across packages |

## Development

Each package has its own dependency management:
- **Python packages**: Use `pip install -r requirements.txt` or `pip install -e .`
- **TypeScript packages**: Use `npm install` from the package directory, or `npm install` from root (workspace-aware)

## Adding a New Package

1. Create a directory under `packages/`
2. Add a `package.json` (for TS) or `pyproject.toml` (for Python)
3. Include a README explaining the package purpose
4. Register it in the root workspace configuration if applicable
