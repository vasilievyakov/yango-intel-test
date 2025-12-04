import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from app.db.base import Base


class SourceType(str, enum.Enum):
    WEBSITE = "website"
    APPSTORE = "appstore"
    PLAYSTORE = "playstore"


class CollectionStatus(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class CollectionLog(Base):
    """Logs of data collection operations"""
    __tablename__ = "collection_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    competitor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="SET NULL")
    )
    
    task_name: Mapped[str | None] = mapped_column(String(100))
    url: Mapped[str | None] = mapped_column(String(500))
    
    status: Mapped[CollectionStatus] = mapped_column(Enum(CollectionStatus), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    items_collected: Mapped[int] = mapped_column(Integer, default=0)
    
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="collection_logs")

    __table_args__ = (
        Index("idx_collection_logs_date", "completed_at"),
        Index("idx_collection_logs_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<CollectionLog {self.task_name} status={self.status.value}>"

