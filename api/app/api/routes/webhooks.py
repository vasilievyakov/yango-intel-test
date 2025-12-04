from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog

from app.api.deps import get_database, verify_webhook_secret
from app.services.webhook_processor import WebhookProcessor

router = APIRouter()
logger = structlog.get_logger()


class OctoparseWebhookPayload(BaseModel):
    taskId: str
    taskName: str
    taskGroup: Optional[str] = None
    dataCount: int = 0
    dataList: List[Dict[str, Any]] = []
    exportedAt: Optional[str] = None


@router.post("/octoparse")
async def receive_octoparse_webhook(
    payload: OctoparseWebhookPayload,
    db: AsyncSession = Depends(get_database),
    _: bool = Depends(verify_webhook_secret),
):
    """
    Receive and process webhook data from Octoparse.
    
    Expected task naming convention:
    - {competitor}-driver-pe: Driver tariffs
    - {competitor}-rider-pe: Rider tariffs
    - appstore-{competitor}: App Store reviews + releases
    - playstore-{competitor}: Play Store reviews + releases
    """
    
    logger.info(
        "Received Octoparse webhook",
        task_id=payload.taskId,
        task_name=payload.taskName,
        data_count=payload.dataCount,
    )
    
    try:
        processor = WebhookProcessor(db)
        result = await processor.process(payload)
        
        logger.info(
            "Webhook processed successfully",
            task_name=payload.taskName,
            processed_count=result.get("processed", 0),
        )
        
        return {
            "status": "ok",
            "processed": result.get("processed", 0),
            "task_name": payload.taskName,
        }
        
    except Exception as e:
        logger.error(
            "Webhook processing failed",
            task_name=payload.taskName,
            error=str(e),
        )
        # Don't expose internal errors to webhook sender
        raise HTTPException(
            status_code=500,
            detail="Internal processing error",
        )


@router.post("/test")
async def test_webhook(
    request: Request,
    db: AsyncSession = Depends(get_database),
):
    """Test endpoint for webhook debugging (no auth required in dev)"""
    
    body = await request.json()
    logger.info("Test webhook received", body=body)
    
    return {
        "status": "ok",
        "received": body,
    }

