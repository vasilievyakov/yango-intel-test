import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Text, Enum, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import enum

from app.db.base import Base


class NewsSource(str, enum.Enum):
    PARALLEL = "parallel"
    MANUAL = "manual"


class NewsItem(Base):
    """
    News items scraped by AI based on info topics.
    Used for tracking competitor news, market trends, regulatory changes, etc.
    """
    __tablename__ = "news_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # The search query/topic that found this news
    search_query: Mapped[str] = mapped_column(Text, nullable=False)
    
    # News content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)  # Full content if available
    
    # Source information
    source_url: Mapped[str | None] = mapped_column(String(1000))
    source_name: Mapped[str | None] = mapped_column(String(200))  # e.g., "El Comercio", "Gestión"
    source_type: Mapped[NewsSource] = mapped_column(Enum(NewsSource), nullable=False)
    
    # Metadata
    published_date: Mapped[date | None] = mapped_column(Date)
    language: Mapped[str] = mapped_column(String(5), default="es")
    
    # AI-extracted data
    competitors_mentioned: Mapped[list[str] | None] = mapped_column(ARRAY(String))  # ['uber', 'indriver']
    topics: Mapped[list[str] | None] = mapped_column(ARRAY(String))  # ['pricing', 'regulation']
    sentiment: Mapped[str | None] = mapped_column(String(20))  # positive/negative/neutral
    relevance_score: Mapped[float | None] = mapped_column()  # 0.0 - 1.0
    
    # Raw AI response for debugging
    raw_response: Mapped[dict | None] = mapped_column(JSONB)
    
    # Status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_relevant: Mapped[bool] = mapped_column(Boolean, default=True)
    
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_news_items_date", "published_date"),
        Index("idx_news_items_query", "search_query"),
        Index("idx_news_items_relevant", "is_relevant"),
    )

    def __repr__(self) -> str:
        return f"<NewsItem {self.title[:50]}...>"

