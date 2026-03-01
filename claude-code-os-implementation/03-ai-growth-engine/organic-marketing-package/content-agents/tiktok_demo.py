#!/usr/bin/env python3
"""
Demo script showing how the system helps create TikTok video content
"""

from agents.tiktok_channel_agent import TikTokChannelAgent
import json

def demonstrate_tiktok_content_creation():
    """Show how the system creates TikTok video content"""

    # Initialize the TikTok agent
    agent = TikTokChannelAgent()

    print("=" * 70)
    print("INFINITY VAULT TIKTOK CONTENT CREATION SYSTEM")
    print("4-Channel Element Strategy: Air, Water, Fire, Earth")
    print("=" * 70)

    # Show available channels
    print("\n📱 Available TikTok Channels:")
    for element in ['air', 'water', 'fire', 'earth']:
        specs = agent.get_channel_specs(element)
        print(f"\n🔹 {element.upper()} Channel - {specs['channel_name']}")
        print(f"   Audience: {specs['target_audience']}")
        print(f"   Tone: {specs['tone']}")
        print(f"   Focus: {specs['content_focus']}")

    print("\n" + "=" * 70)

    # Example 1: Generate Air Channel Video Script (Quick Tips)
    print("\n1️⃣ GENERATING AIR CHANNEL VIDEO (Quick Tournament Tips)")
    print("-" * 50)

    script, path = agent.generate_channel_video_script(
        channel_element='air',
        topic='5 Second Deck Check Before Tournament',
        product='Tournament Ready Deck Box',
        include_product_link=True
    )

    print("\n📄 Generated Script Preview:")
    print(script[:500] + "...\n")
    print(f"✅ Full script saved to: {path}")

    # Example 2: Generate Water Channel Video Script (Community Stories)
    print("\n2️⃣ GENERATING WATER CHANNEL VIDEO (Community Content)")
    print("-" * 50)

    script, path = agent.generate_channel_video_script(
        channel_element='water',
        topic='My First Tournament Story - From Nervous to Champion',
        product='Infinity Vault Collector Binder',
        include_product_link=False
    )

    print("\n📄 Generated Script Preview:")
    print(script[:500] + "...\n")
    print(f"✅ Full script saved to: {path}")

    # Example 3: Generate Fire Channel Video Script (Hot Takes)
    print("\n3️⃣ GENERATING FIRE CHANNEL VIDEO (Controversial Opinion)")
    print("-" * 50)

    script, path = agent.generate_channel_video_script(
        channel_element='fire',
        topic='Why Your Expensive Sleeves Are Actually WORSE',
        product='Battle Ready Card Sleeves',
        include_product_link=True
    )

    print("\n📄 Generated Script Preview:")
    print(script[:500] + "...\n")
    print(f"✅ Full script saved to: {path}")

    # Example 4: Generate Earth Channel Video Script (Product Deep Dive)
    print("\n4️⃣ GENERATING EARTH CHANNEL VIDEO (Educational)")
    print("-" * 50)

    script, path = agent.generate_channel_video_script(
        channel_element='earth',
        topic='Complete Guide to Organizing Your Card Collection',
        product='9-Pocket Premium Pages',
        include_product_link=True
    )

    print("\n📄 Generated Script Preview:")
    print(script[:500] + "...\n")
    print(f"✅ Full script saved to: {path}")

    # Generate Content Calendar
    print("\n" + "=" * 70)
    print("📅 GENERATING 7-DAY CONTENT CALENDAR")
    print("-" * 50)

    calendar, path = agent.generate_channel_content_calendar(
        channel_element='air',
        days_ahead=7,
        posts_per_day=3
    )

    print("\n📆 Sample Calendar Entry:")
    # Parse and show first day
    lines = calendar.split('\n')
    for i, line in enumerate(lines[:20]):
        if line.strip():
            print(line)

    print(f"\n✅ Full calendar saved to: {path}")

    # Multi-Channel Strategy
    print("\n" + "=" * 70)
    print("🎯 GENERATING MULTI-CHANNEL CAMPAIGN")
    print("-" * 50)

    strategy, path = agent.generate_multi_channel_strategy(
        campaign_name='Holiday Tournament Prep',
        campaign_goal='Drive sales of tournament accessories',
        duration_days=7,
        channels=['air', 'fire', 'earth']
    )

    print("\n📊 Campaign Strategy Preview:")
    print(strategy[:800] + "...\n")
    print(f"✅ Full strategy saved to: {path}")

    print("\n" + "=" * 70)
    print("✨ TIKTOK CONTENT GENERATION COMPLETE!")
    print("=" * 70)

    print("\n🎬 What the System Generated:")
    print("• 4 channel-specific video scripts with:")
    print("  - Opening hooks (0-3 seconds)")
    print("  - Main content with visual directions")
    print("  - Text overlay suggestions")
    print("  - Music recommendations")
    print("  - Call-to-action endings")
    print("  - Hashtag strategies")
    print("\n• 7-day content calendar with 3 posts per day")
    print("• Multi-channel campaign strategy")
    print("\n• Each script tailored to channel's:")
    print("  - Target audience")
    print("  - Content tone")
    print("  - Engagement style")
    print("  - Product integration approach")

if __name__ == "__main__":
    demonstrate_tiktok_content_creation()