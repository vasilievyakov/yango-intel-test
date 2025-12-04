from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import Release, Competitor
from app.models.release import Platform

router = APIRouter()


@router.get("")
async def get_releases(
    competitor_id: Optional[UUID] = None,
    platform: Optional[str] = Query(None, regex="^(ios|android)$"),
    category: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get releases with filters and pagination"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(Release).options(joinedload(Release.competitor))
    count_query = select(func.count(Release.id))
    
    # Apply filters
    filters = [Release.collected_at >= since]
    
    if competitor_id:
        filters.append(Release.competitor_id == competitor_id)
    
    if platform:
        filters.append(Release.platform == Platform(platform))
    
    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)
    
    # Get total count
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.order_by(Release.release_date.desc().nullslast()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    releases = result.scalars().unique().all()
    
    return {
        "releases": [
            {
                "id": str(r.id),
                "competitor": {
                    "id": str(r.competitor.id),
                    "name": r.competitor.name,
                    "slug": r.competitor.slug,
                    "logo_url": r.competitor.logo_url,
                },
                "platform": r.platform.value,
                "version": r.version,
                "release_date": r.release_date.isoformat() if r.release_date else None,
                "release_notes": r.release_notes,
                "rating": float(r.rating) if r.rating else None,
                "rating_count": r.rating_count,
                "significance": r.significance.value if r.significance else None,
                "summary_ru": r.summary_ru,
                "collected_at": r.collected_at.isoformat(),
            }
            for r in releases
        ],
        "total": total or 0,
        "page": page,
        "pages": (total or 0) // limit + (1 if (total or 0) % limit else 0),
    }


@router.get("/timeline")
async def get_release_timeline(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get release timeline for visualization"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Release)
        .options(joinedload(Release.competitor))
        .where(Release.release_date >= since.date())
        .order_by(Release.release_date.desc())
    )
    releases = result.scalars().unique().all()
    
    # Group by date
    timeline = {}
    for r in releases:
        date_str = r.release_date.isoformat() if r.release_date else "unknown"
        if date_str not in timeline:
            timeline[date_str] = []
        
        timeline[date_str].append({
            "competitor": r.competitor.name,
            "platform": r.platform.value,
            "version": r.version,
            "significance": r.significance.value if r.significance else None,
        })
    
    return {
        "timeline": [
            {"date": date, "releases": releases}
            for date, releases in sorted(timeline.items(), reverse=True)
        ]
    }

