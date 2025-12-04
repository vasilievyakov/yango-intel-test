"""
Configuration for Peru Market News Monitoring

This file contains:
- Target news sources for Peru market
- Competitor definitions with keywords
- Search query templates
- Category mappings
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


# =============================================================================
# TARGET NEWS SOURCES (Peru Market)
# =============================================================================

PERU_NEWS_SOURCES: List[str] = [
    # Основные новостные порталы
    "apnoticias.pe",
    "agenciaperu.net",
    "elperuano.pe",
    "panamericana.pe",
    "noticiasperu.pe",
    "gacetaperutv.pe",
    
    # Бизнес и экономика
    "linkempresarial.pe",
    "accesoperu.com",
    "serperuano.com",
    "mercadonegro.pe",
    "revistaeconomia.com",
    "jcmagazine.com",
    
    # Автомобили и транспорт
    "sobreruedas.news",
    "dracing.pe",
    
    # Общие новости
    "nteve.com",
    "comunidaria.com",
    "entrenotas20.com",
    "viajandoporperu.com",
    "radionuevaq.pe",
]


# =============================================================================
# COMPETITORS
# =============================================================================

@dataclass
class Competitor:
    name: str
    slug: str
    keywords: List[str]
    aliases: List[str]


COMPETITORS: List[Competitor] = [
    Competitor(
        name="Yango",
        slug="yango",
        keywords=["Yango", "Yango Pro", "Yango Delivery", "Yango Ride"],
        aliases=["yango", "yango peru"]
    ),
    Competitor(
        name="inDrive",
        slug="indrive",
        keywords=["inDrive", "InDrive", "Indrive", "Kuzoba"],
        aliases=["indrive", "in drive", "in-drive", "kuzoba"]
    ),
    Competitor(
        name="Uber",
        slug="uber",
        keywords=["Uber", "Uber Tuk", "Uber Go", "Uber Moto"],
        aliases=["uber", "uber peru"]
    ),
    Competitor(
        name="DiDi",
        slug="didi",
        keywords=["DiDi", "Didi", "DiDi Food"],
        aliases=["didi", "99"]
    ),
    Competitor(
        name="Cabify",
        slug="cabify",
        keywords=["Cabify", "Cabify Ads"],
        aliases=["cabify"]
    ),
    Competitor(
        name="Rappi",
        slug="rappi",
        keywords=["Rappi"],
        aliases=["rappi"]
    ),
    Competitor(
        name="Bolt",
        slug="bolt",
        keywords=["Bolt"],
        aliases=["bolt"]
    ),
]


# =============================================================================
# NEWS CATEGORIES
# =============================================================================

@dataclass
class NewsCategory:
    name: str
    slug: str
    keywords_es: List[str]
    keywords_en: List[str]


NEWS_CATEGORIES: List[NewsCategory] = [
    NewsCategory(
        name="Product Feature",
        slug="product_feature",
        keywords_es=[
            "nueva función", "nueva opción", "actualización", "nueva versión",
            "SuperApp", "algoritmo", "inteligencia artificial", "IA",
            "seguridad", "verificación", "multimodalidad", "nueva herramienta"
        ],
        keywords_en=["new feature", "update", "release", "AI", "safety", "security"]
    ),
    NewsCategory(
        name="Promo & Incentives",
        slug="promo_incentives",
        keywords_es=[
            "promoción", "descuento", "cupón", "código promocional",
            "bono", "bonificación", "incentivo", "sorteo", "premios",
            "oferta", "gratis", "beneficio"
        ],
        keywords_en=["promo", "discount", "coupon", "bonus", "incentive", "free"]
    ),
    NewsCategory(
        name="Commercial Terms",
        slug="commercial_terms",
        keywords_es=[
            "comisión", "ganancias", "tarifa", "precio",
            "financiamiento", "crédito", "alquiler venta", "préstamo",
            "pago", "cobro"
        ],
        keywords_en=["commission", "earnings", "fare", "price", "financing", "payment"]
    ),
    NewsCategory(
        name="Safety & Incidents",
        slug="safety",
        keywords_es=[
            "robos", "asaltos", "extorsión", "accidente",
            "seguridad", "denuncia", "crimen"
        ],
        keywords_en=["robbery", "assault", "accident", "safety", "crime"]
    ),
    NewsCategory(
        name="Regulation",
        slug="regulation",
        keywords_es=[
            "MTC", "ATU", "regulación", "ley", "normativa",
            "multa", "sanción", "permiso", "licencia"
        ],
        keywords_en=["regulation", "law", "fine", "permit", "license"]
    ),
    NewsCategory(
        name="Labor & Strikes",
        slug="labor",
        keywords_es=[
            "paro", "huelga", "protesta", "manifestación",
            "sindicato", "trabajadores", "conductores"
        ],
        keywords_en=["strike", "protest", "union", "workers", "drivers"]
    ),
    NewsCategory(
        name="General",
        slug="general",
        keywords_es=["taxi", "aplicativo", "transporte", "movilidad"],
        keywords_en=["taxi", "app", "transport", "mobility"]
    ),
]


# =============================================================================
# SEARCH QUERY TEMPLATES
# =============================================================================

# Формат запросов для поиска по конкурентам
SEARCH_QUERY_TEMPLATES = {
    # Поиск по конкретному конкуренту
    "competitor_general": "{competitor} Peru noticias {year}",
    "competitor_feature": "{competitor} Peru nueva función actualización {year}",
    "competitor_promo": "{competitor} Peru promoción descuento bono {year}",
    "competitor_drivers": "{competitor} Peru conductores comisión ganancias {year}",
    "competitor_safety": "{competitor} Peru seguridad robos {year}",
    
    # Общие запросы по рынку
    "market_regulation": "taxi aplicativo Peru regulación ATU MTC {year}",
    "market_strikes": "paro huelga conductores aplicativo Peru {year}",
    "market_competition": "Uber inDrive Didi competencia Peru {year}",
}


# =============================================================================
# PREDEFINED SEARCH QUERIES (for automatic data collection)
# =============================================================================

# Эти запросы выполняются автоматически при нажатии кнопки "Обновить данные"
PREDEFINED_QUERIES: List[str] = [
    # Конкуренты + промо/новости
    "Uber Peru promociones descuentos noticias 2024 2025",
    "inDrive Peru promociones conductores noticias 2024 2025",
    "DiDi Peru promociones descuentos noticias 2024 2025",
    "Cabify Peru noticias promociones 2024 2025",
    "Yango Peru noticias promociones 2024 2025",
    
    # Рыночные новости
    "taxi aplicativo Peru regulación ATU MTC 2024 2025",
    "Uber inDrive DiDi competencia Peru Lima 2024",
    
    # Изменения тарифов и комиссий  
    "Uber inDrive DiDi comisión conductores Peru 2024",
    
    # Безопасность
    "taxi aplicativo seguridad robos Peru Lima 2024",
]


def get_predefined_queries() -> List[str]:
    """Get list of predefined search queries for automatic collection"""
    return PREDEFINED_QUERIES


# =============================================================================
# PARALLEL AI SEARCH PROMPT
# =============================================================================

PARALLEL_SEARCH_PROMPT = """# Role
Ты — AI-агент по продуктовой и рыночной разведке (Product & Market Intelligence). 
Твоя задача — искать и анализировать новости о сервисах такси и доставки в Перу.

# Objective
Найди актуальные новости по запросу, фокусируясь на:
1. Новых продуктовых фичах и обновлениях
2. Промо-акциях и условиях для водителей/пассажиров
3. Изменениях тарифов и комиссий
4. Регуляторных изменениях
5. Инцидентах безопасности

# Target Sources (приоритетные)
{sources}

# Search Query
{query}

# Output Requirements
Для каждой найденной новости предоставь:
- URL источника
- Дату публикации
- Заголовок
- Краткое описание (2-3 предложения)
- Упомянутые конкуренты
- Категория (Product Feature / Promo & Incentives / Commercial Terms / Safety / Regulation / Labor / General)

Игнорируй:
- Новости старше 30 дней
- Нерелевантные результаты (не связанные с ride-hailing/delivery)
- Дубликаты одной и той же новости
"""


# =============================================================================
# OUTPUT JSON SCHEMA
# =============================================================================

NEWS_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "unique_id": {
            "type": "string",
            "description": "MD5 hash of source URL for deduplication"
        },
        "date": {
            "type": "string",
            "format": "date",
            "description": "Publication date (YYYY-MM-DD)"
        },
        "source_url": {
            "type": "string",
            "format": "uri",
            "description": "URL of the news article"
        },
        "source_name": {
            "type": "string",
            "description": "Name of the news source"
        },
        "title": {
            "type": "string",
            "description": "Original title of the article"
        },
        "competitor": {
            "type": "string",
            "enum": ["Yango", "inDrive", "Uber", "DiDi", "Cabify", "Rappi", "Bolt", "Multiple", "None"],
            "description": "Primary competitor mentioned"
        },
        "category": {
            "type": "string",
            "enum": ["Product Feature", "Promo & Incentives", "Commercial Terms", "Safety", "Regulation", "Labor", "General"],
            "description": "News category"
        },
        "status": {
            "type": "string",
            "enum": ["New", "Update"],
            "description": "Whether this is new info or update to existing story"
        },
        "summary_ru": {
            "type": "string",
            "description": "Brief summary in Russian (2-3 sentences)"
        },
        "details": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string"},
                "promo_conditions": {"type": "string"},
                "target_audience": {
                    "type": "string",
                    "enum": ["Drivers", "Riders", "B2B", "All"]
                }
            }
        },
        "actionable_insight": {
            "type": "string",
            "description": "Why is this important? (Threat, Opportunity, Market Change)"
        }
    },
    "required": ["unique_id", "date", "source_url", "title", "competitor", "category", "summary_ru"]
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_competitor_by_slug(slug: str) -> Optional[Competitor]:
    """Get competitor by slug"""
    for comp in COMPETITORS:
        if comp.slug == slug:
            return comp
    return None


def get_all_competitor_keywords() -> List[str]:
    """Get flat list of all competitor keywords"""
    keywords = []
    for comp in COMPETITORS:
        keywords.extend(comp.keywords)
    return keywords


def build_site_filter(sources: Optional[List[str]] = None) -> str:
    """Build site: filter for search query"""
    sites = sources or PERU_NEWS_SOURCES
    return " OR ".join([f"site:{s}" for s in sites[:5]])  # Limit to 5 for query length


def generate_search_queries(competitor_slug: Optional[str] = None, category: Optional[str] = None) -> List[str]:
    """Generate list of search queries based on filters"""
    from datetime import datetime
    year = datetime.now().year
    queries = []
    
    if competitor_slug:
        comp = get_competitor_by_slug(competitor_slug)
        if comp:
            for template_key, template in SEARCH_QUERY_TEMPLATES.items():
                if template_key.startswith("competitor_"):
                    queries.append(template.format(competitor=comp.name, year=year))
    else:
        # General market queries
        for template_key, template in SEARCH_QUERY_TEMPLATES.items():
            if template_key.startswith("market_"):
                queries.append(template.format(year=year))
    
    return queries

