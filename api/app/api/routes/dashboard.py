from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import Release, Review, Promo, CollectionLog, DriverTariff
from app.models.collection_log import CollectionStatus

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get dashboard summary with key metrics"""
    
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    # New releases this week
    releases_count = await db.scalar(
        select(func.count(Release.id)).where(Release.collected_at >= week_ago)
    )
    
    # New reviews this week
    reviews_count = await db.scalar(
        select(func.count(Review.id)).where(Review.collected_at >= week_ago)
    )
    
    # Active promos by competitor
    active_promos_query = await db.execute(
        select(
            func.count(Promo.id).label("count"),
        ).where(
            Promo.is_active == True,
            (Promo.valid_until >= datetime.now().date()) | (Promo.valid_until == None),
        )
    )
    active_promos_count = active_promos_query.scalar() or 0
    
    # Last collection
    last_log = await db.scalar(
        select(CollectionLog)
        .where(CollectionLog.status == CollectionStatus.SUCCESS)
        .order_by(CollectionLog.completed_at.desc())
        .limit(1)
    )
    
    # Tariff changes this week (simplified - count new tariff records)
    tariff_changes = await db.scalar(
        select(func.count(DriverTariff.id)).where(DriverTariff.collected_at >= week_ago)
    )
    
    # Determine health status
    health_status = "healthy"
    if last_log:
        hours_since = (now - last_log.completed_at).total_seconds() / 3600
        if hours_since > 48:
            health_status = "error"
        elif hours_since > 24:
            health_status = "warning"
    else:
        health_status = "warning"
    
    return {
        "last_collection": last_log.completed_at.isoformat() if last_log else None,
        "new_releases_week": releases_count or 0,
        "new_reviews_week": reviews_count or 0,
        "active_promos": active_promos_count,
        "tariff_changes_week": tariff_changes or 0,
        "health_status": health_status,
    }

