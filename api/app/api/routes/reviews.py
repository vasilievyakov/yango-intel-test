from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import Review, Competitor
from app.models.release import Platform
from app.models.review import Sentiment, UserRole

router = APIRouter()


@router.get("")
async def get_reviews(
    competitor_id: Optional[UUID] = None,
    platform: Optional[str] = Query(None, regex="^(ios|android)$"),
    role: Optional[str] = Query(None, regex="^(driver|rider)$"),
    sentiment: Optional[str] = Query(None, regex="^(positive|neutral|negative)$"),
    category: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get reviews with filters and pagination"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(Review).options(joinedload(Review.competitor))
    count_query = select(func.count(Review.id))
    
    # Apply filters
    filters = [Review.collected_at >= since]
    
    if competitor_id:
        filters.append(Review.competitor_id == competitor_id)
    
    if platform:
        filters.append(Review.platform == Platform(platform))
    
    if role:
        filters.append(Review.role == UserRole(role))
    
    if sentiment:
        filters.append(Review.sentiment == Sentiment(sentiment))
    
    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)
    
    # Get total count
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.order_by(Review.review_date.desc().nullslast()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().unique().all()
    
    return {
        "reviews": [
            {
                "id": str(r.id),
                "external_id": r.external_id,
                "competitor": {
                    "id": str(r.competitor.id),
                    "name": r.competitor.name,
                    "slug": r.competitor.slug,
                    "logo_url": r.competitor.logo_url,
                },
                "platform": r.platform.value,
                "author": r.author,
                "rating": r.rating,
                "text": r.text,
                "review_date": r.review_date.isoformat() if r.review_date else None,
                "app_version": r.app_version,
                "language": r.language,
                "role": r.role.value,
                "sentiment": r.sentiment.value if r.sentiment else None,
                "collected_at": r.collected_at.isoformat(),
            }
            for r in reviews
        ],
        "total": total or 0,
        "page": page,
        "pages": (total or 0) // limit + (1 if (total or 0) % limit else 0),
    }


@router.get("/stats")
async def get_review_stats(
    competitor_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get review statistics"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Base filter
    base_filter = [Review.collected_at >= since]
    if competitor_id:
        base_filter.append(Review.competitor_id == competitor_id)
    
    # Total reviews
    total = await db.scalar(
        select(func.count(Review.id)).where(*base_filter)
    )
    
    # By sentiment
    sentiment_stats = {}
    for s in Sentiment:
        count = await db.scalar(
            select(func.count(Review.id)).where(*base_filter, Review.sentiment == s)
        )
        sentiment_stats[s.value] = count or 0
    
    # By competitor
    result = await db.execute(
        select(
            Competitor.name,
            Competitor.id,
            func.count(Review.id).label("total"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .join(Review.competitor)
        .where(Review.collected_at >= since)
        .group_by(Competitor.id, Competitor.name)
    )
    by_competitor = []
    for row in result:
        # Get sentiment breakdown for this competitor
        comp_sentiments = {}
        for s in Sentiment:
            count = await db.scalar(
                select(func.count(Review.id)).where(
                    Review.collected_at >= since,
                    Review.competitor_id == row.id,
                    Review.sentiment == s,
                )
            )
            comp_sentiments[s.value] = count or 0
        
        by_competitor.append({
            "competitor": row.name,
            "competitor_id": str(row.id),
            "total": row.total,
            "positive": comp_sentiments.get("positive", 0),
            "neutral": comp_sentiments.get("neutral", 0),
            "negative": comp_sentiments.get("negative", 0),
            "avg_rating": round(float(row.avg_rating), 2) if row.avg_rating else None,
        })
    
    return {
        "total": total or 0,
        "by_sentiment": sentiment_stats,
        "by_competitor": by_competitor,
        "trending_categories": [],  # TODO: Implement category trending
    }


@router.get("/trends")
async def get_review_trends(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get review trends for the period"""
    
    # Current period
    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    
    # Previous period for comparison
    prev_start = current_start - timedelta(days=days)
    prev_end = current_start
    
    # Get competitors
    competitors_result = await db.execute(
        select(Competitor).where(Competitor.is_active == True)
    )
    competitors = competitors_result.scalars().all()
    
    trends = []
    for comp in competitors:
        # Current period negative reviews
        current_negative = await db.scalar(
            select(func.count(Review.id)).where(
                Review.competitor_id == comp.id,
                Review.collected_at >= current_start,
                Review.sentiment == Sentiment.NEGATIVE,
            )
        )
        
        # Previous period negative reviews
        prev_negative = await db.scalar(
            select(func.count(Review.id)).where(
                Review.competitor_id == comp.id,
                Review.collected_at >= prev_start,
                Review.collected_at < prev_end,
                Review.sentiment == Sentiment.NEGATIVE,
            )
        )
        
        # Calculate change
        if prev_negative and prev_negative > 0:
            change = ((current_negative or 0) - prev_negative) / prev_negative * 100
        else:
            change = 0
        
        trends.append({
            "competitor": comp.name,
            "sentiment_change": round(change, 1),
            "top_categories": [],  # TODO: Implement
        })
    
    return {"trends": trends}

