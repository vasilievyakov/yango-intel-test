from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date, timedelta

from app.api.deps import get_database, verify_clerk_token
from app.models import Digest
from app.services.digest_generator import DigestGeneratorService

router = APIRouter()


class GenerateDigestRequest(BaseModel):
    period: str = "week"  # week or month
    end_date: Optional[str] = None


@router.post("/generate")
async def generate_digest(
    request: GenerateDigestRequest,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Generate a new digest using AI"""
    
    # Calculate period
    if request.end_date:
        end_date = date.fromisoformat(request.end_date)
    else:
        end_date = date.today()
    
    if request.period == "week":
        start_date = end_date - timedelta(days=7)
    elif request.period == "month":
        start_date = end_date - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use 'week' or 'month'")
    
    # Generate digest
    generator = DigestGeneratorService(db)
    result = await generator.generate(start_date, end_date, user_id=user.get("sub"))
    
    return result


@router.get("/history")
async def get_digest_history(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get history of generated digests"""
    
    result = await db.execute(
        select(Digest)
        .order_by(Digest.created_at.desc())
        .limit(limit)
    )
    digests = result.scalars().all()
    
    return {
        "digests": [
            {
                "id": str(d.id),
                "period_start": d.period_start.isoformat(),
                "period_end": d.period_end.isoformat(),
                "metadata": d.metadata,
                "created_by": d.created_by,
                "created_at": d.created_at.isoformat(),
            }
            for d in digests
        ],
        "total": len(digests),
    }


@router.get("/{digest_id}")
async def get_digest(
    digest_id: UUID,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Get a specific digest by ID"""
    
    result = await db.execute(
        select(Digest).where(Digest.id == digest_id)
    )
    digest = result.scalar_one_or_none()
    
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    return {
        "id": str(digest.id),
        "period_start": digest.period_start.isoformat(),
        "period_end": digest.period_end.isoformat(),
        "content": digest.content,
        "metadata": digest.metadata,
        "created_by": digest.created_by,
        "created_at": digest.created_at.isoformat(),
    }


class ExportDigestRequest(BaseModel):
    format: str = "markdown"  # markdown or pdf


@router.post("/{digest_id}/export")
async def export_digest(
    digest_id: UUID,
    request: ExportDigestRequest,
    db: AsyncSession = Depends(get_database),
    user: dict = Depends(verify_clerk_token),
):
    """Export digest in specified format"""
    
    result = await db.execute(
        select(Digest).where(Digest.id == digest_id)
    )
    digest = result.scalar_one_or_none()
    
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    if request.format == "markdown":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=digest.content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="digest-{digest.period_end}.md"'
            },
        )
    elif request.format == "pdf":
        # TODO: Implement PDF generation
        raise HTTPException(status_code=501, detail="PDF export not yet implemented")
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'markdown' or 'pdf'")

