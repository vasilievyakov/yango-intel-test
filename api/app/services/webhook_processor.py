"""Webhook Processor for Octoparse data"""
import re
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    Competitor, DriverTariff, RiderTariff, Promo, Release, Review, CollectionLog
)
from app.models.collection_log import SourceType, CollectionStatus
from app.models.release import Platform, Significance
from app.models.promo import DiscountType, TargetAudience
from app.models.review import UserRole, Sentiment
from app.services.classifier import ClassifierService

logger = structlog.get_logger()


class WebhookProcessor:
    """
    Processes incoming webhook data from Octoparse.
    
    Task naming convention:
    - {competitor}-driver-pe: Driver tariffs
    - {competitor}-rider-pe: Rider tariffs
    - appstore-{competitor}: App Store data
    - playstore-{competitor}: Play Store data
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.classifier = ClassifierService()
    
    async def process(self, payload) -> dict:
        """Process webhook payload and store data"""
        
        task_name = payload.taskName.lower()
        data_list = payload.dataList
        
        # Create collection log
        log = CollectionLog(
            task_name=payload.taskName,
            source_type=self._detect_source_type(task_name),
            started_at=datetime.utcnow(),
            status=CollectionStatus.SUCCESS,
            raw_payload={"taskId": payload.taskId, "dataCount": payload.dataCount},
        )
        
        try:
            # Find competitor from task name
            competitor = await self._find_competitor(task_name)
            if competitor:
                log.competitor_id = competitor.id
            
            # Route to appropriate processor
            processed_count = 0
            
            if "-driver-" in task_name:
                processed_count = await self._process_driver_tariffs(competitor, data_list)
            elif "-rider-" in task_name:
                processed_count = await self._process_rider_tariffs(competitor, data_list)
            elif task_name.startswith("appstore-") or task_name.startswith("playstore-"):
                processed_count = await self._process_app_store_data(competitor, task_name, data_list)
            else:
                logger.warning("Unknown task type", task_name=task_name)
                log.status = CollectionStatus.PARTIAL
                log.error_message = "Unknown task type"
            
            log.items_collected = processed_count
            log.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error("Processing failed", task_name=task_name, error=str(e))
            log.status = CollectionStatus.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
        
        self.db.add(log)
        await self.db.commit()
        
        return {"processed": log.items_collected, "status": log.status.value}
    
    def _detect_source_type(self, task_name: str) -> SourceType:
        """Detect source type from task name"""
        if task_name.startswith("appstore-"):
            return SourceType.APPSTORE
        elif task_name.startswith("playstore-"):
            return SourceType.PLAYSTORE
        else:
            return SourceType.WEBSITE
    
    async def _find_competitor(self, task_name: str) -> Optional[Competitor]:
        """Find competitor from task name"""
        # Extract competitor slug from task name
        # Examples: indriver-driver-pe -> indriver, appstore-uber -> uber
        
        patterns = [
            r"^(appstore|playstore)-(\w+)$",  # appstore-uber
            r"^(\w+)-(driver|rider)-\w+$",  # indriver-driver-pe
        ]
        
        slug = None
        for pattern in patterns:
            match = re.match(pattern, task_name)
            if match:
                groups = match.groups()
                if groups[0] in ("appstore", "playstore"):
                    slug = groups[1]
                else:
                    slug = groups[0]
                break
        
        if not slug:
            return None
        
        result = await self.db.execute(
            select(Competitor).where(Competitor.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def _process_driver_tariffs(self, competitor: Optional[Competitor], data_list: list) -> int:
        """Process driver tariff data"""
        if not competitor or not data_list:
            return 0
        
        # Mark previous tariffs as not latest
        await self.db.execute(
            DriverTariff.__table__.update()
            .where(DriverTariff.competitor_id == competitor.id)
            .values(is_latest=False)
        )
        
        processed = 0
        for item in data_list:
            tariff = DriverTariff(
                competitor_id=competitor.id,
                commission_rate=self._parse_decimal(item.get("commission")),
                signup_bonus=self._parse_decimal(item.get("signup_bonus")),
                referral_bonus=self._parse_decimal(item.get("referral_bonus")),
                min_fare=self._parse_decimal(item.get("min_fare")),
                requirements=self._parse_list(item.get("requirements")),
                benefits=self._parse_list(item.get("benefits")),
                is_latest=True,
            )
            self.db.add(tariff)
            processed += 1
        
        return processed
    
    async def _process_rider_tariffs(self, competitor: Optional[Competitor], data_list: list) -> int:
        """Process rider tariff data"""
        if not competitor or not data_list:
            return 0
        
        # Mark previous tariffs as not latest
        await self.db.execute(
            RiderTariff.__table__.update()
            .where(RiderTariff.competitor_id == competitor.id)
            .values(is_latest=False)
        )
        
        processed = 0
        for item in data_list:
            tariff = RiderTariff(
                competitor_id=competitor.id,
                base_fare=self._parse_decimal(item.get("base_fare")),
                per_km_rate=self._parse_decimal(item.get("per_km_rate")),
                per_min_rate=self._parse_decimal(item.get("per_min_rate")),
                booking_fee=self._parse_decimal(item.get("booking_fee")),
                service_type=item.get("service_type", "standard"),
                is_latest=True,
            )
            self.db.add(tariff)
            processed += 1
        
        return processed
    
    async def _process_app_store_data(
        self, competitor: Optional[Competitor], task_name: str, data_list: list
    ) -> int:
        """Process app store data (reviews + release info)"""
        if not competitor or not data_list:
            return 0
        
        platform = Platform.IOS if "appstore" in task_name else Platform.ANDROID
        processed = 0
        
        for item in data_list:
            # Process release info if present
            if item.get("app_version"):
                await self._process_release(competitor, platform, item)
                processed += 1
            
            # Process reviews if present
            reviews = item.get("reviews", [])
            if isinstance(reviews, list):
                for review_data in reviews:
                    await self._process_review(competitor, platform, review_data)
                    processed += 1
        
        return processed
    
    async def _process_release(self, competitor: Competitor, platform: Platform, data: dict):
        """Process a single release"""
        version = data.get("app_version")
        if not version:
            return
        
        # Check if release already exists
        existing = await self.db.execute(
            select(Release).where(
                Release.competitor_id == competitor.id,
                Release.platform == platform,
                Release.version == version,
            )
        )
        if existing.scalar_one_or_none():
            return  # Already have this version
        
        # Classify release notes
        release_notes = data.get("release_notes", "")
        classification = await self.classifier.classify_release(release_notes)
        
        release = Release(
            competitor_id=competitor.id,
            platform=platform,
            version=version,
            release_date=self._parse_date(data.get("release_date")),
            release_notes=release_notes,
            rating=self._parse_decimal(data.get("rating")),
            rating_count=self._parse_int(data.get("rating_count")),
            significance=Significance(classification.get("significance", "minor")),
            summary_ru=classification.get("summary_ru"),
        )
        self.db.add(release)
    
    async def _process_review(self, competitor: Competitor, platform: Platform, data: dict):
        """Process a single review"""
        external_id = data.get("review_id") or data.get("id")
        if not external_id:
            return
        
        # Make external_id unique per platform
        external_id = f"{platform.value}_{external_id}"
        
        # Check if review already exists
        existing = await self.db.execute(
            select(Review).where(Review.external_id == external_id)
        )
        if existing.scalar_one_or_none():
            return  # Already have this review
        
        # Classify review
        text = data.get("text", "")
        rating = self._parse_int(data.get("rating")) or 3
        classification = await self.classifier.classify_review(text, rating)
        
        review = Review(
            external_id=external_id,
            competitor_id=competitor.id,
            platform=platform,
            author=data.get("author"),
            rating=rating,
            text=text,
            review_date=self._parse_date(data.get("date")),
            app_version=data.get("app_version"),
            role=UserRole(classification.get("role", "unknown")),
            sentiment=Sentiment(classification.get("sentiment", "neutral")),
            key_topics=str(classification.get("key_topics", [])),
        )
        self.db.add(review)
    
    def _parse_decimal(self, value) -> Optional[Decimal]:
        """Parse a value to Decimal, extracting numbers from strings"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        
        if isinstance(value, str):
            # Extract numbers from strings like "25%", "S/200", "4.5"
            match = re.search(r"[\d.]+", value.replace(",", "."))
            if match:
                return Decimal(match.group())
        
        return None
    
    def _parse_int(self, value) -> Optional[int]:
        """Parse a value to int"""
        if value is None:
            return None
        
        if isinstance(value, int):
            return value
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, value) -> Optional[date]:
        """Parse a date string"""
        if not value:
            return None
        
        if isinstance(value, date):
            return value
        
        # Try common formats
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(str(value)[:19], fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _parse_list(self, value) -> Optional[list]:
        """Parse a string to list (pipe-separated)"""
        if not value:
            return None
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            return [item.strip() for item in value.split("|") if item.strip()]
        
        return None

