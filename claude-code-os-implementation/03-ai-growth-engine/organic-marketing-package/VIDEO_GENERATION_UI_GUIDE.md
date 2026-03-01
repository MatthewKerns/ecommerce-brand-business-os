# Video Generation UI Guide

## 🎬 Overview

The Video Generation UI is now integrated into the TikTok Content Studio. It uses our new plugin-based video generation architecture to transform generated scripts into TikTok videos.

## 📍 Where to Find It

1. Navigate to **TikTok Content Studio** in the dashboard
2. Select a channel (Air, Water, Earth, or Fire)
3. Generate a script using the Script Generator
4. **The Video Generator section will appear below the script once a script is generated**

## 🔧 How It Works

### Frontend Flow
1. **Script Generation** → User generates a script for their selected channel
2. **Video Generator Appears** → Once script exists, the Video Generator UI becomes visible
3. **Configure Options** → Select quality, provider, and advanced settings
4. **Generate Video** → Click "Generate Video" to start the process
5. **View Result** → See preview, download, or publish to TikTok

### Backend Architecture
```
Frontend (React/Next.js)
    ↓
API Route (/api/tiktok/generate-video)
    ↓
Python Backend (Port 8000)
    ↓
Video Generation Service (Plugin Architecture)
    ↓
Provider (Mock, Remotion, RunwayML, etc.)
```

## 🚀 Quick Start

### 1. Start the Python Backend

```bash
cd content-agents
python3 api_video_endpoint.py
```

This starts the video generation API on `http://localhost:8000`

### 2. Start the Dashboard

```bash
cd dashboard
npm run dev
```

Dashboard runs on `http://localhost:3000`

### 3. Test Video Generation

1. Go to http://localhost:3000/tiktok
2. Select a channel (e.g., Air)
3. Fill in the script generator form:
   - Product: "Test Product"
   - Topic: "Product Benefits"
   - Target Audience: "Young Adults"
4. Click "Generate Script"
5. **Video Generator section appears** ✨
6. Select options:
   - Quality: Standard (720p)
   - Provider: Mock Provider (for testing)
7. Click "Generate Video"
8. See the generated video result!

## 🎯 Features

### Video Quality Options
- **Low (480p)** - Fast generation, smaller file size
- **Standard (720p)** - Balanced quality/speed
- **High (1080p)** - High quality output
- **Ultra (4K)** - Maximum quality

### Provider Options
- **Mock Provider** 🧪 - Testing (returns JSON structure)
- **Remotion** ⚛️ - React-based programmatic video (Phase 2)
- **RunwayML** 🤖 - AI-powered generation (Phase 2)
- **Synthesia** 👤 - AI avatars (Phase 2)
- **FFmpeg** 🎬 - Local processing (Phase 2)

### Advanced Options
- Auto-generate captions
- Add channel watermark
- Include background music
- Enable AI voiceover
- Visual effects (transitions, filters, animations)

## 🔌 API Endpoints

### Generate Video
```
POST /api/tiktok/generate-video
{
  "script": { ... },
  "channel": "air",
  "quality": "standard",
  "provider": "mock"
}
```

### Check Status
```
GET /api/tiktok/generate-video?id=video-123
```

## 🐛 Troubleshooting

### Video Generator Not Showing?

1. **Check if script is generated** - The Video Generator only appears after a script exists
2. **Check console for errors** - Open browser DevTools (F12)
3. **Verify backend is running** - Check http://localhost:8000/health
4. **Check network tab** - Ensure API calls are reaching the backend

### Common Issues

**Issue**: "Video Generator unavailable"
- **Solution**: Component failed to load. Check if VideoGenerator.tsx exists in `/components/tiktok/`

**Issue**: "Failed to generate video"
- **Solution**: Backend not running or CORS issue. Start the Python backend.

**Issue**: Video stuck on "Generating..."
- **Solution**: Check backend logs for errors. Mock provider should complete in 2-3 seconds.

## 🏗️ Architecture Details

### Component Structure
```
/dashboard/src/
├── app/
│   ├── (dashboard)/
│   │   └── tiktok/
│   │       └── page.tsx          # Main TikTok Studio page
│   └── api/
│       └── tiktok/
│           └── generate-video/
│               └── route.ts      # API endpoint
└── components/
    └── tiktok/
        ├── ChannelSelector.tsx
        ├── ScriptGeneratorForm.tsx
        ├── GeneratedScriptDisplay.tsx
        └── VideoGenerator.tsx    # New video generation UI
```

### Backend Structure
```
/content-agents/
├── domain/                      # Domain interfaces
│   └── video_generation/
├── application/                  # Service layer
│   └── video_generation_service.py
├── infrastructure/               # Implementations
│   ├── video_providers/
│   │   ├── base_provider.py
│   │   └── mock_provider.py
│   └── di/
│       └── setup.py
└── api_video_endpoint.py        # Flask API server
```

## 📊 Current Status

### ✅ Phase 1 Complete
- Plugin architecture implemented
- Mock provider working
- UI integrated with TikTok Studio
- API endpoints connected

### 🚧 Phase 2 (Next Steps)
- Implement real video providers
- Add video preview player
- Enable direct TikTok publishing
- Add video analytics

## 🎉 Success Verification

You'll know it's working when:
1. Video Generator section appears after script generation ✓
2. Mock provider returns video metadata ✓
3. Progress bar shows during generation ✓
4. Success message appears with video details ✓
5. Download/Preview buttons become available ✓

## 📝 Notes

- The Mock Provider generates JSON structure, not actual videos (Phase 1)
- Real video generation will be available in Phase 2 with provider implementations
- The UI is fully functional and ready for real providers to be plugged in
- All channel-specific styles and effects are configured in the architecture