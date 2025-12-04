from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import NewsItem
from app.services.news_scraper import NewsScraperService

router = APIRouter()


class SearchNewsRequest(BaseModel):
    """Request to search for news on a specific topic"""
    query: str  # e.g., "InDriver Peru pricing changes", "Uber safety features Lima"
    competitors: Optional[List[str]] = None  # Filter to specific competitors
    language: str = "es"


@router.post("/search")
async def search_news(
    request: SearchNewsRequest,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """
    Search for news on a specific topic using AI.
    
    This uses Perplexity/Tavily to find relevant news articles
    about the ride-hailing market in Peru.
    """
    
    scraper = NewsScraperService(db)
    
    try:
        results = await scraper.search(
            query=request.query,
            competitors=request.competitors,
            language=request.language,
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"News search failed: {str(e)}",
        )


@router.get("")
async def get_news_items(
    query: Optional[str] = None,
    competitor: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    relevant_only: bool = Query(True),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get previously scraped news items"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    filters = [NewsItem.collected_at >= since]
    
    if query:
        filters.append(NewsItem.search_query.ilike(f"%{query}%"))
    
    if competitor:
        filters.append(NewsItem.competitors_mentioned.contains([competitor]))
    
    if relevant_only:
        filters.append(NewsItem.is_relevant == True)
    
    # Count
    count_query = select(func.count(NewsItem.id)).where(*filters)
    total = await db.scalar(count_query)
    
    # Fetch
    offset = (page - 1) * limit
    result = await db.execute(
        select(NewsItem)
        .where(*filters)
        .order_by(NewsItem.published_date.desc().nullslast())
        .offset(offset)
        .limit(limit)
    )
    items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(item.id),
                "title": item.title,
                "summary": item.summary,
                "source_url": item.source_url,
                "source_name": item.source_name,
                "published_date": item.published_date.isoformat() if item.published_date else None,
                "competitors_mentioned": item.competitors_mentioned,
                "topics": item.topics,
                "sentiment": item.sentiment,
                "relevance_score": item.relevance_score,
                "search_query": item.search_query,
                "collected_at": item.collected_at.isoformat(),
            }
            for item in items
        ],
        "total": total or 0,
        "page": page,
        "pages": (total or 0) // limit + (1 if (total or 0) % limit else 0),
    }


@router.delete("/{item_id}")
async def mark_news_irrelevant(
    item_id: UUID,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Mark a news item as irrelevant (soft delete)"""
    
    result = await db.execute(
        select(NewsItem).where(NewsItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
    
    item.is_relevant = False
    await db.commit()
    
    return {"status": "ok", "id": str(item_id)}


class SuggestedTopics(BaseModel):
    """Pre-defined topics for news monitoring"""
    topics: List[str] = [
        "InDriver Peru nuevas tarifas precios",
        "Uber Peru seguridad funciones",
        "Didi Peru expansión mercado",
        "Cabify Peru promociones descuentos",
        "regulación taxi aplicaciones Peru",
        "huelga conductores aplicaciones Lima",
        "nuevas funciones apps transporte Peru",
        "competencia ride-hailing Peru mercado",
    ]


@router.get("/suggested-topics")
async def get_suggested_topics(
    user: dict = Depends(verify_clerk_token),
):
    """Get suggested search topics for news monitoring"""
    return SuggestedTopics()

