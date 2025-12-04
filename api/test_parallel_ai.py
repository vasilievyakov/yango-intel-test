#!/usr/bin/env python3
"""
Parallel AI Search Test

Tests the integration with Parallel AI Search API.
API Docs: https://docs.parallel.ai/search/search-quickstart

Run: python test_parallel_ai.py
"""

import asyncio
import os
import json
from datetime import datetime
from urllib.parse import urlparse

# Load env from .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import httpx

# Get API key from env
PARALLEL_API_KEY = os.environ.get("PARALLEL_API_KEY")
PARALLEL_BASE_URL = "https://api.parallel.ai/v1beta"
PARALLEL_BETA_HEADER = "search-extract-2025-10-10"


def print_header(text: str):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except:
        return url[:30] if url else ""


async def test_parallel_search():
    """Test Parallel AI Search API"""
    print_header("PARALLEL AI SEARCH TEST")
    
    if not PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not set in environment")
        print("\n   Set it with:")
        print('   $env:PARALLEL_API_KEY="your-key-here"')
        return False
    
    print(f"✅ API Key: {PARALLEL_API_KEY[:10]}...{PARALLEL_API_KEY[-4:]}")
    print(f"📡 Endpoint: {PARALLEL_BASE_URL}/search")
    print(f"🏷️  Beta Header: {PARALLEL_BETA_HEADER}")
    
    # Test query for Peru ride-hailing market
    objective = "Últimas noticias sobre Uber, inDrive y DiDi en Perú diciembre 2024. Promociones, nuevas funciones, regulación."
    
    search_queries = [
        "Uber Perú noticias diciembre 2024",
        "inDrive Perú promociones 2024",
        "DiDi Perú taxi app noticias"
    ]
    
    print(f"\n🔍 Objective: {objective[:80]}...")
    print(f"🔍 Search queries: {len(search_queries)}")
    
    try:
        async with httpx.AsyncClient() as client:
            print("\n📡 Sending request to Parallel AI...")
            
            response = await client.post(
                f"{PARALLEL_BASE_URL}/search",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": PARALLEL_API_KEY,
                    "parallel-beta": PARALLEL_BETA_HEADER,
                },
                json={
                    "objective": objective,
                    "search_queries": search_queries,
                    "max_results": 10,
                    "excerpts": {
                        "max_chars_per_result": 3000
                    }
                },
                timeout=60.0,
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Show response structure
                print(f"\n✅ Success!")
                print(f"   Search ID: {data.get('search_id', 'N/A')}")
                print(f"   Results count: {len(data.get('results', []))}")
                
                # Show usage
                usage = data.get("usage", [])
                if usage:
                    print(f"   Usage: {usage}")
                
                # Show warnings
                warnings = data.get("warnings")
                if warnings:
                    print(f"   ⚠️ Warnings: {warnings}")
                
                # Display results
                results = data.get("results", [])
                if results:
                    print(f"\n📰 Search Results ({len(results)} items):")
                    print("-" * 60)
                    
                    for i, item in enumerate(results[:5], 1):
                        title = item.get("title", "No title")[:60]
                        url = item.get("url", "")
                        domain = extract_domain(url)
                        pub_date = item.get("publish_date", "N/A")
                        excerpts = item.get("excerpts", [])
                        excerpt_preview = excerpts[0][:150] if excerpts else "No excerpt"
                        
                        print(f"\n   {i}. {title}")
                        print(f"      🌐 {domain}")
                        print(f"      📅 {pub_date}")
                        print(f"      📝 {excerpt_preview}...")
                    
                    if len(results) > 5:
                        print(f"\n   ... and {len(results) - 5} more results")
                else:
                    print("\n   ⚠️ No results found")
                
                return True
                
            elif response.status_code == 401:
                print(f"\n❌ Authentication Error (401)")
                print(f"   Response: {response.text[:300]}")
                print("\n   Check your API key is valid at:")
                print("   https://platform.parallel.ai")
                return False
                
            elif response.status_code == 429:
                print(f"\n❌ Rate Limited (429)")
                print(f"   Wait and try again later")
                return False
                
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except httpx.TimeoutException:
        print("\n❌ Request timed out (60s)")
        print("   Parallel AI searches can take time for complex queries")
        return False
    except httpx.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_search():
    """Quick test with simple query"""
    print_header("SIMPLE SEARCH TEST")
    
    if not PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not set")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            print("📡 Testing with simple query...")
            
            response = await client.post(
                f"{PARALLEL_BASE_URL}/search",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": PARALLEL_API_KEY,
                    "parallel-beta": PARALLEL_BETA_HEADER,
                },
                json={
                    "objective": "What is the capital of Peru?",
                    "search_queries": ["capital of Peru"],
                    "max_results": 3,
                    "excerpts": {
                        "max_chars_per_result": 1000
                    }
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                print(f"✅ Simple search works! Got {len(results)} results")
                if results:
                    print(f"   First result: {results[0].get('title', 'N/A')[:50]}")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n🚀 Parallel AI Search Test for Yango Intel")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    simple_ok = asyncio.run(test_simple_search())
    
    if simple_ok:
        market_ok = asyncio.run(test_parallel_search())
    else:
        print("\n⚠️ Skipping market search test (simple search failed)")
        market_ok = False
    
    print_header("TEST SUMMARY")
    
    print(f"\n   Simple Search: {'✅ PASS' if simple_ok else '❌ FAIL'}")
    print(f"   Market Search: {'✅ PASS' if market_ok else '❌ FAIL'}")
    
    if simple_ok and market_ok:
        print("\n🎉 Parallel AI integration is working!")
        print("\n   Next steps:")
        print("   1. Deploy updated code to Render")
        print("   2. Add PARALLEL_API_KEY to Render environment")
        print("   3. Test via API: POST /api/news/search")
    else:
        print("\n💡 Troubleshooting:")
        print("   1. Check API key at: https://platform.parallel.ai")
        print("   2. Verify account has API access")
        print("   3. Check rate limits and billing")


if __name__ == "__main__":
    main()

