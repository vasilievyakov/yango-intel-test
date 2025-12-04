import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class Digest(Base):
    """Generated competitive intelligence digests"""
    __tablename__ = "digests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata about what was included in the digest
    metadata: Mapped[dict | None] = mapped_column(JSONB)
    
    created_by: Mapped[str | None] = mapped_column(String(100))  # Clerk user ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Digest {self.period_start} - {self.period_end}>"

