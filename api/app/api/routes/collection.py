from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import datetime, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import CollectionLog, Competitor
from app.models.collection_log import CollectionStatus

router = APIRouter()


@router.get("/status")
async def get_collection_status(
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get status of all collection sources"""
    
    # Get last successful collection for each task
    # This is a simplified version - in production, you'd want a more sophisticated query
    
    result = await db.execute(
        select(CollectionLog)
        .options(joinedload(CollectionLog.competitor))
        .order_by(CollectionLog.completed_at.desc())
        .limit(100)
    )
    logs = result.scalars().unique().all()
    
    # Group by task_name to get latest status for each
    sources = {}
    for log in logs:
        if log.task_name and log.task_name not in sources:
            sources[log.task_name] = {
                "task_name": log.task_name,
                "competitor": log.competitor.name if log.competitor else None,
                "source_type": log.source_type.value,
                "last_success": log.completed_at.isoformat() if log.status == CollectionStatus.SUCCESS else None,
                "last_status": log.status.value,
                "items_collected": log.items_collected,
            }
    
    # Calculate overall health
    now = datetime.utcnow()
    failed_count = sum(1 for s in sources.values() if s["last_status"] == "failed")
    warning_count = sum(1 for s in sources.values() if s["last_status"] == "partial")
    
    if failed_count > len(sources) / 2:
        health = "error"
    elif failed_count > 0 or warning_count > len(sources) / 3:
        health = "warning"
    else:
        health = "healthy"
    
    return {
        "sources": list(sources.values()),
        "last_update": now.isoformat(),
        "health": health,
    }


@router.get("/logs")
async def get_collection_logs(
    status: Optional[str] = Query(None, regex="^(success|partial|failed)$"),
    days: int = Query(7, ge=1, le=90),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get collection logs with filters"""
    
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(CollectionLog).options(joinedload(CollectionLog.competitor))
    count_query = select(func.count(CollectionLog.id))
    
    # Apply filters
    filters = [CollectionLog.completed_at >= since]
    
    if status:
        filters.append(CollectionLog.status == CollectionStatus(status))
    
    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)
    
    # Get total count
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.order_by(CollectionLog.completed_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().unique().all()
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "task_name": log.task_name,
                "competitor": log.competitor.name if log.competitor else None,
                "source_type": log.source_type.value,
                "status": log.status.value,
                "error_message": log.error_message,
                "items_collected": log.items_collected,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "completed_at": log.completed_at.isoformat(),
            }
            for log in logs
        ],
        "total": total or 0,
    }

