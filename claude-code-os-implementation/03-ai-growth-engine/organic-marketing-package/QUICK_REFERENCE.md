# Quick Reference Guide

## 🚀 Common Tasks

### Start the API Server
```bash
cd packages/content-engine
source venv/bin/activate
./scripts/start_services.sh
# API runs at http://localhost:8001
# Docs at http://localhost:8001/api/docs
```

### Generate Content via API
```bash
# Blog post
curl -X POST http://localhost:8001/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your Topic", "content_pillar": "Battle-Ready Lifestyle"}'

# Social media
curl -X POST http://localhost:8001/api/social/instagram/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your Topic", "content_pillar": "Battle-Ready Lifestyle"}'
```

### Run Tests
```bash
cd packages/content-engine
pytest tests/                  # All tests
pytest tests/e2e/             # E2E tests
pytest tests/integration/     # Integration tests
```

## 📁 Key File Locations

| What | Where |
|------|-------|
| **Main API** | `packages/content-engine/src/api/main.py` |
| **API Routes** | `packages/content-engine/src/api/*.py` |
| **AI Agents** | `packages/content-engine/src/agents/*.py` |
| **Config** | `packages/content-engine/src/config/config.py` |
| **Database Models** | `packages/content-engine/src/database/models.py` |
| **Migrations** | `packages/content-engine/src/database/migrations/*.sql` |
| **Integrations** | `packages/content-engine/src/integrations/` |
| **Tests** | `packages/content-engine/tests/` |
| **Generated Content** | `packages/content-engine/output/` |
| **Environment File** | `packages/content-engine/.env` |

## 🔧 API Endpoints

### Blog Content
- `POST /api/blog/generate` - Generate blog post
- `POST /api/blog/listicle` - Generate listicle
- `POST /api/blog/howto` - Generate how-to guide
- `POST /api/blog/series` - Generate series outline

### Social Media
- `POST /api/social/instagram/generate` - Instagram post
- `POST /api/social/reddit/generate` - Reddit post
- `POST /api/social/calendar` - Content calendar
- `POST /api/social/batch` - Batch generate

### Amazon Listings
- `POST /api/amazon/title` - Product title
- `POST /api/amazon/bullets` - Bullet points
- `POST /api/amazon/description` - Description
- `POST /api/amazon/aplus` - A+ content
- `POST /api/amazon/optimize` - Optimize listing

### TikTok Shop
- `POST /api/tiktok/title` - Product title
- `POST /api/tiktok/description` - Description
- `POST /api/tiktok/video-script` - Video script
- `POST /api/tiktok/promotional` - Promo content

### Review Workflow
- `POST /api/reviews/create` - Create review
- `GET /api/reviews/{id}` - Get review
- `PUT /api/reviews/{id}` - Update review
- `POST /api/reviews/{id}/approve` - Approve review

### Tasks
- `POST /api/tasks/create` - Create async task
- `GET /api/tasks/{id}` - Get task status
- `GET /api/tasks` - List all tasks

## 🔑 Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (for specific features)
OPENAI_API_KEY=sk-...           # Embeddings
TIKTOK_APP_ID=...               # TikTok integration
TIKTOK_APP_SECRET=...          # TikTok integration
KLAVIYO_API_KEY=pk_...         # Email platform
DATABASE_URL=postgresql://...   # Production DB
REDIS_URL=redis://...          # Cache (future)
```

## 🛠️ Development Commands

### Install Dependencies
```bash
cd packages/content-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Setup
```bash
cd packages/content-engine
python src/database/init_db.py  # Run migrations
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## 📚 Available Agents

| Agent | Purpose | Key Methods |
|-------|---------|-------------|
| **BlogAgent** | Blog content | `generate_blog_post()`, `generate_listicle()` |
| **SocialAgent** | Social media | `generate_instagram_post()`, `generate_reddit_post()` |
| **AmazonAgent** | Amazon listings | `generate_title()`, `generate_bullets()` |
| **TikTokShopAgent** | TikTok Shop | `generate_video_script()`, `generate_description()` |
| **CompetitorAgent** | Analysis | `analyze_listing()`, `analyze_reviews()` |
| **AEOAgent** | AI search | `generate_aeo_content()`, `generate_featured_snippet()` |
| **SEOResearchAgent** | Keywords | `research_keywords()`, `analyze_serp()` |

## 🎯 Content Pillars

Use these in API requests:

1. **"Battle-Ready Lifestyle"** - Pre-game rituals, tournament culture
2. **"Gear & Equipment"** - Product education as battle gear
3. **"Community Champion"** - Player spotlights, LGS features
4. **"Collector's Journey"** - Collection care, card stories

## 🔍 Debugging

### Check API Logs
```bash
# API logs are printed to console
# Or check uvicorn logs in terminal
```

### Test Individual Agents
```python
from src.agents.blog_agent import BlogAgent

agent = BlogAgent()
content, path = agent.generate_blog_post(
    topic="Test Topic",
    content_pillar="Battle-Ready Lifestyle"
)
print(content)
```

### Database Queries
```python
from src.database import get_session
from src.database.models import Content

with get_session() as session:
    contents = session.query(Content).all()
    for c in contents:
        print(c.title, c.created_at)
```

## 📖 Documentation Links

- [Main README](README.md)
- [Architecture](ARCHITECTURE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Content Engine Docs](packages/content-engine/README.md)
- [API Docs](http://localhost:8001/api/docs) (when running)
- [Roadmap](/.auto-claude/roadmap/roadmap.json)

## 💡 Pro Tips

1. **API Documentation**: Always check `/api/docs` for latest endpoints
2. **Error Details**: API returns detailed error messages in JSON
3. **Async Tasks**: Use task endpoints for long-running operations
4. **Content Output**: Check `output/` directory for generated files
5. **Testing**: Write tests for new agents/routes
6. **Logging**: Enable DEBUG logging for troubleshooting

## 🆘 Common Issues

### Port Already in Use
```bash
# Kill existing process on port 8001
lsof -i :8001
kill -9 <PID>
```

### Import Errors
```bash
# Make sure you're in the right directory
cd packages/content-engine
# And virtual env is activated
source venv/bin/activate
```

### Database Issues
```bash
# Reset database
rm content.db
python src/database/init_db.py
```

### API Key Issues
```bash
# Check .env file exists and has keys
cat packages/content-engine/.env
```

## 🚀 Next Steps

1. Explore API at http://localhost:8001/api/docs
2. Try generating different content types
3. Check the roadmap for upcoming features
4. Contribute to open tasks in roadmap