import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, ARRAY, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class DriverTariff(Base):
    """Driver tariffs and conditions"""
    __tablename__ = "driver_tariffs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    
    commission_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # Commission %
    min_fare: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    signup_bonus: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    referral_bonus: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    
    requirements: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    benefits: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    
    currency: Mapped[str] = mapped_column(String(3), default="PEN")
    source_url: Mapped[str | None] = mapped_column(String(500))
    
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="driver_tariffs")

    __table_args__ = (
        Index("idx_driver_tariffs_latest", "competitor_id", postgresql_where=(is_latest == True)),
    )

    def __repr__(self) -> str:
        return f"<DriverTariff {self.competitor_id} commission={self.commission_rate}%>"


class RiderTariff(Base):
    """Rider/passenger tariffs"""
    __tablename__ = "rider_tariffs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    
    service_type: Mapped[str] = mapped_column(String(50), default="standard")
    base_fare: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    per_km_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    per_min_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    booking_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    
    currency: Mapped[str] = mapped_column(String(3), default="PEN")
    source_url: Mapped[str | None] = mapped_column(String(500))
    
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="rider_tariffs")

    __table_args__ = (
        Index("idx_rider_tariffs_latest", "competitor_id", "service_type", postgresql_where=(is_latest == True)),
    )

    def __repr__(self) -> str:
        return f"<RiderTariff {self.competitor_id} base={self.base_fare}>"

