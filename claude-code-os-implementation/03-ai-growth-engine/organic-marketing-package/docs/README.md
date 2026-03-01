# Organic Marketing Package - Documentation

Central documentation hub for the Organic Marketing Package.

## Quick Links

- [Setup Guide](guides/SETUP_GUIDE.md) - Get started with the full system
- [Architecture Overview](architecture/ARCHITECTURE.md) - System design and components
- [API Quick Reference](api/QUICK_REFERENCE.md) - API endpoints at a glance
- [Package Overview](planning/00-package-overview.md) - Vision, strategy, and success metrics

---

## Architecture

System design, database schemas, and technical architecture documents.

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](architecture/ARCHITECTURE.md) | Overall system architecture |
| [DATABASE_SCHEMA.md](architecture/DATABASE_SCHEMA.md) | Database tables, relationships, and migrations |
| [AEO_ANALYTICS_ARCHITECTURE.md](architecture/AEO_ANALYTICS_ARCHITECTURE.md) | How LLM model analytics are generated |
| [VIDEO_GENERATION_ARCHITECTURE.md](architecture/VIDEO_GENERATION_ARCHITECTURE.md) | Plugin-based video generation pipeline |

## API

REST API design, validation, error handling, and reference documentation.

| Document | Description |
|----------|-------------|
| [API_DESIGN.md](api/API_DESIGN.md) | API endpoints, request/response formats |
| [QUICK_REFERENCE.md](api/QUICK_REFERENCE.md) | Quick reference card for all endpoints |
| [ERROR_HANDLING.md](api/ERROR_HANDLING.md) | Error codes, retry strategies, error responses |
| [VALIDATION.md](api/VALIDATION.md) | Input validation rules and schemas |

## Guides

Setup instructions, user guides, and troubleshooting.

| Document | Description |
|----------|-------------|
| [SETUP_GUIDE.md](guides/SETUP_GUIDE.md) | Full system setup (Python, Node, DB, env vars) |
| [AUTH_SETUP.md](guides/AUTH_SETUP.md) | Clerk authentication configuration |
| [TIKTOK_SHOP_SETUP_GUIDE.md](guides/TIKTOK_SHOP_SETUP_GUIDE.md) | TikTok Shop API integration setup |
| [TIKTOK_CONTENT_STUDIO.md](guides/TIKTOK_CONTENT_STUDIO.md) | Using the TikTok Content Studio dashboard |
| [VIDEO_GENERATION_UI_GUIDE.md](guides/VIDEO_GENERATION_UI_GUIDE.md) | Video generation UI walkthrough |
| [TROUBLESHOOTING_VIDEO_GENERATOR.md](guides/TROUBLESHOOTING_VIDEO_GENERATOR.md) | Video generator troubleshooting |
| [BROWSER_EXTENSION_ERROR_FIX.md](guides/BROWSER_EXTENSION_ERROR_FIX.md) | Browser extension error resolution |
| [BLOG_CONTENT_WORKFLOW.md](guides/BLOG_CONTENT_WORKFLOW.md) | Blog content creation workflow |
| [BLOG_DEPLOYMENT.md](guides/BLOG_DEPLOYMENT.md) | Blog deployment process |
| [BLOG_DOMAIN_SETUP.md](guides/BLOG_DOMAIN_SETUP.md) | Custom domain configuration for blog |
| [TESTING_GUIDE.md](guides/TESTING_GUIDE.md) | How to run the test suite |
| [TESTING_INSTRUCTIONS.md](guides/TESTING_INSTRUCTIONS.md) | Content agents testing instructions |
| [MANUAL_TESTING.md](guides/MANUAL_TESTING.md) | Manual testing procedures |

## Planning

Phase-based planning documents for each system component.

| Phase | Component | Document |
|-------|-----------|----------|
| Overview | Package Overview | [00-package-overview.md](planning/00-package-overview.md) |
| 00 | Dashboard Foundation | [00-dashboard-foundation/](planning/00-dashboard-foundation/) |
| 01 | TikTok Content Automation | [01-tiktok-content-automation/](planning/01-tiktok-content-automation/) |
| 02 | Agentic Engine Optimization | [02-agentic-engine-optimization/](planning/02-agentic-engine-optimization/) |
| 03 | Blog Content Engine | [03-blog-content-engine/](planning/03-blog-content-engine/) |
| 04 | Email Marketing Automation | [04-email-marketing-automation/](planning/04-email-marketing-automation/) |
| 06 | Analytics & Tracking | [06-analytics-and-tracking/](planning/06-analytics-and-tracking/) |
| 07 | Service Packaging | [07-service-packaging/](planning/07-service-packaging/) |

## Verification

Test results, verification reports, and QA checklists.

| Document | Description |
|----------|-------------|
| [VERIFICATION_REPORT.md](verification/VERIFICATION_REPORT.md) | Overall verification report |
| [AEO_E2E_VERIFICATION_GUIDE.md](verification/AEO_E2E_VERIFICATION_GUIDE.md) | AEO end-to-end verification |
| [AEO_VERIFICATION_SUMMARY.md](verification/AEO_VERIFICATION_SUMMARY.md) | AEO verification results |
| [E2E_VERIFICATION.md](verification/E2E_VERIFICATION.md) | End-to-end verification |
| [E2E_TEST_README.md](verification/E2E_TEST_README.md) | E2E test documentation |
| [API_TEST_RESULTS.md](verification/API_TEST_RESULTS.md) | API test results |
| [API_MIDDLEWARE_VERIFICATION.md](verification/API_MIDDLEWARE_VERIFICATION.md) | API middleware verification |
| [AUTH_FLOW_VERIFICATION.md](verification/AUTH_FLOW_VERIFICATION.md) | Authentication flow verification |
| [BLOG_QA_CHECKLIST.md](verification/BLOG_QA_CHECKLIST.md) | Blog QA checklist |
| [BLOG_STRUCTURED_DATA_VERIFICATION.md](verification/BLOG_STRUCTURED_DATA_VERIFICATION.md) | Blog structured data verification |
| [CONFIG_MANAGEMENT_VERIFICATION.md](verification/CONFIG_MANAGEMENT_VERIFICATION.md) | Config management verification |
| [CONTENT_AGENTS_VALIDATION.md](verification/CONTENT_AGENTS_VALIDATION.md) | Content agents validation |
| [CONTENT_AGENTS_VERIFICATION_CHECKLIST.md](verification/CONTENT_AGENTS_VERIFICATION_CHECKLIST.md) | Content agents verification checklist |
| [ERROR_BOUNDARY_VERIFICATION.md](verification/ERROR_BOUNDARY_VERIFICATION.md) | Error boundary verification |
| [HEALTH_MONITOR_VERIFICATION.md](verification/HEALTH_MONITOR_VERIFICATION.md) | Health monitor verification |
| [MCF_E2E_VERIFICATION_COMPLETE.md](verification/MCF_E2E_VERIFICATION_COMPLETE.md) | MCF connector E2E verification |
| [METRICS_API_VERIFICATION.md](verification/METRICS_API_VERIFICATION.md) | Metrics API verification |
| [MOBILE_RESPONSIVENESS_VERIFICATION.md](verification/MOBILE_RESPONSIVENESS_VERIFICATION.md) | Mobile responsiveness verification |
| [RATE_LIMITING_ERROR_HANDLING_TESTING.md](verification/RATE_LIMITING_ERROR_HANDLING_TESTING.md) | Rate limiting and error handling tests |
| [TESTING_README.md](verification/TESTING_README.md) | Testing documentation |
| [REORGANIZATION_VALIDATION_CHECKLIST.md](verification/REORGANIZATION_VALIDATION_CHECKLIST.md) | Package reorganization validation checklist |
