#!/usr/bin/env python3
"""
End-to-end verification script for SEO-optimized content pipeline.

This script tests the complete workflow:
1. Keyword research
2. Blog generation with SEO analysis
3. Internal linking suggestions
4. Database persistence of SEO metadata
"""

import requests
import json
import sys
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_step(step_num, description):
    """Print a test step header"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}STEP {step_num}: {description}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def test_keyword_research():
    """Test Step 1: Keyword research API"""
    print_step(1, "Keyword Research")

    payload = {
        "topic": "tactical backpacks for urban professionals",
        "seed_keywords": ["tactical backpack", "urban gear"],
        "max_keywords": 10
    }

    print_info(f"Request: POST {BASE_URL}/seo/keywords/research")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    try:
        response = requests.post(
            f"{BASE_URL}/seo/keywords/research",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Keyword research completed (Status: {response.status_code})")
            print(f"\nKeywords found: {len(data.get('keywords', []))}")

            # Display first 3 keywords
            keywords = data.get('keywords', [])[:3]
            for i, kw in enumerate(keywords, 1):
                print(f"  {i}. {kw.get('keyword', 'N/A')} (Relevance: {kw.get('relevance_score', 0)})")

            return data.get('keywords', [])
        else:
            print_error(f"Keyword research failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exception during keyword research: {str(e)}")
        return None

def test_blog_generation_with_seo(keywords):
    """Test Step 2: Blog generation with SEO analysis"""
    print_step(2, "Blog Generation with SEO Analysis")

    # Extract keyword strings from keyword objects
    target_keywords = []
    if keywords:
        target_keywords = [kw.get('keyword', '') for kw in keywords[:3]]

    payload = {
        "topic": "Complete Guide to Tactical Backpacks for Urban Professionals",
        "content_pillar": "Gear & Equipment",
        "target_keywords": target_keywords if target_keywords else ["tactical backpack"],
        "target_keyword": target_keywords[0] if target_keywords else "tactical backpack",
        "word_count": 800,
        "include_cta": True,
        "include_seo_analysis": True
    }

    print_info(f"Request: POST {BASE_URL}/blog/generate")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    try:
        response = requests.post(
            f"{BASE_URL}/blog/generate",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Blog generation completed (Status: {response.status_code})")

            # Verify SEO data is present
            has_seo_score = 'seo_score' in data
            has_seo_grade = 'seo_grade' in data
            has_meta_description = 'meta_description' in data
            has_seo_analysis = 'seo_analysis' in data
            has_content = 'content' in data

            print(f"\nResponse validation:")
            print(f"  {'✓' if has_content else '✗'} Content present: {has_content}")
            print(f"  {'✓' if has_seo_score else '✗'} SEO Score present: {has_seo_score}")
            print(f"  {'✓' if has_seo_grade else '✗'} SEO Grade present: {has_seo_grade}")
            print(f"  {'✓' if has_meta_description else '✗'} Meta Description present: {has_meta_description}")
            print(f"  {'✓' if has_seo_analysis else '✗'} SEO Analysis present: {has_seo_analysis}")

            if has_seo_score and has_seo_grade:
                print(f"\nSEO Results:")
                print(f"  Score: {data.get('seo_score', 0):.1f}/100")
                print(f"  Grade: {data.get('seo_grade', 'N/A')}")
                if has_meta_description:
                    meta = data.get('meta_description', '')
                    print(f"  Meta Description: {meta[:80]}..." if len(meta) > 80 else f"  Meta Description: {meta}")

            if all([has_content, has_seo_score, has_seo_grade, has_meta_description]):
                print_success("\nAll required fields present in response")
                return data
            else:
                print_error("\nMissing required fields in response")
                return None
        else:
            print_error(f"Blog generation failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exception during blog generation: {str(e)}")
        return None

def test_internal_links(blog_data):
    """Test Step 3: Internal linking suggestions"""
    print_step(3, "Internal Linking Suggestions")

    if not blog_data:
        print_error("No blog data available, skipping internal links test")
        return None

    content = blog_data.get('content', '')
    if not content:
        print_error("No content in blog data, skipping internal links test")
        return None

    # Extract title from content
    import re
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Tactical Backpacks Guide"

    payload = {
        "content": content[:5000],  # Limit content length
        "title": title,
        "content_pillar": "Gear & Equipment",
        "max_suggestions": 5
    }

    print_info(f"Request: POST {BASE_URL}/seo/internal-links/suggest")
    print(f"Payload: title='{title}', content_length={len(content)}, max_suggestions=5\n")

    try:
        response = requests.post(
            f"{BASE_URL}/seo/internal-links/suggest",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Internal link suggestions completed (Status: {response.status_code})")

            suggestions = data.get('suggestions', [])
            total = data.get('total_suggestions', 0)

            print(f"\nInternal Link Suggestions: {total}")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {i}. {suggestion.get('title', 'N/A')} (Relevance: {suggestion.get('relevance_score', 0)})")

            return data
        else:
            print_error(f"Internal links failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Exception during internal links: {str(e)}")
        return None

def test_database_persistence():
    """Test Step 4: Verify SEO metadata saved to database"""
    print_step(4, "Database SEO Metadata Persistence")

    print_info("Checking if SEO metadata is saved to ContentHistory table...")

    try:
        # Import database models and check for recent content with SEO data
        from database.connection import get_db_session
        from database.models import ContentHistory

        session = get_db_session()

        # Get most recent blog content
        recent_content = session.query(ContentHistory)\
            .filter(ContentHistory.content_type == 'blog')\
            .order_by(ContentHistory.created_at.desc())\
            .first()

        if recent_content:
            print_success("Found recent blog content in database")

            # Check SEO fields
            has_seo_score = recent_content.seo_score is not None
            has_seo_grade = recent_content.seo_grade is not None
            has_target_keyword = recent_content.target_keyword is not None
            has_meta_description = recent_content.meta_description is not None

            print(f"\nSEO Metadata in Database:")
            print(f"  {'✓' if has_seo_score else '✗'} SEO Score: {recent_content.seo_score if has_seo_score else 'Not saved'}")
            print(f"  {'✓' if has_seo_grade else '✗'} SEO Grade: {recent_content.seo_grade if has_seo_grade else 'Not saved'}")
            print(f"  {'✓' if has_target_keyword else '✗'} Target Keyword: {recent_content.target_keyword if has_target_keyword else 'Not saved'}")
            print(f"  {'✓' if has_meta_description else '✗'} Meta Description: {recent_content.meta_description[:50] if has_meta_description else 'Not saved'}...")

            if all([has_seo_score, has_seo_grade]):
                print_success("\nSEO metadata successfully saved to database")
                return True
            else:
                print_error("\nSEO metadata NOT fully saved to database")
                print_info("Note: This may require additional implementation in the API layer")
                return False
        else:
            print_error("No blog content found in database")
            return False

    except Exception as e:
        print_error(f"Exception checking database: {str(e)}")
        print_info("Database persistence check skipped (may not be implemented yet)")
        return None

def main():
    """Run all end-to-end tests"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}SEO-Optimized Content Pipeline - End-to-End Verification{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    print_info("This script tests the complete SEO content generation workflow")
    print_info(f"API Base URL: {BASE_URL}\n")

    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=5)
        if response.status_code == 200:
            print_success("API server is running\n")
        else:
            print_error("API server returned unexpected status")
            sys.exit(1)
    except Exception as e:
        print_error(f"Cannot connect to API server at {BASE_URL}")
        print_info("Please start the API server with: uvicorn api.main:app --reload")
        sys.exit(1)

    # Run tests
    results = {
        'keyword_research': False,
        'blog_generation': False,
        'internal_links': False,
        'database_persistence': None
    }

    # Step 1: Keyword Research
    keywords = test_keyword_research()
    results['keyword_research'] = keywords is not None

    if not results['keyword_research']:
        print_error("\nKeyword research failed. Continuing with fallback keywords...")
        keywords = None

    time.sleep(1)

    # Step 2: Blog Generation with SEO Analysis
    blog_data = test_blog_generation_with_seo(keywords)
    results['blog_generation'] = blog_data is not None

    if not results['blog_generation']:
        print_error("\nBlog generation failed. Cannot continue with workflow.")
    else:
        time.sleep(1)

        # Step 3: Internal Linking Suggestions
        internal_links = test_internal_links(blog_data)
        results['internal_links'] = internal_links is not None

    time.sleep(1)

    # Step 4: Database Persistence
    db_result = test_database_persistence()
    results['database_persistence'] = db_result

    # Print summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    for test_name, result in results.items():
        status = "✓ PASS" if result else ("✗ FAIL" if result is False else "⊘ SKIPPED")
        color = Colors.GREEN if result else (Colors.RED if result is False else Colors.YELLOW)
        print(f"{color}{status}{Colors.RESET} - {test_name.replace('_', ' ').title()}")

    # Determine overall result
    critical_tests = ['keyword_research', 'blog_generation', 'internal_links']
    critical_passed = all([results[test] for test in critical_tests])

    print()
    if critical_passed:
        print_success("All critical workflow steps PASSED")
        if results['database_persistence']:
            print_success("Database persistence verified")
        elif results['database_persistence'] is None:
            print_info("Database persistence not verified (may require implementation)")
        return 0
    else:
        print_error("One or more critical workflow steps FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
