# TikTok Content Studio - Dashboard Feature

## 🎬 Overview

The TikTok Content Studio is a comprehensive dashboard interface for creating, scheduling, and managing TikTok video content using the 4-channel element strategy (Air, Water, Earth, Fire). This feature connects to the Python backend agents to generate AI-powered video scripts optimized for viral engagement.

## 🚀 Features

### 1. **4-Channel Element Strategy**

Each channel targets different audience psychology:

- **💨 AIR Channel** - Quick tips, speed runs, tournament prep (15-30s)
  - Audience: Competitive players, tournament grinders
  - Focus: Fast-paced tips, quick wins, speed strategies

- **💧 WATER Channel** - Community stories, nostalgia, emotions (30-60s)
  - Audience: Collectors, community members
  - Focus: Personal stories, collection showcases, memories

- **🪨 EARTH Channel** - Product demos, organization tips, education (30-45s)
  - Audience: Parents, careful buyers, quality-focused
  - Focus: Product features, durability tests, tutorials

- **🔥 FIRE Channel** - Hot takes, debates, controversial opinions (15-30s)
  - Audience: Competitive players, debate lovers
  - Focus: Bold claims, controversial takes, challenges

### 2. **AI-Powered Script Generation**

- Topic-based script generation with channel-specific tone
- Product integration capabilities
- Automatic hashtag optimization
- Visual direction and text overlay suggestions
- Music and transition recommendations
- Optimized hooks (0-3 seconds) for maximum retention

### 3. **Content Calendar & Scheduling**

- Visual calendar with week/month/list views
- Drag-and-drop scheduling
- Multi-channel content coordination
- Status tracking (draft, scheduled, published, failed)
- Bulk content generation queue

### 4. **Script Management**

- Save generated scripts as drafts
- Edit and refine scripts before publishing
- Copy sections for manual posting
- Download scripts as JSON
- Track script performance metrics

## 📁 File Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   └── tiktok/
│   │   │       └── page.tsx          # Main TikTok Studio page
│   │   └── api/
│   │       └── tiktok/
│   │           ├── generate/
│   │           │   └── route.ts      # Script generation API
│   │           └── scripts/
│   │               └── route.ts      # Script CRUD operations
│   └── components/
│       └── tiktok/
│           ├── ChannelSelector.tsx   # 4-channel selection UI
│           ├── ScriptGeneratorForm.tsx # Script generation form
│           ├── GeneratedScriptDisplay.tsx # Script display/actions
│           └── ContentCalendar.tsx   # Scheduling calendar
```

## 🔧 Setup Instructions

### 1. Environment Variables

Add to `/dashboard/.env.local`:

```env
# Backend API Connection
TIKTOK_API_BASE=http://localhost:8000
BACKEND_API_BASE=http://localhost:8000
```

### 2. Start Backend Services

```bash
# Start Python backend (port 8000)
cd content-agents
python api/main.py
```

### 3. Start Dashboard

```bash
# Install dependencies
cd dashboard
npm install

# Start development server
npm run dev
```

### 4. Access TikTok Studio

Navigate to: `http://localhost:3000/tiktok`

## 💻 Usage Guide

### Generating a Script

1. **Select Channel**: Choose one of the 4 elemental channels
2. **Enter Topic**: Type your video topic or select from suggestions
3. **Product Integration** (Optional): Select a product to feature
4. **Add Hashtags** (Optional): Include additional hashtags
5. **Generate**: Click "Generate Video Script"
6. **Review**: Review the generated script with sections:
   - Hook (0-3s)
   - Main Content
   - Product Integration
   - Call-to-Action
   - Production Notes
   - Caption & Hashtags

### Script Actions

- **Save Script**: Store as draft for later
- **Schedule**: Add to content calendar
- **Download**: Export as JSON file
- **Copy Sections**: Copy individual parts for manual posting

### Content Calendar

- **Week View**: See 7-day schedule at a glance
- **List View**: Table format with all details
- **Drag & Drop**: Reschedule by dragging content cards
- **Status Tracking**: Monitor scheduled, published, failed posts

## 🔌 API Integration

### Generate Script Endpoint

```typescript
POST /api/tiktok/generate

Request Body:
{
  "channel_element": "air",
  "topic": "3-Second Deck Shuffle",
  "product": "Tournament Ready Deck Box",
  "include_product_link": true,
  "additional_hashtags": ["Pokemon", "TCG"]
}

Response:
{
  "channel": "air",
  "topic": "3-Second Deck Shuffle",
  "sections": [...],
  "productionNotes": {...},
  "caption": "...",
  "hashtags": [...],
  "estimatedLength": "15-30 seconds",
  "generatedAt": "2026-02-27T..."
}
```

### Save Script Endpoint

```typescript
POST /api/tiktok/scripts

Request Body:
{
  "channel": "air",
  "topic": "...",
  "script_content": {...},
  "status": "draft"
}
```

## 🎯 Script Structure

Each generated script includes:

```json
{
  "sections": [
    {
      "type": "HOOK",
      "timeRange": "0-3s",
      "visual": "Close-up of cards being shuffled",
      "audio": "You're shuffling WRONG...",
      "textOverlay": "SHUFFLE HACK 🎯"
    },
    {
      "type": "MAIN CONTENT",
      "timeRange": "3-12s",
      "visual": "Side-by-side comparison",
      "audio": "Watch this technique...",
      "textOverlay": "3 SECOND TECHNIQUE ⚡"
    }
  ],
  "productionNotes": {
    "musicStyle": "Fast-paced electronic/trap",
    "pace": "Quick cuts every 2-3 seconds",
    "transitions": "Zoom transitions"
  },
  "caption": "Stop wasting time between rounds 💨",
  "hashtags": ["#TCGSpeed", "#InfinityVault", "#QuickTips"]
}
```

## 🎨 UI Components

### ChannelSelector
- Visual cards for each channel
- Channel descriptions and target audience
- Color-coded by element theme
- Shows video length and content focus

### ScriptGeneratorForm
- Topic textarea with suggestions
- Product dropdown (optional)
- Product link checkbox
- Additional hashtags input
- Loading states and error handling

### GeneratedScriptDisplay
- Sectioned script display
- Copy buttons per section
- Save/Schedule/Download actions
- Production notes highlighting
- Caption and hashtag management

### ContentCalendar
- Week/Month/List view toggle
- Channel filtering
- Status indicators (scheduled/published/failed)
- Hover actions (edit/delete)
- Summary statistics

## 📊 Backend Connection

The dashboard connects to the Python backend agents:

```python
# Backend endpoint (Python FastAPI)
@router.post("/tiktok-channels/generate-script")
async def generate_script(request: ScriptRequest):
    agent = TikTokChannelAgent()
    script, path = agent.generate_channel_video_script(
        channel_element=request.channel_element,
        topic=request.topic,
        product=request.product
    )
    return {"script": script, "file_path": str(path)}
```

## 🚧 Future Enhancements

- [ ] Bulk script generation
- [ ] A/B testing interface
- [ ] Performance analytics integration
- [ ] Direct TikTok API publishing
- [ ] Video preview mockups
- [ ] Multi-channel campaign builder
- [ ] AI-powered topic suggestions
- [ ] Competitor content analysis

## 🐛 Troubleshooting

### Common Issues

1. **Scripts not generating**: Check Python backend is running on port 8000
2. **API connection errors**: Verify TIKTOK_API_BASE in .env.local
3. **Empty calendar**: Ensure database migrations are applied
4. **Styling issues**: Run `npm install @radix-ui/react-tabs`

### Debug Mode

Enable debug logging:
```javascript
// In /api/tiktok/generate/route.ts
console.log("Backend response:", data);
```

## 📚 Resources

- [TikTok Best Practices](https://www.tiktok.com/business/en/blog/tiktok-best-practices)
- [TikTok Shop Integration](../../content-agents/integrations/tiktok_shop/README.md)
- [API Documentation](../api/API_DESIGN.md)

## 🎉 Success Metrics

Track these KPIs in your TikTok Studio:

- **Script Generation Rate**: Scripts created per day
- **Channel Distribution**: Balance across 4 channels
- **Product Integration Rate**: % of videos with products
- **Publishing Success Rate**: Scheduled vs failed posts
- **Save-to-Purchase Ratio**: Key engagement metric

---

Built with ❤️ for Infinity Vault's TikTok domination strategy