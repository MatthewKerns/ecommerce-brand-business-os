# Video Generation Architecture

## Overview

The video generation system follows a **Plugin Architecture** pattern based on clean architecture principles. This design enables:

- **Modularity**: Swap video providers without changing business logic
- **Testability**: Mock providers for testing without infrastructure
- **Extensibility**: Add new providers and channels easily
- **Type Safety**: Full Python type hints throughout
- **Scalability**: Support for multiple providers and concurrent generation

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                 │
│              (API Routes, CLI, Dashboard)           │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│                  Application Layer                  │
│        (VideoGenerationService, ProviderRegistry)   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│                    Domain Layer                     │
│      (Interfaces, Entities, Business Rules)         │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│                Infrastructure Layer                 │
│    (Video Providers, Parsers, Strategies, Config)   │
└─────────────────────────────────────────────────────┘
```

### Domain Layer

**Location**: `/domain/video_generation/`

The domain layer defines the core business logic and interfaces:

- **Interfaces** (`interfaces.py`):
  - `IVideoProvider`: Contract for video generation providers
  - `IScriptParser`: Contract for script parsing
  - `IChannelStrategy`: Contract for channel-specific behavior
  - `IProviderRegistry`: Contract for provider management
  - `IConfigManager`: Contract for configuration

- **Entities** (`entities.py`):
  - `VideoScript`: Parsed video script structure
  - `VideoGenerationRequest`: Request for video generation
  - `VideoResult`: Result from generation
  - `VideoTimeline`: Timeline structure
  - `VideoScene`: Individual scene

### Application Layer

**Location**: `/application/`

The application layer orchestrates the video generation process:

- **VideoGenerationService** (`video_generation_service.py`):
  - Main orchestration service
  - Coordinates script parsing, provider selection, and generation
  - Handles batch generation and status tracking

- **ProviderRegistry** (`provider_registry.py`):
  - Manages provider registration
  - Intelligent provider selection based on requirements
  - Performance tracking and scoring

### Infrastructure Layer

**Location**: `/infrastructure/`

The infrastructure layer contains concrete implementations:

#### Video Providers (`/infrastructure/video_providers/`)

- **BaseVideoProvider**: Abstract base class for all providers
- **MockVideoProvider**: Testing provider that generates JSON
- Future providers: RemotionProvider, RunwayMLProvider, etc.

#### Channel Strategies (`/infrastructure/strategies/`)

- **AirChannelStrategy**: Mental clarity and flow states
- **WaterChannelStrategy**: Emotional intelligence and wellness
- **EarthChannelStrategy**: Practical grounding
- **FireChannelStrategy**: Motivation and transformation

#### Script Parsers (`/infrastructure/parsers/`)

- **TikTokScriptParser**: Parses raw TikTok scripts

#### Configuration (`/infrastructure/config/`)

- **VideoConfigManager**: Manages all configuration

#### Dependency Injection (`/infrastructure/di/`)

- **DIContainer**: Service container
- **Setup**: Wires all dependencies together

## Usage Examples

### Basic Usage

```python
from infrastructure.di import create_video_generation_service
from domain.video_generation import VideoQuality

# Create service (auto-configures all dependencies)
service = create_video_generation_service()

# Generate video
result = await service.generate_video(
    raw_script={
        "channel": "air",
        "topic": "Mindfulness",
        "hook": "Transform your focus",
        "main_points": ["Point 1", "Point 2"],
        "call_to_action": "Follow for more!"
    },
    channel="air",
    quality=VideoQuality.STANDARD
)

# Check status
status = await service.get_video_status(result.id)
```

### Custom Provider Implementation

```python
from infrastructure.video_providers import BaseVideoProvider
from domain.video_generation import ProviderCapability, VideoQuality

class RemotionProvider(BaseVideoProvider):
    def __init__(self):
        super().__init__(
            provider_id="remotion",
            name="Remotion Video Provider",
            capabilities=[
                ProviderCapability.ANIMATION,
                ProviderCapability.TRANSITIONS,
            ],
            supported_qualities=[VideoQuality.HIGH, VideoQuality.ULTRA]
        )

    async def _generate_video_impl(self, request, result):
        # Implement Remotion video generation
        pass
```

### Custom Channel Strategy

```python
from infrastructure.strategies import BaseChannelStrategy, ChannelStyle

class CustomChannelStrategy(BaseChannelStrategy):
    def __init__(self):
        style = ChannelStyle(
            primary_color="#FF0000",
            secondary_color="#FFFFFF",
            animation_style="custom",
            # ... more style config
        )
        super().__init__("custom", style)

    def validate_content(self, script):
        # Custom validation logic
        return True, None
```

## Provider Implementation Guide

### Step 1: Create Provider Class

```python
from infrastructure.video_providers import BaseVideoProvider

class MyProvider(BaseVideoProvider):
    def __init__(self, config):
        super().__init__(
            provider_id="my_provider",
            name="My Video Provider",
            capabilities=[...],
            supported_qualities=[...],
            config=config
        )
```

### Step 2: Implement Required Methods

```python
async def _generate_video_impl(self, request, result):
    """Actual video generation logic"""
    # 1. Connect to provider API
    # 2. Submit generation request
    # 3. Update result with video URL
    pass

async def _get_status_impl(self, video_id):
    """Get status from provider"""
    # Query provider API for status
    pass

def _validate_request_impl(self, request):
    """Provider-specific validation"""
    # Validate provider-specific requirements
    return True, None

async def _cancel_generation_impl(self, video_id):
    """Cancel generation"""
    # Call provider API to cancel
    return True
```

### Step 3: Register Provider

```python
from infrastructure.di import setup_di_container

container = setup_di_container()
container.register("my_provider", MyProvider(config))

registry = container.resolve("provider_registry")
registry.register_provider(container.resolve("my_provider"))
```

## Configuration

### Configuration Structure

```json
{
  "providers": {
    "mock_provider": {
      "enabled": true,
      "max_concurrent": 10,
      "timeout_seconds": 60
    },
    "remotion": {
      "enabled": false,
      "api_key": "...",
      "api_url": "...",
      "max_concurrent": 3
    }
  },
  "channels": {
    "air": {
      "enabled": true,
      "max_duration_seconds": 60,
      "default_quality": "standard"
    }
  },
  "global": {
    "default_provider": "mock_provider",
    "default_quality": "standard",
    "max_concurrent_generations": 5
  }
}
```

### Environment Variables

```bash
# Provider API Keys
VIDEO_PROVIDER_REMOTION_API_KEY=xxx
VIDEO_PROVIDER_RUNWAY_API_KEY=xxx

# Global Settings
VIDEO_DEFAULT_PROVIDER=remotion
VIDEO_STORAGE_PATH=/path/to/videos
VIDEO_MAX_CONCURRENT=10
```

## Testing

### Unit Testing

```python
import pytest
from infrastructure.video_providers import MockVideoProvider

@pytest.mark.asyncio
async def test_mock_provider():
    provider = MockVideoProvider()

    request = VideoGenerationRequest(...)
    result = await provider.generate_video(request)

    assert result.status == VideoStatus.COMPLETED
    assert result.url is not None
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_full_pipeline():
    service = create_video_generation_service()

    result = await service.generate_video(
        raw_script={...},
        channel="air",
        quality=VideoQuality.STANDARD
    )

    assert result.id is not None
    assert result.provider_id == "mock_provider"
```

## Migration from Old System

### Phase 1: Parallel Operation
- Keep existing implementation running
- Deploy new architecture alongside
- Use feature flag to switch between implementations

### Phase 2: Gradual Migration
```python
# In API route
if use_new_architecture():
    # New implementation
    service = create_video_generation_service()
    result = await service.generate_video(...)
else:
    # Old implementation
    result = old_generate_video(...)
```

### Phase 3: Full Migration
- Remove old implementation
- Update all references
- Clean up legacy code

## Provider Capability Matrix

| Provider | Text-to-Video | Animation | AI Generation | Avatar | Real-time |
|----------|--------------|-----------|---------------|--------|-----------|
| Mock | ✅ | ✅ | ❌ | ❌ | ❌ |
| Remotion | ✅ | ✅ | ❌ | ❌ | ✅ |
| RunwayML | ✅ | ✅ | ✅ | ❌ | ❌ |
| Synthesia | ✅ | ❌ | ✅ | ✅ | ❌ |
| FFmpeg | ✅ | ❌ | ❌ | ❌ | ✅ |

## Performance Considerations

### Provider Selection
- Selection algorithm runs in O(n) where n = number of providers
- Providers are scored based on capabilities, quality, performance, and cost
- Scoring weights are configurable

### Concurrent Generation
- Configurable max concurrent generations per provider
- Global concurrency limit across all providers
- Automatic queuing when limits reached

### Caching
- Provider capabilities cached on registration
- Configuration cached and reloaded on demand
- Generation results cached for status queries

## Error Handling

### Provider Errors
```python
try:
    result = await provider.generate_video(request)
except ProviderError as e:
    # Handle provider-specific error
    logger.error(f"Provider error: {e}")
    # Try fallback provider
```

### Validation Errors
```python
is_valid, error = provider.validate_request(request)
if not is_valid:
    return VideoResult(
        status=VideoStatus.FAILED,
        error_message=error
    )
```

### Timeout Handling
```python
async with timeout(provider.config.timeout_seconds):
    result = await provider.generate_video(request)
```

## Monitoring and Metrics

### Provider Metrics
- Successful generations
- Failed generations
- Average generation time
- Last error/success

### Service Metrics
- Total generations
- Provider distribution
- Channel distribution
- Quality distribution

## Future Enhancements

### Phase 2 Providers
- **RemotionProvider**: React-based video generation
- **RunwayMLProvider**: AI-powered generation
- **SynthesiaProvider**: AI avatar generation
- **FFmpegProvider**: Local processing

### Advanced Features
- Video templates system
- A/B testing framework
- Analytics integration
- Webhook notifications
- CDN integration

## Support and Troubleshooting

### Common Issues

1. **Provider not found**: Check provider registration
2. **No suitable provider**: Check capability requirements
3. **Generation timeout**: Increase timeout in config
4. **Invalid script**: Check script validation rules

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailed logging for troubleshooting
service = create_video_generation_service()
```

### Health Check

```python
# Check provider availability
providers = service.get_available_providers()
for provider in providers:
    print(f"{provider['name']}: {provider['is_available']}")
```