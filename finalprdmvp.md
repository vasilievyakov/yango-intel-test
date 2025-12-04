# Yango Competitive Intelligence — Полная техническая архитектура

## Оглавление

1. [Обзор системы](#1-обзор-системы)
2. [Компоненты и их роли](#2-компоненты-и-их-роли)
3. [Поток данных](#3-поток-данных)
4. [Octoparse: настройка и интеграция](#4-octoparse-настройка-и-интеграция)
5. [Backend API (FastAPI)](#5-backend-api-fastapi)
6. [База данных](#6-база-данных)
7. [AI-модуль (Claude Opus 4.5)](#7-ai-модуль-claude-opus-45)
8. [Frontend (Next.js)](#8-frontend-nextjs)
9. [Авторизация (Clerk)](#9-авторизация-clerk)
10. [Deployment](#10-deployment)
11. [Мониторинг и логирование](#11-мониторинг-и-логирование)
12. [Расширение после MVP](#12-расширение-после-mvp)

---

## 1. Обзор системы

### 1.1 Что делает система

Yango Competitive Intelligence собирает, классифицирует и визуализирует данные о конкурентах на рынке ride-hailing в Перу. Система отслеживает:

- **Тарифы** — комиссии, базовые ставки, стоимость за км/мин
- **Промоакции** — скидки, бонусы, реферальные программы
- **Релизы приложений** — версии, release notes, новые фичи
- **Отзывы пользователей** — рейтинги, тексты, тренды

### 1.2 Архитектура высокого уровня

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              ИСТОЧНИКИ ДАННЫХ                           │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────┤
│  InDriver   │    Didi     │    Uber     │   Cabify    │   App Stores    │
│   Website   │   Website   │   Website   │   Website   │   iOS/Android   │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴────────┬────────┘
       │             │             │             │               │
       └─────────────┴─────────────┴─────────────┴───────────────┘
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │       OCTOPARSE         │
                     │   (Standard Plan)       │
                     │                         │
                     │  • 8 задач парсинга     │
                     │  • Расписание/ручной    │
                     │  • Webhook → Backend    │
                     └───────────┬─────────────┘
                                 │
                                 │ POST /api/webhooks/octoparse
                                 │ (JSON payload)
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         RENDER (Backend)                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Application                         │  │
│  │                                                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │  │
│  │  │  Webhooks   │  │    API      │  │     AI Service          │   │  │
│  │  │  Handler    │  │   Routes    │  │  (Claude Opus 4.5)      │   │  │
│  │  │             │  │             │  │                         │   │  │
│  │  │ • Validate  │  │ • /tariffs  │  │ • classify_review()     │   │  │
│  │  │ • Transform │  │ • /promos   │  │ • classify_release()    │   │  │
│  │  │ • Store     │  │ • /releases │  │ • generate_digest()     │   │  │
│  │  │ • Classify  │  │ • /reviews  │  │ • detect_role()         │   │  │
│  │  └──────┬──────┘  │ • /digest   │  └───────────▲─────────────┘   │  │
│  │         │         └──────┬──────┘              │                 │  │
│  │         │                │                     │                 │  │
│  │         ▼                ▼                     │                 │  │
│  │  ┌───────────────────────────────────────────────────────────┐   │  │
│  │  │                    SQLAlchemy ORM                         │   │  │
│  │  └───────────────────────────┬───────────────────────────────┘   │  │
│  └──────────────────────────────┼───────────────────────────────────┘  │
│                                 │                                      │
│  ┌──────────────────────────────▼───────────────────────────────────┐  │
│  │                     PostgreSQL Database                          │  │
│  │                                                                  │  │
│  │  competitors │ tariffs │ promos │ releases │ reviews │ logs      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ REST API (JSON)
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         VERCEL (Frontend)                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Next.js Application                          │  │
│  │                                                                  │  │
│  │  ┌─────────────┐  ┌─────────────────────────────────────────┐    │  │
│  │  │   Clerk     │  │              Pages                      │    │  │
│  │  │   Auth      │  │                                         │    │  │
│  │  │             │  │  • /dashboard      — Обзор              │    │  │
│  │  │ • Sign In   │  │  • /tariffs        — Сравнение тарифов  │    │  │
│  │  │ • Sign Up   │  │  • /promos         — Промоакции         │    │  │
│  │  │ • Protect   │  │  • /releases       — Релизы приложений  │    │  │
│  │  │   Routes    │  │  • /reviews        — Анализ отзывов     │    │  │
│  │  │             │  │  • /digest         — Генерация отчётов  │    │  │
│  │  └─────────────┘  │  • /collection     — Управление сбором  │    │  │
│  │                   └─────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                     ┌─────────────────────────┐
                     │        Браузер          │
                     │    (Аналитик Yango)     │
                     └─────────────────────────┘
```

---

## 2. Компоненты и их роли

### 2.1 Octoparse (Standard Plan)

**Роль:** Сбор сырых данных с веб-страниц конкурентов и магазинов приложений.

**Что делает:**
- Загружает страницы (включая JS-rendered)
- Извлекает данные по настроенным правилам
- Отправляет результаты на backend через webhook

**Ограничения Standard плана:**
- 10 одновременных задач
- Cloud extraction (не локальный)
- Webhooks доступны ✓
- API доступен ✓

### 2.2 FastAPI Backend (Render)

**Роль:** Центральный узел обработки данных.

**Что делает:**
- Принимает данные от Octoparse
- Валидирует и трансформирует
- Сохраняет в PostgreSQL
- Вызывает Claude для классификации
- Отдаёт данные на фронтенд через REST API

### 2.3 PostgreSQL (Render)

**Роль:** Хранение всех данных системы.

**Что хранит:**
- Справочник конкурентов
- Исторические данные тарифов
- Промоакции
- Релизы приложений
- Отзывы пользователей
- Логи сбора данных

### 2.4 Claude Opus 4.5 (Anthropic API)

**Роль:** Интеллектуальная обработка текстов.

**Что делает:**
- Классифицирует отзывы по категориям
- Определяет роль автора (водитель/пассажир)
- Классифицирует release notes
- Генерирует еженедельные дайджесты
- Выявляет тренды в отзывах

### 2.5 Next.js Frontend (Vercel)

**Роль:** Пользовательский интерфейс.

**Что делает:**
- Отображает дашборд с ключевыми метриками
- Показывает сравнительные таблицы
- Позволяет фильтровать и экспортировать данные
- Генерирует и редактирует дайджесты

### 2.6 Clerk

**Роль:** Аутентификация и авторизация.

**Что делает:**
- Управляет пользователями
- Защищает страницы и API
- Предоставляет UI для входа/регистрации

---

## 3. Поток данных

### 3.1 Сценарий: Сбор данных с сайта конкурента

```
Шаг 1: Запуск задачи Octoparse
┌─────────────────────────────────────────────────────────────┐
│ Аналитик запускает задачу вручную в интерфейсе Octoparse   │
│ (или срабатывает расписание)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 2: Octoparse извлекает данные
┌─────────────────────────────────────────────────────────────┐
│ Задача: uber-driver-pe                                      │
│ URL: https://www.uber.com/pe/es/drive                       │
│                                                             │
│ Извлечённые данные:                                         │
│ {                                                           │
│   "commission": "25%",                                      │
│   "signup_bonus": "S/200",                                  │
│   "referral_bonus": "S/50",                                 │
│   "requirements": ["DNI vigente", "Licencia A-II", ...]     │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 3: Webhook отправляет данные на backend
┌─────────────────────────────────────────────────────────────┐
│ POST https://yango-api.onrender.com/api/webhooks/octoparse  │
│                                                             │
│ Headers:                                                    │
│   X-Octoparse-Signature: sha256=abc123...                   │
│   Content-Type: application/json                            │
│                                                             │
│ Body:                                                       │
│ {                                                           │
│   "taskId": "task_uber_driver_pe",                          │
│   "taskName": "uber-driver-pe",                             │
│   "dataList": [                                             │
│     {                                                       │
│       "commission": "25%",                                  │
│       "signup_bonus": "S/200",                              │
│       ...                                                   │
│     }                                                       │
│   ],                                                        │
│   "executedAt": "2025-01-15T10:30:00Z"                      │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 4: Backend обрабатывает данные
┌─────────────────────────────────────────────────────────────┐
│ WebhookHandler:                                             │
│                                                             │
│ 1. Верификация подписи (HMAC SHA256)                        │
│ 2. Определение типа данных по taskName:                     │
│    "uber-driver-pe" → driver_tariffs                        │
│ 3. Трансформация:                                           │
│    "25%" → 25.0 (float)                                     │
│    "S/200" → 200.0 (float)                                  │
│ 4. Валидация:                                               │
│    commission_rate: 0-100 ✓                                 │
│    signup_bonus: > 0 ✓                                      │
│ 5. Поиск competitor_id по taskName                          │
│ 6. Пометка предыдущей записи: is_latest = FALSE             │
│ 7. INSERT новой записи в driver_tariffs                     │
│ 8. INSERT в collection_logs (status: success)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 5: Данные в базе
┌─────────────────────────────────────────────────────────────┐
│ driver_tariffs:                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ id          │ abc-123-...                               │ │
│ │ competitor  │ uuid-uber                                 │ │
│ │ commission  │ 25.00                                     │ │
│ │ signup_bonus│ 200.00                                    │ │
│ │ is_latest   │ TRUE                                      │ │
│ │ collected_at│ 2025-01-15 10:30:00                       │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Сценарий: Сбор и классификация отзывов

```
Шаг 1-3: Аналогично предыдущему (Octoparse → Webhook → Backend)

Шаг 4: Backend получает отзывы
┌─────────────────────────────────────────────────────────────┐
│ Входящие данные от Octoparse:                               │
│ {                                                           │
│   "reviews": [                                              │
│     {                                                       │
│       "external_id": "gp_review_12345",                     │
│       "author": "María G.",                                 │
│       "rating": 2,                                          │
│       "text": "Muy mala experiencia como conductor...",     │
│       "date": "2025-01-14",                                 │
│       "app_version": "5.12.3"                               │
│     },                                                      │
│     ...                                                     │
│   ]                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 5: Дедупликация
┌─────────────────────────────────────────────────────────────┐
│ SELECT id FROM reviews WHERE external_id = 'gp_review_12345'│
│                                                             │
│ Результат: NULL → отзыв новый, продолжаем                   │
│ (если бы нашёлся — пропускаем)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 6: AI-классификация (Claude Opus 4.5)
┌─────────────────────────────────────────────────────────────┐
│ POST https://api.anthropic.com/v1/messages                  │
│                                                             │
│ System: "You are a review classifier for ride-hailing apps" │
│                                                             │
│ User:                                                       │
│ """                                                         │
│ Classify this app review. Respond in JSON only.             │
│                                                             │
│ Review: "Muy mala experiencia como conductor. La app        │
│ se congela cuando acepto viajes y pierdo clientes.          │
│ La comisión del 25% es muy alta."                           │
│ Rating: 2/5                                                 │
│                                                             │
│ Output format:                                              │
│ {                                                           │
│   "role": "driver" | "rider" | "unknown",                   │
│   "categories": ["pricing", "ux_ui", ...],                  │
│   "sentiment": "positive" | "neutral" | "negative",         │
│   "key_topics": ["string"]                                  │
│ }                                                           │
│ """                                                         │
│                                                             │
│ Response:                                                   │
│ {                                                           │
│   "role": "driver",                                         │
│   "categories": ["ux_ui", "pricing", "driver_exp"],         │
│   "sentiment": "negative",                                  │
│   "key_topics": ["app freezing", "high commission"]         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 7: Сохранение в базу
┌─────────────────────────────────────────────────────────────┐
│ INSERT INTO reviews (                                       │
│   external_id, competitor_id, platform, author, rating,     │
│   text, review_date, app_version, language,                 │
│   role, sentiment, categories                               │
│ ) VALUES (                                                  │
│   'gp_review_12345', 'uuid-indriver', 'android',            │
│   'María G.', 2, 'Muy mala experiencia...', '2025-01-14',   │
│   '5.12.3', 'es', 'driver', 'negative',                     │
│   ARRAY['ux_ui', 'pricing', 'driver_exp']                   │
│ )                                                           │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Сценарий: Просмотр данных на фронтенде

```
Шаг 1: Пользователь открывает страницу
┌─────────────────────────────────────────────────────────────┐
│ Браузер: GET https://yango-intel.vercel.app/tariffs         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 2: Clerk проверяет авторизацию
┌─────────────────────────────────────────────────────────────┐
│ middleware.ts:                                              │
│                                                             │
│ const { userId } = auth();                                  │
│                                                             │
│ if (!userId) {                                              │
│   redirect('/sign-in');  // → на страницу входа             │
│ }                                                           │
│                                                             │
│ // userId существует → продолжаем                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 3: Next.js запрашивает данные у backend
┌─────────────────────────────────────────────────────────────┐
│ // app/tariffs/page.tsx (Server Component)                  │
│                                                             │
│ const { getToken } = auth();                                │
│ const token = await getToken();                             │
│                                                             │
│ const response = await fetch(                               │
│   'https://yango-api.onrender.com/api/tariffs/comparison',  │
│   {                                                         │
│     headers: {                                              │
│       'Authorization': `Bearer ${token}`                    │
│     }                                                       │
│   }                                                         │
│ );                                                          │
│                                                             │
│ const data = await response.json();                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 4: Backend обрабатывает запрос
┌─────────────────────────────────────────────────────────────┐
│ @app.get("/api/tariffs/comparison")                         │
│ async def get_tariff_comparison(                            │
│     user: User = Depends(verify_clerk_token)                │
│ ):                                                          │
│     # 1. Верификация JWT токена от Clerk                    │
│     # 2. Запрос к БД                                        │
│                                                             │
│     query = """                                             │
│         SELECT c.name, dt.commission_rate, dt.signup_bonus, │
│                rt.base_fare, rt.per_km_rate                 │
│         FROM competitors c                                  │
│         LEFT JOIN driver_tariffs dt                         │
│           ON dt.competitor_id = c.id AND dt.is_latest       │
│         LEFT JOIN rider_tariffs rt                          │
│           ON rt.competitor_id = c.id AND rt.is_latest       │
│     """                                                     │
│                                                             │
│     return results                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 5: Рендеринг на фронтенде
┌─────────────────────────────────────────────────────────────┐
│ Response JSON:                                              │
│ {                                                           │
│   "comparison": [                                           │
│     {                                                       │
│       "competitor": "Uber",                                 │
│       "driver": { "commission": 25, "bonus": 200 },         │
│       "rider": { "base_fare": 4.5, "per_km": 1.8 }          │
│     },                                                      │
│     {                                                       │
│       "competitor": "InDriver",                             │
│       "driver": { "commission": 10, "bonus": 150 },         │
│       "rider": { "base_fare": 3.5, "per_km": 1.2 }          │
│     },                                                      │
│     ...                                                     │
│   ]                                                         │
│ }                                                           │
│                                                             │
│ → Таблица рендерится в браузере                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Сценарий: Генерация дайджеста

```
Шаг 1: Пользователь нажимает "Сгенерировать дайджест"
┌─────────────────────────────────────────────────────────────┐
│ Frontend: POST /api/digest/generate                         │
│ Body: { "period": "week", "end_date": "2025-01-15" }        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 2: Backend собирает данные за период
┌─────────────────────────────────────────────────────────────┐
│ DigestService.collect_period_data():                        │
│                                                             │
│ 1. Релизы за неделю:                                        │
│    SELECT * FROM releases                                   │
│    WHERE release_date BETWEEN '2025-01-08' AND '2025-01-15' │
│                                                             │
│ 2. Изменения тарифов:                                       │
│    Сравнить текущие vs предыдущие записи                    │
│                                                             │
│ 3. Активные промо:                                          │
│    SELECT * FROM promos                                     │
│    WHERE valid_until >= CURRENT_DATE                        │
│                                                             │
│ 4. Тренды отзывов:                                          │
│    SELECT competitor_id, sentiment, COUNT(*)                │
│    FROM reviews                                             │
│    WHERE review_date BETWEEN ... GROUP BY ...               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 3: Claude генерирует текст дайджеста
┌─────────────────────────────────────────────────────────────┐
│ POST https://api.anthropic.com/v1/messages                  │
│                                                             │
│ System: "You are a competitive intelligence analyst..."     │
│                                                             │
│ User:                                                       │
│ """                                                         │
│ Generate a weekly digest in Russian based on this data:     │
│                                                             │
│ NEW RELEASES:                                               │
│ - InDriver v5.12.3 (iOS): "Улучшена стабильность..."        │
│ - Uber v4.521 (Android): "Новая функция безопасности..."    │
│                                                             │
│ TARIFF CHANGES:                                             │
│ - Didi: commission 18% → 15% (снижение)                     │
│                                                             │
│ ACTIVE PROMOS:                                              │
│ - InDriver: 30% off first 3 rides                           │
│ - Cabify: Free ride up to S/15                              │
│                                                             │
│ REVIEW TRENDS:                                              │
│ - InDriver: 45 negative (↑20% vs last week), top: "wait"    │
│ - Uber: 30 positive (↑15%), top: "safety"                   │
│                                                             │
│ Format as markdown with sections.                           │
│ """                                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Шаг 4: Возврат сгенерированного дайджеста
┌─────────────────────────────────────────────────────────────┐
│ Response:                                                   │
│ {                                                           │
│   "digest": {                                               │
│     "period": "2025-01-08 — 2025-01-15",                    │
│     "content": "# Дайджест за неделю\n\n## Релизы\n...",    │
│     "generated_at": "2025-01-15T14:30:00Z"                  │
│   }                                                         │
│ }                                                           │
│                                                             │
│ → Пользователь видит preview, может редактировать           │
│ → Может экспортировать в PDF/Markdown                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Octoparse: настройка и интеграция

### 4.1 Задачи парсинга

Создайте 12 задач в Octoparse:

| # | Название задачи | URL | Тип данных |
|---|-----------------|-----|------------|
| 1 | `indriver-driver-pe` | indriver.com/pe/driver | driver_tariffs |
| 2 | `indriver-rider-pe` | indriver.com/pe | rider_tariffs |
| 3 | `uber-driver-pe` | uber.com/pe/es/drive | driver_tariffs |
| 4 | `uber-rider-pe` | uber.com/pe/es | rider_tariffs |
| 5 | `didi-driver-pe` | web.didiglobal.com/pe/driver | driver_tariffs |
| 6 | `didi-rider-pe` | web.didiglobal.com/pe | rider_tariffs |
| 7 | `cabify-driver-pe` | cabify.com/pe/driver | driver_tariffs |
| 8 | `cabify-rider-pe` | cabify.com/pe | rider_tariffs |
| 9 | `appstore-indriver` | apps.apple.com/pe/app/id1018263498 | reviews + releases |
| 10 | `appstore-uber` | apps.apple.com/pe/app/id368677368 | reviews + releases |
| 11 | `playstore-indriver` | play.google.com/store/apps/details?id=sinet.startup.inDriver | reviews + releases |
| 12 | `playstore-uber` | play.google.com/store/apps/details?id=com.ubercab | reviews + releases |

### 4.2 Структура извлекаемых данных

**Задачи driver-*:**
```json
{
  "fields": [
    { "name": "commission", "selector": "CSS/XPath для комиссии" },
    { "name": "signup_bonus", "selector": "..." },
    { "name": "referral_bonus", "selector": "..." },
    { "name": "requirements", "selector": "...", "type": "list" },
    { "name": "benefits", "selector": "...", "type": "list" }
  ]
}
```

**Задачи rider-*:**
```json
{
  "fields": [
    { "name": "base_fare", "selector": "..." },
    { "name": "per_km_rate", "selector": "..." },
    { "name": "per_min_rate", "selector": "..." },
    { "name": "promo_codes", "selector": "...", "type": "list" }
  ]
}
```

**Задачи appstore-* и playstore-*:**
```json
{
  "fields": [
    { "name": "app_version", "selector": "..." },
    { "name": "rating", "selector": "..." },
    { "name": "rating_count", "selector": "..." },
    { "name": "release_notes", "selector": "..." },
    { "name": "reviews", "selector": "...", "type": "list", "subfields": [
      { "name": "author", "selector": "..." },
      { "name": "rating", "selector": "..." },
      { "name": "text", "selector": "..." },
      { "name": "date", "selector": "..." }
    ]}
  ]
}
```

### 4.3 Настройка Webhook

В каждой задаче Octoparse → Settings → Data Export → Webhook:

```
URL: https://yango-api.onrender.com/api/webhooks/octoparse
Method: POST
Headers:
  X-Webhook-Secret: {ваш_секретный_ключ}
Format: JSON
```

### 4.4 Формат данных от Octoparse

Octoparse отправляет данные в следующем формате:

```json
{
  "taskId": "abc123",
  "taskName": "uber-driver-pe",
  "taskGroup": "Yango Intel",
  "dataCount": 1,
  "dataList": [
    {
      "commission": "25%",
      "signup_bonus": "S/200",
      "referral_bonus": "S/50",
      "requirements": "DNI vigente|Licencia A-II|SOAT vigente",
      "benefits": "Ganancias flexibles|Bonos semanales"
    }
  ],
  "exportedAt": "2025-01-15T10:30:00Z"
}
```

---

## 5. Backend API (FastAPI)

### 5.1 Структура проекта

```
api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, lifespan
│   ├── config.py               # Settings (Pydantic BaseSettings)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (DB session, auth)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── webhooks.py     # POST /webhooks/octoparse
│   │       ├── tariffs.py      # GET /tariffs/*
│   │       ├── promos.py       # GET /promos/*
│   │       ├── releases.py     # GET /releases/*
│   │       ├── reviews.py      # GET /reviews/*
│   │       ├── digest.py       # GET/POST /digest/*
│   │       └── collection.py   # GET/POST /collection/*
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── competitor.py
│   │   ├── tariff.py
│   │   ├── promo.py
│   │   ├── release.py
│   │   ├── review.py
│   │   └── collection_log.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── webhook.py          # Pydantic models for Octoparse
│   │   ├── tariff.py
│   │   ├── review.py
│   │   └── digest.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── webhook_processor.py    # Обработка данных от Octoparse
│   │   ├── classifier.py           # Claude API для классификации
│   │   ├── digest_generator.py     # Генерация дайджестов
│   │   └── change_detector.py      # Обнаружение изменений
│   │
│   └── db/
│       ├── __init__.py
│       ├── session.py          # SQLAlchemy engine, SessionLocal
│       └── base.py             # Base model
│
├── alembic/                    # Миграции
│   ├── versions/
│   └── env.py
│
├── requirements.txt
├── alembic.ini
└── Dockerfile
```

### 5.2 Ключевые endpoints

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API ENDPOINTS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  WEBHOOKS (публичные, но с верификацией подписи)                        │
│  ─────────────────────────────────────────────────────────────────────  │
│  POST /api/webhooks/octoparse                                           │
│       Принимает данные от Octoparse                                     │
│       Headers: X-Webhook-Secret                                         │
│       Body: OctoparseWebhookPayload                                     │
│       → Возвращает: { "status": "ok", "processed": 5 }                  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TARIFFS (защищены Clerk JWT)                                           │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET /api/tariffs/comparison                                            │
│       Сравнительная таблица всех конкурентов                            │
│       Query: ?type=driver|rider                                         │
│       → Возвращает: TariffComparisonResponse                            │
│                                                                         │
│  GET /api/tariffs/history/{competitor_id}                               │
│       История изменений тарифов конкурента                              │
│       Query: ?from_date=...&to_date=...                                 │
│       → Возвращает: TariffHistoryResponse                               │
│                                                                         │
│  GET /api/tariffs/changes                                               │
│       Последние изменения тарифов                                       │
│       Query: ?days=7                                                    │
│       → Возвращает: TariffChangesResponse                               │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PROMOS                                                                 │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET /api/promos                                                        │
│       Список всех промоакций                                            │
│       Query: ?active_only=true&competitor_id=...                        │
│       → Возвращает: PromoListResponse                                   │
│                                                                         │
│  GET /api/promos/{id}                                                   │
│       Детали промоакции                                                 │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  RELEASES                                                               │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET /api/releases                                                      │
│       Список релизов                                                    │
│       Query: ?competitor_id=...&platform=ios|android&category=...       │
│       → Возвращает: ReleaseListResponse (paginated)                     │
│                                                                         │
│  GET /api/releases/timeline                                             │
│       Timeline релизов для визуализации                                 │
│       Query: ?days=30                                                   │
│       → Возвращает: ReleaseTimelineResponse                             │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REVIEWS                                                                │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET /api/reviews                                                       │
│       Список отзывов с фильтрами                                        │
│       Query: ?competitor_id=...&role=driver|rider                       │
│              &sentiment=positive|negative&category=...                  │
│       → Возвращает: ReviewListResponse (paginated)                      │
│                                                                         │
│  GET /api/reviews/stats                                                 │
│       Статистика по отзывам                                             │
│       Query: ?competitor_id=...&days=30                                 │
│       → Возвращает: ReviewStatsResponse                                 │
│                                                                         │
│  GET /api/reviews/trends                                                │
│       Тренды в отзывах (для дайджеста)                                  │
│       Query: ?days=7                                                    │
│       → Возвращает: ReviewTrendsResponse                                │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DIGEST                                                                 │
│  ─────────────────────────────────────────────────────────────────────  │
│  POST /api/digest/generate                                              │
│       Генерация нового дайджеста                                        │
│       Body: { "period": "week", "end_date": "2025-01-15" }              │
│       → Возвращает: DigestResponse (с markdown контентом)               │
│                                                                         │
│  GET /api/digest/history                                                │
│       История сгенерированных дайджестов                                │
│       → Возвращает: DigestHistoryResponse                               │
│                                                                         │
│  POST /api/digest/{id}/export                                           │
│       Экспорт дайджеста                                                 │
│       Body: { "format": "pdf" | "markdown" }                            │
│       → Возвращает: файл или URL                                        │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COLLECTION (управление сбором)                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET /api/collection/status                                             │
│       Статус последних сборов по всем источникам                        │
│       → Возвращает: CollectionStatusResponse                            │
│                                                                         │
│  GET /api/collection/logs                                               │
│       Детальные логи сбора                                              │
│       Query: ?status=failed&days=7                                      │
│       → Возвращает: CollectionLogsResponse                              │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DASHBOARD                                                              │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET /api/dashboard/summary                                             │
│       Агрегированные данные для главной страницы                        │
│       → Возвращает: {                                                   │
│           last_collection: "2025-01-15T10:30:00Z",                      │
│           new_releases_week: 5,                                         │
│           new_reviews_week: 127,                                        │
│           active_promos: { indriver: 2, uber: 1, ... },                 │
│           health_status: "healthy" | "warning" | "error"                │
│         }                                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Авторизация на backend

```python
# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

security = HTTPBearer()

CLERK_JWKS_URL = "https://{your-clerk-domain}/.well-known/jwks.json"

async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Верифицирует JWT токен от Clerk.
    Возвращает payload с user_id.
    """
    token = credentials.credentials
    
    try:
        # Получаем публичные ключи Clerk
        async with httpx.AsyncClient() as client:
            jwks = await client.get(CLERK_JWKS_URL)
        
        # Верифицируем токен (используем python-jose или PyJWT)
        payload = jwt.decode(
            token,
            jwks.json(),
            algorithms=["RS256"],
            audience="your-clerk-audience"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### 5.4 Webhook верификация

```python
# app/api/routes/webhooks.py

import hmac
import hashlib
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Верификация подписи webhook от Octoparse"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)

@router.post("/octoparse")
async def receive_octoparse_webhook(
    payload: OctoparseWebhookPayload,
    x_webhook_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    # Верификация
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Обработка
    processor = WebhookProcessor(db)
    result = await processor.process(payload)
    
    return {"status": "ok", "processed": result.count}
```

---

## 6. База данных

### 6.1 Полная схема

```sql
-- Расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum типы
CREATE TYPE platform_type AS ENUM ('ios', 'android');
CREATE TYPE user_role AS ENUM ('driver', 'rider', 'unknown');
CREATE TYPE sentiment_type AS ENUM ('positive', 'neutral', 'negative');
CREATE TYPE discount_type AS ENUM ('percent', 'fixed', 'free_ride');
CREATE TYPE collection_status AS ENUM ('success', 'partial', 'failed');
CREATE TYPE source_type AS ENUM ('website', 'appstore', 'playstore');

-- Конкуренты
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,  -- 'indriver', 'uber', etc.
    country VARCHAR(2) DEFAULT 'PE',
    website_driver VARCHAR(500),
    website_rider VARCHAR(500),
    appstore_id VARCHAR(100),
    playstore_id VARCHAR(100),
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Тарифы водителей
CREATE TABLE driver_tariffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    commission_rate DECIMAL(5,2),        -- Комиссия %
    min_fare DECIMAL(10,2),              -- Минимальная стоимость поездки
    signup_bonus DECIMAL(10,2),          -- Бонус за регистрацию
    referral_bonus DECIMAL(10,2),        -- Бонус за приглашение
    requirements TEXT[],                  -- Требования к водителю
    benefits TEXT[],                      -- Преимущества
    currency VARCHAR(3) DEFAULT 'PEN',
    source_url VARCHAR(500),
    is_latest BOOLEAN DEFAULT TRUE,
    collected_at TIMESTAMP DEFAULT NOW(),
    
    -- Индексы для быстрого поиска последних данных
    CONSTRAINT unique_latest_driver_tariff 
        UNIQUE (competitor_id, is_latest) 
        WHERE is_latest = TRUE
);

-- Тарифы пассажиров
CREATE TABLE rider_tariffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    service_type VARCHAR(50) DEFAULT 'standard',  -- economy, comfort, premium
    base_fare DECIMAL(10,2),
    per_km_rate DECIMAL(10,2),
    per_min_rate DECIMAL(10,2),
    booking_fee DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'PEN',
    source_url VARCHAR(500),
    is_latest BOOLEAN DEFAULT TRUE,
    collected_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_latest_rider_tariff 
        UNIQUE (competitor_id, service_type, is_latest) 
        WHERE is_latest = TRUE
);

-- Категории (справочник)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name_ru VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    name_es VARCHAR(100),
    keywords_es TEXT[],
    keywords_en TEXT[]
);

-- Промоакции
CREATE TABLE promos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    title VARCHAR(200),
    description TEXT,
    code VARCHAR(50),
    discount_type discount_type,
    discount_value DECIMAL(10,2),
    valid_from DATE,
    valid_until DATE,
    conditions TEXT,
    target_audience user_role DEFAULT 'rider',
    source_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    collected_at TIMESTAMP DEFAULT NOW()
);

-- Релизы приложений
CREATE TABLE releases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    platform platform_type NOT NULL,
    version VARCHAR(20) NOT NULL,
    release_date DATE,
    release_notes TEXT,
    rating DECIMAL(2,1),           -- Рейтинг на момент релиза
    rating_count INTEGER,          -- Количество оценок
    collected_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (competitor_id, platform, version)
);

-- Связь релизов и категорий
CREATE TABLE release_categories (
    release_id UUID REFERENCES releases(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    confidence DECIMAL(3,2) DEFAULT 1.0,  -- Уверенность классификации
    PRIMARY KEY (release_id, category_id)
);

-- Отзывы
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE NOT NULL,  -- ID из источника
    competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    platform platform_type NOT NULL,
    author VARCHAR(200),
    rating SMALLINT CHECK (rating >= 1 AND rating <= 5),
    text TEXT,
    review_date DATE,
    app_version VARCHAR(20),
    language VARCHAR(5) DEFAULT 'es',
    role user_role DEFAULT 'unknown',
    sentiment sentiment_type,
    collected_at TIMESTAMP DEFAULT NOW()
);

-- Связь отзывов и категорий
CREATE TABLE review_categories (
    review_id UUID REFERENCES reviews(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    PRIMARY KEY (review_id, category_id)
);

-- Логи сбора данных
CREATE TABLE collection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type source_type NOT NULL,
    competitor_id UUID REFERENCES competitors(id),
    task_name VARCHAR(100),          -- Название задачи Octoparse
    url VARCHAR(500),
    status collection_status NOT NULL,
    error_message TEXT,
    items_collected INTEGER DEFAULT 0,
    raw_payload JSONB,               -- Сырые данные для отладки
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT NOW()
);

-- Сгенерированные дайджесты
CREATE TABLE digests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    content TEXT NOT NULL,           -- Markdown контент
    metadata JSONB,                  -- Использованные данные
    created_by VARCHAR(100),         -- Clerk user ID
    created_at TIMESTAMP DEFAULT NOW()
);

-- Гипотезы
CREATE TABLE hypotheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    related_data JSONB,              -- Ссылки на релизы/отзывы/тарифы
    recommendation TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- active, validated, rejected
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ ИНДЕКСЫ ============

-- Для быстрого получения последних тарифов
CREATE INDEX idx_driver_tariffs_latest 
    ON driver_tariffs(competitor_id) 
    WHERE is_latest = TRUE;

CREATE INDEX idx_rider_tariffs_latest 
    ON rider_tariffs(competitor_id) 
    WHERE is_latest = TRUE;

-- Для фильтрации отзывов
CREATE INDEX idx_reviews_competitor ON reviews(competitor_id);
CREATE INDEX idx_reviews_date ON reviews(review_date DESC);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment);
CREATE INDEX idx_reviews_role ON reviews(role);
CREATE INDEX idx_reviews_platform ON reviews(platform);

-- Для релизов
CREATE INDEX idx_releases_date ON releases(release_date DESC);
CREATE INDEX idx_releases_competitor ON releases(competitor_id);

-- Для промо
CREATE INDEX idx_promos_active ON promos(valid_until) WHERE is_active = TRUE;

-- Для логов (очистка старых)
CREATE INDEX idx_collection_logs_date ON collection_logs(completed_at);

-- ============ НАЧАЛЬНЫЕ ДАННЫЕ ============

-- Конкуренты
INSERT INTO competitors (name, slug, website_driver, website_rider, appstore_id, playstore_id) VALUES
('InDriver', 'indriver', 'https://indriver.com/pe/driver', 'https://indriver.com/pe', 'id1018263498', 'sinet.startup.inDriver'),
('Didi', 'didi', 'https://web.didiglobal.com/pe/driver', 'https://web.didiglobal.com/pe', 'id1447432993', 'com.xiaojukeji.didi.global.customer'),
('Uber', 'uber', 'https://www.uber.com/pe/es/drive', 'https://www.uber.com/pe/es', 'id368677368', 'com.ubercab'),
('Cabify', 'cabify', 'https://cabify.com/pe/driver', 'https://cabify.com/pe', 'id476087442', 'com.cabify.rider');

-- Категории
INSERT INTO categories (slug, name_ru, name_en, name_es, keywords_es, keywords_en) VALUES
('pricing', 'Тарифы', 'Pricing', 'Tarifas', ARRAY['tarifa', 'precio', 'comisión', 'costo', 'cobro'], ARRAY['fare', 'price', 'commission', 'cost', 'fee']),
('ux_ui', 'UX/UI', 'UX/UI', 'UX/UI', ARRAY['diseño', 'interfaz', 'pantalla', 'botón', 'app', 'aplicación'], ARRAY['design', 'interface', 'screen', 'button', 'app', 'crash', 'bug']),
('safety', 'Безопасность', 'Safety', 'Seguridad', ARRAY['seguridad', 'verificación', 'SOS', 'emergencia'], ARRAY['safety', 'verification', 'SOS', 'emergency', 'secure']),
('driver_exp', 'Опыт водителя', 'Driver Experience', 'Experiencia conductor', ARRAY['conductor', 'ganancias', 'viajes', 'pasajeros'], ARRAY['driver', 'earnings', 'trips', 'passengers']),
('rider_exp', 'Опыт пассажира', 'Rider Experience', 'Experiencia pasajero', ARRAY['pasajero', 'viaje', 'espera', 'llegada'], ARRAY['rider', 'trip', 'wait', 'arrival', 'pickup']),
('promo', 'Промо', 'Promo', 'Promoción', ARRAY['descuento', 'promoción', 'código', 'gratis', 'oferta'], ARRAY['discount', 'promo', 'code', 'free', 'offer']),
('other', 'Другое', 'Other', 'Otro', ARRAY[], ARRAY[]);
```

### 6.2 Миграции (Alembic)

```bash
# Структура
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_hypotheses.py
│   └── ...
├── env.py
└── script.py.mako

# Команды
alembic upgrade head      # Применить все миграции
alembic revision -m "..."  # Создать новую миграцию
alembic downgrade -1      # Откатить последнюю
```

---

## 7. AI-модуль (Claude Opus 4.5)

### 7.1 Сервис классификации

```python
# app/services/classifier.py

from anthropic import Anthropic
from app.config import settings

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

REVIEW_CLASSIFICATION_PROMPT = """You are a classifier for ride-hailing app reviews in Peru.

Analyze the review and return ONLY a JSON object with these fields:
- role: "driver" | "rider" | "unknown"
- categories: array of applicable categories from: ["pricing", "ux_ui", "safety", "driver_exp", "rider_exp", "promo", "other"]
- sentiment: "positive" | "neutral" | "negative"
- key_topics: array of 1-3 main topics mentioned (in English, lowercase)

Role detection rules:
- "driver" if mentions: conducir, conductor, ganancias, comisión, mis pasajeros, mi carro
- "rider" if mentions: pedir viaje, esperar carro, chofer (as customer perspective)
- "unknown" if unclear

Review text: "{text}"
Rating: {rating}/5
Language: Spanish (Peru)

Respond with JSON only, no markdown formatting."""

RELEASE_CLASSIFICATION_PROMPT = """Classify this app release notes for a ride-hailing app.

Release notes: "{text}"

Return ONLY a JSON object with:
- categories: array from ["pricing", "ux_ui", "safety", "driver_exp", "rider_exp", "promo", "other"]
- summary: one sentence summary in Russian
- significance: "major" | "minor" | "bugfix"

Respond with JSON only."""


class ClassifierService:
    def __init__(self):
        self.client = client
        self.model = "claude-sonnet-4-5-20250929"  # Sonnet для классификации (дешевле)
    
    async def classify_review(self, text: str, rating: int) -> dict:
        """Классифицирует отзыв"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": REVIEW_CLASSIFICATION_PROMPT.format(
                    text=text,
                    rating=rating
                )
            }]
        )
        
        # Парсим JSON из ответа
        result = json.loads(response.content[0].text)
        return result
    
    async def classify_release(self, text: str) -> dict:
        """Классифицирует release notes"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": RELEASE_CLASSIFICATION_PROMPT.format(text=text)
            }]
        )
        
        return json.loads(response.content[0].text)
    
    async def batch_classify_reviews(
        self, 
        reviews: list[dict]
    ) -> list[dict]:
        """
        Пакетная классификация отзывов.
        Для экономии можно группировать по 5-10 отзывов в один запрос.
        """
        results = []
        
        # Простой вариант: по одному
        for review in reviews:
            classification = await self.classify_review(
                review["text"],
                review["rating"]
            )
            results.append({
                "external_id": review["external_id"],
                **classification
            })
        
        return results
```

### 7.2 Генератор дайджестов

```python
# app/services/digest_generator.py

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
4. ## Изменения тарифов (if any)
5. ## Активные промоакции (table format)
6. ## Тренды в отзывах (insights from review analysis)
7. ## Рекомендации (2-3 actionable insights for Yango team)

Keep the tone professional but accessible. Highlight competitive threats and opportunities.
Total length: 500-800 words."""


class DigestGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-opus-4-5-20250514"  # Opus для качественной генерации
    
    async def generate(
        self,
        period_start: date,
        period_end: date
    ) -> dict:
        """Генерирует дайджест за период"""
        
        # 1. Собираем данные
        releases = await self._get_releases(period_start, period_end)
        tariff_changes = await self._detect_tariff_changes(period_start, period_end)
        promos = await self._get_active_promos()
        review_trends = await self._analyze_review_trends(period_start, period_end)
        
        # 2. Форматируем секции
        releases_section = self._format_releases(releases)
        tariff_section = self._format_tariff_changes(tariff_changes)
        promos_section = self._format_promos(promos)
        trends_section = self._format_trends(review_trends)
        
        # 3. Генерируем через Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": DIGEST_PROMPT.format(
                    period_start=period_start.isoformat(),
                    period_end=period_end.isoformat(),
                    releases_section=releases_section,
                    tariff_changes_section=tariff_section,
                    promos_section=promos_section,
                    review_trends_section=trends_section
                )
            }]
        )
        
        content = response.content[0].text
        
        # 4. Сохраняем
        digest = Digest(
            period_start=period_start,
            period_end=period_end,
            content=content,
            metadata={
                "releases_count": len(releases),
                "tariff_changes_count": len(tariff_changes),
                "active_promos_count": len(promos),
                "model": self.model
            }
        )
        self.db.add(digest)
        self.db.commit()
        
        return {
            "id": str(digest.id),
            "period": f"{period_start} — {period_end}",
            "content": content,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _analyze_review_trends(
        self,
        start: date,
        end: date
    ) -> dict:
        """Анализирует тренды в отзывах"""
        
        # Текущий период
        current = self.db.execute("""
            SELECT 
                c.name,
                r.sentiment,
                COUNT(*) as count,
                array_agg(DISTINCT cat.slug) as categories
            FROM reviews r
            JOIN competitors c ON r.competitor_id = c.id
            LEFT JOIN review_categories rc ON r.id = rc.review_id
            LEFT JOIN categories cat ON rc.category_id = cat.id
            WHERE r.review_date BETWEEN :start AND :end
            GROUP BY c.name, r.sentiment
        """, {"start": start, "end": end}).fetchall()
        
        # Предыдущий период для сравнения
        prev_start = start - (end - start)
        previous = self.db.execute("""
            SELECT c.name, r.sentiment, COUNT(*) as count
            FROM reviews r
            JOIN competitors c ON r.competitor_id = c.id
            WHERE r.review_date BETWEEN :start AND :end
            GROUP BY c.name, r.sentiment
        """, {"start": prev_start, "end": start}).fetchall()
        
        # Вычисляем изменения
        # ... логика сравнения
        
        return trends
```

### 7.3 Стоимость API

Примерная оценка затрат на Claude API:

| Операция | Модель | Токены (in/out) | Цена за запрос | Частота | Месяц |
|----------|--------|-----------------|----------------|---------|-------|
| Классификация отзыва | Sonnet | 300/100 | ~$0.001 | 200/нед | ~$0.80 |
| Классификация релиза | Sonnet | 500/150 | ~$0.002 | 20/нед | ~$0.16 |
| Генерация дайджеста | Opus | 2000/1500 | ~$0.10 | 4/мес | ~$0.40 |

**Итого: ~$5-10/месяц** при текущих объёмах.

---

## 8. Frontend (Next.js)

### 8.1 Структура проекта

```
web/
├── app/
│   ├── (auth)/
│   │   ├── sign-in/[[...sign-in]]/page.tsx
│   │   └── sign-up/[[...sign-up]]/page.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx          # Общий layout с навигацией
│   │   ├── page.tsx            # Dashboard (главная)
│   │   ├── tariffs/
│   │   │   └── page.tsx        # Сравнение тарифов
│   │   ├── promos/
│   │   │   └── page.tsx        # Промоакции
│   │   ├── releases/
│   │   │   └── page.tsx        # Релизы
│   │   ├── reviews/
│   │   │   └── page.tsx        # Отзывы
│   │   ├── digest/
│   │   │   └── page.tsx        # Генерация дайджестов
│   │   └── collection/
│   │       └── page.tsx        # Статус сбора
│   │
│   ├── api/                    # API Routes (опционально)
│   ├── layout.tsx              # Root layout
│   └── globals.css
│
├── components/
│   ├── ui/                     # shadcn/ui компоненты
│   ├── dashboard/
│   │   ├── StatsCard.tsx
│   │   ├── RecentActivity.tsx
│   │   └── HealthStatus.tsx
│   ├── tariffs/
│   │   ├── ComparisonTable.tsx
│   │   └── HistoryChart.tsx
│   ├── reviews/
│   │   ├── ReviewList.tsx
│   │   ├── ReviewFilters.tsx
│   │   └── SentimentChart.tsx
│   └── common/
│       ├── DataTable.tsx
│       ├── ExportButton.tsx
│       └── DateRangePicker.tsx
│
├── lib/
│   ├── api.ts                  # API client
│   └── utils.ts
│
├── middleware.ts               # Clerk auth middleware
├── next.config.js
├── tailwind.config.js
└── package.json
```

### 8.2 API Client

```typescript
// lib/api.ts

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Dashboard
  async getDashboardSummary() {
    return this.fetch<DashboardSummary>('/api/dashboard/summary');
  }

  // Tariffs
  async getTariffComparison(type?: 'driver' | 'rider') {
    const params = type ? `?type=${type}` : '';
    return this.fetch<TariffComparison>(`/api/tariffs/comparison${params}`);
  }

  async getTariffHistory(competitorId: string, days = 30) {
    return this.fetch<TariffHistory>(
      `/api/tariffs/history/${competitorId}?days=${days}`
    );
  }

  // Reviews
  async getReviews(filters: ReviewFilters) {
    const params = new URLSearchParams(filters as any);
    return this.fetch<ReviewList>(`/api/reviews?${params}`);
  }

  async getReviewStats(competitorId?: string) {
    const params = competitorId ? `?competitor_id=${competitorId}` : '';
    return this.fetch<ReviewStats>(`/api/reviews/stats${params}`);
  }

  // Releases
  async getReleases(filters: ReleaseFilters) {
    const params = new URLSearchParams(filters as any);
    return this.fetch<ReleaseList>(`/api/releases?${params}`);
  }

  // Digest
  async generateDigest(period: string, endDate: string) {
    return this.fetch<Digest>('/api/digest/generate', {
      method: 'POST',
      body: JSON.stringify({ period, end_date: endDate }),
    });
  }

  // Collection
  async getCollectionStatus() {
    return this.fetch<CollectionStatus>('/api/collection/status');
  }
}

export const api = new ApiClient();
```

### 8.3 Пример страницы

```tsx
// app/(dashboard)/tariffs/page.tsx

import { auth } from '@clerk/nextjs';
import { api } from '@/lib/api';
import { ComparisonTable } from '@/components/tariffs/ComparisonTable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default async function TariffsPage() {
  const { getToken } = auth();
  const token = await getToken();
  
  api.setToken(token!);
  
  const [driverTariffs, riderTariffs] = await Promise.all([
    api.getTariffComparison('driver'),
    api.getTariffComparison('rider'),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Сравнение тарифов</h1>
        <p className="text-muted-foreground">
          Актуальные данные по всем конкурентам
        </p>
      </div>

      <Tabs defaultValue="driver">
        <TabsList>
          <TabsTrigger value="driver">Водители</TabsTrigger>
          <TabsTrigger value="rider">Пассажиры</TabsTrigger>
        </TabsList>
        
        <TabsContent value="driver">
          <ComparisonTable 
            data={driverTariffs} 
            columns={driverColumns}
          />
        </TabsContent>
        
        <TabsContent value="rider">
          <ComparisonTable 
            data={riderTariffs} 
            columns={riderColumns}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

const driverColumns = [
  { key: 'competitor', label: 'Конкурент' },
  { key: 'commission_rate', label: 'Комиссия', format: (v) => `${v}%` },
  { key: 'signup_bonus', label: 'Бонус регистрации', format: (v) => `S/${v}` },
  { key: 'referral_bonus', label: 'Реферальный бонус', format: (v) => `S/${v}` },
];

const riderColumns = [
  { key: 'competitor', label: 'Конкурент' },
  { key: 'base_fare', label: 'Базовый тариф', format: (v) => `S/${v}` },
  { key: 'per_km_rate', label: 'За км', format: (v) => `S/${v}` },
  { key: 'per_min_rate', label: 'За минуту', format: (v) => `S/${v}` },
];
```

---

## 9. Авторизация (Clerk)

### 9.1 Настройка

1. **Создать приложение в Clerk Dashboard**
   - https://dashboard.clerk.com
   - New Application → выбрать sign-in methods (Email, Google)

2. **Получить ключи**
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
   CLERK_SECRET_KEY=sk_live_...
   ```

3. **Настроить URLs**
   ```
   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
   NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
   NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
   ```

### 9.2 Middleware

```typescript
// middleware.ts

import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  // Публичные routes (не требуют авторизации)
  publicRoutes: [
    '/sign-in(.*)',
    '/sign-up(.*)',
    '/api/webhooks/octoparse',  // Webhook от Octoparse
  ],
});

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

### 9.3 Интеграция с Backend

Frontend передаёт JWT токен от Clerk в каждом запросе:

```typescript
// На фронтенде
const { getToken } = useAuth();
const token = await getToken();

fetch('/api/endpoint', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Backend верифицирует токен через Clerk JWKS (см. раздел 5.3).

---

## 10. Deployment

### 10.1 Render (Backend + Database)

**PostgreSQL:**
1. Render Dashboard → New → PostgreSQL
2. Name: `yango-intel-db`
3. Plan: Starter ($7/month)
4. Region: Oregon (US West)
5. → Create Database
6. Сохранить `Internal Database URL`

**FastAPI:**
1. Render Dashboard → New → Web Service
2. Connect GitHub repo
3. Name: `yango-intel-api`
4. Environment: Python 3
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Plan: Starter ($7/month)

**Environment Variables (Render):**
```
DATABASE_URL=postgresql://...  (Internal URL)
ANTHROPIC_API_KEY=sk-ant-...
WEBHOOK_SECRET=your-secret-here
CLERK_JWKS_URL=https://your-app.clerk.accounts.dev/.well-known/jwks.json
ALLOWED_ORIGINS=https://yango-intel.vercel.app
```

### 10.2 Vercel (Frontend)

1. Import GitHub repo
2. Framework: Next.js (auto-detected)
3. Root Directory: `web` (если monorepo)

**Environment Variables (Vercel):**
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_API_URL=https://yango-intel-api.onrender.com
```

### 10.3 CI/CD

Оба сервиса автоматически деплоятся при push в main:

```
git push origin main
    │
    ├──► Vercel: rebuild frontend (30 сек)
    │
    └──► Render: rebuild backend (2-3 мин)
```

---

## 11. Мониторинг и логирование

### 11.1 Логирование

```python
# app/core/logging.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

# Render собирает stdout → можно просматривать в Render Dashboard
logger = logging.getLogger("yango-intel")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 11.2 Health Check

```python
# app/api/routes/health.py

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Проверка БД
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"
    
    # Проверка последнего сбора
    last_collection = db.query(CollectionLog)\
        .order_by(CollectionLog.completed_at.desc())\
        .first()
    
    hours_since_collection = None
    if last_collection:
        hours_since_collection = (
            datetime.now() - last_collection.completed_at
        ).total_seconds() / 3600
    
    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "last_collection": {
            "at": last_collection.completed_at if last_collection else None,
            "hours_ago": round(hours_since_collection, 1) if hours_since_collection else None,
            "status": last_collection.status if last_collection else None
        }
    }
```

### 11.3 Оповещения

Для MVP можно использовать простой Telegram бот для критических ошибок:

```python
# app/services/notifications.py

import httpx

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

async def send_alert(message: str):
    if not TELEGRAM_BOT_TOKEN:
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🚨 Yango Intel Alert\n\n{message}",
            "parse_mode": "HTML"
        })

# Использование
await send_alert("Webhook от Octoparse failed: InDriver website недоступен")
```

---

## 12. Расширение после MVP

### 12.1 Что добавить позже

| Функционал | Сложность | Приоритет |
|------------|-----------|-----------|
| Автоматический сбор по расписанию | Низкая | Высокий |
| Email-уведомления об изменениях | Низкая | Высокий |
| Второй регион (например, Colombia) | Средняя | Средний |
| API для внешних систем | Средняя | Средний |
| ML-модель для классификации (вместо Claude) | Высокая | Низкий |
| Интеграция с BI-инструментами | Средняя | Низкий |

### 12.2 Масштабирование

Если объёмы вырастут:

1. **База данных**: Render позволяет апгрейд до Pro ($30/мес) с бо́льшими ресурсами
2. **Backend**: Добавить worker для фоновых задач (Celery + Redis или просто отдельный процесс)
3. **Парсинг**: Перейти на Octoparse Advanced для бо́льшего параллелизма
4. **AI**: Batch API от Anthropic для снижения стоимости при больших объёмах

---

## Контрольный список перед запуском

### Инфраструктура
- [ ] Render: PostgreSQL создан, URL сохранён
- [ ] Render: Web Service создан, переменные настроены
- [ ] Vercel: Проект импортирован, переменные настроены
- [ ] Clerk: Приложение создано, ключи получены

### Octoparse
- [ ] 12 задач созданы
- [ ] Webhook URL настроен в каждой задаче
- [ ] Тестовый запуск каждой задачи прошёл

### Код
- [ ] Миграции применены (`alembic upgrade head`)
- [ ] Начальные данные загружены (competitors, categories)
- [ ] Health check endpoint работает
- [ ] Webhook принимает и обрабатывает данные

### Безопасность
- [ ] WEBHOOK_SECRET уникален и сохранён
- [ ] CORS настроен только для вашего домена
- [ ] API endpoints защищены Clerk

---

*Документ подготовлен для Yango Competitive Intelligence MVP*
*Версия 1.0 | Январь 2025*