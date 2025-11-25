#!/usr/bin/env python3
"""
Quick Start Script - Generate Content Fast
No command line arguments needed, just edit this file and run it!
"""
import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(__file__))

from agents import BlogAgent, SocialAgent, AmazonAgent, CompetitorAgent


def main():
    """
    Quick content generation examples
    Uncomment the sections you want to use!
    """

    print("🚀 Infinity Vault AI Content Generator - Quick Start\n")

    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY not found")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # ============================================================================
    # BLOG POSTS
    # ============================================================================

    # Example 1: Generate a blog post
    # blog_agent = BlogAgent()
    # content, path = blog_agent.generate_blog_post(
    #     topic="How to Prepare Your TCG Deck for Tournament Day",
    #     content_pillar="Battle-Ready Lifestyle",
    #     target_keywords=["tournament prep", "tcg storage", "card protection"],
    #     word_count=1200
    # )
    # print(f"✅ Blog post saved to: {path}\n")

    # Example 2: Generate a listicle
    # blog_agent = BlogAgent()
    # content, path = blog_agent.generate_listicle(
    #     topic="10 Tournament Prep Mistakes Every TCG Player Makes",
    #     num_items=10,
    #     content_pillar="Battle-Ready Lifestyle"
    # )
    # print(f"✅ Listicle saved to: {path}\n")

    # Example 3: Generate a how-to guide
    # blog_agent = BlogAgent()
    # content, path = blog_agent.generate_how_to_guide(
    #     topic="How to Organize Your Trading Card Collection Like a Pro",
    #     target_audience="Serious collectors",
    #     difficulty_level="intermediate"
    # )
    # print(f"✅ How-to guide saved to: {path}\n")

    # ============================================================================
    # SOCIAL MEDIA
    # ============================================================================

    # Example 4: Generate Instagram post
    # social_agent = SocialAgent()
    # content, path = social_agent.generate_instagram_post(
    #     topic="Pre-tournament ritual and preparation",
    #     content_pillar="Battle-Ready Lifestyle",
    #     image_description="Player organizing their deck in an Infinity Vault binder before a tournament"
    # )
    # print(f"✅ Instagram post saved to: {path}\n")

    # Example 5: Generate Reddit post
    # social_agent = SocialAgent()
    # content, path = social_agent.generate_reddit_post(
    #     subreddit="PokemonTCG",
    #     topic="What's your pre-tournament preparation routine?",
    #     post_type="discussion",
    #     include_product_mention=False  # Pure value, no selling
    # )
    # print(f"✅ Reddit post saved to: {path}\n")

    # Example 6: Generate 7-day content calendar
    # social_agent = SocialAgent()
    # content, path = social_agent.generate_content_calendar(
    #     platform="instagram",
    #     num_days=7,
    #     content_pillar="Battle-Ready Lifestyle"
    # )
    # print(f"✅ Content calendar saved to: {path}\n")

    # Example 7: Batch generate 5 Instagram posts
    # social_agent = SocialAgent()
    # results = social_agent.batch_generate_posts(
    #     platform="instagram",
    #     num_posts=5
    # )
    # print(f"✅ Generated {len(results)} Instagram posts\n")

    # ============================================================================
    # AMAZON LISTINGS
    # ============================================================================

    # Example 8: Generate product title
    # amazon_agent = AmazonAgent()
    # content, path = amazon_agent.generate_product_title(
    #     product_name="Premium Trading Card Binder",
    #     key_features=["9-pocket pages", "scratch-resistant", "lifetime warranty"],
    #     target_keywords=["trading card binder", "pokemon card storage", "tcg binder"]
    # )
    # print(f"✅ Product title saved to: {path}\n")

    # Example 9: Generate bullet points
    # amazon_agent = AmazonAgent()
    # content, path = amazon_agent.generate_bullet_points(
    #     product_name="Premium Trading Card Binder",
    #     features=[
    #         {"feature": "Scratch-resistant pages", "benefit": "Cards stay pristine"},
    #         {"feature": "Reinforced binding", "benefit": "Lasts through countless tournaments"},
    #         {"feature": "9-pocket layout", "benefit": "Perfect organization for deck building"},
    #         {"feature": "Lifetime warranty", "benefit": "Investment protection"},
    #         {"feature": "Professional-grade materials", "benefit": "Tournament-ready quality"}
    #     ]
    # )
    # print(f"✅ Bullet points saved to: {path}\n")

    # Example 10: Generate product description
    # amazon_agent = AmazonAgent()
    # content, path = amazon_agent.generate_product_description(
    #     product_name="Premium Trading Card Binder",
    #     long_description="Professional-grade 9-pocket trading card binder with scratch-resistant pages, reinforced binding, and lifetime warranty. Holds up to 360 cards.",
    #     usp="Battle-Ready Equipment for Serious TCG Players"
    # )
    # print(f"✅ Product description saved to: {path}\n")

    # ============================================================================
    # COMPETITOR ANALYSIS
    # ============================================================================

    # Example 11: Analyze competitor listing
    # competitor_agent = CompetitorAgent()
    # content, path = competitor_agent.analyze_competitor_listing(
    #     competitor_name="Generic Brand X",
    #     product_title="Trading Card Binder - 9 Pocket Pages - Holds 360 Cards - Black",
    #     bullet_points=[
    #         "Holds 360 standard trading cards",
    #         "9 pocket pages",
    #         "Durable construction",
    #         "Available in multiple colors",
    #         "Great for Pokemon, Magic, and sports cards"
    #     ],
    #     description="This trading card binder holds up to 360 cards in 9-pocket pages. Perfect for storing your collection.",
    #     price=19.99,
    #     rating=4.3,
    #     review_count=1250
    # )
    # print(f"✅ Competitor analysis saved to: {path}\n")

    # ============================================================================
    # QUICK START EXAMPLES - UNCOMMENT ONE TO TRY
    # ============================================================================

    print("📝 Quick Start Examples:\n")
    print("Uncomment any example above in quick_start.py and run again!\n")
    print("Examples available:")
    print("  1. Blog post generation")
    print("  2. Listicle generation")
    print("  3. How-to guide")
    print("  4. Instagram post")
    print("  5. Reddit post")
    print("  6. Content calendar")
    print("  7. Batch social posts")
    print("  8. Amazon title")
    print("  9. Amazon bullets")
    print("  10. Amazon description")
    print("  11. Competitor analysis")
    print("\n💡 Or use generate_content.py for CLI interface")
    print("   Example: python generate_content.py blog post 'Tournament Prep Tips'\n")


if __name__ == '__main__':
    main()
