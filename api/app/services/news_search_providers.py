"""
News Search Providers

Multiple search API providers for news monitoring.
Configure the provider based on available API keys.
"""

import json
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import structlog
import httpx

from app.config import settings

logger = structlog.get_logger()


class SearchResult:
    """Unified search result structure"""
    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        source: Optional[str] = None,
        date: Optional[str] = None,
        score: float = 0.5
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.date = date
        self.score = score
        self.unique_id = hashlib.md5(url.lower().rstrip("/").encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            "unique_id": self.unique_id,
            "title": self.title,
            "source_url": self.url,
            "summary": self.snippet,
            "source_name": self.source,
            "published_date": self.date,
            "relevance_score": self.score,
        }


class SearchProvider(ABC):
    """Base class for search providers"""
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Execute search and return results"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        pass


class PerplexityProvider(SearchProvider):
    """
    Perplexity AI - sonar models for web search
    API: https://docs.perplexity.ai/
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'PERPLEXITY_API_KEY', None)
        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar"  # sonar model has web search
    
    @property
    def name(self) -> str:
        return "Perplexity"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        if not self.is_configured:
            logger.warning("Perplexity API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a news research assistant. Search for the latest news and return factual information with sources."
                            },
                            {
                                "role": "user", 
                                "content": f"Search for: {query}\n\nReturn news articles with URLs and dates."
                            }
                        ],
                        "max_tokens": 1500,
                    },
                    timeout=60.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Parse response - Perplexity returns text with citations
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = data.get("citations", [])
                
                results = []
                for i, citation in enumerate(citations[:max_results]):
                    results.append(SearchResult(
                        title=citation.get("title", f"Result {i+1}"),
                        url=citation.get("url", ""),
                        snippet=citation.get("snippet", content[:200] if i == 0 else ""),
                        source=citation.get("source"),
                        date=citation.get("date"),
                        score=1.0 - (i * 0.1)  # Decrease score by position
                    ))
                
                logger.info(f"Perplexity search completed", results_count=len(results))
                return results
                
        except Exception as e:
            logger.error(f"Perplexity search error: {e}")
            return []


class TavilyProvider(SearchProvider):
    """
    Tavily - AI-optimized search API
    API: https://tavily.com/
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'TAVILY_API_KEY', None)
        self.base_url = "https://api.tavily.com"
    
    @property
    def name(self) -> str:
        return "Tavily"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        if not self.is_configured:
            logger.warning("Tavily API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={
                        "Content-Type": "application/json",
                    },
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "include_domains": [],  # Can add Peru domains here
                        "max_results": max_results,
                        "include_raw_content": False,
                    },
                    timeout=60.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source=item.get("domain"),
                        date=item.get("published_date"),
                        score=item.get("score", 0.5)
                    ))
                
                logger.info(f"Tavily search completed", results_count=len(results))
                return results
                
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []


class SerpAPIProvider(SearchProvider):
    """
    SerpAPI - Google Search API
    API: https://serpapi.com/
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'SERPAPI_KEY', None)
        self.base_url = "https://serpapi.com"
    
    @property
    def name(self) -> str:
        return "SerpAPI"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        if not self.is_configured:
            logger.warning("SerpAPI key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search.json",
                    params={
                        "api_key": self.api_key,
                        "q": query,
                        "engine": "google",
                        "gl": "pe",  # Peru
                        "hl": "es",  # Spanish
                        "num": max_results,
                        "tbm": "nws",  # News search
                    },
                    timeout=30.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("news_results", []) or data.get("organic_results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("source", {}).get("name") if isinstance(item.get("source"), dict) else item.get("source"),
                        date=item.get("date"),
                        score=0.8 - (len(results) * 0.05)
                    ))
                
                logger.info(f"SerpAPI search completed", results_count=len(results))
                return results
                
        except Exception as e:
            logger.error(f"SerpAPI search error: {e}")
            return []


class GeminiSearchProvider(SearchProvider):
    """
    Google Gemini with grounding (web search capability)
    Uses existing GOOGLE_API_KEY
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.model = "gemini-2.0-flash"
    
    @property
    def name(self) -> str:
        return "Gemini"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        if not self.is_configured:
            logger.warning("Google API key not configured")
            return []
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            
            # Use Gemini with system instruction to search web
            model = genai.GenerativeModel(
                self.model,
                system_instruction="""You are a news research assistant for the Peru market.
                When given a query, search for recent news and return results in JSON format.
                Each result should have: title, url, snippet, source, date.
                Return ONLY valid JSON array, no markdown."""
            )
            
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

Focus on Peru market, Spanish language sources. Return up to {max_results} results."""

            response = await model.generate_content_async(prompt)
            
            # Parse JSON from response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            items = json.loads(text)
            
            results = []
            for item in items[:max_results]:
                if item.get("url"):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("source"),
                        date=item.get("date"),
                        score=0.7
                    ))
            
            logger.info(f"Gemini search completed", results_count=len(results))
            return results
            
        except Exception as e:
            logger.error(f"Gemini search error: {e}")
            return []


class ParallelAIProvider(SearchProvider):
    """
    Parallel AI - High-accuracy web search for AI
    API: https://docs.parallel.ai/search/search-quickstart
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'PARALLEL_API_KEY', None)
        self.base_url = getattr(settings, 'PARALLEL_BASE_URL', 'https://api.parallel.ai/v1beta')
        self.beta_header = getattr(settings, 'PARALLEL_BETA_HEADER', 'search-extract-2025-10-10')
    
    @property
    def name(self) -> str:
        return "Parallel AI"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        if not self.is_configured:
            logger.warning("Parallel AI API key not configured")
            return []
        
        try:
            # Generate search queries from objective
            search_queries = self._generate_search_queries(query)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "parallel-beta": self.beta_header,
                    },
                    json={
                        "objective": query,
                        "search_queries": search_queries,
                        "max_results": max_results,
                        "excerpts": {
                            "max_chars_per_result": 5000
                        }
                    },
                    timeout=60.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    # Combine excerpts into summary
                    excerpts = item.get("excerpts", [])
                    summary = excerpts[0][:500] if excerpts else ""
                    
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=summary,
                        source=self._extract_domain(item.get("url", "")),
                        date=item.get("publish_date"),
                        score=0.9 - (len(results) * 0.05)  # High confidence for Parallel
                    ))
                
                logger.info(f"Parallel AI search completed", results_count=len(results))
                return results
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Parallel AI API error: {e.response.status_code} - {e.response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"Parallel AI search error: {e}")
            return []
    
    def _generate_search_queries(self, objective: str) -> List[str]:
        """Generate multiple search queries from a single objective"""
        # Create variations of the search query
        queries = [objective]
        
        # Add variations if it contains competitor names
        keywords = ["uber", "indrive", "didi", "cabify", "yango", "rappi", "bolt"]
        for kw in keywords:
            if kw.lower() in objective.lower():
                queries.append(f"{kw} Peru últimas noticias")
                break
        
        return queries[:3]  # Max 3 queries
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return ""


class MultiSearchProvider:
    """
    Multi-provider search - tries multiple providers in order
    """
    
    def __init__(self):
        # Initialize all providers - Parallel AI first as primary
        self.providers: List[SearchProvider] = [
            ParallelAIProvider(),  # Primary - highest accuracy
            TavilyProvider(),
            PerplexityProvider(),
            SerpAPIProvider(),
            GeminiSearchProvider(),  # Fallback
        ]
    
    def get_available_providers(self) -> List[SearchProvider]:
        """Get list of configured providers"""
        return [p for p in self.providers if p.is_configured]
    
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        preferred_provider: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search using available providers.
        
        Args:
            query: Search query
            max_results: Max results to return
            preferred_provider: Optional provider name to use first
        
        Returns:
            List of search results
        """
        available = self.get_available_providers()
        
        if not available:
            logger.error("No search providers configured")
            return []
        
        # Reorder if preferred provider specified
        if preferred_provider:
            available = sorted(
                available, 
                key=lambda p: 0 if p.name.lower() == preferred_provider.lower() else 1
            )
        
        # Try each provider until one succeeds
        for provider in available:
            logger.info(f"Trying search provider: {provider.name}")
            results = await provider.search(query, max_results)
            if results:
                logger.info(f"Search successful with {provider.name}", count=len(results))
                return results
        
        logger.warning("All search providers failed")
        return []
    
    def get_status(self) -> dict:
        """Get status of all providers"""
        return {
            "providers": [
                {
                    "name": p.name,
                    "configured": p.is_configured
                }
                for p in self.providers
            ],
            "available_count": len(self.get_available_providers())
        }


# Convenience function
def get_search_provider() -> MultiSearchProvider:
    """Get configured search provider"""
    return MultiSearchProvider()

