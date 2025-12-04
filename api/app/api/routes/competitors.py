from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api.deps import get_database, verify_clerk_token
from app.models import Competitor

router = APIRouter()


@router.get("")
async def get_competitors(
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get all competitors"""
    
    result = await db.execute(
        select(Competitor).where(Competitor.is_active == True).order_by(Competitor.name)
    )
    competitors = result.scalars().all()
    
    return {
        "competitors": [
            {
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "country": c.country,
                "logo_url": c.logo_url,
                "website_driver": c.website_driver,
                "website_rider": c.website_rider,
                "appstore_id": c.appstore_id,
                "playstore_id": c.playstore_id,
                "is_active": c.is_active,
            }
            for c in competitors
        ]
    }


@router.get("/{competitor_id}")
async def get_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get single competitor by ID"""
    
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return {
        "id": str(competitor.id),
        "name": competitor.name,
        "slug": competitor.slug,
        "country": competitor.country,
        "logo_url": competitor.logo_url,
        "website_driver": competitor.website_driver,
        "website_rider": competitor.website_rider,
        "appstore_id": competitor.appstore_id,
        "playstore_id": competitor.playstore_id,
        "is_active": competitor.is_active,
    }

