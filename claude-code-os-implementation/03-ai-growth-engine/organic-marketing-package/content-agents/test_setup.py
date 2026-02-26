#!/usr/bin/env python3
"""
Test Setup Script
Verifies that the AI Content Agents system is configured correctly
"""
import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from agents import BlogAgent, SocialAgent, AmazonAgent, CompetitorAgent
        print("✅ All agent modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def test_api_key():
    """Test that API key is set"""
    print("\nTesting API key...")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("Or create a .env file (see .env.example)")
        return False
    elif api_key == 'your-api-key-here':
        print("❌ ANTHROPIC_API_KEY is still set to example value")
        print("Get your real API key from: https://console.anthropic.com/")
        return False
    else:
        print(f"✅ API key found (starts with: {api_key[:10]}...)")
        return True


def test_brand_files():
    """Test that brand context files exist"""
    print("\nTesting brand context files...")
    from config.config import (
        BRAND_VOICE_PATH,
        BRAND_STRATEGY_PATH,
        CONTENT_STRATEGY_PATH,
        VALUE_PROP_PATH,
        TARGET_MARKET_PATH
    )

    files_to_check = {
        "Brand Voice Guide": BRAND_VOICE_PATH,
        "Brand Strategy": BRAND_STRATEGY_PATH,
        "Content Strategy": CONTENT_STRATEGY_PATH,
        "Value Proposition": VALUE_PROP_PATH,
        "Target Market": TARGET_MARKET_PATH
    }

    all_exist = True
    for name, path in files_to_check.items():
        if path.exists():
            print(f"✅ {name}: Found")
        else:
            print(f"⚠️  {name}: Not found at {path}")
            all_exist = False

    if all_exist:
        print("✅ All brand context files found")
    else:
        print("⚠️  Some brand files missing (agents will work but with less context)")

    return all_exist


def test_output_directories():
    """Test that output directories exist"""
    print("\nTesting output directories...")
    from config.config import (
        BLOG_OUTPUT_DIR,
        SOCIAL_OUTPUT_DIR,
        AMAZON_OUTPUT_DIR,
        COMPETITOR_OUTPUT_DIR
    )

    dirs = {
        "Blog": BLOG_OUTPUT_DIR,
        "Social": SOCIAL_OUTPUT_DIR,
        "Amazon": AMAZON_OUTPUT_DIR,
        "Competitor": COMPETITOR_OUTPUT_DIR
    }

    all_exist = True
    for name, path in dirs.items():
        if path.exists():
            print(f"✅ {name} output directory exists")
        else:
            print(f"❌ {name} output directory missing: {path}")
            all_exist = False

    return all_exist


def test_agent_initialization():
    """Test that agents can be initialized"""
    print("\nTesting agent initialization...")

    try:
        from agents import BlogAgent, SocialAgent, AmazonAgent, CompetitorAgent

        # Only initialize if API key exists
        if not os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY') == 'your-api-key-here':
            print("⚠️  Skipping agent initialization (no valid API key)")
            return True

        blog_agent = BlogAgent()
        print("✅ BlogAgent initialized")

        social_agent = SocialAgent()
        print("✅ SocialAgent initialized")

        amazon_agent = AmazonAgent()
        print("✅ AmazonAgent initialized")

        competitor_agent = CompetitorAgent()
        print("✅ CompetitorAgent initialized")

        print("✅ All agents initialized successfully")
        return True

    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI CONTENT AGENTS - SETUP TEST")
    print("=" * 60)

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test API key
    results.append(("API Key", test_api_key()))

    # Test brand files
    results.append(("Brand Files", test_brand_files()))

    # Test output directories
    results.append(("Output Dirs", test_output_directories()))

    # Test agent initialization
    results.append(("Agent Init", test_agent_initialization()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to generate content.")
        print("\nNext steps:")
        print("  1. Run: python quick_start.py")
        print("  2. Or: python generate_content.py --help")
        print("  3. Or: Check README.md for more examples")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("Check README.md for setup instructions.")

    print("=" * 60)


if __name__ == '__main__':
    main()
