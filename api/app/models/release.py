import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Date, ForeignKey, Numeric, Text, Enum, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base


class Platform(str, enum.Enum):
    IOS = "ios"
    ANDROID = "android"


class Significance(str, enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    BUGFIX = "bugfix"


class Category(Base):
    """Categories for releases and reviews"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100))
    name_es: Mapped[str | None] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"<Category {self.slug}>"


class Release(Base):
    """App releases and updates"""
    __tablename__ = "releases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    
    platform: Mapped[Platform] = mapped_column(Enum(Platform), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date)
    release_notes: Mapped[str | None] = mapped_column(Text)
    
    rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1))
    rating_count: Mapped[int | None] = mapped_column(Integer)
    
    significance: Mapped[Significance | None] = mapped_column(Enum(Significance))
    summary_ru: Mapped[str | None] = mapped_column(Text)  # AI-generated summary
    
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="releases")
    categories = relationship("ReleaseCategory", back_populates="release")

    __table_args__ = (
        UniqueConstraint("competitor_id", "platform", "version", name="uq_release_version"),
    )

    def __repr__(self) -> str:
        return f"<Release {self.platform.value} {self.version}>"


class ReleaseCategory(Base):
    """Many-to-many relationship between releases and categories"""
    __tablename__ = "release_categories"

    release_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("releases.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), primary_key=True
    )
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=1.0)

    # Relationships
    release = relationship("Release", back_populates="categories")
    category = relationship("Category")

