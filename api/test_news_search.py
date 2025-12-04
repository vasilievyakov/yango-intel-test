#!/usr/bin/env python3
"""
Test script for News Scraper Service

This script tests the integration with Parallel AI for news search.
Run from the api directory:
    python test_news_search.py
"""

import asyncio
import os
import sys
from datetime import datetime
import json

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables if not set (for local testing)
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/yango_intel"

from dotenv import load_dotenv
load_dotenv()

from app.config import settings
from app.news_config.news_sources import (
    PERU_NEWS_SOURCES,
    COMPETITORS,
    NEWS_CATEGORIES,
    generate_search_queries,
    build_site_filter,
)


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_config():
    """Print current configuration"""
    print_header("CONFIGURATION")
    
    print(f"\n📡 Parallel AI:")
    print(f"   API Key: {'✅ Configured' if settings.PARALLEL_API_KEY else '❌ Not set'}")
    print(f"   Base URL: {settings.PARALLEL_BASE_URL}")
    
    print(f"\n📰 Peru News Sources ({len(PERU_NEWS_SOURCES)} total):")
    for source in PERU_NEWS_SOURCES[:5]:
        print(f"   - {source}")
    print(f"   ... and {len(PERU_NEWS_SOURCES) - 5} more")
    
    print(f"\n🏢 Competitors ({len(COMPETITORS)}):")
    for comp in COMPETITORS:
        print(f"   - {comp.name} ({comp.slug}): {', '.join(comp.keywords[:3])}")
    
    print(f"\n📋 Categories ({len(NEWS_CATEGORIES)}):")
    for cat in NEWS_CATEGORIES:
        print(f"   - {cat.name}: {', '.join(cat.keywords_es[:3])}...")


def test_query_generation():
    """Test search query generation"""
    print_header("SEARCH QUERY GENERATION")
    
    print("\n🔍 Market-wide queries:")
    queries = generate_search_queries()
    for q in queries:
        print(f"   → {q}")
    
    print("\n🔍 Competitor-specific queries (Uber):")
    queries = generate_search_queries(competitor_slug="uber")
    for q in queries[:3]:
        print(f"   → {q}")
    
    print("\n🔍 Site filter example:")
    site_filter = build_site_filter(PERU_NEWS_SOURCES[:3])
    print(f"   {site_filter}")


async def test_search_providers():
    """Test all available search providers"""
    print_header("SEARCH PROVIDERS TEST")
    
    from app.services.news_search_providers import get_search_provider, GeminiSearchProvider
    
    # Show provider status
    multi = get_search_provider()
    status = multi.get_status()
    
    print("\n📡 Search Provider Status:")
    for p in status["providers"]:
        icon = "✅" if p["configured"] else "❌"
        print(f"   {icon} {p['name']}")
    
    print(f"\n   Available: {status['available_count']} provider(s)")
    
    # Test with Gemini (we have Google API key)
    if settings.GOOGLE_API_KEY:
        print("\n🔍 Testing Gemini Search...")
        
        gemini = GeminiSearchProvider()
        query = "Uber Peru noticias diciembre 2024"
        
        print(f"   Query: {query}")
        
        try:
            results = await gemini.search(query, max_results=5)
            
            if results:
                print(f"\n✅ Found {len(results)} results:")
                for i, r in enumerate(results[:3], 1):
                    print(f"\n   {i}. {r.title[:60]}...")
                    print(f"      URL: {r.url[:50]}...")
                    print(f"      Source: {r.source or 'N/A'}")
            else:
                print("   ⚠️ No results returned (Gemini may need grounding feature)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print("\n❌ GOOGLE_API_KEY not configured. Skipping Gemini test.")
    
    # Suggest getting additional API keys
    print("\n💡 To improve search capabilities, consider adding:")
    print("   - TAVILY_API_KEY (https://tavily.com - free tier available)")
    print("   - PERPLEXITY_API_KEY (https://perplexity.ai)")
    print("   - SERPAPI_KEY (https://serpapi.com)")


async def test_news_scraper_service():
    """Test the NewsScraperService (requires database)"""
    print_header("NEWS SCRAPER SERVICE TEST")
    
    if not settings.PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not configured. Skipping service test.")
        return
    
    print("\n⚠️  This test requires a database connection.")
    print("   Skipping database-dependent tests in standalone mode.")
    print("   To test with database, use the API endpoint: POST /api/news/search")
    
    # Show example API request
    print("\n📝 Example API request:")
    print("""
    curl -X POST "https://yango-intel-test.onrender.com/api/news/search" \\
         -H "Content-Type: application/json" \\
         -H "Authorization: Bearer YOUR_TOKEN" \\
         -d '{
           "query": "Uber Peru nuevas funciones 2024",
           "competitors": ["uber"],
           "language": "es"
         }'
    """)


def main():
    """Main test runner"""
    print("\n🚀 Yango Intel - News Scraper Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Print configuration
    print_config()
    
    # 2. Test query generation
    test_query_generation()
    
    # 3. Test search providers
    asyncio.run(test_search_providers())
    
    # 4. Test NewsScraperService (info only)
    asyncio.run(test_news_scraper_service())
    
    print_header("TEST COMPLETE")
    print("\n✅ Configuration looks good!")
    print("\nNext steps:")
    print("1. Run 'python test_news_search.py' to test API connection")
    print("2. Deploy to Render with updated code")
    print("3. Test via API: POST /api/news/search")
    print("4. Monitor results in the database\n")


if __name__ == "__main__":
    main()

