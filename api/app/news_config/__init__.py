"""News monitoring configuration package"""

from app.news_config.news_sources import (
    PERU_NEWS_SOURCES,
    COMPETITORS,
    NEWS_CATEGORIES,
    PARALLEL_SEARCH_PROMPT,
    NEWS_ITEM_SCHEMA,
    Competitor,
    NewsCategory,
    get_competitor_by_slug,
    get_all_competitor_keywords,
    build_site_filter,
    generate_search_queries,
)

__all__ = [
    "PERU_NEWS_SOURCES",
    "COMPETITORS",
    "NEWS_CATEGORIES",
    "PARALLEL_SEARCH_PROMPT",
    "NEWS_ITEM_SCHEMA",
    "Competitor",
    "NewsCategory",
    "get_competitor_by_slug",
    "get_all_competitor_keywords",
    "build_site_filter",
    "generate_search_queries",
]

