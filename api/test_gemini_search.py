#!/usr/bin/env python3
"""
Simple Gemini Search Test (no database dependencies)

Tests the Gemini AI search capability for Peru market news.
Run: python test_gemini_search.py
"""

import asyncio
import os
import json
from datetime import datetime

# Load env from .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Get API key from env
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def print_header(text: str):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


async def test_gemini_search():
    """Test Gemini search for Peru market news"""
    print_header("GEMINI SEARCH TEST")
    
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not set in environment")
        return
    
    print(f"✅ API Key configured: {GOOGLE_API_KEY[:10]}...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GOOGLE_API_KEY)
        
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction="""You are a news research assistant for the Peru ride-hailing market.
            When given a query, search for recent news and return results in JSON format.
            Each result should have: title, url, snippet, source, date.
            Return ONLY valid JSON array, no markdown."""
        )
        
        query = "Uber inDrive DiDi Peru noticias diciembre 2024"
        
        print(f"\n🔍 Test query: {query}")
        
        prompt = f"""Search for recent news about: {query}

Return results as a JSON array with this structure:
[
  {{
    "title": "Article title",
    "url": "https://...",
    "snippet": "Brief description",
    "source": "Source name",
    "date": "YYYY-MM-DD"
  }}
]

Focus on Peru market, Spanish language sources. Return up to 5 results."""

        print("📡 Sending request to Gemini...")
        
        response = await model.generate_content_async(prompt)
        
        print(f"\n📊 Response received!")
        
        # Parse response
        text = response.text.strip()
        print(f"\n📝 Raw response preview:\n{text[:500]}...")
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            items = json.loads(text)
            
            print(f"\n✅ Successfully parsed {len(items)} results:")
            
            for i, item in enumerate(items[:5], 1):
                print(f"\n   {i}. {item.get('title', 'N/A')[:60]}")
                print(f"      URL: {item.get('url', 'N/A')[:60]}")
                print(f"      Source: {item.get('source', 'N/A')}")
                print(f"      Date: {item.get('date', 'N/A')}")
                
        except json.JSONDecodeError as e:
            print(f"\n⚠️ Could not parse JSON: {e}")
            print("   Gemini returned non-JSON response (this is expected)")
            print("   The model may not have access to live web search.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_gemini_with_grounding():
    """Test Gemini with Google Search grounding"""
    print_header("GEMINI WITH GROUNDING TEST")
    
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not set")
        return
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Try with grounding tool
        from google.generativeai.types import Tool
        
        # Google Search grounding
        google_search_tool = Tool(
            google_search_retrieval={
                "dynamic_retrieval_config": {
                    "mode": "dynamic",
                    "dynamic_threshold": 0.3,
                }
            }
        )
        
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            tools=[google_search_tool]
        )
        
        query = "Últimas noticias Uber Perú diciembre 2024"
        
        print(f"\n🔍 Query with grounding: {query}")
        print("📡 Sending request...")
        
        response = await model.generate_content_async(query)
        
        print(f"\n📊 Response:")
        print(response.text[:1000])
        
        # Check for grounding metadata
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                print(f"\n📌 Grounding metadata found!")
                print(candidate.grounding_metadata)
                
    except Exception as e:
        print(f"\n⚠️ Grounding test error: {e}")
        print("   This feature may require specific API access.")


def main():
    print("\n🚀 Gemini Search Test for Yango Intel")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    asyncio.run(test_gemini_search())
    asyncio.run(test_gemini_with_grounding())
    
    print_header("TEST COMPLETE")
    
    print("\n💡 Next steps:")
    print("   1. If Gemini search works - great! Deploy to Render")
    print("   2. If not - consider adding Tavily API (free tier)")
    print("      Sign up at: https://tavily.com")
    print("   3. Or use SerpAPI for Google Search results")
    print("      Sign up at: https://serpapi.com\n")


if __name__ == "__main__":
    main()

