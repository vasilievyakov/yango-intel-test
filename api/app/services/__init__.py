from app.services.classifier import ClassifierService
from app.services.digest_generator import DigestGeneratorService
from app.services.webhook_processor import WebhookProcessor
from app.services.news_scraper import NewsScraperService

__all__ = [
    "ClassifierService",
    "DigestGeneratorService",
    "WebhookProcessor",
    "NewsScraperService",
]

