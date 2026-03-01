# AEO Analytics Architecture: How LLM Model Analytics Are Generated

## Executive Summary

The AEO Optimizer generates analytics for different LLM models (ChatGPT, Claude, Perplexity, Google AI) through a multi-layered architecture that actively queries AI platforms, tracks brand citations, analyzes competitive positioning, and provides actionable insights. The system uses **real API integrations** to monitor how AI assistants respond to relevant queries about your brand and competitors.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Dashboard                           │
│        (Citation Tracking, Analytics, Recommendations)       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    API Layer                                 │
│        (/api/aeo/citations/*, /api/aeo/metrics/*)           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Analytics Agents                             │
│    ┌──────────────────┐    ┌────────────────────┐          │
│    │ Citation Tracker │    │   AEO Analyzer     │          │
│    └──────────────────┘    └────────────────────┘          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            Citation Monitoring Agent                         │
│         (Orchestrates AI Platform Queries)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              AI Platform Clients                             │
│  ┌────────┐  ┌────────┐  ┌────────────┐  ┌────────┐       │
│  │ChatGPT │  │ Claude │  │ Perplexity │  │Google AI│       │
│  │Client  │  │ Client │  │   Client   │  │ Client* │       │
│  └────┬───┘  └───┬────┘  └──────┬─────┘  └────┬───┘       │
└───────┼──────────┼──────────────┼──────────────┼───────────┘
        │          │              │              │
        ▼          ▼              ▼              ▼
    OpenAI API  Anthropic API  Perplexity API  Google AI API
```

*Note: Google AI integration is configured but requires implementation of the client class.

## How Analytics Are Generated

### 1. Query Execution Process

The system generates analytics through an active monitoring approach:

#### Step 1: Query Definition
Queries are defined in the configuration (`config.py`) and include:
- **Product discovery queries**: "best TCG card storage solutions"
- **Comparison queries**: "infinity vault vs ultra pro comparison"
- **Purchase intent queries**: "where to buy premium card storage"
- **Problem-solving queries**: "how to protect valuable trading cards"

#### Step 2: AI Platform Querying
The `CitationMonitoringAgent` orchestrates queries to multiple AI platforms:

```python
# Example flow from citation_monitoring_agent.py
def query_ai_assistant(query, platform):
    client = get_client(platform)  # Gets ChatGPT, Claude, or Perplexity client
    response = client.send_message(query)
    return analyze_response(response)
```

Each platform client makes **actual API calls** to the respective service:
- **ChatGPT**: Uses OpenAI API (gpt-4 model by default)
- **Claude**: Uses Anthropic API (claude-3 model)
- **Perplexity**: Uses Perplexity API for search-augmented responses
- **Google AI**: Configured for Gemini API (implementation pending)

#### Step 3: Response Analysis
Responses are analyzed for:
- **Brand mentions**: Direct references to your brand name
- **Citation URLs**: Links to your website or content
- **Competitor mentions**: References to competing brands
- **Citation context**: How and why the brand was mentioned
- **Response quality**: Relevance and accuracy of information

### 2. Data Collection & Storage

#### Database Schema
The `CitationTracking` table stores each monitoring result:
```sql
CitationTracking:
  - tracking_id (UUID)
  - platform (chatgpt|claude|perplexity|google_ai)
  - query (text)
  - brand_mentioned (boolean)
  - citation_url (text)
  - citation_context (text)
  - competitor_citations (JSON)
  - opportunity_score (0-100)
  - response_text (full AI response)
  - response_time_ms (performance metric)
  - query_category (discovery|comparison|purchase|etc)
  - batch_id (for grouping monitoring runs)
  - created_at (timestamp)
```

#### Tracking Methods
The `CitationTracker` agent provides two key methods:

1. **`record_tracking_result()`**: Records each AI platform query result
2. **`get_tracking_history()`**: Retrieves historical data with analytics

### 3. Analytics Generation

#### Real-time Metrics
The system calculates these metrics from actual API responses:

**Citation Rate**
```
Citation Rate = (Queries with Brand Mention / Total Queries) × 100
```

**Platform-Specific Performance**
```python
{
    "chatgpt": {
        "citation_rate": 45.2,
        "avg_position": 2.3,  # Position in response
        "total_queries": 523,
        "brand_mentions": 236
    },
    "claude": {
        "citation_rate": 38.7,
        "avg_position": 3.1,
        "total_queries": 498,
        "brand_mentions": 193
    },
    // ... other platforms
}
```

**Opportunity Scoring**
Each query is scored (0-100) based on:
- Query volume weight: 30%
- Current gap (competitors cited, brand not): 25%
- Competitor density: 20%
- Improvement ease: 15%
- Business impact: 10%

#### Comparative Analytics

**Competitor Benchmarking**
```python
# From citation_tracker.py
competitor_comparison = {
    "brand": {
        "citation_rate": 42.3,
        "platforms": ["chatgpt", "claude", "perplexity"],
        "strong_categories": ["product_discovery", "comparison"]
    },
    "competitor_1": {
        "citation_rate": 56.8,
        "platforms": ["chatgpt", "perplexity"],
        "strong_categories": ["purchase_intent"]
    }
}
```

**Gap Analysis**
Identifies queries where competitors are cited but your brand isn't:
```python
gaps = [
    {
        "query": "best TCG storage for collectors",
        "competitors_cited": ["Ultra Pro", "BCW"],
        "platforms_affected": ["chatgpt", "claude"],
        "opportunity_score": 87.5,
        "recommended_actions": [
            "Create detailed comparison content",
            "Optimize product descriptions",
            "Build Reddit presence on r/mtgfinance"
        ]
    }
]
```

### 4. Dashboard Visualization

The analytics are presented through the dashboard with:

#### Overview Metrics
- **AEO Score**: Overall optimization score (0-100)
- **Citation Rate**: Percentage across all platforms
- **Opportunities**: Number of high-value gaps identified

#### Platform Breakdown
Real-time citation rates for each AI platform with visual indicators:
- ChatGPT: 45.2% ↑
- Claude: 38.7% →
- Perplexity: 52.1% ↑
- Google AI: 23.4% ↓

#### Trend Analysis
- 7-day, 30-day, 90-day trending
- Period-over-period comparisons
- Alert triggers for significant changes (±10%)

## API Integration Details

### Authentication & Configuration

Each AI platform requires API credentials configured in environment variables:

```bash
# .env configuration
OPENAI_API_KEY=sk-...          # ChatGPT
ANTHROPIC_API_KEY=sk-ant-...   # Claude
PERPLEXITY_API_KEY=pplx-...    # Perplexity
GOOGLE_AI_API_KEY=AIza...      # Google AI/Gemini
```

### Rate Limiting & Reliability

The system implements sophisticated error handling:

1. **Rate Limiting**: Automatic backoff when API limits are reached
2. **Retry Logic**: Up to 3 retries with exponential backoff
3. **Timeout Handling**: 60-second default timeout per query
4. **Error Recovery**: Graceful degradation if a platform is unavailable

### Cost Optimization

To manage API costs, the system includes:
- **Batch Processing**: Groups queries for efficient API usage
- **Caching**: Stores responses to avoid duplicate queries
- **Sampling**: Can run on representative query samples
- **Configurable Intervals**: Adjust monitoring frequency based on budget

## Monitoring Workflow

### Automated Monitoring Runs

1. **Scheduled Execution**: Runs can be scheduled (hourly, daily, weekly)
2. **Query Selection**: Uses predefined query sets from configuration
3. **Platform Rotation**: Queries all available platforms
4. **Result Recording**: Stores all responses in CitationTracking table
5. **Alert Generation**: Triggers alerts for significant changes

### Manual Testing

The API provides endpoints for on-demand testing:
```bash
# Test a specific query across all platforms
POST /api/aeo/citations/analyze
{
    "query": "best card storage for pokemon collectors",
    "platforms": ["chatgpt", "claude", "perplexity"]
}
```

## Data Analysis Pipeline

### 1. Raw Data Collection
- Direct API responses from AI platforms
- Timestamp and metadata capture
- Full response text storage

### 2. Information Extraction
- Brand mention detection (regex + NLP)
- URL extraction and validation
- Competitor identification
- Context analysis

### 3. Scoring & Ranking
- Opportunity score calculation
- Query prioritization
- Competitive gap scoring

### 4. Recommendation Generation
- AI-powered analysis using Claude/GPT-4
- Actionable improvement suggestions
- Priority-based task lists

## Implementation Status

### ✅ Fully Implemented
- ChatGPT integration (`chatgpt_client.py`)
- Claude integration (`claude_client.py`)
- Perplexity integration (`perplexity_client.py`)
- Citation tracking database schema
- Analytics calculation engine
- Dashboard visualization components
- API endpoints for data access

### 🔄 Configuration Required
- API keys for each platform
- Target query lists
- Competitor brand names
- Monitoring intervals

### 📋 Pending Implementation
- Google AI/Gemini client class
- Automated scheduling system
- Advanced NLP for context analysis
- Machine learning for trend prediction

## Best Practices

### 1. Query Design
- Use natural, conversational queries
- Include buying intent variations
- Test both branded and unbranded searches
- Rotate query phrasings to avoid bias

### 2. Monitoring Frequency
- **High-value queries**: Daily monitoring
- **General queries**: Weekly monitoring
- **Exploratory queries**: Monthly monitoring

### 3. Response Analysis
- Store full responses for audit trail
- Extract multiple data points per response
- Track response evolution over time
- Identify citation patterns

### 4. Competitive Intelligence
- Monitor top 3-5 competitors
- Track relative citation rates
- Identify competitor strategies
- Find differentiation opportunities

## Security & Privacy

### API Key Management
- Store keys in environment variables only
- Never commit keys to version control
- Rotate keys regularly
- Use separate keys for dev/prod

### Data Privacy
- No PII in queries
- Anonymize user-specific queries
- Comply with AI platform ToS
- Implement data retention policies

## Performance Metrics

### System Performance
- **Query throughput**: 10-20 queries/minute (rate-limited)
- **Response time**: 2-5 seconds per query
- **Storage requirement**: ~1KB per tracking record
- **Dashboard load time**: <2 seconds

### Business Metrics
- **Citation rate improvement**: Track monthly progress
- **Gap closure rate**: Queries moving from uncited to cited
- **Competitive advantage**: Citation rate vs competitors
- **ROI tracking**: Traffic/conversions from AI citations

## Troubleshooting Guide

### Common Issues

1. **No Citations Detected**
   - Verify brand name spelling in config
   - Check if queries are relevant to your product
   - Ensure content exists for AI to reference

2. **API Rate Limits**
   - Reduce monitoring frequency
   - Implement query batching
   - Upgrade API tier if needed

3. **Inconsistent Results**
   - AI responses naturally vary
   - Run multiple samples for accuracy
   - Track trends, not individual responses

4. **Missing Platforms**
   - Verify API keys are configured
   - Check network connectivity
   - Review error logs for auth issues

## Future Enhancements

### Planned Features
1. **Voice Assistant Integration**: Alexa, Google Assistant monitoring
2. **Visual Search Monitoring**: Google Lens, Pinterest citations
3. **Social AI Monitoring**: Meta AI, X/Twitter AI responses
4. **Predictive Analytics**: ML models for citation forecasting
5. **Automated Content Generation**: Create citation-optimized content
6. **Real-time Alerts**: Instant notifications for citation changes

### Research Opportunities
1. **Citation Attribution**: Understanding why certain content gets cited
2. **Query Intent Analysis**: Deeper understanding of user needs
3. **Cross-Platform Patterns**: How citations differ across platforms
4. **Temporal Analysis**: Time-of-day/seasonal citation variations

## Conclusion

The AEO Analytics system provides comprehensive monitoring of AI platform citations through real API integrations, not simulations. By actively querying ChatGPT, Claude, Perplexity, and other AI assistants, the system generates actionable insights about brand visibility in AI-powered search results. This positions businesses to optimize their content for the 25% of search traffic moving to AI platforms by 2026.

The architecture is extensible, allowing for new AI platforms to be added as they emerge, and the analytics provide both real-time monitoring and historical trending to guide strategic decisions in the evolving landscape of AI-powered search.