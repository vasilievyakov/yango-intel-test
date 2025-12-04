"""API Dependencies for authentication and database access"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from jose import jwt, JWTError
import structlog

from app.config import settings
from app.db.session import get_db

logger = structlog.get_logger()

security = HTTPBearer(auto_error=False)


async def verify_clerk_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    Verify JWT token from Clerk.
    Returns user payload or None if no token / in development mode.
    """
    # Skip auth in development if Clerk is not configured
    if not settings.CLERK_JWKS_URL:
        logger.warning("Clerk JWKS URL not configured, skipping auth")
        return {"sub": "dev-user", "email": "dev@example.com"}
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    
    token = credentials.credentials
    
    try:
        # Fetch JWKS from Clerk
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.CLERK_JWKS_URL)
            jwks = response.json()
        
        # Decode and verify the token
        # Note: In production, you'd cache the JWKS
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key",
            )
        
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
        )
        
        return payload
        
    except JWTError as e:
        logger.error("JWT verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except httpx.HTTPError as e:
        logger.error("Failed to fetch JWKS", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )


async def verify_webhook_secret(
    x_webhook_secret: str = Header(..., alias="X-Webhook-Secret"),
) -> bool:
    """Verify webhook secret from Octoparse"""
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )
    return True


# Database dependency
async def get_database() -> AsyncSession:
    """Get database session"""
    async for session in get_db():
        yield session

