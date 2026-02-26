#!/usr/bin/env python3
"""
Quick Content Generation Script
Easy-to-use CLI for generating content with AI agents
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agents import BlogAgent, SocialAgent, AmazonAgent, CompetitorAgent
import argparse


def generate_blog(args):
    """Generate blog content"""
    agent = BlogAgent()

    if args.type == "post":
        print(f"📝 Generating blog post: {args.topic}")
        content, path = agent.generate_blog_post(
            topic=args.topic,
            content_pillar=args.pillar,
            target_keywords=args.keywords.split(',') if args.keywords else None,
            word_count=args.words
        )
        print(f"\n✅ Blog post generated!\n")
        print(content[:500] + "...\n")
        print(f"📄 Full content saved to: {path}")

    elif args.type == "listicle":
        print(f"📝 Generating listicle: {args.topic}")
        content, path = agent.generate_listicle(
            topic=args.topic,
            num_items=args.items,
            content_pillar=args.pillar
        )
        print(f"\n✅ Listicle generated!\n")
        print(content[:500] + "...\n")
        print(f"📄 Full content saved to: {path}")

    elif args.type == "howto":
        print(f"📝 Generating how-to guide: {args.topic}")
        content, path = agent.generate_how_to_guide(
            topic=args.topic,
            target_audience=args.audience or "Tournament players",
            difficulty_level=args.difficulty or "beginner"
        )
        print(f"\n✅ How-to guide generated!\n")
        print(content[:500] + "...\n")
        print(f"📄 Full content saved to: {path}")


def generate_social(args):
    """Generate social media content"""
    agent = SocialAgent()

    if args.platform == "instagram":
        print(f"📱 Generating Instagram post: {args.topic}")
        content, path = agent.generate_instagram_post(
            topic=args.topic,
            content_pillar=args.pillar,
            image_description=args.image
        )
        print(f"\n✅ Instagram post generated!\n")
        print(content)
        print(f"\n📄 Saved to: {path}")

    elif args.platform == "reddit":
        print(f"📱 Generating Reddit post: {args.topic}")
        content, path = agent.generate_reddit_post(
            subreddit=args.subreddit or "TCG",
            topic=args.topic,
            post_type=args.type or "discussion",
            include_product_mention=args.mention_product
        )
        print(f"\n✅ Reddit post generated!\n")
        print(content)
        print(f"\n📄 Saved to: {path}")

    elif args.platform == "calendar":
        print(f"📅 Generating {args.days}-day content calendar for {args.for_platform}")
        content, path = agent.generate_content_calendar(
            platform=args.for_platform,
            num_days=args.days,
            content_pillar=args.pillar
        )
        print(f"\n✅ Content calendar generated!\n")
        print(content[:500] + "...\n")
        print(f"📄 Full calendar saved to: {path}")

    elif args.platform == "batch":
        print(f"📱 Batch generating {args.count} {args.for_platform} posts")
        results = agent.batch_generate_posts(
            platform=args.for_platform,
            num_posts=args.count
        )
        print(f"\n✅ Generated {len(results)} posts!")
        for i, (content, path) in enumerate(results):
            print(f"\n{i+1}. {path}")


def generate_amazon(args):
    """Generate Amazon listing content"""
    agent = AmazonAgent()

    if args.type == "title":
        print(f"🛒 Generating Amazon title for: {args.product}")
        content, path = agent.generate_product_title(
            product_name=args.product,
            key_features=args.features.split(',') if args.features else [],
            target_keywords=args.keywords.split(',') if args.keywords else []
        )
        print(f"\n✅ Title generated!\n")
        print(content)
        print(f"\n📄 Saved to: {path}")

    elif args.type == "bullets":
        print(f"🛒 Generating bullet points for: {args.product}")
        # Parse features (format: "feature1:benefit1,feature2:benefit2")
        features = []
        if args.features:
            for f in args.features.split(','):
                if ':' in f:
                    feat, ben = f.split(':', 1)
                    features.append({'feature': feat.strip(), 'benefit': ben.strip()})
                else:
                    features.append({'feature': f.strip(), 'benefit': ''})

        content, path = agent.generate_bullet_points(
            product_name=args.product,
            features=features,
            target_audience=args.audience or "Tournament players and serious collectors"
        )
        print(f"\n✅ Bullet points generated!\n")
        print(content)
        print(f"\n📄 Saved to: {path}")

    elif args.type == "description":
        print(f"🛒 Generating product description for: {args.product}")
        content, path = agent.generate_product_description(
            product_name=args.product,
            long_description=args.details or "Premium TCG storage product",
            usp=args.usp or "Battle-Ready Equipment for Serious Players"
        )
        print(f"\n✅ Description generated!\n")
        print(content[:500] + "...\n")
        print(f"📄 Full description saved to: {path}")


def generate_competitor(args):
    """Generate competitor analysis"""
    agent = CompetitorAgent()

    if args.type == "listing":
        print(f"🔍 Analyzing competitor: {args.name}")
        # This would need actual competitor data
        print("⚠️  This requires competitor data. See README for data format.")
        print("Example usage in Python:")
        print("""
from agents import CompetitorAgent
agent = CompetitorAgent()
agent.analyze_competitor_listing(
    competitor_name="Competitor Name",
    product_title="Their product title",
    bullet_points=["Bullet 1", "Bullet 2", ...],
    description="Their description",
    price=29.99,
    rating=4.5
)
        """)

    elif args.type == "reviews":
        print(f"🔍 Analyzing reviews for: {args.name}")
        print("⚠️  This requires review data. See README for data format.")

    elif args.type == "comparison":
        print(f"🔍 Creating competitive comparison")
        print("⚠️  This requires multiple competitor data. See README for data format.")


def main():
    parser = argparse.ArgumentParser(description="AI Content Generation for Infinity Vault")
    subparsers = parser.add_subparsers(dest='command', help='Content type to generate')

    # Blog command
    blog_parser = subparsers.add_parser('blog', help='Generate blog content')
    blog_parser.add_argument('type', choices=['post', 'listicle', 'howto'], help='Blog type')
    blog_parser.add_argument('topic', help='Blog topic')
    blog_parser.add_argument('--pillar', help='Content pillar')
    blog_parser.add_argument('--keywords', help='Target keywords (comma-separated)')
    blog_parser.add_argument('--words', type=int, default=1000, help='Word count')
    blog_parser.add_argument('--items', type=int, default=10, help='Number of items (for listicle)')
    blog_parser.add_argument('--audience', help='Target audience (for how-to)')
    blog_parser.add_argument('--difficulty', choices=['beginner', 'intermediate', 'advanced'], help='Difficulty level')

    # Social command
    social_parser = subparsers.add_parser('social', help='Generate social media content')
    social_parser.add_argument('platform', choices=['instagram', 'reddit', 'calendar', 'batch'], help='Social platform')
    social_parser.add_argument('topic', nargs='?', help='Post topic')
    social_parser.add_argument('--pillar', help='Content pillar')
    social_parser.add_argument('--image', help='Image description (for Instagram)')
    social_parser.add_argument('--subreddit', help='Subreddit name (for Reddit)')
    social_parser.add_argument('--type', help='Post type (for Reddit)')
    social_parser.add_argument('--mention-product', action='store_true', help='Include product mention')
    social_parser.add_argument('--days', type=int, default=7, help='Calendar days')
    social_parser.add_argument('--for-platform', help='Platform for calendar/batch')
    social_parser.add_argument('--count', type=int, default=5, help='Number of posts for batch')

    # Amazon command
    amazon_parser = subparsers.add_parser('amazon', help='Generate Amazon listing content')
    amazon_parser.add_argument('type', choices=['title', 'bullets', 'description', 'aplus', 'keywords'], help='Listing element')
    amazon_parser.add_argument('product', help='Product name')
    amazon_parser.add_argument('--features', help='Features (comma-separated)')
    amazon_parser.add_argument('--keywords', help='Keywords (comma-separated)')
    amazon_parser.add_argument('--audience', help='Target audience')
    amazon_parser.add_argument('--details', help='Product details')
    amazon_parser.add_argument('--usp', help='Unique selling proposition')

    # Competitor command
    competitor_parser = subparsers.add_parser('competitor', help='Analyze competitors')
    competitor_parser.add_argument('type', choices=['listing', 'reviews', 'comparison'], help='Analysis type')
    competitor_parser.add_argument('--name', help='Competitor name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    # Route to appropriate handler
    if args.command == 'blog':
        generate_blog(args)
    elif args.command == 'social':
        generate_social(args)
    elif args.command == 'amazon':
        generate_amazon(args)
    elif args.command == 'competitor':
        generate_competitor(args)


if __name__ == '__main__':
    main()
