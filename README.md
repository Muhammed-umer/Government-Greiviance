# Tamil Nadu Government Grievance Portal (Makkal Sevai)

Production-ready, full-stack, mobile-first **Tamil Nadu Government Grievance Portal** ("Makkal Sevai"). Built with Next.js 14+ App Router, TypeScript, Tailwind CSS, Python 3.12 FastAPI, SQLAlchemy 2, Alembic, PostgreSQL with PostGIS & pgvector, Redis, Celery, and Docker Compose.

> **Core Principle**: One real-world issue can have many private citizen petitions, but officers work from one shared operational incident.

---

## Key Features

1. **Bilingual & Tanglish Interface**: Complete Tamil and English UI with live language switcher and PWA support.
2. **Multimodal Filing**: Type text or record audio directly via browser microphone APIs with Speech-to-Text review.
3. **AI Department Routing**: Automatic department classification (GCC, TANGEDCO, CMWSSB, Traffic Police, Revenue, Health) with human triage queue fallback for low confidence (<0.75).
4. **Duplicate Incident Deduplication**: Deduplicates petitions into shared operational tickets based on category, spatial proximity, and semantic vector similarity. Auto-links low-risk cases (>=0.85), flags medium similarity (0.65-0.84) to human triage, and strictly prevents auto-linking sensitive categories (abuse, corruption, domestic violence).
5. **Explainable Priority Rules Engine**: Weighted scoring (0-100) based on Safety Severity, Verified Public Impact, Critical Location, SLA Risk, and Recurrence. Includes an immediate High priority trigger for life-safety hazards (fire, live wire, open manhole, severe flooding).
6. **Officer Priority Override Audit Trail**: Officers can override priority only with a mandatory explanation recorded to the audit log.
7. **Privacy & Security by Design**: Citizens view only their own petitions. Officers work from shared incident views with PII anonymized (citizen names, phone numbers, exact addresses redacted).

---

## Tech Stack & Monorepo Structure

```text
apps/
  web/                 # Next.js 14 App Router, TypeScript, Tailwind CSS, PWA
services/
  api/                 # FastAPI REST API, SQLAlchemy 2, Alembic, PostGIS & pgvector
  worker/              # Celery background worker for AI & SLA monitoring
infra/
  docker-compose.yml   # Multi-container orchestration (Postgres, Redis, MinIO, API, Worker, Web)
docs/                  # Setup instructions & API notes
```

---

## Quickstart

```bash
# 1. Clone & prepare environment
cp .env.example .env

# 2. Build and start containers via Docker Compose
docker compose -f infra/docker-compose.yml up --build -d

# 3. Apply database migrations
docker exec -it tn_grievance_api alembic -c services/api/alembic.ini upgrade head

# 4. Seed demo data
docker exec -it tn_grievance_api python -m services.api.src.seed.seed_data
```

Access Web App: `http://localhost:3000`  
Access OpenAPI Docs: `http://localhost:8000/docs`

---

## Verification & Testing

```bash
# Backend Pytest Suite
pytest services/api/tests

# Frontend Unit Tests
cd apps/web && npm run test
```
