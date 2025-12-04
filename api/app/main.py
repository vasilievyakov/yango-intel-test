from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.db.session import init_db
from app.api.routes import (
    health,
    webhooks,
    tariffs,
    promos,
    releases,
    reviews,
    digest,
    collection,
    dashboard,
    news,
    competitors,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting application", app_name=settings.APP_NAME)
    
    # Initialize database
    await init_db()
    
    yield
    
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for Yango Competitive Intelligence platform",
    lifespan=lifespan,
)

# CORS
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["Competitors"])
app.include_router(tariffs.router, prefix="/api/tariffs", tags=["Tariffs"])
app.include_router(promos.router, prefix="/api/promos", tags=["Promos"])
app.include_router(releases.router, prefix="/api/releases", tags=["Releases"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(digest.router, prefix="/api/digest", tags=["Digest"])
app.include_router(collection.router, prefix="/api/collection", tags=["Collection"])
app.include_router(news.router, prefix="/api/news", tags=["News"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

