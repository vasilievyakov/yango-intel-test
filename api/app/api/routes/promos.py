from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.api.deps import get_database, verify_clerk_token
from app.models import Promo, Competitor

router = APIRouter()


@router.get("")
async def get_promos(
    competitor_id: Optional[UUID] = None,
    active_only: bool = Query(True),
    target: Optional[str] = Query(None, regex="^(driver|rider)$"),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get all promos with filters"""
    
    query = select(Promo).options(joinedload(Promo.competitor))
    
    if competitor_id:
        query = query.where(Promo.competitor_id == competitor_id)
    
    if active_only:
        query = query.where(
            Promo.is_active == True,
            (Promo.valid_until >= datetime.now().date()) | (Promo.valid_until == None),
        )
    
    if target:
        query = query.where(Promo.target_audience == target)
    
    query = query.order_by(Promo.valid_until.desc().nullslast())
    
    result = await db.execute(query)
    promos = result.scalars().unique().all()
    
    return {
        "promos": [
            {
                "id": str(p.id),
                "competitor": {
                    "id": str(p.competitor.id),
                    "name": p.competitor.name,
                    "slug": p.competitor.slug,
                    "logo_url": p.competitor.logo_url,
                },
                "title": p.title,
                "description": p.description,
                "code": p.code,
                "discount_type": p.discount_type.value if p.discount_type else None,
                "discount_value": float(p.discount_value) if p.discount_value else None,
                "valid_from": p.valid_from.isoformat() if p.valid_from else None,
                "valid_until": p.valid_until.isoformat() if p.valid_until else None,
                "conditions": p.conditions,
                "target_audience": p.target_audience.value,
                "is_active": p.is_active,
                "collected_at": p.collected_at.isoformat(),
            }
            for p in promos
        ],
        "total": len(promos),
    }


@router.get("/{promo_id}")
async def get_promo(
    promo_id: UUID,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get single promo by ID"""
    
    result = await db.execute(
        select(Promo)
        .options(joinedload(Promo.competitor))
        .where(Promo.id == promo_id)
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    
    return {
        "promo": {
            "id": str(promo.id),
            "competitor": {
                "id": str(promo.competitor.id),
                "name": promo.competitor.name,
            },
            "title": promo.title,
            "description": promo.description,
            "code": promo.code,
            "discount_type": promo.discount_type.value if promo.discount_type else None,
            "discount_value": float(promo.discount_value) if promo.discount_value else None,
            "valid_from": promo.valid_from.isoformat() if promo.valid_from else None,
            "valid_until": promo.valid_until.isoformat() if promo.valid_until else None,
            "conditions": promo.conditions,
            "target_audience": promo.target_audience.value,
            "is_active": promo.is_active,
        }
    }

