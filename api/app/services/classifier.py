"""AI Classification Service using Google Gemini"""
import json
from typing import Optional
import structlog
import google.generativeai as genai

from app.config import settings

logger = structlog.get_logger()


REVIEW_CLASSIFICATION_PROMPT = """You are a classifier for ride-hailing app reviews in Peru.

Analyze the review and return ONLY a JSON object with these fields:
- role: "driver" | "rider" | "unknown"
- categories: array of applicable categories from: ["pricing", "ux_ui", "safety", "driver_exp", "rider_exp", "promo", "support", "wait_time", "payment", "other"]
- sentiment: "positive" | "neutral" | "negative"
- key_topics: array of 1-3 main topics mentioned (in English, lowercase)

Role detection rules:
- "driver" if mentions: conducir, conductor, ganancias, comisión, mis pasajeros, mi carro, viajes que hago
- "rider" if mentions: pedir viaje, esperar carro, chofer (as customer perspective), mi conductor
- "unknown" if unclear

Review text: "{text}"
Rating: {rating}/5
Language: Spanish (Peru)

Respond with JSON only, no markdown formatting, no explanation."""


RELEASE_CLASSIFICATION_PROMPT = """Classify this app release notes for a ride-hailing app.

Release notes: "{text}"

Return ONLY a JSON object with:
- categories: array from ["pricing", "ux_ui", "safety", "driver_exp", "rider_exp", "promo", "other"]
- summary_ru: one sentence summary in Russian (max 100 chars)
- significance: "major" | "minor" | "bugfix"

Guidelines:
- "major": new features, significant UX changes, safety features
- "minor": improvements, optimizations, small changes
- "bugfix": bug fixes, stability improvements, generic updates

Respond with JSON only, no markdown."""


class ClassifierService:
    """Service for AI-powered classification of reviews and releases using Google Gemini"""
    
    def __init__(self):
        self.model = None
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,  # Low temperature for consistent classification
                )
            )
            logger.info("Gemini classifier initialized", model=settings.GEMINI_MODEL)
        else:
            logger.warning("GOOGLE_API_KEY not set, using fallback classification")
    
    async def classify_review(self, text: str, rating: int) -> dict:
        """
        Classify a review to determine role, sentiment, and categories.
        
        Returns:
            dict with: role, categories, sentiment, key_topics
        """
        if not self.model:
            return self._fallback_review_classification(text, rating)
        
        try:
            prompt = REVIEW_CLASSIFICATION_PROMPT.format(
                text=text[:1000],  # Limit text length
                rating=rating,
            )
            
            response = await self.model.generate_content_async(prompt)
            result = json.loads(response.text)
            
            logger.debug("Review classified", result=result)
            return result
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini response", error=str(e))
            return self._fallback_review_classification(text, rating)
        except Exception as e:
            logger.error("Classification failed", error=str(e))
            return self._fallback_review_classification(text, rating)
    
    async def classify_release(self, text: str) -> dict:
        """
        Classify release notes to determine categories and significance.
        
        Returns:
            dict with: categories, summary_ru, significance
        """
        if not self.model:
            return self._fallback_release_classification(text)
        
        try:
            prompt = RELEASE_CLASSIFICATION_PROMPT.format(text=text[:1000])
            
            response = await self.model.generate_content_async(prompt)
            result = json.loads(response.text)
            
            logger.debug("Release classified", result=result)
            return result
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini response", error=str(e))
            return self._fallback_release_classification(text)
        except Exception as e:
            logger.error("Classification failed", error=str(e))
            return self._fallback_release_classification(text)
    
    async def batch_classify_reviews(self, reviews: list[dict]) -> list[dict]:
        """
        Classify multiple reviews.
        
        Args:
            reviews: List of dicts with 'external_id', 'text', 'rating'
        
        Returns:
            List of classification results with external_id
        """
        results = []
        
        for review in reviews:
            classification = await self.classify_review(
                review.get("text", ""),
                review.get("rating", 3),
            )
            results.append({
                "external_id": review.get("external_id"),
                **classification,
            })
        
        return results
    
    def _fallback_review_classification(self, text: str, rating: int) -> dict:
        """Simple rule-based fallback when AI is unavailable"""
        text_lower = text.lower() if text else ""
        
        # Role detection
        driver_keywords = ["conductor", "conducir", "ganancia", "comisión", "mis pasajeros"]
        rider_keywords = ["pasajero", "viaje", "espera", "llegó", "me cobr"]
        
        role = "unknown"
        if any(kw in text_lower for kw in driver_keywords):
            role = "driver"
        elif any(kw in text_lower for kw in rider_keywords):
            role = "rider"
        
        # Sentiment based on rating
        if rating >= 4:
            sentiment = "positive"
        elif rating <= 2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "role": role,
            "categories": ["other"],
            "sentiment": sentiment,
            "key_topics": [],
        }
    
    def _fallback_release_classification(self, text: str) -> dict:
        """Simple rule-based fallback when AI is unavailable"""
        text_lower = text.lower() if text else ""
        
        # Simple significance detection
        if any(kw in text_lower for kw in ["new", "nuevo", "feature", "función"]):
            significance = "major"
        elif any(kw in text_lower for kw in ["fix", "bug", "error", "crash"]):
            significance = "bugfix"
        else:
            significance = "minor"
        
        return {
            "categories": ["other"],
            "summary_ru": "Обновление приложения",
            "significance": significance,
        }
