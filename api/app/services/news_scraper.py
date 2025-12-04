"""
News Scraper Service using Parallel AI

This service searches for news about the ride-hailing market in Peru
based on user-provided topics/queries using Parallel AI platform.

Enhanced with:
- Peru market news sources configuration
- Competitor detection
- Category classification
- Deduplication via unique_id (MD5 hash of URL)
"""
import json
import hashlib
from typing import Optional, List
from datetime import datetime, date
import structlog
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import NewsItem
from app.models.news_item import NewsSource

# Import news sources configuration
try:
    from app.news_config.news_sources import (
        PERU_NEWS_SOURCES,
        COMPETITORS,
        NEWS_CATEGORIES,
        PARALLEL_SEARCH_PROMPT,
        build_site_filter,
        generate_search_queries,
        get_all_competitor_keywords,
    )
except ImportError:
    # Fallback if config not created yet
    PERU_NEWS_SOURCES = []
    COMPETITORS = []
    NEWS_CATEGORIES = []
    PARALLEL_SEARCH_PROMPT = "{query}"
    def build_site_filter(sources): return ""
    def generate_search_queries(): return []
    def get_all_competitor_keywords(): return []

logger = structlog.get_logger()


class NewsScraperService:
    """
    Service for searching news using Parallel AI.
    
    Parallel AI is a search platform that provides structured,
    relevant results with sources and reasoning.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.PARALLEL_API_KEY
        self.base_url = settings.PARALLEL_BASE_URL
        self.engine = getattr(settings, 'PARALLEL_ENGINE', 'search')
    
    async def search(
        self,
        query: str,
        competitors: Optional[List[str]] = None,
        language: str = "es",
        use_peru_sources: bool = True,
    ) -> List[dict]:
        """
        Search for news on a specific topic using Parallel AI.
        
        Args:
            query: Search query (e.g., "InDriver Peru pricing changes")
            competitors: Optional list of competitors to filter
            language: Language for results (default: Spanish)
            use_peru_sources: Whether to prioritize Peru news sources
        
        Returns:
            List of news items found
        """
        
        logger.info("Searching news with Parallel AI", query=query, competitors=competitors)
        
        # Enhance query with context
        enhanced_query = self._enhance_query(query, competitors, language, use_peru_sources)
        
        # Search using Parallel AI
        if self.api_key:
            results = await self._search_parallel(enhanced_query)
        else:
            logger.warning("Parallel AI API key not configured, returning empty results")
            return []
        
        # Save results to database (with deduplication)
        saved_items = []
        for item in results:
            news_item = await self._save_news_item(query, item)
            if news_item:
                saved_items.append({
                    "id": str(news_item.id),
                    "unique_id": self._generate_unique_id(item.get("source_url")),
                    "title": news_item.title,
                    "summary": news_item.summary,
                    "source_url": news_item.source_url,
                    "source_name": news_item.source_name,
                    "published_date": news_item.published_date.isoformat() if news_item.published_date else None,
                    "competitors_mentioned": news_item.competitors_mentioned,
                    "topics": news_item.topics,
                    "sentiment": news_item.sentiment,
                    "relevance_score": news_item.relevance_score,
                })
        
        return saved_items
    
    async def search_competitor_news(
        self,
        competitor_slug: str,
        category: Optional[str] = None,
    ) -> List[dict]:
        """
        Search news for a specific competitor.
        
        Args:
            competitor_slug: Slug of competitor (e.g., 'uber', 'indrive')
            category: Optional category filter
        
        Returns:
            List of news items
        """
        # Find competitor
        competitor = None
        for comp in COMPETITORS:
            if comp.slug == competitor_slug:
                competitor = comp
                break
        
        if not competitor:
            logger.warning(f"Competitor not found: {competitor_slug}")
            return []
        
        # Build query
        year = datetime.now().year
        query = f"{competitor.name} Peru noticias {year}"
        
        if category:
            # Add category keywords
            for cat in NEWS_CATEGORIES:
                if cat.slug == category:
                    query += " " + " ".join(cat.keywords_es[:3])
                    break
        
        return await self.search(
            query=query,
            competitors=[competitor.name],
            use_peru_sources=True
        )
    
    async def run_market_scan(self) -> dict:
        """
        Run a full market scan across all competitors and categories.
        
        Returns:
            Summary of scan results
        """
        logger.info("Starting full market scan")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_items": 0,
            "by_competitor": {},
            "by_category": {},
            "items": []
        }
        
        # Generate queries
        queries = generate_search_queries()
        
        for query in queries:
            try:
                items = await self.search(query, use_peru_sources=True)
                results["items"].extend(items)
                results["total_items"] += len(items)
                
                # Categorize results
                for item in items:
                    for comp in item.get("competitors_mentioned", []):
                        results["by_competitor"][comp] = results["by_competitor"].get(comp, 0) + 1
                    for topic in item.get("topics", []):
                        results["by_category"][topic] = results["by_category"].get(topic, 0) + 1
                        
            except Exception as e:
                logger.error(f"Error in market scan for query '{query}': {e}")
        
        logger.info(f"Market scan completed: {results['total_items']} items found")
        return results
    
    def _generate_unique_id(self, url: str) -> str:
        """Generate MD5 hash of URL for deduplication"""
        if not url:
            return hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()
        # Normalize URL (remove trailing slashes, lowercase)
        normalized = url.lower().rstrip("/")
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def _check_duplicate(self, source_url: str) -> bool:
        """Check if news item already exists by URL"""
        if not source_url:
            return False
        
        result = await self.db.execute(
            select(NewsItem).where(NewsItem.source_url == source_url)
        )
        return result.scalar_one_or_none() is not None
    
    def _enhance_query(
        self, 
        query: str, 
        competitors: Optional[List[str]], 
        language: str,
        use_peru_sources: bool = True
    ) -> str:
        """Enhance query with context for better results"""
        parts = [query]
        
        # Add competitor context if specified
        if competitors:
            parts.append(f"Конкуренты: {', '.join(competitors)}")
        
        # Add regional context
        parts.append("ride-hailing такси приложение Peru Lima Перу Лима")
        
        # Add time context
        year = datetime.now().year
        parts.append(f"últimas noticias {year}")
        
        # Add site filter for Peru sources
        if use_peru_sources and PERU_NEWS_SOURCES:
            site_filter = build_site_filter(PERU_NEWS_SOURCES[:5])
            parts.append(site_filter)
        
        return " ".join(parts)
    
    async def _search_parallel(self, query: str) -> List[dict]:
        """
        Search using Parallel AI v1beta Search API.
        
        API Docs: https://docs.parallel.ai/search/search-quickstart
        """
        
        try:
            # Generate search queries from the objective
            search_queries = self._generate_search_queries(query)
            
            # Build the objective with context
            objective = f"{query}. Focus on Peru market, ride-hailing apps, taxi services."
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "parallel-beta": getattr(settings, 'PARALLEL_BETA_HEADER', 'search-extract-2025-10-10'),
                    },
                    json={
                        "objective": objective,
                        "search_queries": search_queries,
                        "max_results": 15,  # Increased for more coverage
                        "excerpts": {
                            "max_chars_per_result": 3000
                        }
                    },
                    timeout=60.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Parse Parallel AI response
                results = self._parse_parallel_response(data)
                
                logger.info("Parallel AI search completed", 
                           results_count=len(results),
                           search_id=data.get("search_id"))
                return results
                
        except httpx.HTTPStatusError as e:
            logger.error("Parallel AI API error", 
                        status_code=e.response.status_code,
                        response=e.response.text[:200])
            return []
        except httpx.HTTPError as e:
            logger.error("Parallel AI HTTP error", error=str(e))
            return []
        except Exception as e:
            logger.error("News search failed", error=str(e))
            return []
    
    def _generate_search_queries(self, objective: str) -> List[str]:
        """Generate multiple search queries from objective for better coverage"""
        queries = []
        
        # Base query
        queries.append(objective[:100])
        
        # Add Peru context
        queries.append(f"Peru taxi aplicativo {datetime.now().year}")
        
        # Check for competitor mentions and add specific queries
        for comp in COMPETITORS:
            for kw in comp.keywords:
                if kw.lower() in objective.lower():
                    queries.append(f"{comp.name} Perú noticias {datetime.now().year}")
                    break
        
        return queries[:5]  # Max 5 queries
    
    def _parse_parallel_response(self, data: dict) -> List[dict]:
        """
        Parse Parallel AI v1beta Search response into structured news items.
        
        Response format:
        {
            "search_id": "...",
            "results": [
                {
                    "url": "https://...",
                    "title": "Article title",
                    "publish_date": "YYYY-MM-DD" or null,
                    "excerpts": ["excerpt text..."]
                }
            ],
            "usage": [{"name": "sku_search", "count": 1}]
        }
        """
        
        results = []
        items = data.get("results", [])
        
        for item in items:
            url = item.get("url", "")
            title = item.get("title", "Untitled")
            pub_date = item.get("publish_date")
            excerpts = item.get("excerpts", [])
            
            # Combine excerpts for content analysis
            content = " ".join(excerpts[:2]) if excerpts else ""
            full_text = f"{title} {content}"
            
            # Generate unique ID for deduplication
            unique_id = self._generate_unique_id(url)
            
            # Extract domain as source name
            source_name = self._extract_domain(url)
            
            # Detect competitors mentioned
            competitors_mentioned = self._detect_competitors(full_text)
            
            # Detect topics/categories
            topics = self._detect_topics(full_text)
            
            # Detect category
            category = self._detect_category(full_text)
            
            # Basic sentiment detection
            sentiment = self._detect_sentiment(full_text)
            
            # Create summary from first excerpt
            summary = excerpts[0][:500] if excerpts else title
            
            results.append({
                "unique_id": unique_id,
                "title": title,
                "summary": summary,
                "source_url": url,
                "source_name": source_name,
                "published_date": pub_date,
                "competitors_mentioned": competitors_mentioned,
                "topics": topics,
                "category": category,
                "sentiment": sentiment,
                "relevance_score": 0.8,  # High relevance for Parallel AI results
            })
        
        return results
    
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
    
    def _detect_competitors(self, text: str) -> List[str]:
        """Detect which competitors are mentioned in the text"""
        text_lower = text.lower()
        detected = []
        
        for competitor in COMPETITORS:
            # Check all aliases
            for alias in competitor.aliases:
                if alias.lower() in text_lower:
                    detected.append(competitor.slug)
                    break
        
        # Fallback to original keywords if COMPETITORS not loaded
        if not COMPETITORS:
            competitor_keywords = {
                "indriver": ["indriver", "in driver", "indrive"],
                "uber": ["uber"],
                "didi": ["didi", "99"],
                "cabify": ["cabify"],
                "yango": ["yango"],
                "beat": ["beat"],
                "rappi": ["rappi"],
                "bolt": ["bolt"],
            }
            
            for comp, keywords in competitor_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    detected.append(comp)
        
        return list(set(detected))
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics mentioned in the text"""
        text_lower = text.lower()
        topics = []
        
        topic_keywords = {
            "pricing": ["precio", "tarifa", "comisión", "costo", "price", "fare"],
            "safety": ["seguridad", "safety", "sos", "emergencia", "robo", "asalto"],
            "regulation": ["regulación", "ley", "gobierno", "municipal", "regulation", "MTC", "ATU"],
            "expansion": ["expansión", "nuevo mercado", "lanzamiento", "expansion"],
            "drivers": ["conductor", "driver", "chofer", "ganancias"],
            "promo": ["promoción", "descuento", "oferta", "promo", "discount", "cupón"],
            "technology": ["app", "aplicación", "tecnología", "actualización", "feature", "función"],
            "labor": ["paro", "huelga", "protesta", "strike"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]
    
    def _detect_category(self, text: str) -> str:
        """Detect news category based on content"""
        text_lower = text.lower()
        
        # Priority order for categories
        category_patterns = [
            ("Product Feature", ["nueva función", "actualización", "nueva versión", "lanzamiento", "feature"]),
            ("Promo & Incentives", ["promoción", "descuento", "cupón", "bono", "sorteo", "gratis"]),
            ("Commercial Terms", ["comisión", "tarifa", "precio", "ganancias", "pago"]),
            ("Safety", ["robo", "asalto", "accidente", "seguridad", "crimen"]),
            ("Regulation", ["regulación", "ley", "MTC", "ATU", "multa", "permiso"]),
            ("Labor", ["paro", "huelga", "protesta", "manifestación"]),
        ]
        
        for category, keywords in category_patterns:
            if any(kw in text_lower for kw in keywords):
                return category
        
        return "General"
    
    def _detect_sentiment(self, text: str) -> str:
        """Basic sentiment detection"""
        text_lower = text.lower()
        
        positive_words = ["éxito", "crecimiento", "mejora", "positivo", "success", "growth", "lanza", "nueva"]
        negative_words = ["problema", "queja", "huelga", "protesta", "issue", "problem", "strike", "robo", "asalto"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"
    
    async def _save_news_item(self, query: str, item: dict) -> Optional[NewsItem]:
        """Save a news item to database with deduplication"""
        
        # Check for duplicate
        if await self._check_duplicate(item.get("source_url")):
            logger.debug("Skipping duplicate news item", url=item.get("source_url"))
            return None
        
        try:
            # Parse date
            pub_date = None
            if item.get("published_date"):
                try:
                    if isinstance(item["published_date"], str):
                        pub_date = date.fromisoformat(item["published_date"][:10])
                    elif isinstance(item["published_date"], date):
                        pub_date = item["published_date"]
                except ValueError:
                    pass
            
            news_item = NewsItem(
                search_query=query,
                title=item.get("title", "Untitled")[:500],
                summary=item.get("summary"),
                source_url=item.get("source_url"),
                source_name=item.get("source_name"),
                source_type=NewsSource.PARALLEL,
                published_date=pub_date,
                competitors_mentioned=item.get("competitors_mentioned"),
                topics=item.get("topics"),
                sentiment=item.get("sentiment"),
                relevance_score=float(item.get("relevance_score", 0.5)),
                raw_response=item,
                is_processed=True,
                is_relevant=True,
            )
            
            self.db.add(news_item)
            await self.db.commit()
            await self.db.refresh(news_item)
            
            logger.info("Saved news item", title=news_item.title[:50], url=news_item.source_url)
            return news_item
            
        except Exception as e:
            logger.error("Failed to save news item", error=str(e))
            await self.db.rollback()
            return None
