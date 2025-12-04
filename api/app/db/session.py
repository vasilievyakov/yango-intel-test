from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
import structlog

from app.config import settings
from app.db.base import Base

logger = structlog.get_logger()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """Initialize database (create tables if not exist)"""
    async with engine.begin() as conn:
        # Import all models to register them
        from app.models import (
            competitor,
            tariff,
            promo,
            release,
            review,
            collection_log,
            digest,
            news_item,
        )
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

