"""
News Scraper Service using Parallel AI

This service searches for news about the ride-hailing market in Peru
based on user-provided topics/queries using Parallel AI platform.
"""
import json
from typing import Optional, List
from datetime import datetime, date
import structlog
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import NewsItem
from app.models.news_item import NewsSource

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
        self.engine = settings.PARALLEL_ENGINE
    
    async def search(
        self,
        query: str,
        competitors: Optional[List[str]] = None,
        language: str = "es",
    ) -> List[dict]:
        """
        Search for news on a specific topic using Parallel AI.
        
        Args:
            query: Search query (e.g., "InDriver Peru pricing changes")
            competitors: Optional list of competitors to filter
            language: Language for results (default: Spanish)
        
        Returns:
            List of news items found
        """
        
        logger.info("Searching news with Parallel AI", query=query, competitors=competitors)
        
        # Enhance query with context
        enhanced_query = self._enhance_query(query, competitors, language)
        
        # Search using Parallel AI
        if self.api_key:
            results = await self._search_parallel(enhanced_query)
        else:
            logger.warning("Parallel AI API key not configured, returning empty results")
            return []
        
        # Save results to database
        saved_items = []
        for item in results:
            news_item = await self._save_news_item(query, item)
            if news_item:
                saved_items.append({
                    "id": str(news_item.id),
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
    
    def _enhance_query(
        self, query: str, competitors: Optional[List[str]], language: str
    ) -> str:
        """Enhance query with context for better results"""
        parts = [query]
        
        # Add competitor context if specified
        if competitors:
            parts.append(f"Конкуренты: {', '.join(competitors)}")
        
        # Add regional context
        parts.append("ride-hailing такси приложение Peru Lima Перу Лима")
        
        # Add time context
        parts.append("последние новости 2024 2025")
        
        return " ".join(parts)
    
    async def _search_parallel(self, query: str) -> List[dict]:
        """Search using Parallel AI API"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": query,
                        "engine": self.engine,
                        # Request structured output
                        "output_format": "structured",
                        "max_results": 10,
                    },
                    timeout=60.0,  # Parallel AI may take longer for deep searches
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Parse Parallel AI response
                results = self._parse_parallel_response(data)
                
                logger.info("Parallel AI search completed", results_count=len(results))
                return results
                
        except httpx.HTTPError as e:
            logger.error("Parallel AI API error", error=str(e))
            return []
        except Exception as e:
            logger.error("News search failed", error=str(e))
            return []
    
    def _parse_parallel_response(self, data: dict) -> List[dict]:
        """Parse Parallel AI response into structured news items"""
        
        results = []
        
        # Parallel AI returns structured data with sources
        # Adapt this based on actual API response format
        
        # Check for results in different possible formats
        items = data.get("results", []) or data.get("data", []) or data.get("items", [])
        
        # If response is a single object with content
        if not items and data.get("content"):
            items = [data]
        
        # If response contains answer with sources
        if not items and data.get("answer"):
            # Create item from answer
            items = [{
                "title": data.get("answer", "")[:100],
                "content": data.get("answer"),
                "sources": data.get("sources", []),
            }]
        
        for item in items:
            # Extract sources if available
            sources = item.get("sources", [])
            source_url = sources[0].get("url") if sources else item.get("url")
            source_name = sources[0].get("title") if sources else item.get("source")
            
            # Detect competitors mentioned
            content = str(item.get("content", "")) + str(item.get("title", ""))
            competitors_mentioned = self._detect_competitors(content)
            
            # Detect topics
            topics = self._detect_topics(content)
            
            # Basic sentiment detection
            sentiment = self._detect_sentiment(content)
            
            results.append({
                "title": item.get("title") or item.get("headline") or "Untitled",
                "summary": item.get("summary") or item.get("snippet") or item.get("content", "")[:500],
                "source_url": source_url,
                "source_name": source_name,
                "published_date": item.get("date") or item.get("published_date"),
                "competitors_mentioned": competitors_mentioned,
                "topics": topics,
                "sentiment": sentiment,
                "relevance_score": item.get("relevance_score") or item.get("score") or 0.5,
            })
        
        return results
    
    def _detect_competitors(self, text: str) -> List[str]:
        """Detect which competitors are mentioned in the text"""
        text_lower = text.lower()
        competitors = []
        
        competitor_keywords = {
            "indriver": ["indriver", "in driver", "indrive"],
            "uber": ["uber"],
            "didi": ["didi", "99"],  # 99 is Didi brand in some markets
            "cabify": ["cabify"],
            "yango": ["yango"],
            "beat": ["beat"],
        }
        
        for comp, keywords in competitor_keywords.items():
            if any(kw in text_lower for kw in keywords):
                competitors.append(comp)
        
        return competitors
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics mentioned in the text"""
        text_lower = text.lower()
        topics = []
        
        topic_keywords = {
            "pricing": ["precio", "tarifa", "comisión", "costo", "price", "fare"],
            "safety": ["seguridad", "safety", "sos", "emergencia"],
            "regulation": ["regulación", "ley", "gobierno", "municipal", "regulation"],
            "expansion": ["expansión", "nuevo mercado", "lanzamiento", "expansion"],
            "drivers": ["conductor", "driver", "chofer"],
            "promo": ["promoción", "descuento", "oferta", "promo", "discount"],
            "technology": ["app", "aplicación", "tecnología", "actualización", "feature"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]
    
    def _detect_sentiment(self, text: str) -> str:
        """Basic sentiment detection"""
        text_lower = text.lower()
        
        positive_words = ["éxito", "crecimiento", "mejora", "positivo", "success", "growth"]
        negative_words = ["problema", "queja", "huelga", "protesta", "issue", "problem", "strike"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"
    
    async def _save_news_item(self, query: str, item: dict) -> Optional[NewsItem]:
        """Save a news item to database"""
        
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
            
            return news_item
            
        except Exception as e:
            logger.error("Failed to save news item", error=str(e))
            await self.db.rollback()
            return None
