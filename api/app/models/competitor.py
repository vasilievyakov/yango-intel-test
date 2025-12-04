import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Competitor(Base):
    """Competitor company (InDriver, Uber, Didi, Cabify)"""
    __tablename__ = "competitors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="PE")
    
    website_driver: Mapped[str | None] = mapped_column(String(500))
    website_rider: Mapped[str | None] = mapped_column(String(500))
    appstore_id: Mapped[str | None] = mapped_column(String(100))
    playstore_id: Mapped[str | None] = mapped_column(String(100))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    driver_tariffs = relationship("DriverTariff", back_populates="competitor")
    rider_tariffs = relationship("RiderTariff", back_populates="competitor")
    promos = relationship("Promo", back_populates="competitor")
    releases = relationship("Release", back_populates="competitor")
    reviews = relationship("Review", back_populates="competitor")
    collection_logs = relationship("CollectionLog", back_populates="competitor")

    def __repr__(self) -> str:
        return f"<Competitor {self.name}>"

