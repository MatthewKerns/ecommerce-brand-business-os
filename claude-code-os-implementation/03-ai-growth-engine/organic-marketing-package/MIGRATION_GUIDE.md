# Migration Guide: New Monorepo Structure

## Overview

The organic-marketing-package has been reorganized into a clean monorepo structure. This guide helps you find files in their new locations.

## 📁 What Moved Where

### Old Structure → New Structure

#### Content Agents & API
```
OLD: /content-agents/
NEW: /packages/content-engine/src/

Specifically:
- agents/*.py          → packages/content-engine/src/agents/
- api/*.py            → packages/content-engine/src/api/
- config/*.py         → packages/content-engine/src/config/
- database/*.py       → packages/content-engine/src/database/
- integrations/*.py   → packages/content-engine/src/integrations/
```

#### AI Content Agents (from root)
```
OLD: /ai-content-agents/
NEW: /packages/content-engine/src/agents/
```

#### API Implementation
```
OLD: /api/
NEW: /packages/content-engine/src/api/
```

#### Tests
```
OLD: /content-agents/tests/
NEW: /packages/content-engine/tests/
```

#### Documentation
```
OLD: /content-agents/docs/
NEW: /packages/content-engine/docs/
```

#### Scripts
```
OLD: /content-agents/scripts/
NEW: /packages/content-engine/scripts/
```

#### Configuration Files
```
OLD: /content-agents/config/
NEW: /packages/content-engine/src/config/
```

#### Output Files
```
OLD: /content-agents/output/
NEW: /packages/content-engine/output/
```

## 🚀 Quick Start Commands

### Starting the API Server

**Old way:**
```bash
cd content-agents
python api/main.py
```

**New way:**
```bash
cd packages/content-engine
./scripts/start_services.sh
# OR
python src/api/main.py
```

### Running Tests

**Old way:**
```bash
cd content-agents
pytest tests/
```

**New way:**
```bash
cd packages/content-engine
pytest tests/
```

### Generating Content

**Old way:**
```bash
cd ai-content-agents
python generate_content.py blog post "Topic"
```

**New way:**
```bash
cd packages/content-engine
python src/generate_content.py blog post "Topic"
# OR use the API:
curl -X POST http://localhost:8001/api/blog/generate
```

## 📦 Import Path Updates

If you have existing scripts that import from the old structure, update them:

### Python Imports

**Old:**
```python
from agents.blog_agent import BlogAgent
from api.routes import blog_router
from config.config import BRAND_NAME
```

**New:**
```python
# When running from packages/content-engine directory:
from src.agents.blog_agent import BlogAgent
from src.api.routes import blog_router
from src.config.config import BRAND_NAME
```

### Environment Variables

The `.env` file should now be placed at:
```
packages/content-engine/.env
```

## 🔄 Git History

All files were moved with `git mv`, so history is preserved. You can still view the full history of any file:

```bash
git log --follow packages/content-engine/src/agents/blog_agent.py
```

## 📊 Consolidated Features

The reorganization merged multiple overlapping implementations:

1. **Agents**: All agent implementations are now in `src/agents/`
2. **API Routes**: All 17 route modules are in `src/api/`
3. **Database**: Single consolidated database module in `src/database/`
4. **Integrations**: All external integrations in `src/integrations/`

## 🎯 Benefits of New Structure

1. **Single Source of Truth**: No more duplicate files
2. **Clear Organization**: Logical separation of concerns
3. **Easier Testing**: Tests mirror source structure
4. **Better Imports**: Cleaner import paths
5. **Monorepo Ready**: Prepared for additional packages

## 🔍 Finding Specific Files

### Key Files and Their New Locations

| Component | New Location |
|-----------|--------------|
| Main API | `packages/content-engine/src/api/main.py` |
| Blog Agent | `packages/content-engine/src/agents/blog_agent.py` |
| Social Agent | `packages/content-engine/src/agents/social_agent.py` |
| Database Models | `packages/content-engine/src/database/models.py` |
| Config | `packages/content-engine/src/config/config.py` |
| TikTok Integration | `packages/content-engine/src/integrations/tiktok_shop/` |
| Klaviyo Integration | `packages/content-engine/src/integrations/klaviyo/` |
| E2E Tests | `packages/content-engine/tests/e2e/` |
| API Docs | `http://localhost:8001/api/docs` (when running) |

## 💡 Tips

1. **Virtual Environment**: Create a fresh venv in `packages/content-engine/`
2. **Dependencies**: Use the consolidated `requirements.txt` in `packages/content-engine/`
3. **API Port**: The API now runs on port 8001 by default
4. **Documentation**: Main docs are in the package-level README files

## 🆘 Troubleshooting

### Can't find a file?
```bash
# Search for it in the new structure:
find packages/content-engine -name "*.py" | grep -i "filename"
```

### Import errors?
- Make sure you're in the correct directory (`packages/content-engine`)
- Update import paths to include `src.`
- Check that your virtual environment is activated

### API not starting?
```bash
cd packages/content-engine
source venv/bin/activate
pip install -r requirements.txt
./scripts/start_services.sh
```

## 📝 Notes

- The reorganization was completed on March 1, 2026
- All functionality has been preserved
- No breaking changes to the API endpoints
- Database schema remains unchanged

## 🚀 Next Steps

1. Update any local scripts to use new paths
2. Pull the latest changes from main branch
3. Recreate virtual environment in new location
4. Start using the consolidated structure

For questions or issues, check the main [README](README.md) or the [Content Engine README](packages/content-engine/README.md).