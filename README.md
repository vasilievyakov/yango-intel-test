# 🧪 Yango Competitive Intelligence — TEST REPOSITORY

> ⚠️ **ТЕСТОВЫЙ РЕПОЗИТОРИЙ** — используется для разработки и экспериментов

## Описание

Система мониторинга конкурентов на рынке ride-hailing в Перу (InDriver, Uber, Didi, Cabify).

### Возможности
- 📊 Мониторинг тарифов и комиссий
- 📱 Отслеживание релизов приложений
- ⭐ Анализ отзывов с AI-классификацией
- 🎁 Мониторинг промоакций
- 📝 Автоматическая генерация дайджестов

## Технологии

| Компонент | Технология |
|-----------|------------|
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (Supabase) |
| AI | Google Gemini API |
| Scraping | Parallel AI |
| Auth | Clerk |
| Hosting | Vercel (frontend), Render (backend) |

## Структура

```
peru/
├── api/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/routes/  # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic
│   │   └── db/          # Database config
│   ├── alembic/         # Migrations
│   └── requirements.txt
│
├── web/                 # Next.js Frontend
│   ├── src/
│   │   ├── app/         # Pages (App Router)
│   │   ├── components/  # UI Components
│   │   └── lib/         # Utilities
│   └── package.json
│
├── SETUP.md            # Deployment guide
└── README.md           # This file
```

## Быстрый старт

### Backend
```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd web
npm install
npm run dev
```

## Документация

См. [SETUP.md](./SETUP.md) для инструкций по деплою.

---

*🔬 Тестовый проект — Yango Competitive Intelligence*

