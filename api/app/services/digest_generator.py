"""AI-powered Digest Generation Service using Google Gemini"""
from datetime import date, datetime
from typing import Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import google.generativeai as genai

from app.config import settings
from app.models import Release, Review, Promo, DriverTariff, Digest, Competitor
from app.models.review import Sentiment

logger = structlog.get_logger()


DIGEST_PROMPT = """You are a competitive intelligence analyst for Yango (ride-hailing service in Peru).

Generate a weekly digest in Russian based on this data:

PERIOD: {period_start} — {period_end}

NEW RELEASES:
{releases_section}

TARIFF CHANGES:
{tariff_changes_section}

ACTIVE PROMOS:
{promos_section}

REVIEW TRENDS:
{review_trends_section}

Format the digest as markdown with these sections:
1. # Дайджест за {period_end}
2. ## Ключевые события (2-3 bullet points of most important changes)
3. ## Новые релизы (list each with brief analysis)
4. ## Изменения тарифов (if any, show as table)
5. ## Активные промоакции (table format)
6. ## Тренды в отзывах (insights from review analysis)
7. ## Рекомендации для Yango (2-3 actionable insights)

Keep the tone professional but accessible. Highlight competitive threats and opportunities.
Total length: 500-800 words in Russian."""


class DigestGeneratorService:
    """Service for generating competitive intelligence digests using Google Gemini"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = None
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            # Use Pro model for better quality digest generation
            self.model = genai.GenerativeModel(
                settings.GEMINI_MODEL_PRO,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,  # More creative for digest writing
                    max_output_tokens=2000,
                )
            )
            logger.info("Gemini digest generator initialized", model=settings.GEMINI_MODEL_PRO)
    
    async def generate(
        self,
        period_start: date,
        period_end: date,
        user_id: Optional[str] = None,
    ) -> dict:
        """Generate a digest for the given period"""
        
        logger.info(
            "Generating digest",
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
        )
        
        # Collect data
        releases = await self._get_releases(period_start, period_end)
        tariff_changes = await self._get_tariff_changes(period_start, period_end)
        promos = await self._get_active_promos()
        review_trends = await self._get_review_trends(period_start, period_end)
        
        # Format sections
        releases_section = self._format_releases(releases)
        tariff_section = self._format_tariff_changes(tariff_changes)
        promos_section = self._format_promos(promos)
        trends_section = self._format_trends(review_trends)
        
        # Generate content
        if self.model:
            content = await self._generate_with_ai(
                period_start=period_start,
                period_end=period_end,
                releases_section=releases_section,
                tariff_section=tariff_section,
                promos_section=promos_section,
                trends_section=trends_section,
            )
        else:
            content = self._generate_fallback(
                period_start=period_start,
                period_end=period_end,
                releases_section=releases_section,
                tariff_section=tariff_section,
                promos_section=promos_section,
                trends_section=trends_section,
            )
        
        # Save to database
        digest = Digest(
            period_start=period_start,
            period_end=period_end,
            content=content,
            digest_metadata={
                "releases_count": len(releases),
                "tariff_changes_count": len(tariff_changes),
                "active_promos_count": len(promos),
                "model": settings.GEMINI_MODEL_PRO if self.model else "fallback",
            },
            created_by=user_id,
        )
        
        self.db.add(digest)
        await self.db.commit()
        await self.db.refresh(digest)
        
        logger.info("Digest generated", digest_id=str(digest.id))
        
        return {
            "id": str(digest.id),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "content": content,
            "metadata": digest.digest_metadata,
            "created_at": digest.created_at.isoformat(),
        }
    
    async def _get_releases(self, start: date, end: date) -> list:
        """Get releases for the period"""
        result = await self.db.execute(
            select(Release)
            .where(
                Release.release_date >= start,
                Release.release_date <= end,
            )
            .order_by(Release.release_date.desc())
        )
        return result.scalars().all()
    
    async def _get_tariff_changes(self, start: date, end: date) -> list:
        """Get tariff changes for the period"""
        result = await self.db.execute(
            select(DriverTariff)
            .where(
                DriverTariff.collected_at >= datetime.combine(start, datetime.min.time()),
                DriverTariff.collected_at <= datetime.combine(end, datetime.max.time()),
            )
        )
        return result.scalars().all()
    
    async def _get_active_promos(self) -> list:
        """Get currently active promos"""
        today = date.today()
        result = await self.db.execute(
            select(Promo)
            .where(
                Promo.is_active == True,
                (Promo.valid_until >= today) | (Promo.valid_until == None),
            )
        )
        return result.scalars().all()
    
    async def _get_review_trends(self, start: date, end: date) -> dict:
        """Analyze review trends for the period"""
        competitors_result = await self.db.execute(
            select(Competitor).where(Competitor.is_active == True)
        )
        competitors = competitors_result.scalars().all()
        
        trends = {}
        for comp in competitors:
            # Count by sentiment
            for sentiment in Sentiment:
                count = await self.db.scalar(
                    select(func.count(Review.id)).where(
                        Review.competitor_id == comp.id,
                        Review.review_date >= start,
                        Review.review_date <= end,
                        Review.sentiment == sentiment,
                    )
                )
                if comp.name not in trends:
                    trends[comp.name] = {}
                trends[comp.name][sentiment.value] = count or 0
        
        return trends
    
    def _format_releases(self, releases: list) -> str:
        if not releases:
            return "Нет новых релизов за период"
        
        lines = []
        for r in releases:
            line = f"- {r.competitor.name if hasattr(r, 'competitor') else 'Unknown'} "
            line += f"({r.platform.value}) v{r.version}"
            if r.release_notes:
                line += f": {r.release_notes[:100]}..."
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_tariff_changes(self, changes: list) -> str:
        if not changes:
            return "Нет изменений тарифов за период"
        
        lines = []
        for t in changes:
            lines.append(f"- Комиссия: {t.commission_rate}%")
        
        return "\n".join(lines)
    
    def _format_promos(self, promos: list) -> str:
        if not promos:
            return "Нет активных промоакций"
        
        lines = []
        for p in promos:
            line = f"- {p.competitor.name if hasattr(p, 'competitor') else 'Unknown'}: {p.title}"
            if p.valid_until:
                line += f" (до {p.valid_until})"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_trends(self, trends: dict) -> str:
        if not trends:
            return "Недостаточно данных для анализа трендов"
        
        lines = []
        for comp, sentiments in trends.items():
            total = sum(sentiments.values())
            if total > 0:
                neg_pct = sentiments.get("negative", 0) / total * 100
                lines.append(f"- {comp}: {total} отзывов, {neg_pct:.0f}% негативных")
        
        return "\n".join(lines) if lines else "Недостаточно данных"
    
    async def _generate_with_ai(
        self,
        period_start: date,
        period_end: date,
        releases_section: str,
        tariff_section: str,
        promos_section: str,
        trends_section: str,
    ) -> str:
        """Generate digest content using Gemini"""
        
        prompt = DIGEST_PROMPT.format(
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            releases_section=releases_section,
            tariff_changes_section=tariff_section,
            promos_section=promos_section,
            review_trends_section=trends_section,
        )
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error("AI digest generation failed", error=str(e))
            return self._generate_fallback(
                period_start, period_end,
                releases_section, tariff_section,
                promos_section, trends_section,
            )
    
    def _generate_fallback(
        self,
        period_start: date,
        period_end: date,
        releases_section: str,
        tariff_section: str,
        promos_section: str,
        trends_section: str,
    ) -> str:
        """Generate simple digest without AI"""
        
        return f"""# Дайджест за {period_end}

## Период: {period_start} — {period_end}

## Новые релизы

{releases_section}

## Изменения тарифов

{tariff_section}

## Активные промоакции

{promos_section}

## Тренды в отзывах

{trends_section}

---
*Дайджест сгенерирован автоматически. Для более детального анализа настройте GOOGLE_API_KEY.*
"""
