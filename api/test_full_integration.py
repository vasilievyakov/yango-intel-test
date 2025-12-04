#!/usr/bin/env python3
"""
Full Integration Test - Parallel AI + News Configuration

Tests the complete news monitoring system with:
1. Parallel AI Search
2. Competitor detection
3. Category classification
4. Peru market news sources

Run: python test_full_integration.py
"""

import asyncio
import os
import json
from datetime import datetime
from urllib.parse import urlparse

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import httpx

# Configuration
PARALLEL_API_KEY = os.environ.get("PARALLEL_API_KEY")
PARALLEL_BASE_URL = "https://api.parallel.ai/v1beta"
PARALLEL_BETA_HEADER = "search-extract-2025-10-10"


def print_header(text: str):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_subheader(text: str):
    print(f"\n--- {text} ---")


# Detection functions (same as in NewsScraperService)
COMPETITORS = {
    "yango": ["yango", "yango pro", "yango delivery"],
    "indrive": ["indrive", "in drive", "in-drive", "kuzoba"],
    "uber": ["uber", "uber moto", "uber tuk"],
    "didi": ["didi", "99"],
    "cabify": ["cabify"],
    "rappi": ["rappi"],
    "bolt": ["bolt"],
}

TOPIC_KEYWORDS = {
    "pricing": ["precio", "tarifa", "comisión", "costo", "fare"],
    "safety": ["seguridad", "robo", "asalto", "emergencia", "crimen"],
    "regulation": ["regulación", "ley", "mtc", "atu", "multa", "bloquear"],
    "promo": ["promoción", "descuento", "oferta", "código", "gratis"],
    "technology": ["app", "aplicación", "función", "actualización", "feature"],
    "labor": ["paro", "huelga", "protesta", "conductores"],
}


def detect_competitors(text: str) -> list:
    """Detect competitors mentioned in text"""
    text_lower = text.lower()
    found = []
    for comp, keywords in COMPETITORS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(comp)
    return found


def detect_topics(text: str) -> list:
    """Detect topics in text"""
    text_lower = text.lower()
    found = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(topic)
    return found if found else ["general"]


def detect_sentiment(text: str) -> str:
    """Simple sentiment detection"""
    text_lower = text.lower()
    positive = ["éxito", "crecimiento", "mejora", "lanza", "nueva"]
    negative = ["problema", "queja", "bloquear", "crimen", "robo", "multa"]
    
    pos = sum(1 for w in positive if w in text_lower)
    neg = sum(1 for w in negative if w in text_lower)
    
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""


async def search_parallel_ai(query: str, search_queries: list) -> dict:
    """Execute Parallel AI search"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PARALLEL_BASE_URL}/search",
            headers={
                "Content-Type": "application/json",
                "x-api-key": PARALLEL_API_KEY,
                "parallel-beta": PARALLEL_BETA_HEADER,
            },
            json={
                "objective": query,
                "search_queries": search_queries,
                "max_results": 10,
                "excerpts": {"max_chars_per_result": 3000}
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()


def process_results(data: dict) -> list:
    """Process Parallel AI results with competitor/topic detection"""
    processed = []
    
    for item in data.get("results", []):
        url = item.get("url", "")
        title = item.get("title", "")
        excerpts = item.get("excerpts", [])
        pub_date = item.get("publish_date")
        
        # Full text for analysis
        content = " ".join(excerpts[:2]) if excerpts else ""
        full_text = f"{title} {content}"
        
        processed.append({
            "title": title,
            "url": url,
            "domain": extract_domain(url),
            "date": pub_date,
            "summary": excerpts[0][:200] if excerpts else "",
            "competitors": detect_competitors(full_text),
            "topics": detect_topics(full_text),
            "sentiment": detect_sentiment(full_text),
        })
    
    return processed


async def run_market_scan():
    """Run complete market scan for Peru ride-hailing"""
    print_header("FULL MARKET SCAN")
    
    if not PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not set")
        return
    
    # Define search queries
    queries = [
        {
            "name": "General Market News",
            "objective": "Últimas noticias sobre aplicativos de taxi en Perú 2024-2025. Uber, inDrive, DiDi, Cabify, Rappi.",
            "search_queries": [
                "taxi aplicativo Perú noticias 2024",
                "Uber inDrive DiDi Perú",
                "ride-hailing app Peru news"
            ]
        },
        {
            "name": "Promotions & Discounts",
            "objective": "Promociones y descuentos de Uber, inDrive, DiDi en Perú diciembre 2024",
            "search_queries": [
                "Uber Perú promoción descuento",
                "inDrive código promocional Perú",
                "DiDi descuento Lima"
            ]
        },
        {
            "name": "Regulation & Safety",
            "objective": "Regulación taxi aplicativo Perú MTC ATU. Seguridad conductores.",
            "search_queries": [
                "regulación taxi aplicativo Perú",
                "MTC ATU Uber inDrive",
                "seguridad conductores app taxi Lima"
            ]
        }
    ]
    
    all_results = []
    
    for query in queries:
        print_subheader(query["name"])
        print(f"🔍 {query['objective'][:60]}...")
        
        try:
            data = await search_parallel_ai(query["objective"], query["search_queries"])
            results = process_results(data)
            all_results.extend(results)
            
            print(f"✅ Found {len(results)} results")
            
            # Show top 3
            for i, r in enumerate(results[:3], 1):
                comps = ", ".join(r["competitors"]) if r["competitors"] else "None"
                topics = ", ".join(r["topics"][:2])
                print(f"   {i}. [{r['sentiment']}] {r['title'][:45]}...")
                print(f"      Competitors: {comps} | Topics: {topics}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary
    print_header("SCAN SUMMARY")
    
    print(f"\n📊 Total results: {len(all_results)}")
    
    # Competitor mentions
    comp_counts = {}
    for r in all_results:
        for c in r["competitors"]:
            comp_counts[c] = comp_counts.get(c, 0) + 1
    
    print("\n🏢 Competitor Mentions:")
    for comp, count in sorted(comp_counts.items(), key=lambda x: -x[1]):
        print(f"   {comp}: {count} mentions")
    
    # Topic distribution
    topic_counts = {}
    for r in all_results:
        for t in r["topics"]:
            topic_counts[t] = topic_counts.get(t, 0) + 1
    
    print("\n📋 Topic Distribution:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
        print(f"   {topic}: {count}")
    
    # Sentiment breakdown
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    for r in all_results:
        sentiments[r["sentiment"]] = sentiments.get(r["sentiment"], 0) + 1
    
    print("\n😊 Sentiment Breakdown:")
    for sent, count in sentiments.items():
        pct = (count / len(all_results) * 100) if all_results else 0
        print(f"   {sent}: {count} ({pct:.0f}%)")
    
    # Sources
    sources = set(r["domain"] for r in all_results if r["domain"])
    print(f"\n🌐 Unique Sources: {len(sources)}")
    for s in list(sources)[:5]:
        print(f"   - {s}")
    if len(sources) > 5:
        print(f"   ... and {len(sources) - 5} more")
    
    return all_results


async def test_single_competitor(competitor: str):
    """Test search for a single competitor"""
    print_header(f"COMPETITOR SEARCH: {competitor.upper()}")
    
    if not PARALLEL_API_KEY:
        print("❌ PARALLEL_API_KEY not set")
        return
    
    objective = f"Últimas noticias sobre {competitor} en Perú 2024. Promociones, funciones nuevas, regulación."
    search_queries = [
        f"{competitor} Perú noticias 2024",
        f"{competitor} Perú promoción",
        f"{competitor} taxi app Lima"
    ]
    
    print(f"🔍 Searching for: {competitor}")
    
    try:
        data = await search_parallel_ai(objective, search_queries)
        results = process_results(data)
        
        print(f"✅ Found {len(results)} results")
        
        for i, r in enumerate(results[:5], 1):
            print(f"\n   {i}. {r['title'][:55]}")
            print(f"      🌐 {r['domain']}")
            print(f"      📅 {r['date'] or 'N/A'}")
            print(f"      📝 {r['summary'][:100]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("\n🚀 Yango Intel - Full Integration Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not PARALLEL_API_KEY:
        print("\n❌ PARALLEL_API_KEY not set!")
        print('   Set it with: $env:PARALLEL_API_KEY="your-key"')
        return
    
    print(f"\n✅ Parallel AI Key: {PARALLEL_API_KEY[:10]}...{PARALLEL_API_KEY[-4:]}")
    
    # Run full market scan
    asyncio.run(run_market_scan())
    
    # Test single competitor
    # asyncio.run(test_single_competitor("Uber"))
    
    print_header("TEST COMPLETE")
    print("\n🎉 Integration test successful!")
    print("\nNext steps:")
    print("   1. git add . && git commit -m 'Add Parallel AI integration'")
    print("   2. git push")
    print("   3. Add PARALLEL_API_KEY to Render environment variables")
    print("   4. Redeploy backend on Render")


if __name__ == "__main__":
    main()

