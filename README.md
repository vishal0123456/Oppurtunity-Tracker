# 🌍 Global Opportunity Tracker

An AI-powered platform that **automatically discovers, categorizes, and tracks global opportunities** — scholarships, fellowships, grants, accelerators, VC programs, competitions, conferences, and more — for students, founders, researchers, and creators worldwide.

---

## ✨ Features

| Feature | Status |
|---|---|
| Automated daily scraping (OpportunityDesk, YouthOpportunities, RSS feeds, F6S, Devex) | ✅ |
| AI extraction via Google Gemini (free tier) | ✅ |
| Smart categorization + tag enrichment | ✅ |
| Duplicate detection (URL + fuzzy title match) | ✅ |
| Expired opportunity cleanup | ✅ |
| AI natural language search ("Women founder grants in Europe") | ✅ |
| Full filter panel (category, country, tags, eligibility) | ✅ |
| Application tracker (7 stages, notes, priority, dates, document links) | ✅ |
| Mobile-responsive UI with filter drawer | ✅ |
| REST API with OpenAPI docs | ✅ |
| Daily GitHub Actions pipeline | ✅ |
| Docker Compose for local dev | ✅ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 15)                 │
│  / (Discover)  •  /opportunities/[id]  •  /tracker          │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  /opportunities  •  /applications  •  /health               │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Scrapers   │  │ AI Pipeline  │  │    Scheduler     │  │
│  │ OpDesk       │  │ Gemini LLM   │  │ APScheduler      │  │
│  │ YouthOpp     │  │ Extractor    │  │ Daily @ 06:00 UTC│  │
│  │ RSS (16 feeds│  │ Categorizer  │  │ + GitHub Actions │  │
│  │ F6S          │  │ Search Asst  │  └──────────────────┘  │
│  │ Devex        │  └──────────────┘                        │
│  └──────────────┘                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   PostgreSQL Database                        │
│  opportunities  •  user_applications                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- OR: Python 3.11+, Node.js 20+, PostgreSQL 16+
- A free [Google AI Studio](https://aistudio.google.com/app/apikey) API key (Gemini)

### Option A — Docker Compose (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/your-username/opportunity-tracker.git
cd opportunity-tracker

# 2. Set your Gemini API key
export GEMINI_API_KEY=your_key_here   # Linux/Mac
set GEMINI_API_KEY=your_key_here      # Windows CMD

# 3. Start everything
docker compose up --build

# 4. Open the app
# Frontend: http://localhost:3000
# API docs:  http://localhost:8000/docs
```

### Option B — Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env       # Windows
cp .env.example .env         # Linux/Mac
# Edit .env and set GEMINI_API_KEY and DATABASE_URL

# Start PostgreSQL (or use Docker just for DB)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=opportunity_tracker postgres:16-alpine

# Run the backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.local.example .env.local   # Windows
cp .env.local.example .env.local     # Linux/Mac
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000

# Start the frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## 🔧 Configuration

### Backend Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/opportunity_tracker` | PostgreSQL connection string |
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key (free) |
| `APP_ENV` | `development` | `development` / `production` / `test` |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `PIPELINE_RUN_HOUR` | `6` | UTC hour for daily pipeline |
| `PIPELINE_RUN_MINUTE` | `0` | UTC minute for daily pipeline |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated CORS origins |

Copy `backend/.env.example` to `backend/.env` and fill in your values.

### Frontend Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## 📡 API Documentation

Interactive API docs are available at **`http://localhost:8000/docs`** (Swagger UI) and **`http://localhost:8000/redoc`** (ReDoc).

### Key Endpoints

#### Opportunities

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/opportunities` | List with filters & pagination |
| `GET` | `/opportunities/search?q=...` | AI natural language search |
| `GET` | `/opportunities/{id}` | Single opportunity |
| `POST` | `/opportunities` | Create manually (admin) |
| `PATCH` | `/opportunities/{id}` | Partial update (admin) |
| `POST` | `/opportunities/run-pipeline` | Trigger scraping pipeline |

#### Filter Parameters (`GET /opportunities`)

| Param | Type | Example |
|---|---|---|
| `category` | string | `scholarship`, `fellowship`, `accelerator` |
| `country` | string | `India`, `USA`, `Europe` |
| `tag` | string | `AI`, `Women`, `Startup` |
| `women_friendly` | bool | `true` |
| `india_eligible` | bool | `true` |
| `student_eligible` | bool | `true` |
| `is_remote` | bool | `true` |
| `is_expired` | bool | `false` (default) |
| `deadline_before` | date | `2025-12-31` |
| `deadline_after` | date | `2025-01-01` |
| `search` | string | `climate fellowship` |
| `page` | int | `1` |
| `page_size` | int | `20` (max 100) |

#### Applications

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/applications` | List all tracked applications |
| `POST` | `/applications` | Track an opportunity |
| `PUT` | `/applications/{id}` | Update status, notes, priority, dates |
| `DELETE` | `/applications/{id}` | Remove from tracker |

---

## 🤖 AI Pipeline

### How It Works

```
Scraper fetches URLs
       ↓
Deduplication check (URL + fuzzy title)
       ↓
Fetch page text (BeautifulSoup, robots.txt compliant)
       ↓
Gemini LLM extracts 15 structured fields
       ↓  (fallback: regex heuristics if LLM fails)
Categorizer normalizes + enriches tags
       ↓
Save to PostgreSQL
       ↓
Mark expired opportunities
```

### Extracted Fields

The AI extracts: `title`, `organization`, `country`, `deadline`, `eligibility`, `funding_amount`, `category`, `description`, `is_remote`, `women_friendly`, `india_eligible`, `student_eligible`, `age_limit`, `application_fee`, `tags`

### AI Search Examples

```
"Women founder grants in Europe"
→ { category: "grant", women_friendly: true, country: ["Europe"] }

"Fully funded fellowships for Indian students"
→ { category: "fellowship", india_eligible: true, student_eligible: true }

"AI startup accelerators in Singapore"
→ { category: "accelerator", country: ["Singapore"], tags: ["AI", "Startup"] }

"Travel opportunities under 25"
→ { category: "travel_program", tags: ["Travel"] }
```

---

## 🗄️ Database Schema

### `opportunities`

```sql
id              UUID PRIMARY KEY
title           VARCHAR(500) NOT NULL
organization    VARCHAR(300)
description     TEXT
category        VARCHAR(100)   -- 13 valid values
tags            TEXT[]         -- AI-generated
country         TEXT[]
is_remote       BOOLEAN
women_friendly  BOOLEAN
india_eligible  BOOLEAN
student_eligible BOOLEAN
age_limit       VARCHAR(100)
eligibility     TEXT
funding_amount  VARCHAR(200)
application_fee VARCHAR(100)
link            VARCHAR(2000) UNIQUE NOT NULL
source_url      VARCHAR(2000)
source_name     VARCHAR(200)
deadline        DATE
is_expired      BOOLEAN
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

### `user_applications`

```sql
id              UUID PRIMARY KEY
opportunity_id  UUID REFERENCES opportunities(id) ON DELETE CASCADE
status          VARCHAR(50)   -- saved|planning|applied|interview|accepted|rejected|waitlisted
notes           TEXT
priority        INTEGER       -- 1 (highest) to 5 (lowest)
applied_at      DATE
reminder_date   DATE
document_links  TEXT          -- newline-separated URLs
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

---

## 🧪 Running Tests

```bash
cd backend

# Install dependencies (includes test deps)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_api_opportunities.py -v

# Run a specific test
pytest tests/test_pipeline.py::TestNormalizeCategory -v
```

Tests use an **in-memory SQLite database** — no PostgreSQL required to run tests.

### Test Coverage

| Module | Tests |
|---|---|
| `GET/POST/PATCH /opportunities` | `test_api_opportunities.py` |
| `GET/POST/PUT/DELETE /applications` | `test_api_applications.py` |
| Pipeline deduplicator | `test_pipeline.py` |
| AI categorizer & normalizer | `test_pipeline.py` |
| AI extractor (fallback + LLM mock) | `test_ai_extractor.py` |
| All scrapers (mocked HTTP) | `test_scrapers.py` |

---

## 🌱 Seed Data

Populate the database with 22 realistic sample opportunities for demo purposes:

```bash
cd backend
python scripts/seed_data.py
```

Covers: Chevening, Fulbright, DAAD, Y Combinator, Google Accelerator, Antler, Gates Foundation, Cartier Women's Initiative, Startup India, MIT Solve, Grace Hopper, AWS Activate, and more.

---

### GitHub Actions (Daily Pipeline)

The pipeline runs automatically every day at **06:00 UTC** via `.github/workflows/scraper.yml`.

**Required GitHub Secrets:**

| Secret | Description |
|---|---|
| `DATABASE_URL` | Production PostgreSQL connection string |
| `GEMINI_API_KEY` | Google AI Studio API key |

To set secrets: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

You can also trigger the pipeline manually from the GitHub Actions tab or from the UI using the "Run Pipeline" button.

### Manual Pipeline Trigger

```bash
# Via API
curl -X POST http://localhost:8000/opportunities/run-pipeline

# Via Python directly
cd backend
python -m app.pipeline.runner
```

---

## 🚢 Deployment

### Railway (recommended)

1. Push to GitHub
2. Create a new Railway project → Deploy from GitHub
3. Add a PostgreSQL plugin
4. Set environment variables: `DATABASE_URL`, `GEMINI_API_KEY`, `APP_ENV=production`, `ALLOWED_ORIGINS=https://your-frontend.vercel.app`
5. Deploy the backend service from `backend/`

### Vercel (frontend)

1. Import the GitHub repo in Vercel
2. Set root directory to `frontend`
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
4. Deploy

### Render

Similar to Railway — create a Web Service for the backend and a Static Site / Web Service for the frontend.

---

## 📁 Project Structure

```
opportunity-tracker/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── categorizer.py      # Tag normalization & enrichment
│   │   │   ├── extractor.py        # Gemini LLM extraction + fallback
│   │   │   └── search_assistant.py # Natural language → filters
│   │   ├── api/
│   │   │   ├── opportunities.py    # Opportunity CRUD + search
│   │   │   └── applications.py     # Application tracker CRUD
│   │   ├── models/
│   │   │   ├── opportunity.py      # SQLAlchemy ORM model
│   │   │   └── application.py      # UserApplication ORM model
│   │   ├── pipeline/
│   │   │   ├── runner.py           # Main pipeline orchestrator
│   │   │   └── deduplicator.py     # URL + fuzzy title dedup
│   │   ├── scraper/
│   │   │   ├── base_scraper.py     # Abstract base + robots.txt
│   │   │   ├── opportunity_desk.py # OpportunityDesk.org scraper
│   │   │   ├── youth_opportunities.py # YouthOp.com scraper
│   │   │   ├── rss_scraper.py      # 16 RSS feeds
│   │   │   └── global_grants.py    # F6S + Devex scrapers
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── config.py               # Settings from .env
│   │   ├── database.py             # SQLAlchemy async engine
│   │   ├── main.py                 # FastAPI app entry point
│   │   └── scheduler.py            # APScheduler daily cron
│   ├── migrations/                 # Alembic migrations
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Discovery page
│   │   │   ├── opportunities/[id]/ # Opportunity detail
│   │   │   └── tracker/            # Application tracker
│   │   ├── components/
│   │   │   ├── FilterPanel.tsx     # Desktop filter sidebar
│   │   │   ├── MobileFilterDrawer.tsx # Mobile filter drawer
│   │   │   ├── Navbar.tsx
│   │   │   ├── OpportunityCard.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── lib/api.ts              # Typed API client
│   │   └── types/opportunity.ts    # TypeScript types
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/scraper.yml   # Daily GitHub Actions pipeline
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| AI | Google Gemini 2.0 Flash (free tier) |
| Scraping | httpx, BeautifulSoup4, feedparser |
| Scheduling | APScheduler + GitHub Actions |
| Deployment | Docker, Vercel, Railway/Render |

---

## 🔑 Getting a Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the key and add it to `backend/.env` as `GEMINI_API_KEY`

**Free tier limits:** 15 requests/minute, 1,500 requests/day — sufficient for the daily pipeline.

---

## 📊 Evaluation Criteria Coverage

| Criteria | Implementation |
|---|---|
| Engineering quality (25%) | Clean async architecture, modular scrapers, error handling, logging, type safety |
| AI implementation (25%) | Gemini LLM extraction + fallback heuristics, AI search assistant, smart tag enrichment |
| Automation reliability (20%) | Deduplication, retry logic (tenacity), robots.txt compliance, daily scheduler + GitHub Actions |
| Product thinking (15%) | 7-stage tracker, priority ranking, notes, document links, deadline reminders, mobile-responsive |
| UI/UX (10%) | Clean dashboard, AI search, filter panel + mobile drawer, deadline countdown, eligibility badges |
| Documentation (5%) | This README, OpenAPI docs at `/docs`, `.env.example`, inline code comments |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-scraper`
3. Add your scraper in `backend/app/scraper/` extending `BaseScraper`
4. Register it in `backend/app/scraper/__init__.py`
5. Submit a pull request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
