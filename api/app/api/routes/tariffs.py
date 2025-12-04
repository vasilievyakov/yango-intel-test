from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import DriverTariff, RiderTariff, Competitor

router = APIRouter()


@router.get("/comparison")
async def get_tariff_comparison(
    tariff_type: Optional[str] = Query(None, alias="type", regex="^(driver|rider)$"),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get tariff comparison across all competitors"""
    
    # Get all active competitors
    competitors_result = await db.execute(
        select(Competitor).where(Competitor.is_active == True)
    )
    competitors = competitors_result.scalars().all()
    
    comparison = []
    
    for comp in competitors:
        item = {
            "competitor": comp.name,
            "competitor_id": str(comp.id),
            "logo_url": comp.logo_url,
        }
        
        # Get latest driver tariff
        if tariff_type in (None, "driver"):
            driver_result = await db.execute(
                select(DriverTariff)
                .where(DriverTariff.competitor_id == comp.id, DriverTariff.is_latest == True)
                .limit(1)
            )
            driver_tariff = driver_result.scalar_one_or_none()
            
            if driver_tariff:
                item["driver"] = {
                    "commission_rate": float(driver_tariff.commission_rate) if driver_tariff.commission_rate else None,
                    "signup_bonus": float(driver_tariff.signup_bonus) if driver_tariff.signup_bonus else None,
                    "referral_bonus": float(driver_tariff.referral_bonus) if driver_tariff.referral_bonus else None,
                    "min_fare": float(driver_tariff.min_fare) if driver_tariff.min_fare else None,
                }
        
        # Get latest rider tariff
        if tariff_type in (None, "rider"):
            rider_result = await db.execute(
                select(RiderTariff)
                .where(RiderTariff.competitor_id == comp.id, RiderTariff.is_latest == True)
                .limit(1)
            )
            rider_tariff = rider_result.scalar_one_or_none()
            
            if rider_tariff:
                item["rider"] = {
                    "base_fare": float(rider_tariff.base_fare) if rider_tariff.base_fare else None,
                    "per_km_rate": float(rider_tariff.per_km_rate) if rider_tariff.per_km_rate else None,
                    "per_min_rate": float(rider_tariff.per_min_rate) if rider_tariff.per_min_rate else None,
                    "booking_fee": float(rider_tariff.booking_fee) if rider_tariff.booking_fee else None,
                }
        
        comparison.append(item)
    
    return {
        "comparison": comparison,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/history/{competitor_id}")
async def get_tariff_history(
    competitor_id: UUID,
    days: int = Query(30, ge=1, le=365),
    tariff_type: str = Query("driver", regex="^(driver|rider)$"),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get tariff history for a specific competitor"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    if tariff_type == "driver":
        result = await db.execute(
            select(DriverTariff)
            .where(
                DriverTariff.competitor_id == competitor_id,
                DriverTariff.collected_at >= since,
            )
            .order_by(DriverTariff.collected_at)
        )
        tariffs = result.scalars().all()
        
        history = [
            {
                "date": t.collected_at.isoformat(),
                "commission_rate": float(t.commission_rate) if t.commission_rate else None,
                "signup_bonus": float(t.signup_bonus) if t.signup_bonus else None,
            }
            for t in tariffs
        ]
    else:
        result = await db.execute(
            select(RiderTariff)
            .where(
                RiderTariff.competitor_id == competitor_id,
                RiderTariff.collected_at >= since,
            )
            .order_by(RiderTariff.collected_at)
        )
        tariffs = result.scalars().all()
        
        history = [
            {
                "date": t.collected_at.isoformat(),
                "base_fare": float(t.base_fare) if t.base_fare else None,
                "per_km_rate": float(t.per_km_rate) if t.per_km_rate else None,
            }
            for t in tariffs
        ]
    
    return {"history": history}


@router.get("/changes")
async def get_tariff_changes(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get recent tariff changes"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get recent driver tariffs with their competitors
    result = await db.execute(
        select(DriverTariff)
        .options(joinedload(DriverTariff.competitor))
        .where(DriverTariff.collected_at >= since)
        .order_by(DriverTariff.collected_at.desc())
    )
    tariffs = result.scalars().unique().all()
    
    # TODO: Compare with previous values to detect actual changes
    # For now, just return recent records
    
    changes = [
        {
            "competitor": t.competitor.name,
            "field": "commission_rate",
            "new_value": float(t.commission_rate) if t.commission_rate else None,
            "changed_at": t.collected_at.isoformat(),
        }
        for t in tariffs
        if t.commission_rate
    ]
    
    return {"changes": changes}

