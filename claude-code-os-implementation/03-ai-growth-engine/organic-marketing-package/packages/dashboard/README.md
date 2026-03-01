# Dashboard

Next.js management interface for the Organic Marketing platform.

## Features

- System health monitoring and service status
- API key management
- Configuration management with service-specific forms
- KPI overview and metrics visualization
- Multi-tenant workspace support (Clerk authentication)
- Email sequence management
- TikTok content analytics
- AEO performance tracking

## Setup

```bash
cd packages/dashboard
npm install
cp .env.example .env.local
```

## Development

```bash
npm run dev    # Start development server on port 3000
npm run build  # Production build
npm run test   # Run tests
```

## Previous Location

Migrated from `dashboard/` in the package root.
