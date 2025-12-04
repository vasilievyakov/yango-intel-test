import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base


class DiscountType(str, enum.Enum):
    PERCENT = "percent"
    FIXED = "fixed"
    FREE_RIDE = "free_ride"


class TargetAudience(str, enum.Enum):
    DRIVER = "driver"
    RIDER = "rider"
    BOTH = "both"


class Promo(Base):
    """Promotional offers and discounts"""
    __tablename__ = "promos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    
    title: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    code: Mapped[str | None] = mapped_column(String(50))
    
    discount_type: Mapped[DiscountType | None] = mapped_column(Enum(DiscountType))
    discount_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date)
    conditions: Mapped[str | None] = mapped_column(Text)
    
    target_audience: Mapped[TargetAudience] = mapped_column(
        Enum(TargetAudience), default=TargetAudience.RIDER
    )
    
    source_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="promos")

    def __repr__(self) -> str:
        return f"<Promo {self.title}>"

