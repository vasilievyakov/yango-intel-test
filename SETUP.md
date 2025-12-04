# 🚀 Yango Competitive Intelligence — Cloud Setup

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vercel    │────▶│   Render    │────▶│  Supabase   │
│  (Frontend) │     │  (Backend)  │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌─────────┐   ┌──────────┐
              │ Gemini  │   │ Parallel │
              │   API   │   │    AI    │
              └─────────┘   └──────────┘
```

---

## 1. Настройка Supabase (PostgreSQL)

### Шаг 1: Создание проекта
1. Перейдите на https://supabase.com
2. **New Project** → Выберите организацию
3. Заполните:
   - **Name**: `yango-intel`
   - **Database Password**: сохраните этот пароль!
   - **Region**: выберите ближайший (eu-central-1 для Европы)
4. Нажмите **Create new project**

### Шаг 2: Получение Connection String
1. После создания → **Settings** → **Database**
2. Скопируйте **URI** из секции "Connection string"
3. Замените `[YOUR-PASSWORD]` на ваш пароль
4. Измените `postgresql://` на `postgresql+asyncpg://`

**Пример:**
```
postgresql+asyncpg://postgres.xxxx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

---

## 2. Получение API ключей

### Google Gemini API
1. Перейдите на https://aistudio.google.com/apikey
2. **Create API Key** → Выберите проект
3. Скопируйте ключ (начинается с `AIza...`)

### Parallel AI
1. Перейдите на https://www.parallel.ai
2. Зарегистрируйтесь / войдите
3. **API Keys** → создайте новый ключ

### Clerk (авторизация)
1. Перейдите на https://dashboard.clerk.com
2. **Create application**
3. Выберите методы входа (Email, Google)
4. Скопируйте из **API Keys**:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - `CLERK_SECRET_KEY`
5. В **Settings** найдите JWKS URL

---

## 3. Деплой Backend на Render

### Шаг 1: Подключение репозитория
1. Перейдите на https://dashboard.render.com
2. **New** → **Web Service**
3. Подключите GitHub репозиторий
4. Выберите репозиторий `peru`

### Шаг 2: Настройка сервиса
```
Name: yango-intel-api
Region: Frankfurt (EU Central)
Branch: main
Root Directory: api
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Шаг 3: Environment Variables
Добавьте в Render Dashboard → Environment:

```env
# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres.xxxx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Security
WEBHOOK_SECRET=your-random-secret-32-chars
ALLOWED_ORIGINS=https://yango-intel.vercel.app

# Google Gemini
GOOGLE_API_KEY=AIza...your-gemini-key

# Parallel AI
PARALLEL_API_KEY=your-parallel-key

# Clerk Auth
CLERK_JWKS_URL=https://your-app.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://your-app.clerk.accounts.dev
```

### Шаг 4: Deploy
Нажмите **Create Web Service** → дождитесь деплоя

**URL бэкенда:** `https://yango-intel-api.onrender.com`

---

## 4. Деплой Frontend на Vercel

### Шаг 1: Import проекта
1. Перейдите на https://vercel.com/new
2. **Import Git Repository** → выберите `peru`
3. **Configure Project**:
   - **Root Directory**: `web`
   - **Framework Preset**: Next.js

### Шаг 2: Environment Variables
```env
# Backend API
NEXT_PUBLIC_API_URL=https://yango-intel-api.onrender.com

# Clerk Auth
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
```

### Шаг 3: Deploy
Нажмите **Deploy** → дождитесь завершения

**URL фронтенда:** `https://yango-intel.vercel.app`

---

## 5. Применение миграций

После деплоя бэкенда нужно создать таблицы в Supabase.

### Вариант A: Через Render Shell
1. Render Dashboard → ваш сервис → **Shell**
2. Выполните:
```bash
alembic upgrade head
```

### Вариант B: Локально
```bash
cd api

# Установите переменную окружения
export DATABASE_URL="postgresql+asyncpg://..."

# Примените миграции
alembic upgrade head
```

---

## 6. Проверка работы

### Backend Health Check
```bash
curl https://yango-intel-api.onrender.com/health
```

Ожидаемый ответ:
```json
{"status": "healthy", "database": "connected"}
```

### Frontend
1. Откройте https://yango-intel.vercel.app
2. Войдите через Clerk
3. Проверьте дашборд

---

## 7. Обновление CORS

После деплоя обновите `ALLOWED_ORIGINS` в Render:
```
ALLOWED_ORIGINS=https://yango-intel.vercel.app,https://your-custom-domain.com
```

---

## Переменные окружения — полный список

### Backend (Render)
| Переменная | Описание | Пример |
|------------|----------|--------|
| `DATABASE_URL` | Supabase connection string | `postgresql+asyncpg://...` |
| `GOOGLE_API_KEY` | Gemini API key | `AIza...` |
| `PARALLEL_API_KEY` | Parallel AI key | `...` |
| `WEBHOOK_SECRET` | Секрет для Octoparse | random 32 chars |
| `ALLOWED_ORIGINS` | CORS origins | `https://your-app.vercel.app` |
| `CLERK_JWKS_URL` | Clerk JWKS endpoint | `https://.../.well-known/jwks.json` |
| `CLERK_ISSUER` | Clerk issuer | `https://your-app.clerk.accounts.dev` |

### Frontend (Vercel)
| Переменная | Описание | Пример |
|------------|----------|--------|
| `NEXT_PUBLIC_API_URL` | Backend URL | `https://yango-intel-api.onrender.com` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk public key | `pk_live_...` |
| `CLERK_SECRET_KEY` | Clerk secret key | `sk_live_...` |

---

## Стоимость

| Сервис | План | Цена |
|--------|------|------|
| Supabase | Free | $0 (500MB) |
| Render | Free | $0 (спит после 15 мин) |
| Render | Starter | $7/мес (всегда онлайн) |
| Vercel | Hobby | $0 |
| Gemini API | Pay-as-you-go | ~$0.50/1M tokens |
| Clerk | Free | $0 (до 10k MAU) |

**Итого для MVP: $0-7/месяц**
