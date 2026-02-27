"""
Video Generation Example

Example of how to use the new video generation architecture.
"""

import asyncio
import json
from pathlib import Path

from infrastructure.di import create_video_generation_service
from domain.video_generation import VideoQuality, VideoStatus


async def main():
    """Run video generation example."""
    print("Video Generation Architecture Example")
    print("=" * 50)

    # Create video generation service
    # This automatically sets up all dependencies
    service = create_video_generation_service()

    # Example script (what would come from TikTok content agent)
    raw_script = {
        "channel": "air",
        "topic": "Finding Mental Clarity Through Breathing",
        "hook": "Did you know 3 minutes of breathing can transform your focus?",
        "main_points": [
            "Deep breathing activates your parasympathetic nervous system",
            "It reduces cortisol and increases mental clarity",
            "Try the 4-7-8 technique for instant calm"
        ],
        "call_to_action": "Follow for daily mindfulness tips!",
        "duration": 30,
        "visual_style": "minimalist",
        "music_style": "ambient",
        "hashtags": ["#mindfulness", "#mentalclarity", "#breathwork"],
        "target_audience": "young professionals"
    }

    # Generate video
    print("\n1. Generating video...")
    print(f"   Channel: {raw_script['channel']}")
    print(f"   Topic: {raw_script['topic']}")

    result = await service.generate_video(
        raw_script=raw_script,
        channel="air",
        quality=VideoQuality.STANDARD,
        options={"fast_generation": True}
    )

    print(f"\n2. Generation started:")
    print(f"   Video ID: {result.id}")
    print(f"   Status: {result.status.value}")
    print(f"   Provider: {result.provider_id}")

    # Check status (mock provider completes quickly)
    await asyncio.sleep(2)

    status = await service.get_video_status(result.id)
    print(f"\n3. Generation status:")
    print(f"   Status: {status.status.value}")

    if status.status == VideoStatus.COMPLETED:
        print(f"   URL: {status.url}")
        print(f"   Duration: {status.duration_seconds}s")
        print(f"   Metadata: {json.dumps(status.metadata, indent=2)}")

    # Show available providers
    providers = service.get_available_providers()
    print(f"\n4. Available providers:")
    for provider in providers:
        print(f"   - {provider['name']} ({provider['id']})")
        print(f"     Capabilities: {', '.join(provider['capabilities'])}")
        print(f"     Qualities: {', '.join(provider['supported_qualities'])}")

    # Example: Multiple channels
    print(f"\n5. Generating for multiple channels...")

    channels = ["water", "earth", "fire"]
    scripts = []

    for channel in channels:
        script = raw_script.copy()
        script["channel"] = channel
        scripts.append((script, channel, VideoQuality.STANDARD))

    results = await service.batch_generate_videos(scripts, max_concurrent=2)

    for i, result in enumerate(results):
        print(f"   {channels[i]}: {result.status.value} (ID: {result.id})")

    print(f"\n✅ Example complete!")


async def test_provider_selection():
    """Test provider selection based on requirements."""
    from infrastructure.di import setup_di_container
    from infrastructure.video_providers import MockVideoProvider
    from domain.video_generation import ProviderCapability, VideoQuality

    print("\nProvider Selection Test")
    print("=" * 50)

    # Set up container
    container = setup_di_container()
    registry = container.resolve("provider_registry")

    # Create and register additional mock providers with different capabilities
    class AIVideoProvider(MockVideoProvider):
        def __init__(self):
            super().__init__()
            self._info.id = "ai_provider"
            self._info.name = "AI Video Provider"
            self._info.capabilities = [
                ProviderCapability.AI_GENERATION,
                ProviderCapability.AVATAR_GENERATION,
                ProviderCapability.TEXT_TO_VIDEO,
            ]

    class AnimationProvider(MockVideoProvider):
        def __init__(self):
            super().__init__()
            self._info.id = "animation_provider"
            self._info.name = "Animation Provider"
            self._info.capabilities = [
                ProviderCapability.ANIMATION,
                ProviderCapability.TRANSITIONS,
                ProviderCapability.TEXT_TO_VIDEO,
            ]

    # Register providers
    ai_provider = AIVideoProvider()
    animation_provider = AnimationProvider()

    registry.register_provider(ai_provider)
    registry.register_provider(animation_provider)

    # Test selection
    test_cases = [
        {
            "name": "Basic text-to-video",
            "quality": VideoQuality.STANDARD,
            "features": [ProviderCapability.TEXT_TO_VIDEO],
        },
        {
            "name": "AI generation required",
            "quality": VideoQuality.HIGH,
            "features": [ProviderCapability.AI_GENERATION],
        },
        {
            "name": "Animation required",
            "quality": VideoQuality.STANDARD,
            "features": [ProviderCapability.ANIMATION, ProviderCapability.TRANSITIONS],
        },
    ]

    for test in test_cases:
        provider = registry.select_provider(
            quality=test["quality"],
            required_features=test["features"]
        )

        print(f"\nTest: {test['name']}")
        print(f"  Requirements: {[f.value for f in test['features']]}")

        if provider:
            print(f"  Selected: {provider.info.name} ({provider.info.id})")
        else:
            print(f"  No provider found!")

    print("\n✅ Provider selection test complete!")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())

    # Run provider selection test
    asyncio.run(test_provider_selection())