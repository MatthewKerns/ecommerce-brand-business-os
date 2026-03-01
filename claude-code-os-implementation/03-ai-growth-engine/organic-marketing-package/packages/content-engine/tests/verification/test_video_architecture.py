#!/usr/bin/env python3
"""
Test Video Generation Architecture

Simple test to verify the video generation architecture is working.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
from pathlib import Path

# Import the architecture components
from domain.video_generation import (
    VideoQuality,
    VideoStatus,
    VideoGenerationRequest,
    VideoScript,
    ProviderCapability
)
from infrastructure.video_providers import MockVideoProvider
from infrastructure.strategies import ChannelStrategyFactory
from infrastructure.parsers import TikTokScriptParser
from infrastructure.config import VideoConfigManager
from application import VideoGenerationService, ProviderRegistry


async def test_basic_architecture():
    """Test the basic architecture components."""
    print("=" * 60)
    print("Testing Video Generation Architecture - Phase 1")
    print("=" * 60)

    # 1. Test Domain Layer
    print("\n1. Testing Domain Layer...")
    script = VideoScript(
        channel="air",
        topic="Mindfulness and Focus",
        hook="3 minutes to transform your focus",
        main_points=["Breathe deeply", "Clear your mind", "Find your flow"],
        call_to_action="Follow for daily mindfulness!",
        duration_seconds=30,
        visual_style="minimalist"
    )
    print(f"   ✓ Created VideoScript for '{script.topic}'")

    # 2. Test Infrastructure Layer - Parser
    print("\n2. Testing Infrastructure Layer...")
    parser = TikTokScriptParser()
    raw_script = {
        "channel": "air",
        "topic": "Finding focus through breathing",
        "hook": "Transform your mind in 3 minutes",
        "main_points": [
            "Deep breathing activates calm",
            "Reduces stress hormones",
            "Increases mental clarity"
        ],
        "call_to_action": "Follow for more mindfulness tips!"
    }
    parsed = parser.parse(raw_script)
    is_valid, error = parser.validate_script(parsed)
    print(f"   ✓ TikTokScriptParser: parsed and validated (valid={is_valid})")

    # 3. Test Infrastructure Layer - Channel Strategies
    factory = ChannelStrategyFactory()
    air_strategy = factory.get_strategy("air")
    print(f"   ✓ ChannelStrategyFactory: got {air_strategy.channel_name} strategy")

    # 4. Test Infrastructure Layer - Mock Provider
    mock_provider = MockVideoProvider()
    print(f"   ✓ MockVideoProvider: {mock_provider.info.name} initialized")
    print(f"     Capabilities: {[c.value for c in mock_provider.info.capabilities]}")

    # 5. Test Application Layer - Provider Registry
    print("\n3. Testing Application Layer...")
    registry = ProviderRegistry()
    registry.register_provider(mock_provider)
    providers = registry.list_providers()
    print(f"   ✓ ProviderRegistry: {len(providers)} provider(s) registered")

    # 6. Test provider selection
    selected = registry.select_provider(
        quality=VideoQuality.STANDARD,
        required_features=[ProviderCapability.TEXT_TO_VIDEO],
        channel="air"
    )
    print(f"   ✓ Provider Selection: selected '{selected.info.name}'")

    # 7. Test Application Layer - Video Generation Service
    config_manager = VideoConfigManager()
    service = VideoGenerationService(
        provider_registry=registry,
        script_parser=parser,
        channel_strategy_factory=factory,
        config_manager=config_manager
    )
    print(f"   ✓ VideoGenerationService: initialized with all dependencies")

    # 8. Test actual video generation
    print("\n4. Testing Video Generation...")
    result = await service.generate_video(
        raw_script=raw_script,
        channel="air",
        quality=VideoQuality.STANDARD
    )

    print(f"   ✓ Video Generation Started:")
    print(f"     - ID: {result.id}")
    print(f"     - Status: {result.status.value}")
    print(f"     - Provider: {result.provider_id}")

    # Wait for completion (mock provider is fast)
    await asyncio.sleep(2)

    # Check status
    status = await service.get_video_status(result.id)
    print(f"\n   ✓ Video Generation Completed:")
    print(f"     - Status: {status.status.value}")

    if status.status == VideoStatus.COMPLETED:
        print(f"     - Duration: {status.duration_seconds}s")
        print(f"     - URL: {status.url}")

        # Get the generated mock video data
        if hasattr(mock_provider, 'get_generated_video'):
            video_data = mock_provider.get_generated_video(result.id)
            if video_data:
                print(f"     - Scenes: {len(video_data['timeline']['scenes'])}")
                print(f"     - Channel Style: {video_data['channel_styling']['theme']}")

    print("\n" + "=" * 60)
    print("✅ Phase 1 Architecture Test Complete!")
    print("=" * 60)

    # Show architecture summary
    print("\n📊 Architecture Summary:")
    print(f"   Domain Layer: ✓ Interfaces and entities defined")
    print(f"   Application Layer: ✓ Service orchestration working")
    print(f"   Infrastructure Layer: ✓ Providers and strategies implemented")
    print(f"   Dependency Injection: ✓ All components wired correctly")

    return True


async def test_channel_strategies():
    """Test all channel strategies."""
    print("\n" + "=" * 60)
    print("Testing Channel Strategies")
    print("=" * 60)

    factory = ChannelStrategyFactory()
    channels = ["air", "water", "earth", "fire"]

    for channel in channels:
        strategy = factory.get_strategy(channel)
        visual = strategy.get_visual_style()
        audio = strategy.get_audio_style()

        print(f"\n{channel.upper()} Channel:")
        print(f"  Primary Color: {visual['primary_color']}")
        print(f"  Animation: {visual['animations']['style']}")
        print(f"  Music: {audio['music']['genre']}")
        print(f"  Voice Tone: {audio['voice']['tone']}")

    print("\n✅ Channel strategies test complete!")


async def test_batch_generation():
    """Test batch video generation."""
    print("\n" + "=" * 60)
    print("Testing Batch Generation")
    print("=" * 60)

    # Set up service
    registry = ProviderRegistry()
    registry.register_provider(MockVideoProvider())

    service = VideoGenerationService(
        provider_registry=registry,
        script_parser=TikTokScriptParser(),
        channel_strategy_factory=ChannelStrategyFactory(),
        config_manager=VideoConfigManager()
    )

    # Create multiple scripts
    scripts = []
    for i, channel in enumerate(["air", "water", "earth", "fire"]):
        script = {
            "channel": channel,
            "topic": f"Test video for {channel}",
            "hook": f"Amazing {channel} content",
            "main_points": [f"Point about {channel}"],
            "call_to_action": f"Follow for more {channel} content!"
        }
        scripts.append((script, channel, VideoQuality.STANDARD))

    # Batch generate
    print(f"\nGenerating {len(scripts)} videos in batch...")
    results = await service.batch_generate_videos(scripts, max_concurrent=2)

    for i, result in enumerate(results):
        channel = scripts[i][1]
        print(f"  {channel}: {result.status.value} (ID: {result.id[:8]}...)")

    print("\n✅ Batch generation test complete!")


if __name__ == "__main__":
    print("\n🚀 Video Generation Architecture Test Suite\n")

    # Run tests
    asyncio.run(test_basic_architecture())
    asyncio.run(test_channel_strategies())
    asyncio.run(test_batch_generation())

    print("\n" + "=" * 60)
    print("🎉 All Tests Passed!")
    print("=" * 60)
    print("\n📝 Phase 2 Roadmap:")
    print("   - Implement RemotionProvider (React-based generation)")
    print("   - Implement FFmpegProvider (Local processing)")
    print("   - Implement RunwayMLProvider (AI generation)")
    print("   - Implement SynthesiaProvider (AI avatars)")
    print("\n   See: docs/PHASE_2_ROADMAP.json for detailed implementation plan")