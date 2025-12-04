import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, ForeignKey, Text, Enum, Integer, SmallInteger, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base
from app.models.release import Platform


class UserRole(str, enum.Enum):
    DRIVER = "driver"
    RIDER = "rider"
    UNKNOWN = "unknown"


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Review(Base):
    """User reviews from app stores"""
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    
    platform: Mapped[Platform] = mapped_column(Enum(Platform), nullable=False)
    author: Mapped[str | None] = mapped_column(String(200))
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    review_date: Mapped[date | None] = mapped_column(Date)
    app_version: Mapped[str | None] = mapped_column(String(20))
    language: Mapped[str] = mapped_column(String(5), default="es")
    
    # AI-classified fields
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.UNKNOWN)
    sentiment: Mapped[Sentiment | None] = mapped_column(Enum(Sentiment))
    key_topics: Mapped[str | None] = mapped_column(Text)  # JSON array as text
    
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="reviews")
    categories = relationship("ReviewCategory", back_populates="review")

    __table_args__ = (
        Index("idx_reviews_competitor", "competitor_id"),
        Index("idx_reviews_date", "review_date"),
        Index("idx_reviews_sentiment", "sentiment"),
        Index("idx_reviews_role", "role"),
        Index("idx_reviews_platform", "platform"),
    )

    def __repr__(self) -> str:
        return f"<Review {self.external_id} rating={self.rating}>"


class ReviewCategory(Base):
    """Many-to-many relationship between reviews and categories"""
    __tablename__ = "review_categories"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), primary_key=True
    )

    # Relationships
    review = relationship("Review", back_populates="categories")
    category = relationship("Category")

