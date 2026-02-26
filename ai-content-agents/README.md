# Infinity Vault AI Content Agents

AI-powered content generation system for creating brand-aligned marketing content at scale.

## 🎯 What This Does

This system uses Claude AI to generate high-quality, on-brand content for Infinity Vault across multiple channels:

- **Blog Posts**: SEO-optimized articles, listicles, how-to guides
- **Social Media**: Instagram captions, Reddit posts, content calendars
- **Amazon Listings**: Titles, bullet points, descriptions, A+ content
- **Competitor Analysis**: Listing analysis, review mining, content gaps

All content is automatically infused with:
- Infinity Vault brand voice (confident, passionate, empowering)
- "Battle-Ready" positioning (equipment, not commodity storage)
- Fantasy/gaming language
- Customer identity focus (serious players, not casual hobbyists)

## 🏗️ Architecture

This system uses an **inheritance-based agent design** where all specialized agents extend a common `BaseAgent` class.

### Design Patterns

**1. Template Method Pattern**

The `BaseAgent` class defines the skeleton of content generation:
- `_load_brand_context()`: Loads brand voice, strategy, and positioning from markdown files
- `_build_system_prompt()`: Constructs AI system prompt with brand context
- `generate_content()`: Core generation method using Anthropic API
- `save_output()`: Standardized file saving with metadata

**2. Configuration Centralization**

All paths, API keys, and brand constants are defined in `config/config.py`:
```python
# Brand knowledge paths
BRAND_VOICE_PATH = "../claude-code-os-implementation/04-content-team/brand-voice-guide.md"
BRAND_STRATEGY_PATH = "../claude-code-os-implementation/03-ai-growth-engine/positioning/brand-strategy.md"

# Brand identity
BRAND_NAME = "Infinity Vault"
BRAND_TAGLINE = "Show Up Battle Ready"
```

**3. Agent Hierarchy**

```
BaseAgent
    ├── BlogAgent (SEO-optimized blog content)
    ├── SocialAgent (Platform-specific social media)
    ├── AmazonAgent (E-commerce optimization)
    └── CompetitorAgent (Market analysis)
```

### Data Flow

```
Brand Markdown Files → config.py → BaseAgent._load_brand_context()
    → Specialized Agent Methods → Anthropic API → Generated Content + Metadata
```

**Read more:** [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai-content-agents
pip install -r requirements.txt
```

### 2. Set Your API Key

Get your Anthropic API key from https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your key
```

### 3. Generate Content!

**Option A: Quick Start Script (Easiest)**

```bash
# Edit quick_start.py and uncomment an example
python quick_start.py
```

**Option B: Command Line Interface**

```bash
# Generate a blog post
python generate_content.py blog post "How to Prepare for Your First TCG Tournament" --pillar "Battle-Ready Lifestyle" --words 1500

# Generate Instagram post
python generate_content.py social instagram "Tournament prep essentials" --image "Player organizing deck in Infinity Vault binder"

# Generate Amazon title
python generate_content.py amazon title "Premium Trading Card Binder" --features "scratch-resistant,9-pocket,lifetime warranty" --keywords "tcg binder,pokemon storage"

# Generate 7-day content calendar
python generate_content.py social calendar --for-platform instagram --days 7
```

**Option C: Use in Your Own Python Scripts**

```python
from agents import BlogAgent, SocialAgent, AmazonAgent

# Generate blog post
blog_agent = BlogAgent()
content, path = blog_agent.generate_blog_post(
    topic="10 Tournament Mistakes TCG Players Make",
    content_pillar="Battle-Ready Lifestyle",
    word_count=1500
)

# Generate Instagram post
social_agent = SocialAgent()
content, path = social_agent.generate_instagram_post(
    topic="Pre-tournament ritual",
    content_pillar="Battle-Ready Lifestyle"
)

# Generate Amazon bullets
amazon_agent = AmazonAgent()
content, path = amazon_agent.generate_bullet_points(
    product_name="Premium Card Binder",
    features=[
        {"feature": "Scratch-resistant pages", "benefit": "Cards stay pristine"},
        {"feature": "Lifetime warranty", "benefit": "Investment protection"}
    ]
)
```

## 📚 Available Agents

### BlogAgent
Creates SEO-optimized blog content:
- `generate_blog_post()` - Full blog articles
- `generate_listicle()` - "Top 10" style posts
- `generate_how_to_guide()` - Step-by-step guides
- `generate_blog_series()` - Multi-part series outlines

### SocialAgent
Generates platform-optimized social content:
- `generate_instagram_post()` - Captions with hashtags
- `generate_reddit_post()` - Authentic, value-first posts
- `generate_carousel_script()` - Multi-slide Instagram content
- `generate_content_calendar()` - Weekly/monthly calendars
- `batch_generate_posts()` - Multiple posts at once

### AmazonAgent
Optimizes Amazon product listings:
- `generate_product_title()` - SEO-optimized titles
- `generate_bullet_points()` - Benefit-focused bullets
- `generate_product_description()` - Compelling descriptions
- `generate_a_plus_content()` - A+ content sections
- `generate_backend_keywords()` - Search term optimization
- `optimize_existing_listing()` - Analyze and improve current listings

### CompetitorAgent
Analyzes competition:
- `analyze_competitor_listing()` - Deep listing analysis
- `analyze_competitor_reviews()` - Review mining for insights
- `compare_multiple_competitors()` - Side-by-side comparison
- `identify_content_gaps()` - Find content opportunities

## 📖 Usage Examples

### Blog Content

```bash
# Standard blog post
python generate_content.py blog post "Card Protection Tips for Serious Collectors" \
  --pillar "Gear & Equipment" \
  --keywords "card protection,tcg storage,card care" \
  --words 1200

# Listicle
python generate_content.py blog listicle "15 Must-Have Items in Your Tournament Bag" \
  --items 15 \
  --pillar "Battle-Ready Lifestyle"

# How-to guide
python generate_content.py blog howto "How to Build a Pre-Tournament Checklist" \
  --audience "Tournament players" \
  --difficulty intermediate
```

### Social Media

```bash
# Instagram post
python generate_content.py social instagram "The battle-ready mindset" \
  --pillar "Battle-Ready Lifestyle" \
  --image "Player confidently entering tournament with organized gear"

# Reddit post (value-focused, no selling)
python generate_content.py social reddit "Tournament prep advice for beginners" \
  --subreddit "PokemonTCG" \
  --type discussion

# Content calendar
python generate_content.py social calendar \
  --for-platform instagram \
  --days 14 \
  --pillar "Community Champion"

# Batch generate 10 posts
python generate_content.py social batch \
  --for-platform instagram \
  --count 10
```

### Amazon Listings

```bash
# Product title
python generate_content.py amazon title "Ultra-Premium Card Binder" \
  --features "scratch-resistant,reinforced binding,9-pocket" \
  --keywords "trading card binder,tcg storage,pokemon binder"

# Bullet points (use format: feature:benefit)
python generate_content.py amazon bullets "Ultra-Premium Card Binder" \
  --features "Scratch-resistant pages:Keep cards pristine,Lifetime warranty:Investment protection" \
  --audience "Competitive players and serious collectors"

# Full description
python generate_content.py amazon description "Ultra-Premium Card Binder" \
  --details "Professional 9-pocket binder with scratch-resistant pages and reinforced binding" \
  --usp "Battle-Ready Equipment for Tournament Players"
```

### Competitor Analysis

Use Python for competitor analysis (requires data input):

```python
from agents import CompetitorAgent

agent = CompetitorAgent()

# Analyze competitor listing
content, path = agent.analyze_competitor_listing(
    competitor_name="Budget Storage Co",
    product_title="Card Binder 9 Pocket - Black - 360 Cards",
    bullet_points=[
        "Holds 360 cards",
        "9 pocket pages",
        "Black color",
        "Multiple sizes available"
    ],
    description="Basic card storage binder with 9-pocket pages.",
    price=15.99,
    rating=4.2,
    review_count=850
)

# Analyze competitor reviews
content, path = agent.analyze_competitor_reviews(
    competitor_name="Budget Storage Co",
    positive_reviews=[
        "Great value for the price",
        "Holds all my cards perfectly",
        "Pages are sturdy enough"
    ],
    negative_reviews=[
        "Pages scratch easily",
        "Binding broke after 6 months",
        "Cheap feeling materials"
    ]
)
```

## 🎨 Brand Voice & Positioning

All content automatically incorporates:

**Brand Identity:**
- Name: Infinity Vault
- Tagline: "Show Up Battle Ready"
- Promise: Show up to every game feeling confident, prepared, and respected

**Positioning:**
- Battle-Ready Equipment (NOT commodity storage)
- Professional-grade quality
- Tournament-tested gear
- For serious players, not casual hobbyists

**Voice Attributes:**
- Confident but not arrogant
- Passionate about gaming culture
- Empowering and aspirational
- Direct and punchy

**Content Pillars:**
1. Battle-Ready Lifestyle - Pre-game rituals, tournament culture
2. Gear & Equipment - Product education as battle gear
3. Community Champion - Player spotlights, LGS features
4. Collector's Journey - Collection care, card stories

## 📁 Output Structure

All generated content is saved to:

```
ai-content-agents/output/
├── blog/                    # Blog posts and articles
├── social/
│   ├── instagram/          # Instagram captions
│   └── reddit/             # Reddit posts
├── amazon/                 # Amazon listing content
└── competitor-analysis/    # Competitive research
```

Each file includes:
- Generated content (markdown format)
- Metadata JSON (topic, keywords, timestamp)
- Clear naming with timestamps

## 🔧 Advanced Usage

### Customize Generation Parameters

```python
from agents import BlogAgent

agent = BlogAgent()

# Custom temperature for more/less creativity
content = agent.generate_content(
    prompt="Your prompt here",
    temperature=0.7,  # Lower = more focused, Higher = more creative
    max_tokens=4096   # Longer content
)
```

### Batch Processing

```python
from agents import SocialAgent

agent = SocialAgent()

topics = [
    "Tournament preparation tips",
    "Card organization strategies",
    "Pre-game rituals that work"
]

for topic in topics:
    content, path = agent.generate_instagram_post(
        topic=topic,
        content_pillar="Battle-Ready Lifestyle"
    )
    print(f"Generated: {path}")
```

### Content Calendar Workflow

```python
from agents import SocialAgent
from datetime import datetime, timedelta

agent = SocialAgent()

# Generate 30-day calendar
content, path = agent.generate_content_calendar(
    platform="instagram",
    num_days=30,
    content_pillar="Mix of all pillars"
)

# Then generate each post from the calendar
# (Parse calendar and generate individually)
```

## 🎓 Best Practices

### For Blog Posts
- Use specific, searchable topics
- Target 1000-2000 words for SEO
- Include target keywords naturally
- Mix educational and inspirational content
- End with clear CTAs to products

### For Social Media
- Instagram: Visual-first, use emojis sparingly
- Reddit: Value-first, never sound salesy
- Vary content types (educational, inspirational, community)
- Post during peak gaming hours (evenings, weekends)

### For Amazon Listings
- Front-load keywords in titles
- Start bullets with benefits, not features
- Use emotional language (confident, prepared, respected)
- Emphasize battle-ready positioning
- Include trust signals (warranty, quality, tournament-tested)

### For Competitor Analysis
- Analyze top 3-5 competitors in each category
- Focus on messaging gaps, not just features
- Look for review patterns (pain points)
- Identify positioning white space
- Test and iterate based on insights

## 🧪 Testing

The system maintains **70% minimum test coverage** to ensure reliability and prevent regressions.

### Running Tests

```bash
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
tests/
├── conftest.py                 # Shared fixtures (mock API clients, brand context)
├── fixtures/
│   └── mock_responses.py       # Mock Anthropic API responses
├── test_base_agent.py          # BaseAgent initialization and methods
├── test_blog_agent.py          # BlogAgent content generation
├── test_social_agent.py        # SocialAgent platform-specific tests
├── test_amazon_agent.py        # AmazonAgent listing optimization
├── test_competitor_agent.py    # CompetitorAgent analysis tests
└── test_api.py                 # API integration tests (future)
```

### Writing Tests

All tests mock the Anthropic API to avoid real API calls:

```python
import pytest
from unittest.mock import Mock, patch
from agents.blog_agent import BlogAgent

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client"""
    mock = Mock()
    mock.messages.create.return_value = Mock(
        content=[Mock(text="Generated blog content")]
    )
    return mock

def test_generate_blog_post(mock_anthropic_client):
    with patch('agents.base_agent.anthropic.Anthropic', return_value=mock_anthropic_client):
        agent = BlogAgent()
        content, path = agent.generate_blog_post(
            topic="Test Topic",
            content_pillar="Battle-Ready Lifestyle"
        )
        assert "Generated blog content" in content
        assert path.exists()
```

### Testing Philosophy

- **Test First**: Write tests before implementing new features
- **Isolated Tests**: Mock all external dependencies (API calls, file I/O)
- **Fast Feedback**: All tests should run in under 10 seconds
- **Real Scenarios**: Test actual usage patterns, not implementation details

**Read more:** [`../docs/TESTING_GUIDE.md`](../docs/TESTING_GUIDE.md)

## 🔌 API Usage

### Current: CLI and Python API

**Command Line Interface:**
```bash
# Universal generation
python generate_content.py blog post "Topic" --pillar "Battle-Ready Lifestyle"
python generate_content.py social instagram "Topic" --image "Description"
python generate_content.py amazon title "Product" --features "feature1,feature2"
```

**Python API:**
```python
from agents import BlogAgent, SocialAgent, AmazonAgent, CompetitorAgent

# Blog content
blog_agent = BlogAgent()
content, path = blog_agent.generate_blog_post(
    topic="Your Topic",
    content_pillar="Battle-Ready Lifestyle",
    word_count=1500
)

# Social content
social_agent = SocialAgent()
content, path = social_agent.generate_instagram_post(
    topic="Your Topic",
    content_pillar="Battle-Ready Lifestyle",
    image_description="Description of visual"
)

# Amazon optimization
amazon_agent = AmazonAgent()
content, path = amazon_agent.generate_product_title(
    product_name="Product Name",
    key_features=["feature1", "feature2"],
    target_keywords=["keyword1", "keyword2"]
)

# Competitor analysis
competitor_agent = CompetitorAgent()
content, path = competitor_agent.analyze_competitor_listing(
    competitor_name="Competitor Name",
    product_title="Their Product Title",
    bullet_points=["bullet1", "bullet2"],
    description="Their description",
    price=29.99,
    rating=4.5,
    review_count=1000
)
```

### Future: REST API (Planned)

A FastAPI-based REST API is planned for Phase 2:

**Endpoints:**
- `POST /api/content/generate` - Universal content generation
- `POST /api/blog/generate` - Blog-specific generation
- `POST /api/social/generate` - Social media generation
- `POST /api/amazon/generate` - Amazon listing optimization

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "blog",
    "prompt": "Write a blog post about tournament preparation",
    "parameters": {
      "pillar": "Battle-Ready Lifestyle",
      "word_count": 1500
    }
  }'
```

**Read more:** [`../docs/API_DESIGN.md`](../docs/API_DESIGN.md)

## 🔒 Security

- Never commit your `.env` file or API keys
- Store API keys in environment variables
- Use `.gitignore` to exclude sensitive files
- Rotate API keys periodically

## 🛠️ Troubleshooting

**"ANTHROPIC_API_KEY not found"**
```bash
export ANTHROPIC_API_KEY='your-key-here'
# Or create .env file
```

**Import errors**
```bash
# Make sure you're in the right directory
cd ai-content-agents
pip install -r requirements.txt
```

**"Module not found: agents"**
```bash
# Run from ai-content-agents directory
cd ai-content-agents
python generate_content.py blog post "Your Topic"
```

**Content doesn't match brand voice**
- Check that brand docs are in correct locations
- Review `config/config.py` for correct paths
- Regenerate with more specific prompts

## 📈 Roadmap

Future enhancements:
- [ ] Email newsletter generator
- [ ] Video script writer (YouTube, TikTok)
- [ ] Product naming assistant
- [ ] A/B test variation generator
- [ ] SEO keyword research automation
- [ ] Content performance tracking
- [ ] Multi-language support
- [ ] Image generation integration
- [ ] Automated publishing workflows

## 💡 Tips for Maximum Impact

1. **Start with high-leverage content**: Amazon listings first (direct revenue impact)
2. **Batch by pillar**: Generate all "Battle-Ready Lifestyle" content in one session
3. **Iterate based on performance**: Track what converts, generate more of that
4. **Use competitor analysis**: Let data guide content strategy
5. **Maintain consistency**: Use the same agent for similar content types
6. **Review and edit**: AI generates drafts - you add the final polish
7. **Test variations**: Generate multiple options, A/B test the best

## 🤝 Contributing

This system is built for Infinity Vault but can be adapted for other brands:
1. Update brand docs in `claude-code-os-implementation/`
2. Modify `config/config.py` with your brand identity
3. Adjust agents for your specific use cases

## 📞 Support

Questions or issues?
- Check the troubleshooting section above
- Review the examples in `quick_start.py`
- Consult Anthropic docs: https://docs.anthropic.com/

---

**Built with Claude Sonnet 4.5** | **Powered by Anthropic AI**

*Show Up Battle Ready* ⚔️
